#!/usr/bin/env python3
"""
Create Fresh Database Script for NNDR Insight Project
This script creates a complete database schema with all tables and indexes in one go.
Supports environment variables and optional database recreation.
"""
import sqlalchemy
from sqlalchemy import text
from db_config import get_connection_string, print_config, check_drop_recreate_arg, DB_CONFIG

def create_engine_for_db(dbname):
    return sqlalchemy.create_engine(get_connection_string(dbname))

def run_ddl(engine, ddl):
    with engine.connect() as conn:
        with conn.begin():
            for stmt in ddl:
                conn.execute(text(stmt))

def main():
    # Print current configuration
    print_config()
    
    # Check if we should drop and recreate the database
    drop_recreate = check_drop_recreate_arg()
    
    if drop_recreate:
        print(f"🔄 Dropping and recreating database '{DB_CONFIG['DBNAME']}'...")
        # Connect to default DB to drop/create target DB
        admin_engine = create_engine_for_db("postgres")
        with admin_engine.connect() as conn:
            conn = conn.execution_options(isolation_level="AUTOCOMMIT")
            if conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{DB_CONFIG['DBNAME']}'")).scalar():
                conn.execute(text(f"DROP DATABASE {DB_CONFIG['DBNAME']}"))
                print(f"Database '{DB_CONFIG['DBNAME']}' dropped.")
            conn.execute(text(f"CREATE DATABASE {DB_CONFIG['DBNAME']}"))
            print(f"Database '{DB_CONFIG['DBNAME']}' created.")
    else:
        print(f"📋 Using existing database '{DB_CONFIG['DBNAME']}' (use --drop-recreate to recreate)...")
        # Check if database exists, create if it doesn't
        admin_engine = create_engine_for_db("postgres")
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
    engine = create_engine_for_db(DB_CONFIG['DBNAME'])
    
    # Complete DDL for all tables and indexes
    ddl = [
        # Enable PostGIS extension
        "CREATE EXTENSION IF NOT EXISTS postgis;",
        
        # Core NNDR Tables
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
        """,
        
        # Geospatial Tables
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
            id SERIAL PRIMARY KEY,
            uprn BIGINT UNIQUE,
            x_coordinate NUMERIC,
            y_coordinate NUMERIC,
            latitude NUMERIC,
            longitude NUMERIC
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
        
        # Spatial indexes for OS Open Names
        "CREATE INDEX IF NOT EXISTS os_open_names_geom_idx ON os_open_names USING GIST (geom);",
        
        # LAD boundaries (geometry)
        """
        CREATE TABLE IF NOT EXISTS lad_boundaries (
            id SERIAL PRIMARY KEY,
            lad_code TEXT,
            lad_name TEXT,
            geometry GEOMETRY(MultiPolygon, 27700)
        );
        """,
        "CREATE INDEX IF NOT EXISTS lad_boundaries_geom_idx ON lad_boundaries USING GIST (geometry);",
        
        # OS Open Map Local
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
        """,
        "CREATE INDEX IF NOT EXISTS os_open_map_local_geom_idx ON os_open_map_local USING GIST (geometry);",
        
        # NNDR Rating List (simplified)
        """
        CREATE TABLE IF NOT EXISTS nndr_rating_list (
            id SERIAL PRIMARY KEY,
            property_id VARCHAR(64),
            ratepayer_name TEXT,
            rateable_value NUMERIC,
            effective_date DATE,
            source TEXT
        );
        """,
        
        # Staging Tables
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
        """,
        
        # Additional indexes for performance
        "CREATE INDEX IF NOT EXISTS properties_ba_reference_idx ON properties(ba_reference);",
        "CREATE INDEX IF NOT EXISTS properties_postcode_idx ON properties(postcode);",
        "CREATE INDEX IF NOT EXISTS ratepayers_property_id_idx ON ratepayers(property_id);",
        "CREATE INDEX IF NOT EXISTS valuations_property_id_idx ON valuations(property_id);",
        "CREATE INDEX IF NOT EXISTS valuations_ba_reference_idx ON valuations(ba_reference);",
        "CREATE INDEX IF NOT EXISTS historic_valuations_property_id_idx ON historic_valuations(property_id);",
        "CREATE INDEX IF NOT EXISTS gazetteer_property_id_idx ON gazetteer(property_id);",
        "CREATE INDEX IF NOT EXISTS gazetteer_postcode_idx ON gazetteer(postcode);",
        "CREATE INDEX IF NOT EXISTS code_point_open_postcode_idx ON code_point_open(postcode);",
        "CREATE INDEX IF NOT EXISTS onspd_pcds_idx ON onspd(pcds);",
    ]
    
    try:
        run_ddl(engine, ddl)
        print("✅ Complete database schema created successfully!")
        print(f"📊 Created {len(ddl)} DDL statements including:")
        print("   - Core NNDR tables (properties, ratepayers, valuations, historic_valuations)")
        print("   - Geospatial tables (gazetteer, os_open_uprn, code_point_open, onspd)")
        print("   - OS Open data tables (os_open_names, os_open_map_local, lad_boundaries)")
        print("   - Staging tables for data ingestion")
        print("   - Spatial indexes for geospatial queries")
        print("   - Performance indexes for common queries")
        print("   - PostGIS extension enabled")
        
    except Exception as e:
        print(f"❌ Error creating database schema: {e}")
        raise

if __name__ == "__main__":
    main() 