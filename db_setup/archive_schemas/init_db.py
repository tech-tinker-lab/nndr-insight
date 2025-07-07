#!/usr/bin/env python3
"""
Initialize NNDR database with normalized schema and PostGIS support.
Supports environment variables and optional database recreation.
"""
import sqlalchemy
from sqlalchemy import text
from db_config import get_connection_string, print_config, check_drop_recreate_arg, DB_CONFIG

def main():
    # Print current configuration
    print_config()
    
    # Check if we should drop and recreate the database
    drop_recreate = check_drop_recreate_arg()
    
    if drop_recreate:
        print(f"🔄 Dropping and recreating database '{DB_CONFIG['DBNAME']}'...")
        # Connect to default 'postgres' database to manage target DB
        admin_engine = sqlalchemy.create_engine(get_connection_string("postgres"))
        with admin_engine.connect() as conn:
            conn = conn.execution_options(isolation_level="AUTOCOMMIT")
            # Check if DB exists
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{DB_CONFIG['DBNAME']}'"))
            exists = result.scalar() is not None
            if exists:
                conn.execute(text(f"DROP DATABASE {DB_CONFIG['DBNAME']}"))
                print(f"Database '{DB_CONFIG['DBNAME']}' dropped.")
            conn.execute(text(f"CREATE DATABASE {DB_CONFIG['DBNAME']}"))
            print(f"Database '{DB_CONFIG['DBNAME']}' created.")
    else:
        print(f"📋 Using existing database '{DB_CONFIG['DBNAME']}' (use --drop-recreate to recreate)...")
        # Check if database exists, create if it doesn't
        admin_engine = sqlalchemy.create_engine(get_connection_string("postgres"))
        with admin_engine.connect() as conn:
            conn = conn.execution_options(isolation_level="AUTOCOMMIT")
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{DB_CONFIG['DBNAME']}'"))
            exists = result.scalar() is not None
            if not exists:
                print(f"Database '{DB_CONFIG['DBNAME']}' doesn't exist, creating...")
                conn.execute(text(f"CREATE DATABASE {DB_CONFIG['DBNAME']}"))
                print(f"Database '{DB_CONFIG['DBNAME']}' created.")
            else:
                print(f"Database '{DB_CONFIG['DBNAME']}' already exists.")

    # Connect to the target database
    engine = sqlalchemy.create_engine(get_connection_string())

    with engine.connect() as conn:
        with conn.begin():
            # Enable PostGIS extension (if not already)
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            print("PostGIS extension enabled.")

            # Create tables
            conn.execute(text("""
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
            """))

            conn.execute(text("""
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
            """))

            conn.execute(text("""
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
            """))

            conn.execute(text("""
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
            """))

            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS categories (
                code TEXT PRIMARY KEY,
                description TEXT
            );
            """))

            conn.execute(text("""
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
            """))

            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS gazetteer_staging (
                uprn BIGINT,
                x_coordinate DOUBLE PRECISION,
                y_coordinate DOUBLE PRECISION,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION
            );
            """))

            conn.execute(text("""
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
            """))

            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS os_open_uprn (
                uprn BIGINT PRIMARY KEY,
                x_coordinate DOUBLE PRECISION,
                y_coordinate DOUBLE PRECISION,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                source TEXT
            );
            """))

            conn.execute(text("""
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
            """))

            conn.execute(text("""
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
            """))

    print("✅ Database initialized with normalized NNDR schema and PostGIS support.")

if __name__ == "__main__":
    main()
