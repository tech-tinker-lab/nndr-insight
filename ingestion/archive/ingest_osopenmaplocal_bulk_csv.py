import os
import glob
import csv
import json
import fiona
from shapely.geometry import shape
from shapely.wkb import dumps as wkb_dumps
from dotenv import load_dotenv
import psycopg2

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

# --- Configuration ---
USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")
TABLE_NAME = "os_open_map_local"
GML_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'data', 'opmplc_gml3_gb', 'data')
CSV_FILE = os.path.join(os.path.dirname(__file__), 'os_open_map_local_bulk.csv')

# --- GML Collection ---
def collect_gml_files():
    return glob.glob(os.path.join(GML_ROOT, "*", "*.gml"))

# --- Parse GML Features and Write to CSV ---
def write_features_to_csv(csv_file, gml_files):
    fieldnames = ["fid", "gml_id", "feature_code", "geometry", "feature_type", "properties"]
    total_features = 0
    with open(csv_file, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for gml_path in gml_files:
            gfs_path = os.path.splitext(gml_path)[0] + ".gfs"
            if os.path.exists(gfs_path):
                print(f"✅ Found GFS file for {os.path.basename(gml_path)}: {os.path.basename(gfs_path)}")
            else:
                print(f"⚠️ No GFS file found for {os.path.basename(gml_path)}. Fiona/GDAL will infer schema.")
            print(f"Processing {os.path.basename(gml_path)}...")
            try:
                with fiona.open(gml_path, driver="GML") as src:
                    for feature in src:
                        try:
                            props = feature["properties"]
                            geom = feature["geometry"]
                            feature_type = feature.get('geometry', {}).get('type')
                            if not feature_type:
                                feature_type = props.get('featureType') or props.get('type')
                            fid = feature.get("id")
                            gml_id = props.get("gml_id")
                            feature_code = props.get("featureCode")
                            extra_props = {k: v for k, v in props.items() if k not in {"gml_id", "featureCode"}}
                            row = {
                                "fid": fid,
                                "gml_id": gml_id,
                                "feature_code": feature_code,
                                "geometry": wkb_dumps(shape(geom), hex=True) if geom else None,
                                "feature_type": feature_type,
                                "properties": json.dumps(extra_props, ensure_ascii=False)
                            }
                            writer.writerow(row)
                            total_features += 1
                        except Exception as e:
                            print(f"⚠️ Skipping feature in {os.path.basename(gml_path)}: {e}")
            except Exception as e:
                print(f"❌ Error reading {os.path.basename(gml_path)}: {e}")
    print(f"\n✅ Done. Wrote {total_features} features to {csv_file}")
    return total_features

# --- Bulk Load CSV into PostgreSQL ---
def bulk_load_csv_to_postgres(csv_file):
    print(f"\n🚀 Loading CSV into PostgreSQL using COPY...")
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST, port=PORT)
    cur = conn.cursor()
    # Drop and recreate table with expanded schema
    ddl = f"""
    DROP TABLE IF EXISTS {TABLE_NAME};
    CREATE TABLE {TABLE_NAME} (
        id SERIAL PRIMARY KEY,
        fid TEXT,
        gml_id TEXT,
        feature_code INTEGER,
        geometry geometry(Geometry, 27700),
        feature_type TEXT,
        properties JSONB
    );
    CREATE INDEX {TABLE_NAME}_geom_idx ON {TABLE_NAME} USING GIST (geometry);
    CREATE INDEX {TABLE_NAME}_feature_code_idx ON {TABLE_NAME} (feature_code);
    CREATE INDEX {TABLE_NAME}_feature_type_idx ON {TABLE_NAME} (feature_type);
    """
    cur.execute(ddl)
    conn.commit()
    # Use a staging table for geometry as text, then update
    copy_sql = f"""
    COPY {TABLE_NAME} (fid, gml_id, feature_code, geometry, feature_type, properties)
    FROM STDIN WITH (FORMAT csv, HEADER true)
    """
    with open(csv_file, "r", encoding="utf-8") as f:
        cur.copy_expert(copy_sql, f)
    conn.commit()
    print(f"✅ Bulk load complete.")
    cur.close()
    conn.close()

# --- Main ---
def main():
    print("🗺️ Starting OS Open Map Local Bulk CSV Ingestion")
    print(f"Database: {DBNAME} on {HOST}:{PORT}")
    print(f"GML Root: {GML_ROOT}")
    print(f"CSV Output: {CSV_FILE}")
    gml_files = collect_gml_files()
    print(f"📂 Found {len(gml_files)} GML files.")
    total = write_features_to_csv(CSV_FILE, gml_files)
    bulk_load_csv_to_postgres(CSV_FILE)
    print(f"\n🎉 All done! {total} features ingested.")

if __name__ == "__main__":
    main() 