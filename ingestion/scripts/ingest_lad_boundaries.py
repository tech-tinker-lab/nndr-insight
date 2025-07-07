import geopandas as gpd
import sys
from sqlalchemy import text
from services.db_service import get_engine
import os
from dotenv import load_dotenv

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

USER = os.getenv("PGUSER", "")
PASSWORD = os.getenv("PGPASSWORD", "")
HOST = os.getenv("PGHOST", "")
PORT = os.getenv("PGPORT", "")
DBNAME = os.getenv("PGDATABASE", "")

# Path to LAD shapefile (.shp)
SHAPEFILE = "data/LAD_MAY_2025_UK_BFC.shp"

# Target table name
TABLE_NAME = "lad_boundaries_2025"

def main():
    # Allow target DB to be passed as a command-line argument
    dbname = sys.argv[1] if len(sys.argv) > 1 else None
    if dbname:
        engine = get_engine(USER, PASSWORD, HOST, PORT, dbname)
        print(f"Using target database: {dbname}")
    else:
        engine = get_engine(USER, PASSWORD, HOST, PORT, DBNAME)
        print("Using default database from environment or config.")

    # Read shapefile with GeoPandas
    print(f"📂 Loading shapefile: {SHAPEFILE}")
    gdf = gpd.read_file(SHAPEFILE)

    print(f"✅ Loaded {len(gdf)} records with columns: {list(gdf.columns)}")
    print("🧭 Original CRS:", gdf.crs)

    # Convert to British National Grid (EPSG:27700) if needed
    if gdf.crs is not None and gdf.crs.to_epsg() != 27700:
        gdf = gdf.to_crs(epsg=27700)
        print("🔁 Reprojected to EPSG:27700 (British National Grid)")

    # Drop & create table
    # with engine.begin() as conn:
    #     conn.execute(text(f"DROP TABLE IF EXISTS {TABLE_NAME};"))
    # print(f"🧱 Dropped old table `{TABLE_NAME}` (if existed)")

    # Write to PostGIS (this will auto-create schema)
    gdf.to_postgis(TABLE_NAME, engine, if_exists="replace", index=False)

    # Create spatial index
    with engine.begin() as conn:
        conn.execute(text(f"CREATE INDEX {TABLE_NAME}_geom_idx ON {TABLE_NAME} USING GIST (geometry);"))
    print(f"✅ Ingested {len(gdf)} LAD boundaries into `{TABLE_NAME}` with spatial index.")

if __name__ == "__main__":
    main()
