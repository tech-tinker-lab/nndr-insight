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
import json
import tempfile

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

# Performance settings
BATCH_SIZE = 50000  # Large batches for better performance
GML_ROOT = "data/opmplc_gml3_gb/data"
MAX_WORKERS = min(mp.cpu_count(), 8)  # Use available CPU cores, max 8

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

def extract_theme_from_props(props, feature_type=""):
    """Extract theme from various possible sources in GML properties"""
    # Try direct theme property
    if "theme" in props:
        return props["theme"].lower().replace(" ", "_")
    
    # Try building theme
    if "buildingTheme" in props:
        return props["buildingTheme"].lower().replace(" ", "_")
    
    # Try site theme
    if "siteTheme" in props:
        return props["siteTheme"].lower().replace(" ", "_")
    
    # Try to infer from feature type
    feature_type_lower = feature_type.lower()
    if "building" in feature_type_lower:
        return "building"
    elif "road" in feature_type_lower or "highway" in feature_type_lower:
        return "road"
    elif "water" in feature_type_lower or "river" in feature_type_lower or "lake" in feature_type_lower:
        return "water"
    elif "rail" in feature_type_lower or "train" in feature_type_lower:
        return "transport"
    elif "boundary" in feature_type_lower or "admin" in feature_type_lower:
        return "boundary"
    elif "park" in feature_type_lower or "forest" in feature_type_lower:
        return "land"
    else:
        return "other"

def process_gml_file_to_temp(filepath):
    """Process GML file and save to temporary files for each theme"""
    theme_files = defaultdict(list)
    temp_dir = tempfile.mkdtemp()
    
    try:
        with fiona.open(filepath, driver="GML") as src:
            for feature in src:
                try:
                    geom = shape(feature["geometry"])
                    props = feature["properties"]
                    feature_type = feature.get("type", "")
                    
                    theme = extract_theme_from_props(props, feature_type)
                    
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

                    theme_files[theme].append(record)
                    
                    # Write to temp file if batch size reached
                    if len(theme_files[theme]) >= BATCH_SIZE:
                        temp_file = os.path.join(temp_dir, f"{theme}_{len(theme_files)}.json")
                        with open(temp_file, 'w') as f:
                            json.dump(theme_files[theme], f)
                        theme_files[theme] = []
                        
                except Exception as e:
                    print(f"⚠️ Error processing feature in {filepath}: {e}")
                    continue
        
        # Write remaining records
        for theme, records in theme_files.items():
            if records:
                temp_file = os.path.join(temp_dir, f"{theme}_final.json")
                with open(temp_file, 'w') as f:
                    json.dump(records, f)
        
        return temp_dir
        
    except Exception as e:
        print(f"❌ Error processing file {filepath}: {e}")
        return None

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
        CREATE INDEX {table_name}_fclass_idx ON {table_name} (fclass);
    """)

def bulk_load_from_temp_files(cur, theme, temp_dir):
    """Bulk load from temporary files to staging table"""
    table_name = f"os_oml_{theme}_staging"
    total_count = 0
    
    # Find all temp files for this theme
    temp_files = glob.glob(os.path.join(temp_dir, f"{theme}_*.json"))
    
    for temp_file in temp_files:
        try:
            with open(temp_file, 'r') as f:
                records = json.load(f)
            
            if not records:
                continue
            
            # Prepare data for COPY
            from io import StringIO
            output = StringIO()
            for record in records:
                row = (
                    record["fid"],
                    record["theme"],
                    record["make"],
                    record["physicalpresence"],
                    record["descriptivegroup"],
                    record["descriptiveterm"],
                    record["fclass"],
                    record["geometry_hex"]
                )
                output.write('\t'.join(str(field) for field in row) + '\n')
            output.seek(0)
            
            # Use COPY for bulk loading
            cur.copy_expert(
                f"COPY {table_name} FROM STDIN WITH (FORMAT CSV, DELIMITER E'\\t')",
                output
            )
            
            total_count += len(records)
            
        except Exception as e:
            print(f"⚠️ Error loading from {temp_file}: {e}")
            continue
    
    return total_count

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

def process_file_parallel(filepath, dbname):
    """Process a single file in parallel and return theme counts"""
    theme_counts = defaultdict(int)
    
    # Process GML to temp files
    temp_dir = process_gml_file_to_temp(filepath)
    if not temp_dir:
        return theme_counts
    
    try:
        # Load from temp files to database
        conn = get_db_connection(dbname)
        with conn.cursor() as cur:
            # Get all themes from temp files
            temp_files = glob.glob(os.path.join(temp_dir, "*.json"))
            themes = set()
            for temp_file in temp_files:
                theme = os.path.basename(temp_file).split('_')[0]
                themes.add(theme)
            
            # Load each theme
            for theme in themes:
                create_staging_table(cur, theme)
                count = bulk_load_from_temp_files(cur, theme, temp_dir)
                theme_counts[theme] += count
            
            conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
    
    finally:
        # Clean up temp files
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
    
    return theme_counts

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

def load_data_parallel(dbname):
    """Main ingestion function with parallel processing"""
    start_time = time.time()
    
    # Collect all GML files
    files = glob.glob(os.path.join(GML_ROOT, "**", "*.gml"), recursive=True)
    print(f"📂 Found {len(files)} GML files under {GML_ROOT}")
    print(f"🔧 Using {MAX_WORKERS} parallel workers")
    
    if not files:
        print("No GML files found!")
        return
    
    # Process files in parallel
    total_counts = defaultdict(int)
    
    try:
        # Create process pool
        with mp.Pool(processes=MAX_WORKERS) as pool:
            # Process files in parallel
            process_func = partial(process_file_parallel, dbname=dbname)
            
            print("🚀 Starting parallel processing...")
            results = list(tqdm(
                pool.imap(process_func, files),
                total=len(files),
                desc="Processing GML files"
            ))
            
            # Aggregate results
            for theme_counts in results:
                for theme, count in theme_counts.items():
                    total_counts[theme] += count
        
        # Transfer from staging to final tables
        print("📊 Transferring data to final tables...")
        with get_db_connection(dbname) as conn:
            with conn.cursor() as cur:
                for theme in total_counts.keys():
                    if total_counts[theme] > 0:
                        create_final_table(cur, theme)
                        final_count = transfer_from_staging_to_final(cur, theme)
                        print(f"  📌 {theme}: {final_count} features")
                
                # Create summary table
                print("📈 Creating summary table...")
                create_summary_table(cur, total_counts)
                conn.commit()
        
        # Final statistics
        print("\n✅ Parallel ingestion complete!")
        print("📊 Final statistics:")
        for theme, count in sorted(total_counts.items()):
            print(f"  📌 {theme}: {count} features")
        
    except Exception as e:
        print(f"❌ Error during parallel ingestion: {e}")
        raise
    
    total_time = time.time() - start_time
    print(f"⏱️ Total processing time: {total_time:.1f} seconds")
    print(f"📈 Average: {len(files)/total_time:.1f} files/second")
    print(f"🚀 Speedup: {MAX_WORKERS}x parallel processing")

def main():
    dbname = sys.argv[1] if len(sys.argv) > 1 else DBNAME
    if dbname != DBNAME:
        print(f"Using target database: {dbname}")
    else:
        print("Using default database from environment or config.")
    
    load_data_parallel(dbname)

if __name__ == "__main__":
    main() 