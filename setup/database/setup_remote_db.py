#!/usr/bin/env python3
"""
Remote Database Setup Script
Sets up all database tables on the remote PostGIS server.
"""
import os
import sys
import sqlalchemy
from sqlalchemy import text
from datetime import datetime

# Remote server configuration
REMOTE_CONFIG = {
    'USER': 'nndr',
    'PASSWORD': 'nndrpass',
    'HOST': '192.168.1.79',  # Your remote server IP
    'PORT': '5432',
    'DBNAME': 'nndr_db'
}

def get_connection_string(dbname=None):
    """Get database connection string for remote server."""
    if dbname is None:
        dbname = REMOTE_CONFIG['DBNAME']
    
    return f"postgresql://{REMOTE_CONFIG['USER']}:{REMOTE_CONFIG['PASSWORD']}@{REMOTE_CONFIG['HOST']}:{REMOTE_CONFIG['PORT']}/{dbname}"

def create_engine_for_db(dbname):
    return sqlalchemy.create_engine(get_connection_string(dbname))

def run_sql(engine, sql, params=None, description=""):
    """Execute SQL with parameters and logging"""
    if description:
        print(f"🔄 {description}")
    
    try:
        with engine.connect() as conn:
            with conn.begin():
                if params:
                    result = conn.execute(text(sql), params)
                else:
                    result = conn.execute(text(sql))
                return result
    except Exception as e:
        print(f"❌ Error executing SQL: {e}")
        print(f"SQL: {sql[:100]}...")
        raise

def run_sql_file(engine, file_path, description=""):
    """Execute SQL from a file"""
    if description:
        print(f"📄 {description}")
    
    try:
        with open(file_path, 'r') as f:
            sql_content = f.read()
        
        # Split into individual statements and execute
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"   Executing statement {i}/{len(statements)}...")
                run_sql(engine, statement)
        
        print(f"✅ {description} completed")
        
    except FileNotFoundError:
        print(f"⚠️  File not found: {file_path}")
        raise
    except Exception as e:
        print(f"❌ Error executing file {file_path}: {e}")
        raise

def print_config():
    """Print current database configuration."""
    print("Remote Database Configuration:")
    print(f"  Host: {REMOTE_CONFIG['HOST']}:{REMOTE_CONFIG['PORT']}")
    print(f"  User: {REMOTE_CONFIG['USER']}")
    print(f"  Database: {REMOTE_CONFIG['DBNAME']}")

def setup_remote_database():
    """Set up the complete database on remote server"""
    print("🚀 Setting up Remote Database")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_config()
    
    # Connect to the remote database
    engine = create_engine_for_db(REMOTE_CONFIG['DBNAME'])
    
    # Step 1: Enable PostGIS extension
    print("\n" + "="*60)
    print("STEP 1: Enabling PostGIS Extension")
    print("="*60)
    run_sql(engine, "CREATE EXTENSION IF NOT EXISTS postgis;", description="Enabling PostGIS extension")
    run_sql(engine, "CREATE EXTENSION IF NOT EXISTS postgis_topology;", description="Enabling PostGIS Topology")
    run_sql(engine, "CREATE EXTENSION IF NOT EXISTS postgis_raster;", description="Enabling PostGIS Raster")
    run_sql(engine, "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;", description="Enabling pg_stat_statements")
    run_sql(engine, "CREATE EXTENSION IF NOT EXISTS uuid-ossp;", description="Enabling UUID extension")
    run_sql(engine, "CREATE EXTENSION IF NOT EXISTS pg_trgm;", description="Enabling Trigram extension")
    
    # Step 2: Create master gazetteer schema
    print("\n" + "="*60)
    print("STEP 2: Creating Master Gazetteer Schema")
    print("="*60)
    gazetteer_schema_path = os.path.join(os.path.dirname(__file__), 'master_gazetteer_schema.sql')
    run_sql_file(engine, gazetteer_schema_path, "Creating master gazetteer tables")
    
    # Step 3: Create forecasting system schema
    print("\n" + "="*60)
    print("STEP 3: Creating Forecasting System Schema")
    print("="*60)
    forecasting_schema_path = os.path.join(os.path.dirname(__file__), 'forecasting_system_schema.sql')
    run_sql_file(engine, forecasting_schema_path, "Creating forecasting system tables")
    
    # Step 4: Create core NNDR tables
    print("\n" + "="*60)
    print("STEP 4: Creating Core NNDR Tables")
    print("="*60)
    
    core_tables_sql = [
        """
        CREATE TABLE IF NOT EXISTS properties (
            id SERIAL PRIMARY KEY,
            list_altered VARCHAR(32),
            community_code VARCHAR(16),
            ba_reference VARCHAR(32) UNIQUE,
            property_category_code VARCHAR(16),
            property_description TEXT,
            property_address TEXT,
            street_descriptor TEXT,
            locality TEXT,
            post_town TEXT,
            administrative_area TEXT,
            postcode VARCHAR(16),
            effective_date DATE,
            partially_domestic_signal VARCHAR(4),
            rateable_value NUMERIC,
            scat_code VARCHAR(16),
            appeal_settlement_code VARCHAR(16),
            unique_property_ref VARCHAR(64),
            location GEOMETRY(POINT, 27700),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS ratepayers (
            id SERIAL PRIMARY KEY,
            property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
            name TEXT,
            address TEXT,
            company_number VARCHAR(32),
            liability_start_date DATE,
            liability_end_date DATE,
            annual_charge NUMERIC,
            exemption_amount NUMERIC,
            exemption_code TEXT,
            mandatory_amount NUMERIC,
            mandatory_relief TEXT,
            charity_relief_amount NUMERIC,
            disc_relief_amount NUMERIC,
            discretionary_charitable_relief TEXT,
            additional_rlf TEXT,
            additional_relief TEXT,
            sbr_applied TEXT,
            sbr_supplement TEXT,
            sbr_amount NUMERIC,
            charge_type TEXT,
            report_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS valuations (
            id SERIAL PRIMARY KEY,
            property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
            row_id TEXT,
            billing_auth_code TEXT,
            ba_reference VARCHAR(32),
            scat_code TEXT,
            description TEXT,
            herid TEXT,
            address_full TEXT,
            address1 TEXT,
            address2 TEXT,
            address3 TEXT,
            address4 TEXT,
            address5 TEXT,
            postcode VARCHAR(16),
            effective_date DATE,
            rateable_value NUMERIC,
            uprn BIGINT,
            compiled_list_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]
    
    for i, sql in enumerate(core_tables_sql, 1):
        run_sql(engine, sql, description=f"Creating core table {i}")
    
    # Step 5: Create geospatial tables
    print("\n" + "="*60)
    print("STEP 5: Creating Geospatial Tables")
    print("="*60)
    
    geospatial_tables_sql = [
        """
        CREATE TABLE IF NOT EXISTS os_open_uprn (
            id SERIAL PRIMARY KEY,
            uprn BIGINT UNIQUE,
            os_address_toid VARCHAR(32),
            uprn_status VARCHAR(16),
            building_number VARCHAR(32),
            sao_start_number VARCHAR(32),
            sao_start_suffix VARCHAR(8),
            sao_end_number VARCHAR(32),
            sao_end_suffix VARCHAR(8),
            sao_text VARCHAR(256),
            pao_start_number VARCHAR(32),
            pao_start_suffix VARCHAR(8),
            pao_end_number VARCHAR(32),
            pao_end_suffix VARCHAR(8),
            pao_text VARCHAR(256),
            street_description VARCHAR(256),
            locality VARCHAR(256),
            town_name VARCHAR(256),
            administrative_area VARCHAR(256),
            post_town VARCHAR(256),
            island VARCHAR(256),
            postcode VARCHAR(16),
            postcode_locator VARCHAR(16),
            country_code VARCHAR(8),
            local_custodian_code INTEGER,
            language VARCHAR(8),
            rpc INTEGER,
            x_coordinate NUMERIC,
            y_coordinate NUMERIC,
            latitude NUMERIC,
            longitude NUMERIC,
            location GEOMETRY(POINT, 27700),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS code_point_open (
            id SERIAL PRIMARY KEY,
            postcode VARCHAR(16),
            positional_quality_indicator INTEGER,
            eastings INTEGER,
            northings INTEGER,
            country_code VARCHAR(8),
            nhs_regional_ha_code VARCHAR(8),
            nhs_ha_code VARCHAR(8),
            admin_county_code VARCHAR(8),
            admin_district_code VARCHAR(8),
            admin_ward_code VARCHAR(8),
            location GEOMETRY(POINT, 27700),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS local_authority_districts (
            id SERIAL PRIMARY KEY,
            lad_code VARCHAR(16),
            lad_name VARCHAR(256),
            geometry GEOMETRY(MULTIPOLYGON, 27700),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]
    
    for i, sql in enumerate(geospatial_tables_sql, 1):
        run_sql(engine, sql, description=f"Creating geospatial table {i}")
    
    # Step 6: Create indexes
    print("\n" + "="*60)
    print("STEP 6: Creating Indexes")
    print("="*60)
    
    indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_properties_postcode ON properties(postcode);",
        "CREATE INDEX IF NOT EXISTS idx_properties_ba_reference ON properties(ba_reference);",
        "CREATE INDEX IF NOT EXISTS idx_properties_location ON properties USING GIST(location);",
        "CREATE INDEX IF NOT EXISTS idx_ratepayers_property_id ON ratepayers(property_id);",
        "CREATE INDEX IF NOT EXISTS idx_valuations_property_id ON valuations(property_id);",
        "CREATE INDEX IF NOT EXISTS idx_valuations_ba_reference ON valuations(ba_reference);",
        "CREATE INDEX IF NOT EXISTS idx_os_open_uprn_uprn ON os_open_uprn(uprn);",
        "CREATE INDEX IF NOT EXISTS idx_os_open_uprn_postcode ON os_open_uprn(postcode);",
        "CREATE INDEX IF NOT EXISTS idx_os_open_uprn_location ON os_open_uprn USING GIST(location);",
        "CREATE INDEX IF NOT EXISTS idx_code_point_open_postcode ON code_point_open(postcode);",
        "CREATE INDEX IF NOT EXISTS idx_code_point_open_location ON code_point_open USING GIST(location);",
        "CREATE INDEX IF NOT EXISTS idx_lad_geometry ON local_authority_districts USING GIST(geometry);"
    ]
    
    for i, sql in enumerate(indexes_sql, 1):
        run_sql(engine, sql, description=f"Creating index {i}")
    
    print("\n" + "="*60)
    print("✅ DATABASE SETUP COMPLETE!")
    print("="*60)
    print(f"📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📊 Database Summary:")
    print(f"   Host: {REMOTE_CONFIG['HOST']}:{REMOTE_CONFIG['PORT']}")
    print(f"   Database: {REMOTE_CONFIG['DBNAME']}")
    print(f"   User: {REMOTE_CONFIG['USER']}")
    print("\n🗂️  Tables Created:")
    print("   - properties (NNDR properties)")
    print("   - ratepayers (NNDR ratepayers)")
    print("   - valuations (NNDR valuations)")
    print("   - os_open_uprn (OS Open UPRN)")
    print("   - code_point_open (Code-Point Open)")
    print("   - local_authority_districts (LAD boundaries)")
    print("   - master_gazetteer (comprehensive property gazetteer)")
    print("   - forecasting tables (for analysis and predictions)")
    print("\n🔧 Next Steps:")
    print("   1. Run data ingestion scripts to load your NNDR data")
    print("   2. Apply performance tuning if needed")
    print("   3. Start your analysis and forecasting")

def main():
    """Main function"""
    try:
        setup_remote_database()
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 