import geopandas as gpd
import sys
import psycopg2
import os
import logging
import argparse
import uuid
from datetime import datetime
from sqlalchemy import create_engine
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(path):
        pass  # Fallback if dotenv not available
from tqdm import tqdm

# Load .env file from db_setup directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'db_setup', '.env'))

# Database configuration
USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Target table name
STAGING_TABLE = "lad_boundaries_staging"

def get_connection():
    """Get database connection"""
    return psycopg2.connect(
        dbname=DBNAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )

def get_engine():
    """Get SQLAlchemy engine for GeoPandas"""
    return create_engine(f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}')

def check_staging_table_exists():
    """Check if the staging table exists"""
    logger.info("Checking if lad_boundaries_staging table exists...")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Check if table exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'lad_boundaries_staging'
                    );
                """)
                result = cur.fetchone()
                table_exists = result[0] if result else False
                
                if not table_exists:
                    logger.error("❌ Table 'lad_boundaries_staging' does not exist!")
                    logger.error("Please create the table first using database setup scripts.")
                    return False
                
                logger.info("✅ Staging table exists")
                return True
                
    except Exception as e:
        logger.error(f"Error checking staging table: {e}")
        return False

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='LAD Boundaries Staging Ingestion')
    parser.add_argument('--source-path', required=True, help='Path to shapefile or directory containing shapefiles')
    parser.add_argument('--source', help='Source identifier (e.g., "LAD_2025")')
    parser.add_argument('--client', help='Client identifier (e.g., "client_001")')
    parser.add_argument('--session-id', help='Session identifier for concurrent ingestion (auto-generated if not provided)')
    parser.add_argument('--batch-id', help='Batch identifier (auto-generated if not provided)')
    parser.add_argument('--dbname', help='Override database name from environment')
    args = parser.parse_args()

    # Override database if specified
    if args.dbname:
        global DBNAME
        DBNAME = args.dbname

    # Generate identifiers
    batch_id = args.batch_id or f"lad_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    session_id = args.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    source_name = args.source or "LAD_BOUNDARIES_2025"
    client_name = args.client or "default_client"

    # Determine if source-path is a file or directory
    if os.path.isdir(args.source_path):
        shapefiles = [f for f in os.listdir(args.source_path) if f.lower().endswith('.shp')]
        if not shapefiles:
            logger.error(f"No shapefiles found in directory: {args.source_path}")
            sys.exit(1)
        shapefile_path = os.path.join(args.source_path, shapefiles[0])
    elif os.path.isfile(args.source_path):
        shapefile_path = args.source_path
    else:
        logger.error(f"source-path is not a valid file or directory: {args.source_path}")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("LAD BOUNDARIES STAGING INGESTION")
    logger.info("=" * 60)
    logger.info(f"Staging table: {STAGING_TABLE}")
    logger.info(f"Source path: {shapefile_path}")
    logger.info(f"Batch ID: {batch_id}")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Source: {source_name}")
    logger.info(f"Client: {client_name}")
    logger.info("=" * 60)

    try:
        # Step 1: Check if staging table exists
        if not check_staging_table_exists():
            sys.exit(1)

        # Step 2: Load and process shapefile
        logger.info(f"📂 Loading shapefile: {shapefile_path}")
        logger.info(f"File size: {os.path.getsize(shapefile_path)} bytes")
        logger.info(f"File modified: {datetime.fromtimestamp(os.path.getmtime(shapefile_path))}")
        
        gdf = gpd.read_file(shapefile_path)
        logger.info(f"✅ Loaded {len(gdf)} records with columns: {list(gdf.columns)}")
        logger.info(f"🧭 Original CRS: {gdf.crs}")
        
        # Reproject to British National Grid if needed
        if gdf.crs is not None and gdf.crs.to_epsg() != 27700:
            gdf = gdf.to_crs(epsg=27700)
            logger.info("🔁 Reprojected to EPSG:27700 (British National Grid)")

        # Add metadata columns
        gdf['source_name'] = source_name
        gdf['upload_user'] = USER
        gdf['upload_timestamp'] = datetime.now().isoformat()
        gdf['batch_id'] = batch_id
        gdf['source_file'] = os.path.basename(shapefile_path)
        gdf['file_size'] = os.path.getsize(shapefile_path)
        gdf['file_modified'] = datetime.fromtimestamp(os.path.getmtime(shapefile_path)).isoformat()
        gdf['session_id'] = session_id
        gdf['client_name'] = client_name

        # Step 3: Load data into staging table
        logger.info(f"📊 Loading {len(gdf)} records into {STAGING_TABLE}...")
        
        # Convert geometry to WKT for staging table
        gdf['geometry'] = gdf['geometry'].astype(str)
        
        # Prepare data for insertion
        data_to_insert = []
        for _, row in gdf.iterrows():
            data_to_insert.append((
                row.get('LAD25CD', ''),  # lad_code
                row.get('LAD25NM', ''),  # lad_name
                row.get('geometry', ''),  # geometry as WKT
                row.get('source_name', ''),
                row.get('upload_user', ''),
                row.get('upload_timestamp', ''),
                row.get('batch_id', ''),
                row.get('source_file', ''),
                row.get('file_size', 0),
                row.get('file_modified', ''),
                row.get('session_id', ''),
                row.get('client_name', '')
            ))
        
        # Upload in chunks with progress bar
        chunk_size = 50  # Process 50 records at a time
        with tqdm(total=len(data_to_insert), desc="Uploading LAD boundaries") as pbar:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    for i in range(0, len(data_to_insert), chunk_size):
                        chunk = data_to_insert[i:i + chunk_size]
                        
                        # Insert chunk
                        cur.executemany("""
                            INSERT INTO lad_boundaries_staging (
                                lad_code, lad_name, geometry, source_name, upload_user,
                                upload_timestamp, batch_id, source_file, file_size,
                                file_modified, session_id, client_name
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, chunk)
                        
                        # Update progress bar
                        pbar.update(len(chunk))
                        
                        # Commit every chunk
                        conn.commit()

        # Step 4: Verify data quality
        verify_staging_data_quality(batch_id, session_id, client_name)
        
        logger.info("✅ LAD Boundaries staging ingestion completed successfully!")
        logger.info(f"📊 Data loaded into staging table with batch_id: {batch_id}")
            
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        sys.exit(1)

def verify_staging_data_quality(batch_id=None, session_id=None, client_name=None):
    """Verify the loaded staging data quality"""
    logger.info("Verifying staging data quality...")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Build WHERE clause for specific batch/session if provided
                where_clause = ""
                params = []
                if batch_id and session_id and client_name:
                    where_clause = "WHERE batch_id = %s AND session_id = %s AND client_name = %s"
                    params = [batch_id, session_id, client_name]
                elif batch_id and session_id:
                    where_clause = "WHERE batch_id = %s AND session_id = %s"
                    params = [batch_id, session_id]
                elif batch_id:
                    where_clause = "WHERE batch_id = %s"
                    params = [batch_id]
                
                # Check total count
                cur.execute(f"SELECT COUNT(*) FROM {STAGING_TABLE} {where_clause};", params)
                total_count_result = cur.fetchone()
                total_count = total_count_result[0] if total_count_result else 0
                
                # Check for null geometries
                cur.execute(f"SELECT COUNT(*) FROM {STAGING_TABLE} {where_clause} AND geometry IS NULL;", params)
                null_geom_result = cur.fetchone()
                null_geom_count = null_geom_result[0] if null_geom_result else 0
                
                logger.info("=" * 60)
                logger.info("LAD BOUNDARIES STAGING DATA QUALITY REPORT")
                logger.info("=" * 60)
                logger.info(f"Total records: {total_count:,}")
                logger.info(f"Null geometries: {null_geom_count}")
                logger.info(f"Valid records: {total_count - null_geom_count:,}")
                if batch_id:
                    logger.info(f"Batch ID: {batch_id}")
                if session_id:
                    logger.info(f"Session ID: {session_id}")
                if client_name:
                    logger.info(f"Client: {client_name}")
                logger.info("=" * 60)
                
                return True
                
    except Exception as e:
        logger.error(f"Error during data quality verification: {e}")
        return False

if __name__ == "__main__":
    main()
