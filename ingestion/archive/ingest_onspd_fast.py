#!/usr/bin/env python3
"""
Fast ONSPD Data Ingestion Script (Staging Only, Concurrency-Safe)
Loads data into onspd_staging with batch/client/session tagging and audit columns.
No DROP/TRUNCATE/CREATE on final tables. No upsert. Follows standardized ingestion pattern.
"""

import psycopg2
import os
import sys
import logging
import argparse
from dotenv import load_dotenv
from datetime import datetime

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_connection():
    return psycopg2.connect(
        dbname=DBNAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )

def parse_args():
    parser = argparse.ArgumentParser(description="Fast, concurrency-safe ONSPD ingestion (staging only)")
    parser.add_argument('--csv', type=str, required=False, default="../../backend/data/ONSPD_Online_Latest_Centroids.csv", help='Path to input CSV')
    parser.add_argument('--client', type=str, required=True, help='Client name or ID')
    parser.add_argument('--batch-id', type=str, required=True, help='Batch ID for this ingestion')
    parser.add_argument('--session-id', type=str, required=False, default=None, help='Session ID (optional)')
    parser.add_argument('--source', type=str, required=False, default=None, help='Source system (optional)')
    parser.add_argument('--source-file', type=str, required=False, default=None, help='Source file name (optional)')
    return parser.parse_args()

def load_onspd_data_staging(csv_path, client, batch_id, session_id, source, source_file):
    if not os.path.isfile(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        return False
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                logger.info(f"Bulk loading {csv_path} into onspd_staging with batch/client tagging...")
                # Preview first two lines
                with open(csv_path, 'r', encoding='utf-8') as f:
                    header = f.readline().strip()
                    first_data = f.readline().strip()
                    logger.info(f'Header: {header}')
                    logger.info(f'First data row: {first_data}')
                # Prepare COPY with extra columns for audit
                with open(csv_path, 'r', encoding='utf-8') as f:
                    import csv, tempfile
                    temp = tempfile.NamedTemporaryFile('w+', newline='', delete=False)
                    writer = csv.writer(temp)
                    reader = csv.reader(f)
                    header_row = next(reader)
                    writer.writerow(header_row + ['batch_id', 'client_name', 'session_id', 'source', 'source_file', 'loaded_at'])
                    for row in reader:
                        writer.writerow(row + [batch_id, client, session_id or '', source or '', source_file or os.path.basename(csv_path), datetime.utcnow().isoformat()])
                    temp.flush()
                    temp.seek(0)
                    copy_sql = f"""
                        COPY onspd_staging (x, y, objectid, pcd, pcd2, pcds, dointr, doterm, oscty, ced, oslaua, osward, parish, usertype, oseast1m, osnrth1m, osgrdind, oshlthau, nhser, ctry, rgn, streg, pcon, eer, teclec, ttwa, pct, itl, statsward, oa01, casward, npark, lsoa01, msoa01, ur01ind, oac01, oa11, lsoa11, msoa11, wz11, sicbl, bua24, ru11ind, oac11, lat, long, lep1, lep2, pfa, imd, calncv, icb, oa21, lsoa21, msoa21, ruc21ind, globalid, batch_id, client_name, session_id, source, source_file, loaded_at)
                        FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
                    """
                    with open(temp.name, 'r', encoding='utf-8') as tf:
                        cur.copy_expert(sql=copy_sql, file=tf)
                    os.unlink(temp.name)
                    conn.commit()
                # Get record count
                cur.execute("SELECT COUNT(*) FROM onspd_staging WHERE batch_id = %s AND client_name = %s;", (batch_id, client))
                row = cur.fetchone()
                rowcount = row[0] if row else 0
                logger.info(f"Successfully loaded {rowcount} records into onspd_staging for batch {batch_id}, client {client}")
                return True
    except Exception as e:
        logger.error(f"Error during data load: {e}")
        return False

def verify_data_quality(batch_id, client):
    logger.info("Verifying data quality for this batch...")
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM onspd_staging WHERE batch_id = %s AND client_name = %s;", (batch_id, client))
                row = cur.fetchone()
                total_count = row[0] if row else 0
                cur.execute("SELECT COUNT(*) FROM onspd_staging WHERE batch_id = %s AND client_name = %s AND pcds IS NULL;", (batch_id, client))
                row = cur.fetchone()
                null_postcode_count = row[0] if row else 0
                cur.execute("""
                    SELECT COUNT(*) FROM (
                        SELECT pcds, COUNT(*) FROM onspd_staging WHERE batch_id = %s AND client_name = %s GROUP BY pcds HAVING COUNT(*) > 1
                    ) as duplicates;
                """, (batch_id, client))
                row = cur.fetchone()
                duplicate_count = row[0] if row else 0
                cur.execute("""
                    SELECT MIN(lat), MAX(lat), MIN(long), MAX(long)
                    FROM onspd_staging WHERE batch_id = %s AND client_name = %s;
                """, (batch_id, client))
                coord_ranges = cur.fetchone()
                logger.info("=" * 60)
                logger.info("DATA QUALITY REPORT (staging, this batch)")
                logger.info("=" * 60)
                logger.info(f"Total records: {total_count:,}")
                logger.info(f"Null postcodes: {null_postcode_count}")
                logger.info(f"Duplicate postcodes: {duplicate_count}")
                if coord_ranges and all(x is not None for x in coord_ranges):
                    logger.info(f"Latitude range: {coord_ranges[0]} to {coord_ranges[1]}")
                    logger.info(f"Longitude range: {coord_ranges[2]} to {coord_ranges[3]}")
                else:
                    logger.info("Coordinate ranges: N/A (no data)")
                logger.info("=" * 60)
                return True
    except Exception as e:
        logger.error(f"Error during data quality verification: {e}")
        return False

def main():
    args = parse_args()
    logger.info("=" * 60)
    logger.info("FAST ONSPD DATA INGESTION (STAGING ONLY)")
    logger.info("=" * 60)
    logger.info(f"CSV file: {args.csv}")
    logger.info(f"Client: {args.client}")
    logger.info(f"Batch ID: {args.batch_id}")
    logger.info(f"Session ID: {args.session_id}")
    logger.info(f"Source: {args.source}")
    logger.info(f"Source file: {args.source_file}")
    logger.info("=" * 60)
    if load_onspd_data_staging(args.csv, args.client, args.batch_id, args.session_id, args.source, args.source_file):
        verify_data_quality(args.batch_id, args.client)
        logger.info("✅ ONSPD data ingestion (staging) completed successfully!")
    else:
        logger.error("❌ Data loading failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 