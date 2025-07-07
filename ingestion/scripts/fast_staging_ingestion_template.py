#!/usr/bin/env python3
"""
Fast Staging Table Ingestion Template
This template shows the fastest approach for uploading data into staging tables.
"""

import psycopg2
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'db_setup', '.env'))

# Database configuration
USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_connection():
    """Get database connection"""
    return psycopg2.connect(
        dbname=DBNAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )

def fast_staging_ingestion(csv_path, staging_table, columns, batch_id=None, source_name=None):
    """
    Fastest approach for staging table ingestion using COPY
    
    Args:
        csv_path: Path to CSV file
        staging_table: Name of staging table
        columns: List of column names in order
        batch_id: Optional batch identifier
        source_name: Optional source name
    """
    
    if not os.path.isfile(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        return False

    start_time = datetime.now()
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                logger.info(f"Starting fast staging ingestion: {csv_path} → {staging_table}")
                
                # Clear staging table
                cur.execute(f"TRUNCATE TABLE {staging_table};")
                logger.info(f"Cleared staging table: {staging_table}")
                
                # Prepare COPY command
                column_list = ', '.join(columns)
                copy_sql = f"""
                    COPY {staging_table} ({column_list})
                    FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
                """
                
                # Execute fast COPY operation
                with open(csv_path, 'r', encoding='utf-8') as f:
                    cur.copy_expert(sql=copy_sql, file=f)
                
                # Get row count
                cur.execute(f"SELECT COUNT(*) FROM {staging_table};")
                row_count_result = cur.fetchone()
                row_count = row_count_result[0] if row_count_result else 0
                
                # Update metadata if provided
                if batch_id or source_name:
                    update_sql = f"UPDATE {staging_table} SET "
                    updates = []
                    if batch_id:
                        updates.append(f"batch_id = '{batch_id}'")
                    if source_name:
                        updates.append(f"source_name = '{source_name}'")
                    if updates:
                        update_sql += ', '.join(updates)
                        cur.execute(update_sql)
                
                conn.commit()
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                rate = row_count / duration if duration > 0 else 0
                
                logger.info(f"✅ Successfully loaded {row_count:,} rows in {duration:.1f}s")
                logger.info(f"📊 Rate: {rate:,.0f} rows/second")
                
                return True
                
    except Exception as e:
        logger.error(f"❌ Error during staging ingestion: {e}")
        return False

def verify_staging_data(staging_table):
    """Verify staging table data quality"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Basic counts
                cur.execute(f"SELECT COUNT(*) FROM {staging_table};")
                total_count_result = cur.fetchone()
                total_count = total_count_result[0] if total_count_result else 0
                
                # Check for empty rows
                cur.execute(f"SELECT COUNT(*) FROM {staging_table} WHERE raw_line IS NULL OR raw_line = '';")
                empty_count_result = cur.fetchone()
                empty_count = empty_count_result[0] if empty_count_result else 0
                
                logger.info(f"📊 Staging table verification:")
                logger.info(f"   Total rows: {total_count:,}")
                logger.info(f"   Empty rows: {empty_count:,}")
                logger.info(f"   Valid rows: {total_count - empty_count:,}")
                
                return True
                
    except Exception as e:
        logger.error(f"Error verifying staging data: {e}")
        return False

# Example usage for different datasets
def example_os_open_uprn_staging(csv_path):
    """Example: Fast OS Open UPRN staging ingestion"""
    columns = [
        'uprn', 'x_coordinate', 'y_coordinate', 'latitude', 'longitude',
        'raw_line', 'source_name', 'upload_user', 'upload_timestamp', 
        'batch_id', 'raw_filename'
    ]
    
    return fast_staging_ingestion(
        csv_path=csv_path,
        staging_table='os_open_uprn_staging',
        columns=columns,
        batch_id=f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        source_name='OS_Open_UPRN'
    )

def example_code_point_staging(csv_path):
    """Example: Fast Code Point Open staging ingestion"""
    columns = [
        'postcode', 'positional_quality_indicator', 'easting', 'northing',
        'country_code', 'nhs_regional_ha_code', 'nhs_ha_code',
        'admin_county_code', 'admin_district_code', 'admin_ward_code',
        'raw_line', 'source_name', 'upload_user', 'upload_timestamp',
        'batch_id', 'raw_filename'
    ]
    
    return fast_staging_ingestion(
        csv_path=csv_path,
        staging_table='code_point_open_staging',
        columns=columns,
        batch_id=f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        source_name='Code_Point_Open'
    )

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 2:
        print("Usage: python fast_staging_ingestion_template.py <csv_file> [dataset_type]")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    dataset_type = sys.argv[2] if len(sys.argv) > 2 else 'uprn'
    
    if dataset_type == 'uprn':
        success = example_os_open_uprn_staging(csv_file)
    elif dataset_type == 'codepoint':
        success = example_code_point_staging(csv_file)
    else:
        print(f"Unknown dataset type: {dataset_type}")
        sys.exit(1)
    
    if success:
        print("🎉 Staging ingestion completed successfully!")
    else:
        print("❌ Staging ingestion failed!")
        sys.exit(1) 