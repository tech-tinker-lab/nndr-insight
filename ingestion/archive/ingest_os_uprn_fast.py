#!/usr/bin/env python3
"""
Fast OS UPRN Data Ingestion Script
Drops and recreates os_open_uprn table with only necessary columns
Uses COPY for fast bulk insertion without duplicate checking
"""

import psycopg2
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

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

def get_connection():
    """Get database connection"""
    return psycopg2.connect(
        dbname=DBNAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )

def drop_and_recreate_uprn_table():
    """Drop and recreate os_open_uprn table with only necessary columns"""
    logger.info("Dropping and recreating os_open_uprn table...")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Drop the table if it exists
                cur.execute("DROP TABLE IF EXISTS os_open_uprn CASCADE;")
                logger.info("Dropped existing os_open_uprn table")
                
                # Create new table with only OS UPRN data columns
                create_table_sql = """
                CREATE TABLE os_open_uprn (
                    uprn BIGINT PRIMARY KEY,
                    x_coordinate NUMERIC(10,3),
                    y_coordinate NUMERIC(10,3),
                    latitude NUMERIC(10,8),
                    longitude NUMERIC(11,8)
                );
                """
                cur.execute(create_table_sql)
                logger.info("Created new os_open_uprn table with simplified schema")
                
                # Create indexes for performance
                cur.execute("CREATE INDEX idx_os_open_uprn_coords ON os_open_uprn(x_coordinate, y_coordinate);")
                cur.execute("CREATE INDEX idx_os_open_uprn_latlong ON os_open_uprn(latitude, longitude);")
                logger.info("Created indexes for performance")
                
                conn.commit()
                logger.info("Table recreation completed successfully")
                
    except Exception as e:
        logger.error(f"Error recreating table: {e}")
        raise

def load_uprn_data(csv_path):
    """Load UPRN data using fast COPY operation"""
    if not os.path.isfile(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        return False

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                logger.info(f"Starting bulk load from {csv_path} into os_open_uprn...")
                
                # Preview first few lines to verify format
                with open(csv_path, 'r', encoding='utf-8') as f:
                    header = f.readline().strip()
                    first_data = f.readline().strip()
                    logger.info(f'Header: {header}')
                    logger.info(f'First data row: {first_data}')
                
                # Use COPY for fast bulk insertion
                with open(csv_path, 'r', encoding='utf-8') as f:
                    copy_sql = """
                        COPY os_open_uprn (uprn, x_coordinate, y_coordinate, latitude, longitude)
                        FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
                    """
                    cur.copy_expert(sql=copy_sql, file=f)
                    conn.commit()

                # Get record count
                cur.execute("SELECT COUNT(*) FROM os_open_uprn;")
                rowcount = cur.fetchone()[0]
                logger.info(f"Successfully loaded {rowcount} records into os_open_uprn")
                
                return True

    except Exception as e:
        logger.error(f"Error during data load: {e}")
        return False

def verify_data_quality():
    """Verify the loaded data quality"""
    logger.info("Verifying data quality...")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Check total count
                cur.execute("SELECT COUNT(*) FROM os_open_uprn;")
                total_count = cur.fetchone()[0]
                
                # Check for null UPRNs
                cur.execute("SELECT COUNT(*) FROM os_open_uprn WHERE uprn IS NULL;")
                null_uprn_count = cur.fetchone()[0]
                
                # Check for duplicate UPRNs (should be 0 due to PRIMARY KEY)
                cur.execute("""
                    SELECT COUNT(*) FROM (
                        SELECT uprn, COUNT(*) 
                        FROM os_open_uprn 
                        GROUP BY uprn 
                        HAVING COUNT(*) > 1
                    ) as duplicates;
                """)
                duplicate_count = cur.fetchone()[0]
                
                # Check coordinate ranges
                cur.execute("""
                    SELECT 
                        MIN(x_coordinate) as min_x, MAX(x_coordinate) as max_x,
                        MIN(y_coordinate) as min_y, MAX(y_coordinate) as max_y,
                        MIN(latitude) as min_lat, MAX(latitude) as max_lat,
                        MIN(longitude) as min_lon, MAX(longitude) as max_lon
                    FROM os_open_uprn;
                """)
                coord_ranges = cur.fetchone()
                
                logger.info("=" * 60)
                logger.info("DATA QUALITY REPORT")
                logger.info("=" * 60)
                logger.info(f"Total records: {total_count:,}")
                logger.info(f"Null UPRNs: {null_uprn_count}")
                logger.info(f"Duplicate UPRNs: {duplicate_count}")
                logger.info(f"X coordinate range: {coord_ranges[0]:.3f} to {coord_ranges[1]:.3f}")
                logger.info(f"Y coordinate range: {coord_ranges[2]:.3f} to {coord_ranges[3]:.3f}")
                logger.info(f"Latitude range: {coord_ranges[4]:.8f} to {coord_ranges[5]:.8f}")
                logger.info(f"Longitude range: {coord_ranges[6]:.8f} to {coord_ranges[7]:.8f}")
                logger.info("=" * 60)
                
                return True
                
    except Exception as e:
        logger.error(f"Error during data quality verification: {e}")
        return False

def main():
    """Main execution function"""
    # Default CSV path
    default_path = "backend/data/osopenuprn_202506_csv/osopenuprn_202506.csv"
    csv_file = sys.argv[1] if len(sys.argv) > 1 else default_path
    
    if len(sys.argv) < 2:
        logger.info(f"No CSV file path provided; using default: {default_path}")
    
    logger.info("=" * 60)
    logger.info("FAST OS UPRN DATA INGESTION")
    logger.info("=" * 60)
    logger.info(f"CSV file: {csv_file}")
    logger.info("=" * 60)
    
    try:
        # Step 1: Drop and recreate table
        drop_and_recreate_uprn_table()
        
        # Step 2: Load data using fast COPY
        if load_uprn_data(csv_file):
            # Step 3: Verify data quality
            verify_data_quality()
            logger.info("✅ OS UPRN data ingestion completed successfully!")
        else:
            logger.error("❌ Data loading failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 