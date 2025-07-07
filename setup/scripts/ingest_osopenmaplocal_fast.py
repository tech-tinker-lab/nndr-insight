import os
import glob
import time
import fiona
import sqlalchemy
from sqlalchemy import text, create_engine
from shapely.geometry import shape
from shapely.wkb import dumps as wkb_dumps
from dotenv import load_dotenv

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

# --- Configuration ---
USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")
TABLE_NAME = "os_open_map_local"
BATCH_SIZE = 1000

GML_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'data', 'opmplc_gml3_gb', 'data')

# --- GML Collection ---
def collect_gml_files():
    return glob.glob(os.path.join(GML_ROOT, "**", "*.gml"), recursive=True)

# --- Parse GML Features ---
def process_gml_file(filepath):
    records = []
    try:
        with fiona.open(filepath, driver="GML") as src:
            for feature in src:
                try:
                    geom = shape(feature["geometry"])
                    props = feature["properties"]
                    records.append({
                        "fid": feature.get("id"),
                        "theme": props.get("theme"),
                        "make": props.get("make"),
                        "physicalpresence": props.get("physicalpresence"),
                        "descriptivegroup": props.get("descriptivegroup"),
                        "descriptiveterm": props.get("descriptiveterm"),
                        "fclass": props.get("fclass"),
                        "geometry": wkb_dumps(geom, hex=True)
                    })
                except Exception as e:
                    print(f"⚠️ Skipping feature in {os.path.basename(filepath)}: {e}")
    except Exception as e:
        print(f"❌ Error reading {os.path.basename(filepath)}: {e}")
    return records

# --- Bulk Insert ---
def bulk_insert(engine, records):
    if not records:
        return 0
    stmt = text(f"""
        INSERT INTO {TABLE_NAME} (
            fid, theme, make, physicalpresence, descriptivegroup,
            descriptiveterm, fclass, geometry
        ) VALUES (
            :fid, :theme, :make, :physicalpresence, :descriptivegroup,
            :descriptiveterm, :fclass,
            ST_GeomFromWKB(decode(:geometry, 'hex'), 27700)
        )
    """)
    with engine.begin() as conn:
        for i in range(0, len(records), BATCH_SIZE):
            batch = records[i:i+BATCH_SIZE]
            conn.execute(stmt, batch)
    return len(records)

# --- Drop & Create Table ---
def recreate_table(engine):
    ddl = f"""
    DROP TABLE IF EXISTS {TABLE_NAME};
    CREATE TABLE {TABLE_NAME} (
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
    CREATE INDEX {TABLE_NAME}_geom_idx ON {TABLE_NAME} USING GIST (geometry);
    """
    with engine.begin() as conn:
        conn.execute(text(ddl))
    print(f"🧱 Recreated table `{TABLE_NAME}` with spatial index.")

# --- Ingest All Files ---
def load_all_gml(engine):
    files = collect_gml_files()
    print(f"📂 Found {len(files)} GML files under {GML_ROOT}")
    
    if not files:
        print("❌ No GML files found!")
        return
    
    total_features = 0
    processed_files = 0
    start_time = time.time()

    for fpath in files:
        try:
            print(f"Processing {os.path.basename(fpath)}...")
            records = process_gml_file(fpath)
            inserted = bulk_insert(engine, records)
            total_features += inserted
            processed_files += 1
            
            if processed_files % 10 == 0:
                print(f"  ✅ Processed {processed_files}/{len(files)} files, {total_features} features so far")
                
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(fpath)}: {e}")

    elapsed = time.time() - start_time
    print(f"\n✅ Done. Inserted {total_features} features from {processed_files} files in {elapsed:.1f} seconds.")
    
    # Quality check
    with engine.begin() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}"))
        final_count = result.scalar()
        print(f"📊 Final table count: {final_count} features")

# --- Main ---
def main():
    print("🗺️ Starting OS Open Map Local Fast Ingestion")
    print(f"Database: {DBNAME} on {HOST}:{PORT}")
    print(f"GML Root: {GML_ROOT}")
    
    engine = create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}")
    recreate_table(engine)
    load_all_gml(engine)

if __name__ == "__main__":
    main() 