from fastapi import APIRouter, HTTPException, Depends, Query, status, Security
from typing import Optional, List, Dict, Any
from sqlalchemy import text, func
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from ..services.database_service import get_db
from ..models import StagingMigrationRequest, StagingMigrationResponse, StagingPreviewResponse
from app.models import User
from app.services.database_service import get_db
from app.services.auth_service import get_current_user

# RBAC dependency

def require_admin_or_power(user: User = Depends(get_current_user)):
    if user.role not in ("admin", "power_user"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return user

def require_authenticated_user(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user

router = APIRouter(prefix="/admin", tags=["admin"])

logger = logging.getLogger(__name__)

@router.get("/staging/preview/{table_name}", response_model=StagingPreviewResponse)
async def preview_staging_data(
    table_name: str,
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    source_name: Optional[str] = Query(None, description="Filter by source name"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    page_size: int = Query(100, description="Number of records per page (page size)"),
    offset: int = Query(0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Preview staging data with optional filters and pagination.
    Note: Reducing page_size reduces data transferred per request, but without indexes on filter columns, the database still scans all matching rows before pagination. For large tables, add indexes on batch_id, source_name, session_id, or other filter columns for best performance.
    """
    try:
        # Validate table name to prevent SQL injection
        valid_staging_tables = [
            'onspd_staging', 'code_point_open_staging', 'os_open_names_staging',
            'os_open_map_local_staging', 'os_open_usrn_staging', 'os_open_uprn_staging',
            'nndr_properties_staging', 'nndr_ratepayers_staging', 'valuations_staging',
            'lad_boundaries_staging'
        ]
        
        if table_name not in valid_staging_tables:
            raise HTTPException(status_code=400, detail=f"Invalid table name. Must be one of: {valid_staging_tables}")
        
        # Build WHERE clause for filters
        where_conditions = []
        params = {}
        
        if batch_id:
            where_conditions.append("batch_id = :batch_id")
            params['batch_id'] = batch_id
            
        if source_name:
            where_conditions.append("source_name = :source_name")
            params['source_name'] = source_name
            
        if session_id:
            where_conditions.append("session_id = :session_id")
            params['session_id'] = session_id
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Get total count
        count_query = text(f"""
            SELECT COUNT(*) as total_count 
            FROM {table_name} 
            WHERE {where_clause}
        """)
        count_result = db.execute(count_query, params).fetchone()
        total_count = count_result[0] if count_result else 0
        
        # Get sample data
        sample_query = text(f"""
            SELECT * FROM {table_name} 
            WHERE {where_clause}
            ORDER BY upload_timestamp DESC
            LIMIT :page_size OFFSET :offset
        """)
        params.update({'page_size': page_size, 'offset': offset})
        
        result = db.execute(sample_query, params)
        columns = result.keys()
        sample_data = [dict(zip(columns, row)) for row in result.fetchall()]
        
        # Get unique values for filters
        filter_options = {}
        for filter_field in ['batch_id', 'source_name', 'session_id']:
            filter_query = text(f"""
                SELECT DISTINCT {filter_field} 
                FROM {table_name} 
                WHERE {filter_field} IS NOT NULL 
                ORDER BY {filter_field}
                LIMIT 50
            """)
            filter_result = db.execute(filter_query).fetchall()
            filter_options[filter_field] = [row[0] for row in filter_result]
        
        return StagingPreviewResponse(
            table_name=table_name,
            total_count=total_count,
            sample_data=sample_data,
            filter_options=filter_options,
            applied_filters={
                'batch_id': batch_id,
                'source_name': source_name,
                'session_id': session_id
            }
        )
        
    except Exception as e:
        logger.error(f"Error previewing staging data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error previewing staging data: {str(e)}")

@router.post("/staging/migrate/{table_name}", response_model=StagingMigrationResponse)
async def migrate_staging_to_master(
    table_name: str,
    request: StagingMigrationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_power)
):
    """
    Generic migration from staging to master table. Dynamically maps columns (ignoring metadata), casts types as needed, and migrates only filtered data.
    Note: For large tables, add indexes on filter columns (batch_id, source_name, session_id, etc.) for best performance.
    """
    try:
        # Validate table name
        valid_staging_tables = [
            'onspd_staging', 'code_point_open_staging', 'os_open_names_staging',
            'os_open_map_local_staging', 'os_open_usrn_staging', 'os_open_uprn_staging',
            'nndr_properties_staging', 'nndr_ratepayers_staging', 'valuations_staging',
            'lad_boundaries_staging'
        ]
        if table_name not in valid_staging_tables:
            raise HTTPException(status_code=400, detail=f"Migration not supported for table: {table_name}")

        # Infer master table name
        if table_name.endswith('_staging'):
            master_table = table_name[:-8]  # remove '_staging'
        else:
            raise HTTPException(status_code=400, detail="Invalid staging table name")

        # Metadata columns to ignore
        metadata_cols = [
            'source_name', 'upload_user', 'upload_timestamp', 'batch_id', 'source_file',
            'file_size', 'file_modified', 'session_id', 'client_name'
        ]

        # Get columns for staging and master tables
        staging_cols_query = text(f"""
            SELECT column_name, data_type FROM information_schema.columns
            WHERE table_name = :table AND table_schema = 'public'
        """)
        master_cols_query = text(f"""
            SELECT column_name, data_type FROM information_schema.columns
            WHERE table_name = :table AND table_schema = 'public'
        """)
        staging_cols = db.execute(staging_cols_query, {'table': table_name}).fetchall()
        master_cols = db.execute(master_cols_query, {'table': master_table}).fetchall()

        # Build mapping: only columns present in both, and not metadata
        staging_col_names = set([c[0] for c in staging_cols if c[0] not in metadata_cols])
        master_col_names = set([c[0] for c in master_cols])
        common_cols = list(staging_col_names & master_col_names)
        if not common_cols:
            raise HTTPException(status_code=400, detail="No common columns to migrate.")

        # Build WHERE clause for filters
        where_conditions = []
        params = {}
        if request.batch_id:
            where_conditions.append("batch_id = :batch_id")
            params['batch_id'] = request.batch_id
        if request.source_name:
            where_conditions.append("source_name = :source_name")
            params['source_name'] = request.source_name
        if request.session_id:
            where_conditions.append("session_id = :session_id")
            params['session_id'] = request.session_id
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        # Build column list for INSERT, with explicit type casts if needed
        # Build a mapping of column types for casting
        staging_types = {c[0]: c[1] for c in staging_cols}
        master_types = {c[0]: c[1] for c in master_cols}
        insert_cols = ', '.join(common_cols)
        select_cols_list = []
        for col in common_cols:
            staging_type = staging_types.get(col)
            master_type = master_types.get(col)
            if staging_type and master_type and staging_type != master_type:
                # Add explicit cast if types differ
                select_cols_list.append(f"{col}::{master_type}")
            else:
                select_cols_list.append(f"{col}")
        select_cols = ', '.join(select_cols_list)

        # Get count before migration
        count_query = text(f"SELECT COUNT(*) FROM {table_name} WHERE {where_clause}")
        count_result = db.execute(count_query, params).fetchone()
        records_to_migrate = count_result[0] if count_result else 0

        # Perform migration
        migration_status = "success"
        error_message = None
        try:
            migration_query = text(f"""
                INSERT INTO {master_table} ({insert_cols})
                SELECT {select_cols}
                FROM {table_name}
                WHERE {where_clause}
                ON CONFLICT DO NOTHING
            """)
            db.execute(migration_query, params)
            db.commit()
        except Exception as mig_exc:
            db.rollback()
            migration_status = "error"
            error_message = str(mig_exc)
        # Get final count in master table
        final_count_query = text(f"SELECT COUNT(*) FROM {master_table}")
        final_result = db.execute(final_count_query).fetchone()
        final_count = final_result[0] if final_result else 0
        # Insert migration history record
        filters_json = request.dict(exclude_unset=True)
        migrated_by = user.username if user is not None and hasattr(user, 'username') else None
        db.execute(text("""
            INSERT INTO migration_history (
                staging_table, master_table, migrated_by, filters, records_migrated, final_master_count, migration_timestamp, status, error_message
            ) VALUES (
                :staging_table, :master_table, :migrated_by, :filters, :records_migrated, :final_master_count, NOW(), :status, :error_message
            )
        """), {
            'staging_table': table_name,
            'master_table': master_table,
            'migrated_by': migrated_by,
            'filters': filters_json,
            'records_migrated': records_to_migrate,
            'final_master_count': final_count,
            'status': migration_status,
            'error_message': error_message
        })
        db.commit()
        if migration_status == "error":
            raise HTTPException(status_code=500, detail=f"Migration failed: {error_message}")
        return StagingMigrationResponse(
            table_name=table_name,
            master_table=master_table,
            records_migrated=records_to_migrate,
            final_master_count=final_count,
            migration_timestamp=datetime.now(),
            applied_filters=request.dict(exclude_unset=True)
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error migrating staging data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error migrating staging data: {str(e)}")

@router.get("/staging/tables")
async def get_staging_tables(db: Session = Depends(get_db)):
    """
    Get list of available staging tables
    """
    try:
        query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%_staging'
            ORDER BY table_name
        """)
        
        result = db.execute(query)
        tables = [row[0] for row in result.fetchall()]
        
        return {
            "staging_tables": tables,
            "total_count": len(tables)
        }
        
    except Exception as e:
        logger.error(f"Error getting staging tables: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting staging tables: {str(e)}")

@router.get("/staging/summary/{table_name}")
async def get_staging_summary(
    table_name: str,
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for a staging table
    """
    try:
        # Validate table name
        valid_staging_tables = [
            'onspd_staging', 'code_point_open_staging', 'os_open_names_staging',
            'os_open_map_local_staging', 'os_open_usrn_staging', 'os_open_uprn_staging',
            'nndr_properties_staging', 'nndr_ratepayers_staging', 'valuations_staging',
            'lad_boundaries_staging'
        ]
        
        if table_name not in valid_staging_tables:
            raise HTTPException(status_code=400, detail=f"Invalid table name. Must be one of: {valid_staging_tables}")
        
        # Get summary statistics
        summary_query = text(f"""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT batch_id) as unique_batches,
                COUNT(DISTINCT source_name) as unique_sources,
                COUNT(DISTINCT session_id) as unique_sessions,
                MIN(upload_timestamp) as earliest_upload,
                MAX(upload_timestamp) as latest_upload
            FROM {table_name}
        """)
        
        result = db.execute(summary_query).fetchone()
        
        return {
            "table_name": table_name,
            "total_records": result[0],
            "unique_batches": result[1],
            "unique_sources": result[2],
            "unique_sessions": result[3],
            "earliest_upload": result[4],
            "latest_upload": result[5]
        }
        
    except Exception as e:
        logger.error(f"Error getting staging summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting staging summary: {str(e)}") 

@router.get("/users", response_model=List[Dict[str, Any]])
def list_users(db: Session = Depends(get_db), user: User = Depends(require_admin_or_power)):
    users = db.query(User).all()
    return [
        {"id": u.id, "username": u.username, "role": u.role, "email": u.email, "created_at": u.created_at}
        for u in users
    ]

@router.post("/users", response_model=Dict[str, Any])
def create_user(new_user: Dict[str, str], db: Session = Depends(get_db), user: User = Depends(require_admin_or_power)):
    if db.query(User).filter(User.username == new_user["username"]).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    from app.services.auth_service import get_password_hash
    user_obj = User(
        username=new_user["username"],
        password_hash=get_password_hash(new_user["password"]),
        role=new_user["role"],
        email=new_user.get("email")
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return {"id": user_obj.id, "username": user_obj.username, "role": user_obj.role, "email": user_obj.email}

@router.put("/users/{user_id}", response_model=Dict[str, Any])
def update_user(user_id: int, update: Dict[str, str], db: Session = Depends(get_db), user: User = Depends(require_admin_or_power)):
    user_obj = db.query(User).filter(User.id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    if "password" in update:
        from app.services.auth_service import get_password_hash
        user_obj.password_hash = get_password_hash(update["password"])
    if "role" in update:
        user_obj.role = update["role"]
    if "email" in update:
        user_obj.email = update["email"]
    db.commit()
    db.refresh(user_obj)
    return {"id": user_obj.id, "username": user_obj.username, "role": user_obj.role, "email": user_obj.email}

@router.delete("/users/{user_id}", response_model=Dict[str, Any])
def delete_user(user_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin_or_power)):
    user_obj = db.query(User).filter(User.id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user_obj)
    db.commit()
    return {"result": "deleted"} 

@router.get("/user/me")
def get_current_user_info(user: User = Depends(get_current_user)):
    """
    Return the current authenticated user's info for frontend session restore.
    """
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "email": user.email,
        "created_at": user.created_at
    } 

@router.get("/master/preview/{table_name}")
async def preview_master_data(
    table_name: str,
    page_size: int = Query(100, description="Number of records per page (page size)"),
    offset: int = Query(0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Preview master data with pagination.
    """
    try:
        valid_master_tables = [
            'onspd', 'code_point_open', 'os_open_names',
            'os_open_map_local', 'os_open_usrn', 'os_open_uprn',
            'nndr_properties', 'nndr_ratepayers', 'valuations',
            'lad_boundaries'
        ]
        if table_name not in valid_master_tables:
            raise HTTPException(status_code=400, detail=f"Invalid table name. Must be one of: {valid_master_tables}")
        # Get total count
        count_query = text(f"SELECT COUNT(*) as total_count FROM {table_name}")
        count_result = db.execute(count_query).fetchone()
        total_count = count_result[0] if count_result else 0
        # Get sample data
        sample_query = text(f"SELECT * FROM {table_name} ORDER BY 1 LIMIT :page_size OFFSET :offset")
        params = {'page_size': page_size, 'offset': offset}
        result = db.execute(sample_query, params)
        columns = result.keys()
        sample_data = [dict(zip(columns, row)) for row in result.fetchall()]
        return {
            'table_name': table_name,
            'total_count': total_count,
            'sample_data': sample_data
        }
    except Exception as e:
        logger.error(f"Error previewing master data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error previewing master data: {str(e)}") 

@router.get("/master/tables")
def get_master_tables():
    """
    Return the list of master tables and their relationships (edges).
    """
    master_tables = [
        "onspd",
        "code_point_open",
        "os_open_names",
        "os_open_map_local",
        "os_open_usrn",
        "os_open_uprn",
        "nndr_properties",
        "nndr_ratepayers",
        "valuations",
        "lad_boundaries"
    ]
    table_edges = [
        {"source": "onspd", "target": "code_point_open", "label": "postcode"},
        {"source": "nndr_properties", "target": "onspd", "label": "postcode"},
        {"source": "nndr_ratepayers", "target": "nndr_properties", "label": "property_id"},
        {"source": "valuations", "target": "nndr_properties", "label": "property_id"},
        {"source": "os_open_names", "target": "onspd", "label": "postcode"},
        {"source": "os_open_uprn", "target": "onspd", "label": "postcode"},
        {"source": "os_open_usrn", "target": "os_open_map_local", "label": "usrn"},
        # Add more as needed
    ]
    return {"master_tables": master_tables, "table_edges": table_edges} 

@router.get("/staging/migration_history")
def get_migration_history(
    staging_table: Optional[str] = Query(None),
    master_table: Optional[str] = Query(None),
    migrated_by: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_power)
):
    """
    Fetch paginated migration history with optional filters.
    """
    where_clauses = []
    params = {}
    if staging_table:
        where_clauses.append("staging_table = :staging_table")
        params['staging_table'] = staging_table
    if master_table:
        where_clauses.append("master_table = :master_table")
        params['master_table'] = master_table
    if migrated_by:
        where_clauses.append("migrated_by = :migrated_by")
        params['migrated_by'] = migrated_by
    if status:
        where_clauses.append("status = :status")
        params['status'] = status
    where_sql = " AND ".join(where_clauses)
    if where_sql:
        where_sql = "WHERE " + where_sql
    query = text(f"""
        SELECT * FROM migration_history
        {where_sql}
        ORDER BY migration_timestamp DESC
        LIMIT :limit OFFSET :offset
    """)
    params['limit'] = limit
    params['offset'] = offset
    result = db.execute(query, params)
    rows = [dict(row) for row in result.fetchall()]
    # Get total count
    count_query = text(f"SELECT COUNT(*) FROM migration_history {where_sql}")
    count_result = db.execute(count_query, params).fetchone()
    total = count_result[0] if count_result else 0
    return {"history": rows, "total": total, "limit": limit, "offset": offset} 

@router.delete("/staging/purge/{table_name}")
async def purge_staging_table(
    table_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    Purge (truncate) all data from a staging table. Any authenticated user can perform this.
    Also logs the purge event to migration_history.
    """
    valid_staging_tables = [
        'onspd_staging', 'code_point_open_staging', 'os_open_names_staging',
        'os_open_map_local_staging', 'os_open_usrn_staging', 'os_open_uprn_staging',
        'nndr_properties_staging', 'nndr_ratepayers_staging', 'valuations_staging',
        'lad_boundaries_staging'
    ]
    if table_name not in valid_staging_tables:
        raise HTTPException(status_code=400, detail=f"Invalid staging table name. Must be one of: {valid_staging_tables}")
    try:
        # Get count before purge
        count_query = text(f"SELECT COUNT(*) FROM {table_name}")
        count_result = db.execute(count_query).fetchone()
        records_deleted = count_result[0] if count_result else 0
        db.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
        db.commit()
        # Log to migration_history
        db.execute(text("""
            INSERT INTO migration_history (
                staging_table, master_table, migrated_by, filters, records_migrated, final_master_count, migration_timestamp, status, error_message
            ) VALUES (
                :staging_table, NULL, :migrated_by, NULL, :records_migrated, 0, NOW(), :status, NULL
            )
        """), {
            'staging_table': table_name,
            'migrated_by': user.username,
            'records_migrated': records_deleted,
            'status': 'purged'
        })
        db.commit()
        return {"result": "staging table purged", "table": table_name}
    except Exception as e:
        db.rollback()
        logger.error(f"Error purging staging table {table_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error purging staging table: {str(e)}")

@router.delete("/master/purge/{table_name}")
async def purge_master_table(
    table_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_power)
):
    """
    Purge (truncate) all data from a master table. Only admin or power_user can perform this.
    Also logs the purge event to migration_history.
    """
    valid_master_tables = [
        'onspd', 'code_point_open', 'os_open_names',
        'os_open_map_local', 'os_open_usrn', 'os_open_uprn',
        'nndr_properties', 'nndr_ratepayers', 'valuations',
        'lad_boundaries'
    ]
    if table_name not in valid_master_tables:
        raise HTTPException(status_code=400, detail=f"Invalid master table name. Must be one of: {valid_master_tables}")
    try:
        # Get count before purge
        count_query = text(f"SELECT COUNT(*) FROM {table_name}")
        count_result = db.execute(count_query).fetchone()
        records_deleted = count_result[0] if count_result else 0
        db.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
        db.commit()
        # Log to migration_history
        db.execute(text("""
            INSERT INTO migration_history (
                staging_table, master_table, migrated_by, filters, records_migrated, final_master_count, migration_timestamp, status, error_message
            ) VALUES (
                NULL, :master_table, :migrated_by, NULL, :records_migrated, 0, NOW(), :status, NULL
            )
        """), {
            'master_table': table_name,
            'migrated_by': user.username,
            'records_migrated': records_deleted,
            'status': 'purged_master'
        })
        db.commit()
        return {"result": "master table purged", "table": table_name}
    except Exception as e:
        db.rollback()
        logger.error(f"Error purging master table {table_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error purging master table: {str(e)}") 

@router.delete("/staging/delete/{table_name}")
async def delete_staging_data(
    table_name: str,
    request: StagingMigrationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    Delete data from a staging table based on filter criteria (batch_id, source_name, session_id).
    At least one filter must be provided. Any authenticated user can perform this.
    Also logs the deletion event to migration_history.
    """
    valid_staging_tables = [
        'onspd_staging', 'code_point_open_staging', 'os_open_names_staging',
        'os_open_map_local_staging', 'os_open_usrn_staging', 'os_open_uprn_staging',
        'nndr_properties_staging', 'nndr_ratepayers_staging', 'valuations_staging',
        'lad_boundaries_staging'
    ]
    if table_name not in valid_staging_tables:
        raise HTTPException(status_code=400, detail=f"Invalid staging table name. Must be one of: {valid_staging_tables}")
    # Build WHERE clause for filters
    where_conditions = []
    params = {}
    if request.batch_id:
        where_conditions.append("batch_id = :batch_id")
        params['batch_id'] = request.batch_id
    if request.source_name:
        where_conditions.append("source_name = :source_name")
        params['source_name'] = request.source_name
    if request.session_id:
        where_conditions.append("session_id = :session_id")
        params['session_id'] = request.session_id
    if not where_conditions:
        raise HTTPException(status_code=400, detail="At least one filter (batch_id, source_name, session_id) must be provided.")
    where_clause = " AND ".join(where_conditions)
    try:
        # Get count before delete
        count_query = text(f"SELECT COUNT(*) FROM {table_name} WHERE {where_clause}")
        count_result = db.execute(count_query, params).fetchone()
        records_deleted = count_result[0] if count_result else 0
        delete_query = text(f"DELETE FROM {table_name} WHERE {where_clause}")
        result = db.execute(delete_query, params)
        db.commit()
        # Log to migration_history
        db.execute(text("""
            INSERT INTO migration_history (
                staging_table, master_table, migrated_by, filters, records_migrated, final_master_count, migration_timestamp, status, error_message
            ) VALUES (
                :staging_table, NULL, :migrated_by, :filters, :records_migrated, 0, NOW(), :status, NULL
            )
        """), {
            'staging_table': table_name,
            'migrated_by': user.username,
            'filters': request.dict(exclude_unset=True),
            'records_migrated': records_deleted,
            'status': 'deleted'
        })
        db.commit()
        return {"result": "deleted", "table": table_name, "rows_deleted": result.rowcount}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting data from staging table {table_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting data from staging table: {str(e)}") 