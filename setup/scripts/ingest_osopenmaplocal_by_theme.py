import os
import glob
import time
import fiona
import sqlalchemy
from sqlalchemy import text, create_engine
from shapely.geometry import shape
from shapely.wkb import dumps as wkb_dumps
from collections import defaultdict
from tqdm import tqdm

# Database config
USER = "nndr"
PASSWORD = "nndrpass"
HOST = "localhost"
PORT = "5432"
DBNAME = "nndr_db"
BATCH_SIZE = 500

# GML source root
GML_ROOT = "data/opmplc_gml3_gb/data"

# Collect all GML file paths
def collect_gml_files():
    return glob.glob(os.path.join(GML_ROOT, "**", "*.gml"), recursive=True)

# Extract records from a GML file and group by theme
def process_gml_file(filepath):
    themed_records = defaultdict(list)

    with fiona.open(filepath, driver="GML") as src:
        for feature in src:
            try:
                geom = shape(feature["geometry"])
                props = feature["properties"]
                theme = (props.get("theme") or "unknown").lower().replace(" ", "_")

                record = {
                    "fid": feature.get("id"),
                    "theme": props.get("theme"),
                    "make": props.get("make"),
                    "physicalpresence": props.get("physicalpresence"),
                    "descriptivegroup": props.get("descriptivegroup"),
                    "descriptiveterm": props.get("descriptiveterm"),
                    "fclass": props.get("fclass"),
                    "geometry": wkb_dumps(geom, hex=True)
                }

                themed_records[theme].append(record)

            except Exception as e:
                print(f"⚠️ Skipping feature in {filepath}: {e}")
    return themed_records

# Create table if not already seen
def ensure_table(engine, theme):
    table_name = f"os_oml_{theme}"
    ddl = f"""
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
    """
    with engine.begin() as conn:
        conn.execute(text(ddl))
    print(f"🧱 Created table `{table_name}`")

# Insert records into a themed table
def bulk_insert(engine, theme, records):
    if not records:
        return
    table_name = f"os_oml_{theme}"
    stmt = text(f"""
        INSERT INTO {table_name} (
            fid, theme, make, physicalpresence,
            descriptivegroup, descriptiveterm, fclass, geometry
        ) VALUES (
            :fid, :theme, :make, :physicalpresence,
            :descriptivegroup, :descriptiveterm, :fclass,
            ST_GeomFromWKB(decode(:geometry, 'hex'), 27700)
        )
    """)
    with engine.begin() as conn:
        for i in range(0, len(records), BATCH_SIZE):
            batch = records[i:i+BATCH_SIZE]
            conn.execute(stmt, batch)

# Load all GML files, grouped by theme
def load_all_gml(engine):
    files = collect_gml_files()
    print(f"📂 Found {len(files)} GML files under {GML_ROOT}")
    start_time = time.time()

    tables_created = set()
    totals = defaultdict(int)

    for fpath in tqdm(files, desc="🗺️ Ingesting GML tiles"):
        try:
            themed_data = process_gml_file(fpath)
            for theme, records in themed_data.items():
                if theme not in tables_created:
                    ensure_table(engine, theme)
                    tables_created.add(theme)
                bulk_insert(engine, theme, records)
                totals[theme] += len(records)
        except Exception as e:
            print(f"❌ Error processing {fpath}: {e}")

    elapsed = time.time() - start_time
    print("\n✅ Ingestion complete.")
    for theme, count in sorted(totals.items()):
        print(f"  📌 {theme}: {count} features")

    print(f"⏱️ Total time: {elapsed:.1f} seconds")

# Main entry point
def main():
    engine = create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}")
    load_all_gml(engine)

if __name__ == "__main__":
    main()
