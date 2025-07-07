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
from sqlalchemy import text, create_engine
from shapely.geometry import shape
from shapely.wkb import dumps as wkb_dumps
from dotenv import load_dotenv
import argparse
from datetime import datetime

# Load .env file from db_setup directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'db_setup', '.env'))

USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")
STAGING_TABLE = "os_open_map_local_staging"
BATCH_SIZE = 1000
GML_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'data', 'opmplc_gml3_gb', 'data')

def parse_arguments():
    parser = argparse.ArgumentParser(description='OS Open Map Local Staging-Only Ingestion')
    parser.add_argument('--client', help='Client identifier (e.g., "client_001", "internal_team")')
    parser.add_argument('--source', help='Source identifier (e.g., "OS_Open_Map_Local_2024")')
    parser.add_argument('--session-id', help='Session identifier for concurrent ingestion (auto-generated if not provided)')
    parser.add_argument('--batch-id', help='Batch identifier (auto-generated if not provided)')
    parser.add_argument('--dbname', help='Override database name from environment')
    return parser.parse_args()

def generate_identifiers(args):
    batch_id = args.batch_id or f"os_open_map_local_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    session_id = args.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return batch_id, session_id

def collect_gml_files():
    return glob.glob(os.path.join(GML_ROOT, "**", "*.gml"), recursive=True)

def process_gml_file(filepath, source_name, client_name, batch_id, session_id):
    records = []
    file_size = os.path.getsize(filepath)
    file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
    file_name = os.path.basename(filepath)
    try:
        with fiona.open(filepath, driver="GML") as src:
            for feature in src:
                try:
                    geom = shape(feature["geometry"])
                    props = feature["properties"]
                    records.append({
                        "fid": feature.get("id"),
                        "theme": props.get("theme"),
                        "make": props.get("make"),
                        "physicalpresence": props.get("physicalpresence"),
                        "descriptivegroup": props.get("descriptivegroup"),
                        "descriptiveterm": props.get("descriptiveterm"),
                        "fclass": props.get("fclass"),
                        "geometry": wkb_dumps(geom, hex=True),
                        "raw_line": str(props),
                        "source_name": source_name,
                        "upload_user": USER,
                        "upload_timestamp": datetime.now().isoformat(),
                        "batch_id": batch_id,
                        "raw_filename": file_name,
                        "file_path": filepath,
                        "file_size": str(file_size),
                        "file_modified": file_modified.isoformat(),
                        "session_id": session_id,
                        "client_name": client_name
                    })
                except Exception as e:
                    print(f"⚠️ Skipping feature in {os.path.basename(filepath)}: {e}")
    except Exception as e:
        print(f"❌ Error reading {os.path.basename(filepath)}: {e}")
    return records

def bulk_insert(engine, records):
    if not records:
        return 0
    stmt = text(f"""
        INSERT INTO {STAGING_TABLE} (
            fid, theme, make, physicalpresence, descriptivegroup,
            descriptiveterm, fclass, geometry, raw_line, source_name, upload_user, upload_timestamp,
            batch_id, raw_filename, file_path, file_size, file_modified, session_id, client_name
        ) VALUES (
            :fid, :theme, :make, :physicalpresence, :descriptivegroup,
            :descriptiveterm, :fclass,
            ST_GeomFromWKB(decode(:geometry, 'hex'), 27700),
            :raw_line, :source_name, :upload_user, :upload_timestamp,
            :batch_id, :raw_filename, :file_path, :file_size, :file_modified, :session_id, :client_name
        )
    """)
    with engine.begin() as conn:
        for i in range(0, len(records), BATCH_SIZE):
            batch = records[i:i+BATCH_SIZE]
            conn.execute(stmt, batch)
    return len(records)

def main():
    args = parse_arguments()
    if args.dbname:
        global DBNAME
        DBNAME = args.dbname
    batch_id, session_id = generate_identifiers(args)
    source_name = args.source or "OS_Open_Map_Local_DEFAULT"
    client_name = args.client or "default_client"
    print("🗺️ Starting OS Open Map Local Staging-Only Ingestion")
    print(f"Database: {DBNAME} on {HOST}:{PORT}")
    print(f"GML Root: {GML_ROOT}")
    print(f"Batch ID: {batch_id}")
    print(f"Session ID: {session_id}")
    print(f"Source: {source_name}")
    print(f"Client: {client_name}")
    engine = create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}")
    files = collect_gml_files()
    print(f"📂 Found {len(files)} GML files under {GML_ROOT}")
    if not files:
        print("❌ No GML files found!")
        return
    total_features = 0
    processed_files = 0
    start_time = time.time()
    for fpath in files:
        try:
            print(f"Processing {os.path.basename(fpath)}...")
            records = process_gml_file(fpath, source_name, client_name, batch_id, session_id)
            inserted = bulk_insert(engine, records)
            total_features += inserted
            processed_files += 1
            if processed_files % 10 == 0:
                print(f"  ✅ Processed {processed_files}/{len(files)} files, {total_features} features so far")
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(fpath)}: {e}")
    elapsed = time.time() - start_time
    print(f"\n✅ Done. Inserted {total_features} features from {processed_files} files in {elapsed:.1f} seconds.")
    # Quality check
    with engine.begin() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {STAGING_TABLE} WHERE batch_id = :batch_id AND session_id = :session_id"), {"batch_id": batch_id, "session_id": session_id})
        final_count = result.scalar()
        print(f"📊 Final staging table count for this batch/session: {final_count} features")

if __name__ == "__main__":
    main() 