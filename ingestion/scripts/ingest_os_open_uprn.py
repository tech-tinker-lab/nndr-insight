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
import tempfile
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import uuid

# Load .env file from db_setup directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

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

def load_uprn_data_to_staging(csv_paths, session_id=None, source_name=None, client_name=None, batch_id=None, max_rows=None):
    """Ultra-fast load of UPRN data into staging table using COPY directly from file, with audit fields and progress bar."""
    start_time = time.time()  # Add missing start_time variable
    
    if not csv_paths:
        logger.error("No CSV files provided for ingestion.")
        return False, None

    # Generate unique batch ID as UUID if not provided
    batch_id = batch_id or str(uuid.uuid4())
    session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    source_name = source_name or "OS_Open_UPRN"
    client_name = client_name or "default_client"

    # Get source file information
    file_size = 0
    file_modified = datetime.fromtimestamp(0) # Default to epoch
    source_file = "N/A"
    for csv_path in csv_paths:
        if not os.path.isfile(csv_path):
            logger.error(f"CSV file not found: {csv_path}")
            return False, None
        file_size += os.path.getsize(csv_path)
        file_modified = max(file_modified, datetime.fromtimestamp(os.path.getmtime(csv_path)))
        source_file = os.path.basename(csv_path)

    logger.info(f"Batch ID: {batch_id}")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Source: {source_name}")
    logger.info(f"Client: {client_name}")
    logger.info(f"Source file: {csv_paths}")
    logger.info(f"File size: {file_size:,} bytes")
    logger.info(f"File modified: {file_modified}")

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                logger.info(f"Starting ultra-fast bulk load from {csv_paths} into os_open_uprn_staging...")

                import csv
                from io import StringIO
                from tqdm import tqdm

                # Count total lines for progress bar
                total_lines = 0
                for csv_path in csv_paths:
                    with open(csv_path, 'r', encoding='utf-8-sig') as f_count:
                        total_lines += sum(1 for _ in f_count) - 1  # exclude header

                def row_generator():
                    row_count = 0
                    for csv_path in csv_paths:
                        file_size = os.path.getsize(csv_path)
                        file_modified = datetime.fromtimestamp(os.path.getmtime(csv_path))
                        source_file = os.path.basename(csv_path)
                        with open(csv_path, 'r', encoding='utf-8-sig') as f:
                            reader = csv.reader(f)
                            header = next(reader)
                            
                            # Debug: Print header and first data row for analysis
                            logger.info(f"CSV Header: {header}")
                            first_row = next(reader)
                            logger.info(f"First Data Row: {first_row}")
                            logger.info(f"Header length: {len(header)}, First row length: {len(first_row)}")
                            
                            # Reset file pointer to start after header
                            f.seek(0)
                            next(reader)  # Skip header again
                            
                            for row in tqdm(reader, total=total_lines, desc=f"Processing rows from {os.path.basename(csv_path)}"):
                                # Check max_rows limit
                                if max_rows is not None and row_count >= max_rows:
                                    logger.info(f"Reached max_rows limit ({max_rows}), stopping processing")
                                    return
                                
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
                                row_count += 1

                # Create temporary CSV file for large dataset
                logger.info("Creating temporary CSV file for database insertion...")
                with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8-sig', newline='') as temp_csv:
                    temp_csv_path = temp_csv.name
                    writer = csv.writer(temp_csv)
                    
                    # Write header
                    writer.writerow([
                        'uprn', 'x_coordinate', 'y_coordinate', 'latitude', 'longitude',
                        'source_name', 'upload_user', 'upload_timestamp',
                        'batch_id', 'source_file', 'file_size', 'file_modified', 'session_id', 'client_name'
                    ])
                    
                    # Write data rows
                    for row in row_generator():
                        writer.writerow(row)

                # Load data from temporary file
                logger.info("Loading data from temporary file into database...")
                load_start = time.time()

                copy_sql = """
                    COPY os_open_uprn_staging (
                        uprn, x_coordinate, y_coordinate, latitude, longitude,
                        source_name, upload_user, upload_timestamp,
                        batch_id, source_file, file_size, file_modified, session_id, client_name
                    )
                    FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
                """

                with open(temp_csv_path, 'r', encoding='utf-8-sig') as csv_file:
                    cur.copy_expert(sql=copy_sql, file=csv_file)

                conn.commit()

                # Clean up temporary file
                try:
                    os.unlink(temp_csv_path)
                    logger.info("Temporary file cleaned up successfully")
                except Exception as e:
                    logger.warning(f"Could not remove temporary file {temp_csv_path}: {e}")

                load_time = time.time() - load_start
                total_time = time.time() - start_time

                # Get record count for this batch
                cur.execute("""
                    SELECT COUNT(*) FROM os_open_uprn_staging 
                    WHERE batch_id = %s AND session_id = %s
                """, (batch_id, session_id))
                rowcount_result = cur.fetchone()
                rowcount = rowcount_result[0] if rowcount_result else 0

                logger.info(f"✅ Database loading completed!")
                logger.info(f"📊 Total rows loaded: {rowcount:,}")
                logger.info(f"⏱️  Database load time: {load_time:.1f} seconds")
                logger.info(f"⏱️  Total processing time: {total_time:.1f} seconds")

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
                
                # Check for empty UPRNs (instead of raw_line)
                cur.execute(f"SELECT COUNT(*) FROM os_open_uprn_staging {where_clause} AND (uprn IS NULL OR uprn = '');", params)
                empty_result = cur.fetchone()
                empty_count = empty_result[0] if empty_result else 0
                
                logger.info("=" * 60)
                logger.info("STAGING DATA QUALITY REPORT")
                logger.info("=" * 60)
                logger.info(f"Total records: {total_count:,}")
                logger.info(f"Null UPRNs: {null_uprn_count}")
                logger.info(f"Empty UPRNs: {empty_count}")
                logger.info(f"Valid UPRNs: {total_count - empty_count:,}")
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
    parser.add_argument('--source-path', required=True, help='Path to CSV file or directory')
    
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
    parser.add_argument('--max-rows', type=int, default=None, help='Maximum number of rows to ingest (for debugging)')
    
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
    
    # Determine if source-path is a file or directory
    if os.path.isdir(args.source_path):
        csv_files = [os.path.join(args.source_path, f) for f in os.listdir(args.source_path) if f.lower().endswith('.csv')]
        if not csv_files:
            logger.error(f"No CSV files found in directory: {args.source_path}")
            sys.exit(1)
    elif os.path.isfile(args.source_path):
        csv_files = [args.source_path]
    else:
        logger.error(f"source-path is not a valid file or directory: {args.source_path}")
        sys.exit(1)

    # Improved file metadata logging
    if len(csv_files) == 1:
        logger.info(f"File path: {csv_files[0]}")
        logger.info(f"File size: {os.path.getsize(csv_files[0])}")
        logger.info(f"File modified: {datetime.fromtimestamp(os.path.getmtime(csv_files[0]))}")
    else:
        logger.info(f"Number of files: {len(csv_files)}")
        logger.info(f"First file: {csv_files[0]}")
        logger.info(f"First file size: {os.path.getsize(csv_files[0])}")
        logger.info(f"First file modified: {datetime.fromtimestamp(os.path.getmtime(csv_files[0]))}")
        total_size = sum(os.path.getsize(f) for f in csv_files)
        logger.info(f"Total size of all files: {total_size}")

    logger.info("=" * 60)
    logger.info("OS OPEN UPRN STAGING-ONLY INGESTION")
    logger.info("=" * 60)
    logger.info(f"CSV files: {csv_files}")
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
        # ensure_staging_table_exists()  # REMOVE THIS LINE
        
        # Step 2: Load data into staging table
        success, batch_id = load_uprn_data_to_staging(
            csv_files, 
            session_id,
            source_name,
            client_name,
            batch_id,
            args.max_rows
        )
        
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