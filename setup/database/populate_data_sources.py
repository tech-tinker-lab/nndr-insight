#!/usr/bin/env python3
"""
Populate the data_sources table with our defined data sources
"""

import psycopg2
from db_config import get_connection_string

def populate_data_sources():
    """Populate data_sources table with our defined sources"""
    
    # Define our data sources
    data_sources = [
        {
            'source_name': 'voa_2023',
            'source_type': 'nndr',
            'source_description': 'VOA 2023 NNDR Compiled List - Official source',
            'source_priority': 1,
            'source_quality_score': 0.95,
            'source_update_frequency': 'annual',
            'source_coordinate_system': 'wgs84',
            'source_file_pattern': 'uk-englandwales-ndr-2023-listentries-compiled-epoch-0015-baseline-csv.csv'
        },
        {
            'source_name': 'local_council_2015',
            'source_type': 'nndr',
            'source_description': 'Local Council NNDR Data 2015 - Supplementary source',
            'source_priority': 2,
            'source_quality_score': 0.85,
            'source_update_frequency': 'annual',
            'source_coordinate_system': 'unknown',
            'source_file_pattern': 'NNDR Rating List  March 2015_0.csv'
        },
        {
            'source_name': 'sample_nndr',
            'source_type': 'nndr',
            'source_description': 'Sample NNDR Data - Development and testing',
            'source_priority': 3,
            'source_quality_score': 0.80,
            'source_update_frequency': 'manual',
            'source_coordinate_system': 'wgs84',
            'source_file_pattern': 'sample_nndr.csv'
        },
        {
            'source_name': 'os_uprn',
            'source_type': 'reference',
            'source_description': 'OS Open UPRN - Official property reference numbers with coordinates',
            'source_priority': 1,
            'source_quality_score': 0.98,
            'source_update_frequency': 'monthly',
            'source_coordinate_system': 'osgb',
            'source_file_pattern': 'osopenuprn_202506_csv/osopenuprn_202506.csv'
        },
        {
            'source_name': 'codepoint',
            'source_type': 'reference',
            'source_description': 'CodePoint Open - Postcode to coordinate mapping',
            'source_priority': 2,
            'source_quality_score': 0.90,
            'source_update_frequency': 'quarterly',
            'source_coordinate_system': 'osgb',
            'source_file_pattern': 'codepo_gb/Data/CSV/*.csv'
        },
        {
            'source_name': 'onspd',
            'source_type': 'reference',
            'source_description': 'ONS Postcode Directory - Comprehensive postcode data with administrative geographies',
            'source_priority': 1,
            'source_quality_score': 0.95,
            'source_update_frequency': 'quarterly',
            'source_coordinate_system': 'osgb',
            'source_file_pattern': 'ONSPD_Online_Latest_Centroids.csv'
        },
        # Land Revenue and Property Sales Data Sources
        {
            'source_name': 'land_registry',
            'source_type': 'property_sales',
            'source_description': 'HM Land Registry - Official property sales data',
            'source_priority': 1,
            'source_quality_score': 0.98,
            'source_update_frequency': 'monthly',
            'source_coordinate_system': 'osgb',
            'source_file_pattern': 'land_registry_sales_*.csv'
        },
        {
            'source_name': 'rightmove',
            'source_type': 'property_sales',
            'source_description': 'Rightmove - Property listings and sales data',
            'source_priority': 2,
            'source_quality_score': 0.85,
            'source_update_frequency': 'weekly',
            'source_coordinate_system': 'wgs84',
            'source_file_pattern': 'rightmove_*.csv'
        },
        {
            'source_name': 'zoopla',
            'source_type': 'property_sales',
            'source_description': 'Zoopla - Property market data and valuations',
            'source_priority': 2,
            'source_quality_score': 0.85,
            'source_update_frequency': 'weekly',
            'source_coordinate_system': 'wgs84',
            'source_file_pattern': 'zoopla_*.csv'
        },
        {
            'source_name': 'estates_gazette',
            'source_type': 'market_analysis',
            'source_description': 'Estates Gazette - Commercial property market analysis',
            'source_priority': 1,
            'source_quality_score': 0.90,
            'source_update_frequency': 'monthly',
            'source_coordinate_system': 'unknown',
            'source_file_pattern': 'estates_gazette_*.csv'
        },
        {
            'source_name': 'ons_economic',
            'source_type': 'economic_indicators',
            'source_description': 'ONS Economic Indicators - Official economic data',
            'source_priority': 1,
            'source_quality_score': 0.95,
            'source_update_frequency': 'monthly',
            'source_coordinate_system': 'n/a',
            'source_file_pattern': 'ons_economic_*.csv'
        },
        {
            'source_name': 'bank_of_england',
            'source_type': 'economic_indicators',
            'source_description': 'Bank of England - Interest rates and monetary policy data',
            'source_priority': 1,
            'source_quality_score': 0.98,
            'source_update_frequency': 'weekly',
            'source_coordinate_system': 'n/a',
            'source_file_pattern': 'boe_*.csv'
        },
        {
            'source_name': 'rental_data',
            'source_type': 'land_revenue',
            'source_description': 'Rental Income Data - Commercial property rental information',
            'source_priority': 2,
            'source_quality_score': 0.80,
            'source_update_frequency': 'quarterly',
            'source_coordinate_system': 'wgs84',
            'source_file_pattern': 'rental_data_*.csv'
        }
    ]
    
    conn_str = get_connection_string()
    try:
        with psycopg2.connect(conn_str) as conn:
            with conn.cursor() as cur:
                # Clear existing data sources
                cur.execute("DELETE FROM data_sources")
                
                # Insert new data sources
                for source in data_sources:
                    cur.execute("""
                        INSERT INTO data_sources 
                        (source_name, source_type, source_description, source_priority, 
                         source_quality_score, source_update_frequency, source_coordinate_system, source_file_pattern)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        source['source_name'],
                        source['source_type'],
                        source['source_description'],
                        source['source_priority'],
                        source['source_quality_score'],
                        source['source_update_frequency'],
                        source['source_coordinate_system'],
                        source['source_file_pattern']
                    ))
                
                conn.commit()
                print(f"✓ Successfully populated {len(data_sources)} data sources")
                
                # Show what was inserted
                cur.execute("SELECT source_name, source_type, source_priority, source_quality_score FROM data_sources ORDER BY source_type, source_priority")
                sources = cur.fetchall()
                print("\nConfigured data sources by type:")
                current_type = None
                for source in sources:
                    if source[1] != current_type:
                        current_type = source[1]
                        print(f"\n{current_type.upper()} sources:")
                    print(f"  - {source[0]} (priority: {source[2]}, quality: {source[3]})")
                
    except Exception as e:
        print(f"❌ Failed to populate data sources: {e}")
        raise

if __name__ == "__main__":
    populate_data_sources() 