import os
import sys
import time
import psycopg2
from dotenv import load_dotenv

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

ONSPD_CSV = '../../backend/data/ONSPD_Online_Latest_Centroids.csv'

def main():
    dbname = sys.argv[1] if len(sys.argv) > 1 else DBNAME
    start = time.time()
    try:
        with psycopg2.connect(
            dbname=dbname,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        ) as conn:
            with conn.cursor() as cur:
                print(f"Truncating onspd_staging table...")
                cur.execute("TRUNCATE TABLE onspd_staging;")
                print(f"Bulk loading ONSPD from {ONSPD_CSV} into onspd_staging...")
                with open(ONSPD_CSV, 'r', encoding='utf-8') as f:
                    # Print the first two lines for debugging
                    header_line = f.readline()
                    data_line = f.readline()
                    print(f"CSV Header: {header_line.strip()}")
                    print(f"First data row: {data_line.strip()}")
                    f.seek(0)
                    print("Starting COPY command...")
                    cur.copy_expert(
                        """
                        COPY onspd_staging FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
                        """, f
                    )
                print("COPY command finished. Committing...")
                conn.commit()
                print("Bulk load complete.")

                # Optionally, move from staging to final table with deduplication/upsert
                print("Upserting from staging to final onspd table...")
                cur.execute("""
                    INSERT INTO onspd (
                        pcds, pcd, lat, long, ctry, oslaua, osward, parish,
                        oa11, lsoa11, msoa11, imd, rgn, pcon, ur01ind, oac11,
                        oseast1m, osnrth1m, dointr, doterm
                    )
                    SELECT DISTINCT
                        pcds, pcd, lat, long, ctry, oslaua, osward, parish,
                        oa11, lsoa11, msoa11, imd, rgn, pcon, ur01ind, oac11,
                        oseast1m, osnrth1m, dointr, doterm
                    FROM onspd_staging
                    ON CONFLICT (pcds) DO UPDATE SET
                        pcd = EXCLUDED.pcd,
                        lat = EXCLUDED.lat,
                        long = EXCLUDED.long,
                        ctry = EXCLUDED.ctry,
                        oslaua = EXCLUDED.oslaua,
                        osward = EXCLUDED.osward,
                        parish = EXCLUDED.parish,
                        oa11 = EXCLUDED.oa11,
                        lsoa11 = EXCLUDED.lsoa11,
                        msoa11 = EXCLUDED.msoa11,
                        imd = EXCLUDED.imd,
                        rgn = EXCLUDED.rgn,
                        pcon = EXCLUDED.pcon,
                        ur01ind = EXCLUDED.ur01ind,
                        oac11 = EXCLUDED.oac11,
                        oseast1m = EXCLUDED.oseast1m,
                        osnrth1m = EXCLUDED.osnrth1m,
                        dointr = EXCLUDED.dointr,
                        doterm = EXCLUDED.doterm;
                """)
                print("Upsert finished. Committing...")
                conn.commit()
                print("Upsert complete.")

                print("Counting records in onspd table...")
                cur.execute("SELECT COUNT(*) FROM onspd;")
                row = cur.fetchone()
                total = row[0] if row else 0
                print(f"ONSPD import complete. Total records in onspd: {total}")

    except Exception as e:
        print(f"Error during ONSPD import: {e}")

    end = time.time()
    print(f"Total time: {end-start:.1f} seconds")

if __name__ == "__main__":
    main()
