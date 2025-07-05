import os
import glob
import time
import fiona
import sqlalchemy
from sqlalchemy import text, create_engine
from shapely.geometry import shape
from shapely.wkb import dumps as wkb_dumps
from tqdm import tqdm

# --- Configuration ---
USER = "nndr"
PASSWORD = "nndrpass"
HOST = "localhost"
PORT = "5432"
DBNAME = "nndr_db"
TABLE_NAME = "os_open_map_local"
BATCH_SIZE = 500

GML_ROOT = "data/opmplc_gml3_gb/data"

# --- GML Collection ---
def collect_gml_files():
    return glob.glob(os.path.join(GML_ROOT, "**", "*.gml"), recursive=True)

# --- Parse GML Features ---
def process_gml_file(filepath):
    records = []
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
                print(f"⚠️ Skipping feature in {filepath}: {e}")
    return records

# --- Bulk Insert ---
def bulk_insert(engine, records):
    if not records:
        return
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
    total_features = 0
    start_time = time.time()

    for fpath in tqdm(files, desc="🗺️ Ingesting GML tiles"):
        try:
            records = process_gml_file(fpath)
            bulk_insert(engine, records)
            total_features += len(records)
        except Exception as e:
            print(f"❌ Error processing {fpath}: {e}")

    elapsed = time.time() - start_time
    print(f"\n✅ Done. Inserted {total_features} features in {elapsed:.1f} seconds.")

# --- Main ---
def main():
    engine = create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}")
    recreate_table(engine)
    load_all_gml(engine)

if __name__ == "__main__":
    main()
