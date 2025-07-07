#!/usr/bin/env python3
"""
Fast CodePoint Open Data Ingestion Script
Drops and recreates code_point_open table with only necessary columns
Uses COPY for fast bulk insertion without duplicate checking
"""

import psycopg2
import os
import sys
import logging
import glob
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

def drop_and_recreate_codepoint_table():
    """Drop and recreate code_point_open table with only necessary columns"""
    logger.info("Dropping and recreating code_point_open table...")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Drop the table if it exists
                cur.execute("DROP TABLE IF EXISTS code_point_open CASCADE;")
                logger.info("Dropped existing code_point_open table")
                
                # Create new table with only CodePoint data columns
                create_table_sql = """
                CREATE TABLE code_point_open (
                    postcode TEXT PRIMARY KEY,
                    positional_quality_indicator INTEGER,
                    easting NUMERIC(10,3),
                    northing NUMERIC(10,3),
                    country_code VARCHAR(20),
                    nhs_regional_ha_code VARCHAR(20),
                    nhs_ha_code VARCHAR(20),
                    admin_county_code VARCHAR(20),
                    admin_district_code VARCHAR(20),
                    admin_ward_code VARCHAR(20)
                );
                """
                cur.execute(create_table_sql)
                logger.info("Created new code_point_open table with simplified schema")
                
                # Create indexes for performance
                cur.execute("CREATE INDEX idx_code_point_open_coords ON code_point_open(easting, northing);")
                cur.execute("CREATE INDEX idx_code_point_open_country ON code_point_open(country_code);")
                cur.execute("CREATE INDEX idx_code_point_open_admin ON code_point_open(admin_district_code);")
                logger.info("Created indexes for performance")
                
                conn.commit()
                logger.info("Table recreation completed successfully")
                
    except Exception as e:
        logger.error(f"Error recreating table: {e}")
        raise

def load_codepoint_data(csv_path):
    """Load CodePoint data using fast COPY operation"""
    if not os.path.isfile(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        return False

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                logger.info(f"Starting bulk load from {csv_path} into code_point_open...")
                
                # Preview first few lines to verify format
                with open(csv_path, 'r', encoding='utf-8') as f:
                    first_data = f.readline().strip()
                    second_data = f.readline().strip()
                    logger.info(f'First data row: {first_data}')
                    logger.info(f'Second data row: {second_data}')
                
                # Use COPY for fast bulk insertion
                with open(csv_path, 'r', encoding='utf-8') as f:
                    copy_sql = """
                        COPY code_point_open (postcode, positional_quality_indicator, easting, northing, 
                                             country_code, nhs_regional_ha_code, nhs_ha_code, 
                                             admin_county_code, admin_district_code, admin_ward_code)
                        FROM STDIN WITH (FORMAT CSV, DELIMITER ',', HEADER FALSE)
                    """
                    cur.copy_expert(sql=copy_sql, file=f)
                    conn.commit()

                # Get record count
                cur.execute("SELECT COUNT(*) FROM code_point_open;")
                rowcount = cur.fetchone()[0]
                logger.info(f"Successfully loaded {rowcount} records into code_point_open")
                
                return True

    except Exception as e:
        logger.error(f"Error during data load: {e}")
        return False

def load_codepoint_directory(directory_path):
    """Load all CodePoint CSV files from a directory"""
    if not os.path.isdir(directory_path):
        logger.error(f"Directory not found: {directory_path}")
        return False

    # Find all CSV files
    csv_files = glob.glob(os.path.join(directory_path, "*.csv"))
    if not csv_files:
        logger.error(f"No CSV files found in {directory_path}")
        return False

    logger.info(f"Found {len(csv_files)} CSV files to process")
    
    total_records = 0
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                for csv_file in csv_files:
                    logger.info(f"Processing {os.path.basename(csv_file)}...")
                    
                    # Use COPY for fast bulk insertion
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        copy_sql = """
                            COPY code_point_open (postcode, positional_quality_indicator, easting, northing, 
                                                 country_code, nhs_regional_ha_code, nhs_ha_code, 
                                                 admin_county_code, admin_district_code, admin_ward_code)
                            FROM STDIN WITH (FORMAT CSV, DELIMITER ',', HEADER FALSE)
                        """
                        cur.copy_expert(sql=copy_sql, file=f)
                    
                    # Get count for this file
                    cur.execute("SELECT COUNT(*) FROM code_point_open;")
                    current_count = cur.fetchone()[0]
                    file_records = current_count - total_records
                    total_records = current_count
                    
                    logger.info(f"Loaded {file_records} records from {os.path.basename(csv_file)}")
                
                conn.commit()
                logger.info(f"Total records loaded: {total_records}")
                return True

    except Exception as e:
        logger.error(f"Error during directory load: {e}")
        return False

def verify_data_quality():
    """Verify the loaded data quality"""
    logger.info("Verifying data quality...")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Check total count
                cur.execute("SELECT COUNT(*) FROM code_point_open;")
                total_count = cur.fetchone()[0]
                
                # Check for null postcodes
                cur.execute("SELECT COUNT(*) FROM code_point_open WHERE postcode IS NULL;")
                null_postcode_count = cur.fetchone()[0]
                
                # Check for duplicate postcodes (should be 0 due to PRIMARY KEY)
                cur.execute("""
                    SELECT COUNT(*) FROM (
                        SELECT postcode, COUNT(*) 
                        FROM code_point_open 
                        GROUP BY postcode 
                        HAVING COUNT(*) > 1
                    ) as duplicates;
                """)
                duplicate_count = cur.fetchone()[0]
                
                # Check coordinate ranges
                cur.execute("""
                    SELECT 
                        MIN(easting) as min_easting, MAX(easting) as max_easting,
                        MIN(northing) as min_northing, MAX(northing) as max_northing
                    FROM code_point_open;
                """)
                coord_ranges = cur.fetchone()
                
                # Check country distribution
                cur.execute("""
                    SELECT country_code, COUNT(*) 
                    FROM code_point_open 
                    GROUP BY country_code 
                    ORDER BY COUNT(*) DESC;
                """)
                country_distribution = cur.fetchall()
                
                logger.info("=" * 60)
                logger.info("DATA QUALITY REPORT")
                logger.info("=" * 60)
                logger.info(f"Total records: {total_count:,}")
                logger.info(f"Null postcodes: {null_postcode_count}")
                logger.info(f"Duplicate postcodes: {duplicate_count}")
                logger.info(f"Easting range: {coord_ranges[0]:.3f} to {coord_ranges[1]:.3f}")
                logger.info(f"Northing range: {coord_ranges[2]:.3f} to {coord_ranges[3]:.3f}")
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
    # Default paths
    default_file = "backend/data/codepo_gb/Data/CSV/codepo_gb.csv"
    default_dir = "backend/data/codepo_gb/Data/CSV"
    
    # Check command line arguments
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        if os.path.isfile(input_path):
            csv_file = input_path
            csv_dir = None
        elif os.path.isdir(input_path):
            csv_file = None
            csv_dir = input_path
        else:
            logger.error(f"Path not found: {input_path}")
            sys.exit(1)
    else:
        # Use defaults
        if os.path.exists(default_file):
            csv_file = default_file
            csv_dir = None
        elif os.path.exists(default_dir):
            csv_file = None
            csv_dir = default_dir
        else:
            logger.info(f"No CSV file or directory provided; using default: {default_dir}")
            csv_file = None
            csv_dir = default_dir
    
    logger.info("=" * 60)
    logger.info("FAST CODEPOINT DATA INGESTION")
    logger.info("=" * 60)
    if csv_file:
        logger.info(f"CSV file: {csv_file}")
    else:
        logger.info(f"CSV directory: {csv_dir}")
    logger.info("=" * 60)
    
    try:
        # Step 1: Drop and recreate table
        drop_and_recreate_codepoint_table()
        
        # Step 2: Load data using fast COPY
        if csv_file:
            success = load_codepoint_data(csv_file)
        else:
            success = load_codepoint_directory(csv_dir)
        
        if success:
            # Step 3: Verify data quality
            verify_data_quality()
            logger.info("✅ CodePoint data ingestion completed successfully!")
        else:
            logger.error("❌ Data loading failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 