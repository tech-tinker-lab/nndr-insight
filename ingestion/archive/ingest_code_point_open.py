import os
import sys
import glob
import time
import psycopg2
from dotenv import load_dotenv

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

DATA_DIR = "data/codepo_gb/Data/CSV"

def create_staging_table(cur):
    """Create staging table for bulk loading"""
    cur.execute("""
        DROP TABLE IF EXISTS code_point_open_staging;
        CREATE TABLE code_point_open_staging (
            postcode TEXT,
            positional_quality_indicator INTEGER,
            easting DOUBLE PRECISION,
            northing DOUBLE PRECISION,
            country_code TEXT,
            nhs_regional_ha_code TEXT,
            nhs_ha_code TEXT,
            admin_county_code TEXT,
            admin_district_code TEXT,
            admin_ward_code TEXT
        );
    """)

def process_file(file_path, cur):
    """Process a single CSV file using bulk COPY"""
    print(f"Processing {os.path.basename(file_path)}...")
    file_start = time.time()
    
    try:
        # Bulk load CSV into staging table
        with open(file_path, 'r', encoding='utf-8') as f:
            cur.copy_expert(
                """
                COPY code_point_open_staging FROM STDIN WITH (FORMAT CSV, DELIMITER ',', HEADER FALSE)
                """, f
            )
        
        # Get count of loaded rows
        cur.execute("SELECT COUNT(*) FROM code_point_open_staging")
        row = cur.fetchone()
        file_rows = row[0] if row else 0
        
        file_time = time.time() - file_start
        print(f"  Loaded {file_rows} rows in {file_time:.1f}s")
        
        return file_rows
        
    except Exception as e:
        print(f"  Error processing {os.path.basename(file_path)}: {e}")
        return 0

def load_data(dbname):
    start_time = time.time()
    csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    print(f"Found {len(csv_files)} CSV files in {DATA_DIR}")
    
    if not csv_files:
        print("No CSV files found!")
        return

    try:
        with psycopg2.connect(
            dbname=dbname,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        ) as conn:
            with conn.cursor() as cur:
                print("Creating staging table...")
                create_staging_table(cur)
                conn.commit()
                
                total_rows_inserted = 0
                
                for file_path in csv_files:
                    file_rows = process_file(file_path, cur)
                    total_rows_inserted += file_rows
                    conn.commit()
                
                print(f"Total rows in staging: {total_rows_inserted}")
                
                if total_rows_inserted > 0:
                    # Move from staging to final table with geometry
                    print("Creating final table with geometry...")
                    cur.execute("""
                        INSERT INTO code_point_open (
                            postcode, positional_quality_indicator, easting, northing,
                            country_code, nhs_regional_ha_code, nhs_ha_code,
                            admin_county_code, admin_district_code, admin_ward_code, geom
                        )
                        SELECT 
                            postcode, positional_quality_indicator, easting, northing,
                            country_code, nhs_regional_ha_code, nhs_ha_code,
                            admin_county_code, admin_district_code, admin_ward_code,
                            ST_SetSRID(ST_MakePoint(easting, northing), 27700) as geom
                        FROM code_point_open_staging
                        WHERE easting IS NOT NULL AND northing IS NOT NULL;
                    """)
                    conn.commit()
                    
                    # Get final count
                    cur.execute("SELECT COUNT(*) FROM code_point_open")
                    row = cur.fetchone()
                    final_count = row[0] if row else 0
                    
                    print(f"✅ Successfully loaded {final_count} rows into code_point_open")
                else:
                    print("No data was loaded successfully.")
                
    except Exception as e:
        print(f"Error during ingestion: {e}")
        raise

    total_time = time.time() - start_time
    print(f"Total processing time: {total_time:.1f} seconds")

def main():
    dbname = sys.argv[1] if len(sys.argv) > 1 else DBNAME
    if dbname != DBNAME:
        print(f"Using target database: {dbname}")
    else:
        print("Using default database from environment or config.")
    
    load_data(dbname)

if __name__ == "__main__":
    main()
