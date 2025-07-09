#!/usr/bin/env python3
"""
Valuations Staging-Only Ingestion Script
Loads valuations data into staging table only with client and source tracking
"""

import psycopg2
import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

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

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='Valuations Staging-Only Ingestion')
    
    # Required: CSV file path
    parser.add_argument('--source-path', required=True, help='Path to valuations CSV file or directory')
    
    # Optional: Client and source information
    parser.add_argument('--client', 
                       help='Client identifier (e.g., "client_001", "internal_team")')
    parser.add_argument('--source', 
                       help='Source identifier (e.g., "VALUATIONS_2024", "VOA_2025")')
    parser.add_argument('--session-id', 
                       help='Session identifier for concurrent ingestion (auto-generated if not provided)')
    parser.add_argument('--batch-id', 
                       help='Batch identifier (auto-generated if not provided)')
    
    # Optional: Database override
    parser.add_argument('--dbname', 
                       help='Override database name from environment')
    parser.add_argument('--max-rows', type=int, default=None, help='Maximum number of rows to ingest (for debugging)')
    
    return parser.parse_args()

def generate_identifiers(args):
    """Generate batch_id and session_id if not provided"""
    batch_id = args.batch_id or f"valuations_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    session_id = args.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return batch_id, session_id

def get_file_metadata(file_path):
    """Get metadata about the source file"""
    if not os.path.isfile(file_path):
        return None
    
    return {
        'file_size': os.path.getsize(file_path),
        'file_modified': datetime.fromtimestamp(os.path.getmtime(file_path)),
        'file_name': os.path.basename(file_path),
        'file_path': file_path
    }

def load_valuations_to_staging(csv_files, batch_id, session_id, source_name, client_name, max_rows=None):
    """Load valuations data into staging table"""
    import csv
    from io import StringIO
    from tqdm import tqdm
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                logger.info(f"Starting valuations staging ingestion: {csv_files}")
                logger.info(f"Batch ID: {batch_id}")
                logger.info(f"Session ID: {session_id}")
                logger.info(f"Source: {source_name}")
                logger.info(f"Client: {client_name}")
                output_buffer = StringIO()
                writer = csv.writer(output_buffer)
                columns = [
                    'ba_reference', 'valuation_date', 'rateable_value', 'valuation_type',
                    'valuation_reason', 'assessor_name', 'assessment_date', 'notes'
                ]
                metadata_columns = [
                    'source_name', 'upload_user', 'upload_timestamp',
                    'batch_id', 'source_file', 'file_size', 'file_modified', 'session_id', 'client_name'
                ]
                writer.writerow(columns + metadata_columns)
                row_counter = 0
                for csv_file in csv_files:
                    file_size = os.path.getsize(csv_file)
                    file_modified = datetime.fromtimestamp(os.path.getmtime(csv_file))
                    file_name = os.path.basename(csv_file)
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        pbar = tqdm(reader, desc=f"Ingesting {file_name}")
                        for row in pbar:
                            while len(row) < len(columns):
                                row.append('')
                            metadata_row = [
                                source_name,
                                USER,
                                datetime.now().isoformat(),
                                batch_id,
                                file_name,
                                str(file_size),
                                file_modified.isoformat(),
                                session_id,
                                client_name
                            ]
                            writer.writerow(row + metadata_row)
                            row_counter += 1
                            if max_rows is not None and row_counter >= max_rows:
                                logger.info(f"Reached max_rows={max_rows}, stopping early for debug.")
                                break
                        pbar.close()
                    if max_rows is not None and row_counter >= max_rows:
                        break
                output_buffer.seek(0)
                copy_sql = f"""
                    COPY valuations_staging (
                        {', '.join(columns + metadata_columns)}
                    )
                    FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
                """
                cur.copy_expert(sql=copy_sql, file=output_buffer)
                conn.commit()
                cur.execute("""
                    SELECT COUNT(*) FROM valuations_staging 
                    WHERE batch_id = %s AND session_id = %s
                """, (batch_id, session_id))
                rowcount_result = cur.fetchone()
                rowcount = rowcount_result[0] if rowcount_result else 0
                logger.info(f"✅ Successfully loaded {rowcount:,} rows")
                return True, rowcount
    except Exception as e:
        logger.error(f"❌ Error during staging ingestion: {e}")
        return False, 0

def verify_staging_data(batch_id=None, session_id=None):
    """Verify the loaded staging data quality"""
    logger.info("Verifying valuations staging data quality...")
    
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
                cur.execute(f"SELECT COUNT(*) FROM valuations_staging {where_clause};", params)
                total_count_result = cur.fetchone()
                total_count = total_count_result[0] if total_count_result else 0
                
                # Check for empty BA references
                cur.execute(f"SELECT COUNT(*) FROM valuations_staging {where_clause} AND (ba_reference IS NULL OR ba_reference = '');", params)
                null_ba_result = cur.fetchone()
                null_ba_count = null_ba_result[0] if null_ba_result else 0
                
                # Check for empty rows
                cur.execute(f"SELECT COUNT(*) FROM valuations_staging {where_clause} AND (raw_line IS NULL OR raw_line = '');", params)
                empty_result = cur.fetchone()
                empty_count = empty_result[0] if empty_result else 0
                
                logger.info("=" * 60)
                logger.info("VALUATIONS STAGING DATA QUALITY REPORT")
                logger.info("=" * 60)
                logger.info(f"Total records: {total_count:,}")
                logger.info(f"Null BA references: {null_ba_count}")
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
    # Parse arguments
    args = parse_arguments()
    
    # Override database if specified
    if args.dbname:
        global DBNAME
        DBNAME = args.dbname
    
    # Generate identifiers
    batch_id, session_id = generate_identifiers(args)
    
    # Get source and client names
    source_name = args.source or "VALUATIONS_DEFAULT"
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
    logger.info("VALUATIONS STAGING-ONLY INGESTION")
    logger.info("=" * 60)
    logger.info(f"CSV files: {csv_files}")
    logger.info(f"Staging table: valuations_staging")
    logger.info(f"Source: {source_name}")
    logger.info(f"Client: {client_name}")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Batch ID: {batch_id}")
    logger.info("=" * 60)
    
    try:
        # Load data into staging table
        success, rowcount = load_valuations_to_staging(
            csv_files, batch_id, session_id, source_name, client_name, max_rows=args.max_rows
        )
        
        if success:
            # Verify staging data quality
            verify_staging_data(batch_id, session_id)
            logger.info("✅ Valuations staging ingestion completed successfully!")
            logger.info(f"📊 Data loaded into staging table with batch_id: {batch_id}")
        else:
            logger.error("❌ Data loading failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
