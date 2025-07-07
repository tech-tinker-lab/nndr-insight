#!/usr/bin/env python3
"""
OS Open USRN Staging-Only Ingestion Script
Loads OS Open USRN GPKG data into staging table only with client and source tracking
"""

import sys
import os
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv
import geopandas as gpd
from sqlalchemy import create_engine
from sqlalchemy import text

# Load .env file from db_setup directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'db_setup', '.env'))

USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")
STAGING_TABLE = "os_open_usrn_staging"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description='OS Open USRN Staging-Only Ingestion')
    parser.add_argument('--source-file', default="data/osopenusrn_202507_gpkg/osopenusrn_202507.gpkg", help='Path to source file (GeoPackage)')
    parser.add_argument('--layer', default="openUSRN", help='Layer name in GeoPackage')
    parser.add_argument('--client', help='Client identifier (e.g., "client_001", "internal_team")')
    parser.add_argument('--source', help='Source identifier (e.g., "OS_Open_USRN_2024")')
    parser.add_argument('--session-id', help='Session identifier for concurrent ingestion (auto-generated if not provided)')
    parser.add_argument('--batch-id', help='Batch identifier (auto-generated if not provided)')
    parser.add_argument('--dbname', help='Override database name from environment')
    return parser.parse_args()

def generate_identifiers(args):
    batch_id = args.batch_id or f"os_open_usrn_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    session_id = args.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return batch_id, session_id

def main():
    args = parse_arguments()
    dbname = args.dbname or DBNAME
    batch_id, session_id = generate_identifiers(args)
    source_name = args.source or "OS_Open_USRN_DEFAULT"
    client_name = args.client or "default_client"
    source_file = args.source_file
    layer_name = args.layer

    logger.info("=" * 60)
    logger.info("OS OPEN USRN STAGING-ONLY INGESTION")
    logger.info("=" * 60)
    logger.info(f"Source file: {source_file}")
    logger.info(f"Layer: {layer_name}")
    logger.info(f"Staging table: {STAGING_TABLE}")
    logger.info(f"Source: {source_name}")
    logger.info(f"Client: {client_name}")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Batch ID: {batch_id}")
    logger.info("=" * 60)

    if not os.path.isfile(source_file):
        logger.error(f"Source file not found: {source_file}")
        sys.exit(1)

    try:
        # Read GPKG with invalid geometry handling
        gdf = gpd.read_file(source_file, layer=layer_name, on_invalid='ignore')
        logger.info(f"Loaded {len(gdf)} features from layer '{layer_name}' (invalid geometries ignored)")
        
        if len(gdf) == 0:
            logger.warning("No valid features found in the file")
            return

        # Add audit columns
        gdf['source_name'] = source_name
        gdf['upload_user'] = USER
        gdf['upload_timestamp'] = datetime.now().isoformat()
        gdf['batch_id'] = batch_id
        gdf['raw_filename'] = os.path.basename(source_file)
        gdf['file_path'] = source_file
        gdf['file_size'] = os.path.getsize(source_file)
        gdf['file_modified'] = datetime.fromtimestamp(os.path.getmtime(source_file)).isoformat()
        gdf['session_id'] = session_id
        gdf['client_name'] = client_name

        # Write to staging table
        engine = create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{dbname}")
        gdf.to_postgis(name=STAGING_TABLE, con=engine, if_exists='append', index=False)
        logger.info(f"✅ Successfully loaded {len(gdf)} rows into '{STAGING_TABLE}' with batch_id {batch_id}")

        # Quality check
        with engine.begin() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {STAGING_TABLE} WHERE batch_id = :batch_id AND session_id = :session_id"), {"batch_id": batch_id, "session_id": session_id})
            if hasattr(result, 'scalar'):
                rowcount = result.scalar()
            else:
                row_result = result.fetchone()
                rowcount = row_result[0] if row_result else 0
            if rowcount is None:
                rowcount = 0
            logger.info(f"📊 Staging table count for this batch/session: {rowcount} features")

    except Exception as e:
        logger.exception(f"Failed to ingest source file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
