#!/usr/bin/env python3
"""
Complete Database Setup Script
This script runs all database setup scripts in the correct order, similar to Liquibase functionality.
It handles the complete database initialization including all tables, indexes, and data population.
"""
import sqlalchemy
from sqlalchemy import text
from db_config import get_connection_string, print_config, DB_CONFIG
import os
import sys
import time
from datetime import datetime

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

def check_database_exists(engine, dbname):
    """Check if database exists"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :dbname"), {"dbname": dbname})
            return result.fetchone() is not None
    except Exception:
        return False

def create_database_if_not_exists(dbname):
    """Create database if it doesn't exist"""
    print(f"🔍 Checking if database '{dbname}' exists...")
    
    # Connect to default postgres database
    default_engine = sqlalchemy.create_engine(
        f"postgresql://{DB_CONFIG['USER']}:{DB_CONFIG['PASSWORD']}@{DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/postgres"
    )
    
    if not check_database_exists(default_engine, dbname):
        print(f"📝 Creating database '{dbname}'...")
        with default_engine.connect() as conn:
            with conn.begin():
                conn.execute(text(f"CREATE DATABASE {dbname}"))
        print(f"✅ Database '{dbname}' created successfully")
    else:
        print(f"✅ Database '{dbname}' already exists")

def run_migration_step(step_number, description, function, *args, **kwargs):
    """Run a migration step with logging"""
    print(f"\n{'='*60}")
    print(f"STEP {step_number}: {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        function(*args, **kwargs)
        end_time = time.time()
        print(f"✅ Step {step_number} completed in {end_time - start_time:.2f} seconds")
        return True
    except Exception as e:
        print(f"❌ Step {step_number} failed: {e}")
        return False

def run_complete_db_setup():
    """Run complete database setup"""
    print("🚀 Starting Complete Database Setup")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_config()
    
    # Step 1: Create database if it doesn't exist
    dbname = DB_CONFIG['DBNAME']
    run_migration_step(1, "Database Creation", create_database_if_not_exists, dbname)
    
    # Connect to the target database
    engine = create_engine_for_db(dbname)
    
    # Step 2: Enable PostGIS extension
    def enable_postgis():
        run_sql(engine, "CREATE EXTENSION IF NOT EXISTS postgis;", description="Enabling PostGIS extension")
    
    run_migration_step(2, "PostGIS Extension", enable_postgis)
    
    # Step 3: Create core NNDR tables
    def create_core_tables():
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
                unique_property_ref VARCHAR(64)
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
                notes TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS valuations (
                id SERIAL PRIMARY KEY,
                property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
                row_id TEXT,
                billing_auth_code TEXT,
                empty1 TEXT,
                ba_reference VARCHAR(32),
                scat_code TEXT,
                description TEXT,
                herid TEXT,
                address_full TEXT,
                empty2 TEXT,
                address1 TEXT,
                address2 TEXT,
                address3 TEXT,
                address4 TEXT,
                address5 TEXT,
                postcode VARCHAR(16),
                effective_date DATE,
                empty3 TEXT,
                rateable_value NUMERIC,
                empty4 TEXT,
                uprn BIGINT,
                compiled_list_date TEXT,
                list_code TEXT,
                empty5 TEXT,
                empty6 TEXT,
                empty7 TEXT,
                property_link_number TEXT,
                entry_date TEXT,
                empty8 TEXT,
                empty9 TEXT,
                source TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS historic_valuations (
                id SERIAL PRIMARY KEY,
                property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
                billing_auth_code TEXT,
                empty1 TEXT,
                ba_reference VARCHAR(32),
                scat_code TEXT,
                description TEXT,
                herid TEXT,
                effective_date DATE,
                empty2 TEXT,
                rateable_value NUMERIC,
                uprn BIGINT,
                change_date TEXT,
                list_code TEXT,
                property_link_number TEXT,
                entry_date TEXT,
                removal_date TEXT,
                source TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS categories (
                code TEXT PRIMARY KEY,
                description TEXT
            );
            """
        ]
        
        for i, sql in enumerate(core_tables_sql, 1):
            table_name = ["properties", "ratepayers", "valuations", "historic_valuations", "categories"][i-1]
            run_sql(engine, sql, description=f"Creating {table_name} table")
    
    run_migration_step(3, "Core NNDR Tables", create_core_tables)
    
    # Step 4: Create geospatial tables
    def create_geospatial_tables():
        geospatial_tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS gazetteer (
                id SERIAL PRIMARY KEY,
                property_id VARCHAR(64) UNIQUE,
                x_coordinate DOUBLE PRECISION,
                y_coordinate DOUBLE PRECISION,
                address TEXT,
                postcode VARCHAR(16),
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                property_type TEXT,
                district TEXT,
                source TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS os_open_uprn (
                uprn BIGINT PRIMARY KEY,
                x_coordinate DOUBLE PRECISION,
                y_coordinate DOUBLE PRECISION,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                source TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS code_point_open (
                postcode TEXT PRIMARY KEY,
                positional_quality_indicator TEXT,
                easting DOUBLE PRECISION,
                northing DOUBLE PRECISION,
                country_code TEXT,
                nhs_regional_ha_code TEXT,
                nhs_ha_code TEXT,
                admin_county_code TEXT,
                admin_district_code TEXT,
                admin_ward_code TEXT,
                source TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS onspd (
                pcds TEXT PRIMARY KEY,
                pcd TEXT,
                lat DOUBLE PRECISION,
                long DOUBLE PRECISION,
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
            """,
            """
            CREATE TABLE IF NOT EXISTS os_open_names (
                id SERIAL PRIMARY KEY,
                os_id TEXT UNIQUE,
                names_uri TEXT,
                name1 TEXT,
                name1_lang TEXT,
                name2 TEXT,
                name2_lang TEXT,
                type TEXT,
                local_type TEXT,
                geometry_x DOUBLE PRECISION,
                geometry_y DOUBLE PRECISION,
                most_detail_view_res INTEGER,
                least_detail_view_res INTEGER,
                mbr_xmin DOUBLE PRECISION,
                mbr_ymin DOUBLE PRECISION,
                mbr_xmax DOUBLE PRECISION,
                mbr_ymax DOUBLE PRECISION,
                postcode_district TEXT,
                postcode_district_uri TEXT,
                populated_place TEXT,
                populated_place_uri TEXT,
                populated_place_type TEXT,
                district_borough TEXT,
                district_borough_uri TEXT,
                district_borough_type TEXT,
                county_unitary TEXT,
                county_unitary_uri TEXT,
                county_unitary_type TEXT,
                region TEXT,
                region_uri TEXT,
                country TEXT,
                country_uri TEXT,
                related_spatial_object TEXT,
                same_as_dbpedia TEXT,
                same_as_geonames TEXT,
                geom GEOMETRY(Point, 27700)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS lad_boundaries (
                id SERIAL PRIMARY KEY,
                lad_code TEXT,
                lad_name TEXT,
                geometry GEOMETRY(MultiPolygon, 27700)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS os_open_map_local (
                id SERIAL PRIMARY KEY,
                feature_id TEXT,
                feature_type TEXT,
                feature_description TEXT,
                theme TEXT,
                geometry GEOMETRY(Geometry, 27700),
                source TEXT
            );
            """
        ]
        
        for i, sql in enumerate(geospatial_tables_sql, 1):
            table_name = ["gazetteer", "os_open_uprn", "code_point_open", "onspd", "os_open_names", "lad_boundaries", "os_open_map_local"][i-1]
            run_sql(engine, sql, description=f"Creating {table_name} table")
    
    run_migration_step(4, "Geospatial Tables", create_geospatial_tables)
    
    # Step 5: Create staging tables
    def create_staging_tables():
        staging_tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS gazetteer_staging (
                uprn BIGINT,
                x_coordinate DOUBLE PRECISION,
                y_coordinate DOUBLE PRECISION,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS os_open_uprn_staging (
                uprn BIGINT,
                x_coordinate DOUBLE PRECISION,
                y_coordinate DOUBLE PRECISION,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                source TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS code_point_open_staging (
                postcode TEXT,
                positional_quality_indicator TEXT,
                easting DOUBLE PRECISION,
                northing DOUBLE PRECISION,
                country_code TEXT,
                nhs_regional_ha_code TEXT,
                nhs_ha_code TEXT,
                admin_county_code TEXT,
                admin_district_code TEXT,
                admin_ward_code TEXT,
                source TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS onspd_staging (
                x DOUBLE PRECISION,
                y DOUBLE PRECISION,
                objectid INTEGER,
                pcd TEXT,
                pcd2 TEXT,
                pcds TEXT,
                dointr TEXT,
                doterm TEXT,
                oscty TEXT,
                ced TEXT,
                oslaua TEXT,
                osward TEXT,
                parish TEXT,
                usertype TEXT,
                oseast1m TEXT,
                osnrth1m TEXT,
                osgrdind TEXT,
                oshlthau TEXT,
                nhser TEXT,
                ctry TEXT,
                rgn TEXT,
                streg TEXT,
                pcon TEXT,
                eer TEXT,
                teclec TEXT,
                ttwa TEXT,
                pct TEXT,
                itl TEXT,
                statsward TEXT,
                oa01 TEXT,
                casward TEXT,
                npark TEXT,
                lsoa01 TEXT,
                msoa01 TEXT,
                ur01ind TEXT,
                oac01 TEXT,
                oa11 TEXT,
                lsoa11 TEXT,
                msoa11 TEXT,
                wz11 TEXT,
                sicbl TEXT,
                bua24 TEXT,
                ru11ind TEXT,
                oac11 TEXT,
                lat DOUBLE PRECISION,
                long DOUBLE PRECISION,
                lep1 TEXT,
                lep2 TEXT,
                pfa TEXT,
                imd TEXT,
                calncv TEXT,
                icb TEXT,
                oa21 TEXT,
                lsoa21 TEXT,
                msoa21 TEXT,
                ruc21ind TEXT,
                GlobalID TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS os_open_map_local_staging (
                feature_id TEXT,
                feature_type TEXT,
                feature_description TEXT,
                theme TEXT,
                geometry GEOMETRY(Geometry, 27700),
                source TEXT
            );
            """
        ]
        
        for i, sql in enumerate(staging_tables_sql, 1):
            table_name = ["gazetteer_staging", "os_open_uprn_staging", "code_point_open_staging", "onspd_staging", "os_open_map_local_staging"][i-1]
            run_sql(engine, sql, description=f"Creating {table_name} table")
    
    run_migration_step(5, "Staging Tables", create_staging_tables)
    
    # Step 6: Create master gazetteer table
    def create_master_gazetteer():
        if os.path.exists('master_gazetteer_schema.sql'):
            run_sql_file(engine, 'master_gazetteer_schema.sql', "Creating master gazetteer table from schema file")
        else:
            print("⚠️  master_gazetteer_schema.sql not found, using inline schema...")
            # Fallback to inline schema
            run_sql(engine, """
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
            """, description="Creating master gazetteer table")
    
    run_migration_step(6, "Master Gazetteer Table", create_master_gazetteer)
    
    # Step 7: Create forecasting system tables
    def create_forecasting_tables():
        if os.path.exists('forecasting_system_schema.sql'):
            run_sql_file(engine, 'forecasting_system_schema.sql', "Creating forecasting system tables from schema file")
        else:
            print("⚠️  forecasting_system_schema.sql not found, using inline schema...")
            # Fallback to basic forecasting tables
            forecasting_tables_sql = [
                """
                CREATE TABLE IF NOT EXISTS forecasting_models (
                    id SERIAL PRIMARY KEY,
                    model_name VARCHAR(100) NOT NULL,
                    model_version VARCHAR(20) NOT NULL,
                    model_type VARCHAR(50) NOT NULL,
                    model_description TEXT,
                    model_parameters JSONB,
                    training_data_start_date DATE,
                    training_data_end_date DATE,
                    model_accuracy_score NUMERIC,
                    model_performance_metrics JSONB,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100),
                    notes TEXT
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS forecasts (
                    id SERIAL PRIMARY KEY,
                    model_id INTEGER REFERENCES forecasting_models(id),
                    property_id INTEGER REFERENCES master_gazetteer(id),
                    forecast_period_start DATE NOT NULL,
                    forecast_period_end DATE NOT NULL,
                    forecast_date DATE NOT NULL,
                    forecasted_rateable_value NUMERIC,
                    forecasted_annual_charge NUMERIC,
                    forecasted_net_charge NUMERIC,
                    confidence_interval_lower NUMERIC,
                    confidence_interval_upper NUMERIC,
                    confidence_score NUMERIC,
                    forecast_factors JSONB,
                    forecast_assumptions JSONB,
                    forecast_scenario VARCHAR(50),
                    actual_value NUMERIC,
                    forecast_error NUMERIC,
                    is_validated BOOLEAN DEFAULT FALSE,
                    validation_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100),
                    notes TEXT
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS non_rated_properties (
                    id SERIAL PRIMARY KEY,
                    uprn BIGINT,
                    property_address TEXT,
                    postcode VARCHAR(16),
                    property_type VARCHAR(64),
                    building_type VARCHAR(64),
                    floor_area NUMERIC,
                    number_of_floors INTEGER,
                    construction_year INTEGER,
                    x_coordinate DOUBLE PRECISION,
                    y_coordinate DOUBLE PRECISION,
                    latitude DOUBLE PRECISION,
                    longitude DOUBLE PRECISION,
                    geom GEOMETRY(Point, 27700),
                    lad_code VARCHAR(10),
                    lad_name TEXT,
                    ward_code VARCHAR(10),
                    ward_name TEXT,
                    business_activity_indicator BOOLEAN,
                    business_name TEXT,
                    business_type VARCHAR(64),
                    business_sector VARCHAR(64),
                    estimated_rateable_value NUMERIC,
                    estimated_annual_charge NUMERIC,
                    rating_potential_score NUMERIC,
                    rating_potential_factors JSONB,
                    investigation_status VARCHAR(32),
                    investigation_date DATE,
                    investigation_notes TEXT,
                    investigator VARCHAR(100),
                    data_sources JSONB,
                    discovery_date DATE,
                    last_verified_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100),
                    notes TEXT
                );
                """
            ]
            
            for i, sql in enumerate(forecasting_tables_sql, 1):
                table_name = ["forecasting_models", "forecasts", "non_rated_properties"][i-1]
                run_sql(engine, sql, description=f"Creating {table_name} table")
    
    run_migration_step(7, "Forecasting System Tables", create_forecasting_tables)
    
    # Step 8: Create indexes
    def create_indexes():
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS properties_ba_reference_idx ON properties(ba_reference);",
            "CREATE INDEX IF NOT EXISTS properties_postcode_idx ON properties(postcode);",
            "CREATE INDEX IF NOT EXISTS ratepayers_property_id_idx ON ratepayers(property_id);",
            "CREATE INDEX IF NOT EXISTS valuations_property_id_idx ON valuations(property_id);",
            "CREATE INDEX IF NOT EXISTS valuations_ba_reference_idx ON valuations(ba_reference);",
            "CREATE INDEX IF NOT EXISTS historic_valuations_property_id_idx ON historic_valuations(property_id);",
            "CREATE INDEX IF NOT EXISTS gazetteer_property_id_idx ON gazetteer(property_id);",
            "CREATE INDEX IF NOT EXISTS gazetteer_postcode_idx ON gazetteer(postcode);",
            "CREATE INDEX IF NOT EXISTS os_open_names_geom_idx ON os_open_names USING GIST (geom);",
            "CREATE INDEX IF NOT EXISTS lad_boundaries_geom_idx ON lad_boundaries USING GIST (geometry);",
            "CREATE INDEX IF NOT EXISTS os_open_map_local_geom_idx ON os_open_map_local USING GIST (geometry);",
            "CREATE INDEX IF NOT EXISTS master_gazetteer_uprn_idx ON master_gazetteer(uprn);",
            "CREATE INDEX IF NOT EXISTS master_gazetteer_ba_reference_idx ON master_gazetteer(ba_reference);",
            "CREATE INDEX IF NOT EXISTS master_gazetteer_postcode_idx ON master_gazetteer(postcode);",
            "CREATE INDEX IF NOT EXISTS master_gazetteer_geom_idx ON master_gazetteer USING GIST(geom);",
            "CREATE INDEX IF NOT EXISTS forecasts_property_id_idx ON forecasts(property_id);",
            "CREATE INDEX IF NOT EXISTS forecasts_period_idx ON forecasts(forecast_period_start, forecast_period_end);",
            "CREATE INDEX IF NOT EXISTS non_rated_properties_uprn_idx ON non_rated_properties(uprn);",
            "CREATE INDEX IF NOT EXISTS non_rated_properties_geom_idx ON non_rated_properties USING GIST(geom);"
        ]
        
        for i, sql in enumerate(indexes_sql, 1):
            run_sql(engine, sql, description=f"Creating index {i}/{len(indexes_sql)}")
    
    run_migration_step(8, "Database Indexes", create_indexes)
    
    # Step 9: Populate master gazetteer (optional)
    def populate_master_gazetteer():
        print("🔄 Populating Master Gazetteer Table...")
        
        # Import the population function
        try:
            from populate_master_gazetteer import populate_master_gazetteer as populate_func
            populate_func()
        except ImportError:
            print("⚠️  populate_master_gazetteer.py not found, skipping population")
        except Exception as e:
            print(f"⚠️  Error during population: {e}")
    
    # Ask user if they want to populate the master gazetteer
    print("\n" + "="*60)
    print("POPULATION OPTION")
    print("="*60)
    response = input("Do you want to populate the master gazetteer table now? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        run_migration_step(9, "Master Gazetteer Population", populate_master_gazetteer)
    else:
        print("⏭️  Skipping master gazetteer population")
    
    # Final summary
    print(f"\n{'='*60}")
    print("🎉 COMPLETE DATABASE SETUP FINISHED")
    print(f"{'='*60}")
    print(f"📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🗄️  Database: {dbname}")
    print(f"🏗️  Tables created: Core NNDR (5), Geospatial (7), Staging (5), Master Gazetteer (1), Forecasting (3+)")
    print(f"📊 Indexes created: 19+ performance indexes")
    print(f"🌍 PostGIS extension: Enabled")
    
    print("\n📋 Next steps:")
    print("1. Run data ingestion scripts to populate tables")
    print("2. Execute populate_master_gazetteer.py to consolidate data")
    print("3. Begin developing forecasting models")
    print("4. Implement non-rated property detection algorithms")
    
    print("\n✅ Database setup completed successfully!")

def main():
    """Main function"""
    print("🚀 Complete Database Setup Script")
    print("This script will create all database tables and indexes in the correct order.")
    print("Similar to Liquibase functionality for database migrations.\n")
    
    try:
        run_complete_db_setup()
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 