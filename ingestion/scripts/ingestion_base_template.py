#!/usr/bin/env python3
"""
Base Template for Staging-Only Ingestion Scripts
All ingestion scripts should inherit from this pattern to ensure:
1. Data is only loaded into staging tables
2. Client and source information is captured via command-line arguments
3. Concurrency-safe ingestion with batch_id and session_id
4. Standardized logging and error handling
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

def parse_standard_arguments(description, default_csv_path=None):
    """
    Parse standard command-line arguments for all ingestion scripts
    
    Args:
        description: Script description
        default_csv_path: Default path to CSV file
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description=description)
    
    # Required: CSV file path
    parser.add_argument('csv_file', nargs='?', 
                       default=default_csv_path,
                       help='Path to CSV file')
    
    # Optional: Client and source information
    parser.add_argument('--client', 
                       help='Client identifier (e.g., "client_001", "internal_team")')
    parser.add_argument('--source', 
                       help='Source identifier (e.g., "OS_Open_UPRN", "NNDR_2024")')
    parser.add_argument('--session-id', 
                       help='Session identifier for concurrent ingestion (auto-generated if not provided)')
    parser.add_argument('--batch-id', 
                       help='Batch identifier (auto-generated if not provided)')
    
    # Optional: Database override
    parser.add_argument('--dbname', 
                       help='Override database name from environment')
    
    return parser.parse_args()

def generate_identifiers(args, dataset_type):
    """
    Generate batch_id and session_id if not provided
    
    Args:
        args: Parsed arguments
        dataset_type: Type of dataset (e.g., "uprn", "codepoint", "nndr")
    
    Returns:
        tuple: (batch_id, session_id)
    """
    batch_id = args.batch_id or f"{dataset_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    session_id = args.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return batch_id, session_id

def get_file_metadata(file_path):
    """
    Get metadata about the source file
    
    Args:
        file_path: Path to the file
    
    Returns:
        dict: File metadata
    """
    if not os.path.isfile(file_path):
        return None
    
    return {
        'file_size': os.path.getsize(file_path),
        'file_modified': datetime.fromtimestamp(os.path.getmtime(file_path)),
        'file_name': os.path.basename(file_path),
        'file_path': file_path
    }

def load_data_to_staging(csv_path, staging_table, columns, batch_id, session_id, 
                        source_name, client_name, file_metadata):
    """
    Load data into staging table with metadata
    
    Args:
        csv_path: Path to CSV file
        staging_table: Name of staging table
        columns: List of column names in order
        batch_id: Batch identifier
        session_id: Session identifier
        source_name: Source name
        client_name: Client name
        file_metadata: File metadata dictionary
    
    Returns:
        tuple: (success, row_count)
    """
    if not os.path.isfile(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        return False, 0

    start_time = datetime.now()
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                logger.info(f"Starting staging ingestion: {csv_path} → {staging_table}")
                logger.info(f"Batch ID: {batch_id}")
                logger.info(f"Session ID: {session_id}")
                logger.info(f"Source: {source_name}")
                logger.info(f"Client: {client_name}")
                
                # Use COPY for fast bulk insertion
                column_list = ', '.join(columns)
                copy_sql = f"""
                    COPY {staging_table} ({column_list})
                    FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
                """
                
                # Process CSV and add metadata columns
                from io import StringIO
                import csv
                
                output_buffer = StringIO()
                writer = csv.writer(output_buffer)
                
                # Write header with metadata columns
                metadata_columns = [
                    'raw_line', 'source_name', 'upload_user', 'upload_timestamp',
                    'batch_id', 'raw_filename', 'file_path', 'file_size', 
                    'file_modified', 'session_id', 'client_name'
                ]
                writer.writerow(columns + metadata_columns)
                
                # Process each data row and add metadata
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        # Add metadata columns
                        metadata_row = row + [
                            row[0] if row else '',  # raw_line (use first column)
                            source_name,  # source_name
                            USER,  # upload_user
                            datetime.now().isoformat(),  # upload_timestamp
                            batch_id,  # batch_id
                            file_metadata['file_name'],  # raw_filename
                            file_metadata['file_path'],  # file_path
                            str(file_metadata['file_size']),  # file_size
                            file_metadata['file_modified'].isoformat(),  # file_modified
                            session_id,  # session_id
                            client_name  # client_name
                        ]
                        writer.writerow(metadata_row)
                
                # Reset buffer and copy to staging table
                output_buffer.seek(0)
                cur.copy_expert(sql=copy_sql, file=output_buffer)
                conn.commit()

                # Get record count for this batch
                cur.execute(f"""
                    SELECT COUNT(*) FROM {staging_table} 
                    WHERE batch_id = %s AND session_id = %s
                """, (batch_id, session_id))
                rowcount_result = cur.fetchone()
                rowcount = rowcount_result[0] if rowcount_result else 0
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                rate = rowcount / duration if duration > 0 else 0
                
                logger.info(f"✅ Successfully loaded {rowcount:,} rows in {duration:.1f}s")
                logger.info(f"📊 Rate: {rate:,.0f} rows/second")
                
                return True, rowcount
                
    except Exception as e:
        logger.error(f"❌ Error during staging ingestion: {e}")
        return False, 0

def verify_staging_data(staging_table, batch_id=None, session_id=None):
    """
    Verify staging table data quality
    
    Args:
        staging_table: Name of staging table
        batch_id: Optional batch identifier
        session_id: Optional session identifier
    
    Returns:
        bool: Success status
    """
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
                cur.execute(f"SELECT COUNT(*) FROM {staging_table} {where_clause};", params)
                total_count_result = cur.fetchone()
                total_count = total_count_result[0] if total_count_result else 0
                
                # Check for empty rows
                cur.execute(f"SELECT COUNT(*) FROM {staging_table} {where_clause} AND (raw_line IS NULL OR raw_line = '');", params)
                empty_result = cur.fetchone()
                empty_count = empty_result[0] if empty_result else 0
                
                logger.info("=" * 60)
                logger.info("STAGING DATA QUALITY REPORT")
                logger.info("=" * 60)
                logger.info(f"Table: {staging_table}")
                logger.info(f"Total records: {total_count:,}")
                logger.info(f"Empty rows: {empty_count}")
                logger.info(f"Valid rows: {total_count - empty_count:,}")
                if batch_id:
                    logger.info(f"Batch ID: {batch_id}")
                if session_id:
                    logger.info(f"Session ID: {session_id}")
                logger.info("=" * 60)
                
                return True
                
    except Exception as e:
        logger.error(f"Error verifying staging data: {e}")
        return False

def main_template(dataset_type, staging_table, columns, description, default_csv_path=None):
    """
    Template main function for ingestion scripts
    
    Args:
        dataset_type: Type of dataset (e.g., "uprn", "codepoint")
        staging_table: Name of staging table
        columns: List of column names
        description: Script description
        default_csv_path: Default CSV file path
    """
    # Parse arguments
    args = parse_standard_arguments(description, default_csv_path)
    
    # Override database if specified
    if args.dbname:
        global DBNAME
        DBNAME = args.dbname
    
    # Generate identifiers
    batch_id, session_id = generate_identifiers(args, dataset_type)
    
    # Get source and client names
    source_name = args.source or f"{dataset_type.upper()}_DEFAULT"
    client_name = args.client or "default_client"
    
    # Get file metadata
    file_metadata = get_file_metadata(args.csv_file)
    if not file_metadata:
        logger.error(f"Could not read file metadata for: {args.csv_file}")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info(f"STAGING-ONLY {dataset_type.upper()} INGESTION")
    logger.info("=" * 60)
    logger.info(f"CSV file: {args.csv_file}")
    logger.info(f"Staging table: {staging_table}")
    logger.info(f"Source: {source_name}")
    logger.info(f"Client: {client_name}")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Batch ID: {batch_id}")
    logger.info("=" * 60)
    
    try:
        # Load data into staging table
        success, rowcount = load_data_to_staging(
            args.csv_file, staging_table, columns, batch_id, session_id,
            source_name, client_name, file_metadata
        )
        
        if success:
            # Verify staging data quality
            verify_staging_data(staging_table, batch_id, session_id)
            logger.info("✅ Staging ingestion completed successfully!")
            logger.info(f"📊 Data loaded into staging table with batch_id: {batch_id}")
        else:
            logger.error("❌ Data loading failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        sys.exit(1)

# Example usage:
# if __name__ == "__main__":
#     columns = ['uprn', 'x_coordinate', 'y_coordinate', 'latitude', 'longitude']
#     main_template(
#         dataset_type="uprn",
#         staging_table="os_open_uprn_staging",
#         columns=columns,
#         description="OS Open UPRN Staging Ingestion",
#         default_csv_path="data/osopenuprn.csv"
#     ) 