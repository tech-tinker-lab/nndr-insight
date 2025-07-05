#!/usr/bin/env python3
"""
Comprehensive NNDR Database Setup Script
A clean, efficient script that sets up the complete database schema and handles data ingestion
for the NNDR Insight project. Designed for performance and future growth.
"""

import os
import sys
import sqlalchemy
from sqlalchemy import text, create_engine
import pandas as pd
import geopandas as gpd
import logging
from pathlib import Path
import time
from datetime import datetime
import zipfile
import tempfile
import shutil
from typing import Dict, List, Optional, Tuple
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_db_setup.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveDatabaseSetup:
    """
    Comprehensive database setup and data ingestion for NNDR Insight project.
    Handles all data types efficiently with performance optimizations.
    """
    
    def __init__(self, db_config: Optional[Dict] = None):
        """Initialize the database setup process"""
        # Database configuration
        self.db_config = db_config or {
            'host': '192.168.1.79',
            'port': 5432,
            'database': 'nndr_db',
            'user': 'nndr',
            'password': 'nndrpass'
        }
        
        self.connection_string = (
            f"postgresql://{self.db_config['user']}:{self.db_config['password']}@"
            f"{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
        )
        
        self.engine = None
        self.conn = None
        
        # Data paths
        self.data_root = Path(__file__).parent.parent.parent / 'backend' / 'data'
        
        # Statistics tracking
        self.stats = {
            'tables_created': 0,
            'records_processed': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Performance settings
        self.chunk_size = 10000  # Records per batch
        self.max_workers = 4     # Parallel processing
        
        logger.info("Comprehensive Database Setup Initialized")
        logger.info(f"Target Database: {self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}")
        logger.info(f"Data Root: {self.data_root}")
    
    def connect(self) -> bool:
        """Establish database connection with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.engine = create_engine(
                    self.connection_string,
                    pool_pre_ping=True,
                    pool_size=10,
                    max_overflow=20,
                    pool_recycle=3600
                )
                self.conn = self.engine.connect()
                logger.info("Database connection established")
                return True
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    logger.error(f"Failed to connect after {max_retries} attempts")
                    return False
        return False  # Fallback return
    
    def disconnect(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
        if self.engine:
            self.engine.dispose()
        logger.info("Database connection closed")
    
    def execute_sql(self, sql: str, params: Optional[Dict] = None, description: str = "") -> bool:
        """Execute SQL with error handling and logging"""
        if not self.engine:
            logger.error("Database engine not initialized")
            return False
            
        if description:
            logger.info(f"Executing: {description}")
        
        try:
            with self.engine.connect() as conn:
                with conn.begin():
                    if params:
                        conn.execute(text(sql), params)
                    else:
                        conn.execute(text(sql))
            return True
        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            logger.error(f"SQL: {sql[:200]}...")
            self.stats['errors'] += 1
            return False
    
    def execute_sql_file(self, file_path: Path, description: str = "") -> bool:
        """Execute SQL from a file"""
        if description:
            logger.info(f"Loading file: {description}")
        
        try:
            with open(file_path, 'r') as f:
                sql_content = f.read()
            
            # Split into individual statements
            statements = [
                stmt.strip() for stmt in sql_content.split(';') 
                if stmt.strip() and not stmt.strip().startswith('--')
            ]
            
            for i, statement in enumerate(statements, 1):
                if statement:
                    logger.debug(f"   Executing statement {i}/{len(statements)}...")
                    if not self.execute_sql(statement):
                        return False
            
            logger.info(f"File execution completed: {description}")
            return True
            
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return False
        except Exception as e:
            logger.error(f"Error executing file {file_path}: {e}")
            return False
    
    def setup_database_schema(self) -> bool:
        """Set up the complete database schema"""
        logger.info("Setting up database schema...")
        
        # Step 1: Enable PostGIS extensions
        extensions = [
            "CREATE EXTENSION IF NOT EXISTS postgis;",
            "CREATE EXTENSION IF NOT EXISTS postgis_topology;",
            "CREATE EXTENSION IF NOT EXISTS postgis_raster;",
            "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;",
            'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";',
            "CREATE EXTENSION IF NOT EXISTS pg_trgm;",
            "CREATE EXTENSION IF NOT EXISTS btree_gin;",
            "CREATE EXTENSION IF NOT EXISTS btree_gist;"
        ]
        
        for ext in extensions:
            if not self.execute_sql(ext, description="Enabling PostgreSQL extensions"):
                return False
        
        # Step 2: Create core NNDR tables
        core_tables = self._get_core_tables_sql()
        for table_name, sql in core_tables.items():
            if self.execute_sql(sql, description=f"Creating {table_name} table"):
                self.stats['tables_created'] += 1
        
        # Step 3: Create geospatial tables
        geospatial_tables = self._get_geospatial_tables_sql()
        for table_name, sql in geospatial_tables.items():
            if self.execute_sql(sql, description=f"Creating {table_name} table"):
                self.stats['tables_created'] += 1
        
        # Step 4: Create master gazetteer
        gazetteer_sql = self._get_master_gazetteer_sql()
        if self.execute_sql(gazetteer_sql, description="Creating master gazetteer table"):
            self.stats['tables_created'] += 1
        
        # Step 5: Create forecasting tables
        forecasting_tables = self._get_forecasting_tables_sql()
        for table_name, sql in forecasting_tables.items():
            if self.execute_sql(sql, description=f"Creating {table_name} table"):
                self.stats['tables_created'] += 1
        
        # Step 6: Create indexes
        indexes = self._get_indexes_sql()
        for index_name, sql in indexes.items():
            self.execute_sql(sql, description=f"Creating {index_name}")
        
        logger.info(f"Database schema setup completed. Created {self.stats['tables_created']} tables.")
        return True
    
    def _get_core_tables_sql(self) -> Dict[str, str]:
        """Get SQL for core NNDR tables"""
        return {
            'properties': """
                CREATE TABLE IF NOT EXISTS properties (
                    id SERIAL PRIMARY KEY,
                    list_altered VARCHAR(32),
                    community_code VARCHAR(16),
                    ba_reference VARCHAR(32) UNIQUE NOT NULL,
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
                    rateable_value NUMERIC(15,2),
                    scat_code VARCHAR(16),
                    appeal_settlement_code VARCHAR(16),
                    unique_property_ref VARCHAR(64),
                    location GEOMETRY(POINT, 27700),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            'ratepayers': """
                CREATE TABLE IF NOT EXISTS ratepayers (
                    id SERIAL PRIMARY KEY,
                    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
                    name TEXT,
                    address TEXT,
                    company_number VARCHAR(32),
                    liability_start_date DATE,
                    liability_end_date DATE,
                    annual_charge NUMERIC(15,2),
                    exemption_amount NUMERIC(15,2),
                    exemption_code TEXT,
                    mandatory_amount NUMERIC(15,2),
                    mandatory_relief TEXT,
                    charity_relief_amount NUMERIC(15,2),
                    disc_relief_amount NUMERIC(15,2),
                    discretionary_charitable_relief TEXT,
                    additional_rlf TEXT,
                    additional_relief TEXT,
                    sbr_applied TEXT,
                    sbr_supplement TEXT,
                    sbr_amount NUMERIC(15,2),
                    charge_type TEXT,
                    report_date DATE,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            'valuations': """
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
                    rateable_value NUMERIC(15,2),
                    uprn BIGINT,
                    compiled_list_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
        }
    
    def _get_geospatial_tables_sql(self) -> Dict[str, str]:
        """Get SQL for geospatial tables"""
        return {
            'os_open_uprn': """
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
                    x_coordinate NUMERIC(10,3),
                    y_coordinate NUMERIC(10,3),
                    latitude NUMERIC(10,8),
                    longitude NUMERIC(11,8),
                    location GEOMETRY(POINT, 27700),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            'code_point_open': """
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
            
            'local_authority_districts': """
                CREATE TABLE IF NOT EXISTS local_authority_districts (
                    id SERIAL PRIMARY KEY,
                    lad_code VARCHAR(16),
                    lad_name VARCHAR(256),
                    geometry GEOMETRY(MULTIPOLYGON, 27700),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
        }
    
    def _get_master_gazetteer_sql(self) -> str:
        """Get SQL for master gazetteer table"""
        return """
            CREATE TABLE IF NOT EXISTS master_gazetteer (
                id SERIAL PRIMARY KEY,
                uprn BIGINT UNIQUE,
                ba_reference VARCHAR(32),
                property_address TEXT,
                street_descriptor TEXT,
                locality TEXT,
                post_town TEXT,
                administrative_area TEXT,
                postcode VARCHAR(16),
                property_category_code VARCHAR(16),
                property_description TEXT,
                rateable_value NUMERIC(15,2),
                effective_date DATE,
                x_coordinate NUMERIC(10,3),
                y_coordinate NUMERIC(10,3),
                latitude NUMERIC(10,8),
                longitude NUMERIC(11,8),
                geom GEOMETRY(POINT, 27700),
                lad_code VARCHAR(16),
                lad_name VARCHAR(256),
                data_sources JSONB,
                confidence_score NUMERIC(3,2),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
    
    def _get_forecasting_tables_sql(self) -> Dict[str, str]:
        """Get SQL for forecasting tables"""
        return {
            'forecasting_models': """
                CREATE TABLE IF NOT EXISTS forecasting_models (
                    id SERIAL PRIMARY KEY,
                    model_name VARCHAR(100) NOT NULL,
                    model_version VARCHAR(20) NOT NULL,
                    model_type VARCHAR(50) NOT NULL,
                    model_description TEXT,
                    model_parameters JSONB,
                    training_data_start_date DATE,
                    training_data_end_date DATE,
                    model_accuracy_score NUMERIC(5,4),
                    model_performance_metrics JSONB,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100),
                    notes TEXT
                );
            """,
            
            'forecasts': """
                CREATE TABLE IF NOT EXISTS forecasts (
                    id SERIAL PRIMARY KEY,
                    model_id INTEGER REFERENCES forecasting_models(id),
                    property_id INTEGER REFERENCES master_gazetteer(id),
                    forecast_period_start DATE NOT NULL,
                    forecast_period_end DATE NOT NULL,
                    forecast_date DATE NOT NULL,
                    forecasted_rateable_value NUMERIC(15,2),
                    forecasted_annual_charge NUMERIC(15,2),
                    forecasted_net_charge NUMERIC(15,2),
                    confidence_interval_lower NUMERIC(15,2),
                    confidence_interval_upper NUMERIC(15,2),
                    confidence_score NUMERIC(3,2),
                    forecast_factors JSONB,
                    forecast_assumptions JSONB,
                    forecast_scenario VARCHAR(50),
                    actual_value NUMERIC(15,2),
                    forecast_error NUMERIC(15,2),
                    is_validated BOOLEAN DEFAULT FALSE,
                    validation_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100),
                    notes TEXT
                );
            """,
            
            'non_rated_properties': """
                CREATE TABLE IF NOT EXISTS non_rated_properties (
                    id SERIAL PRIMARY KEY,
                    uprn BIGINT,
                    property_address TEXT,
                    postcode VARCHAR(16),
                    property_type VARCHAR(64),
                    building_type VARCHAR(64),
                    floor_area NUMERIC(10,2),
                    number_of_floors INTEGER,
                    construction_year INTEGER,
                    x_coordinate NUMERIC(10,3),
                    y_coordinate NUMERIC(10,3),
                    latitude NUMERIC(10,8),
                    longitude NUMERIC(11,8),
                    geom GEOMETRY(POINT, 27700),
                    lad_code VARCHAR(10),
                    lad_name TEXT,
                    ward_code VARCHAR(10),
                    ward_name TEXT,
                    business_activity_indicator BOOLEAN,
                    business_name TEXT,
                    business_type VARCHAR(64),
                    business_sector VARCHAR(64),
                    estimated_rateable_value NUMERIC(15,2),
                    estimated_annual_charge NUMERIC(15,2),
                    rating_potential_score NUMERIC(3,2),
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
        }
    
    def _get_indexes_sql(self) -> Dict[str, str]:
        """Get SQL for performance indexes"""
        return {
            'properties_ba_reference': "CREATE INDEX IF NOT EXISTS idx_properties_ba_reference ON properties(ba_reference);",
            'properties_postcode': "CREATE INDEX IF NOT EXISTS idx_properties_postcode ON properties(postcode);",
            'properties_location': "CREATE INDEX IF NOT EXISTS idx_properties_location ON properties USING GIST(location);",
            'properties_rateable_value': "CREATE INDEX IF NOT EXISTS idx_properties_rateable_value ON properties(rateable_value);",
            'ratepayers_property_id': "CREATE INDEX IF NOT EXISTS idx_ratepayers_property_id ON ratepayers(property_id);",
            'valuations_property_id': "CREATE INDEX IF NOT EXISTS idx_valuations_property_id ON valuations(property_id);",
            'valuations_ba_reference': "CREATE INDEX IF NOT EXISTS idx_valuations_ba_reference ON valuations(ba_reference);",
            'os_open_uprn_uprn': "CREATE INDEX IF NOT EXISTS idx_os_open_uprn_uprn ON os_open_uprn(uprn);",
            'os_open_uprn_postcode': "CREATE INDEX IF NOT EXISTS idx_os_open_uprn_postcode ON os_open_uprn(postcode);",
            'os_open_uprn_location': "CREATE INDEX IF NOT EXISTS idx_os_open_uprn_location ON os_open_uprn USING GIST(location);",
            'code_point_open_postcode': "CREATE INDEX IF NOT EXISTS idx_code_point_open_postcode ON code_point_open(postcode);",
            'code_point_open_location': "CREATE INDEX IF NOT EXISTS idx_code_point_open_location ON code_point_open USING GIST(location);",
            'lad_geometry': "CREATE INDEX IF NOT EXISTS idx_lad_geometry ON local_authority_districts USING GIST(geometry);",
            'master_gazetteer_uprn': "CREATE INDEX IF NOT EXISTS idx_master_gazetteer_uprn ON master_gazetteer(uprn);",
            'master_gazetteer_ba_reference': "CREATE INDEX IF NOT EXISTS idx_master_gazetteer_ba_reference ON master_gazetteer(ba_reference);",
            'master_gazetteer_postcode': "CREATE INDEX IF NOT EXISTS idx_master_gazetteer_postcode ON master_gazetteer(postcode);",
            'master_gazetteer_geom': "CREATE INDEX IF NOT EXISTS idx_master_gazetteer_geom ON master_gazetteer USING GIST(geom);",
            'forecasts_property_id': "CREATE INDEX IF NOT EXISTS idx_forecasts_property_id ON forecasts(property_id);",
            'forecasts_period': "CREATE INDEX IF NOT EXISTS idx_forecasts_period ON forecasts(forecast_period_start, forecast_period_end);",
            'non_rated_properties_uprn': "CREATE INDEX IF NOT EXISTS idx_non_rated_properties_uprn ON non_rated_properties(uprn);",
            'non_rated_properties_geom': "CREATE INDEX IF NOT EXISTS idx_non_rated_properties_geom ON non_rated_properties USING GIST(geom);"
        }
    
    def analyze_data_availability(self) -> Dict[str, Dict]:
        """Analyze what data is available and its structure"""
        logger.info("🔍 Analyzing data availability...")
        
        data_analysis = {
            'nndr_data': {},
            'geospatial_data': {},
            'summary': {}
        }
        
        # Check NNDR data
        nndr_files = {
            'rating_list_2015': self.data_root / 'NNDR Rating List  March 2015_0.csv',
            'ratepayers_2015': self.data_root / 'nndr-ratepayers March 2015_0.csv',
            'list_entries_2010': self.data_root / 'uk-englandwales-ndr-2010-listentries-compiled-epoch-0052-baseline-csv',
            'list_entries_2017': self.data_root / 'uk-englandwales-ndr-2017-listentries-compiled-epoch-0051-baseline-csv',
            'list_entries_2023': self.data_root / 'uk-englandwales-ndr-2023-listentries-compiled-epoch-0015-baseline-csv',
            'summary_valuations_2010': self.data_root / 'uk-englandwales-ndr-2010-summaryvaluations-compiled-epoch-0052-baseline-csv',
            'summary_valuations_2017': self.data_root / 'uk-englandwales-ndr-2017-summaryvaluations-compiled-epoch-0051-baseline-csv',
            'summary_valuations_2023': self.data_root / 'uk-englandwales-ndr-2023-summaryvaluations-compiled-epoch-0015-baseline-csv'
        }
        
        for name, path in nndr_files.items():
            if path.exists():
                if path.is_file():
                    size = path.stat().st_size
                    data_analysis['nndr_data'][name] = {
                        'path': str(path),
                        'type': 'file',
                        'size_mb': round(size / (1024 * 1024), 2),
                        'available': True
                    }
                elif path.is_dir():
                    csv_files = list(path.glob('*.csv'))
                    total_size = sum(f.stat().st_size for f in csv_files)
                    data_analysis['nndr_data'][name] = {
                        'path': str(path),
                        'type': 'directory',
                        'file_count': len(csv_files),
                        'size_mb': round(total_size / (1024 * 1024), 2),
                        'available': True
                    }
            else:
                data_analysis['nndr_data'][name] = {'available': False}
        
        # Check geospatial data
        geospatial_files = {
            'os_open_uprn': self.data_root / 'osopenuprn_202506_csv' / 'osopenuprn_202506.csv',
            'code_point_open': self.data_root / 'codepo_gb' / 'Data' / 'CSV',
            'local_authority_districts': self.data_root / 'LAD_MAY_2025_UK_BFC.shp',
            'os_open_names': self.data_root / 'opname_csv_gb' / 'Data',
            'os_open_map_local': self.data_root / 'opmplc_gml3_gb',
            'onspd': self.data_root / 'ONSPD_Online_Latest_Centroids.csv'
        }
        
        for name, path in geospatial_files.items():
            if path.exists():
                if path.is_file():
                    size = path.stat().st_size
                    data_analysis['geospatial_data'][name] = {
                        'path': str(path),
                        'type': 'file',
                        'size_mb': round(size / (1024 * 1024), 2),
                        'available': True
                    }
                elif path.is_dir():
                    files = list(path.rglob('*'))
                    total_size = sum(f.stat().st_size for f in files if f.is_file())
                    data_analysis['geospatial_data'][name] = {
                        'path': str(path),
                        'type': 'directory',
                        'file_count': len(files),
                        'size_mb': round(total_size / (1024 * 1024), 2),
                        'available': True
                    }
            else:
                data_analysis['geospatial_data'][name] = {'available': False}
        
        # Summary
        nndr_available = sum(1 for data in data_analysis['nndr_data'].values() if data.get('available', False))
        geospatial_available = sum(1 for data in data_analysis['geospatial_data'].values() if data.get('available', False))
        
        data_analysis['summary'] = {
            'total_nndr_datasets': len(data_analysis['nndr_data']),
            'available_nndr_datasets': nndr_available,
            'total_geospatial_datasets': len(data_analysis['geospatial_data']),
            'available_geospatial_datasets': geospatial_available,
            'total_datasets': len(data_analysis['nndr_data']) + len(data_analysis['geospatial_data']),
            'total_available': nndr_available + geospatial_available
        }
        
        logger.info(f"📊 Data Analysis Complete:")
        logger.info(f"   NNDR datasets: {nndr_available}/{len(data_analysis['nndr_data'])} available")
        logger.info(f"   Geospatial datasets: {geospatial_available}/{len(data_analysis['geospatial_data'])} available")
        
        return data_analysis
    
    def run_complete_setup(self) -> bool:
        """Run the complete database setup process"""
        self.stats['start_time'] = datetime.now()
        logger.info("🚀 Starting Comprehensive Database Setup")
        logger.info(f"📅 Started at: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Step 1: Connect to database
            if not self.connect():
                return False
            
            # Step 2: Analyze data availability
            data_analysis = self.analyze_data_availability()
            
            # Step 3: Set up database schema
            if not self.setup_database_schema():
                logger.error("❌ Database schema setup failed")
                return False
            
            # Step 4: Ingest data (optional - can be run separately)
            logger.info("📋 Database setup completed successfully!")
            logger.info("💡 To ingest data, run: ingest_data() method")
            
            self.stats['end_time'] = datetime.now()
            self._print_summary(data_analysis)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False
        finally:
            self.disconnect()
    
    def _print_summary(self, data_analysis: Dict):
        """Print setup summary"""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        print("\n" + "="*80)
        print("🎉 COMPREHENSIVE DATABASE SETUP COMPLETE!")
        print("="*80)
        print(f"📅 Duration: {duration}")
        print(f"🏗️ Tables Created: {self.stats['tables_created']}")
        print(f"❌ Errors: {self.stats['errors']}")
        
        print(f"\n📊 Data Availability Summary:")
        print(f"   NNDR Datasets: {data_analysis['summary']['available_nndr_datasets']}/{data_analysis['summary']['total_nndr_datasets']}")
        print(f"   Geospatial Datasets: {data_analysis['summary']['available_geospatial_datasets']}/{data_analysis['summary']['total_geospatial_datasets']}")
        
        print(f"\n🗄️ Database Details:")
        print(f"   Host: {self.db_config['host']}:{self.db_config['port']}")
        print(f"   Database: {self.db_config['database']}")
        print(f"   User: {self.db_config['user']}")
        
        print(f"\n🔧 Next Steps:")
        print(f"   1. Run data ingestion: setup.ingest_data()")
        print(f"   2. Apply performance tuning: setup/database/tuning/apply_tuning.sh")
        print(f"   3. Start analysis and forecasting")
        
        print(f"\n✅ Setup completed successfully!")

def main():
    """Main function"""
    print("🚀 Comprehensive NNDR Database Setup")
    print("This script sets up the complete database schema for the NNDR Insight project.")
    print("It's designed for performance, scalability, and future growth.\n")
    
    try:
        setup = ComprehensiveDatabaseSetup()
        success = setup.run_complete_setup()
        
        if success:
            print("\n🎯 Setup completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Setup failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 