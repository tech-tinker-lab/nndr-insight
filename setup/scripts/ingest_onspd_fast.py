#!/usr/bin/env python3
"""
Fast ONSPD Data Ingestion Script
Drops and recreates onspd table with only necessary columns
Uses COPY for fast bulk insertion without staging table
"""

import psycopg2
import os
import sys
import logging
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

def drop_and_recreate_onspd_table():
    """Drop and recreate onspd table with only necessary columns"""
    logger.info("Dropping and recreating onspd table...")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Drop the table if it exists
                cur.execute("DROP TABLE IF EXISTS onspd CASCADE;")
                logger.info("Dropped existing onspd table")
                
                # Create new table with only ONSPD data columns we need
                create_table_sql = """
                CREATE TABLE onspd (
                    pcds TEXT PRIMARY KEY,
                    pcd TEXT,
                    lat NUMERIC(10,6),
                    long NUMERIC(10,6),
                    ctry TEXT,
                    oslaua TEXT,
                    osward TEXT,
                    parish TEXT,
                    oa11 TEXT,
                    lsoa11 TEXT,
                    msoa11 TEXT,
                    imd TEXT,
                    rgn TEXT,
                    pcon TEXT,
                    ur01ind TEXT,
                    oac11 TEXT,
                    oseast1m TEXT,
                    osnrth1m TEXT,
                    dointr TEXT,
                    doterm TEXT
                );
                """
                cur.execute(create_table_sql)
                logger.info("Created new onspd table with simplified schema")
                
                # Create indexes for performance
                cur.execute("CREATE INDEX idx_onspd_coords ON onspd(lat, long);")
                cur.execute("CREATE INDEX idx_onspd_country ON onspd(ctry);")
                cur.execute("CREATE INDEX idx_onspd_admin ON onspd(oslaua);")
                cur.execute("CREATE INDEX idx_onspd_oa ON onspd(oa11);")
                logger.info("Created indexes for performance")
                
                conn.commit()
                logger.info("Table recreation completed successfully")
                
    except Exception as e:
        logger.error(f"Error recreating table: {e}")
        raise

def load_onspd_data(csv_path):
    """Load ONSPD data using fast COPY operation with staging table"""
    if not os.path.isfile(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        return False

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                logger.info(f"Starting bulk load from {csv_path} into onspd...")
                
                # Create staging table with all columns
                logger.info("Creating staging table...")
                cur.execute("DROP TABLE IF EXISTS onspd_staging;")
                staging_schema = """
                CREATE TABLE onspd_staging (
                    x TEXT, y TEXT, objectid TEXT, pcd TEXT, pcd2 TEXT, pcds TEXT,
                    dointr TEXT, doterm TEXT, oscty TEXT, ced TEXT, oslaua TEXT,
                    osward TEXT, parish TEXT, usertype TEXT, oseast1m TEXT, osnrth1m TEXT,
                    osgrdind TEXT, oshlthau TEXT, nhser TEXT, ctry TEXT, rgn TEXT,
                    streg TEXT, pcon TEXT, eer TEXT, teclec TEXT, ttwa TEXT, pct TEXT,
                    itl TEXT, statsward TEXT, oa01 TEXT, casward TEXT, npark TEXT,
                    lsoa01 TEXT, msoa01 TEXT, ur01ind TEXT, oac01 TEXT, oa11 TEXT,
                    lsoa11 TEXT, msoa11 TEXT, wz11 TEXT, sicbl TEXT, bua24 TEXT,
                    ru11ind TEXT, oac11 TEXT, lat TEXT, long TEXT, lep1 TEXT, lep2 TEXT,
                    pfa TEXT, imd TEXT, calncv TEXT, icb TEXT, oa21 TEXT, lsoa21 TEXT,
                    msoa21 TEXT, ruc21ind TEXT, globalid TEXT
                );
                """
                cur.execute(staging_schema)
                
                # Preview first few lines to verify format
                with open(csv_path, 'r', encoding='utf-8') as f:
                    first_data = f.readline().strip()
                    second_data = f.readline().strip()
                    logger.info(f'First data row: {first_data}')
                    logger.info(f'Second data row: {second_data}')
                
                # Use COPY for fast bulk insertion into staging
                with open(csv_path, 'r', encoding='utf-8') as f:
                    copy_sql = """
                        COPY onspd_staging FROM STDIN WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE)
                    """
                    cur.copy_expert(sql=copy_sql, file=f)
                    conn.commit()
                
                # Move selected columns from staging to final table
                logger.info("Moving data from staging to final table...")
                cur.execute("""
                    INSERT INTO onspd (pcds, pcd, lat, long, ctry, oslaua, osward, parish,
                                      oa11, lsoa11, msoa11, imd, rgn, pcon, ur01ind, oac11,
                                      oseast1m, osnrth1m, dointr, doterm)
                    SELECT pcds, pcd, 
                           NULLIF(lat, '')::NUMERIC, 
                           NULLIF(long, '')::NUMERIC, 
                           ctry, oslaua, osward, parish,
                           oa11, lsoa11, msoa11, imd, rgn, pcon, ur01ind, oac11,
                           oseast1m, osnrth1m, dointr, doterm
                    FROM onspd_staging
                    WHERE pcds IS NOT NULL;
                """)
                conn.commit()
                
                # Clean up staging table
                cur.execute("DROP TABLE onspd_staging;")
                conn.commit()

                # Get record count
                cur.execute("SELECT COUNT(*) FROM onspd;")
                rowcount = cur.fetchone()[0]
                logger.info(f"Successfully loaded {rowcount} records into onspd")
                
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
                cur.execute("SELECT COUNT(*) FROM onspd;")
                total_count = cur.fetchone()[0]
                
                # Check for null postcodes
                cur.execute("SELECT COUNT(*) FROM onspd WHERE pcds IS NULL;")
                null_postcode_count = cur.fetchone()[0]
                
                # Check for duplicate postcodes (should be 0 due to PRIMARY KEY)
                cur.execute("""
                    SELECT COUNT(*) FROM (
                        SELECT pcds, COUNT(*) 
                        FROM onspd 
                        GROUP BY pcds 
                        HAVING COUNT(*) > 1
                    ) as duplicates;
                """)
                duplicate_count = cur.fetchone()[0]
                
                # Check coordinate ranges
                cur.execute("""
                    SELECT 
                        MIN(lat) as min_lat, MAX(lat) as max_lat,
                        MIN(long) as min_long, MAX(long) as max_long
                    FROM onspd;
                """)
                coord_ranges = cur.fetchone()
                
                # Check country distribution
                cur.execute("""
                    SELECT ctry, COUNT(*) 
                    FROM onspd 
                    GROUP BY ctry 
                    ORDER BY COUNT(*) DESC;
                """)
                country_distribution = cur.fetchall()
                
                # Check administrative area distribution
                cur.execute("""
                    SELECT COUNT(DISTINCT oslaua) as unique_lad_count
                    FROM onspd;
                """)
                lad_count = cur.fetchone()[0]
                
                logger.info("=" * 60)
                logger.info("DATA QUALITY REPORT")
                logger.info("=" * 60)
                logger.info(f"Total records: {total_count:,}")
                logger.info(f"Null postcodes: {null_postcode_count}")
                logger.info(f"Duplicate postcodes: {duplicate_count}")
                logger.info(f"Latitude range: {coord_ranges[0]:.6f} to {coord_ranges[1]:.6f}")
                logger.info(f"Longitude range: {coord_ranges[2]:.6f} to {coord_ranges[3]:.6f}")
                logger.info(f"Unique Local Authority Districts: {lad_count}")
                logger.info("Country distribution:")
                for country, count in country_distribution:
                    logger.info(f"  {country}: {count:,} records")
                logger.info("=" * 60)
                
                return True
                
    except Exception as e:
        logger.error(f"Error during data quality verification: {e}")
        return False

def main():
    """Main execution function"""
    # Default path (relative to setup/scripts directory)
    default_file = "../../backend/data/ONSPD_Online_Latest_Centroids.csv"
    
    # Check command line arguments
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = default_file
    
    logger.info("=" * 60)
    logger.info("FAST ONSPD DATA INGESTION")
    logger.info("=" * 60)
    logger.info(f"CSV file: {csv_file}")
    logger.info("=" * 60)
    
    try:
        # Step 1: Drop and recreate table
        drop_and_recreate_onspd_table()
        
        # Step 2: Load data using fast COPY
        success = load_onspd_data(csv_file)
        
        if success:
            # Step 3: Verify data quality
            verify_data_quality()
            logger.info("✅ ONSPD data ingestion completed successfully!")
        else:
            logger.error("❌ Data loading failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 