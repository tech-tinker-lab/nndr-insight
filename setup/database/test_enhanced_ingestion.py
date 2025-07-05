#!/usr/bin/env python3
"""
Test the enhanced ingestion pipeline with sample data
"""

import os
import sys
import logging
import pandas as pd
import psycopg2
from db_config import get_connection_string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_enhanced_ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_master_gazetteer_columns():
    conn_str = get_connection_string()
    with psycopg2.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='master_gazetteer'")
            return set(row[0] for row in cur.fetchall())

def test_sample_data_ingestion():
    """Test ingestion with sample NNDR data"""
    logger.info("Starting test ingestion with sample data")
    
    # Path to sample data
    sample_file = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'data', 'sample_nndr.csv')
    
    if not os.path.exists(sample_file):
        logger.error(f"Sample file not found: {sample_file}")
        return False
    
    try:
        # Read sample data
        df = pd.read_csv(sample_file)
        logger.info(f"Loaded {len(df)} records from sample data")
        
        # Add source tracking information
        df['data_source'] = 'sample_nndr'
        df['source_priority'] = 3  # Low priority for sample data
        df['source_confidence_score'] = 0.80
        df['last_source_update'] = pd.Timestamp.now()
        df['source_file_reference'] = 'sample_nndr.csv'
        df['duplicate_group_id'] = None
        df['is_preferred_record'] = False
        
        # Map columns to match our schema
        column_mapping = {
            'PropertyID': 'ba_reference',
            'Address': 'property_address',
            'Postcode': 'postcode',
            'RateableValue': 'rateable_value',
            'Description': 'property_description',
            'Latitude': 'latitude',
            'Longitude': 'longitude',
            'CurrentRatingStatus': 'property_category_code',
            'LastBilledDate': 'effective_date'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Clean and validate data
        df['postcode'] = df['postcode'].str.strip().str.upper()
        df['rateable_value'] = pd.to_numeric(df['rateable_value'], errors='coerce')
        
        # Only keep columns that exist in master_gazetteer
        valid_columns = get_master_gazetteer_columns()
        df = df[[col for col in df.columns if col in valid_columns]]
        
        # Connect to database and insert
        conn_str = get_connection_string()
        with psycopg2.connect(conn_str) as conn:
            with conn.cursor() as cur:
                # Prepare data for insertion
                columns = df.columns.tolist()
                data = list(df.itertuples(index=False, name=None))
                
                # Insert data
                from psycopg2.extras import execute_values
                execute_values(
                    cur,
                    f"INSERT INTO master_gazetteer ({','.join(columns)}) VALUES %s",
                    data,
                    template=None,
                    page_size=1000
                )
                
                conn.commit()
                logger.info(f"Successfully inserted {len(df)} test records")
                
                # Verify insertion
                cur.execute("SELECT COUNT(*) FROM master_gazetteer WHERE data_source = 'sample_nndr'")
                result = cur.fetchone()
                count = result[0] if result else 0
                logger.info(f"Verified {count} records in database")
                
                # Show sample of inserted data
                cur.execute("""
                    SELECT ba_reference, property_address, postcode, rateable_value, data_source, source_priority 
                    FROM master_gazetteer 
                    WHERE data_source = 'sample_nndr' 
                    LIMIT 3
                """)
                sample_records = cur.fetchall()
                logger.info("Sample of inserted records:")
                for record in sample_records:
                    logger.info(f"  - {record}")
        
        return True
        
    except Exception as e:
        logger.error(f"Test ingestion failed: {e}")
        return False

def test_data_source_configuration():
    """Test that data sources are properly configured"""
    logger.info("Testing data source configuration")
    
    try:
        conn_str = get_connection_string()
        with psycopg2.connect(conn_str) as conn:
            with conn.cursor() as cur:
                # Check data sources table
                cur.execute("SELECT source_name, source_priority, source_quality_score FROM data_sources ORDER BY source_priority")
                sources = cur.fetchall()
                
                logger.info("Configured data sources:")
                for source in sources:
                    logger.info(f"  - {source[0]} (priority: {source[1]}, quality: {source[2]})")
                
                return len(sources) > 0
                
    except Exception as e:
        logger.error(f"Data source configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting enhanced ingestion pipeline tests")
    
    # Test 1: Data source configuration
    if not test_data_source_configuration():
        logger.error("Data source configuration test failed")
        return False
    
    # Test 2: Sample data ingestion
    if not test_sample_data_ingestion():
        logger.error("Sample data ingestion test failed")
        return False
    
    logger.info("✓ All tests passed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 