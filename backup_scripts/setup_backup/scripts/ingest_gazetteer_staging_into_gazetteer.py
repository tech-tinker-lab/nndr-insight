import psycopg2
import logging
import os
import time
from dotenv import load_dotenv
import sys

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

# Setup logging format with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def insert_from_staging():
    start_time = time.time()
    try:
        with psycopg2.connect(
            dbname=DBNAME,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        ) as conn:
            with conn.cursor() as cur:
                # Count before insert
                cur.execute("SELECT COUNT(*) FROM gazetteer;")
                row = cur.fetchone()
                before_count = row[0] if row else 0

                logging.info("Starting bulk insert from gazetteer_staging to gazetteer...")
                insert_sql = """
                    INSERT INTO gazetteer (property_id, x_coordinate, y_coordinate, latitude, longitude, source)
                    SELECT DISTINCT uprn::VARCHAR, x_coordinate, y_coordinate, latitude, longitude, 'OS Open UPRN 2025-06'
                    FROM gazetteer_staging
                    WHERE uprn IS NOT NULL
                    ON CONFLICT (property_id) DO NOTHING;
                """
                cur.execute(insert_sql)
                conn.commit()

                # Count after insert
                cur.execute("SELECT COUNT(*) FROM gazetteer;")
                row = cur.fetchone()
                after_count = row[0] if row else 0
                inserted = after_count - before_count

                logging.info(f"Inserted {inserted} new rows into gazetteer.")
                logging.info("Running ANALYZE on gazetteer...")
                cur.execute("ANALYZE gazetteer;")
                conn.commit()

        elapsed = time.time() - start_time
        logging.info(f"Process completed in {elapsed:.2f} seconds.")

    except Exception as e:
        logging.error(f"Error during insertion from staging: {e}", exc_info=True)

if __name__ == "__main__":
    # Accept optional DB name from command line
    dbname = sys.argv[1] if len(sys.argv) > 1 else DBNAME
    if dbname != DBNAME:
        print(f"Using target database: {dbname}")
    else:
        print("Using default database from environment or config.")
    # Override DBNAME for connection
    DBNAME = dbname
    insert_from_staging()
