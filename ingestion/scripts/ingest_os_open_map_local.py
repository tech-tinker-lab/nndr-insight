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
    parser.add_argument('--data-dir', required=True, help='Directory containing GML files (e.g., "data/opmplc_gml3_gb/data")')
    parser.add_argument('--source', help='Source identifier (e.g., "OS_Open_Map_Local_2024")')
    parser.add_argument('--session-id', help='Session identifier for concurrent ingestion (auto-generated if not provided)')
    parser.add_argument('--batch-id', help='Batch identifier (auto-generated if not provided)')
    parser.add_argument('--dbname', help='Override database name from environment')
    return parser.parse_args()

def generate_identifiers(args):
    batch_id = args.batch_id or f"os_open_map_local_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    session_id = args.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return batch_id, session_id

def collect_gml_files(data_dir):
    return glob.glob(os.path.join(data_dir, "**", "*.gml"), recursive=True)

def process_gml_file(filepath, source_name, batch_id):
    """Process a single GML file and extract features"""
    logger.info(f"Processing {os.path.basename(filepath)}...")
    file_start = time.time()
    
    records = []
    file_name = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)
    file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
    
    # Check if file is empty
    if file_size == 0:
        logger.warning(f"⚠️ Skipping empty file: {os.path.basename(filepath)} (0 bytes)")
        return []
    
    try:
        with fiona.open(filepath, driver="GML") as src:
            feature_count = 0
            for feature in src:
                try:
                    geom = shape(feature["geometry"])
                    props = feature["properties"]
                    records.append({
                        "id": str(uuid.uuid4()),
                        "fid": feature.get("id"),
                        "gml_id": props.get("gml_id"),
                        "feature_code": props.get("feature_code"),
                        "geometry": wkb_dumps(geom, hex=True),
                        "feature_type": props.get("feature_type"),
                        "properties": str(props),
                        "source_name": source_name,
                        "upload_user": USER,
                        "upload_timestamp": datetime.now().isoformat(),
                        "batch_id": batch_id,
                        "source_file": file_name
                    })
                    feature_count += 1
                except Exception as e:
                    logger.warning(f"⚠️ Skipping feature in {os.path.basename(filepath)}: {e}")
            
            file_time = time.time() - file_start
            logger.info(f"  Extracted {feature_count} features in {file_time:.1f}s")
            logger.info(f"  File size: {file_size:,} bytes")
            
            return records
            
    except Exception as e:
        logger.error(f"❌ Error reading {os.path.basename(filepath)}: {e}")
        return []

def bulk_insert(engine, records):
    """Bulk insert records into staging table"""
    if not records:
        return 0
    
    logger.info(f"Inserting {len(records):,} records into {STAGING_TABLE}...")
    insert_start = time.time()
    
    stmt = text(f"""
        INSERT INTO {STAGING_TABLE} (
            id, fid, gml_id, feature_code, geometry, feature_type, properties, source_name, upload_user, upload_timestamp, batch_id, source_file
        ) VALUES (
            :id, :fid, :gml_id, :feature_code, ST_GeomFromWKB(decode(:geometry, 'hex'), 27700), :feature_type, :properties, :source_name, :upload_user, :upload_timestamp, :batch_id, :source_file
        )
    """)
    
    try:
        with engine.begin() as conn:
            for i in range(0, len(records), BATCH_SIZE):
                batch = records[i:i+BATCH_SIZE]
                conn.execute(stmt, batch)
        
        insert_time = time.time() - insert_start
        logger.info(f"✅ Inserted {len(records):,} records in {insert_time:.1f}s")
        return len(records)
        
    except Exception as e:
        logger.error(f"❌ Error during bulk insert: {e}")
        return 0

def main():
    """Main execution function"""
    args = parse_arguments()
    if args.dbname:
        global DBNAME
        DBNAME = args.dbname
    batch_id, session_id = generate_identifiers(args)
    source_name = args.source or "OS_Open_Map_Local_DEFAULT"
    
    logger.info("=" * 60)
    logger.info("OS OPEN MAP LOCAL STAGING INGESTION")
    logger.info("=" * 60)
    logger.info(f"Database: {DBNAME} on {HOST}:{PORT}")
    logger.info(f"Data directory: {args.data_dir}")
    logger.info(f"Batch ID: {batch_id}")
    logger.info(f"Source: {source_name}")
    logger.info("=" * 60)
    
    try:
        engine = create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}")
        files = collect_gml_files(args.data_dir)
        logger.info(f"📂 Found {len(files)} GML files under {args.data_dir}")
        
        if not files:
            logger.error("❌ No GML files found!")
            return
        
        total_features = 0
        processed_files = 0
        empty_files = 0
        start_time = time.time()
        
        # Progress bar for files
        with tqdm(files, desc="Processing GML files", unit="file") as pbar:
            for fpath in pbar:
                pbar.set_description(f"Processing {os.path.basename(fpath)}")
                try:
                    # Check if file is empty before processing
                    if os.path.getsize(fpath) == 0:
                        empty_files += 1
                        logger.warning(f"⚠️ Skipping empty file: {os.path.basename(fpath)} (0 bytes)")
                        pbar.update(1)
                        continue
                    
                    records = process_gml_file(fpath, source_name, batch_id)
                    inserted = bulk_insert(engine, records)
                    total_features += inserted
                    processed_files += 1
                    pbar.set_postfix({
                        'Files': f"{processed_files}/{len(files)}",
                        'Features': f"{total_features:,}",
                        'Empty': empty_files
                    })
                except Exception as e:
                    logger.error(f"❌ Error processing {os.path.basename(fpath)}: {e}")
        
        elapsed = time.time() - start_time
        logger.info("=" * 60)
        logger.info("INGESTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Inserted {total_features:,} features from {processed_files} files")
        logger.info(f"⚠️  Skipped {empty_files} empty files")
        logger.info(f"📂 Total files found: {len(files)}")
        logger.info(f"⏱️  Total processing time: {elapsed:.1f} seconds")
        
        # Quality check
        with engine.begin() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {STAGING_TABLE} WHERE batch_id = :batch_id"), {"batch_id": batch_id})
            final_count = result.scalar()
            logger.info(f"📊 Final staging table count for this batch: {final_count:,} features")
        
        logger.info("✅ OS Open Map Local staging ingestion completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        raise

if __name__ == "__main__":
    main() 