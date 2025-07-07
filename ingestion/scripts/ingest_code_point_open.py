#!/usr/bin/env python3
"""
Concurrency-Safe Code Point Open Data Ingestion Script
Loads data into staging table with batch_id and client_id for safe concurrent ingestion
Uses COPY for fast bulk insertion with audit trail
"""

import os
import sys
import glob
import time
import psycopg2
import argparse
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load .env file from db_setup directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'db_setup', '.env'))

# Database configuration
USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

DATA_DIR = "data/codepo_gb/Data/CSV"

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

def ensure_staging_table_exists():
    """Ensure the staging table exists with proper schema"""
    logger.info("Ensuring code_point_open_staging table exists...")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Create staging table if it doesn't exist
                create_staging_sql = """
                CREATE TABLE IF NOT EXISTS code_point_open_staging (
                    postcode TEXT,
                    positional_quality_indicator TEXT,
                    easting TEXT,
                    northing TEXT,
                    country_code TEXT,
                    nhs_regional_ha_code TEXT,
                    nhs_ha_code TEXT,
                    admin_county_code TEXT,
                    admin_district_code TEXT,
                    admin_ward_code TEXT,
                    raw_line TEXT,
                    source_name TEXT,
                    upload_user TEXT,
                    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    batch_id TEXT,
                    raw_filename TEXT,
                    file_path TEXT,
                    file_size TEXT,
                    file_modified TIMESTAMP,
                    session_id TEXT
                );
                """
                cur.execute(create_staging_sql)
                conn.commit()
                logger.info("Staging table verified/created successfully")
                
    except Exception as e:
        logger.error(f"Error ensuring staging table exists: {e}")
        raise

def process_file_to_staging(file_path, batch_id, session_id):
    """Process a single CSV file into staging table with metadata"""
    logger.info(f"Processing {os.path.basename(file_path)}...")
    file_start = time.time()
    
    # Get source file information
    file_size = os.path.getsize(file_path)
    file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Process data and add metadata columns
                from io import StringIO
                import csv
                
                # Create a new CSV with metadata columns
                output_buffer = StringIO()
                writer = csv.writer(output_buffer)
                
                # Write header with metadata columns
                writer.writerow([
                    'postcode', 'positional_quality_indicator', 'easting', 'northing',
                    'country_code', 'nhs_regional_ha_code', 'nhs_ha_code',
                    'admin_county_code', 'admin_district_code', 'admin_ward_code',
                    'raw_line', 'source_name', 'upload_user', 'upload_timestamp',
                    'batch_id', 'raw_filename', 'file_path', 'file_size', 'file_modified', 'session_id'
                ])
                
                # Process each data row and add metadata
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        # Add metadata columns
                        metadata_row = row + [
                            ','.join(row) if row else '',  # raw_line (join all columns)
                            'Code_Point_Open',  # source_name
                            USER,  # upload_user
                            datetime.now().isoformat(),  # upload_timestamp
                            batch_id,  # batch_id
                            os.path.basename(file_path),  # raw_filename
                            file_path,  # file_path
                            str(file_size),  # file_size
                            file_modified.isoformat(),  # file_modified
                            session_id  # session_id
                        ]
                        writer.writerow(metadata_row)
                
                # Reset buffer and copy to staging table
                output_buffer.seek(0)
                copy_sql = """
                    COPY code_point_open_staging (
                        postcode, positional_quality_indicator, easting, northing,
                        country_code, nhs_regional_ha_code, nhs_ha_code,
                        admin_county_code, admin_district_code, admin_ward_code,
                        raw_line, source_name, upload_user, upload_timestamp,
                        batch_id, raw_filename, file_path, file_size, file_modified, session_id
                    )
                    FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
                """
                cur.copy_expert(sql=copy_sql, file=output_buffer)
                conn.commit()
                
                # Get count of loaded rows for this file
                cur.execute("""
                    SELECT COUNT(*) FROM code_point_open_staging 
                    WHERE batch_id = %s AND raw_filename = %s
                """, (batch_id, os.path.basename(file_path)))
                row_result = cur.fetchone()
                file_rows = row_result[0] if row_result else 0
                
                file_time = time.time() - file_start
                logger.info(f"  Loaded {file_rows} rows in {file_time:.1f}s")
                logger.info(f"  File size: {file_size:,} bytes")
                
                return file_rows
                
    except Exception as e:
        logger.error(f"  Error processing {os.path.basename(file_path)}: {e}")
        return 0

def load_data_to_staging(data_dir, session_id=None):
    """Load Code Point Open data into staging table"""
    start_time = time.time()
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    logger.info(f"Found {len(csv_files)} CSV files in {data_dir}")
    
    if not csv_files:
        logger.error("No CSV files found!")
        return False, None

    # Generate unique batch ID
    batch_id = f"codepoint_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    logger.info(f"Batch ID: {batch_id}")
    logger.info(f"Session ID: {session_id}")

    try:
        total_rows_inserted = 0
        
        for file_path in csv_files:
            file_rows = process_file_to_staging(file_path, batch_id, session_id)
            total_rows_inserted += file_rows
        
        logger.info(f"Total rows in staging: {total_rows_inserted}")
        
        total_time = time.time() - start_time
        logger.info(f"Total processing time: {total_time:.1f} seconds")
        
        return True, batch_id
        
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        return False, None

def verify_staging_data_quality(batch_id=None, session_id=None):
    """Verify the loaded staging data quality"""
    logger.info("Verifying staging data quality...")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Build WHERE clause for specific batch/session if provided
                where_clause = ""
                params = []
                if batch_id and session_id:
                    where_clause = "WHERE batch_id = %s AND session_id = %s"
                    params = [batch_id, session_id]
                elif batch_id:
                    where_clause = "WHERE batch_id = %s"
                    params = [batch_id]
                
                # Check total count
                cur.execute(f"SELECT COUNT(*) FROM code_point_open_staging {where_clause};", params)
                total_count_result = cur.fetchone()
                total_count = total_count_result[0] if total_count_result else 0
                
                # Check for empty rows
                cur.execute(f"SELECT COUNT(*) FROM code_point_open_staging {where_clause} AND (raw_line IS NULL OR raw_line = '');", params)
                empty_result = cur.fetchone()
                empty_count = empty_result[0] if empty_result else 0
                
                # Check for null postcodes
                cur.execute(f"SELECT COUNT(*) FROM code_point_open_staging {where_clause} AND postcode IS NULL;", params)
                null_postcode_result = cur.fetchone()
                null_postcode_count = null_postcode_result[0] if null_postcode_result else 0
                
                logger.info("=" * 60)
                logger.info("STAGING DATA QUALITY REPORT")
                logger.info("=" * 60)
                logger.info(f"Total records: {total_count:,}")
                logger.info(f"Null postcodes: {null_postcode_count}")
                logger.info(f"Empty rows: {empty_count}")
                logger.info(f"Valid rows: {total_count - empty_count:,}")
                if batch_id:
                    logger.info(f"Batch ID: {batch_id}")
                if session_id:
                    logger.info(f"Session ID: {session_id}")
                logger.info("=" * 60)
                
                return True
                
    except Exception as e:
        logger.error(f"Error during data quality verification: {e}")
        return False

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Concurrency-Safe Code Point Open Staging Ingestion')
    parser.add_argument('--data-dir', default=DATA_DIR, help='Directory containing CSV files')
    parser.add_argument('--session-id', help='Session identifier for concurrent ingestion')
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("CONCURRENCY-SAFE CODE POINT OPEN STAGING INGESTION")
    logger.info("=" * 60)
    logger.info(f"Data directory: {args.data_dir}")
    logger.info(f"Session ID: {args.session_id or 'auto-generated'}")
    logger.info("=" * 60)
    
    try:
        # Step 1: Ensure staging table exists
        ensure_staging_table_exists()
        
        # Step 2: Load data into staging table
        success, batch_id = load_data_to_staging(
            args.data_dir,
            args.session_id
        )
        
        if success:
            # Step 3: Verify staging data quality
            verify_staging_data_quality(batch_id, args.session_id)
            logger.info("✅ Code Point Open staging ingestion completed successfully!")
            if batch_id:
                logger.info(f"📊 Data loaded into staging table with batch_id: {batch_id}")
        else:
            logger.error("❌ Data loading failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
