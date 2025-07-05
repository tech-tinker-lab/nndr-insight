#!/usr/bin/env python3
"""
Enhanced Database Schema Setup Script
Comprehensive script to set up the complete enhanced NNDR database schema
"""

import os
import sys
import sqlalchemy
from sqlalchemy import text, create_engine
import logging
from pathlib import Path
import time
from datetime import datetime
import json
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_schema_setup.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedSchemaSetup:
    """
    Enhanced database schema setup for NNDR Insight project
    """
    
    def __init__(self, db_config: Optional[Dict] = None):
        """Initialize the enhanced schema setup"""
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
        
        # Statistics tracking
        self.stats = {
            'schemas_created': 0,
            'tables_created': 0,
            'indexes_created': 0,
            'extensions_enabled': 0,
            'start_time': None,
            'end_time': None
        }
        
        logger.info("Enhanced Schema Setup Initialized")
        logger.info(f"Target Database: {self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}")
    
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
                # Test connection
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.info("Database connection established")
                return True
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    logger.error(f"Failed to connect after {max_retries} attempts")
                    return False
        return False
    
    def disconnect(self) -> None:
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
        logger.info("Database connection closed")
    
    def execute_sql(self, sql: str, params: Optional[Dict] = None, description: str = "") -> bool:
        """Execute SQL with error handling and logging"""
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
            return False
    
    def enable_extensions(self) -> bool:
        """Enable required PostgreSQL extensions"""
        logger.info("Enabling PostgreSQL extensions...")
        
        extensions = [
            ("CREATE EXTENSION IF NOT EXISTS postgis;", "PostGIS"),
            ("CREATE EXTENSION IF NOT EXISTS postgis_topology;", "PostGIS Topology"),
            ("CREATE EXTENSION IF NOT EXISTS postgis_raster;", "PostGIS Raster"),
            ("CREATE EXTENSION IF NOT EXISTS pg_stat_statements;", "pg_stat_statements"),
            ('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";', "UUID"),
            ("CREATE EXTENSION IF NOT EXISTS pg_trgm;", "Trigram"),
            ("CREATE EXTENSION IF NOT EXISTS btree_gin;", "B-tree GIN"),
            ("CREATE EXTENSION IF NOT EXISTS btree_gist;", "B-tree GIST"),
            ("CREATE EXTENSION IF NOT EXISTS hstore;", "HStore"),
            ("CREATE EXTENSION IF NOT EXISTS tablefunc;", "Table Functions")
        ]
        
        for sql, name in extensions:
            if self.execute_sql(sql, description=f"Enabling {name} extension"):
                self.stats['extensions_enabled'] += 1
            else:
                logger.error(f"Failed to enable {name} extension")
                return False
        
        logger.info(f"Enabled {self.stats['extensions_enabled']} extensions")
        return True
    
    def create_schemas(self) -> bool:
        """Create all required schemas"""
        logger.info("Creating database schemas...")
        
        schemas = [
            "staging",
            "geography", 
            "economic",
            "forecasting",
            "mapping",
            "business_intelligence",
            "data_quality"
        ]
        
        for schema in schemas:
            sql = f"CREATE SCHEMA IF NOT EXISTS {schema};"
            if self.execute_sql(sql, description=f"Creating {schema} schema"):
                self.stats['schemas_created'] += 1
            else:
                logger.error(f"Failed to create {schema} schema")
                return False
        
        logger.info(f"Created {self.stats['schemas_created']} schemas")
        return True
    
    def create_staging_tables(self) -> bool:
        """Create staging tables"""
        logger.info("Creating staging tables...")
        
        staging_tables = {
            'raw_nndr_list_entries': """
                CREATE TABLE IF NOT EXISTS staging.raw_nndr_list_entries (
                    id SERIAL PRIMARY KEY,
                    raw_data TEXT,
                    file_source VARCHAR(255),
                    ingestion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE,
                    error_message TEXT,
                    data_hash VARCHAR(64)
                );
            """,
            
            'raw_geospatial_data': """
                CREATE TABLE IF NOT EXISTS staging.raw_geospatial_data (
                    id SERIAL PRIMARY KEY,
                    data_type VARCHAR(50),
                    raw_data JSONB,
                    file_source VARCHAR(255),
                    ingestion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE,
                    error_message TEXT,
                    data_hash VARCHAR(64)
                );
            """,
            
            'raw_economic_data': """
                CREATE TABLE IF NOT EXISTS staging.raw_economic_data (
                    id SERIAL PRIMARY KEY,
                    data_type VARCHAR(50),
                    raw_data JSONB,
                    file_source VARCHAR(255),
                    ingestion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE,
                    error_message TEXT,
                    data_hash VARCHAR(64)
                );
            """,
            
            'data_quality_checks': """
                CREATE TABLE IF NOT EXISTS staging.data_quality_checks (
                    id SERIAL PRIMARY KEY,
                    table_name VARCHAR(100),
                    column_name VARCHAR(100),
                    check_type VARCHAR(50),
                    check_result JSONB,
                    check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    severity VARCHAR(20)
                );
            """
        }
        
        for table_name, sql in staging_tables.items():
            if self.execute_sql(sql, description=f"Creating staging table: {table_name}"):
                self.stats['tables_created'] += 1
            else:
                logger.error(f"Failed to create staging table: {table_name}")
                return False
        
        return True
    
    def create_geography_tables(self) -> bool:
        """Create hierarchical geography tables"""
        logger.info("Creating geography tables...")
        
        geography_tables = {
            'countries': """
                CREATE TABLE IF NOT EXISTS geography.countries (
                    id SERIAL PRIMARY KEY,
                    country_code VARCHAR(3) UNIQUE NOT NULL,
                    country_name VARCHAR(100) NOT NULL,
                    geometry GEOMETRY(MULTIPOLYGON, 27700),
                    population_estimate BIGINT,
                    gdp_estimate NUMERIC(20,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            'regions': """
                CREATE TABLE IF NOT EXISTS geography.regions (
                    id SERIAL PRIMARY KEY,
                    region_code VARCHAR(10) UNIQUE NOT NULL,
                    region_name VARCHAR(100) NOT NULL,
                    country_code VARCHAR(3) REFERENCES geography.countries(country_code),
                    geometry GEOMETRY(MULTIPOLYGON, 27700),
                    population_estimate BIGINT,
                    economic_growth_rate NUMERIC(5,4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            'counties': """
                CREATE TABLE IF NOT EXISTS geography.counties (
                    id SERIAL PRIMARY KEY,
                    county_code VARCHAR(10) UNIQUE NOT NULL,
                    county_name VARCHAR(100) NOT NULL,
                    region_code VARCHAR(10) REFERENCES geography.regions(region_code),
                    geometry GEOMETRY(MULTIPOLYGON, 27700),
                    population_estimate BIGINT,
                    business_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            'local_authority_districts': """
                CREATE TABLE IF NOT EXISTS geography.local_authority_districts (
                    id SERIAL PRIMARY KEY,
                    lad_code VARCHAR(10) UNIQUE NOT NULL,
                    lad_name VARCHAR(100) NOT NULL,
                    county_code VARCHAR(10) REFERENCES geography.counties(county_code),
                    region_code VARCHAR(10) REFERENCES geography.regions(region_code),
                    geometry GEOMETRY(MULTIPOLYGON, 27700),
                    population_estimate BIGINT,
                    area_hectares NUMERIC(12,2),
                    business_density NUMERIC(10,2),
                    economic_activity_score NUMERIC(5,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            'electoral_wards': """
                CREATE TABLE IF NOT EXISTS geography.electoral_wards (
                    id SERIAL PRIMARY KEY,
                    ward_code VARCHAR(10) UNIQUE NOT NULL,
                    ward_name VARCHAR(100) NOT NULL,
                    lad_code VARCHAR(10) REFERENCES geography.local_authority_districts(lad_code),
                    geometry GEOMETRY(MULTIPOLYGON, 27700),
                    population_estimate BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            'parishes': """
                CREATE TABLE IF NOT EXISTS geography.parishes (
                    id SERIAL PRIMARY KEY,
                    parish_code VARCHAR(10) UNIQUE NOT NULL,
                    parish_name VARCHAR(100) NOT NULL,
                    lad_code VARCHAR(10) REFERENCES geography.local_authority_districts(lad_code),
                    geometry GEOMETRY(MULTIPOLYGON, 27700),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
        }
        
        for table_name, sql in geography_tables.items():
            if self.execute_sql(sql, description=f"Creating geography table: {table_name}"):
                self.stats['tables_created'] += 1
            else:
                logger.error(f"Failed to create geography table: {table_name}")
                return False
        
        return True
    
    def create_economic_tables(self) -> bool:
        """Create economic data tables"""
        logger.info("Creating economic tables...")
        
        economic_tables = {
            'economic_indicators': """
                CREATE TABLE IF NOT EXISTS economic.economic_indicators (
                    id SERIAL PRIMARY KEY,
                    geography_type VARCHAR(20),
                    geography_code VARCHAR(10),
                    indicator_date DATE NOT NULL,
                    gdp_growth_rate NUMERIC(5,4),
                    inflation_rate NUMERIC(5,4),
                    unemployment_rate NUMERIC(5,4),
                    interest_rate NUMERIC(5,4),
                    exchange_rate_gbp_usd NUMERIC(8,4),
                    exchange_rate_gbp_eur NUMERIC(8,4),
                    commercial_property_growth_rate NUMERIC(5,4),
                    industrial_property_growth_rate NUMERIC(5,4),
                    retail_property_growth_rate NUMERIC(5,4),
                    office_property_growth_rate NUMERIC(5,4),
                    business_formation_rate NUMERIC(5,4),
                    business_closure_rate NUMERIC(5,4),
                    employment_growth_rate NUMERIC(5,4),
                    wage_growth_rate NUMERIC(5,4),
                    consumer_confidence_index NUMERIC(5,2),
                    retail_sales_growth NUMERIC(5,4),
                    housing_market_index NUMERIC(5,2),
                    data_source VARCHAR(100),
                    confidence_level NUMERIC(3,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(geography_type, geography_code, indicator_date)
                );
            """,
            
            'sector_economic_data': """
                CREATE TABLE IF NOT EXISTS economic.sector_economic_data (
                    id SERIAL PRIMARY KEY,
                    sector_code VARCHAR(10),
                    sector_name VARCHAR(100),
                    geography_type VARCHAR(20),
                    geography_code VARCHAR(10),
                    data_date DATE NOT NULL,
                    sector_growth_rate NUMERIC(5,4),
                    sector_employment_count INTEGER,
                    sector_wage_average NUMERIC(10,2),
                    sector_productivity NUMERIC(10,2),
                    sector_property_demand_score NUMERIC(5,2),
                    sector_rental_growth_rate NUMERIC(5,4),
                    sector_yield_rate NUMERIC(5,4),
                    data_source VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
        }
        
        for table_name, sql in economic_tables.items():
            if self.execute_sql(sql, description=f"Creating economic table: {table_name}"):
                self.stats['tables_created'] += 1
            else:
                logger.error(f"Failed to create economic table: {table_name}")
                return False
        
        return True
    
    def create_forecasting_tables(self) -> bool:
        """Create enhanced forecasting tables"""
        logger.info("Creating forecasting tables...")
        
        forecasting_tables = {
            'forecasting_models': """
                CREATE TABLE IF NOT EXISTS forecasting.forecasting_models (
                    id SERIAL PRIMARY KEY,
                    model_name VARCHAR(100) NOT NULL,
                    model_version VARCHAR(20) NOT NULL,
                    model_type VARCHAR(50) NOT NULL,
                    forecast_category VARCHAR(50) NOT NULL,
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
                CREATE TABLE IF NOT EXISTS forecasting.forecasts (
                    id SERIAL PRIMARY KEY,
                    model_id INTEGER REFERENCES forecasting.forecasting_models(id),
                    property_id INTEGER REFERENCES master_gazetteer(id),
                    forecast_period_start DATE NOT NULL,
                    forecast_period_end DATE NOT NULL,
                    forecast_date DATE NOT NULL,
                    forecast_scenario VARCHAR(50),
                    forecasted_rateable_value NUMERIC(15,2),
                    forecasted_annual_charge NUMERIC(15,2),
                    forecasted_net_charge NUMERIC(15,2),
                    forecasted_inflation_impact NUMERIC(5,4),
                    forecasted_economic_growth_impact NUMERIC(5,4),
                    forecasted_market_conditions_score NUMERIC(5,2),
                    confidence_interval_lower NUMERIC(15,2),
                    confidence_interval_upper NUMERIC(15,2),
                    confidence_score NUMERIC(3,2),
                    forecast_factors JSONB,
                    forecast_assumptions JSONB,
                    economic_factors_considered JSONB,
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
            
            'economic_scenario_forecasts': """
                CREATE TABLE IF NOT EXISTS forecasting.economic_scenario_forecasts (
                    id SERIAL PRIMARY KEY,
                    scenario_name VARCHAR(100) NOT NULL,
                    scenario_description TEXT,
                    geography_type VARCHAR(20),
                    geography_code VARCHAR(10),
                    forecast_period_start DATE,
                    forecast_period_end DATE,
                    gdp_growth_scenario NUMERIC(5,4),
                    inflation_scenario NUMERIC(5,4),
                    interest_rate_scenario NUMERIC(5,4),
                    employment_growth_scenario NUMERIC(5,4),
                    expected_nndr_growth_rate NUMERIC(5,4),
                    expected_property_value_change NUMERIC(5,4),
                    expected_business_formation_impact NUMERIC(5,4),
                    confidence_level NUMERIC(3,2),
                    scenario_probability NUMERIC(3,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            'non_rated_properties': """
                CREATE TABLE IF NOT EXISTS forecasting.non_rated_properties (
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
        
        for table_name, sql in forecasting_tables.items():
            if self.execute_sql(sql, description=f"Creating forecasting table: {table_name}"):
                self.stats['tables_created'] += 1
            else:
                logger.error(f"Failed to create forecasting table: {table_name}")
                return False
        
        return True
    
    def create_mapping_tables(self) -> bool:
        """Create custom map layer tables"""
        logger.info("Creating mapping tables...")
        
        mapping_tables = {
            'map_layers': """
                CREATE TABLE IF NOT EXISTS mapping.map_layers (
                    id SERIAL PRIMARY KEY,
                    layer_name VARCHAR(100) UNIQUE NOT NULL,
                    layer_description TEXT,
                    layer_type VARCHAR(50),
                    data_source_table VARCHAR(100),
                    data_source_column VARCHAR(100),
                    geometry_column VARCHAR(100),
                    style_config JSONB,
                    legend_config JSONB,
                    popup_config JSONB,
                    min_zoom INTEGER DEFAULT 0,
                    max_zoom INTEGER DEFAULT 18,
                    default_visible BOOLEAN DEFAULT TRUE,
                    layer_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100)
                );
            """,
            
            'custom_icons': """
                CREATE TABLE IF NOT EXISTS mapping.custom_icons (
                    id SERIAL PRIMARY KEY,
                    icon_name VARCHAR(100) UNIQUE NOT NULL,
                    icon_description TEXT,
                    icon_type VARCHAR(50),
                    icon_url VARCHAR(500),
                    icon_data TEXT,
                    icon_size JSONB,
                    icon_colors JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100)
                );
            """,
            
            'layer_icon_assignments': """
                CREATE TABLE IF NOT EXISTS mapping.layer_icon_assignments (
                    id SERIAL PRIMARY KEY,
                    layer_id INTEGER REFERENCES mapping.map_layers(id),
                    icon_id INTEGER REFERENCES mapping.custom_icons(id),
                    condition_column VARCHAR(100),
                    condition_value VARCHAR(100),
                    priority INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
        }
        
        for table_name, sql in mapping_tables.items():
            if self.execute_sql(sql, description=f"Creating mapping table: {table_name}"):
                self.stats['tables_created'] += 1
            else:
                logger.error(f"Failed to create mapping table: {table_name}")
                return False
        
        return True
    
    def create_business_intelligence_tables(self) -> bool:
        """Create business intelligence tables"""
        logger.info("Creating business intelligence tables...")
        
        bi_tables = {
            'kpis': """
                CREATE TABLE IF NOT EXISTS business_intelligence.kpis (
                    id SERIAL PRIMARY KEY,
                    kpi_name VARCHAR(100) UNIQUE NOT NULL,
                    kpi_description TEXT,
                    kpi_category VARCHAR(50),
                    calculation_method TEXT,
                    target_value NUMERIC(15,2),
                    target_date DATE,
                    unit_of_measure VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            'kpi_measurements': """
                CREATE TABLE IF NOT EXISTS business_intelligence.kpi_measurements (
                    id SERIAL PRIMARY KEY,
                    kpi_id INTEGER REFERENCES business_intelligence.kpis(id),
                    measurement_date DATE NOT NULL,
                    geography_type VARCHAR(20),
                    geography_code VARCHAR(10),
                    actual_value NUMERIC(15,2),
                    target_value NUMERIC(15,2),
                    variance NUMERIC(15,2),
                    variance_percentage NUMERIC(5,2),
                    status VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            'dashboards': """
                CREATE TABLE IF NOT EXISTS business_intelligence.dashboards (
                    id SERIAL PRIMARY KEY,
                    dashboard_name VARCHAR(100) UNIQUE NOT NULL,
                    dashboard_description TEXT,
                    dashboard_type VARCHAR(50),
                    layout_config JSONB,
                    refresh_interval INTEGER,
                    is_public BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100)
                );
            """,
            
            'dashboard_widgets': """
                CREATE TABLE IF NOT EXISTS business_intelligence.dashboard_widgets (
                    id SERIAL PRIMARY KEY,
                    dashboard_id INTEGER REFERENCES business_intelligence.dashboards(id),
                    widget_name VARCHAR(100),
                    widget_type VARCHAR(50),
                    widget_config JSONB,
                    position_x INTEGER,
                    position_y INTEGER,
                    width INTEGER,
                    height INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
        }
        
        for table_name, sql in bi_tables.items():
            if self.execute_sql(sql, description=f"Creating BI table: {table_name}"):
                self.stats['tables_created'] += 1
            else:
                logger.error(f"Failed to create BI table: {table_name}")
                return False
        
        return True
    
    def create_data_quality_tables(self) -> bool:
        """Create data quality tables"""
        logger.info("Creating data quality tables...")
        
        quality_tables = {
            'quality_rules': """
                CREATE TABLE IF NOT EXISTS data_quality.quality_rules (
                    id SERIAL PRIMARY KEY,
                    rule_name VARCHAR(100) UNIQUE NOT NULL,
                    rule_description TEXT,
                    table_name VARCHAR(100),
                    column_name VARCHAR(100),
                    rule_type VARCHAR(50),
                    rule_definition TEXT,
                    severity VARCHAR(20),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100)
                );
            """,
            
            'quality_check_results': """
                CREATE TABLE IF NOT EXISTS data_quality.quality_check_results (
                    id SERIAL PRIMARY KEY,
                    rule_id INTEGER REFERENCES data_quality.quality_rules(id),
                    check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    table_name VARCHAR(100),
                    column_name VARCHAR(100),
                    records_checked BIGINT,
                    records_failed BIGINT,
                    failure_rate NUMERIC(5,4),
                    failed_values JSONB,
                    check_duration_seconds NUMERIC(10,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            'data_lineage': """
                CREATE TABLE IF NOT EXISTS data_quality.data_lineage (
                    id SERIAL PRIMARY KEY,
                    table_name VARCHAR(100),
                    column_name VARCHAR(100),
                    source_table VARCHAR(100),
                    source_column VARCHAR(100),
                    transformation_type VARCHAR(50),
                    transformation_rule TEXT,
                    data_flow_step INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
        }
        
        for table_name, sql in quality_tables.items():
            if self.execute_sql(sql, description=f"Creating quality table: {table_name}"):
                self.stats['tables_created'] += 1
            else:
                logger.error(f"Failed to create quality table: {table_name}")
                return False
        
        return True
    
    def create_enhanced_master_gazetteer(self) -> bool:
        """Create enhanced master gazetteer table"""
        logger.info("Creating enhanced master gazetteer table...")
        
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
        
        if self.execute_sql(master_gazetteer_sql, description="Creating enhanced master gazetteer table"):
            self.stats['tables_created'] += 1
            return True
        else:
            logger.error("Failed to create enhanced master gazetteer table")
            return False
    
    def create_performance_indexes(self) -> bool:
        """Create comprehensive performance indexes"""
        logger.info("Creating performance indexes...")
        
        indexes = [
            # Geography indexes
            ("CREATE INDEX IF NOT EXISTS idx_countries_geometry ON geography.countries USING GIST(geometry);", "Countries geometry"),
            ("CREATE INDEX IF NOT EXISTS idx_regions_geometry ON geography.regions USING GIST(geometry);", "Regions geometry"),
            ("CREATE INDEX IF NOT EXISTS idx_counties_geometry ON geography.counties USING GIST(geometry);", "Counties geometry"),
            ("CREATE INDEX IF NOT EXISTS idx_lad_geometry ON geography.local_authority_districts USING GIST(geometry);", "LAD geometry"),
            ("CREATE INDEX IF NOT EXISTS idx_wards_geometry ON geography.electoral_wards USING GIST(geometry);", "Wards geometry"),
            ("CREATE INDEX IF NOT EXISTS idx_parishes_geometry ON geography.parishes USING GIST(geometry);", "Parishes geometry"),
            
            # Economic indexes
            ("CREATE INDEX IF NOT EXISTS idx_economic_indicators_geo_date ON economic.economic_indicators(geography_type, geography_code, indicator_date);", "Economic indicators geo-date"),
            ("CREATE INDEX IF NOT EXISTS idx_sector_economic_geo_date ON economic.sector_economic_data(geography_type, geography_code, data_date);", "Sector economic geo-date"),
            
            # Forecasting indexes
            ("CREATE INDEX IF NOT EXISTS idx_forecasts_property_period ON forecasting.forecasts(property_id, forecast_period_start, forecast_period_end);", "Forecasts property-period"),
            ("CREATE INDEX IF NOT EXISTS idx_forecasts_scenario ON forecasting.forecasts(forecast_scenario, forecast_date);", "Forecasts scenario"),
            ("CREATE INDEX IF NOT EXISTS idx_economic_scenarios_geo_period ON forecasting.economic_scenario_forecasts(geography_type, geography_code, forecast_period_start);", "Economic scenarios geo-period"),
            
            # Business Intelligence indexes
            ("CREATE INDEX IF NOT EXISTS idx_kpi_measurements_date_geo ON business_intelligence.kpi_measurements(measurement_date, geography_type, geography_code);", "KPI measurements date-geo"),
            
            # Quality indexes
            ("CREATE INDEX IF NOT EXISTS idx_quality_check_results_date ON data_quality.quality_check_results(check_date);", "Quality check results date"),
            
            # Master gazetteer indexes
            ("CREATE INDEX IF NOT EXISTS idx_master_gazetteer_uprn ON master_gazetteer(uprn);", "Master gazetteer UPRN"),
            ("CREATE INDEX IF NOT EXISTS idx_master_gazetteer_ba_reference ON master_gazetteer(ba_reference);", "Master gazetteer BA reference"),
            ("CREATE INDEX IF NOT EXISTS idx_master_gazetteer_postcode ON master_gazetteer(postcode);", "Master gazetteer postcode"),
            ("CREATE INDEX IF NOT EXISTS idx_master_gazetteer_geom ON master_gazetteer USING GIST(geom);", "Master gazetteer geometry"),
            ("CREATE INDEX IF NOT EXISTS idx_master_gazetteer_lad_code ON master_gazetteer(lad_code);", "Master gazetteer LAD code"),
            ("CREATE INDEX IF NOT EXISTS idx_master_gazetteer_category ON master_gazetteer(property_category_code);", "Master gazetteer category"),
            ("CREATE INDEX IF NOT EXISTS idx_master_gazetteer_rateable_value ON master_gazetteer(current_rateable_value);", "Master gazetteer rateable value"),
            
            # Composite indexes
            ("CREATE INDEX IF NOT EXISTS idx_master_gazetteer_postcode_category ON master_gazetteer(postcode, property_category_code);", "Master gazetteer postcode-category"),
            ("CREATE INDEX IF NOT EXISTS idx_master_gazetteer_lad_category ON master_gazetteer(lad_code, property_category_code);", "Master gazetteer LAD-category"),
            ("CREATE INDEX IF NOT EXISTS idx_master_gazetteer_value_range ON master_gazetteer(current_rateable_value) WHERE current_rateable_value > 0;", "Master gazetteer value range")
        ]
        
        for sql, description in indexes:
            if self.execute_sql(sql, description=f"Creating index: {description}"):
                self.stats['indexes_created'] += 1
            else:
                logger.warning(f"Failed to create index: {description}")
        
        logger.info(f"Created {self.stats['indexes_created']} indexes")
        return True
    
    def add_comments_and_documentation(self) -> bool:
        """Add comments and documentation to tables"""
        logger.info("Adding table comments and documentation...")
        
        comments = [
            ("COMMENT ON SCHEMA staging IS 'Staging area for data ingestion and processing';", "Staging schema"),
            ("COMMENT ON SCHEMA geography IS 'Hierarchical geographic data from country to parish level';", "Geography schema"),
            ("COMMENT ON SCHEMA economic IS 'Economic indicators and sector-specific data';", "Economic schema"),
            ("COMMENT ON SCHEMA forecasting IS 'Enhanced forecasting system with multiple scenarios';", "Forecasting schema"),
            ("COMMENT ON SCHEMA mapping IS 'Custom map layers and icon management';", "Mapping schema"),
            ("COMMENT ON SCHEMA business_intelligence IS 'KPIs, dashboards, and business metrics';", "BI schema"),
            ("COMMENT ON SCHEMA data_quality IS 'Data quality rules, checks, and lineage tracking';", "Quality schema"),
            
            ("COMMENT ON TABLE staging.raw_nndr_list_entries IS 'Raw NNDR data before processing and validation';", "Raw NNDR entries"),
            ("COMMENT ON TABLE geography.countries IS 'Country-level geographic and economic data';", "Countries"),
            ("COMMENT ON TABLE economic.economic_indicators IS 'Economic indicators by geography and time period';", "Economic indicators"),
            ("COMMENT ON TABLE forecasting.forecasts IS 'Property and economic forecasts with multiple scenarios';", "Forecasts"),
            ("COMMENT ON TABLE mapping.map_layers IS 'Custom map layer definitions and styling';", "Map layers"),
            ("COMMENT ON TABLE business_intelligence.kpis IS 'Key Performance Indicators for business monitoring';", "KPIs"),
            ("COMMENT ON TABLE data_quality.quality_rules IS 'Data quality rules and validation criteria';", "Quality rules"),
            ("COMMENT ON TABLE master_gazetteer IS 'Master gazetteer table consolidating all property and location data for NNDR business rate forecasting';", "Master gazetteer")
        ]
        
        for sql, description in comments:
            if self.execute_sql(sql, description=f"Adding comment: {description}"):
                pass  # Comments don't count as tables
            else:
                logger.warning(f"Failed to add comment: {description}")
        
        return True
    
    def run_complete_setup(self) -> bool:
        """Run the complete enhanced schema setup"""
        self.stats['start_time'] = datetime.now()
        logger.info("Starting enhanced database schema setup...")
        
        try:
            # Step 1: Connect to database
            if not self.connect():
                return False
            
            # Step 2: Enable extensions
            if not self.enable_extensions():
                return False
            
            # Step 3: Create schemas
            if not self.create_schemas():
                return False
            
            # Step 4: Create staging tables
            if not self.create_staging_tables():
                return False
            
            # Step 5: Create geography tables
            if not self.create_geography_tables():
                return False
            
            # Step 6: Create economic tables
            if not self.create_economic_tables():
                return False
            
            # Step 7: Create forecasting tables
            if not self.create_forecasting_tables():
                return False
            
            # Step 8: Create mapping tables
            if not self.create_mapping_tables():
                return False
            
            # Step 9: Create business intelligence tables
            if not self.create_business_intelligence_tables():
                return False
            
            # Step 10: Create data quality tables
            if not self.create_data_quality_tables():
                return False
            
            # Step 11: Create enhanced master gazetteer
            if not self.create_enhanced_master_gazetteer():
                return False
            
            # Step 12: Create performance indexes
            if not self.create_performance_indexes():
                return False
            
            # Step 13: Add comments and documentation
            if not self.add_comments_and_documentation():
                return False
            
            self.stats['end_time'] = datetime.now()
            self._print_final_summary()
            
            return True
            
        except Exception as e:
            logger.error(f"Enhanced schema setup failed: {e}")
            return False
        finally:
            self.disconnect()
    
    def _print_final_summary(self):
        """Print final setup summary"""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        logger.info("=" * 80)
        logger.info("ENHANCED DATABASE SCHEMA SETUP COMPLETED")
        logger.info("=" * 80)
        logger.info(f"Duration: {duration}")
        logger.info(f"Extensions enabled: {self.stats['extensions_enabled']}")
        logger.info(f"Schemas created: {self.stats['schemas_created']}")
        logger.info(f"Tables created: {self.stats['tables_created']}")
        logger.info(f"Indexes created: {self.stats['indexes_created']}")
        logger.info("=" * 80)
        logger.info("SCHEMAS CREATED:")
        logger.info("  - staging (Data staging and processing)")
        logger.info("  - geography (Hierarchical geographic data)")
        logger.info("  - economic (Economic indicators and sector data)")
        logger.info("  - forecasting (Enhanced forecasting system)")
        logger.info("  - mapping (Custom map layers and styling)")
        logger.info("  - business_intelligence (KPIs and dashboards)")
        logger.info("  - data_quality (Quality rules and lineage)")
        logger.info("=" * 80)
        logger.info("KEY TABLES CREATED:")
        logger.info("  - master_gazetteer (Enhanced master property reference)")
        logger.info("  - economic.economic_indicators (Economic data by geography)")
        logger.info("  - forecasting.forecasts (Property and economic forecasts)")
        logger.info("  - mapping.map_layers (Custom map layer definitions)")
        logger.info("  - business_intelligence.kpis (Key Performance Indicators)")
        logger.info("  - data_quality.quality_rules (Data quality framework)")
        logger.info("=" * 80)
        logger.info("NEXT STEPS:")
        logger.info("  1. Review the schema structure")
        logger.info("  2. Test the enhanced data ingestion pipeline")
        logger.info("  3. Begin data loading and validation")
        logger.info("  4. Configure custom map layers and dashboards")
        logger.info("=" * 80)

def main():
    """Main function"""
    # Configuration
    db_config = {
        'host': '192.168.1.79',
        'port': 5432,
        'database': 'nndr_db',
        'user': 'nndr',
        'password': 'nndrpass'
    }
    
    # Run setup
    setup = EnhancedSchemaSetup(db_config)
    
    try:
        success = setup.run_complete_setup()
        if success:
            logger.info("Enhanced database schema setup completed successfully")
            sys.exit(0)
        else:
            logger.error("Enhanced database schema setup failed")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 