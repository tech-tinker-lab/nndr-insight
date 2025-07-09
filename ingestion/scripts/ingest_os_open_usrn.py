#!/usr/bin/env python3
"""
OS Open USRN Staging-Only Ingestion Script
Loads OS Open USRN GPKG data into staging table only with client and source tracking
"""

import sys
import os
import logging
import argparse
import tempfile
import csv
from datetime import datetime
from dotenv import load_dotenv
import geopandas as gpd
from sqlalchemy import create_engine, text
from tqdm import tqdm

# Load .env file from db_setup directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'db_setup', '.env'))

USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")
STAGING_TABLE = "os_open_usrn_staging"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_connection():
    """Get database connection"""
    try:
        engine = create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}")
        return engine
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return None

def check_staging_table_exists():
    """Check if the staging table exists with correct schema"""
    logger.info("Checking if os_open_usrn_staging table exists with correct schema...")
    try:
        engine = get_connection()
        if not engine:
            return False
        
        with engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = '{STAGING_TABLE}'
                );
            """))
            exists = result.scalar()
            
            if not exists:
                logger.error(f"❌ Staging table '{STAGING_TABLE}' does not exist!")
                logger.error("Please run the database setup script to create the staging table.")
                return False
            
            # Check if geometry column is correct type
            result = conn.execute(text(f"""
                SELECT data_type, udt_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = '{STAGING_TABLE}' 
                AND column_name = 'geometry'
            """))
            geometry_info = result.fetchone()
            
            if not geometry_info or geometry_info[1] != 'geometry':
                logger.error(f"❌ Staging table '{STAGING_TABLE}' has wrong geometry column type!")
                logger.error("Expected: GEOMETRY(GEOMETRY, 27700)")
                logger.error(f"Found: {geometry_info[1] if geometry_info else 'TEXT'}")
                logger.error("Please run the database setup script to recreate the staging table.")
                return False
            
            logger.info("✅ Staging table exists with correct schema")
            return True
                
    except Exception as e:
        logger.error(f"Error checking staging table: {e}")
        return False

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='OS Open USRN Staging-Only Ingestion')
    
    # Required: GPKG file path
    parser.add_argument('--source-path', required=True, help='Path to GPKG file or directory')
    
    # Optional: Layer and processing options
    parser.add_argument('--layer', default="openUSRN", help='Layer name in GeoPackage')
    parser.add_argument('--max-rows', type=int, help='Maximum number of rows to process (for testing)')
    
    # Optional: Client and source information
    parser.add_argument('--client', help='Client identifier (e.g., "client_001", "internal_team")')
    parser.add_argument('--source', help='Source identifier (e.g., "OS_Open_USRN_2024")')
    parser.add_argument('--session-id', help='Session identifier for concurrent ingestion (auto-generated if not provided)')
    parser.add_argument('--batch-id', help='Batch identifier (auto-generated if not provided)')
    
    # Optional: Database override
    parser.add_argument('--dbname', help='Override database name from environment')
    
    return parser.parse_args()

def generate_identifiers(args):
    """Generate batch_id and session_id if not provided"""
    batch_id = args.batch_id or f"os_open_usrn_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    session_id = args.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return batch_id, session_id

def load_usrn_to_staging(gpkg_files, layer_name, batch_id, session_id, source_name, client_name, max_rows=None):
    """Load USRN data into staging table"""
    try:
        engine = get_connection()
        if not engine:
            return False, 0
        
        total_inserted = 0
        
        for gpkg_file in gpkg_files:
            if not os.path.isfile(gpkg_file):
                logger.error(f"Source file not found: {gpkg_file}")
                continue
            
            # Load GeoPackage data
            logger.info(f"Loading {gpkg_file}...")
            gdf = gpd.read_file(gpkg_file, layer=layer_name, on_invalid='ignore')
            logger.info(f"Loaded {len(gdf)} features from {gpkg_file} (invalid geometries ignored)")
            
            if len(gdf) == 0:
                logger.warning(f"No valid features found in {gpkg_file}")
                continue
            
            # Limit rows if max_rows is specified
            if max_rows is not None:
                original_count = len(gdf)
                gdf = gdf.head(max_rows)
                logger.info(f"Limited to {len(gdf)} rows (max_rows={max_rows})")
            
            # Add standard metadata columns
            file_size = os.path.getsize(gpkg_file)
            file_modified = datetime.fromtimestamp(os.path.getmtime(gpkg_file))
            file_name = os.path.basename(gpkg_file)
            
            gdf['source_name'] = source_name
            gdf['upload_user'] = USER
            gdf['upload_timestamp'] = datetime.now().isoformat()
            gdf['batch_id'] = batch_id
            gdf['source_file'] = file_name
            gdf['file_size'] = file_size
            gdf['file_modified'] = file_modified.isoformat()
            gdf['session_id'] = session_id
            gdf['client_name'] = client_name
            
            # Upload to staging table with progress bar
            logger.info(f"Uploading {len(gdf)} features to {STAGING_TABLE}...")
            try:
                # Ensure geometry column is properly set
                if 'geometry' in gdf.columns:
                    # Set CRS if not already set (assuming British National Grid)
                    if gdf.crs is None:
                        gdf.set_crs(epsg=27700, inplace=True)
                    elif gdf.crs.to_epsg() != 27700:
                        # Transform to British National Grid if needed
                        gdf = gdf.to_crs(epsg=27700)
                
                # Use chunked upload for large datasets to avoid memory issues
                chunk_size = 50000  # Process in chunks of 50K rows
                total_uploaded = 0
                
                # Calculate number of chunks for progress bar
                num_chunks = (len(gdf) + chunk_size - 1) // chunk_size
                
                with tqdm(total=num_chunks, desc=f"Uploading {file_name} (chunks)") as pbar:
                    for i in range(0, len(gdf), chunk_size):
                        chunk = gdf.iloc[i:i+chunk_size]
                        
                        # Upload chunk to PostGIS (uses client-side COPY internally)
                        chunk.to_postgis(name=STAGING_TABLE, con=engine, if_exists='append', index=False)
                        
                        total_uploaded += len(chunk)
                        pbar.update(1)
                        pbar.set_postfix({'Records': f"{total_uploaded:,}/{len(gdf):,}"})
                        
            except Exception as e:
                logger.error(f"❌ Failed to upload to PostGIS: {e}")
                logger.error("This might be due to:")
                logger.error("1. Staging table doesn't exist or has wrong schema")
                logger.error("2. Geometry column type mismatch")
                logger.error("3. CRS/SRID issues")
                logger.error("Please ensure the staging table is created with proper PostGIS geometry column")
                raise e
            
            total_inserted += len(gdf)
            
            # Stop if max_rows reached
            if max_rows is not None and total_inserted >= max_rows:
                logger.info(f"Reached max_rows={max_rows}, stopping early for testing.")
                break
        
        return True, total_inserted
        
    except Exception as e:
        logger.error(f"❌ Error during staging ingestion: {e}")
        return False, 0

def verify_staging_data(batch_id=None, session_id=None):
    """Verify the loaded staging data quality"""
    logger.info("Verifying USRN staging data quality...")
    
    try:
        engine = get_connection()
        if not engine:
            return False
        
        with engine.connect() as conn:
            # Build WHERE clause for specific batch/session if provided
            where_clause = ""
            params = {}
            if batch_id and session_id:
                where_clause = "WHERE batch_id = :batch_id AND session_id = :session_id"
                params = {"batch_id": batch_id, "session_id": session_id}
            elif batch_id:
                where_clause = "WHERE batch_id = :batch_id"
                params = {"batch_id": batch_id}
            
            # Check total count
            result = conn.execute(text(f"SELECT COUNT(*) FROM {STAGING_TABLE} {where_clause}"), params)
            total_count = result.scalar()
            
            # Check for empty USRNs
            result = conn.execute(text(f"SELECT COUNT(*) FROM {STAGING_TABLE} {where_clause} AND (usrn IS NULL OR usrn = '')"), params)
            null_usrn_count = result.scalar()
            
            logger.info("=" * 60)
            logger.info("USRN STAGING DATA QUALITY REPORT")
            logger.info("=" * 60)
            logger.info(f"Total records: {total_count:,}")
            logger.info(f"Null USRNs: {null_usrn_count}")
            logger.info(f"Valid records: {total_count - null_usrn_count:,}")
            if batch_id:
                logger.info(f"Batch ID: {batch_id}")
            if session_id:
                logger.info(f"Session ID: {session_id}")
            logger.info("=" * 60)
            
            return True
            
    except Exception as e:
        logger.error(f"Error during data quality verification: {e}")
        return False

def main():
    """Main execution function"""
    # Parse arguments
    args = parse_arguments()
    
    # Override database if specified
    if args.dbname:
        global DBNAME
        DBNAME = args.dbname
    
    # Generate identifiers
    batch_id, session_id = generate_identifiers(args)
    
    # Get source and client names
    source_name = args.source or "OS_Open_USRN_DEFAULT"
    client_name = args.client or "default_client"
    layer_name = args.layer
    
    # Determine if source-path is a file or directory
    if os.path.isdir(args.source_path):
        gpkg_files = [os.path.join(args.source_path, f) for f in os.listdir(args.source_path) if f.lower().endswith('.gpkg')]
        if not gpkg_files:
            logger.error(f"No GPKG files found in directory: {args.source_path}")
            sys.exit(1)
    elif os.path.isfile(args.source_path) and args.source_path.lower().endswith('.gpkg'):
        gpkg_files = [args.source_path]
    else:
        logger.error(f"source-path is not a valid GPKG file or directory: {args.source_path}")
        sys.exit(1)
    
    # Log file metadata
    if len(gpkg_files) == 1:
        logger.info(f"File path: {gpkg_files[0]}")
        logger.info(f"File size: {os.path.getsize(gpkg_files[0])}")
        logger.info(f"File modified: {datetime.fromtimestamp(os.path.getmtime(gpkg_files[0]))}")
    else:
        logger.info(f"Number of files: {len(gpkg_files)}")
        total_size = sum(os.path.getsize(f) for f in gpkg_files)
        logger.info(f"Total size of all files: {total_size}")
    
    logger.info("=" * 60)
    logger.info("OS OPEN USRN STAGING-ONLY INGESTION")
    logger.info("=" * 60)
    logger.info(f"GPKG files: {gpkg_files}")
    logger.info(f"Layer: {layer_name}")
    logger.info(f"Staging table: {STAGING_TABLE}")
    logger.info(f"Source: {source_name}")
    logger.info(f"Client: {client_name}")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Batch ID: {batch_id}")
    logger.info("=" * 60)
    
    try:
        # Step 1: Check and fix staging table if needed
        if not check_staging_table_exists():
            sys.exit(1)

        # Step 2: Load data into staging table
        success, rowcount = load_usrn_to_staging(
            gpkg_files, layer_name, batch_id, session_id, source_name, client_name, max_rows=args.max_rows
        )
        
        if success:
            # Verify staging data quality
            verify_staging_data(batch_id, session_id)
            logger.info("✅ USRN staging ingestion completed successfully!")
            logger.info(f"📊 Data loaded into staging table with batch_id: {batch_id}")
        else:
            logger.error("❌ Data loading failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
