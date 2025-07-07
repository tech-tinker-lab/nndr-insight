import os
import sys
import glob
import time
import fiona
import psycopg2
from dotenv import load_dotenv
from shapely.geometry import shape
from shapely.wkb import dumps as wkb_dumps
from collections import defaultdict
from tqdm import tqdm
import multiprocessing as mp
from functools import partial

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

# Performance settings
BATCH_SIZE = 10000  # Increased from 500
GML_ROOT = "data/opmplc_gml3_gb/data"
MAX_WORKERS = 4  # Number of parallel processes

# Optional: restrict to specific themes
FILTER_THEMES = None  # Example: ["building", "road"], or None for all

def get_db_connection(dbname):
    """Get database connection"""
    return psycopg2.connect(
        dbname=dbname,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )

def create_staging_table(cur, theme):
    """Create staging table for bulk loading"""
    table_name = f"os_oml_{theme}_staging"
    cur.execute(f"""
        DROP TABLE IF EXISTS {table_name};
        CREATE TABLE {table_name} (
            fid TEXT,
            theme TEXT,
            make TEXT,
            physicalpresence TEXT,
            descriptivegroup TEXT,
            descriptiveterm TEXT,
            fclass TEXT,
            geometry_hex TEXT
        );
    """)

def create_final_table(cur, theme):
    """Create final themed table with proper structure and indexes"""
    table_name = f"os_oml_{theme}"
    cur.execute(f"""
        DROP TABLE IF EXISTS {table_name};
        CREATE TABLE {table_name} (
            id SERIAL PRIMARY KEY,
            fid TEXT,
            theme TEXT,
            make TEXT,
            physicalpresence TEXT,
            descriptivegroup TEXT,
            descriptiveterm TEXT,
            fclass TEXT,
            geometry geometry(Geometry, 27700)
        );
        CREATE INDEX {table_name}_geom_idx ON {table_name} USING GIST (geometry);
        CREATE INDEX {table_name}_fid_idx ON {table_name} (fid);
        CREATE INDEX {table_name}_theme_idx ON {table_name} (theme);
    """)

def process_gml_file_optimized(filepath):
    """Process GML file with optimized memory usage"""
    themed_records = defaultdict(list)
    
    try:
        with fiona.open(filepath, driver="GML") as src:
            for feature in src:
                try:
                    geom = shape(feature["geometry"])
                    props = feature["properties"]
                    
                    # Extract theme from various possible sources
                    theme = None
                    if "theme" in props:
                        theme = props["theme"].lower().replace(" ", "_")
                    elif "buildingTheme" in props:
                        theme = props["buildingTheme"].lower().replace(" ", "_")
                    elif "siteTheme" in props:
                        theme = props["siteTheme"].lower().replace(" ", "_")
                    else:
                        # Try to infer from feature type
                        feature_type = feature.get("type", "").lower()
                        if "building" in feature_type:
                            theme = "building"
                        elif "road" in feature_type:
                            theme = "road"
                        elif "water" in feature_type:
                            theme = "water"
                        else:
                            theme = "other"
                    
                    if FILTER_THEMES and theme not in FILTER_THEMES:
                        continue

                    record = {
                        "fid": feature.get("id", ""),
                        "theme": props.get("theme", ""),
                        "make": props.get("make", ""),
                        "physicalpresence": props.get("physicalpresence", ""),
                        "descriptivegroup": props.get("descriptivegroup", ""),
                        "descriptiveterm": props.get("descriptiveterm", ""),
                        "fclass": props.get("fclass", ""),
                        "geometry_hex": wkb_dumps(geom, hex=True)
                    }

                    themed_records[theme].append(record)
                    
                    # Flush to disk if batch size reached
                    if len(themed_records[theme]) >= BATCH_SIZE:
                        yield theme, themed_records[theme]
                        themed_records[theme] = []
                        
                except Exception as e:
                    print(f"⚠️ Error processing feature in {filepath}: {e}")
                    continue
        
        # Yield remaining records
        for theme, records in themed_records.items():
            if records:
                yield theme, records
                
    except Exception as e:
        print(f"❌ Error processing file {filepath}: {e}")

def bulk_load_to_staging(cur, theme, records):
    """Bulk load records to staging table using COPY"""
    if not records:
        return 0
    
    table_name = f"os_oml_{theme}_staging"
    
    # Prepare data for COPY
    data = []
    for record in records:
        data.append((
            record["fid"],
            record["theme"],
            record["make"],
            record["physicalpresence"],
            record["descriptivegroup"],
            record["descriptiveterm"],
            record["fclass"],
            record["geometry_hex"]
        ))
    
    # Use COPY for bulk loading
    from io import StringIO
    output = StringIO()
    for row in data:
        output.write('\t'.join(str(field) for field in row) + '\n')
    output.seek(0)
    
    cur.copy_expert(
        f"COPY {table_name} FROM STDIN WITH (FORMAT CSV, DELIMITER E'\\t')",
        output
    )
    
    return len(records)

def transfer_from_staging_to_final(cur, theme):
    """Transfer data from staging to final table with geometry conversion"""
    staging_table = f"os_oml_{theme}_staging"
    final_table = f"os_oml_{theme}"
    
    cur.execute(f"""
        INSERT INTO {final_table} (
            fid, theme, make, physicalpresence,
            descriptivegroup, descriptiveterm, fclass, geometry
        )
        SELECT 
            fid, theme, make, physicalpresence,
            descriptivegroup, descriptiveterm, fclass,
            ST_GeomFromWKB(decode(geometry_hex, 'hex'), 27700) as geometry
        FROM {staging_table}
        WHERE geometry_hex IS NOT NULL AND geometry_hex != '';
    """)
    
    # Get count of transferred records
    cur.execute(f"SELECT COUNT(*) FROM {final_table}")
    return cur.fetchone()[0]

def process_file_batch(filepath, dbname):
    """Process a single file and return theme counts"""
    conn = get_db_connection(dbname)
    theme_counts = defaultdict(int)
    
    try:
        with conn.cursor() as cur:
            # Process file and load to staging
            for theme, records in process_gml_file_optimized(filepath):
                # Create staging table if needed
                create_staging_table(cur, theme)
                
                # Bulk load to staging
                count = bulk_load_to_staging(cur, theme, records)
                theme_counts[theme] += count
                
                conn.commit()
        
        conn.close()
        return theme_counts
        
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        conn.close()
        return {}

def create_summary_table(cur, totals):
    """Create summary table with theme statistics"""
    cur.execute("""
        DROP TABLE IF EXISTS os_oml_theme_summary;
        CREATE TABLE os_oml_theme_summary (
            theme TEXT PRIMARY KEY,
            feature_count INTEGER,
            table_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    for theme, count in totals.items():
        cur.execute("""
            INSERT INTO os_oml_theme_summary (theme, feature_count, table_name)
            VALUES (%s, %s, %s)
        """, (theme, count, f"os_oml_{theme}"))

def load_data(dbname):
    """Main ingestion function with optimized performance"""
    start_time = time.time()
    
    # Collect all GML files
    files = glob.glob(os.path.join(GML_ROOT, "**", "*.gml"), recursive=True)
    print(f"📂 Found {len(files)} GML files under {GML_ROOT}")
    
    if not files:
        print("No GML files found!")
        return
    
    # Process files in batches for better memory management
    batch_size = 10  # Process 10 files at a time
    total_counts = defaultdict(int)
    
    try:
        with get_db_connection(dbname) as conn:
            with conn.cursor() as cur:
                # Process files in batches
                for i in range(0, len(files), batch_size):
                    batch_files = files[i:i + batch_size]
                    print(f"Processing batch {i//batch_size + 1}/{(len(files) + batch_size - 1)//batch_size}")
                    
                    # Process each file in the batch
                    for filepath in tqdm(batch_files, desc="Processing files"):
                        theme_counts = process_file_batch(filepath, dbname)
                        
                        # Aggregate counts
                        for theme, count in theme_counts.items():
                            total_counts[theme] += count
                    
                    # Transfer from staging to final tables for this batch
                    print("Transferring data to final tables...")
                    for theme in total_counts.keys():
                        if total_counts[theme] > 0:
                            # Create final table if not exists
                            create_final_table(cur, theme)
                            
                            # Transfer data
                            final_count = transfer_from_staging_to_final(cur, theme)
                            print(f"  📌 {theme}: {final_count} features")
                    
                    conn.commit()
                
                # Create summary table
                print("Creating summary table...")
                create_summary_table(cur, total_counts)
                conn.commit()
                
                # Final statistics
                print("\n✅ Ingestion complete!")
                print("📊 Final statistics:")
                for theme, count in sorted(total_counts.items()):
                    print(f"  📌 {theme}: {count} features")
                
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        raise
    
    total_time = time.time() - start_time
    print(f"⏱️ Total processing time: {total_time:.1f} seconds")
    print(f"📈 Average: {len(files)/total_time:.1f} files/second")

def main():
    dbname = sys.argv[1] if len(sys.argv) > 1 else DBNAME
    if dbname != DBNAME:
        print(f"Using target database: {dbname}")
    else:
        print("Using default database from environment or config.")
    
    load_data(dbname)

if __name__ == "__main__":
    main()
