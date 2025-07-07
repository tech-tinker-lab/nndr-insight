#!/usr/bin/env python3
"""
Schema Alignment Check Script
Check if the current database schema matches the expected schema for the parallel pipeline
"""

import os
import sys
import psycopg2
import pandas as pd
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_connection_string():
    """Get database connection string"""
    return "postgresql://nndr:nndrpass@192.168.1.79:5432/nndr_db"

def check_table_exists(cursor, table_name: str) -> bool:
    """Check if a table exists"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = %s
        );
    """, (table_name,))
    return cursor.fetchone()[0]

def get_table_columns(cursor, table_name: str) -> List[str]:
    """Get column names for a table"""
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = %s 
        ORDER BY ordinal_position;
    """, (table_name,))
    return [row[0] for row in cursor.fetchall()]

def check_reference_tables():
    """Check all reference tables and their schemas"""
    logger.info("Checking reference tables schema alignment...")
    
    # Expected table schemas
    expected_schemas = {
        'os_open_uprn': [
            'id', 'uprn', 'x_coordinate', 'y_coordinate', 'latitude', 'longitude'
        ],
        'code_point_open': [
            'id', 'postcode', 'positional_quality_indicator', 'eastings', 'northings', 
            'country_code', 'nhs_regional_ha_code', 'nhs_ha_code', 'admin_county_code', 
            'admin_district_code', 'admin_ward_code', 'location', 'created_at'
        ],
        'onspd': [
            'id', 'pcds', 'pcd', 'pcd2', 'lat', 'long', 'ctry', 'oscty', 'ced', 'oslaua', 'osward', 'parish', 
            'usertype', 'oseast1m', 'osnrth1m', 'osgrdind', 'oshlthau', 'nhser', 'rgn', 'streg', 'pcon', 
            'eer', 'teclec', 'ttwa', 'pct', 'itl', 'statsward', 'oa01', 'casward', 'npark', 'lsoa01', 
            'msoa01', 'oac01', 'oa11', 'lsoa11', 'msoa11', 'wz11', 'sicbl', 'bua24', 'ru11ind', 'oac11', 
            'lep1', 'lep2', 'pfa', 'imd', 'calncv', 'icb', 'oa21', 'lsoa21', 'msoa21', 'ruc21ind', 'globalid', 'created_at'
        ],
        'os_open_names': [
            'id', 'os_id', 'names_uri', 'name1', 'name1_lang', 'name2', 'name2_lang',
            'type', 'local_type', 'geometry_x', 'geometry_y', 'most_detail_view_res',
            'least_detail_view_res', 'mbr_xmin', 'mbr_ymin', 'mbr_xmax', 'mbr_ymax',
            'postcode_district', 'postcode_district_uri', 'populated_place', 'populated_place_uri',
            'admin_area', 'admin_area_uri', 'country', 'country_uri', 'created_at'
        ],
        'os_open_usrn': [
            'id', 'usrn', 'street_name', 'locality', 'town', 'administrative_area', 
            'postcode', 'geometry_x', 'geometry_y', 'created_at'
        ],
        'lad_boundaries': [
            'id', 'lad_code', 'lad_name', 'geometry', 'created_at', 'updated_at'
        ],
        'os_open_map_local': [
            'id', 'feature_id', 'feature_type', 'theme', 'geometry', 'created_at', 'updated_at'
        ]
    }
    
    try:
        conn = psycopg2.connect(get_connection_string())
        cursor = conn.cursor()
        
        issues = []
        missing_tables = []
        schema_mismatches = []
        
        for table_name, expected_columns in expected_schemas.items():
            logger.info(f"Checking table: {table_name}")
            
            if not check_table_exists(cursor, table_name):
                missing_tables.append(table_name)
                logger.warning(f"❌ Table {table_name} does not exist")
                continue
            
            actual_columns = get_table_columns(cursor, table_name)
            logger.info(f"✅ Table {table_name} exists with {len(actual_columns)} columns")
            
            # Check for missing columns
            missing_columns = [col for col in expected_columns if col not in actual_columns]
            if missing_columns:
                schema_mismatches.append({
                    'table': table_name,
                    'missing_columns': missing_columns,
                    'actual_columns': actual_columns
                })
                logger.warning(f"❌ Table {table_name} missing columns: {missing_columns}")
            
            # Check for extra columns
            extra_columns = [col for col in actual_columns if col not in expected_columns]
            if extra_columns:
                logger.info(f"ℹ️  Table {table_name} has extra columns: {extra_columns}")
        
        cursor.close()
        conn.close()
        
        # Print summary
        logger.info("=" * 60)
        logger.info("SCHEMA ALIGNMENT SUMMARY")
        logger.info("=" * 60)
        
        if missing_tables:
            logger.error(f"❌ Missing tables: {missing_tables}")
        else:
            logger.info("✅ All expected tables exist")
        
        if schema_mismatches:
            logger.error(f"❌ Schema mismatches found in {len(schema_mismatches)} tables:")
            for mismatch in schema_mismatches:
                logger.error(f"  - {mismatch['table']}: missing {mismatch['missing_columns']}")
        else:
            logger.info("✅ All table schemas match expectations")
        
        return len(missing_tables) == 0 and len(schema_mismatches) == 0
        
    except Exception as e:
        logger.error(f"Error checking schema: {e}")
        return False

def check_data_counts():
    """Check record counts in reference tables"""
    logger.info("Checking data counts in reference tables...")
    
    reference_tables = [
        'os_open_uprn', 'code_point_open', 'onspd', 'os_open_names', 
        'os_open_usrn', 'lad_boundaries', 'os_open_map_local'
    ]
    
    try:
        conn = psycopg2.connect(get_connection_string())
        cursor = conn.cursor()
        
        for table_name in reference_tables:
            if check_table_exists(cursor, table_name):
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                logger.info(f"📊 {table_name}: {count:,} records")
            else:
                logger.warning(f"❌ {table_name}: table does not exist")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error checking data counts: {e}")

def main():
    """Main execution function"""
    logger.info("Starting schema alignment check...")
    
    # Check schema alignment
    schema_ok = check_reference_tables()
    
    # Check data counts
    check_data_counts()
    
    if schema_ok:
        logger.info("✅ Schema alignment check passed!")
        return 0
    else:
        logger.error("❌ Schema alignment check failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 