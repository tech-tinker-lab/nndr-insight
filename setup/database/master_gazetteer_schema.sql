-- Master Gazetteer Table for NNDR Business Rate Forecasting
-- This table consolidates all property and location data for comprehensive analysis

CREATE TABLE IF NOT EXISTS master_gazetteer (
    -- Primary identification
    id SERIAL PRIMARY KEY,
    uprn BIGINT UNIQUE,  -- Unique Property Reference Number
    ba_reference VARCHAR(32),  -- Billing Authority Reference
    property_id VARCHAR(64),  -- Internal property identifier
    
    -- Property details
    property_name TEXT,
    property_description TEXT,
    property_category_code VARCHAR(16),
    property_category_description TEXT,
    
    -- Address information
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
    
    -- Geographic coordinates
    x_coordinate DOUBLE PRECISION,  -- Easting (OSGB)
    y_coordinate DOUBLE PRECISION,  -- Northing (OSGB)
    latitude DOUBLE PRECISION,      -- WGS84
    longitude DOUBLE PRECISION,     -- WGS84
    geom GEOMETRY(Point, 27700),    -- PostGIS geometry
    
    -- Administrative boundaries
    lad_code VARCHAR(10),           -- Local Authority District code
    lad_name TEXT,                  -- Local Authority District name
    ward_code VARCHAR(10),          -- Electoral ward code
    ward_name TEXT,                 -- Electoral ward name
    parish_code VARCHAR(10),        -- Parish code
    parish_name TEXT,               -- Parish name
    constituency_code VARCHAR(10),  -- Parliamentary constituency
    constituency_name TEXT,         -- Parliamentary constituency name
    
    -- Statistical areas
    lsoa_code VARCHAR(10),          -- Lower Super Output Area
    lsoa_name TEXT,                 -- Lower Super Output Area name
    msoa_code VARCHAR(10),          -- Middle Super Output Area
    msoa_name TEXT,                 -- Middle Super Output Area name
    oa_code VARCHAR(10),            -- Output Area code
    
    -- Economic indicators
    imd_decile INTEGER,             -- Index of Multiple Deprivation decile
    imd_rank INTEGER,               -- Index of Multiple Deprivation rank
    rural_urban_code VARCHAR(2),    -- Rural/Urban classification
    
    -- Property characteristics
    property_type TEXT,             -- Type of property (commercial, industrial, etc.)
    building_type TEXT,             -- Specific building type
    floor_area NUMERIC,             -- Floor area in square meters
    number_of_floors INTEGER,       -- Number of floors
    construction_year INTEGER,      -- Year of construction
    last_refurbished INTEGER,       -- Year of last refurbishment
    
    -- Current rating information
    current_rateable_value NUMERIC,
    current_effective_date DATE,
    current_scat_code VARCHAR(16),
    current_appeal_status VARCHAR(32),
    current_exemption_code VARCHAR(16),
    current_relief_code VARCHAR(16),
    
    -- Historical rating data
    historical_rateable_values JSONB,  -- Array of historical values with dates
    valuation_history_count INTEGER,   -- Number of historical valuations
    
    -- Ratepayer information
    current_ratepayer_name TEXT,
    current_ratepayer_type VARCHAR(32),  -- Individual, Company, Charity, etc.
    current_ratepayer_company_number VARCHAR(32),
    current_liability_start_date DATE,
    current_annual_charge NUMERIC,
    
    -- Business indicators
    business_type VARCHAR(64),      -- Type of business
    business_sector VARCHAR(64),    -- Business sector classification
    employee_count_range VARCHAR(32), -- Estimated employee count range
    turnover_range VARCHAR(32),     -- Estimated turnover range
    
    -- Development and planning
    planning_permission_status VARCHAR(32),
    last_planning_decision_date DATE,
    development_potential_score NUMERIC,  -- 0-100 score for development potential
    
    -- Market indicators
    market_value_estimate NUMERIC,
    market_value_source VARCHAR(32),
    market_value_date DATE,
    rental_value_estimate NUMERIC,
    rental_value_source VARCHAR(32),
    rental_value_date DATE,
    
    -- Risk and compliance
    compliance_risk_score NUMERIC,  -- 0-100 risk score
    last_inspection_date DATE,
    enforcement_notices_count INTEGER,
    
    -- Forecasting indicators
    forecast_rateable_value NUMERIC,
    forecast_effective_date DATE,
    forecast_confidence_score NUMERIC,  -- 0-100 confidence in forecast
    forecast_factors JSONB,         -- Factors influencing forecast
    
    -- Data quality and sources
    data_quality_score NUMERIC,     -- 0-100 data quality score
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_sources JSONB,             -- Array of data sources used
    source_priority INTEGER,        -- Priority of source (1=highest)
    
    -- System fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS master_gazetteer_uprn_idx ON master_gazetteer(uprn);
CREATE INDEX IF NOT EXISTS master_gazetteer_ba_reference_idx ON master_gazetteer(ba_reference);
CREATE INDEX IF NOT EXISTS master_gazetteer_postcode_idx ON master_gazetteer(postcode);
CREATE INDEX IF NOT EXISTS master_gazetteer_lad_code_idx ON master_gazetteer(lad_code);
CREATE INDEX IF NOT EXISTS master_gazetteer_geom_idx ON master_gazetteer USING GIST(geom);
CREATE INDEX IF NOT EXISTS master_gazetteer_category_idx ON master_gazetteer(property_category_code);
CREATE INDEX IF NOT EXISTS master_gazetteer_rateable_value_idx ON master_gazetteer(current_rateable_value);
CREATE INDEX IF NOT EXISTS master_gazetteer_forecast_idx ON master_gazetteer(forecast_rateable_value);

-- Spatial index for geographic queries
CREATE INDEX IF NOT EXISTS master_gazetteer_spatial_idx ON master_gazetteer USING GIST(geom);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS master_gazetteer_lad_category_idx ON master_gazetteer(lad_code, property_category_code);
CREATE INDEX IF NOT EXISTS master_gazetteer_postcode_category_idx ON master_gazetteer(postcode, property_category_code);
CREATE INDEX IF NOT EXISTS master_gazetteer_value_range_idx ON master_gazetteer(current_rateable_value, forecast_rateable_value);

-- Comments for documentation
COMMENT ON TABLE master_gazetteer IS 'Master gazetteer table consolidating all property and location data for NNDR business rate forecasting';
COMMENT ON COLUMN master_gazetteer.uprn IS 'Unique Property Reference Number from OS';
COMMENT ON COLUMN master_gazetteer.ba_reference IS 'Billing Authority Reference from NNDR data';
COMMENT ON COLUMN master_gazetteer.current_rateable_value IS 'Current rateable value for business rates';
COMMENT ON COLUMN master_gazetteer.forecast_rateable_value IS 'Forecasted rateable value for future periods';
COMMENT ON COLUMN master_gazetteer.compliance_risk_score IS 'Risk score for compliance issues (0-100)';
COMMENT ON COLUMN master_gazetteer.development_potential_score IS 'Score indicating development potential (0-100)'; 