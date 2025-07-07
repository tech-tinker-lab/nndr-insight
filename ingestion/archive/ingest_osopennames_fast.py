import csv
import os
import sys
import time
import psycopg2
from dotenv import load_dotenv
import tempfile

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
    return sorted(csv_files)  # Sort for consistent processing order

def create_table_schema(cur):
    """Create table with official OS Open Names columns"""
    # Drop existing table
    cur.execute("DROP TABLE IF EXISTS os_open_names;")
    
    # Create table with official columns
    column_definitions = []
    for col in OS_OPEN_NAMES_COLUMNS:
        # Map columns to appropriate PostgreSQL types
        if col in ['GEOMETRY_X', 'GEOMETRY_Y', 'MBR_XMIN', 'MBR_YMIN', 'MBR_XMAX', 'MBR_YMAX']:
            column_definitions.append(f'"{col}" NUMERIC')
        elif col in ['MOST_DETAIL_VIEW_RES', 'LEAST_DETAIL_VIEW_RES']:
            column_definitions.append(f'"{col}" INTEGER')
        else:
            column_definitions.append(f'"{col}" TEXT')
    
    # Add geometry column
    column_definitions.append('geom GEOMETRY(POINT, 27700)')
    
    create_sql = f"""
    CREATE TABLE os_open_names (
        {', '.join(column_definitions)}
    );
    """
    
    cur.execute(create_sql)
    print(f"Created table with {len(OS_OPEN_NAMES_COLUMNS)} official columns + geometry")

def normalize_csv_to_header(input_path):
    """Yield rows from input_path, normalized to official header length (pad/truncate as needed)"""
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        # No header to skip - first line is data
        for row in reader:
            if len(row) < len(OS_OPEN_NAMES_COLUMNS):
                row = row + [''] * (len(OS_OPEN_NAMES_COLUMNS) - len(row))
            elif len(row) > len(OS_OPEN_NAMES_COLUMNS):
                row = row[:len(OS_OPEN_NAMES_COLUMNS)]
            yield row

def load_data(dbname):
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
                print("Creating table with official columns...")
                create_table_schema(cur)
                conn.commit()
                
                total_rows_inserted = 0
                processed_files = 0
                
                for file_path in csv_files:
                    print(f"Processing {os.path.basename(file_path)}...")
                    file_start = time.time()
                    
                    try:
                        # Normalize and write to temp file
                        with tempfile.NamedTemporaryFile('w', delete=False, newline='', encoding='utf-8') as tmpfile:
                            writer = csv.writer(tmpfile)
                            writer.writerow(OS_OPEN_NAMES_COLUMNS)
                            for row in normalize_csv_to_header(file_path):
                                writer.writerow(row)
                            tmpfile_path = tmpfile.name
                        
                        # Use COPY for fast bulk insertion
                        with open(tmpfile_path, 'r', encoding='utf-8') as f:
                            cur.copy_expert(
                                f"""
                                COPY os_open_names ({', '.join(['"' + col + '"' for col in OS_OPEN_NAMES_COLUMNS])}) 
                                FROM STDIN WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE)
                                """, f
                            )
                        os.remove(tmpfile_path)
                        
                        # Get count of loaded rows
                        cur.execute("SELECT COUNT(*) FROM os_open_names")
                        row = cur.fetchone()
                        current_total = row[0] if row else 0
                        file_rows = current_total - total_rows_inserted
                        total_rows_inserted = current_total
                        
                        file_time = time.time() - file_start
                        print(f"  Loaded {file_rows} rows in {file_time:.1f}s")
                        processed_files += 1
                        
                        # Commit every 10 files to avoid long transactions
                        if processed_files % 10 == 0:
                            conn.commit()
                            print(f"  Committed after {processed_files} files")
                        
                    except Exception as e:
                        print(f"  Error processing {os.path.basename(file_path)}: {e}")
                        print(f"  Rolling back transaction and continuing...")
                        conn.rollback()
                        continue
                
                # Final commit
                conn.commit()
                
                print(f"Total rows loaded: {total_rows_inserted}")
                
                # Create geometry from coordinates
                print("Creating geometry from coordinates...")
                cur.execute("""
                    UPDATE os_open_names 
                    SET geom = ST_SetSRID(ST_MakePoint("GEOMETRY_X", "GEOMETRY_Y"), 27700)
                    WHERE "GEOMETRY_X" IS NOT NULL AND "GEOMETRY_Y" IS NOT NULL;
                """)
                conn.commit()
                
                # Get final count and quality check
                cur.execute("SELECT COUNT(*) FROM os_open_names")
                row = cur.fetchone()
                final_count = row[0] if row else 0
                
                cur.execute("SELECT COUNT(*) FROM os_open_names WHERE geom IS NOT NULL")
                row = cur.fetchone()
                geom_count = row[0] if row else 0
                
                print(f"✅ Successfully loaded {final_count} rows into os_open_names")
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
    
    load_data(dbname)

if __name__ == "__main__":
    main() 