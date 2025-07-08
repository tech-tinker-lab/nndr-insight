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
    parser.add_argument('csv_file', nargs='?', 
                       default="data/os_open_names.csv",
                       help='Path to OS Open Names CSV file')
    
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

def load_os_open_names_to_staging(input_path, batch_id, session_id, source_name, client_name, file_metadata, max_rows=None, use_temp_file=False):
    """Load OS Open Names data into staging table from a file or directory of CSVs (no header in source files)."""
    import csv
    from io import StringIO
    from tqdm import tqdm
    import os
    import tempfile

    # Determine if input_path is a file or directory
    if os.path.isdir(input_path):
        csv_files = sorted(glob.glob(os.path.join(input_path, '*.csv')))
        if not csv_files:
            logger.error(f"No CSV files found in directory: {input_path}")
            return False, 0
        logger.info(f"Found {len(csv_files)} CSV files in directory: {input_path}")
        total_lines = get_total_lines_in_files(csv_files)
    else:
        csv_files = [input_path]
        total_lines = get_total_lines_in_files(csv_files)

    start_time = datetime.now()
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                logger.info(f"Starting OS Open Names staging ingestion: {input_path}")
                logger.info(f"Batch ID: {batch_id}")
                logger.info(f"Session ID: {session_id}")
                logger.info(f"Source: {source_name}")
                logger.info(f"Client: {client_name}")
                if use_temp_file:
                    logger.info("Using temporary file for buffer (Windows memory optimization)")
                    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
                    writer = csv.writer(temp_file)
                else:
                    output_buffer = StringIO()
                    writer = csv.writer(output_buffer)
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
                # Do NOT write a header row
                pbar = tqdm(total=total_lines, desc="Ingesting rows")
                first_rows = []
                row_counter = 0
                for file_idx, csv_file in enumerate(csv_files):
                    this_file_metadata = get_file_metadata(csv_file)
                    if not this_file_metadata:
                        logger.warning(f"Skipping file with missing metadata: {csv_file}")
                        continue
                    # Use utf-8-sig to strip BOM if present
                    with open(csv_file, 'r', encoding='utf-8-sig') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            # Skip blank lines
                            if not row or all(cell.strip() == '' for cell in row):
                                continue
                            # Truncate or warn on too many columns
                            if len(row) > len(data_columns):
                                logger.warning(f"Row has too many columns ({len(row)}): {row}")
                                row = row[:len(data_columns)]
                            # Pad short rows
                            while len(row) < len(data_columns):
                                row.append('')
                            # Now row is exactly 35 columns
                            metadata_row = [
                                source_name,
                                USER,
                                datetime.now().isoformat(),
                                batch_id,
                                os.path.basename(csv_file),
                                str(this_file_metadata['file_size']),
                                this_file_metadata['file_modified'].isoformat(),
                                session_id,
                                client_name
                            ]
                            full_row = row + metadata_row
                            writer.writerow(full_row)
                            if len(first_rows) < 5:
                                first_rows.append(full_row)
                            pbar.update(1)
                            row_counter += 1
                            if max_rows is not None and row_counter >= max_rows:
                                logger.info(f"Reached max_rows={max_rows}, stopping early for debug.")
                                break
                    if max_rows is not None and row_counter >= max_rows:
                        break
                pbar.close()
                if use_temp_file:
                    temp_file.close()
                    logger.info(f"Temporary file created: {temp_file.name}")
                else:
                    output_buffer.seek(0)
                # Debug: print first 5 rows and column counts
                logger.info(f"COPY will use {len(data_columns + metadata_columns)} columns: {data_columns + metadata_columns}")
                for i, r in enumerate(first_rows):
                    logger.info(f"Row {i+1} ({len(r)} columns): {r}")
                if use_temp_file:
                    copy_sql = f"""
                        COPY os_open_names_staging (
                            {', '.join(data_columns + metadata_columns)}
                        )
                        FROM '{temp_file.name}' WITH (FORMAT CSV)
                    """
                    cur.execute(copy_sql)
                    # Clean up temp file
                    os.unlink(temp_file.name)
                    logger.info("Temporary file cleaned up")
                else:
                    copy_sql = f"""
                        COPY os_open_names_staging (
                            {', '.join(data_columns + metadata_columns)}
                        )
                        FROM STDIN WITH (FORMAT CSV)
                    """
                    cur.copy_expert(sql=copy_sql, file=output_buffer)
                conn.commit()
                cur.execute("""
                    SELECT COUNT(*) FROM os_open_names_staging 
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
    except ImportError:
        logger.error("tqdm is not installed. Please install it with 'pip install tqdm' for progress bar support.")
        return False, 0
    except Exception as e:
        logger.error(f"❌ Error during staging ingestion: {e}")
        return False, 0

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
    
    # Get file metadata (for directory, use first file's metadata)
    if os.path.isdir(args.csv_file):
        # Find all CSV files in the directory
        csv_files = sorted(glob.glob(os.path.join(args.csv_file, '*.csv')))
        if not csv_files:
            logger.error(f"No CSV files found in directory: {args.csv_file}")
            sys.exit(1)
        file_metadata = get_file_metadata(csv_files[0])
    else:
        file_metadata = get_file_metadata(args.csv_file)
    if not file_metadata:
        logger.error(f"Could not read file metadata for: {args.csv_file}")
        sys.exit(1)
    
    # Print DB connection and audit details
    logger.info("Database connection details:")
    logger.info(f"  Host: {HOST}")
    logger.info(f"  Port: {PORT}")
    logger.info(f"  DB Name: {DBNAME}")
    logger.info(f"  User: {USER}")
    logger.info(f"  Password: {'***' if PASSWORD else '(not set)'}")
    logger.info(f"CSV file: {args.csv_file}")
    logger.info(f"Client: {client_name}")
    logger.info(f"Source: {source_name}")
    logger.info(f"Batch ID: {batch_id}")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"File path: {file_metadata['file_path']}")
    logger.info(f"File size: {file_metadata['file_size']}")
    logger.info(f"File modified: {file_metadata['file_modified']}")
    logger.info("=" * 60)
    logger.info("OS OPEN NAMES STAGING-ONLY INGESTION")
    logger.info("=" * 60)
    logger.info(f"Staging table: os_open_names_staging")
    logger.info("=" * 60)
    
    try:
        # Load data into staging table
        success, rowcount = load_os_open_names_to_staging(
            args.csv_file, batch_id, session_id, source_name, client_name, file_metadata,
            max_rows=args.max_rows, use_temp_file=args.use_temp_file
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