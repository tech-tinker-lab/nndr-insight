import psycopg2
import os
from dotenv import load_dotenv

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

def load_to_staging(csv_path, truncate_staging=True):
    if not os.path.isfile(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        return

    try:
        with psycopg2.connect(
            dbname=DBNAME,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        ) as conn:
            with conn.cursor() as cur:
                if truncate_staging:
                    print("Truncating gazetteer_staging table before load...")
                    cur.execute("TRUNCATE TABLE gazetteer_staging;")
                    conn.commit()

                print(f"Starting bulk load from {csv_path} into gazetteer_staging...")
                with open(csv_path, 'r', encoding='utf-8') as f:
                    # Preview first two lines
                    line1 = f.readline()
                    line2 = f.readline()
                    print('First line (header):', line1.strip())
                    print('Second line (first data row):', line2.strip())
                    f.seek(0)
                    copy_sql = """
                        COPY gazetteer_staging (uprn, x_coordinate, y_coordinate, latitude, longitude)
                        FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
                    """
                    cur.copy_expert(sql=copy_sql, file=f)
                    conn.commit()

                cur.execute("SELECT COUNT(*) FROM gazetteer_staging;")
                row = cur.fetchone()
                rowcount = row[0] if row else 0
                print(f"Loaded {rowcount} rows into gazetteer_staging.")

    except Exception as e:
        print(f"Error during staging load: {e}")

if __name__ == "__main__":
    import sys
    default_path = "data/osopenuprn_202506_csv/osopenuprn_202506.csv"
    csv_file = sys.argv[1] if len(sys.argv) > 1 else default_path
    if len(sys.argv) < 2:
        print(f"No CSV file path provided; using default: {default_path}")
    load_to_staging(csv_file)
