#!/usr/bin/env python3
"""
OS Open Names Staging-Only Ingestion Script
Loads OS Open Names data into staging table only with client and source tracking
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
from tqdm import tqdm
import glob
import tempfile

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

# Official OS Open Names columns
OS_OPEN_NAMES_COLUMNS = [
    'ID', 'NAMES_URI', 'NAME1', 'NAME1_LANG', 'NAME2', 'NAME2_LANG', 'TYPE', 'LOCAL_TYPE',
    'GEOMETRY_X', 'GEOMETRY_Y', 'MOST_DETAIL_VIEW_RES', 'LEAST_DETAIL_VIEW_RES',
    'MBR_XMIN', 'MBR_YMIN', 'MBR_XMAX', 'MBR_YMAX', 'POSTCODE_DISTRICT', 'POSTCODE_DISTRICT_URI',
    'POPULATED_PLACE', 'POPULATED_PLACE_URI', 'POPULATED_PLACE_TYPE', 'DISTRICT_BOROUGH',
    'DISTRICT_BOROUGH_URI', 'DISTRICT_BOROUGH_TYPE', 'COUNTY_UNITARY', 'COUNTY_UNITARY_URI',
    'COUNTY_UNITARY_TYPE', 'REGION', 'REGION_URI', 'COUNTRY', 'COUNTRY_URI',
    'RELATED_SPATIAL_OBJECT', 'SAME_AS_DBPEDIA', 'SAME_AS_GEONAMES'
]

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
    parser = argparse.ArgumentParser(description='OS Open Names Staging-Only Ingestion')
    
    # Required: CSV file path
    parser.add_argument('--source-path', required=True, help='Path to OS Open Names CSV file or directory')
    
    # Optional: Client and source information
    parser.add_argument('--client', 
                       help='Client identifier (e.g., "client_001", "internal_team")')
    parser.add_argument('--source', 
                       help='Source identifier (e.g., "OS_Open_Names_2024", "OS_2025")')
    parser.add_argument('--session-id', 
                       help='Session identifier for concurrent ingestion (auto-generated if not provided)')
    parser.add_argument('--batch-id', 
                       help='Batch identifier (auto-generated if not provided)')
    
    # Optional: Database override
    parser.add_argument('--dbname', 
                       help='Override database name from environment')
    parser.add_argument('--max-rows', type=int, default=None, help='Maximum number of rows to ingest (for debugging)')
    parser.add_argument('--use-temp-file', action='store_true', help='Use temporary file instead of memory buffer (for large datasets on Windows)')
    parser.add_argument('--output-csv', help='Path to save the combined CSV file for server-side COPY (optional, for large datasets)')
    parser.add_argument('--load-from-csv', help='Load directly from existing combined CSV file (skip aggregation step)')
    
    return parser.parse_args()

def generate_identifiers(args):
    """Generate batch_id and session_id if not provided"""
    batch_id = args.batch_id or str(uuid.uuid4())
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

def get_total_lines_in_files(file_list):
    total = 0
    for file in file_list:
        with open(file, 'r', encoding='utf-8') as f:
            total += sum(1 for _ in f)
    return total

def load_os_open_names_to_staging(csv_files, batch_id, session_id, source_name, client_name, max_rows=None, use_temp_file=False, output_csv_path=None, load_from_csv=None):
    import csv
    from io import StringIO
    from tqdm import tqdm
    import os
    import tempfile
    import shutil
    import sys
    import uuid
    from datetime import datetime
    
    # Define columns
    metadata_columns = [
        'source_name', 'upload_user', 'upload_timestamp',
        'batch_id', 'source_file', 'file_size', 'file_modified', 'session_id', 'client_name'
    ]
    data_columns = [
        'id_text', 'names_uri', 'name1', 'name1_lang', 'name2', 'name2_lang', 'type', 'local_type',
        'geometry_x', 'geometry_y', 'most_detail_view_res', 'least_detail_view_res',
        'mbr_xmin', 'mbr_ymin', 'mbr_xmax', 'mbr_ymax', 'postcode_district', 'postcode_district_uri',
        'populated_place', 'populated_place_uri', 'populated_place_type', 'district_borough',
        'district_borough_uri', 'district_borough_type', 'county_unitary', 'county_unitary_uri',
        'county_unitary_type', 'region', 'region_uri', 'country', 'country_uri',
        'related_spatial_object', 'same_as_dbpedia', 'same_as_geonames', 'geom'
    ]
    
    # If loading from existing CSV, skip aggregation
    if load_from_csv:
        if not os.path.exists(load_from_csv):
            logger.error(f"❌ Combined CSV file not found: {load_from_csv}")
            return False, 0
        
        logger.info(f"📁 Loading from existing combined CSV: {load_from_csv}")
        combined_csv_path = os.path.abspath(load_from_csv)
    else:
        # Normal aggregation process
        total_lines = 0
        for csv_file in csv_files:
            with open(csv_file, 'r', encoding='utf-8') as f:
                total_lines += sum(1 for _ in f)
        
        # Use output_csv_path if provided, else temp file
        if output_csv_path:
            # Convert relative path to absolute path
            if not os.path.isabs(output_csv_path):
                combined_csv_path = os.path.abspath(output_csv_path)
                logger.info(f"📁 Converting relative path to absolute: {output_csv_path} → {combined_csv_path}")
            else:
                combined_csv_path = output_csv_path
        else:
            logger.warning("No --output-csv provided. Using a temp file, which may not work for server-side COPY on Windows if PostgreSQL cannot access it.")
            combined_csv_path = os.path.join(tempfile.gettempdir(), f'os_open_names_combined_{batch_id}.csv')
        
        # Create the combined CSV file
        with open(combined_csv_path, 'w', encoding='utf-8', newline='') as tmpfile:
            writer = csv.writer(tmpfile)
            writer.writerow(data_columns + metadata_columns)
            row_counter = 0
            with tqdm(total=total_lines, desc="Aggregating rows") as pbar:
                for csv_file in csv_files:
                    file_size = os.path.getsize(csv_file)
                    file_modified = datetime.fromtimestamp(os.path.getmtime(csv_file))
                    file_name = os.path.basename(csv_file)
                    with open(csv_file, 'r', encoding='utf-8-sig') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            # Skip blank lines
                            if not row or all(cell.strip() == '' for cell in row):
                                continue
                            # Truncate or warn on too many columns
                            if len(row) > len(data_columns):
                                row = row[:len(data_columns)]
                            # Pad short rows
                            while len(row) < len(data_columns):
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
                            pbar.update(1)
                            if max_rows is not None and row_counter >= max_rows:
                                break
                    if max_rows is not None and row_counter >= max_rows:
                        break
    
    # Bulk load with client-side COPY (works with local files)
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Use client-side COPY which can read local files
            with open(combined_csv_path, 'r', encoding='utf-8') as csv_file:
                # Skip header row
                next(csv_file)
                
                # Use COPY FROM STDIN for client-side loading
                copy_sql = f"""
                    COPY os_open_names_staging (
                        {', '.join(data_columns + metadata_columns)}
                    )
                    FROM STDIN WITH (FORMAT CSV)
                """
                cur.copy_expert(copy_sql, csv_file)
                conn.commit()
                
                cur.execute("""
                    SELECT COUNT(*) FROM os_open_names_staging 
                    WHERE batch_id = %s AND session_id = %s
                """, (batch_id, session_id))
                rowcount_result = cur.fetchone()
                rowcount = rowcount_result[0] if rowcount_result else 0
                logger.info(f"✅ Successfully loaded {rowcount:,} rows from aggregated file")
    
    # Clean up temp file if not user-specified and not loaded from existing
    if not output_csv_path and not load_from_csv:
        try:
            os.remove(combined_csv_path)
            logger.info(f"Temporary file cleaned up: {combined_csv_path}")
        except Exception as e:
            logger.warning(f"Could not remove temporary file {combined_csv_path}: {e}")
    
    return True, rowcount

def verify_staging_data(batch_id=None, session_id=None):
    """Verify the loaded staging data quality"""
    logger.info("Verifying OS Open Names staging data quality...")
    
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
                cur.execute(f"SELECT COUNT(*) FROM os_open_names_staging {where_clause};", params)
                total_count_result = cur.fetchone()
                total_count = total_count_result[0] if total_count_result else 0
                
                # Check for empty names
                cur.execute(f"SELECT COUNT(*) FROM os_open_names_staging {where_clause} AND (NAME1 IS NULL OR NAME1 = '');", params)
                null_name_result = cur.fetchone()
                null_name_count = null_name_result[0] if null_name_result else 0
                
                logger.info("=" * 60)
                logger.info("OS OPEN NAMES STAGING DATA QUALITY REPORT")
                logger.info("=" * 60)
                logger.info(f"Total records: {total_count:,}")
                logger.info(f"Null names: {null_name_count}")
                logger.info(f"Valid rows: {total_count - null_name_count:,}")
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
    source_name = args.source or "OS_Open_Names_DEFAULT"
    client_name = args.client or "default_client"
    
    # Determine if source-path is a file or directory (only needed if not loading from CSV)
    if args.load_from_csv:
        csv_files = []  # Not needed when loading from existing CSV
        logger.info(f"📁 Loading from existing combined CSV: {args.load_from_csv}")
    else:
        # Determine if source-path is a file or directory
        if os.path.isdir(args.source_path):
            csv_files = sorted(glob.glob(os.path.join(args.source_path, '*.csv')))
            if not csv_files:
                logger.error(f"No CSV files found in directory: {args.source_path}")
                sys.exit(1)
            file_metadata = get_file_metadata(csv_files[0])
        elif os.path.isfile(args.source_path):
            csv_files = [args.source_path]
            file_metadata = get_file_metadata(args.source_path)
        else:
            logger.error(f"source-path is not a valid file or directory: {args.source_path}")
            sys.exit(1)
        if not file_metadata:
            logger.error(f"Could not read file metadata for: {csv_files[0]}")
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
    logger.info("OS OPEN NAMES STAGING-ONLY INGESTION")
    logger.info("=" * 60)
    logger.info(f"Staging table: os_open_names_staging")
    if args.load_from_csv:
        logger.info(f"Mode: Load from existing CSV")
    elif args.output_csv:
        logger.info(f"Mode: Generate combined CSV")
    else:
        logger.info(f"Mode: Generate temporary CSV")
    logger.info("=" * 60)
    
    try:
        # Load data into staging table
        success, rowcount = load_os_open_names_to_staging(
            csv_files, batch_id, session_id, source_name, client_name,
            max_rows=args.max_rows, use_temp_file=args.use_temp_file, 
            output_csv_path=args.output_csv, load_from_csv=args.load_from_csv
        )
        
        if success:
            # Verify staging data quality
            verify_staging_data(batch_id, session_id)
            logger.info("✅ OS Open Names staging ingestion completed successfully!")
            logger.info(f"📊 Data loaded into staging table with batch_id: {batch_id}")
        else:
            logger.error("❌ Data loading failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 