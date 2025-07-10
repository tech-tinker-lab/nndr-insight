#!/usr/bin/env python3
"""
NNDR Properties Staging-Only Ingestion Script
Loads NNDR properties data into staging table only with client and source tracking
"""

import psycopg2
import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

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

def check_table_exists(table_name):
    """Check if the staging table exists"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, (table_name,))
                exists = cur.fetchone()[0]
                if not exists:
                    logger.error(f"❌ Table '{table_name}' does not exist!")
                    logger.error("Please create the staging table first using the database setup scripts.")
                    return False
                return True
    except Exception as e:
        logger.error(f"❌ Error checking table existence: {e}")
        return False

def examine_csv_structure(csv_file):
    import csv
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            lines = [f.readline().strip() for _ in range(10)]
            # Check for * delimiter and 17 columns in all lines
            for idx, line in enumerate(lines):
                if not line:
                    continue
                cols = line.split('*')
                if len(cols) != 17:
                    logger.error(f"Line {idx+1} in {os.path.basename(csv_file)} does not have 17 columns (found {len(cols)}). Aborting.")
                    return None, ',', False
            logger.info(f"Detected headerless, *-delimited file with 17 columns: {os.path.basename(csv_file)}")
            header = [f'col{i+1}' for i in range(17)]
            return header, '*', True
    except Exception as e:
        logger.error(f"❌ Error reading CSV file: {e}")
        return None, ',', False

def map_columns_to_schema(csv_columns):
    """Map CSV columns to expected schema columns"""
    expected_columns = [
        'list_altered', 'community_code', 'ba_reference', 'property_category_code',
        'property_description', 'property_address', 'street_descriptor', 'locality',
        'post_town', 'administrative_area', 'postcode', 'effective_date',
        'partially_domestic_signal', 'rateable_value', 'scat_code',
        'appeal_settlement_code', 'unique_property_ref'
    ]
    if csv_columns is None:
        return {col: '' for col in expected_columns}, expected_columns
    # If headerless 17-column NNDR historic format, use fixed mapping
    if len(csv_columns) == 17 and all(col.startswith('col') for col in csv_columns):
        mapping = {
            'list_altered': 'col1',
            'community_code': 'col2',
            'ba_reference': 'col3',
            'property_category_code': 'col4',
            'property_description': 'col5',
            'property_address': 'col6',
            'street_descriptor': 'col7',
            'locality': 'col8',
            'post_town': 'col9',
            'administrative_area': 'col10',
            'postcode': 'col11',
            'effective_date': 'col12',
            'partially_domestic_signal': 'col13',
            'rateable_value': 'col14',
            'scat_code': 'col15',
            'appeal_settlement_code': 'col16',
            'unique_property_ref': 'col17',
        }
        unmapped_columns = []
        return mapping, unmapped_columns
    
    # Original logic for named columns
    column_mapping = {
        # BA Reference variations
        'ba_reference': ['ba_reference', 'ba_reference_number', 'ba_ref', 'ba_ref_no', 'reference'],
        'property_category_code': ['property_category_code', 'category_code', 'prop_category', 'category'],
        'property_description': ['property_description', 'description', 'prop_desc', 'desc'],
        'property_address': ['property_address', 'address', 'prop_address', 'full_address'],
        'street_descriptor': ['street_descriptor', 'street', 'street_name', 'road'],
        'locality': ['locality', 'locality_name', 'area'],
        'post_town': ['post_town', 'town', 'city'],
        'administrative_area': ['administrative_area', 'admin_area', 'county', 'district'],
        'postcode': ['postcode', 'post_code', 'postal_code', 'pc'],
        'effective_date': ['effective_date', 'date', 'valuation_date', 'list_date'],
        'rateable_value': ['rateable_value', 'rateable_val', 'rv', 'value'],
        'scat_code': ['scat_code', 'scat', 'sector_code'],
        'unique_property_ref': ['unique_property_ref', 'uprn', 'property_ref', 'unique_ref']
    }
    
    # Create mapping from CSV columns to expected columns
    mapping = {}
    unmapped_columns = []
    
    for expected_col in expected_columns:
        mapped = False
        for csv_col in csv_columns:
            csv_col_lower = csv_col.lower().replace(' ', '_').replace('-', '_')
            if csv_col_lower == expected_col.lower():
                mapping[expected_col] = csv_col
                mapped = True
                break
            elif expected_col in column_mapping:
                for variation in column_mapping[expected_col]:
                    if csv_col_lower == variation.lower():
                        mapping[expected_col] = csv_col
                        mapped = True
                        break
                if mapped:
                    break
        
        if not mapped:
            mapping[expected_col] = ''  # Will be filled with empty string
            unmapped_columns.append(expected_col)
    
    return mapping, unmapped_columns

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='NNDR Properties Staging-Only Ingestion (expects a single headerless, *-delimited file with exactly 17 columns)')
    parser.add_argument('--source-file', required=True, help='Path to NNDR properties CSV file (must be headerless, *-delimited, 17 columns)')
    parser.add_argument('--client', help='Client identifier (e.g., "client_001", "internal_team")')
    parser.add_argument('--source', help='Source identifier (e.g., "NNDR_2024", "VOA_2025")')
    parser.add_argument('--session-id', help='Session identifier for concurrent ingestion (auto-generated if not provided)')
    parser.add_argument('--batch-id', help='Batch identifier (auto-generated if not provided)')
    parser.add_argument('--dbname', help='Override database name from environment')
    parser.add_argument('--max-rows', type=int, default=None, help='Maximum number of rows to ingest (for debugging)')
    parser.add_argument('--examine-only', action='store_true', help='Only examine CSV structure, do not ingest')
    return parser.parse_args()

def generate_identifiers(args):
    """Generate batch_id and session_id if not provided"""
    batch_id = args.batch_id or f"nndr_properties_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
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

def count_rows_in_csv(csv_file, delimiter=','):
    """Count rows in CSV file for progress bar"""
    import csv
    try:
        if not delimiter:
            delimiter = ','
        with open(csv_file, 'r', encoding='utf-8') as f:
            return sum(1 for _ in csv.reader(f, delimiter=delimiter)) - 1  # Subtract header
    except Exception:
        return 0

def load_nndr_properties_to_staging(csv_files, batch_id, session_id, source_name, client_name, max_rows=None, args=None):
    """Load NNDR properties data into staging table"""
    import csv
    from io import StringIO
    from tqdm import tqdm
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                logger.info(f"Starting NNDR properties staging ingestion: {csv_files}")
                logger.info(f"Batch ID: {batch_id}")
                logger.info(f"Session ID: {session_id}")
                logger.info(f"Source: {source_name}")
                logger.info(f"Client: {client_name}")
                
                output_buffer = StringIO()
                writer = csv.writer(output_buffer)
                columns = [
                    'list_altered', 'community_code', 'ba_reference', 'property_category_code',
                    'property_description', 'property_address', 'street_descriptor', 'locality',
                    'post_town', 'administrative_area', 'postcode', 'effective_date',
                    'partially_domestic_signal', 'rateable_value', 'scat_code',
                    'appeal_settlement_code', 'unique_property_ref'
                ]
                metadata_columns = [
                    'source_name', 'upload_user', 'upload_timestamp',
                    'batch_id', 'source_file', 'file_size', 'file_modified', 'session_id', 'client_name'
                ]
                writer.writerow(columns + metadata_columns)
                
                row_counter = 0
                total_files = len(csv_files)
                
                for file_idx, csv_file in enumerate(csv_files, 1):
                    file_size = os.path.getsize(csv_file)
                    file_modified = datetime.fromtimestamp(os.path.getmtime(csv_file))
                    file_name = os.path.basename(csv_file)
                    
                    # Examine CSV structure
                    csv_columns, detected_delimiter, is_headerless = examine_csv_structure(csv_file)
                    if csv_columns is None:
                        logger.error(f"❌ Could not read CSV structure from {csv_file}")
                        continue
                    
                    # Map columns
                    column_mapping, unmapped_columns = map_columns_to_schema(csv_columns)
                    if not column_mapping:
                        logger.error(f"❌ Could not map columns for {csv_file}")
                        continue
                    
                    if unmapped_columns:
                        logger.warning(f"⚠️  Unmapped columns for {file_name}: {unmapped_columns}")
                        logger.info("   These columns will be filled with empty strings")
                    
                    # Count rows for progress bar
                    total_rows = count_rows_in_csv(csv_file, detected_delimiter)
                    if max_rows is not None:
                        total_rows = min(total_rows, max_rows - row_counter)
                    
                    logger.info(f"Processing file {file_idx}/{total_files}: {file_name} ({total_rows:,} rows)")
                    
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f, delimiter=detected_delimiter)
                        if not is_headerless:
                            next(reader)  # Skip header
                        
                        pbar = tqdm(reader, total=total_rows, desc=f"File {file_idx}/{total_files}: {file_name}")
                        
                        for row in pbar:
                            if len(row) != 17:
                                logger.error(f"Row {row_counter+1} in {file_name} does not have 17 columns (found {len(row)}). Aborting.")
                                sys.exit(1)
                            row_dict = {f'col{i+1}': value for i, value in enumerate(row)}
                            
                            # Map to expected columns
                            mapped_row = []
                            for expected_col in columns:
                                mapping_key = column_mapping.get(expected_col)
                                if mapping_key is not None and mapping_key in row_dict:
                                    mapped_row.append(row_dict[mapping_key])
                                else:
                                    mapped_row.append('')  # Empty string for unmapped columns
                            
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
                            writer.writerow(mapped_row + metadata_row)
                            row_counter += 1
                            
                            if max_rows is not None and row_counter >= max_rows:
                                logger.info(f"Reached max_rows={max_rows}, stopping early for debug.")
                                break
                        
                        pbar.close()
                    
                    if max_rows is not None and row_counter >= max_rows:
                        break
                
                output_buffer.seek(0)
                
                # Show progress for database loading
                logger.info("Loading data from temporary file into database...")
                with tqdm(total=row_counter, desc="Database loading", unit="rows") as pbar:
                    copy_sql = f"""
                        COPY nndr_properties_staging (
                            {', '.join(columns + metadata_columns)}
                        )
                        FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
                    """
                    cur.copy_expert(sql=copy_sql, file=output_buffer)
                    pbar.update(row_counter)
                
                conn.commit()
                
                cur.execute("""
                    SELECT COUNT(*) FROM nndr_properties_staging 
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
    logger.info("Verifying NNDR properties staging data quality...")
    
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
                cur.execute(f"SELECT COUNT(*) FROM nndr_properties_staging {where_clause};", params)
                total_count_result = cur.fetchone()
                total_count = total_count_result[0] if total_count_result else 0
                
                # Check for empty BA references
                cur.execute(f"SELECT COUNT(*) FROM nndr_properties_staging {where_clause} AND (ba_reference IS NULL OR ba_reference = '');", params)
                null_ba_result = cur.fetchone()
                null_ba_count = null_ba_result[0] if null_ba_result else 0
                
                # Check for empty postcodes
                cur.execute(f"SELECT COUNT(*) FROM nndr_properties_staging {where_clause} AND (postcode IS NULL OR postcode = '');", params)
                null_postcode_result = cur.fetchone()
                null_postcode_count = null_postcode_result[0] if null_postcode_result else 0
                
                logger.info("=" * 60)
                logger.info("NNDR PROPERTIES STAGING DATA QUALITY REPORT")
                logger.info("=" * 60)
                logger.info(f"Total records: {total_count:,}")
                logger.info(f"Null BA references: {null_ba_count:,}")
                logger.info(f"Null postcodes: {null_postcode_count:,}")
                logger.info(f"Valid records: {total_count - null_ba_count:,}")
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
    args = parse_arguments()
    
    if args.dbname:
        global DBNAME
        DBNAME = args.dbname
    
    # Check if staging table exists (unless examine-only mode)
    if not args.examine_only and not check_table_exists('nndr_properties_staging'):
        sys.exit(1)
    
    batch_id, session_id = generate_identifiers(args)
    source_name = args.source or "NNDR_PROPERTIES_DEFAULT"
    client_name = args.client or "default_client"
    
    # Determine if source-file is a file or directory
    if os.path.isdir(args.source_file):
        logger.error(f"source-file is a directory: {args.source_file}. This script expects a single CSV file.")
        sys.exit(1)
    elif os.path.isfile(args.source_file):
        csv_files = [args.source_file]
    else:
        logger.error(f"source-file is not a valid file or directory: {args.source_file}")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("NNDR PROPERTIES STAGING-ONLY INGESTION")
    logger.info("=" * 60)
    logger.info(f"CSV files: {csv_files}")
    logger.info(f"Staging table: nndr_properties_staging")
    logger.info(f"Source: {source_name}")
    logger.info(f"Client: {client_name}")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Batch ID: {batch_id}")
    
    # Improved file metadata logging
    if len(csv_files) == 1:
        logger.info(f"File path: {csv_files[0]}")
        logger.info(f"File size: {os.path.getsize(csv_files[0]):,} bytes")
        logger.info(f"File modified: {datetime.fromtimestamp(os.path.getmtime(csv_files[0]))}")
    else:
        logger.info(f"Number of files: {len(csv_files)}")
        logger.info(f"First file: {csv_files[0]}")
        logger.info(f"First file size: {os.path.getsize(csv_files[0]):,} bytes")
        logger.info(f"First file modified: {datetime.fromtimestamp(os.path.getmtime(csv_files[0]))}")
        total_size = sum(os.path.getsize(f) for f in csv_files)
        logger.info(f"Total size of all files: {total_size:,} bytes")
    
    logger.info("=" * 60)
    
    # Examine-only mode
    if args.examine_only:
        logger.info("🔍 EXAMINE-ONLY MODE - No data will be ingested")
        for csv_file in csv_files:
            csv_columns, detected_delimiter, is_headerless = examine_csv_structure(csv_file)
            if csv_columns is None:
                logger.error(f"❌ Could not read CSV structure from {csv_file}")
                continue
            column_mapping, unmapped_columns = map_columns_to_schema(csv_columns)
            if not column_mapping:
                logger.error(f"❌ Could not map columns for {csv_file}")
                continue
            logger.info(f"📊 Column mapping for {os.path.basename(csv_file)}:")
            for expected_col, csv_col in column_mapping.items():
                if csv_col:
                    logger.info(f"   ✓ {expected_col} ← {csv_col}")
                else:
                    logger.info(f"   ✗ {expected_col} ← (empty)")
            if unmapped_columns:
                logger.warning(f"   ⚠️  Unmapped columns: {unmapped_columns}")
        return
    
    try:
        success, rowcount = load_nndr_properties_to_staging(
            csv_files, batch_id, session_id, source_name, client_name, max_rows=args.max_rows, args=args
        )
        
        if success:
            logger.info("✅ NNDR properties staging ingestion completed successfully!")
            logger.info(f"📊 Data loaded into staging table with batch_id: {batch_id}")
            
            # Verify data quality
            verify_staging_data(batch_id, session_id)
        else:
            logger.error("❌ Data loading failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
