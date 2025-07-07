import csv
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

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'data', 'opname_csv_gb', 'Data')

# Official OS Open Names columns from OS_Open_Names_Header.csv
OS_OPEN_NAMES_COLUMNS = [
    'ID', 'NAMES_URI', 'NAME1', 'NAME1_LANG', 'NAME2', 'NAME2_LANG', 'TYPE', 'LOCAL_TYPE',
    'GEOMETRY_X', 'GEOMETRY_Y', 'MOST_DETAIL_VIEW_RES', 'LEAST_DETAIL_VIEW_RES',
    'MBR_XMIN', 'MBR_YMIN', 'MBR_XMAX', 'MBR_YMAX', 'POSTCODE_DISTRICT', 'POSTCODE_DISTRICT_URI',
    'POPULATED_PLACE', 'POPULATED_PLACE_URI', 'POPULATED_PLACE_TYPE', 'DISTRICT_BOROUGH',
    'DISTRICT_BOROUGH_URI', 'DISTRICT_BOROUGH_TYPE', 'COUNTY_UNITARY', 'COUNTY_UNITARY_URI',
    'COUNTY_UNITARY_TYPE', 'REGION', 'REGION_URI', 'COUNTRY', 'COUNTRY_URI',
    'RELATED_SPATIAL_OBJECT', 'SAME_AS_DBPEDIA', 'SAME_AS_GEONAMES'
]

def find_csv_files(folder_path):
    """Find all CSV files in the given folder"""
    csv_files = []
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            if file.endswith('.csv'):
                csv_files.append(os.path.join(folder_path, file))
    return sorted(csv_files)

def create_table_schema(cur):
    """Create table with all TEXT columns initially to avoid data type issues"""
    # Drop existing table
    cur.execute("DROP TABLE IF EXISTS os_open_names_simple;")
    
    # Create table with all TEXT columns initially
    column_definitions = []
    for col in OS_OPEN_NAMES_COLUMNS:
        column_definitions.append(f'"{col}" TEXT')
    
    # Add geometry column
    column_definitions.append('geom GEOMETRY(POINT, 27700)')
    
    create_sql = f"""
    CREATE TABLE os_open_names_simple (
        {', '.join(column_definitions)}
    );
    """
    
    cur.execute(create_sql)
    print(f"Created simple table with {len(OS_OPEN_NAMES_COLUMNS)} TEXT columns + geometry")

def get_first_row_from_file(file_path):
    """Get the first data row from a CSV file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            # Get first row (no header to skip)
            first_row = next(reader)
            
            # Normalize to official column count
            if len(first_row) < len(OS_OPEN_NAMES_COLUMNS):
                first_row = first_row + [''] * (len(OS_OPEN_NAMES_COLUMNS) - len(first_row))
            elif len(first_row) > len(OS_OPEN_NAMES_COLUMNS):
                first_row = first_row[:len(OS_OPEN_NAMES_COLUMNS)]
            
            return first_row
    except Exception as e:
        print(f"Error reading first row from {file_path}: {e}")
        return None

def load_sample_data(dbname):
    start_time = time.time()
    csv_files = find_csv_files(DATA_DIR)
    print(f"Found {len(csv_files)} CSV files in {DATA_DIR}")
    
    if not csv_files:
        print("No CSV files found!")
        return

    print(f"Using official OS Open Names columns: {OS_OPEN_NAMES_COLUMNS}")

    try:
        with psycopg2.connect(
            dbname=dbname,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        ) as conn:
            with conn.cursor() as cur:
                print("Creating simple table with all TEXT columns...")
                create_table_schema(cur)
                conn.commit()
                
                total_rows_inserted = 0
                processed_files = 0
                
                for file_path in csv_files:
                    print(f"Processing first row from {os.path.basename(file_path)}...")
                    
                    try:
                        first_row = get_first_row_from_file(file_path)
                        if first_row:
                            # Insert the first row
                            placeholders = ', '.join(['%s'] * len(OS_OPEN_NAMES_COLUMNS))
                            insert_sql = f"""
                                INSERT INTO os_open_names_simple ({', '.join(['"' + col + '"' for col in OS_OPEN_NAMES_COLUMNS])})
                                VALUES ({placeholders})
                            """
                            cur.execute(insert_sql, first_row)
                            total_rows_inserted += 1
                            processed_files += 1
                            
                            # Commit every 50 files
                            if processed_files % 50 == 0:
                                conn.commit()
                                print(f"  Committed after {processed_files} files")
                        
                    except Exception as e:
                        print(f"  Error processing {os.path.basename(file_path)}: {e}")
                        # Rollback and continue
                        conn.rollback()
                        continue
                
                # Final commit
                conn.commit()
                
                print(f"Total sample rows loaded: {total_rows_inserted}")
                
                # Create geometry from coordinates (handle conversion errors)
                print("Creating geometry from coordinates...")
                cur.execute("""
                    UPDATE os_open_names_simple 
                    SET geom = ST_SetSRID(ST_MakePoint(
                        CASE WHEN "GEOMETRY_X" ~ '^[0-9]+\.?[0-9]*$' THEN "GEOMETRY_X"::NUMERIC ELSE NULL END,
                        CASE WHEN "GEOMETRY_Y" ~ '^[0-9]+\.?[0-9]*$' THEN "GEOMETRY_Y"::NUMERIC ELSE NULL END
                    ), 27700)
                    WHERE "GEOMETRY_X" IS NOT NULL AND "GEOMETRY_Y" IS NOT NULL
                    AND "GEOMETRY_X" ~ '^[0-9]+\.?[0-9]*$' AND "GEOMETRY_Y" ~ '^[0-9]+\.?[0-9]*$';
                """)
                conn.commit()
                
                # Get final count and quality check
                cur.execute("SELECT COUNT(*) FROM os_open_names_simple")
                row = cur.fetchone()
                final_count = row[0] if row else 0
                
                cur.execute("SELECT COUNT(*) FROM os_open_names_simple WHERE geom IS NOT NULL")
                row = cur.fetchone()
                geom_count = row[0] if row else 0
                
                print(f"✅ Successfully loaded {final_count} sample rows into os_open_names_simple")
                print(f"   - {geom_count} rows with valid geometry")
                print(f"   - {final_count - geom_count} rows without geometry")
                
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
    
    load_sample_data(dbname)

if __name__ == "__main__":
    main() 