#!/usr/bin/env python3
"""
Concurrency-Safe OS UPRN Data Ingestion Script
Loads data into staging table with batch_id and client_id for safe concurrent ingestion
Uses COPY for fast bulk insertion with audit trail
"""

import psycopg2
import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import uuid

# Load .env file from db_setup directory
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

def ensure_staging_table_exists():
    """Ensure the staging table exists with proper schema"""
    logger.info("Ensuring os_open_uprn_staging table exists...")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Create staging table if it doesn't exist
                create_staging_sql = """
                CREATE TABLE IF NOT EXISTS os_open_uprn_staging (
                    uprn TEXT,
                    x_coordinate TEXT,
                    y_coordinate TEXT,
                    latitude TEXT,
                    longitude TEXT,
                    raw_line TEXT,
                    source_name TEXT,
                    upload_user TEXT,
                    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    batch_id TEXT,
                    raw_filename TEXT,
                    file_path TEXT,
                    file_size BIGINT,
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

def load_uprn_data_to_staging(csv_path, session_id=None, source_name=None, client_name=None, batch_id=None):
    """Ultra-fast load of UPRN data into staging table using COPY directly from file, with audit fields and progress bar."""
    if not os.path.isfile(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        return False

    # Generate unique batch ID as UUID if not provided
    batch_id = batch_id or str(uuid.uuid4())
    session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    source_name = source_name or "OS_Open_UPRN"
    client_name = client_name or "default_client"

    # Get source file information
    file_size = os.path.getsize(csv_path)
    file_modified = datetime.fromtimestamp(os.path.getmtime(csv_path))
    source_file = os.path.basename(csv_path)

    logger.info(f"Batch ID: {batch_id}")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Source: {source_name}")
    logger.info(f"Client: {client_name}")
    logger.info(f"Source file: {csv_path}")
    logger.info(f"File size: {file_size:,} bytes")
    logger.info(f"File modified: {file_modified}")

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                logger.info(f"Starting ultra-fast bulk load from {csv_path} into os_open_uprn_staging...")

                import csv
                from io import StringIO
                from tqdm import tqdm

                # Count total lines for progress bar
                with open(csv_path, 'r', encoding='utf-8') as f_count:
                    total_lines = sum(1 for _ in f_count) - 1  # exclude header

                def row_generator():
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        header = next(reader)
                        for row in tqdm(reader, total=total_lines, desc="Processing rows"):
                            yield [
                                row[0] if len(row) > 0 else '',  # uprn
                                row[1] if len(row) > 1 else '',  # x_coordinate
                                row[2] if len(row) > 2 else '',  # y_coordinate
                                row[3] if len(row) > 3 else '',  # latitude
                                row[4] if len(row) > 4 else '',  # longitude
                                source_name,                     # source_name
                                USER,                            # upload_user
                                datetime.now().isoformat(),      # upload_timestamp
                                batch_id,                        # batch_id
                                source_file,                     # source_file
                                str(file_size),                  # file_size
                                file_modified.isoformat(),       # file_modified
                                session_id,                      # session_id
                                client_name                      # client_name
                            ]

                # Write to a StringIO buffer in CSV format for COPY
                output_buffer = StringIO()
                writer = csv.writer(output_buffer)
                writer.writerow([
                    'uprn', 'x_coordinate', 'y_coordinate', 'latitude', 'longitude',
                    'source_name', 'upload_user', 'upload_timestamp',
                    'batch_id', 'source_file', 'file_size', 'file_modified', 'session_id', 'client_name'
                ])
                for row in row_generator():
                    writer.writerow(row)
                output_buffer.seek(0)

                copy_sql = """
                    COPY os_open_uprn_staging (
                        uprn, x_coordinate, y_coordinate, latitude, longitude,
                        source_name, upload_user, upload_timestamp,
                        batch_id, source_file, file_size, file_modified, session_id, client_name
                    )
                    FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
                """
                cur.copy_expert(sql=copy_sql, file=output_buffer)
                conn.commit()

                # Get record count for this batch
                cur.execute("""
                    SELECT COUNT(*) FROM os_open_uprn_staging 
                    WHERE batch_id = %s AND session_id = %s
                """, (batch_id, session_id))
                rowcount_result = cur.fetchone()
                rowcount = rowcount_result[0] if rowcount_result else 0

                logger.info(f"Successfully loaded {rowcount} records into os_open_uprn_staging")
                logger.info(f"Batch ID: {batch_id}")

                return True, batch_id

    except Exception as e:
        logger.error(f"Error during data load: {e}")
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
                cur.execute(f"SELECT COUNT(*) FROM os_open_uprn_staging {where_clause};", params)
                total_count_result = cur.fetchone()
                total_count = total_count_result[0] if total_count_result else 0
                
                # Check for null UPRNs
                cur.execute(f"SELECT COUNT(*) FROM os_open_uprn_staging {where_clause} AND uprn IS NULL;", params)
                null_uprn_result = cur.fetchone()
                null_uprn_count = null_uprn_result[0] if null_uprn_result else 0
                
                # Check for empty rows
                cur.execute(f"SELECT COUNT(*) FROM os_open_uprn_staging {where_clause} AND (raw_line IS NULL OR raw_line = '');", params)
                empty_result = cur.fetchone()
                empty_count = empty_result[0] if empty_result else 0
                
                logger.info("=" * 60)
                logger.info("STAGING DATA QUALITY REPORT")
                logger.info("=" * 60)
                logger.info(f"Total records: {total_count:,}")
                logger.info(f"Null UPRNs: {null_uprn_count}")
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
    parser = argparse.ArgumentParser(description='OS Open UPRN Staging-Only Ingestion')
    
    # Required: CSV file path
    parser.add_argument('--source-file', nargs='?', 
                       default="backend/data/osopenuprn_202506_csv/osopenuprn_202506.csv",
                       help='Path to CSV file')
    
    # Optional: Client and source information
    parser.add_argument('--client', 
                       help='Client identifier (e.g., "client_001", "internal_team")')
    parser.add_argument('--source', 
                       help='Source identifier (e.g., "OS_Open_UPRN_2024", "VOA_2025")')
    parser.add_argument('--session-id', 
                       help='Session identifier for concurrent ingestion (auto-generated if not provided)')
    parser.add_argument('--batch-id', 
                       help='Batch identifier (auto-generated if not provided)')
    
    # Optional: Database override
    parser.add_argument('--dbname', 
                       help='Override database name from environment')
    
    args = parser.parse_args()
    
    # Override database if specified
    if args.dbname:
        global DBNAME
        DBNAME = args.dbname
    
    # Generate identifiers
    batch_id = args.batch_id or str(uuid.uuid4())
    session_id = args.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Get source and client names
    source_name = args.source or "OS_Open_UPRN_DEFAULT"
    client_name = args.client or "default_client"
    
    logger.info("=" * 60)
    logger.info("OS OPEN UPRN STAGING-ONLY INGESTION")
    logger.info("=" * 60)
    logger.info(f"Source file: {args.source_file}")
    logger.info(f"Staging table: os_open_uprn_staging")
    logger.info(f"Source: {source_name}")
    logger.info(f"Client: {client_name}")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Batch ID: {batch_id}")
    logger.info("=" * 60)
    
    # Print DB connection details (mask password)
    logger.info("Database connection details:")
    logger.info(f"  Host: {HOST}")
    logger.info(f"  Port: {PORT}")
    logger.info(f"  DB Name: {DBNAME}")
    logger.info(f"  User: {USER}")
    logger.info(f"  Password: {'***' if PASSWORD else '(not set)'}")

    try:
        # Step 1: Ensure staging table exists
        ensure_staging_table_exists()
        
        # Step 2: Load data into staging table
        result = load_uprn_data_to_staging(
            args.source_file, 
            session_id,
            source_name,
            client_name,
            batch_id
        )
        
        if isinstance(result, tuple) and len(result) == 2:
            success, batch_id = result
        else:
            success = result
            batch_id = None
        
        if success:
            # Step 3: Verify staging data quality
            verify_staging_data_quality(batch_id, session_id)
            logger.info("✅ OS UPRN staging ingestion completed successfully!")
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