#!/usr/bin/env python3
"""
Populate Master Gazetteer Table
This script consolidates data from all existing tables into the master_gazetteer table
for comprehensive business rate forecasting and analysis.
"""
import sqlalchemy
from sqlalchemy import text
from db_config import get_connection_string, print_config, DB_CONFIG
import json
from datetime import datetime

def create_engine_for_db(dbname):
    return sqlalchemy.create_engine(get_connection_string(dbname))

def run_sql(engine, sql, params=None):
    """Execute SQL with parameters"""
    with engine.connect() as conn:
        with conn.begin():
            if params:
                result = conn.execute(text(sql), params)
            else:
                result = conn.execute(text(sql))
            return result

def populate_master_gazetteer():
    """Populate the master gazetteer table with consolidated data"""
    print("🔄 Populating Master Gazetteer Table...")
    
    # Connect to database
    engine = create_engine_for_db(DB_CONFIG['DBNAME'])
    
    # Step 1: Create master_gazetteer table if it doesn't exist
    print("📋 Creating master_gazetteer table...")
    
    # Read the SQL schema file
    try:
        with open('master_gazetteer_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Split into individual statements and execute
        statements = schema_sql.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                run_sql(engine, statement)
        
        print("✅ Master gazetteer table created successfully")
    except FileNotFoundError:
        print("⚠️  master_gazetteer_schema.sql not found, using inline schema...")
        # Fallback to inline schema creation
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS master_gazetteer (
            id SERIAL PRIMARY KEY,
            uprn BIGINT UNIQUE,
            ba_reference VARCHAR(32),
            property_id VARCHAR(64),
            property_name TEXT,
            property_description TEXT,
            property_category_code VARCHAR(16),
            property_category_description TEXT,
            address_line_1 TEXT,
            address_line_2 TEXT,
            address_line_3 TEXT,
            address_line_4 TEXT,
            address_line_5 TEXT,
            street_descriptor TEXT,
            locality TEXT,
            post_town TEXT,
            administrative_area TEXT,
            postcode VARCHAR(16),
            postcode_district VARCHAR(8),
            x_coordinate DOUBLE PRECISION,
            y_coordinate DOUBLE PRECISION,
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            geom GEOMETRY(Point, 27700),
            lad_code VARCHAR(10),
            lad_name TEXT,
            ward_code VARCHAR(10),
            ward_name TEXT,
            parish_code VARCHAR(10),
            parish_name TEXT,
            constituency_code VARCHAR(10),
            constituency_name TEXT,
            lsoa_code VARCHAR(10),
            lsoa_name TEXT,
            msoa_code VARCHAR(10),
            msoa_name TEXT,
            oa_code VARCHAR(10),
            imd_decile INTEGER,
            imd_rank INTEGER,
            rural_urban_code VARCHAR(2),
            property_type TEXT,
            building_type TEXT,
            floor_area NUMERIC,
            number_of_floors INTEGER,
            construction_year INTEGER,
            last_refurbished INTEGER,
            current_rateable_value NUMERIC,
            current_effective_date DATE,
            current_scat_code VARCHAR(16),
            current_appeal_status VARCHAR(32),
            current_exemption_code VARCHAR(16),
            current_relief_code VARCHAR(16),
            historical_rateable_values JSONB,
            valuation_history_count INTEGER,
            current_ratepayer_name TEXT,
            current_ratepayer_type VARCHAR(32),
            current_ratepayer_company_number VARCHAR(32),
            current_liability_start_date DATE,
            current_annual_charge NUMERIC,
            business_type VARCHAR(64),
            business_sector VARCHAR(64),
            employee_count_range VARCHAR(32),
            turnover_range VARCHAR(32),
            planning_permission_status VARCHAR(32),
            last_planning_decision_date DATE,
            development_potential_score NUMERIC,
            market_value_estimate NUMERIC,
            market_value_source VARCHAR(32),
            market_value_date DATE,
            rental_value_estimate NUMERIC,
            rental_value_source VARCHAR(32),
            rental_value_date DATE,
            compliance_risk_score NUMERIC,
            last_inspection_date DATE,
            enforcement_notices_count INTEGER,
            forecast_rateable_value NUMERIC,
            forecast_effective_date DATE,
            forecast_confidence_score NUMERIC,
            forecast_factors JSONB,
            data_quality_score NUMERIC,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_sources JSONB,
            source_priority INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            notes TEXT
        );
        """
        run_sql(engine, create_table_sql)
        print("✅ Master gazetteer table created successfully")
    
    # Step 2: Populate from properties table
    print("📊 Populating from properties table...")
    properties_sql = """
    INSERT INTO master_gazetteer (
        ba_reference, property_id, property_description, property_category_code,
        address_line_1, address_line_2, address_line_3, address_line_4, address_line_5,
        street_descriptor, locality, post_town, administrative_area, postcode,
        current_rateable_value, current_effective_date, current_scat_code,
        data_sources, source_priority, data_quality_score
    )
    SELECT 
        ba_reference,
        id::VARCHAR(64),
        property_description,
        property_category_code,
        property_address,
        street_descriptor,
        locality,
        post_town,
        administrative_area,
        postcode,
        street_descriptor,
        locality,
        post_town,
        administrative_area,
        postcode,
        rateable_value,
        effective_date,
        scat_code,
        '["properties"]'::jsonb,
        1,
        85
    FROM properties
    WHERE ba_reference IS NOT NULL
    ON CONFLICT (ba_reference) DO UPDATE SET
        property_description = EXCLUDED.property_description,
        property_category_code = EXCLUDED.property_category_code,
        current_rateable_value = EXCLUDED.current_rateable_value,
        current_effective_date = EXCLUDED.current_effective_date,
        current_scat_code = EXCLUDED.current_scat_code,
        updated_at = CURRENT_TIMESTAMP;
    """
    run_sql(engine, properties_sql)
    print("✅ Properties data populated")
    
    # Step 3: Populate from gazetteer table
    print("📊 Populating from gazetteer table...")
    gazetteer_sql = """
    INSERT INTO master_gazetteer (
        property_id, x_coordinate, y_coordinate, latitude, longitude, geom,
        address_line_1, postcode, property_type, district,
        data_sources, source_priority, data_quality_score
    )
    SELECT 
        property_id,
        x_coordinate,
        y_coordinate,
        latitude,
        longitude,
        ST_SetSRID(ST_MakePoint(x_coordinate, y_coordinate), 27700),
        address,
        postcode,
        property_type,
        district,
        '["gazetteer"]'::jsonb,
        2,
        80
    FROM gazetteer
    WHERE property_id IS NOT NULL
    ON CONFLICT (property_id) DO UPDATE SET
        x_coordinate = EXCLUDED.x_coordinate,
        y_coordinate = EXCLUDED.y_coordinate,
        latitude = EXCLUDED.latitude,
        longitude = EXCLUDED.longitude,
        geom = EXCLUDED.geom,
        address_line_1 = EXCLUDED.address_line_1,
        postcode = EXCLUDED.postcode,
        property_type = EXCLUDED.property_type,
        updated_at = CURRENT_TIMESTAMP;
    """
    run_sql(engine, gazetteer_sql)
    print("✅ Gazetteer data populated")
    
    # Step 4: Populate from os_open_uprn table
    print("📊 Populating from OS Open UPRN table...")
    uprn_sql = """
    INSERT INTO master_gazetteer (
        uprn, x_coordinate, y_coordinate, latitude, longitude, geom,
        data_sources, source_priority, data_quality_score
    )
    SELECT 
        uprn,
        x_coordinate,
        y_coordinate,
        latitude,
        longitude,
        ST_SetSRID(ST_MakePoint(x_coordinate, y_coordinate), 27700),
        '["os_open_uprn"]'::jsonb,
        3,
        90
    FROM os_open_uprn
    WHERE uprn IS NOT NULL
    ON CONFLICT (uprn) DO UPDATE SET
        x_coordinate = EXCLUDED.x_coordinate,
        y_coordinate = EXCLUDED.y_coordinate,
        latitude = EXCLUDED.latitude,
        longitude = EXCLUDED.longitude,
        geom = EXCLUDED.gem,
        updated_at = CURRENT_TIMESTAMP;
    """
    run_sql(engine, uprn_sql)
    print("✅ OS Open UPRN data populated")
    
    # Step 5: Enrich with ONSPD data
    print("📊 Enriching with ONSPD data...")
    onspd_sql = """
    UPDATE master_gazetteer 
    SET 
        lsoa_code = o.lsoa11,
        msoa_code = o.msoa11,
        oa_code = o.oa11,
        imd_decile = CASE 
            WHEN o.imd ~ '^[0-9]+$' THEN o.imd::integer 
            ELSE NULL 
        END,
        rural_urban_code = o.ur01ind,
        data_sources = CASE 
            WHEN data_sources IS NULL THEN '["onspd"]'::jsonb
            ELSE data_sources || '["onspd"]'::jsonb
        END,
        updated_at = CURRENT_TIMESTAMP
    FROM onspd o
    WHERE master_gazetteer.postcode = o.pcds
    AND o.lsoa11 IS NOT NULL;
    """
    run_sql(engine, onspd_sql)
    print("✅ ONSPD data enrichment completed")
    
    # Step 6: Enrich with ratepayer information
    print("📊 Enriching with ratepayer information...")
    ratepayer_sql = """
    UPDATE master_gazetteer 
    SET 
        current_ratepayer_name = r.name,
        current_ratepayer_type = CASE 
            WHEN r.company_number IS NOT NULL THEN 'Company'
            WHEN r.name ILIKE '%charity%' OR r.name ILIKE '%trust%' THEN 'Charity'
            ELSE 'Individual'
        END,
        current_ratepayer_company_number = r.company_number,
        current_liability_start_date = r.liability_start_date,
        current_annual_charge = r.annual_charge,
        updated_at = CURRENT_TIMESTAMP
    FROM ratepayers r
    JOIN properties p ON r.property_id = p.id
    WHERE master_gazetteer.ba_reference = p.ba_reference
    AND r.name IS NOT NULL;
    """
    run_sql(engine, ratepayer_sql)
    print("✅ Ratepayer data enrichment completed")
    
    # Step 7: Calculate data quality scores
    print("📊 Calculating data quality scores...")
    quality_sql = """
    UPDATE master_gazetteer 
    SET 
        data_quality_score = (
            CASE WHEN uprn IS NOT NULL THEN 20 ELSE 0 END +
            CASE WHEN ba_reference IS NOT NULL THEN 20 ELSE 0 END +
            CASE WHEN postcode IS NOT NULL THEN 15 ELSE 0 END +
            CASE WHEN x_coordinate IS NOT NULL AND y_coordinate IS NOT NULL THEN 15 ELSE 0 END +
            CASE WHEN current_rateable_value IS NOT NULL THEN 10 ELSE 0 END +
            CASE WHEN property_category_code IS NOT NULL THEN 10 ELSE 0 END +
            CASE WHEN current_ratepayer_name IS NOT NULL THEN 10 ELSE 0 END
        ),
        updated_at = CURRENT_TIMESTAMP;
    """
    run_sql(engine, quality_sql)
    print("✅ Data quality scores calculated")
    
    # Step 8: Generate summary statistics
    print("📊 Generating summary statistics...")
    summary_sql = """
    SELECT 
        COUNT(*) as total_properties,
        COUNT(CASE WHEN ba_reference IS NOT NULL THEN 1 END) as rated_properties,
        COUNT(CASE WHEN ba_reference IS NULL THEN 1 END) as non_rated_properties,
        COUNT(CASE WHEN current_rateable_value IS NOT NULL THEN 1 END) as properties_with_values,
        AVG(data_quality_score) as avg_data_quality,
        SUM(current_rateable_value) as total_rateable_value
    FROM master_gazetteer;
    """
    result = run_sql(engine, summary_sql)
    stats = result.fetchone()
    
    print("\n📈 Master Gazetteer Population Summary:")
    print(f"   Total Properties: {stats[0]:,}")
    print(f"   Rated Properties: {stats[1]:,}")
    print(f"   Non-Rated Properties: {stats[2]:,}")
    print(f"   Properties with Values: {stats[3]:,}")
    print(f"   Average Data Quality: {stats[4]:.1f}/100")
    print(f"   Total Rateable Value: £{stats[5]:,.0f}" if stats[5] else "   Total Rateable Value: £0")
    
    print("\n✅ Master Gazetteer population completed successfully!")

def main():
    """Main function"""
    print("🚀 Starting Master Gazetteer Population Process")
    print_config()
    
    try:
        populate_master_gazetteer()
        print("\n🎉 Master Gazetteer population process completed successfully!")
        print("\nNext steps:")
        print("1. Review the populated data")
        print("2. Run data quality checks")
        print("3. Begin forecasting model development")
        print("4. Implement non-rated property detection algorithms")
        
    except Exception as e:
        print(f"❌ Error during master gazetteer population: {e}")
        raise

if __name__ == "__main__":
    main() 