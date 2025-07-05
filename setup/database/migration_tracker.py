#!/usr/bin/env python3
"""
Migration Tracker
This module tracks database migrations to ensure they run only once, similar to Liquibase functionality.
"""
import sqlalchemy
from sqlalchemy import text
from db_config import get_connection_string, DB_CONFIG
import hashlib
from datetime import datetime

class MigrationTracker:
    def __init__(self, engine):
        self.engine = engine
        self.ensure_migration_table()
    
    def ensure_migration_table(self):
        """Create the migration tracking table if it doesn't exist"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS db_migrations (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) UNIQUE NOT NULL,
            migration_hash VARCHAR(64) NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            execution_time_ms INTEGER,
            status VARCHAR(20) DEFAULT 'SUCCESS',
            error_message TEXT,
            created_by VARCHAR(100) DEFAULT 'system'
        );
        """
        
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(text(create_table_sql))
    
    def get_migration_hash(self, content):
        """Generate a hash for migration content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def is_migration_applied(self, migration_name, migration_hash):
        """Check if a migration has already been applied"""
        with self.engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, migration_hash FROM db_migrations WHERE migration_name = :name"),
                {"name": migration_name}
            )
            row = result.fetchone()
            
            if row:
                stored_hash = row[1]
                if stored_hash != migration_hash:
                    raise Exception(f"Migration {migration_name} has been modified since last run. "
                                  f"Stored hash: {stored_hash}, Current hash: {migration_hash}")
                return True
            return False
    
    def record_migration_start(self, migration_name, migration_hash):
        """Record the start of a migration"""
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(
                    text("""
                        INSERT INTO db_migrations (migration_name, migration_hash, status, applied_at)
                        VALUES (:name, :hash, 'RUNNING', CURRENT_TIMESTAMP)
                    """),
                    {"name": migration_name, "hash": migration_hash}
                )
    
    def record_migration_success(self, migration_name, execution_time_ms):
        """Record successful completion of a migration"""
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(
                    text("""
                        UPDATE db_migrations 
                        SET status = 'SUCCESS', execution_time_ms = :exec_time
                        WHERE migration_name = :name
                    """),
                    {"name": migration_name, "exec_time": execution_time_ms}
                )
    
    def record_migration_failure(self, migration_name, error_message):
        """Record failed migration"""
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(
                    text("""
                        UPDATE db_migrations 
                        SET status = 'FAILED', error_message = :error
                        WHERE migration_name = :name
                    """),
                    {"name": migration_name, "error": error_message}
                )
    
    def get_applied_migrations(self):
        """Get list of applied migrations"""
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT migration_name, applied_at, execution_time_ms, status
                    FROM db_migrations 
                    ORDER BY applied_at
                """)
            )
            return result.fetchall()
    
    def get_pending_migrations(self, available_migrations):
        """Get list of migrations that haven't been applied"""
        applied_migrations = {row[0] for row in self.get_applied_migrations()}
        return [m for m in available_migrations if m not in applied_migrations]

def run_migration_with_tracking(tracker, migration_name, migration_content, migration_function):
    """Run a migration with tracking"""
    migration_hash = tracker.get_migration_hash(migration_content)
    
    # Check if already applied
    if tracker.is_migration_applied(migration_name, migration_hash):
        print(f"⏭️  Migration '{migration_name}' already applied, skipping")
        return True
    
    print(f"🔄 Running migration: {migration_name}")
    start_time = datetime.now()
    
    try:
        # Record migration start
        tracker.record_migration_start(migration_name, migration_hash)
        
        # Execute migration
        migration_function()
        
        # Record success
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        tracker.record_migration_success(migration_name, int(execution_time))
        
        print(f"✅ Migration '{migration_name}' completed successfully")
        return True
        
    except Exception as e:
        # Record failure
        tracker.record_migration_failure(migration_name, str(e))
        print(f"❌ Migration '{migration_name}' failed: {e}")
        raise

def print_migration_status(tracker):
    """Print current migration status"""
    print("\n📊 Migration Status:")
    print("=" * 80)
    
    applied_migrations = tracker.get_applied_migrations()
    
    if not applied_migrations:
        print("No migrations have been applied yet.")
        return
    
    print(f"{'Migration Name':<40} {'Applied At':<20} {'Status':<10} {'Time (ms)':<10}")
    print("-" * 80)
    
    for migration in applied_migrations:
        name, applied_at, exec_time, status = migration
        applied_str = applied_at.strftime('%Y-%m-%d %H:%M:%S') if applied_at else 'N/A'
        exec_time_str = str(exec_time) if exec_time else 'N/A'
        
        status_icon = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "🔄"
        
        print(f"{name:<40} {applied_str:<20} {status_icon} {status:<7} {exec_time_str:<10}")

def create_migration_summary(tracker):
    """Create a summary of migration status"""
    applied_migrations = tracker.get_applied_migrations()
    
    total_migrations = len(applied_migrations)
    successful_migrations = len([m for m in applied_migrations if m[3] == 'SUCCESS'])
    failed_migrations = len([m for m in applied_migrations if m[3] == 'FAILED'])
    running_migrations = len([m for m in applied_migrations if m[3] == 'RUNNING'])
    
    total_time = sum(m[2] for m in applied_migrations if m[2] is not None)
    
    print(f"\n📈 Migration Summary:")
    print(f"   Total Migrations: {total_migrations}")
    print(f"   Successful: {successful_migrations}")
    print(f"   Failed: {failed_migrations}")
    print(f"   Running: {running_migrations}")
    print(f"   Total Execution Time: {total_time:.0f}ms")
    
    if failed_migrations > 0:
        print(f"\n⚠️  {failed_migrations} migration(s) have failed. Check the migration log for details.")
    
    if running_migrations > 0:
        print(f"\n🔄 {running_migrations} migration(s) are currently running or were interrupted.")

# Example usage functions
def get_available_migrations():
    """Define available migrations"""
    return [
        "001_create_core_tables",
        "002_create_geospatial_tables", 
        "003_create_staging_tables",
        "004_create_master_gazetteer",
        "005_create_forecasting_tables",
        "006_create_indexes",
        "007_populate_master_gazetteer"
    ]

def run_migration_001_create_core_tables(engine):
    """Migration 001: Create core NNDR tables"""
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
    
    for sql in core_tables_sql:
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text(sql))

def run_migration_002_create_geospatial_tables(engine):
    """Migration 002: Create geospatial tables"""
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
    
    for sql in geospatial_tables_sql:
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text(sql))

def run_migration_003_create_staging_tables(engine):
    """Migration 003: Create staging tables"""
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
    
    for sql in staging_tables_sql:
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text(sql))

def run_migration_004_create_master_gazetteer(engine):
    """Migration 004: Create master gazetteer table"""
    master_gazetteer_sql = """
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
    
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text(master_gazetteer_sql))

def run_migration_005_create_forecasting_tables(engine):
    """Migration 005: Create forecasting system tables"""
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
        """,
        """
        CREATE TABLE IF NOT EXISTS forecasting_scenarios (
            id SERIAL PRIMARY KEY,
            scenario_name VARCHAR(100) NOT NULL,
            scenario_description TEXT,
            scenario_type VARCHAR(50),
            economic_growth_rate NUMERIC,
            inflation_rate NUMERIC,
            market_growth_rate NUMERIC,
            policy_changes JSONB,
            scenario_start_date DATE,
            scenario_end_date DATE,
            expected_impact_on_rates NUMERIC,
            confidence_level NUMERIC,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(100),
            notes TEXT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS forecasting_reports (
            id SERIAL PRIMARY KEY,
            report_name VARCHAR(200) NOT NULL,
            report_type VARCHAR(50),
            report_period_start DATE,
            report_period_end DATE,
            total_properties_count INTEGER,
            total_rateable_value NUMERIC,
            total_annual_charge NUMERIC,
            total_net_charge NUMERIC,
            forecasted_total_rateable_value NUMERIC,
            forecasted_total_annual_charge NUMERIC,
            forecasted_total_net_charge NUMERIC,
            non_rated_properties_count INTEGER,
            potential_additional_rateable_value NUMERIC,
            potential_additional_annual_charge NUMERIC,
            report_data JSONB,
            report_format VARCHAR(20),
            report_file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(100),
            notes TEXT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS property_valuation_history (
            id SERIAL PRIMARY KEY,
            property_id INTEGER REFERENCES master_gazetteer(id),
            valuation_date DATE NOT NULL,
            rateable_value NUMERIC,
            effective_date DATE,
            scat_code VARCHAR(16),
            description TEXT,
            previous_rateable_value NUMERIC,
            value_change NUMERIC,
            percentage_change NUMERIC,
            revaluation_type VARCHAR(32),
            appeal_status VARCHAR(32),
            appeal_settlement_code VARCHAR(16),
            source VARCHAR(50),
            source_reference VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS market_analysis (
            id SERIAL PRIMARY KEY,
            analysis_date DATE NOT NULL,
            lad_code VARCHAR(10),
            property_category_code VARCHAR(16),
            average_rateable_value NUMERIC,
            median_rateable_value NUMERIC,
            market_trend VARCHAR(20),
            market_volatility NUMERIC,
            total_properties_count INTEGER,
            vacant_properties_count INTEGER,
            new_properties_count INTEGER,
            demolished_properties_count INTEGER,
            local_economic_growth_rate NUMERIC,
            employment_rate NUMERIC,
            business_formation_rate NUMERIC,
            market_outlook VARCHAR(20),
            confidence_score NUMERIC,
            analysis_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(100),
            notes TEXT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS compliance_enforcement (
            id SERIAL PRIMARY KEY,
            property_id INTEGER REFERENCES master_gazetteer(id),
            compliance_status VARCHAR(32),
            compliance_score NUMERIC,
            enforcement_action_type VARCHAR(50),
            enforcement_action_date DATE,
            enforcement_action_description TEXT,
            enforcement_action_amount NUMERIC,
            investigation_start_date DATE,
            investigation_end_date DATE,
            investigation_outcome VARCHAR(50),
            investigation_notes TEXT,
            risk_level VARCHAR(20),
            risk_factors JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(100),
            notes TEXT
        );
        """
    ]
    
    for sql in forecasting_tables_sql:
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text(sql))

def run_migration_006_create_indexes(engine):
    """Migration 006: Create database indexes"""
    indexes_sql = [
        # Core table indexes
        "CREATE INDEX IF NOT EXISTS properties_ba_reference_idx ON properties(ba_reference);",
        "CREATE INDEX IF NOT EXISTS properties_postcode_idx ON properties(postcode);",
        "CREATE INDEX IF NOT EXISTS ratepayers_property_id_idx ON ratepayers(property_id);",
        "CREATE INDEX IF NOT EXISTS valuations_property_id_idx ON valuations(property_id);",
        "CREATE INDEX IF NOT EXISTS valuations_ba_reference_idx ON valuations(ba_reference);",
        "CREATE INDEX IF NOT EXISTS historic_valuations_property_id_idx ON historic_valuations(property_id);",
        
        # Geospatial table indexes
        "CREATE INDEX IF NOT EXISTS gazetteer_property_id_idx ON gazetteer(property_id);",
        "CREATE INDEX IF NOT EXISTS gazetteer_postcode_idx ON gazetteer(postcode);",
        "CREATE INDEX IF NOT EXISTS os_open_names_geom_idx ON os_open_names USING GIST (geom);",
        "CREATE INDEX IF NOT EXISTS lad_boundaries_geom_idx ON lad_boundaries USING GIST (geometry);",
        "CREATE INDEX IF NOT EXISTS os_open_map_local_geom_idx ON os_open_map_local USING GIST (geometry);",
        
        # Master gazetteer indexes
        "CREATE INDEX IF NOT EXISTS master_gazetteer_uprn_idx ON master_gazetteer(uprn);",
        "CREATE INDEX IF NOT EXISTS master_gazetteer_ba_reference_idx ON master_gazetteer(ba_reference);",
        "CREATE INDEX IF NOT EXISTS master_gazetteer_postcode_idx ON master_gazetteer(postcode);",
        "CREATE INDEX IF NOT EXISTS master_gazetteer_geom_idx ON master_gazetteer USING GIST(geom);",
        "CREATE INDEX IF NOT EXISTS master_gazetteer_category_idx ON master_gazetteer(property_category_code);",
        "CREATE INDEX IF NOT EXISTS master_gazetteer_rateable_value_idx ON master_gazetteer(current_rateable_value);",
        "CREATE INDEX IF NOT EXISTS master_gazetteer_forecast_idx ON master_gazetteer(forecast_rateable_value);",
        "CREATE INDEX IF NOT EXISTS master_gazetteer_lad_category_idx ON master_gazetteer(lad_code, property_category_code);",
        "CREATE INDEX IF NOT EXISTS master_gazetteer_postcode_category_idx ON master_gazetteer(postcode, property_category_code);",
        "CREATE INDEX IF NOT EXISTS master_gazetteer_value_range_idx ON master_gazetteer(current_rateable_value, forecast_rateable_value);",
        
        # Forecasting table indexes
        "CREATE INDEX IF NOT EXISTS forecasts_model_id_idx ON forecasts(model_id);",
        "CREATE INDEX IF NOT EXISTS forecasts_property_id_idx ON forecasts(property_id);",
        "CREATE INDEX IF NOT EXISTS forecasts_period_idx ON forecasts(forecast_period_start, forecast_period_end);",
        "CREATE INDEX IF NOT EXISTS forecasts_date_idx ON forecasts(forecast_date);",
        "CREATE INDEX IF NOT EXISTS non_rated_properties_uprn_idx ON non_rated_properties(uprn);",
        "CREATE INDEX IF NOT EXISTS non_rated_properties_lad_idx ON non_rated_properties(lad_code);",
        "CREATE INDEX IF NOT EXISTS non_rated_properties_status_idx ON non_rated_properties(investigation_status);",
        "CREATE INDEX IF NOT EXISTS non_rated_properties_potential_idx ON non_rated_properties(rating_potential_score);",
        "CREATE INDEX IF NOT EXISTS non_rated_properties_geom_idx ON non_rated_properties USING GIST(geom);",
        "CREATE INDEX IF NOT EXISTS property_valuation_history_property_idx ON property_valuation_history(property_id);",
        "CREATE INDEX IF NOT EXISTS property_valuation_history_date_idx ON property_valuation_history(valuation_date);",
        "CREATE INDEX IF NOT EXISTS market_analysis_lad_category_idx ON market_analysis(lad_code, property_category_code);",
        "CREATE INDEX IF NOT EXISTS market_analysis_date_idx ON market_analysis(analysis_date);",
        "CREATE INDEX IF NOT EXISTS compliance_enforcement_property_idx ON compliance_enforcement(property_id);",
        "CREATE INDEX IF NOT EXISTS compliance_enforcement_status_idx ON compliance_enforcement(compliance_status);",
        "CREATE INDEX IF NOT EXISTS compliance_enforcement_risk_idx ON compliance_enforcement(risk_level);"
    ]
    
    for sql in indexes_sql:
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text(sql))

def run_migration_007_populate_master_gazetteer(engine):
    """Migration 007: Populate master gazetteer"""
    # This migration will populate the master gazetteer table with data from existing tables
    # It's similar to the populate_master_gazetteer.py script but integrated into the migration system
    
    print("🔄 Populating Master Gazetteer Table...")
    
    try:
        # Step 1: Populate from properties table
        print("   Step 1: Populating from properties table...")
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
            NULL,  -- address_line_2
            NULL,  -- address_line_3
            NULL,  -- address_line_4
            NULL,  -- address_line_5
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
        
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text(properties_sql))
        print("   ✅ Properties data populated")
        
        # Step 2: Populate from gazetteer table (if it exists and has data)
        print("   Step 2: Populating from gazetteer table...")
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
        
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text(gazetteer_sql))
        print("   ✅ Gazetteer data populated")
        
        # Step 3: Populate from os_open_uprn table (if it exists and has data)
        print("   Step 3: Populating from OS Open UPRN table...")
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
            geom = EXCLUDED.geom,
            updated_at = CURRENT_TIMESTAMP;
        """
        
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text(uprn_sql))
        print("   ✅ OS Open UPRN data populated")
        
        # Step 4: Enrich with ONSPD data (if it exists and has data)
        print("   Step 4: Enriching with ONSPD data...")
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
        
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text(onspd_sql))
        print("   ✅ ONSPD data enrichment completed")
        
        # Step 5: Enrich with ratepayer information (if it exists and has data)
        print("   Step 5: Enriching with ratepayer information...")
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
        
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text(ratepayer_sql))
        print("   ✅ Ratepayer data enrichment completed")
        
        # Step 6: Calculate data quality scores
        print("   Step 6: Calculating data quality scores...")
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
        
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text(quality_sql))
        print("   ✅ Data quality scores calculated")
        
        # Step 7: Generate summary statistics
        print("   Step 7: Generating summary statistics...")
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
        
        with engine.connect() as conn:
            result = conn.execute(text(summary_sql))
            stats = result.fetchone()
        
        print(f"\n📈 Master Gazetteer Population Summary:")
        print(f"   Total Properties: {stats[0]:,}")
        print(f"   Rated Properties: {stats[1]:,}")
        print(f"   Non-Rated Properties: {stats[2]:,}")
        print(f"   Properties with Values: {stats[3]:,}")
        print(f"   Average Data Quality: {stats[4]:.1f}/100")
        print(f"   Total Rateable Value: £{stats[5]:,.0f}" if stats[5] else "   Total Rateable Value: £0")
        
        print("✅ Master gazetteer population completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during master gazetteer population: {e}")
        print("This migration can be safely retried - it uses ON CONFLICT clauses")
        raise

# Migration registry
MIGRATION_REGISTRY = {
    "001_create_core_tables": run_migration_001_create_core_tables,
    "002_create_geospatial_tables": run_migration_002_create_geospatial_tables,
    "003_create_staging_tables": run_migration_003_create_staging_tables,
    "004_create_master_gazetteer": run_migration_004_create_master_gazetteer,
    "005_create_forecasting_tables": run_migration_005_create_forecasting_tables,
    "006_create_indexes": run_migration_006_create_indexes,
    "007_populate_master_gazetteer": run_migration_007_populate_master_gazetteer,
} 