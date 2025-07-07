import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import fiona
from shapely.geometry import shape
import geopandas as gpd
import logging
import sys
import os
from dotenv import load_dotenv
from backend.services.db_service import get_engine

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def ingest_gpkg_to_postgis(
    gpkg_path="data/osopenusrn_202507_gpkg/osopenusrn_202507.gpkg",
    layer_name="openUSRN",
    table_name="usrn_streets",
    dbname=None,
    progress_interval=10000,  # Log progress every 10,000 features
    chunk_size=10000          # Write to DB in chunks of 10,000
):
    if dbname:
        engine = get_engine(os.getenv("PGUSER"), os.getenv("PGPASSWORD"), os.getenv("PGHOST"), os.getenv("PGPORT"), dbname)
        logger.info(f"Using target database: {dbname}")
    else:
        engine = get_engine(os.getenv("PGUSER"), os.getenv("PGPASSWORD"), os.getenv("PGHOST"), os.getenv("PGPORT"), os.getenv("PGDATABASE"))
        logger.info("Using default database from environment or config.")

    try:
        logger.info(f"Opening GeoPackage '{gpkg_path}', layer '{layer_name}'")
        with fiona.open(gpkg_path, layer=layer_name) as src:
            crs = src.crs
            total = len(src)
            logger.info(f"Total features in layer: {total}")

            skipped = 0
            batch = []
            written = 0

            for i, feat in enumerate(src, 1):
                try:
                    geom = shape(feat['geometry'])
                    batch.append(feat)
                except Exception as e:
                    skipped += 1
                    logger.warning(f"Skipping invalid geometry at feature {i}: {e}")

                if len(batch) >= chunk_size or (i == total):
                    gdf = gpd.GeoDataFrame.from_features(batch, crs=crs)
                    logger.info(f"Writing batch {written//chunk_size + 1} to PostGIS ({len(gdf)} rows)...")
                    gdf.to_postgis(name=table_name, con=engine, if_exists='append' if written else 'replace', index=False, chunksize=chunk_size)
                    written += len(gdf)
                    batch = []
                    logger.info(f"Written {written} features so far...")

                if i % progress_interval == 0:
                    logger.info(f"Processed {i} features...")

            logger.info(f"Finished reading features. Skipped {skipped} invalid geometries.")
            logger.info(f"✅ Successfully loaded {written} rows into '{table_name}'")

    except Exception as e:
        logger.exception(f"Failed to ingest GeoPackage data: {e}")

if __name__ == "__main__":
    # CLI support for path, layer name, and optional dbname
    gpkg_path = sys.argv[1] if len(sys.argv) > 1 else "data/osopenusrn_202507_gpkg/osopenusrn_202507.gpkg"
    layer_name = sys.argv[2] if len(sys.argv) > 2 else "openUSRN"
    dbname = sys.argv[3] if len(sys.argv) > 3 else None
    ingest_gpkg_to_postgis(gpkg_path=gpkg_path, layer_name=layer_name, dbname=dbname)
