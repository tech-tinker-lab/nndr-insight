-- Enhanced NNDR Database Schema
-- Comprehensive schema for business rate forecasting with staging, economic data, and custom map layers
-- Designed for maximum performance and accuracy

-- ============================================================================
-- 1. STAGING SCHEMA - For data ingestion and processing
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS staging;

-- Staging tables for raw data ingestion
CREATE TABLE IF NOT EXISTS staging.raw_nndr_list_entries (
    id SERIAL PRIMARY KEY,
    raw_data TEXT,  -- Raw CSV line for debugging
    file_source VARCHAR(255),
    ingestion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS staging.raw_geospatial_data (
    id SERIAL PRIMARY KEY,
    data_type VARCHAR(50),  -- 'uprn', 'postcode', 'address', 'boundary'
    raw_data JSONB,
    file_source VARCHAR(255),
    ingestion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS staging.data_quality_checks (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    column_name VARCHAR(100),
    check_type VARCHAR(50),  -- 'null_count', 'duplicate_count', 'format_check', 'range_check'
    check_result JSONB,
    check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    severity VARCHAR(20)  -- 'info', 'warning', 'error', 'critical'
);

-- ============================================================================
-- 2. HIERARCHICAL GEOGRAPHY SCHEMA
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS geography;

-- Country level
CREATE TABLE IF NOT EXISTS geography.countries (
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(3) UNIQUE NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    geometry GEOMETRY(MULTIPOLYGON, 27700),
    population_estimate BIGINT,
    gdp_estimate NUMERIC(20,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Region level (England, Scotland, Wales, Northern Ireland)
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

-- County level
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

-- Local Authority District (enhanced)
CREATE TABLE IF NOT EXISTS geography.local_authority_districts (
    id SERIAL PRIMARY KEY,
    lad_code VARCHAR(10) UNIQUE NOT NULL,
    lad_name VARCHAR(100) NOT NULL,
    county_code VARCHAR(10) REFERENCES geography.counties(country_code),
    region_code VARCHAR(10) REFERENCES geography.regions(region_code),
    geometry GEOMETRY(MULTIPOLYGON, 27700),
    population_estimate BIGINT,
    area_hectares NUMERIC(12,2),
    business_density NUMERIC(10,2),  -- Businesses per hectare
    economic_activity_score NUMERIC(5,2),  -- 0-100 score
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Electoral Wards
CREATE TABLE IF NOT EXISTS geography.electoral_wards (
    id SERIAL PRIMARY KEY,
    ward_code VARCHAR(10) UNIQUE NOT NULL,
    ward_name VARCHAR(100) NOT NULL,
    lad_code VARCHAR(10) REFERENCES geography.local_authority_districts(lad_code),
    geometry GEOMETRY(MULTIPOLYGON, 27700),
    population_estimate BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Parishes
CREATE TABLE IF NOT EXISTS geography.parishes (
    id SERIAL PRIMARY KEY,
    parish_code VARCHAR(10) UNIQUE NOT NULL,
    parish_name VARCHAR(100) NOT NULL,
    lad_code VARCHAR(10) REFERENCES geography.local_authority_districts(lad_code),
    geometry GEOMETRY(MULTIPOLYGON, 27700),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 3. ECONOMIC DATA SCHEMA
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS economic;

-- Economic indicators by geography and time
CREATE TABLE IF NOT EXISTS economic.economic_indicators (
    id SERIAL PRIMARY KEY,
    geography_type VARCHAR(20),  -- 'country', 'region', 'county', 'lad', 'ward'
    geography_code VARCHAR(10),
    indicator_date DATE NOT NULL,
    
    -- Economic indicators
    gdp_growth_rate NUMERIC(5,4),
    inflation_rate NUMERIC(5,4),
    unemployment_rate NUMERIC(5,4),
    interest_rate NUMERIC(5,4),
    exchange_rate_gbp_usd NUMERIC(8,4),
    exchange_rate_gbp_eur NUMERIC(8,4),
    
    -- Property market indicators
    commercial_property_growth_rate NUMERIC(5,4),
    industrial_property_growth_rate NUMERIC(5,4),
    retail_property_growth_rate NUMERIC(5,4),
    office_property_growth_rate NUMERIC(5,4),
    
    -- Business indicators
    business_formation_rate NUMERIC(5,4),
    business_closure_rate NUMERIC(5,4),
    employment_growth_rate NUMERIC(5,4),
    wage_growth_rate NUMERIC(5,4),
    
    -- Consumer indicators
    consumer_confidence_index NUMERIC(5,2),
    retail_sales_growth NUMERIC(5,4),
    housing_market_index NUMERIC(5,2),
    
    data_source VARCHAR(100),
    confidence_level NUMERIC(3,2),  -- 0-1 confidence in data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(geography_type, geography_code, indicator_date)
);

-- Sector-specific economic data
CREATE TABLE IF NOT EXISTS economic.sector_economic_data (
    id SERIAL PRIMARY KEY,
    sector_code VARCHAR(10),  -- SIC codes
    sector_name VARCHAR(100),
    geography_type VARCHAR(20),
    geography_code VARCHAR(10),
    data_date DATE NOT NULL,
    
    -- Sector performance
    sector_growth_rate NUMERIC(5,4),
    sector_employment_count INTEGER,
    sector_wage_average NUMERIC(10,2),
    sector_productivity NUMERIC(10,2),
    
    -- Property metrics
    sector_property_demand_score NUMERIC(5,2),  -- 0-100
    sector_rental_growth_rate NUMERIC(5,4),
    sector_yield_rate NUMERIC(5,4),
    
    data_source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 4. ENHANCED FORECASTING SCHEMA
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS forecasting;

-- Enhanced forecasting models with multiple types
CREATE TABLE IF NOT EXISTS forecasting.forecasting_models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    model_type VARCHAR(50) NOT NULL,  -- 'regression', 'time_series', 'ml', 'ensemble', 'prophet'
    forecast_category VARCHAR(50) NOT NULL,  -- 'nndr', 'economic', 'property_market', 'business_growth'
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

-- Enhanced forecasts with multiple scenarios
CREATE TABLE IF NOT EXISTS forecasting.forecasts (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES forecasting.forecasting_models(id),
    property_id INTEGER REFERENCES master_gazetteer(id),
    forecast_period_start DATE NOT NULL,
    forecast_period_end DATE NOT NULL,
    forecast_date DATE NOT NULL,
    forecast_scenario VARCHAR(50),  -- 'baseline', 'optimistic', 'pessimistic', 'stress_test'
    
    -- NNDR specific forecasts
    forecasted_rateable_value NUMERIC(15,2),
    forecasted_annual_charge NUMERIC(15,2),
    forecasted_net_charge NUMERIC(15,2),
    
    -- Economic factor forecasts
    forecasted_inflation_impact NUMERIC(5,4),
    forecasted_economic_growth_impact NUMERIC(5,4),
    forecasted_market_conditions_score NUMERIC(5,2),
    
    -- Confidence and uncertainty
    confidence_interval_lower NUMERIC(15,2),
    confidence_interval_upper NUMERIC(15,2),
    confidence_score NUMERIC(3,2),
    
    -- Forecast factors and reasoning
    forecast_factors JSONB,
    forecast_assumptions JSONB,
    economic_factors_considered JSONB,
    
    -- Validation
    actual_value NUMERIC(15,2),
    forecast_error NUMERIC(15,2),
    is_validated BOOLEAN DEFAULT FALSE,
    validation_date DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    notes TEXT
);

-- Economic scenario forecasts
CREATE TABLE IF NOT EXISTS forecasting.economic_scenario_forecasts (
    id SERIAL PRIMARY KEY,
    scenario_name VARCHAR(100) NOT NULL,
    scenario_description TEXT,
    geography_type VARCHAR(20),
    geography_code VARCHAR(10),
    forecast_period_start DATE,
    forecast_period_end DATE,
    
    -- Economic scenario parameters
    gdp_growth_scenario NUMERIC(5,4),
    inflation_scenario NUMERIC(5,4),
    interest_rate_scenario NUMERIC(5,4),
    employment_growth_scenario NUMERIC(5,4),
    
    -- Impact on NNDR
    expected_nndr_growth_rate NUMERIC(5,4),
    expected_property_value_change NUMERIC(5,4),
    expected_business_formation_impact NUMERIC(5,4),
    
    confidence_level NUMERIC(3,2),
    scenario_probability NUMERIC(3,2),  -- 0-1 probability of scenario
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 5. CUSTOM MAP LAYERS SCHEMA
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS mapping;

-- Map layer definitions
CREATE TABLE IF NOT EXISTS mapping.map_layers (
    id SERIAL PRIMARY KEY,
    layer_name VARCHAR(100) UNIQUE NOT NULL,
    layer_description TEXT,
    layer_type VARCHAR(50),  -- 'choropleth', 'point', 'line', 'heatmap', 'custom'
    data_source_table VARCHAR(100),
    data_source_column VARCHAR(100),
    geometry_column VARCHAR(100),
    
    -- Styling configuration
    style_config JSONB,  -- Colors, opacity, stroke width, etc.
    legend_config JSONB,  -- Legend title, breaks, colors
    popup_config JSONB,   -- Popup fields and formatting
    
    -- Display settings
    min_zoom INTEGER DEFAULT 0,
    max_zoom INTEGER DEFAULT 18,
    default_visible BOOLEAN DEFAULT TRUE,
    layer_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

-- Custom pin icons and symbols
CREATE TABLE IF NOT EXISTS mapping.custom_icons (
    id SERIAL PRIMARY KEY,
    icon_name VARCHAR(100) UNIQUE NOT NULL,
    icon_description TEXT,
    icon_type VARCHAR(50),  -- 'pin', 'symbol', 'marker', 'custom'
    icon_url VARCHAR(500),  -- URL to icon file
    icon_data TEXT,  -- Base64 encoded icon data
    icon_size JSONB,  -- Width, height, anchor point
    icon_colors JSONB,  -- Available color variants
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

-- Map layer assignments
CREATE TABLE IF NOT EXISTS mapping.layer_icon_assignments (
    id SERIAL PRIMARY KEY,
    layer_id INTEGER REFERENCES mapping.map_layers(id),
    icon_id INTEGER REFERENCES mapping.custom_icons(id),
    condition_column VARCHAR(100),  -- Column to base icon selection on
    condition_value VARCHAR(100),   -- Value that triggers this icon
    priority INTEGER DEFAULT 0,     -- Priority for multiple matches
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 6. BUSINESS INTELLIGENCE SCHEMA
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS business_intelligence;

-- Key Performance Indicators
CREATE TABLE IF NOT EXISTS business_intelligence.kpis (
    id SERIAL PRIMARY KEY,
    kpi_name VARCHAR(100) UNIQUE NOT NULL,
    kpi_description TEXT,
    kpi_category VARCHAR(50),  -- 'financial', 'operational', 'compliance', 'forecasting'
    calculation_method TEXT,
    target_value NUMERIC(15,2),
    target_date DATE,
    unit_of_measure VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- KPI measurements over time
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
    status VARCHAR(20),  -- 'on_target', 'below_target', 'above_target', 'critical'
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dashboard configurations
CREATE TABLE IF NOT EXISTS business_intelligence.dashboards (
    id SERIAL PRIMARY KEY,
    dashboard_name VARCHAR(100) UNIQUE NOT NULL,
    dashboard_description TEXT,
    dashboard_type VARCHAR(50),  -- 'executive', 'operational', 'analytical', 'custom'
    layout_config JSONB,  -- Widget positions and sizes
    refresh_interval INTEGER,  -- Seconds
    is_public BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

-- Dashboard widgets
CREATE TABLE IF NOT EXISTS business_intelligence.dashboard_widgets (
    id SERIAL PRIMARY KEY,
    dashboard_id INTEGER REFERENCES business_intelligence.dashboards(id),
    widget_name VARCHAR(100),
    widget_type VARCHAR(50),  -- 'chart', 'table', 'metric', 'map', 'gauge'
    widget_config JSONB,  -- Chart type, data source, styling
    position_x INTEGER,
    position_y INTEGER,
    width INTEGER,
    height INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 7. DATA QUALITY AND AUDIT SCHEMA
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS data_quality;

-- Data quality rules
CREATE TABLE IF NOT EXISTS data_quality.quality_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) UNIQUE NOT NULL,
    rule_description TEXT,
    table_name VARCHAR(100),
    column_name VARCHAR(100),
    rule_type VARCHAR(50),  -- 'not_null', 'unique', 'range', 'format', 'custom'
    rule_definition TEXT,
    severity VARCHAR(20),  -- 'info', 'warning', 'error', 'critical'
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

-- Data quality check results
CREATE TABLE IF NOT EXISTS data_quality.quality_check_results (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES data_quality.quality_rules(id),
    check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    table_name VARCHAR(100),
    column_name VARCHAR(100),
    records_checked BIGINT,
    records_failed BIGINT,
    failure_rate NUMERIC(5,4),
    failed_values JSONB,  -- Sample of failed values
    check_duration_seconds NUMERIC(10,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data lineage tracking
CREATE TABLE IF NOT EXISTS data_quality.data_lineage (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    column_name VARCHAR(100),
    source_table VARCHAR(100),
    source_column VARCHAR(100),
    transformation_type VARCHAR(50),  -- 'direct_copy', 'calculation', 'aggregation', 'join'
    transformation_rule TEXT,
    data_flow_step INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 8. PERFORMANCE INDEXES
-- ============================================================================

-- Geography indexes
CREATE INDEX IF NOT EXISTS idx_countries_geometry ON geography.countries USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_regions_geometry ON geography.regions USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_counties_geometry ON geography.counties USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_lad_geometry ON geography.local_authority_districts USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_wards_geometry ON geography.electoral_wards USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_parishes_geometry ON geography.parishes USING GIST(geometry);

-- Economic indexes
CREATE INDEX IF NOT EXISTS idx_economic_indicators_geo_date ON economic.economic_indicators(geography_type, geography_code, indicator_date);
CREATE INDEX IF NOT EXISTS idx_sector_economic_geo_date ON economic.sector_economic_data(geography_type, geography_code, data_date);

-- Forecasting indexes
CREATE INDEX IF NOT EXISTS idx_forecasts_property_period ON forecasting.forecasts(property_id, forecast_period_start, forecast_period_end);
CREATE INDEX IF NOT EXISTS idx_forecasts_scenario ON forecasting.forecasts(forecast_scenario, forecast_date);
CREATE INDEX IF NOT EXISTS idx_economic_scenarios_geo_period ON forecasting.economic_scenario_forecasts(geography_type, geography_code, forecast_period_start);

-- Business Intelligence indexes
CREATE INDEX IF NOT EXISTS idx_kpi_measurements_date_geo ON business_intelligence.kpi_measurements(measurement_date, geography_type, geography_code);
CREATE INDEX IF NOT EXISTS idx_quality_check_results_date ON data_quality.quality_check_results(check_date);

-- ============================================================================
-- 9. COMMENTS AND DOCUMENTATION
-- ============================================================================

COMMENT ON SCHEMA staging IS 'Staging area for data ingestion and processing';
COMMENT ON SCHEMA geography IS 'Hierarchical geographic data from country to parish level';
COMMENT ON SCHEMA economic IS 'Economic indicators and sector-specific data';
COMMENT ON SCHEMA forecasting IS 'Enhanced forecasting system with multiple scenarios';
COMMENT ON SCHEMA mapping IS 'Custom map layers and icon management';
COMMENT ON SCHEMA business_intelligence IS 'KPIs, dashboards, and business metrics';
COMMENT ON SCHEMA data_quality IS 'Data quality rules, checks, and lineage tracking';

COMMENT ON TABLE staging.raw_nndr_list_entries IS 'Raw NNDR data before processing and validation';
COMMENT ON TABLE geography.countries IS 'Country-level geographic and economic data';
COMMENT ON TABLE economic.economic_indicators IS 'Economic indicators by geography and time period';
COMMENT ON TABLE forecasting.forecasts IS 'Property and economic forecasts with multiple scenarios';
COMMENT ON TABLE mapping.map_layers IS 'Custom map layer definitions and styling';
COMMENT ON TABLE business_intelligence.kpis IS 'Key Performance Indicators for business monitoring';
COMMENT ON TABLE data_quality.quality_rules IS 'Data quality rules and validation criteria'; 