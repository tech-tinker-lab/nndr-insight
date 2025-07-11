# Upload NNDR data router
from fastapi import APIRouter
from sqlalchemy import create_engine, text
import os
import math
from fastapi import UploadFile, File, Form, HTTPException
import shutil
from fastapi import Depends
from app.services.auth_service import get_current_user
from app.models import User
from fastapi import Query
from datetime import datetime
import platform
import logging
import json
import uuid

router = APIRouter()

# --- File upload endpoints are commented out for future implementation ---
# @router.post("/upload")
# async def upload_nndr_data(file: UploadFile = File(...)):
#     # TODO: Accept file upload, detect dataset type, and process accordingly
#     # For now, upload is disabled. Use this endpoint in the future for file uploads.
#     return {"filename": file.filename, "message": "Upload endpoint (not yet implemented)"}

# --- End future upload endpoints ---

# Database connection using environment variables
import os
connection_string = (
    f"postgresql://{os.getenv('PGUSER', 'nndr')}:{os.getenv('PGPASSWORD', 'nndrpass')}@"
    f"{os.getenv('PGHOST', 'localhost')}:{os.getenv('PGPORT', '5432')}/"
    f"{os.getenv('PGDATABASE', 'nndr_test')}"
)
engine = create_engine(connection_string)

# Set default upload directory based on platform
if platform.system() == "Windows":
    # Windows: relative to project root
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
else:
    # Linux/Unix: absolute path
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/server")

os.makedirs(UPLOAD_DIR, exist_ok=True)

def clean_for_json(records):
    for row in records:
        for k, v in row.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                row[k] = None
    return records

@router.get("/nndr/properties")
def get_nndr_properties(skip: int = 0, limit: int = 100):
    # Returns paginated property data from the database
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, ba_reference, property_address, postcode, property_category_code, property_description
            FROM properties
            ORDER BY id
            OFFSET :skip LIMIT :limit
        """), {"skip": skip, "limit": limit})
        records = [dict(row._mapping) for row in result]
    return {"data": clean_for_json(records), "skip": skip, "limit": limit}

@router.get("/nndr/categories")
def get_nndr_categories():
    # Returns all property categories
    with engine.connect() as conn:
        result = conn.execute(text("SELECT code, description FROM categories ORDER BY code"))
        records = [dict(row) for row in result]
    return {"categories": records}

# --- The following endpoints are deprecated or for future use ---
# @router.get("/nndr-data")
# def get_nndr_data(...):
#     # Deprecated: Use /nndr/properties instead
#     pass
# @router.get("/datasets")
# def list_datasets():
#     # Deprecated: Use database-driven endpoints
#     pass
# @router.get("/dataset-columns")
# def get_dataset_columns(...):
#     # Deprecated: Use database-driven endpoints
#     pass

def detect_dataset_type(filename):
    """
    Detect dataset type from filename or content.
    Returns the appropriate staging table name in the staging schema.
    """
    filename_lower = filename.lower()
    
    # Detect by filename patterns - now using staging schema
    if 'uprn' in filename_lower:
        return 'staging.os_open_uprn_staging'
    elif 'onspd' in filename_lower or 'postcode' in filename_lower:
        return 'staging.onspd_staging'
    elif 'names' in filename_lower:
        return 'staging.os_open_names_staging'
    elif 'map' in filename_lower and 'local' in filename_lower:
        return 'staging.os_open_map_local_staging'
    elif 'usrn' in filename_lower:
        return 'staging.os_open_usrn_staging'
    elif 'codepoint' in filename_lower or 'code_point' in filename_lower:
        return 'staging.code_point_open_staging'
    elif 'nndr' in filename_lower and 'properties' in filename_lower:
        return 'staging.nndr_properties_staging'
    elif 'nndr' in filename_lower and 'ratepayers' in filename_lower:
        return 'staging.nndr_ratepayers_staging'
    elif 'valuations' in filename_lower:
        return 'staging.valuations_staging'
    elif 'boundaries' in filename_lower or 'lad' in filename_lower:
        return 'staging.lad_boundaries_staging'
    else:
        # Default fallback - create a generic table in staging schema
        return f'staging.upload_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

logger = logging.getLogger(__name__)

@router.post("/ingestions/upload")
async def upload_ingestion_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """
    Upload a file for ingestion. Automatically detects dataset type and routes to appropriate staging table.
    Saves the file to a temporary location and returns a success message.
    Also logs the upload event to staging.upload_metadata.
    """
    logger.info(f"Starting upload for file: {file.filename}, user: {user.username if user else 'None'}")
    
    # Generate unique identifiers
    upload_id = str(uuid.uuid4())
    batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Detect dataset type from filename
    table_name = detect_dataset_type(file.filename)
    logger.info(f"Detected dataset type: {table_name} for file: {file.filename}")
    
    # Extract just the table name without schema for validation
    table_name_only = table_name.split('.')[-1] if '.' in table_name else table_name
    
    # Validate table name (basic check)
    valid_staging_tables = [
        'onspd_staging', 'code_point_open_staging', 'os_open_names_staging',
        'os_open_map_local_staging', 'os_open_usrn_staging', 'os_open_uprn_staging',
        'nndr_properties_staging', 'nndr_ratepayers_staging', 'valuations_staging',
        'lad_boundaries_staging'
    ]
    
    # Allow dynamic table names that start with 'upload_'
    if not (table_name_only in valid_staging_tables or table_name_only.startswith('upload_')):
        logger.error(f"Invalid table name detected: {table_name} for file: {file.filename}")
        raise HTTPException(status_code=400, detail=f"Could not detect dataset type for file: {file.filename}")

    temp_path = os.path.join(UPLOAD_DIR, str(file.filename))
    logger.info(f"Saving file to: {temp_path}")
    logger.info(f"Upload directory: {UPLOAD_DIR}")
    logger.info(f"Upload directory exists: {os.path.exists(UPLOAD_DIR)}")
    logger.info(f"Upload directory writable: {os.access(UPLOAD_DIR, os.W_OK) if os.path.exists(UPLOAD_DIR) else 'N/A'}")
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File saved successfully to: {temp_path}")
        logger.info(f"File size: {os.path.getsize(temp_path)} bytes")
        
        # Log to staging.upload_metadata
        logger.info("Logging upload to staging.upload_metadata table")
        with engine.connect() as conn:
            logger.info("Database connection established")
            insert_sql = """
                INSERT INTO staging.upload_metadata (
                    upload_id, original_filename, file_size, file_type, uploaded_by, 
                    status, table_name, source_file, metadata
                ) VALUES (
                    :upload_id, :filename, :file_size, :file_type, :uploaded_by, 
                    :status, :table_name, :file_path, :metadata
                )
            """
            insert_params = {
                'upload_id': upload_id,
                'filename': file.filename,
                'file_size': os.path.getsize(temp_path),
                'file_type': file.content_type or 'unknown',
                'uploaded_by': getattr(user, 'username', None) if user else None,
                'status': 'uploaded',
                'table_name': table_name_only,
                'file_path': temp_path,
                'metadata': json.dumps({
                    'batch_id': batch_id,
                    'detected_table': table_name,
                    'upload_timestamp': datetime.now().isoformat(),
                    'file_hash': None,  # Could be enhanced with file hash calculation
                    'session_id': None,  # Could be enhanced with session tracking
                    'client_name': 'web_upload'
                })
            }
            logger.info(f"Executing INSERT with SQL: {insert_sql}")
            logger.info(f"INSERT parameters: {insert_params}")
            
            try:
                result = conn.execute(text(insert_sql), insert_params)
                logger.info(f"INSERT result: {result}")
                conn.commit()
                logger.info("Database transaction committed successfully")
            except Exception as db_error:
                logger.error(f"Database INSERT error: {db_error}")
                logger.error(f"Error type: {type(db_error).__name__}")
                raise db_error
            logger.info("Upload logged to staging.upload_metadata successfully")
        
        # Log staging operation
        try:
            audit_sql = """
                SELECT staging.log_staging_operation(
                    'FILE_UPLOAD',
                    :table_name,
                    :performed_by,
                    :operation_details,
                    :affected_rows
                )
            """
            audit_params = {
                'table_name': table_name_only,
                'performed_by': getattr(user, 'username', None) if user else 'system',
                'operation_details': json.dumps({
                    'upload_id': upload_id,
                    'batch_id': batch_id,
                    'filename': file.filename,
                    'file_size': os.path.getsize(temp_path),
                    'detected_table': table_name
                }),
                'affected_rows': 0  # No rows affected yet, just file upload
            }
            conn.execute(text(audit_sql), audit_params)
            conn.commit()
            logger.info("Staging operation logged successfully")
        except Exception as audit_error:
            logger.warning(f"Failed to log staging operation: {audit_error}")
        
        logger.info(f"Upload completed successfully for file: {file.filename}")
        return {
            "filename": file.filename, 
            "table_name": table_name_only, 
            "upload_id": upload_id,
            "batch_id": batch_id,
            "message": "File uploaded successfully to staging schema. (Ingestion not yet implemented)"
        }
    except Exception as e:
        logger.error(f"Error uploading file {file.filename}: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Full error details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

@router.get("/ingestions/my_uploads")
async def get_my_uploads(
    table_name: str = Query(None),
    filename: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
):
    """
    Return the current user's upload history from staging.upload_metadata, with optional filters.
    """
    logger.info(f"get_my_uploads called by user: {user.username}")
    logger.info(f"Parameters: table_name={table_name}, filename={filename}, start_date={start_date}, end_date={end_date}")
    
    where_clauses = ["uploaded_by = :username"]
    params = {"username": user.username}
    if table_name:
        where_clauses.append("table_name = :table_name")
        params["table_name"] = str(table_name)
    if filename:
        where_clauses.append("original_filename = :filename")
        params["filename"] = str(filename)
    if start_date:
        where_clauses.append("upload_timestamp >= :start_date")
        params["start_date"] = str(start_date)
    if end_date:
        where_clauses.append("upload_timestamp <= :end_date")
        params["end_date"] = str(end_date)
    where_sql = " AND ".join(where_clauses)
    logger.info(f"SQL WHERE clause: {where_sql}")
    logger.info(f"SQL parameters: {params}")
    
    query = text(f"""
        SELECT 
            upload_id, original_filename, file_size, file_type, upload_timestamp,
            uploaded_by, status, table_name, row_count, processing_time_ms,
            error_message, source_file, metadata
        FROM staging.upload_metadata
        WHERE {where_sql}
        ORDER BY upload_timestamp DESC
        LIMIT :limit OFFSET :offset
    """)
    params["limit"] = int(limit)
    params["offset"] = int(offset)
    
    with engine.connect() as conn:
        # First, let's check if the table exists and has any data
        try:
            check_table = conn.execute(text("SELECT COUNT(*) FROM staging.upload_metadata"))
            table_count = check_table.scalar()
            logger.info(f"staging.upload_metadata table exists and has {table_count} total records")
        except Exception as table_error:
            logger.error(f"Error checking staging.upload_metadata table: {table_error}")
            return {"history": [], "total": 0, "limit": limit, "offset": offset}
        
        result = conn.execute(query, params)
        rows = [dict(row._mapping) for row in result.fetchall()]
        logger.info(f"Query returned {len(rows)} rows")
        logger.info(f"First few rows: {rows[:2] if rows else 'No rows'}")
        
        # Get total count
        count_query = text(f"SELECT COUNT(*) FROM staging.upload_metadata WHERE {where_sql}")
        count_result = conn.execute(count_query, params).fetchone()
        total = count_result[0] if count_result else 0
        logger.info(f"Total count: {total}")
    
    return {"history": rows, "total": total, "limit": limit, "offset": offset}
