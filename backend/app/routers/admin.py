from fastapi import APIRouter, HTTPException, Depends, Query, status, Security
from typing import Optional, List, Dict, Any
from sqlalchemy import text, func
from sqlalchemy.orm import Session
import logging
import json
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

# Test endpoint to verify router is working
@router.get("/test")
async def test_admin_router():
    """Test endpoint to verify admin router is working"""
    return {"message": "Admin router is working", "status": "ok"}

@router.post("/staging/search-tables-simple")
async def search_staging_tables_simple(
    request: dict,
    db: Session = Depends(get_db)
):
    """Simple table search endpoint for testing"""
    try:
        query = request.get("query", "").lower()
        limit = request.get("limit", 10)
        
        # Get actual tables from database
        try:
            # Get tables from staging schema only
            staging_query = text("""
                SELECT table_name, 'staging' as schema_name
                FROM information_schema.tables 
                WHERE table_schema = 'staging' 
                AND table_name NOT LIKE 'staging_%'  -- Exclude system tables
                AND table_name LIKE '%_staging'  -- Only tables ending with _staging
            """)
            
            staging_result = db.execute(staging_query)
            staging_tables = [{"name": row[0], "schema": row[1]} for row in staging_result.fetchall()]
            
            all_tables = staging_tables
            
        except Exception as db_error:
            logger.warning(f"Database query failed, using fallback suggestions: {db_error}")
            # Fallback to hardcoded suggestions if database query fails
            all_tables = [
                {"name": "os_open_uprn_staging", "schema": "staging"},
                {"name": "onspd_staging", "schema": "staging"},
                {"name": "code_point_open_staging", "schema": "staging"},
                {"name": "os_open_names_staging", "schema": "staging"},
                {"name": "os_open_map_local_staging", "schema": "staging"},
                {"name": "os_open_usrn_staging", "schema": "staging"},
                {"name": "nndr_properties_staging", "schema": "staging"},
                {"name": "nndr_ratepayers_staging", "schema": "staging"},
                {"name": "valuations_staging", "schema": "staging"},
                {"name": "lad_boundaries_staging", "schema": "staging"}
            ]
        
        # Build suggestions from actual tables
        suggestions = []
        
        # Add existing tables that match the query
        for table in all_tables:
            if not query or query in table["name"].lower():
                # Calculate similarity score
                similarity = 0.0
                if query:
                    if query in table["name"].lower():
                        similarity = 0.8
                    if table["name"].lower().startswith(query):
                        similarity = 0.9
                    if table["name"].lower() == query:
                        similarity = 1.0
                else:
                    similarity = 0.5  # Default score for no query
                
                suggestions.append({
                    "name": table["name"],
                    "schema": table["schema"],
                    "full_name": f"{table['schema']}.{table['name']}",
                    "type": "existing",
                    "confidence": similarity,
                    "description": f"Existing table in {table['schema']} schema"
                })
        
        # Add AI suggestions for new table creation
        if query and len(query) >= 2:
            # Suggest new table name based on query
            new_table_name = f"{query}_staging"
            suggestions.append({
                "name": new_table_name,
                "schema": "staging",
                "full_name": f"staging.{new_table_name}",
                "type": "ai_suggested",
                "confidence": 0.6,
                "description": f"Create new table: {new_table_name}"
            })
            
            # Add more generic suggestions
            if "data" in query or "upload" in query:
                suggestions.append({
                    "name": f"upload_{query}_staging",
                    "schema": "staging",
                    "full_name": f"staging.upload_{query}_staging",
                    "type": "ai_suggested",
                    "confidence": 0.5,
                    "description": f"Create upload table for {query}"
                })
        
        # Sort by confidence and limit results
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        suggestions = suggestions[:limit]
        
        logger.info(f"Search query '{query}' returned {len(suggestions)} suggestions")
        
        return {
            "suggestions": suggestions,
            "query": query,
            "total_found": len(suggestions),
            "status": "success",
            "allow_new_tables": True  # Always allow new table creation
        }
        
    except Exception as e:
        logger.error(f"Error in search-tables-simple: {str(e)}")
        # Return empty suggestions instead of 404
        return {
            "suggestions": [],
            "query": request.get("query", ""),
            "total_found": 0,
            "status": "success",
            "allow_new_tables": True,
            "error": "Search temporarily unavailable"
        }

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
    Get list of available staging tables from both public and staging schemas
    """
    try:
        # Get tables from public schema (legacy)
        public_query = text("""
            SELECT table_name, 'public' as schema_name
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%_staging'
        """)
        
        # Get tables from staging schema (new)
        staging_query = text("""
            SELECT table_name, 'staging' as schema_name
            FROM information_schema.tables 
            WHERE table_schema = 'staging' 
            AND table_name NOT LIKE 'staging_%'  -- Exclude system tables
        """)
        
        public_result = db.execute(public_query)
        staging_result = db.execute(staging_query)
        
        public_tables = [{"name": row[0], "schema": row[1]} for row in public_result.fetchall()]
        staging_tables = [{"name": row[0], "schema": row[1]} for row in staging_result.fetchall()]
        
        all_tables = public_tables + staging_tables
        
        return {
            "staging_tables": all_tables,
            "total_count": len(all_tables),
            "public_count": len(public_tables),
            "staging_count": len(staging_tables)
        }
        
    except Exception as e:
        logger.error(f"Error getting staging tables: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting staging tables: {str(e)}")

@router.post("/staging/suggest-table-name")
async def suggest_staging_table_name(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Suggest staging table name based on file content and existing tables
    """
    try:
        headers = request.get("headers", [])
        file_name = request.get("file_name", "")
        content_preview = request.get("content_preview", "")
        
        # Get existing staging tables
        query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%_staging'
            ORDER BY table_name
        """)
        
        result = db.execute(query)
        existing_tables = [row[0] for row in result.fetchall()]
        
        # AI-based table name suggestion
        suggested_name = suggest_table_name_ai(headers, file_name, content_preview)
        
        # Find similar existing tables
        similar_tables = find_similar_tables(headers, existing_tables)
        
        # Generate suggestions with confidence scores
        suggestions = []
        
        # Add AI suggestion
        if suggested_name:
            suggestions.append({
                "name": suggested_name,
                "type": "ai_suggested",
                "confidence": 0.9,
                "reason": "AI analysis of file content"
            })
        
        # Add similar existing tables
        for table in similar_tables:
            suggestions.append({
                "name": table["name"],
                "type": "existing_similar",
                "confidence": table["similarity"],
                "reason": f"Similar to existing table ({table['similarity']:.1%} match)"
            })
        
        # Add common patterns
        common_patterns = generate_common_patterns(headers, file_name)
        for pattern in common_patterns:
            suggestions.append({
                "name": pattern["name"],
                "type": "pattern_based",
                "confidence": pattern["confidence"],
                "reason": pattern["reason"]
            })
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {
            "suggestions": suggestions,
            "existing_tables": existing_tables,
            "file_analysis": {
                "headers": headers,
                "file_name": file_name,
                "header_count": len(headers)
            }
        }
        
    except Exception as e:
        logger.error(f"Error suggesting table name: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error suggesting table name: {str(e)}")

def suggest_table_name_ai(headers, file_name, content_preview):
    """AI-based table name suggestion"""
    keywords = " ".join(headers).lower()
    file_lower = file_name.lower()
    
    # Enhanced keyword mapping
    keyword_mappings = {
        'uprn': 'os_open_uprn_staging',
        'usrn': 'os_open_usrn_staging', 
        'postcode': 'onspd_staging',
        'post_code': 'onspd_staging',
        'pcd': 'onspd_staging',
        'pcds': 'onspd_staging',
        'name': 'os_open_names_staging',
        'names_uri': 'os_open_names_staging',
        'geometry': 'os_open_map_local_staging',
        'geom': 'os_open_map_local_staging',
        'boundary': 'lad_boundaries_staging',
        'boundaries': 'lad_boundaries_staging',
        'rateable': 'nndr_properties_staging',
        'rateable_value': 'nndr_properties_staging',
        'valuation': 'valuations_staging',
        'property': 'nndr_properties_staging',
        'ratepayer': 'nndr_ratepayers_staging',
        'business': 'nndr_properties_staging',
        'address': 'os_open_names_staging',
        'street': 'os_open_usrn_staging',
        'coordinate': 'os_open_uprn_staging',
        'latitude': 'os_open_uprn_staging',
        'longitude': 'os_open_uprn_staging',
        'x_coord': 'os_open_uprn_staging',
        'y_coord': 'os_open_uprn_staging'
    }
    
    # Check for exact matches first
    for keyword, table_name in keyword_mappings.items():
        if keyword in keywords or keyword in file_lower:
            return table_name
    
    # Check for partial matches
    for keyword, table_name in keyword_mappings.items():
        if any(keyword in header.lower() for header in headers):
            return table_name
    
    # File name based suggestions
    if 'onspd' in file_lower or 'postcode' in file_lower:
        return 'onspd_staging'
    elif 'uprn' in file_lower:
        return 'os_open_uprn_staging'
    elif 'usrn' in file_lower or 'street' in file_lower:
        return 'os_open_usrn_staging'
    elif 'name' in file_lower:
        return 'os_open_names_staging'
    elif 'boundary' in file_lower:
        return 'lad_boundaries_staging'
    elif 'nndr' in file_lower or 'rate' in file_lower:
        return 'nndr_properties_staging'
    elif 'valuation' in file_lower:
        return 'valuations_staging'
    
    # Default suggestion
    return 'staging_data'

def find_similar_tables(headers, existing_tables):
    """Find existing tables similar to current headers"""
    similar_tables = []
    
    for table in existing_tables:
        # Get table structure from database
        similarity = calculate_table_similarity(headers, table)
        if similarity > 0.3:  # Only include if >30% similar
            similar_tables.append({
                "name": table,
                "similarity": similarity
            })
    
    return similar_tables

def calculate_table_similarity(headers, table_name):
    """Calculate similarity between headers and existing table"""
    # This would ideally query the actual table structure
    # For now, use a simplified approach based on common patterns
    
    header_set = set(h.lower() for h in headers)
    
    # Common field patterns for each table type
    table_patterns = {
        'onspd_staging': {'postcode', 'pcd', 'pcds', 'x_coord', 'y_coord', 'lat', 'long'},
        'os_open_uprn_staging': {'uprn', 'x_coordinate', 'y_coordinate', 'latitude', 'longitude'},
        'os_open_usrn_staging': {'usrn', 'street_type', 'geometry'},
        'os_open_names_staging': {'name', 'names_uri', 'type', 'local_type'},
        'os_open_map_local_staging': {'geometry', 'geom', 'toid'},
        'lad_boundaries_staging': {'boundary', 'geometry', 'name'},
        'nndr_properties_staging': {'rateable', 'property', 'address', 'postcode'},
        'nndr_ratepayers_staging': {'ratepayer', 'name', 'address'},
        'valuations_staging': {'valuation', 'rateable_value', 'property'}
    }
    
    if table_name in table_patterns:
        pattern_set = table_patterns[table_name]
        intersection = header_set.intersection(pattern_set)
        union = header_set.union(pattern_set)
        return len(intersection) / len(union) if union else 0
    
    return 0

def generate_common_patterns(headers, file_name):
    """Generate common naming patterns based on headers"""
    patterns = []
    
    # Count different types of fields
    field_types = {
        'spatial': sum(1 for h in headers if any(x in h.lower() for x in ['coord', 'lat', 'long', 'geometry', 'geom'])),
        'address': sum(1 for h in headers if any(x in h.lower() for x in ['address', 'postcode', 'street'])),
        'property': sum(1 for h in headers if any(x in h.lower() for x in ['property', 'rateable', 'valuation'])),
        'person': sum(1 for h in headers if any(x in h.lower() for x in ['name', 'person', 'ratepayer'])),
        'reference': sum(1 for h in headers if any(x in h.lower() for x in ['uprn', 'usrn', 'id', 'code']))
    }
    
    # Suggest based on dominant field type
    if field_types['spatial'] > 2:
        patterns.append({
            "name": "spatial_data_staging",
            "confidence": 0.7,
            "reason": "Multiple spatial fields detected"
        })
    
    if field_types['address'] > 2:
        patterns.append({
            "name": "address_data_staging", 
            "confidence": 0.7,
            "reason": "Multiple address fields detected"
        })
    
    if field_types['property'] > 2:
        patterns.append({
            "name": "property_data_staging",
            "confidence": 0.7,
            "reason": "Multiple property fields detected"
        })
    
    # File name based patterns
    if file_name:
        base_name = file_name.split('.')[0].lower()
        if base_name not in ['data', 'file', 'upload']:
            patterns.append({
                "name": f"{base_name}_staging",
                "confidence": 0.6,
                "reason": "Based on file name"
            })
    
    return patterns

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

@router.post("/staging/create-table")
async def create_staging_table(
    request: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """Create a new staging table from configuration"""
    try:
        table_name = request.get("table_name", "").strip()
        schema_name = request.get("schema_name", "staging")
        columns = request.get("columns", [])
        
        if not table_name:
            raise HTTPException(status_code=400, detail="Table name is required")
        
        # Validate table name format
        if not table_name.replace("_", "").replace("-", "").isalnum():
            raise HTTPException(status_code=400, detail="Table name can only contain letters, numbers, underscores, and hyphens")
        
        # Ensure table name ends with _staging for consistency
        if not table_name.endswith("_staging"):
            table_name = f"{table_name}_staging"
        
        # Check if table already exists
        check_query = text("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = :schema AND table_name = :table
        """)
        result = db.execute(check_query, {"schema": schema_name, "table": table_name})
        if result.scalar() > 0:
            raise HTTPException(status_code=400, detail=f"Table {schema_name}.{table_name} already exists")
        
        # Build CREATE TABLE SQL
        column_definitions = []
        for col in columns:
            col_name = col.get("name", "").lower().replace(" ", "_")
            col_type = col.get("type", "TEXT").upper()
            
            # Map common types to PostgreSQL types
            if col_type in ["TEXT", "VARCHAR", "STRING"]:
                pg_type = "TEXT"
            elif col_type in ["INTEGER", "INT", "NUMBER"]:
                pg_type = "INTEGER"
            elif col_type in ["DECIMAL", "NUMERIC", "FLOAT"]:
                pg_type = "NUMERIC(10,2)"
            elif col_type in ["DATE"]:
                pg_type = "DATE"
            elif col_type in ["TIMESTAMP", "DATETIME"]:
                pg_type = "TIMESTAMP"
            elif col_type in ["BOOLEAN", "BOOL"]:
                pg_type = "BOOLEAN"
            else:
                pg_type = "TEXT"
            
            column_def = f"{col_name} {pg_type}"
            
            # Add constraints
            if col.get("required", False):
                column_def += " NOT NULL"
            if col.get("primary_key", False):
                column_def += " PRIMARY KEY"
            if col.get("unique", False):
                column_def += " UNIQUE"
            
            column_definitions.append(column_def)
        
        # Add standard metadata columns
        metadata_columns = [
            "source_file TEXT",
            "upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "uploaded_by VARCHAR(100)",
            "batch_id TEXT",
            "session_id TEXT",
            "client_name TEXT DEFAULT 'web_upload'"
        ]
        
        all_columns = column_definitions + metadata_columns
        
        # Create the table
        create_sql = f"""
        CREATE TABLE {schema_name}.{table_name} (
            {', '.join(all_columns)}
        )
        """
        
        logger.info(f"Creating table: {create_sql}")
        db.execute(text(create_sql))
        db.commit()
        
        # Log the operation
        try:
            audit_sql = """
                SELECT staging.log_staging_operation(
                    'CREATE_TABLE',
                    :table_name,
                    :performed_by,
                    :operation_details,
                    :affected_rows
                )
            """
            audit_params = {
                'table_name': table_name,
                'performed_by': user.username,
                'operation_details': json.dumps({
                    'schema': schema_name,
                    'columns': columns,
                    'full_sql': create_sql
                }),
                'affected_rows': 0
            }
            db.execute(text(audit_sql), audit_params)
            db.commit()
        except Exception as audit_error:
            logger.warning(f"Failed to log table creation: {audit_error}")
        
        return {
            "success": True,
            "table_name": table_name,
            "schema_name": schema_name,
            "full_name": f"{schema_name}.{table_name}",
            "columns_created": len(all_columns),
            "message": f"Table {schema_name}.{table_name} created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating staging table: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create table: {str(e)}")

@router.post("/staging/configs")
async def save_staging_config(
    request: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    Save a staging table configuration
    """
    try:
        config_data = {
            "name": request.get("name"),
            "description": request.get("description", ""),
            "file_pattern": request.get("file_pattern", ""),
            "file_type": request.get("file_type", "csv"),
            "staging_table_name": request.get("staging_table_name"),
            "source_schema": request.get("source_schema", "public"),
            "target_schema": request.get("target_schema", "staging"),
            "created_by": user.username,
            "settings": request.get("settings", {}),
            "column_mappings": request.get("column_mappings", [])
        }
        
        # Insert into staging_configs table
        config_query = text("""
            INSERT INTO staging_configs (
                name, description, file_pattern, file_type, staging_table_name,
                source_schema, target_schema, created_by, settings
            ) VALUES (
                :name, :description, :file_pattern, :file_type, :staging_table_name,
                :source_schema, :target_schema, :created_by, :settings
            ) RETURNING id
        """)
        
        result = db.execute(config_query, config_data)
        config_id = result.fetchone()[0]
        
        # Insert column mappings
        if config_data["column_mappings"]:
            for mapping in config_data["column_mappings"]:
                mapping_query = text("""
                    INSERT INTO column_mappings (
                        config_id, source_column_name, target_column_name,
                        target_column_type, mapping_type, is_required,
                        default_value, transformation_config
                    ) VALUES (
                        :config_id, :source_column, :target_column,
                        :data_type, :mapping_type, :is_required,
                        :default_value, :transformation_config
                    )
                """)
                
                db.execute(mapping_query, {
                    "config_id": config_id,
                    "source_column": mapping.get("sourceColumn"),
                    "target_column": mapping.get("targetColumn"),
                    "data_type": mapping.get("dataType", "text"),
                    "mapping_type": mapping.get("mappingType", "direct"),
                    "is_required": mapping.get("isRequired", False),
                    "default_value": mapping.get("defaultValue", ""),
                    "transformation_config": mapping.get("transformationConfig", {})
                })
        
        db.commit()
        
        return {
            "id": config_id,
            "message": "Configuration saved successfully",
            "config": config_data
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving staging config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving configuration: {str(e)}")

@router.get("/staging/configs")
async def get_staging_configs(
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    Get all staging table configurations
    """
    try:
        query = text("""
            SELECT 
                sc.id, sc.name, sc.description, sc.file_pattern, sc.file_type,
                sc.staging_table_name, sc.created_by, sc.created_at, sc.settings,
                COUNT(cm.id) as mapping_count
            FROM staging_configs sc
            LEFT JOIN column_mappings cm ON sc.id = cm.config_id
            WHERE sc.is_active = true
            GROUP BY sc.id, sc.name, sc.description, sc.file_pattern, sc.file_type,
                     sc.staging_table_name, sc.created_by, sc.created_at, sc.settings
            ORDER BY sc.created_at DESC
        """)
        
        result = db.execute(query)
        configs = []
        
        for row in result.fetchall():
            configs.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "file_pattern": row[3],
                "file_type": row[4],
                "staging_table_name": row[5],
                "created_by": row[6],
                "created_at": row[7],
                "settings": row[8],
                "mapping_count": row[9]
            })
        
        return {
            "configs": configs,
            "total_count": len(configs)
        }
        
    except Exception as e:
        logger.error(f"Error getting staging configs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting configurations: {str(e)}")

@router.get("/staging/configs/{config_id}")
async def get_staging_config(
    config_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    Get a specific staging table configuration with column mappings
    """
    try:
        # Get config details
        config_query = text("""
            SELECT 
                id, name, description, file_pattern, file_type,
                staging_table_name, created_by, created_at, settings
            FROM staging_configs
            WHERE id = :config_id AND is_active = true
        """)
        
        config_result = db.execute(config_query, {"config_id": config_id})
        config_row = config_result.fetchone()
        
        if not config_row:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        # Get column mappings
        mappings_query = text("""
            SELECT 
                source_column_name, target_column_name, target_column_type,
                mapping_type, is_required, default_value, transformation_config
            FROM column_mappings
            WHERE config_id = :config_id
            ORDER BY display_order, source_column_name
        """)
        
        mappings_result = db.execute(mappings_query, {"config_id": config_id})
        mappings = []
        
        for row in mappings_result.fetchall():
            mappings.append({
                "sourceColumn": row[0],
                "targetColumn": row[1],
                "dataType": row[2],
                "mappingType": row[3],
                "isRequired": row[4],
                "defaultValue": row[5],
                "transformationConfig": row[6]
            })
        
        return {
            "id": config_row[0],
            "name": config_row[1],
            "description": config_row[2],
            "file_pattern": config_row[3],
            "file_type": config_row[4],
            "staging_table_name": config_row[5],
            "created_by": config_row[6],
            "created_at": config_row[7],
            "settings": config_row[8],
            "column_mappings": mappings
        }
        
    except Exception as e:
        logger.error(f"Error getting staging config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting configuration: {str(e)}")

@router.post("/staging/configs/match")
async def match_staging_configs(
    request: dict,
    db: Session = Depends(get_db)
):
    """Match uploaded file with existing staging configurations"""
    headers = request.get("headers", [])
    file_name = request.get("file_name", "")
    file_type = request.get("file_type", "")
    
    # Get all active configurations
    configs_query = text("""
        SELECT id, name, description, file_pattern, file_type, staging_table_name, 
               settings, created_at
        FROM staging_configs 
        WHERE is_active = true
        ORDER BY created_at DESC
    """)
    
    result = db.execute(configs_query)
    all_configs = []
    
    for row in result.fetchall():
        config = {
            "config_id": str(row[0]),
            "config_name": row[1],
            "description": row[2],
            "file_pattern": row[3],
            "file_type": row[4],
            "staging_table_name": row[5],
            "settings": row[6] if row[6] else {},
            "created_at": row[7].isoformat() if row[7] else None
        }
        
        # Calculate similarity score
        similarity = calculate_config_similarity(headers, file_name, file_type, config)
        config["similarity"] = similarity
        
        all_configs.append(config)
    
    # Sort by similarity (highest first)
    all_configs.sort(key=lambda x: x["similarity"], reverse=True)
    
    # Find best match (≥75% threshold)
    best_match = None
    if all_configs and all_configs[0]["similarity"] >= 0.75:
        best_match = all_configs[0]
    
    # Filter configs with ≥50% similarity for display
    similar_configs = [c for c in all_configs if c["similarity"] >= 0.5]
    
    return {
        "configs": similar_configs,
        "best_match": best_match,
        "total_configs": len(all_configs),
        "file_info": {
            "headers_count": len(headers),
            "file_name": file_name,
            "file_type": file_type
        }
    }

def calculate_config_similarity(headers, file_name, file_type, config):
    """Enhanced similarity calculation with 75% threshold logic"""
    score = 0.0
    
    # Header similarity (weighted by importance)
    header_similarity = calculate_header_similarity(headers, config.get("settings", {}).get("headers", []))
    score += header_similarity * 0.6  # 60% weight for headers
    
    # File pattern matching
    if config.get("file_pattern") and file_name:
        pattern_match = calculate_pattern_match(file_name, config["file_pattern"])
        score += pattern_match * 0.2  # 20% weight for file patterns
    
    # File type matching
    if config.get("file_type") == file_type:
        score += 0.1  # 10% weight for file type
    
    # Content analysis matching
    content_similarity = analyze_content_similarity(headers, config)
    score += content_similarity * 0.1  # 10% weight for content
    
    return min(score, 1.0)

def calculate_header_similarity(source_headers, config_headers):
    """Calculate header similarity with semantic matching"""
    if not config_headers:
        return 0.0
    
    source_set = set(h.lower() for h in source_headers)
    config_set = set(h.lower() for h in config_headers)
    
    # Exact matches
    exact_matches = len(source_set.intersection(config_set))
    
    # Semantic matches (using AI analysis)
    semantic_matches = calculate_semantic_matches(source_headers, config_headers)
    
    total_possible = max(len(source_headers), len(config_headers))
    similarity = (exact_matches + semantic_matches * 0.8) / total_possible
    
    return similarity

def calculate_pattern_match(file_name, pattern):
    """Calculate file pattern match score"""
    if not pattern or not file_name:
        return 0.0
    
    # Simple pattern matching (can be enhanced with regex)
    file_lower = file_name.lower()
    pattern_lower = pattern.lower()
    
    # Exact pattern match
    if pattern_lower in file_lower:
        return 1.0
    
    # Partial pattern match
    pattern_words = pattern_lower.replace('*', '').replace('?', '').split()
    file_words = file_lower.replace('.', ' ').replace('_', ' ').split()
    
    matches = sum(1 for word in pattern_words if any(word in fw for fw in file_words))
    return matches / len(pattern_words) if pattern_words else 0.0

def calculate_semantic_matches(source_headers, config_headers):
    """Calculate semantic matches between headers"""
    if not source_headers or not config_headers:
        return 0
    
    # Common government data field mappings
    semantic_mappings = {
        'uprn': ['uprn', 'property_id', 'building_id', 'unique_property_reference'],
        'postcode': ['postcode', 'post_code', 'zip', 'postal_code'],
        'address': ['address', 'street_address', 'property_address', 'location'],
        'rateable_value': ['rateable_value', 'rateable', 'value', 'valuation'],
        'business_type': ['business_type', 'property_type', 'use_type', 'category'],
        'latitude': ['latitude', 'lat', 'y_coordinate'],
        'longitude': ['longitude', 'long', 'x_coordinate'],
        'ward': ['ward', 'electoral_ward', 'administrative_ward'],
        'constituency': ['constituency', 'parliamentary_constituency', 'electoral_area']
    }
    
    matches = 0
    for source_header in source_headers:
        source_lower = source_header.lower()
        for semantic_group, variations in semantic_mappings.items():
            if source_lower in variations:
                # Check if any config header matches this semantic group
                for config_header in config_headers:
                    config_lower = config_header.lower()
                    if config_lower in variations:
                        matches += 1
                        break
                break
    
    return matches

def analyze_content_similarity(headers, config):
    """Analyze content similarity between headers and config"""
    if not headers:
        return 0.0
    
    # Check for government data indicators
    government_keywords = [
        'uprn', 'usrn', 'toid', 'lad', 'ward', 'constituency', 'parish',
        'rateable', 'valuation', 'business', 'property', 'address',
        'postcode', 'post_code', 'local_authority', 'council', 'borough',
        'district', 'county', 'region', 'boundary', 'geometry'
    ]
    
    source_indicators = sum(1 for header in headers 
                           if any(keyword in header.lower() for keyword in government_keywords))
    
    # If config has government indicators and source has them too, boost similarity
    if source_indicators > 0:
        return min(source_indicators / len(headers), 1.0)
    
    return 0.0

@router.post("/staging/suggest-actions")
async def suggest_upload_actions(
    request: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    Suggest actions after file selection (save config, pick existing, etc.)
    """
    try:
        headers = request.get("headers", [])
        file_name = request.get("file_name", "")
        file_type = request.get("file_type", "")
        content_preview = request.get("content_preview", "")
        
        # Get existing configurations
        existing_configs = []
        
        # Try to get existing configurations from staging_configs table
        try:
            configs_query = text("""
                SELECT config_id, config_name, headers, file_patterns, created_at, created_by
                FROM staging.staging_configs 
                WHERE created_by = :user_id
                ORDER BY created_at DESC
            """)
            
            result = db.execute(configs_query, {"user_id": user.id})
            
            for row in result.fetchall():
                try:
                    config_headers = json.loads(row[2]) if row[2] else []
                    config_patterns = json.loads(row[3]) if row[3] else []
                    
                    # Calculate similarity with current file
                    similarity = calculate_config_similarity(headers, file_name, file_type, {
                        "headers": config_headers,
                        "file_patterns": config_patterns
                    })
                    
                    if similarity > 0.3:  # Only show relevant configs
                        existing_configs.append({
                            "config_id": row[0],
                            "config_name": row[1],
                            "similarity": similarity,
                            "created_at": row[4],
                            "created_by": row[5]
                        })
                except Exception as e:
                    logger.warning(f"Error processing config {row[0]}: {e}")
                    continue
            
            # Sort by similarity
            existing_configs.sort(key=lambda x: x["similarity"], reverse=True)
            
        except Exception as e:
            logger.warning(f"Could not query staging_configs table: {e}")
            # Continue without existing configs
        
        # Generate suggestions
        suggestions = []
        
        # Always suggest saving a new config
        suggestions.append({
            "action": "save_config",
            "title": "Save Configuration",
            "description": "Save current mapping configuration for future use",
            "priority": "high",
            "icon": "save"
        })
        
        # Suggest using existing configs if available
        if existing_configs:
            best_config = existing_configs[0]
            if best_config["similarity"] > 0.7:
                suggestions.append({
                    "action": "use_existing",
                    "title": f"Use '{best_config['config_name']}'",
                    "description": f"High similarity ({best_config['similarity']:.1%}) with existing configuration",
                    "priority": "high",
                    "icon": "check",
                    "config_id": best_config["config_id"]
                })
            elif best_config["similarity"] > 0.5:
                suggestions.append({
                    "action": "use_existing",
                    "title": f"Consider '{best_config['config_name']}'",
                    "description": f"Moderate similarity ({best_config['similarity']:.1%}) with existing configuration",
                    "priority": "medium",
                    "icon": "info",
                    "config_id": best_config["config_id"]
                })
        
        # Suggest AI analysis if file is complex
        if len(headers) > 10 or file_type in ['zip', 'gml', 'shapefile']:
            suggestions.append({
                "action": "ai_analysis",
                "title": "AI Analysis",
                "description": "Get AI-powered insights and recommendations",
                "priority": "medium",
                "icon": "brain"
            })
        
        # Suggest proceeding with upload
        suggestions.append({
            "action": "proceed_upload",
            "title": "Proceed with Upload",
            "description": "Continue with current configuration",
            "priority": "low",
            "icon": "upload"
        })
        
        return {
            "suggestions": suggestions,
            "existing_configs": existing_configs[:5],  # Top 5 most similar
            "file_analysis": {
                "headers": headers,
                "file_name": file_name,
                "file_type": file_type,
                "header_count": len(headers)
            }
        }
        
    except Exception as e:
        logger.error(f"Error suggesting upload actions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error suggesting upload actions: {str(e)}")

@router.post("/staging/generate-mappings")
async def generate_column_mappings(
    request: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    Generate AI-powered column mappings for a staging table
    """
    try:
        headers = request.get("headers", [])
        staging_table_name = request.get("staging_table_name", "")
        file_name = request.get("file_name", "")
        content_preview = request.get("content_preview", "")
        
        # Generate mappings based on table type
        mappings = generate_ai_column_mappings(headers, staging_table_name, file_name, content_preview)
        
        # Get existing table structure if table exists
        existing_columns = []
        if staging_table_name:
            try:
                columns_query = text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = :table_name 
                    AND table_schema = 'public'
                    AND column_name NOT IN ('source_name', 'upload_user', 'upload_timestamp', 'batch_id', 'source_file', 'file_size', 'file_modified', 'session_id', 'client_name')
                    ORDER BY ordinal_position
                """)
                
                result = db.execute(columns_query, {"table_name": staging_table_name})
                existing_columns = [{"name": row[0], "type": row[1]} for row in result.fetchall()]
            except Exception as e:
                logger.warning(f"Could not get existing table structure for {staging_table_name}: {e}")
        
        return {
            "mappings": mappings,
            "staging_table_name": staging_table_name,
            "existing_columns": existing_columns,
            "match_status": calculate_mapping_match_status(headers, mappings, existing_columns),
            "suggestions": generate_mapping_suggestions(headers, staging_table_name)
        }
        
    except Exception as e:
        logger.error(f"Error generating column mappings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating mappings: {str(e)}")

def generate_ai_column_mappings(headers, staging_table_name, file_name, content_preview):
    """Generate AI-powered column mappings"""
    mappings = []
    
    # Get table-specific mapping patterns
    table_patterns = get_table_mapping_patterns(staging_table_name)
    
    # Check if this is a new table (no existing patterns)
    is_new_table = not table_patterns or staging_table_name not in [
        'onspd_staging', 'os_open_uprn_staging', 'os_open_usrn_staging', 
        'os_open_names_staging', 'nndr_properties_staging', 'nndr_ratepayers_staging',
        'valuations_staging', 'lad_boundaries_staging'
    ]
    
    for i, header in enumerate(headers):
        mapping = {
            "id": f"mapping_{i}",
            "sourceColumn": header,
            "targetColumn": "",
            "mappingType": "direct",
            "dataType": "text",
            "isRequired": False,
            "defaultValue": "",
            "confidence": 0.0,
            "matchStatus": "unmatched",  # unmatched, partial, exact, suggested, new_table
            "reason": ""
        }
        
        # Find best match for this header
        best_match = find_best_column_match(header, table_patterns, staging_table_name)
        
        if best_match:
            mapping.update(best_match)
        else:
            # Generate a sensible default mapping
            default_column_name = generate_default_column_name(header)
            inferred_data_type = infer_data_type(header, content_preview)
            
            mapping["targetColumn"] = default_column_name
            mapping["dataType"] = inferred_data_type
            mapping["matchStatus"] = "new_table" if is_new_table else "suggested"
            mapping["confidence"] = 0.8 if is_new_table else 0.5
            mapping["reason"] = "AI-generated mapping for new table" if is_new_table else "AI-generated default mapping"
        
        mappings.append(mapping)
    
    return mappings

def get_table_mapping_patterns(staging_table_name):
    """Get mapping patterns for specific table types"""
    patterns = {
        'onspd_staging': {
            'pcd': {'target': 'pcd', 'type': 'varchar(8)', 'required': True},
            'pcd2': {'target': 'pcd2', 'type': 'varchar(8)', 'required': False},
            'pcds': {'target': 'pcds', 'type': 'varchar(8)', 'required': True},
            'x_coord': {'target': 'x_coord', 'type': 'numeric(10,6)', 'required': False},
            'y_coord': {'target': 'y_coord', 'type': 'numeric(10,6)', 'required': False},
            'lat': {'target': 'lat', 'type': 'numeric(10,6)', 'required': False},
            'long': {'target': 'long', 'type': 'numeric(10,6)', 'required': False},
            'postcode': {'target': 'pcds', 'type': 'varchar(8)', 'required': True},
            'post_code': {'target': 'pcds', 'type': 'varchar(8)', 'required': True}
        },
        'os_open_uprn_staging': {
            'uprn': {'target': 'uprn', 'type': 'bigint', 'required': True},
            'x_coordinate': {'target': 'x_coordinate', 'type': 'text', 'required': False},
            'y_coordinate': {'target': 'y_coordinate', 'type': 'text', 'required': False},
            'latitude': {'target': 'latitude', 'type': 'text', 'required': False},
            'longitude': {'target': 'longitude', 'type': 'text', 'required': False},
            'x_coord': {'target': 'x_coordinate', 'type': 'text', 'required': False},
            'y_coord': {'target': 'y_coordinate', 'type': 'text', 'required': False}
        },
        'os_open_usrn_staging': {
            'usrn': {'target': 'usrn', 'type': 'text', 'required': True},
            'street_type': {'target': 'street_type', 'type': 'text', 'required': False},
            'geometry': {'target': 'geometry', 'type': 'geometry', 'required': False},
            'geom': {'target': 'geometry', 'type': 'geometry', 'required': False}
        },
        'os_open_names_staging': {
            'name': {'target': 'name1', 'type': 'text', 'required': False},
            'name1': {'target': 'name1', 'type': 'text', 'required': False},
            'names_uri': {'target': 'names_uri', 'type': 'text', 'required': False},
            'type': {'target': 'type', 'type': 'text', 'required': False},
            'local_type': {'target': 'local_type', 'type': 'text', 'required': False}
        },
        'nndr_properties_staging': {
            'rateable_value': {'target': 'rateable_value', 'type': 'text', 'required': False},
            'property_address': {'target': 'address_full', 'type': 'text', 'required': False},
            'address': {'target': 'address_full', 'type': 'text', 'required': False},
            'postcode': {'target': 'postcode', 'type': 'text', 'required': False},
            'uprn': {'target': 'uprn', 'type': 'text', 'required': False},
            'property_id': {'target': 'ba_reference', 'type': 'text', 'required': False}
        },
        'nndr_ratepayers_staging': {
            'ratepayer': {'target': 'ratepayer_name', 'type': 'text', 'required': False},
            'name': {'target': 'ratepayer_name', 'type': 'text', 'required': False},
            'address': {'target': 'ratepayer_address', 'type': 'text', 'required': False}
        },
        'valuations_staging': {
            'valuation': {'target': 'rateable_value', 'type': 'text', 'required': False},
            'rateable_value': {'target': 'rateable_value', 'type': 'text', 'required': False},
            'property': {'target': 'ba_reference', 'type': 'text', 'required': False},
            'effective_date': {'target': 'effective_date', 'type': 'text', 'required': False}
        },
        'lad_boundaries_staging': {
            'boundary': {'target': 'boundary_name', 'type': 'text', 'required': False},
            'geometry': {'target': 'geometry', 'type': 'geometry', 'required': False},
            'geom': {'target': 'geometry', 'type': 'geometry', 'required': False},
            'name': {'target': 'boundary_name', 'type': 'text', 'required': False},
            'lad_code': {'target': 'lad_code', 'type': 'text', 'required': False}
        }
    }
    
    return patterns.get(staging_table_name, {})

def find_best_column_match(header, patterns, staging_table_name):
    """Find the best matching column for a header"""
    header_lower = header.lower()
    
    # Check for exact matches first
    for pattern_key, pattern_info in patterns.items():
        if header_lower == pattern_key.lower():
            return {
                "targetColumn": pattern_info["target"],
                "dataType": pattern_info["type"],
                "isRequired": pattern_info.get("required", False),
                "confidence": 1.0,
                "matchStatus": "exact",
                "reason": f"Exact match for {staging_table_name}"
            }
    
    # Check for partial matches
    for pattern_key, pattern_info in patterns.items():
        if pattern_key.lower() in header_lower or header_lower in pattern_key.lower():
            return {
                "targetColumn": pattern_info["target"],
                "dataType": pattern_info["type"],
                "isRequired": pattern_info.get("required", False),
                "confidence": 0.8,
                "matchStatus": "partial",
                "reason": f"Partial match: '{header}' contains '{pattern_key}'"
            }
    
    # Check for semantic matches
    semantic_matches = {
        'postcode': ['postcode', 'post_code', 'pcd', 'pcds'],
        'address': ['address', 'property_address', 'full_address'],
        'name': ['name', 'names', 'title', 'description'],
        'value': ['value', 'amount', 'rateable_value', 'valuation'],
        'coordinate': ['coordinate', 'coord', 'x_coord', 'y_coord', 'lat', 'long'],
        'geometry': ['geometry', 'geom', 'shape', 'polygon'],
        'id': ['id', 'identifier', 'reference', 'code']
    }
    
    for semantic_key, semantic_terms in semantic_matches.items():
        if any(term in header_lower for term in semantic_terms):
            # Find corresponding pattern
            for pattern_key, pattern_info in patterns.items():
                if semantic_key in pattern_key.lower():
                    return {
                        "targetColumn": pattern_info["target"],
                        "dataType": pattern_info["type"],
                        "isRequired": pattern_info.get("required", False),
                        "confidence": 0.6,
                        "matchStatus": "semantic",
                        "reason": f"Semantic match: '{header}' relates to '{semantic_key}'"
                    }
    
    return None

def generate_default_column_name(header):
    """Generate a default column name from header"""
    # Clean and normalize the header
    clean_name = header.lower().replace(' ', '_').replace('-', '_')
    clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
    
    # Remove common prefixes/suffixes
    prefixes_to_remove = ['field_', 'column_', 'data_']
    for prefix in prefixes_to_remove:
        if clean_name.startswith(prefix):
            clean_name = clean_name[len(prefix):]
    
    return clean_name or 'column_' + str(hash(header) % 1000)

def infer_data_type(header, content_preview):
    """Infer data type from header and content"""
    header_lower = header.lower()
    
    # Check for geometry/geospatial fields first
    geometry_keywords = ['geometry', 'geom', 'shape', 'polygon', 'point', 'line', 'boundary', 'coordinates', 'lat', 'long', 'latitude', 'longitude', 'x_coord', 'y_coord', 'x_coordinate', 'y_coordinate']
    if any(keyword in header_lower for keyword in geometry_keywords):
        return 'geometry'
    
    # Check for date/time fields
    date_keywords = ['date', 'time', 'created', 'updated', 'modified', 'timestamp', 'effective', 'expiry']
    if any(keyword in header_lower for keyword in date_keywords):
        return 'timestamp'
    
    # Check for numeric fields
    numeric_keywords = ['amount', 'value', 'price', 'cost', 'rate', 'total', 'sum', 'average', 'count', 'number', 'quantity', 'size', 'length', 'width', 'height', 'area', 'volume']
    if any(keyword in header_lower for keyword in numeric_keywords):
        # Check if it's likely decimal or integer
        if any(keyword in header_lower for keyword in ['amount', 'value', 'price', 'cost', 'rate', 'total', 'sum', 'average']):
            return 'decimal'
        else:
            return 'integer'
    
    # Check for ID/reference fields
    id_keywords = ['id', 'code', 'reference', 'uprn', 'usrn', 'pcd', 'postcode']
    if any(keyword in header_lower for keyword in id_keywords):
        return 'text'  # Most IDs are text to preserve leading zeros
    
    # Check for boolean fields
    boolean_keywords = ['flag', 'is_', 'has_', 'active', 'enabled', 'valid', 'verified']
    if any(keyword in header_lower for keyword in boolean_keywords):
        return 'boolean'
    
    # Default to text for everything else
    return 'text'

def calculate_mapping_match_status(headers, mappings, existing_columns):
    """Calculate overall match status for the mapping"""
    if not existing_columns:
        # Check if this is a new table with good AI-generated mappings
        new_table_mappings = sum(1 for m in mappings if m["matchStatus"] == "new_table")
        suggested_mappings = sum(1 for m in mappings if m["matchStatus"] == "suggested")
        
        if new_table_mappings > 0:
            return {
                "status": "new_table",
                "confidence": 0.85,
                "color": "blue",
                "message": f"New table - {new_table_mappings} AI-generated mappings"
            }
        elif suggested_mappings > 0:
            return {
                "status": "suggested",
                "confidence": 0.7,
                "color": "purple",
                "message": f"Suggested mappings - {suggested_mappings} AI-generated"
            }
        else:
            return {
                "status": "new_table",
                "confidence": 0.6,
                "color": "blue",
                "message": "New table - Basic mappings"
            }
    
    # Calculate match percentages for existing tables
    exact_matches = sum(1 for m in mappings if m["matchStatus"] == "exact")
    partial_matches = sum(1 for m in mappings if m["matchStatus"] == "partial")
    semantic_matches = sum(1 for m in mappings if m["matchStatus"] == "semantic")
    suggested_mappings = sum(1 for m in mappings if m["matchStatus"] == "suggested")
    unmatched = sum(1 for m in mappings if m["matchStatus"] == "unmatched")
    
    total = len(mappings)
    
    # Weighted scoring: exact=1.0, partial=0.8, semantic=0.6, suggested=0.4, unmatched=0.0
    match_percentage = (
        exact_matches * 1.0 + 
        partial_matches * 0.8 + 
        semantic_matches * 0.6 + 
        suggested_mappings * 0.4
    ) / total
    
    if match_percentage >= 0.8:
        return {
            "status": "excellent",
            "confidence": match_percentage,
            "color": "green",
            "message": f"Excellent match ({match_percentage:.1%}) - {exact_matches} exact, {partial_matches} partial"
        }
    elif match_percentage >= 0.6:
        return {
            "status": "good",
            "confidence": match_percentage,
            "color": "yellow",
            "message": f"Good match ({match_percentage:.1%}) - {exact_matches + partial_matches} matched"
        }
    elif match_percentage >= 0.4:
        return {
            "status": "fair",
            "confidence": match_percentage,
            "color": "orange",
            "message": f"Fair match ({match_percentage:.1%}) - {semantic_matches} semantic matches"
        }
    else:
        return {
            "status": "poor",
            "confidence": match_percentage,
            "color": "red",
            "message": f"Poor match ({match_percentage:.1%}) - {unmatched} unmatched columns"
        }

def generate_mapping_suggestions(headers, staging_table_name):
    """Generate suggestions for improving mappings"""
    suggestions = []
    
    # Check for missing required fields
    required_fields = get_required_fields(staging_table_name)
    missing_required = [field for field in required_fields if not any(field in h.lower() for h in headers)]
    
    if missing_required:
        suggestions.append({
            "type": "warning",
            "message": f"Missing required fields: {', '.join(missing_required)}",
            "action": "add_missing_fields"
        })
    
    # Check for potential data type mismatches
    for header in headers:
        if any(keyword in header.lower() for keyword in ['date', 'time']) and 'date' not in header.lower():
            suggestions.append({
                "type": "info",
                "message": f"Consider mapping '{header}' to a date/timestamp field",
                "action": "suggest_date_mapping"
            })
    
    return suggestions

def get_required_fields(staging_table_name):
    """Get required fields for a staging table"""
    required_fields = {
        'onspd_staging': ['pcds'],
        'os_open_uprn_staging': ['uprn'],
        'os_open_usrn_staging': ['usrn'],
        'nndr_properties_staging': ['ba_reference'],
        'valuations_staging': ['ba_reference']
    }
    
    return required_fields.get(staging_table_name, []) 

@router.post("/staging/search-tables")
async def search_staging_tables(
    request: dict,
    db: Session = Depends(get_db)
):
    """Real-time table name search during mapping design"""
    query = request.get("query", "").lower()
    limit = request.get("limit", 10)
    
    # Search existing tables
    existing_tables = []
    if query:
        tables_query = text("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns 
                    WHERE table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public' 
            AND table_name LIKE :pattern
            ORDER BY table_name
            LIMIT :limit
        """)
        
        result = db.execute(tables_query, {
            "pattern": f"%{query}%",
            "limit": limit
        })
        
        for row in result.fetchall():
            if row and len(row) >= 2:
                existing_tables.append({
                    "name": str(row[0]),
                    "type": "existing",
                    "confidence": calculate_name_similarity(query, str(row[0])),
                    "description": f"Existing table with {row[1]} columns"
                })
    
    # Generate AI suggestions
    ai_suggestions = generate_table_suggestions(query)
    
    # Combine and sort by confidence
    all_suggestions = existing_tables + ai_suggestions
    all_suggestions.sort(key=lambda x: x["confidence"], reverse=True)
    
    return {
        "suggestions": all_suggestions[:limit],
        "query": query
    }

def calculate_name_similarity(query: str, table_name: str) -> float:
    """Calculate similarity between query and table name"""
    if not query or not table_name:
        return 0.0
    
    query_lower = query.lower()
    table_lower = table_name.lower()
    
    # Exact match
    if query_lower == table_lower:
        return 1.0
    
    # Contains match
    if query_lower in table_lower or table_lower in query_lower:
        return 0.8
    
    # Word overlap
    query_words = set(query_lower.split('_'))
    table_words = set(table_lower.split('_'))
    
    if query_words and table_words:
        overlap = len(query_words.intersection(table_words))
        total = len(query_words.union(table_words))
        return overlap / total if total > 0 else 0.0
    
    return 0.0

def generate_table_suggestions(query: str) -> List[Dict]:
    """Generate AI-powered table name suggestions"""
    suggestions = []
    
    # Common patterns for government data
    patterns = {
        'uprn': ['properties', 'addresses', 'buildings'],
        'postcode': ['postcodes', 'addresses', 'locations'],
        'rateable': ['business_rates', 'valuations', 'properties'],
        'boundary': ['boundaries', 'areas', 'regions'],
        'street': ['streets', 'roads', 'addresses'],
        'ward': ['wards', 'electoral', 'administrative'],
        'constituency': ['constituencies', 'electoral', 'political']
    }
    
    query_lower = query.lower()
    
    for keyword, suggestions_list in patterns.items():
        if keyword in query_lower:
            for suggestion in suggestions_list:
                suggestions.append({
                    "name": f"staging_{suggestion}",
                    "type": "ai_suggested",
                    "confidence": 0.7,
                    "description": f"AI suggested table for {keyword} data"
                })
    
    # Generic suggestions
    if 'data' in query_lower or 'file' in query_lower:
        suggestions.append({
            "name": "staging_data",
            "type": "ai_suggested", 
            "confidence": 0.6,
            "description": "Generic staging table for data"
        })
    
    return suggestions 