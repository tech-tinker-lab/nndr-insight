import csv
import os
import sys
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

BATCH_SIZE = 50000  # Increased for better performance
DATA_DIR = "data/opname_csv_gb/Data"

def find_csv_files(folder_path):
    """Find all CSV files in the given folder"""
    csv_files = []
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            if file.endswith('.csv'):
                csv_files.append(os.path.join(folder_path, file))
    return csv_files

def create_staging_table(cur):
    """Create staging table for bulk loading - matches actual CSV structure"""
    cur.execute("""
        DROP TABLE IF EXISTS os_open_names_staging;
        CREATE TABLE os_open_names_staging (
            os_id TEXT,
            names_uri TEXT,
            name1 TEXT,
            name1_lang TEXT,
            name2 TEXT,
            name2_lang TEXT,
            type TEXT,
            local_type TEXT,
            geometry_x DOUBLE PRECISION,
            geometry_y DOUBLE PRECISION,
            most_detail_view_res INTEGER,
            least_detail_view_res INTEGER,
            mbr_xmin DOUBLE PRECISION,
            mbr_ymin DOUBLE PRECISION,
            mbr_xmax DOUBLE PRECISION,
            mbr_ymax DOUBLE PRECISION,
            postcode_district TEXT,
            postcode_district_uri TEXT,
            populated_place TEXT,
            populated_place_uri TEXT,
            populated_place_type TEXT,
            district_borough TEXT,
            district_borough_uri TEXT,
            district_borough_type TEXT,
            county_unitary TEXT,
            county_unitary_uri TEXT,
            county_unitary_type TEXT,
            region TEXT,
            region_uri TEXT,
            country TEXT,
            country_uri TEXT,
            related_spatial_object TEXT,
            same_as_dbpedia TEXT,
            same_as_geonames TEXT
        );
    """)

def load_data(dbname):
    start_time = time.time()
    csv_files = find_csv_files(DATA_DIR)
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
                    print(f"Processing {os.path.basename(file_path)}...")
                    file_start = time.time()
                    
                    try:
                        # Bulk load CSV into staging table using comma delimiter
                        with open(file_path, 'r', encoding='utf-8') as f:
                            cur.copy_expert(
                                """
                                COPY os_open_names_staging FROM STDIN WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE)
                                """, f
                            )
                        
                        # Get count of loaded rows
                        cur.execute("SELECT COUNT(*) FROM os_open_names_staging")
                        row = cur.fetchone()
                        file_rows = row[0] if row else 0
                        total_rows_inserted += file_rows
                        
                        file_time = time.time() - file_start
                        print(f"  Loaded {file_rows} rows in {file_time:.1f}s")
                        conn.commit()
                        
                    except Exception as e:
                        print(f"  Error processing {os.path.basename(file_path)}: {e}")
                        print(f"  Rolling back transaction and continuing...")
                        conn.rollback()
                        continue
                
                print(f"Total rows in staging: {total_rows_inserted}")
                
                if total_rows_inserted > 0:
                    # Move from staging to final table with geometry
                    print("Creating final table with geometry...")
                    cur.execute("""
                        INSERT INTO os_open_names (
                            os_id, names_uri, name1, name1_lang, name2, name2_lang, type, local_type,
                            geometry_x, geometry_y, most_detail_view_res, least_detail_view_res,
                            mbr_xmin, mbr_ymin, mbr_xmax, mbr_ymax, postcode_district, postcode_district_uri,
                            populated_place, populated_place_uri, populated_place_type,
                            district_borough, district_borough_uri, district_borough_type,
                            county_unitary, county_unitary_uri, county_unitary_type,
                            region, region_uri, country, country_uri,
                            related_spatial_object, same_as_dbpedia, same_as_geonames, geom
                        )
                        SELECT 
                            os_id, names_uri, name1, name1_lang, name2, name2_lang, type, local_type,
                            geometry_x, geometry_y, most_detail_view_res, least_detail_view_res,
                            mbr_xmin, mbr_ymin, mbr_xmax, mbr_ymax, postcode_district, postcode_district_uri,
                            populated_place, populated_place_uri, populated_place_type,
                            district_borough, district_borough_uri, district_borough_type,
                            county_unitary, county_unitary_uri, county_unitary_type,
                            region, region_uri, country, country_uri,
                            related_spatial_object, same_as_dbpedia, same_as_geonames,
                            ST_SetSRID(ST_MakePoint(geometry_x, geometry_y), 27700) as geom
                        FROM os_open_names_staging
                        WHERE geometry_x IS NOT NULL AND geometry_y IS NOT NULL;
                    """)
                    conn.commit()
                    
                    # Get final count
                    cur.execute("SELECT COUNT(*) FROM os_open_names")
                    row = cur.fetchone()
                    final_count = row[0] if row else 0
                    
                    print(f"✅ Successfully loaded {final_count} rows into os_open_names")
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