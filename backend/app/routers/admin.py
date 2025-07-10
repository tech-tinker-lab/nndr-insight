from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List, Dict, Any
from sqlalchemy import text, func
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from ..services.database_service import get_db
from ..models import StagingMigrationRequest, StagingMigrationResponse, StagingPreviewResponse

router = APIRouter(prefix="/admin", tags=["admin"])

logger = logging.getLogger(__name__)

@router.get("/staging/preview/{table_name}", response_model=StagingPreviewResponse)
async def preview_staging_data(
    table_name: str,
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    source_name: Optional[str] = Query(None, description="Filter by source name"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    limit: int = Query(100, description="Number of records to preview"),
    offset: int = Query(0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Preview staging data with optional filters
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
            LIMIT :limit OFFSET :offset
        """)
        params.update({'limit': limit, 'offset': offset})
        
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
    db: Session = Depends(get_db)
):
    """
    Migrate data from staging to master table based on filter criteria
    """
    try:
        # Validate table name and get mapping
        table_mappings = {
            'onspd_staging': {
                'master_table': 'onspd',
                'columns': {
                    'pcds': 'pcds',
                    'pcd': 'pcd',
                    'lat': 'lat',
                    'long': 'long',
                    'ctry': 'ctry',
                    'oslaua': 'oslaua',
                    'osward': 'osward',
                    'parish': 'parish',
                    'oa11': 'oa11',
                    'lsoa11': 'lsoa11',
                    'msoa11': 'msoa11',
                    'imd': 'imd',
                    'rgn': 'rgn',
                    'pcon': 'pcon',
                    'ur01ind': 'ur01ind',
                    'oac11': 'oac11',
                    'oseast1m': 'oseast1m',
                    'osnrth1m': 'osnrth1m',
                    'dointr': 'dointr',
                    'doterm': 'doterm'
                }
            }
            # Add other table mappings as needed
        }
        
        if table_name not in table_mappings:
            raise HTTPException(status_code=400, detail=f"Migration not supported for table: {table_name}")
        
        mapping = table_mappings[table_name]
        master_table = mapping['master_table']
        columns = mapping['columns']
        
        # Build WHERE clause for staging data selection
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
        
        # Build column list for INSERT
        staging_columns = list(columns.keys())
        master_columns = list(columns.values())
        
        # Perform migration
        migration_query = text(f"""
            INSERT INTO {master_table} ({', '.join(master_columns)})
            SELECT {', '.join(staging_columns)}
            FROM {table_name}
            WHERE {where_clause}
            ON CONFLICT (pcds) DO UPDATE SET
                pcd = EXCLUDED.pcd,
                lat = EXCLUDED.lat,
                long = EXCLUDED.long,
                ctry = EXCLUDED.ctry,
                oslaua = EXCLUDED.oslaua,
                osward = EXCLUDED.osward,
                parish = EXCLUDED.parish,
                oa11 = EXCLUDED.oa11,
                lsoa11 = EXCLUDED.lsoa11,
                msoa11 = EXCLUDED.msoa11,
                imd = EXCLUDED.imd,
                rgn = EXCLUDED.rgn,
                pcon = EXCLUDED.pcon,
                ur01ind = EXCLUDED.ur01ind,
                oac11 = EXCLUDED.oac11,
                oseast1m = EXCLUDED.oseast1m,
                osnrth1m = EXCLUDED.osnrth1m,
                dointr = EXCLUDED.dointr,
                doterm = EXCLUDED.doterm
        """)
        
        # Get count before migration
        count_query = text(f"""
            SELECT COUNT(*) FROM {table_name} WHERE {where_clause}
        """)
        count_result = db.execute(count_query, params).fetchone()
        records_to_migrate = count_result[0] if count_result else 0
        
        # Execute migration
        result = db.execute(migration_query, params)
        db.commit()
        
        # Get final count in master table
        final_count_query = text(f"SELECT COUNT(*) FROM {master_table}")
        final_result = db.execute(final_count_query).fetchone()
        final_count = final_result[0] if final_result else 0
        
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