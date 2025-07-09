#!/usr/bin/env python3
"""
OS Open Map Local Staging-Only Ingestion Script
Loads OS Open Map Local GML data into staging table only with client and source tracking
"""

import os
import glob
import time
import fiona
import sqlalchemy
import uuid
import logging
from sqlalchemy import text, create_engine
from shapely.geometry import shape
from shapely.wkb import dumps as wkb_dumps
from dotenv import load_dotenv
import argparse
from datetime import datetime
from tqdm import tqdm
import tempfile
import csv

# Load .env file from root directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Database configuration
USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

STAGING_TABLE = "os_open_map_local_staging"
BATCH_SIZE = 1000

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description='OS Open Map Local Staging-Only Ingestion')
    parser.add_argument('--source-path', required=True, help='Path to GML file or directory containing GML files (e.g., "data/opmplc_gml3_gb/data")')
    parser.add_argument('--max-rows', type=int, help='Maximum number of rows to process (for testing)')
    parser.add_argument('--source', help='Source identifier (e.g., "OS_Open_Map_Local_2024")')
    parser.add_argument('--session-id', help='Session identifier for concurrent ingestion (auto-generated if not provided)')
    parser.add_argument('--batch-id', help='Batch identifier (auto-generated if not provided)')
    parser.add_argument('--dbname', help='Override database name from environment')
    parser.add_argument('--client', help='Client identifier (e.g., "client_001")')
    return parser.parse_args()

def generate_identifiers(args):
    batch_id = args.batch_id or f"os_open_map_local_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    session_id = args.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return batch_id, session_id

def check_staging_table_exists():
    """Check if the staging table exists with correct schema"""
    logger.info("Checking if os_open_map_local_staging table exists with correct schema...")
    try:
        engine = create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}")
        with engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = '{STAGING_TABLE}'
                );
            """))
            exists = result.scalar()
            
            if not exists:
                logger.error(f"❌ Staging table '{STAGING_TABLE}' does not exist!")
                logger.error("Please run the database setup script to create the staging table.")
                return False
            
            # Check if geometry column is correct type
            result = conn.execute(text(f"""
                SELECT data_type, udt_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = '{STAGING_TABLE}' 
                AND column_name = 'geometry'
            """))
            geometry_info = result.fetchone()
            
            if not geometry_info or geometry_info[1] != 'geometry':
                logger.error(f"❌ Staging table '{STAGING_TABLE}' has wrong geometry column type!")
                logger.error("Expected: GEOMETRY(GEOMETRY, 27700)")
                logger.error(f"Found: {geometry_info[1] if geometry_info else 'TEXT'}")
                logger.error("Please run the database setup script to recreate the staging table.")
                return False
            
            logger.info("✅ Staging table exists with correct schema")
            return True
                
    except Exception as e:
        logger.error(f"Error checking staging table: {e}")
        return False

def collect_gml_files(source_path):
    if os.path.isdir(source_path):
        return glob.glob(os.path.join(source_path, "**", "*.gml"), recursive=True)
    elif os.path.isfile(source_path) and source_path.lower().endswith('.gml'):
        return [source_path]
    else:
        return []

def process_gml_file_to_csv(filepath, source_name, batch_id, session_id, client_name, writer, max_rows=None):
    """Process a single GML file and write features to CSV via writer"""
    logger.info(f"Processing {os.path.basename(filepath)}...")
    file_start = time.time()
    file_name = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)
    file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
    gfs_file = os.path.splitext(filepath)[0] + ".gfs"
    if not os.path.exists(gfs_file) or os.path.getsize(gfs_file) == 0:
        logger.warning(f"⚠️ Skipping {file_name} due to missing/invalid .gfs file: {gfs_file}")
        return 0
    if file_size == 0:
        logger.warning(f"⚠️ Skipping empty file: {file_name} (0 bytes)")
        return 0
    feature_count = 0
    try:
        with fiona.open(filepath, driver="GML") as src:
            for feature in src:
                try:
                    geom = shape(feature["geometry"])
                    props = feature["properties"]

                    
                    writer.writerow([
                        str(uuid.uuid4()),
                        feature.get("id"),
                        props.get("gml_id"),
                        props.get("featureCode"),  # Use correct property name
                        wkb_dumps(geom, hex=True),
                        props.get("feature_type"),
                        str(props),
                        source_name,
                        USER,
                        datetime.now().isoformat(),
                        batch_id,
                        file_name,
                        file_size,
                        file_modified.isoformat(),
                        session_id,
                        client_name
                    ])
                    feature_count += 1
                    
                    # Stop if max_rows reached
                    if max_rows is not None and feature_count >= max_rows:
                        logger.info(f"Reached max_rows={max_rows}, stopping early for testing.")
                        break
                        
                except Exception as e:
                    logger.warning(f"⚠️ Skipping feature in {file_name}: {e}")
        file_time = time.time() - file_start
        logger.info(f"  Extracted {feature_count} features in {file_time:.1f}s")
        logger.info(f"  File size: {file_size:,} bytes")
        return feature_count
    except Exception as e:
        logger.error(f"❌ Error reading {file_name}: {e}")
        return 0

def bulk_insert_from_csv(engine, csv_path):
    logger.info(f"Bulk inserting from temp CSV: {csv_path}")
    raw = engine.raw_connection()
    try:
        with raw.cursor() as cursor, open(csv_path, 'r', encoding='utf-8') as f:
            copy_sql = f'''
                COPY {STAGING_TABLE} (
                    id, fid, gml_id, feature_code, geometry, feature_type, properties, source_name, upload_user, upload_timestamp, batch_id, source_file, file_size, file_modified, session_id, client_name
                ) FROM STDIN WITH (FORMAT csv)
            '''
            cursor.copy_expert(copy_sql, f)
        raw.commit()
        logger.info("✅ Bulk insert from CSV completed.")
    except Exception as e:
        logger.error(f"❌ Error during COPY from CSV: {e}")
        raw.rollback()
    finally:
        raw.close()

def verify_staging_data(batch_id=None, session_id=None):
    """Verify the loaded staging data quality"""
    logger.info("Verifying OS Open Map Local staging data quality...")
    
    try:
        engine = create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}")
        with engine.connect() as conn:
            # Build WHERE clause for specific batch/session if provided
            where_clause = ""
            params = {}
            if batch_id and session_id:
                where_clause = "WHERE batch_id = :batch_id AND session_id = :session_id"
                params = {"batch_id": batch_id, "session_id": session_id}
            elif batch_id:
                where_clause = "WHERE batch_id = :batch_id"
                params = {"batch_id": batch_id}
            
            # Check total count
            result = conn.execute(text(f"SELECT COUNT(*) FROM {STAGING_TABLE} {where_clause}"), params)
            total_count = result.scalar()
            
            # Check for empty feature codes
            result = conn.execute(text(f"SELECT COUNT(*) FROM {STAGING_TABLE} {where_clause} AND (feature_code IS NULL OR feature_code = '')"), params)
            null_feature_code_count = result.scalar()
            
            # Check for empty geometries (PostGIS geometry column)
            result = conn.execute(text(f"SELECT COUNT(*) FROM {STAGING_TABLE} {where_clause} AND geometry IS NULL"), params)
            null_geometry_count = result.scalar()
            
            logger.info("=" * 60)
            logger.info("OS OPEN MAP LOCAL STAGING DATA QUALITY REPORT")
            logger.info("=" * 60)
            logger.info(f"Total records: {total_count:,}")
            logger.info(f"Null feature codes: {null_feature_code_count}")
            logger.info(f"Null geometries: {null_geometry_count}")
            logger.info(f"Valid records: {total_count - max(null_feature_code_count, null_geometry_count):,}")
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
    batch_id, session_id = generate_identifiers(args)
    source_name = args.source or "OS_Open_Map_Local_DEFAULT"
    client_name = args.client or "default_client"
    logger.info("=" * 60)
    logger.info("OS OPEN MAP LOCAL STAGING INGESTION (CSV AGGREGATION MODE)")
    logger.info("=" * 60)
    logger.info(f"Database: {DBNAME} on {HOST}:{PORT}")
    logger.info(f"Source path: {args.source_path}")
    logger.info(f"Batch ID: {batch_id}")
    logger.info(f"Source: {source_name}")
    logger.info("=" * 60)
    try:
        # Step 1: Check and fix staging table if needed
        if not check_staging_table_exists():
            return

        engine = create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}")
        files = collect_gml_files(args.source_path)
        logger.info(f"📂 Found {len(files)} GML files under {args.source_path}")
        if not files:
            logger.error("❌ No GML files found!")
            return
        # Improved file metadata logging
        if len(files) == 1:
            logger.info(f"File path: {files[0]}")
            logger.info(f"File size: {os.path.getsize(files[0])}")
            logger.info(f"File modified: {datetime.fromtimestamp(os.path.getmtime(files[0]))}")
        else:
            logger.info(f"Number of files: {len(files)}")
            logger.info(f"First file: {files[0]}")
            logger.info(f"First file size: {os.path.getsize(files[0])}")
            logger.info(f"First file modified: {datetime.fromtimestamp(os.path.getmtime(files[0]))}")
            total_size = sum(os.path.getsize(f) for f in files)
            logger.info(f"Total size of all files: {total_size}")
        total_features = 0
        processed_files = 0
        empty_files = 0
        skipped_gfs = 0
        start_time = time.time()
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, newline='', suffix='.csv') as tmpfile:
            writer = csv.writer(tmpfile)
            with tqdm(total=len(files), desc="Processing GML files", unit="file", leave=False) as pbar:
                for fpath in files:
                    features = process_gml_file_to_csv(fpath, source_name, batch_id, session_id, client_name, writer, args.max_rows)
                    if features == 0:
                        if not os.path.exists(os.path.splitext(fpath)[0] + ".gfs") or os.path.getsize(os.path.splitext(fpath)[0] + ".gfs") == 0:
                            skipped_gfs += 1
                        else:
                            empty_files += 1
                    else:
                        total_features += features
                        processed_files += 1
                    
                    # Stop if max_rows reached
                    if args.max_rows is not None and total_features >= args.max_rows:
                        pbar.close()
                        logger.info(f"Reached max_rows={args.max_rows}, stopping early for testing.")
                        break
                        
                    pbar.update(1)
                    pbar.set_postfix({
                        'Files': f"{processed_files}/{len(files)}",
                        'Features': f"{total_features:,}",
                        'Empty': empty_files,
                        'Skipped_gfs': skipped_gfs
                    })
            tmpfile.flush()
            logger.info(f"📝 Aggregated {total_features:,} features into temp file: {tmpfile.name}")
            bulk_insert_from_csv(engine, tmpfile.name)
        elapsed = time.time() - start_time
        logger.info("=" * 60)
        logger.info("INGESTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Inserted {total_features:,} features from {processed_files} files")
        logger.info(f"⚠️  Skipped {empty_files} empty files")
        logger.info(f"⚠️  Skipped {skipped_gfs} files due to missing/invalid .gfs")
        logger.info(f"📂 Total files found: {len(files)}")
        logger.info(f"⏱️  Total processing time: {elapsed:.1f} seconds")
        with engine.begin() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {STAGING_TABLE} WHERE batch_id = :batch_id"), {"batch_id": batch_id})
            final_count = result.scalar()
            logger.info(f"📊 Final staging table count for this batch: {final_count:,} features")
        
        # Verify staging data quality
        verify_staging_data(batch_id, session_id)
        logger.info("✅ OS Open Map Local staging ingestion completed successfully!")
        logger.info(f"📊 Data loaded into staging table with batch_id: {batch_id}")
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        raise

if __name__ == "__main__":
    main() 