#!/usr/bin/env python3
"""
ONSPD Staging-Only Ingestion Script
Loads ONSPD data into staging table only with client and source tracking
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

def check_staging_table_exists():
    """Check if the staging table exists"""
    logger.info("Checking if onspd_staging table exists...")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Check if table exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'onspd_staging'
                    );
                """)
                result = cur.fetchone()
                table_exists = result[0] if result else False
                
                if not table_exists:
                    logger.error("❌ Table 'onspd_staging' does not exist!")
                    logger.error("Please create the table first using database setup scripts.")
                    return False
                
                logger.info("✅ Staging table exists")
                return True
                
    except Exception as e:
        logger.error(f"Error checking staging table: {e}")
        return False

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='ONSPD Staging-Only Ingestion')
    
    # Required: CSV file path
    parser.add_argument('--source-path', required=True, help='Path to ONSPD CSV file or directory')
    
    # Optional: Client and source information
    parser.add_argument('--client', 
                       help='Client identifier (e.g., "client_001", "internal_team")')
    parser.add_argument('--source', 
                       help='Source identifier (e.g., "ONSPD_2024", "ONS_2025")')
    parser.add_argument('--session-id', 
                       help='Session identifier for concurrent ingestion (auto-generated if not provided)')
    parser.add_argument('--batch-id', 
                       help='Batch identifier (auto-generated if not provided)')
    
    # Optional: Database override
    parser.add_argument('--dbname', 
                       help='Override database name from environment')
    parser.add_argument('--max-rows', type=int, help='Maximum number of rows to process (for testing - e.g., 100 for testing)')
    parser.add_argument('--encoding', default='utf-8', help='File encoding (default: utf-8, try latin-1 for older files)')
    parser.add_argument('--server-copy', action='store_true', help='Use server-side COPY (requires PostgreSQL server access to file)')
    
    return parser.parse_args()

def generate_identifiers(args):
    """Generate batch_id and session_id if not provided"""
    batch_id = args.batch_id or f"onspd_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
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

def load_onspd_to_staging(csv_files, batch_id, session_id, source_name, client_name, max_rows=None, encoding='utf-8', server_copy=True):
    """Load ONSPD data into staging table"""
    import csv
    from tqdm import tqdm
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                logger.info(f"Starting ONSPD staging ingestion: {csv_files}")
                logger.info(f"Batch ID: {batch_id}")
                logger.info(f"Session ID: {session_id}")
                logger.info(f"Source: {source_name}")
                logger.info(f"Client: {client_name}")
                
                # Map ALL ONSPD CSV columns to our staging table (57 columns)
                # CSV columns: ['\ufeffX', 'Y', 'OBJECTID', 'PCD', 'PCD2', 'PCDS', 'DOINTR', 'DOTERM', 'OSCTY', 'CED', 'OSLAUA', 'OSWARD', 'PARISH', 'USERTYPE', 'OSEAST1M', 'OSNRTH1M', 'OSGRDIND', 'OSHLTHAU', 'NHSER', 'CTRY', 'RGN', 'STREG', 'PCON', 'EER', 'TECLEC', 'TTWA', 'PCT', 'ITL', 'STATSWARD', 'OA01', 'CASWARD', 'NPARK', 'LSOA01', 'MSOA01', 'UR01IND', 'OAC01', 'OA11', 'LSOA11', 'MSOA11', 'WZ11', 'SICBL', 'BUA24', 'RU11IND', 'OAC11', 'LAT', 'LONG', 'LEP1', 'LEP2', 'PFA', 'IMD', 'CALNCV', 'ICB', 'OA21', 'LSOA21', 'MSOA21', 'RUC21IND', 'GlobalID']
                
                # Define the mapping from CSV column index to our staging table columns
                column_mapping = {
                    0: 'x_coord',      # X
                    1: 'y_coord',      # Y
                    2: 'objectid',     # OBJECTID
                    3: 'pcd',          # PCD
                    4: 'pcd2',         # PCD2
                    5: 'pcds',         # PCDS
                    6: 'dointr',       # DOINTR
                    7: 'doterm',       # DOTERM
                    8: 'oscty',        # OSCTY
                    9: 'ced',          # CED
                    10: 'oslaua',      # OSLAUA
                    11: 'osward',      # OSWARD
                    12: 'parish',      # PARISH
                    13: 'usertype',    # USERTYPE
                    14: 'oseast1m',    # OSEAST1M
                    15: 'osnrth1m',    # OSNRTH1M
                    16: 'osgrdind',    # OSGRDIND
                    17: 'oshlthau',    # OSHLTHAU
                    18: 'nhser',       # NHSER
                    19: 'ctry',        # CTRY
                    20: 'rgn',         # RGN
                    21: 'streg',       # STREG
                    22: 'pcon',        # PCON
                    23: 'eer',         # EER
                    24: 'teclec',      # TECLEC
                    25: 'ttwa',        # TTWA
                    26: 'pct',         # PCT
                    27: 'itl',         # ITL
                    28: 'statward',    # STATSWARD
                    29: 'oa01',        # OA01
                    30: 'casward',     # CASWARD
                    31: 'npark',       # NPARK
                    32: 'lsoa01',      # LSOA01
                    33: 'msoa01',      # MSOA01
                    34: 'ur01ind',     # UR01IND
                    35: 'oac01',       # OAC01
                    36: 'oa11',        # OA11
                    37: 'lsoa11',      # LSOA11
                    38: 'msoa11',      # MSOA11
                    39: 'wz11',        # WZ11
                    40: 'sicbl',       # SICBL
                    41: 'bua24',       # BUA24
                    42: 'ru11ind',     # RU11IND
                    43: 'oac11',       # OAC11
                    44: 'lat',         # LAT
                    45: 'long',        # LONG
                    46: 'lep1',        # LEP1
                    47: 'lep2',        # LEP2
                    48: 'pfa',         # PFA
                    49: 'imd',         # IMD
                    50: 'calncv',      # CALNCV
                    51: 'icb',         # ICB
                    52: 'oa21',        # OA21
                    53: 'lsoa21',      # LSOA21
                    54: 'msoa21',      # MSOA21
                    55: 'ruc21ind',    # RUC21IND
                    56: 'globalid'     # GlobalID
                }
                
                columns = ['x_coord', 'y_coord', 'objectid', 'pcd', 'pcd2', 'pcds', 'dointr', 'doterm', 'oscty', 'ced',
                          'oslaua', 'osward', 'parish', 'usertype', 'oseast1m', 'osnrth1m', 'osgrdind', 'oshlthau', 'nhser', 'ctry',
                          'rgn', 'streg', 'pcon', 'eer', 'teclec', 'ttwa', 'pct', 'itl', 'statward', 'oa01',
                          'casward', 'npark', 'lsoa01', 'msoa01', 'ur01ind', 'oac01', 'oa11', 'lsoa11', 'msoa11', 'wz11',
                          'sicbl', 'bua24', 'ru11ind', 'oac11', 'lat', 'long', 'lep1', 'lep2', 'pfa', 'imd',
                          'calncv', 'icb', 'oa21', 'lsoa21', 'msoa21', 'ruc21ind', 'globalid']
                metadata_columns = [
                    'source_name', 'upload_user', 'upload_timestamp',
                    'batch_id', 'source_file', 'file_size', 'file_modified', 'session_id', 'client_name'
                ]
                
                row_counter = 0
                total_rows = 0
                
                # Count total rows for progress bar
                for csv_file in csv_files:
                    with open(csv_file, 'r', encoding=encoding) as f:
                        total_rows += sum(1 for _ in csv.reader(f)) - 1  # Subtract 1 for header
                
                # Adjust total rows if max_rows is specified
                if max_rows is not None:
                    total_rows = min(total_rows, max_rows)
                    logger.info(f"📊 Total rows to process: {total_rows:,} (limited by --max-rows {max_rows:,})")
                else:
                    logger.info(f"📊 Total rows to process: {total_rows:,}")
                
                # Use server-side COPY if available and enabled
                if server_copy and len(csv_files) == 1:
                    success = server_side_copy(cur, csv_files[0], columns, metadata_columns, 
                                             batch_id, session_id, source_name, client_name, 
                                             encoding, total_rows)
                    if success:
                        # Count inserted rows
                        cur.execute("""
                            SELECT COUNT(*) FROM onspd_staging 
                            WHERE batch_id = %s AND session_id = %s
                        """, (batch_id, session_id))
                        rowcount_result = cur.fetchone()
                        rowcount = rowcount_result[0] if rowcount_result else 0
                        logger.info(f"✅ Successfully loaded {rowcount:,} rows")
                        return True, rowcount
                
                # Try client-side COPY for chunked processing of large files
                if len(csv_files) == 1:
                    file_size = os.path.getsize(csv_files[0])
                    if file_size > 1024 * 1024:  # Files larger than 1MB
                        logger.info("📤 Using client-side COPY with chunked processing (large file)")
                        success, rowcount = client_side_copy_chunked(cur, csv_files[0], columns, metadata_columns,
                                                                   batch_id, session_id, source_name, client_name, encoding)
                        if success:
                            logger.info(f"✅ Successfully loaded {rowcount:,} rows using client-side COPY")
                            return True, rowcount
                        else:
                            logger.warning("⚠️ Client-side COPY failed, falling back to chunked INSERT")
                    else:
                        # Small files can use the original client-side COPY
                        logger.info("📤 Using client-side COPY with STDIN (small file)")
                        success, rowcount = client_side_copy_chunked(cur, csv_files[0], columns, metadata_columns,
                                                                   batch_id, session_id, source_name, client_name, encoding, chunk_size=1000)
                        if success:
                            logger.info(f"✅ Successfully loaded {rowcount:,} rows using client-side COPY")
                            return True, rowcount
                        else:
                            logger.warning("⚠️ Client-side COPY failed, falling back to chunked INSERT")
                
                # Fallback to client-side chunked inserts
                logger.info("📤 Using client-side chunked INSERT")
                chunk_size = 10000  # Increased chunk size for better performance
                with tqdm(total=total_rows, desc="Processing ONSPD files") as pbar:
                    for csv_file in csv_files:
                        file_size = os.path.getsize(csv_file)
                        file_modified = datetime.fromtimestamp(os.path.getmtime(csv_file))
                        file_name = os.path.basename(csv_file)
                        
                        with open(csv_file, 'r', encoding=encoding) as f:
                            reader = csv.reader(f)
                            
                            # Skip header row
                            next(reader, None)
                            
                            chunk_data = []
                            for row in reader:
                                # Map CSV columns to our staging table columns using the mapping
                                mapped_row = []
                                for col_name in columns:
                                    # Find the CSV column index for this staging column
                                    csv_index = None
                                    for idx, mapped_col in column_mapping.items():
                                        if mapped_col == col_name:
                                            csv_index = idx
                                            break
                                    
                                    if csv_index is not None and csv_index < len(row):
                                        mapped_row.append(row[csv_index])
                                    else:
                                        mapped_row.append('')  # Default empty value
                                
                                # Add metadata
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
                                
                                # Combine data and metadata
                                full_row = mapped_row + metadata_row
                                chunk_data.append(full_row)
                                
                                # Insert chunk when it reaches the size limit
                                if len(chunk_data) >= chunk_size:
                                    insert_chunk_fast(cur, chunk_data, columns + metadata_columns)
                                    row_counter += len(chunk_data)
                                    pbar.update(len(chunk_data))
                                    chunk_data = []
                                
                                # Check if we've reached max_rows limit
                                if max_rows is not None and row_counter >= max_rows:
                                    logger.info(f"Reached max_rows={max_rows:,}, stopping early for testing.")
                                    break

                            
                            # Insert remaining data in the last chunk
                            if chunk_data:
                                insert_chunk_fast(cur, chunk_data, columns + metadata_columns)
                                row_counter += len(chunk_data)
                                pbar.update(len(chunk_data))
                            

                
                conn.commit()
                
                # Verify the inserted data
                cur.execute("""
                    SELECT COUNT(*) FROM onspd_staging 
                    WHERE batch_id = %s AND session_id = %s
                """, (batch_id, session_id))
                rowcount_result = cur.fetchone()
                rowcount = rowcount_result[0] if rowcount_result else 0
                logger.info(f"✅ Successfully loaded {rowcount:,} rows")
                return True, rowcount
    except Exception as e:
        logger.error(f"❌ Error during staging ingestion: {e}")
        return False, 0

def insert_chunk(cur, chunk_data, columns):
    """Insert a chunk of data using executemany"""
    placeholders = ', '.join(['%s'] * len(columns))
    insert_sql = f"""
        INSERT INTO onspd_staging (
            {', '.join(columns)}
        ) VALUES ({placeholders})
    """
    cur.executemany(insert_sql, chunk_data)

def insert_chunk_fast(cur, chunk_data, columns):
    """Optimized bulk insert using VALUES clause"""
    if not chunk_data:
        return
    
    # Create VALUES clause with all rows
    placeholders = ', '.join(['%s'] * len(columns))
    values_clauses = []
    all_values = []
    
    for row in chunk_data:
        values_clauses.append(f"({placeholders})")
        all_values.extend(row)
    
    insert_sql = f"""
        INSERT INTO onspd_staging (
            {', '.join(columns)}
        ) VALUES {', '.join(values_clauses)}
    """
    
    cur.execute(insert_sql, all_values)

def verify_staging_data(batch_id=None, session_id=None):
    """Verify the loaded staging data quality"""
    logger.info("Verifying ONSPD staging data quality...")
    
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
                cur.execute(f"SELECT COUNT(*) FROM onspd_staging {where_clause};", params)
                total_count_result = cur.fetchone()
                total_count = total_count_result[0] if total_count_result else 0
                
                # Check for empty postcodes
                cur.execute(f"SELECT COUNT(*) FROM onspd_staging {where_clause} AND (pcds IS NULL OR pcds = '');", params)
                null_postcode_result = cur.fetchone()
                null_postcode_count = null_postcode_result[0] if null_postcode_result else 0
                
                # Check for empty postcodes (using pcds instead of raw_line)
                cur.execute(f"SELECT COUNT(*) FROM onspd_staging {where_clause} AND (pcds IS NULL OR pcds = '');", params)
                empty_result = cur.fetchone()
                empty_count = empty_result[0] if empty_result else 0
                
                logger.info("=" * 60)
                logger.info("ONSPD STAGING DATA QUALITY REPORT")
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

def server_side_copy(cur, csv_file, columns, metadata_columns, batch_id, session_id, source_name, client_name, encoding, total_rows):
    """Use server-side COPY for maximum performance"""
    try:
        import tempfile
        import shutil
        
        # Create a temporary file with metadata columns added
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding=encoding)
        
        file_size = os.path.getsize(csv_file)
        file_modified = datetime.fromtimestamp(os.path.getmtime(csv_file))
        file_name = os.path.basename(csv_file)
        
        with open(csv_file, 'r', encoding=encoding) as source_file:
            reader = csv.reader(source_file)
            writer = csv.writer(temp_file)
            
            # Write header with metadata columns
            header = columns + metadata_columns
            writer.writerow(header)
            
            # Process data rows with progress bar
            with tqdm(total=total_rows, desc="Preparing data for server-side COPY") as pbar:
                for row in reader:
                    # Map CSV columns to our staging table columns using the mapping
                    mapped_row = []
                    for col_name in columns:
                        # Find the CSV column index for this staging column
                        csv_index = None
                        for idx, mapped_col in column_mapping.items():
                            if mapped_col == col_name:
                                csv_index = idx
                                break
                        
                        if csv_index is not None and csv_index < len(row):
                            mapped_row.append(row[csv_index])
                        else:
                            mapped_row.append('')  # Default empty value
                    
                    # Add metadata
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
                    
                    # Write row with metadata
                    writer.writerow(mapped_row + metadata_row)
                    pbar.update(1)
        
        temp_file.close()
        
        # Use server-side COPY from the temporary file
        copy_sql = f"""
            COPY onspd_staging (
                {', '.join(columns + metadata_columns)}
            ) FROM '{temp_file.name}' WITH (FORMAT CSV, HEADER TRUE, ENCODING '{encoding}')
        """
        
        cur.execute(copy_sql)
        
        # Clean up temporary file
        os.unlink(temp_file.name)
        
        return True
        
    except Exception as e:
        logger.error(f"Server-side COPY failed: {e}")
        # Clean up temp file if it exists
        if 'temp_file' in locals():
            try:
                os.unlink(temp_file.name)
            except:
                pass
        return False

def client_side_copy_chunked(cur, csv_file, columns, metadata_columns, batch_id, session_id, source_name, client_name, encoding, chunk_size=10000):
    """Use client-side COPY with STDIN for chunked processing of large files"""
    try:
        import csv
        from io import StringIO
        from tqdm import tqdm
        
        file_size = os.path.getsize(csv_file)
        file_modified = datetime.fromtimestamp(os.path.getmtime(csv_file))
        file_name = os.path.basename(csv_file)
        
        # Define the mapping from CSV column index to our staging table columns
        column_mapping = {
            0: 'x_coord', 1: 'y_coord', 2: 'objectid', 3: 'pcd', 4: 'pcd2', 5: 'pcds', 6: 'dointr', 7: 'doterm',
            8: 'oscty', 9: 'ced', 10: 'oslaua', 11: 'osward', 12: 'parish', 13: 'usertype', 14: 'oseast1m', 15: 'osnrth1m',
            16: 'osgrdind', 17: 'oshlthau', 18: 'nhser', 19: 'ctry', 20: 'rgn', 21: 'streg', 22: 'pcon', 23: 'eer',
            24: 'teclec', 25: 'ttwa', 26: 'pct', 27: 'itl', 28: 'statward', 29: 'oa01', 30: 'casward', 31: 'npark',
            32: 'lsoa01', 33: 'msoa01', 34: 'ur01ind', 35: 'oac01', 36: 'oa11', 37: 'lsoa11', 38: 'msoa11', 39: 'wz11',
            40: 'sicbl', 41: 'bua24', 42: 'ru11ind', 43: 'oac11', 44: 'lat', 45: 'long', 46: 'lep1', 47: 'lep2',
            48: 'pfa', 49: 'imd', 50: 'calncv', 51: 'icb', 52: 'oa21', 53: 'lsoa21', 54: 'msoa21', 55: 'ruc21ind', 56: 'globalid'
        }
        
        # First pass: count total rows for progress bar
        with open(csv_file, 'r', encoding=encoding) as f:
            total_rows = sum(1 for _ in csv.reader(f)) - 1  # Subtract 1 for header
        
        logger.info(f"📤 Using client-side COPY with chunked processing ({chunk_size:,} rows per chunk)")
        
        with open(csv_file, 'r', encoding=encoding) as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            
            chunk_data = []
            total_processed = 0
            
            with tqdm(total=total_rows, desc="Processing with client-side COPY") as pbar:
                for row in reader:
                    # Map CSV columns to our staging table columns
                    mapped_row = []
                    for col_name in columns:
                        csv_index = None
                        for idx, mapped_col in column_mapping.items():
                            if mapped_col == col_name:
                                csv_index = idx
                                break
                        
                        if csv_index is not None and csv_index < len(row):
                            mapped_row.append(row[csv_index])
                        else:
                            mapped_row.append('')
                    
                    # Add metadata
                    metadata_row = [
                        source_name, USER, datetime.now().isoformat(), batch_id, file_name,
                        str(file_size), file_modified.isoformat(), session_id, client_name
                    ]
                    
                    chunk_data.append(mapped_row + metadata_row)
                    
                    # Process chunk when it reaches the size limit
                    if len(chunk_data) >= chunk_size:
                        # Use client-side COPY with STDIN for this chunk
                        copy_data = StringIO()
                        writer = csv.writer(copy_data)
                        for chunk_row in chunk_data:
                            writer.writerow(chunk_row)
                        
                        copy_data.seek(0)
                        
                        # Execute COPY FROM STDIN
                        copy_sql = f"""
                            COPY onspd_staging (
                                {', '.join(columns + metadata_columns)}
                            ) FROM STDIN WITH (FORMAT CSV)
                        """
                        
                        cur.copy_expert(copy_sql, copy_data)
                        total_processed += len(chunk_data)
                        pbar.update(len(chunk_data))
                        chunk_data = []
                
                # Process remaining data
                if chunk_data:
                    copy_data = StringIO()
                    writer = csv.writer(copy_data)
                    for chunk_row in chunk_data:
                        writer.writerow(chunk_row)
                    
                    copy_data.seek(0)
                    
                    copy_sql = f"""
                        COPY onspd_staging (
                            {', '.join(columns + metadata_columns)}
                        ) FROM STDIN WITH (FORMAT CSV)
                    """
                    
                    cur.copy_expert(copy_sql, copy_data)
                    total_processed += len(chunk_data)
                    pbar.update(len(chunk_data))
        
        return True, total_processed
        
    except Exception as e:
        logger.error(f"Client-side COPY failed: {e}")
        return False, 0

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
    source_name = args.source or "ONSPD_DEFAULT"
    client_name = args.client or "default_client"
    
    # Log encoding information
    logger.info(f"Using encoding: {args.encoding}")
    if args.server_copy:
        logger.info("Using server-side COPY (PostgreSQL server must have access to files)")
    else:
        logger.info("Using client-side COPY (works with Docker and remote databases)")
    
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
    logger.info("ONSPD STAGING-ONLY INGESTION")
    logger.info("=" * 60)
    logger.info(f"CSV files: {csv_files}")
    logger.info(f"Staging table: onspd_staging")
    logger.info(f"Source: {source_name}")
    logger.info(f"Client: {client_name}")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Batch ID: {batch_id}")
    logger.info("=" * 60)
    
    try:
        # Step 1: Check if staging table exists
        if not check_staging_table_exists():
            sys.exit(1)

        # Step 2: Load data into staging table
        success, rowcount = load_onspd_to_staging(
            csv_files, batch_id, session_id, source_name, client_name, 
            max_rows=args.max_rows, encoding=args.encoding, server_copy=args.server_copy
        )
        
        if success:
            # Verify staging data quality
            verify_staging_data(batch_id, session_id)
            logger.info("✅ ONSPD staging ingestion completed successfully!")
            logger.info(f"📊 Data loaded into staging table with batch_id: {batch_id}")
        else:
            logger.error("❌ Data loading failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 