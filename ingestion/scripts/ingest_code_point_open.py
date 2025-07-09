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
import tempfile
import psycopg2
import argparse
import logging
import uuid
import csv
from datetime import datetime
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(path):
        pass  # Fallback if dotenv not available
from tqdm import tqdm

# Load .env file from root directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

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

def check_staging_table_exists():
    """Check if the staging table exists"""
    logger.info("Checking if code_point_open_staging table exists...")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Check if table exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'code_point_open_staging'
                    );
                """)
                result = cur.fetchone()
                table_exists = result[0] if result else False
                
                if not table_exists:
                    logger.error("❌ Table 'code_point_open_staging' does not exist!")
                    logger.error("Please create the table first using database setup scripts.")
                    return False
                
                logger.info("✅ Staging table exists")
                return True
                
    except Exception as e:
        logger.error(f"Error checking staging table: {e}")
        return False

def create_combined_csv(data_dir, batch_id, session_id, client_name, output_csv_path=None):
    """Create a combined CSV file from all individual CSV files"""
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not csv_files:
        logger.error("No CSV files found!")
        return None
    
    # Create output CSV file
    if output_csv_path is None:
        output_csv_path = os.path.join(tempfile.gettempdir(), f'combined_codepoint_{batch_id}.csv')
    
    logger.info(f"Creating combined CSV file: {output_csv_path}")
    logger.info(f"Processing {len(csv_files)} CSV files...")
    
    total_lines = 0
    processed_files = 0
    
    try:
        with open(output_csv_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            
            # Write header with data columns + metadata columns (matching actual table structure)
            writer.writerow([
                'postcode', 'positional_quality_indicator', 'easting', 'northing',
                'country_code', 'nhs_regional_ha_code', 'nhs_ha_code',
                'admin_county_code', 'admin_district_code', 'admin_ward_code',
                'source_name', 'upload_user', 'upload_timestamp',
                'batch_id', 'source_file', 'file_size', 'file_modified', 'session_id', 'client_name'
            ])
            
            # Progress bar for files
            with tqdm(csv_files, desc="Combining CSV files", unit="file") as pbar:
                for csv_file in csv_files:
                    file_name = os.path.basename(csv_file)
                    pbar.set_description(f"Processing {file_name}")
                    
                    # Get file metadata
                    file_size = os.path.getsize(csv_file)
                    file_modified = datetime.fromtimestamp(os.path.getmtime(csv_file))
                    
                    # Count lines in current file
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        file_lines = sum(1 for _ in f)
                    
                    # Process each data row and add metadata
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            # Add metadata columns (matching actual table structure)
                            metadata_row = row + [
                                'Code_Point_Open',  # source_name
                                USER,  # upload_user
                                datetime.now().isoformat(),  # upload_timestamp
                                batch_id,  # batch_id
                                file_name,  # source_file
                                file_size,  # file_size
                                file_modified.isoformat(),  # file_modified
                                session_id,  # session_id
                                client_name  # client_name
                            ]
                            writer.writerow(metadata_row)
                            total_lines += 1
                    
                    processed_files += 1
                    pbar.set_postfix({
                        'Files': f"{processed_files}/{len(csv_files)}",
                        'Lines': f"{total_lines:,}",
                        'Size': f"{os.path.getsize(output_csv_path)/1024/1024:.1f}MB"
                    })
                    pbar.update(1)  # Update progress bar for each file processed
        
        logger.info(f"✅ Combined CSV created successfully!")
        logger.info(f"📁 Output file: {output_csv_path}")
        logger.info(f"📊 Total lines: {total_lines:,}")
        logger.info(f"📊 Files processed: {processed_files}")
        logger.info(f"📊 File size: {os.path.getsize(output_csv_path)/1024/1024:.1f} MB")
        
        return output_csv_path
        
    except Exception as e:
        logger.error(f"Error creating combined CSV: {e}")
        return None

def load_data_to_staging(data_dir, session_id=None, client_name=None, output_csv_path=None):
    """Load Code Point Open data into staging table using combined CSV approach"""
    start_time = time.time()
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    logger.info(f"Found {len(csv_files)} CSV files in {data_dir}")
    
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

    if not csv_files:
        logger.error("No CSV files found!")
        return False, None

    # Generate unique batch ID
    batch_id = f"codepoint_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    client_name = client_name or "default_client"
    
    logger.info(f"Batch ID: {batch_id}")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Client: {client_name}")

    try:
        # Step 1: Create combined CSV file
        combined_csv_path = create_combined_csv(data_dir, batch_id, session_id, client_name, output_csv_path)
        if not combined_csv_path:
            logger.error("Failed to create combined CSV file!")
            return False, None
        
        # Step 2: Load combined CSV into database
        logger.info("Loading combined CSV into database...")
        load_start = time.time()
        
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Count rows in the combined CSV for progress bar
                with open(combined_csv_path, 'r', encoding='utf-8') as csv_file:
                    row_count = sum(1 for _ in csv_file) - 1  # Subtract header
                
                logger.info("Loading data from temporary file into database...")
                
                # Use copy_expert to load the combined CSV file from client side
                copy_sql = """
                    COPY code_point_open_staging (
                        postcode, positional_quality_indicator, easting, northing,
                        country_code, nhs_regional_ha_code, nhs_ha_code,
                        admin_county_code, admin_district_code, admin_ward_code,
                        source_name, upload_user, upload_timestamp,
                        batch_id, source_file, file_size, file_modified, session_id, client_name
                    )
                    FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
                """
                
                with tqdm(total=row_count, desc="Database loading", unit="rows") as pbar:
                    with open(combined_csv_path, 'r', encoding='utf-8') as csv_file:
                        cur.copy_expert(sql=copy_sql, file=csv_file)
                    pbar.update(row_count)
                
                conn.commit()
                
                # Get count of loaded rows
                cur.execute("""
                    SELECT COUNT(*) FROM code_point_open_staging 
                    WHERE batch_id = %s
                """, (batch_id,))
                row_result = cur.fetchone()
                total_rows_inserted = row_result[0] if row_result else 0
        
        load_time = time.time() - load_start
        total_time = time.time() - start_time
        
        logger.info(f"✅ Database loading completed!")
        logger.info(f"📊 Total rows loaded: {total_rows_inserted:,}")
        logger.info(f"⏱️  Database load time: {load_time:.1f} seconds")
        logger.info(f"⏱️  Total processing time: {total_time:.1f} seconds")
        
        # Clean up temporary file if it was created automatically
        if output_csv_path is None and os.path.exists(combined_csv_path):
            try:
                os.remove(combined_csv_path)
                logger.info(f"🗑️  Cleaned up temporary file: {combined_csv_path}")
            except Exception as e:
                logger.warning(f"Could not remove temporary file {combined_csv_path}: {e}")
        
        return True, batch_id
        
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        return False, None

def verify_staging_data_quality(batch_id=None, session_id=None, client_name=None):
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
                
                # Check for null postcodes
                cur.execute(f"SELECT COUNT(*) FROM code_point_open_staging {where_clause} AND postcode IS NULL;", params)
                null_postcode_result = cur.fetchone()
                null_postcode_count = null_postcode_result[0] if null_postcode_result else 0
                
                logger.info("=" * 60)
                logger.info("STAGING DATA QUALITY REPORT")
                logger.info("=" * 60)
                logger.info(f"Total records: {total_count:,}")
                logger.info(f"Null postcodes: {null_postcode_count}")
                logger.info(f"Valid rows: {total_count - null_postcode_count:,}")
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
    # Change --data-dir to --source-path and support both file and directory
    parser = argparse.ArgumentParser(description='Concurrency-Safe Code Point Open Staging Ingestion')
    parser.add_argument('--source-path', required=True, help='Path to CSV file or directory containing CSV files')
    parser.add_argument('--session-id', help='Session identifier for concurrent ingestion')
    parser.add_argument('--client', help='Client name for data traceability')
    parser.add_argument('--output-csv', help='Output path for combined CSV file (optional, creates temp file if not specified)')
    parser.add_argument('--max-rows', type=int, default=None, help='Maximum number of rows to ingest (for debugging)')
    parser.add_argument('--use-temp-file', action='store_true', help='Use temporary file instead of memory buffer (for large datasets on Windows)')
    
    args = parser.parse_args()
    
    # Determine if source-path is a file or directory
    if os.path.isdir(args.source_path):
        data_dir = args.source_path
        csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
        if not csv_files:
            logger.error(f"No CSV files found in directory: {data_dir}")
            sys.exit(1)
    elif os.path.isfile(args.source_path):
        data_dir = os.path.dirname(args.source_path)
        csv_files = [args.source_path]
    else:
        logger.error(f"source-path is not a valid file or directory: {args.source_path}")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("CONCURRENCY-SAFE CODE POINT OPEN STAGING INGESTION")
    logger.info("=" * 60)
    logger.info(f"Data directory: {data_dir}")
    logger.info(f"Session ID: {args.session_id or 'auto-generated'}")
    logger.info(f"Client: {args.client or 'default_client'}")
    if args.output_csv:
        logger.info(f"Output CSV: {args.output_csv}")
    else:
        logger.info("Output CSV: Temporary file (will be cleaned up)")
    logger.info("=" * 60)
    
    try:
        # Step 1: Check if staging table exists
        if not check_staging_table_exists():
            sys.exit(1)
        
        # Step 2: Load data into staging table
        success, batch_id = load_data_to_staging(
            data_dir,
            args.session_id,
            args.client,
            args.output_csv
        )
        
        if success:
            # Step 3: Verify staging data quality
            verify_staging_data_quality(batch_id, args.session_id, args.client)
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
