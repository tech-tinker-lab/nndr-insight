-- Business Rate Forecasting System Schema
-- Comprehensive system for forecasting business rate income and identifying non-rated properties

-- 1. FORECASTING MODELS TABLE
CREATE TABLE IF NOT EXISTS forecasting_models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- 'regression', 'time_series', 'machine_learning', 'ensemble'
    model_description TEXT,
    model_parameters JSONB, -- Model hyperparameters and configuration
    training_data_start_date DATE,
    training_data_end_date DATE,
    model_accuracy_score NUMERIC, -- Overall accuracy score (0-1)
    model_performance_metrics JSONB, -- Detailed performance metrics
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    notes TEXT
);

-- 2. FORECASTS TABLE
CREATE TABLE IF NOT EXISTS forecasts (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES forecasting_models(id),
    property_id INTEGER REFERENCES master_gazetteer(id),
    forecast_period_start DATE NOT NULL,
    forecast_period_end DATE NOT NULL,
    forecast_date DATE NOT NULL, -- When the forecast was made
    
    -- Forecasted values
    forecasted_rateable_value NUMERIC,
    forecasted_annual_charge NUMERIC,
    forecasted_net_charge NUMERIC, -- After reliefs and exemptions
    
    -- Confidence and uncertainty
    confidence_interval_lower NUMERIC,
    confidence_interval_upper NUMERIC,
    confidence_score NUMERIC, -- 0-100 confidence in forecast
    
    -- Forecast factors and reasoning
    forecast_factors JSONB, -- Key factors influencing the forecast
    forecast_assumptions JSONB, -- Assumptions made in the forecast
    forecast_scenario VARCHAR(50), -- 'baseline', 'optimistic', 'pessimistic'
    
    -- Validation and tracking
    actual_value NUMERIC, -- Actual value when known
    forecast_error NUMERIC, -- Difference between forecast and actual
    is_validated BOOLEAN DEFAULT FALSE,
    validation_date DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    notes TEXT
);

-- 3. NON-RATED PROPERTIES TABLE
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
    
    -- Location data
    x_coordinate DOUBLE PRECISION,
    y_coordinate DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    geom GEOMETRY(Point, 27700),
    
    -- Administrative areas
    lad_code VARCHAR(10),
    lad_name TEXT,
    ward_code VARCHAR(10),
    ward_name TEXT,
    
    -- Business indicators
    business_activity_indicator BOOLEAN, -- Signs of business activity
    business_name TEXT,
    business_type VARCHAR(64),
    business_sector VARCHAR(64),
    
    -- Rating potential
    estimated_rateable_value NUMERIC,
    estimated_annual_charge NUMERIC,
    rating_potential_score NUMERIC, -- 0-100 likelihood of being rateable
    rating_potential_factors JSONB, -- Factors indicating rating potential
    
    -- Investigation status
    investigation_status VARCHAR(32), -- 'pending', 'investigating', 'confirmed', 'exempt'
    investigation_date DATE,
    investigation_notes TEXT,
    investigator VARCHAR(100),
    
    -- Data sources
    data_sources JSONB, -- Sources that identified this property
    discovery_date DATE,
    last_verified_date DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    notes TEXT
);

-- 4. FORECASTING SCENARIOS TABLE
CREATE TABLE IF NOT EXISTS forecasting_scenarios (
    id SERIAL PRIMARY KEY,
    scenario_name VARCHAR(100) NOT NULL,
    scenario_description TEXT,
    scenario_type VARCHAR(50), -- 'economic', 'policy', 'market', 'custom'
    
    -- Scenario parameters
    economic_growth_rate NUMERIC, -- Annual economic growth assumption
    inflation_rate NUMERIC, -- Inflation assumption
    market_growth_rate NUMERIC, -- Property market growth assumption
    policy_changes JSONB, -- Expected policy changes
    
    -- Time period
    scenario_start_date DATE,
    scenario_end_date DATE,
    
    -- Impact assessment
    expected_impact_on_rates NUMERIC, -- Expected percentage change in rates
    confidence_level NUMERIC, -- Confidence in scenario (0-100)
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    notes TEXT
);

-- 5. FORECASTING REPORTS TABLE
CREATE TABLE IF NOT EXISTS forecasting_reports (
    id SERIAL PRIMARY KEY,
    report_name VARCHAR(200) NOT NULL,
    report_type VARCHAR(50), -- 'monthly', 'quarterly', 'annual', 'ad_hoc'
    report_period_start DATE,
    report_period_end DATE,
    
    -- Report content
    total_properties_count INTEGER,
    total_rateable_value NUMERIC,
    total_annual_charge NUMERIC,
    total_net_charge NUMERIC,
    
    -- Forecast summary
    forecasted_total_rateable_value NUMERIC,
    forecasted_total_annual_charge NUMERIC,
    forecasted_total_net_charge NUMERIC,
    
    -- Non-rated properties
    non_rated_properties_count INTEGER,
    potential_additional_rateable_value NUMERIC,
    potential_additional_annual_charge NUMERIC,
    
    -- Report metadata
    report_data JSONB, -- Detailed report data
    report_format VARCHAR(20), -- 'pdf', 'excel', 'json'
    report_file_path TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    notes TEXT
);

-- 6. PROPERTY VALUATION HISTORY TABLE
CREATE TABLE IF NOT EXISTS property_valuation_history (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES master_gazetteer(id),
    valuation_date DATE NOT NULL,
    rateable_value NUMERIC,
    effective_date DATE,
    scat_code VARCHAR(16),
    description TEXT,
    
    -- Change tracking
    previous_rateable_value NUMERIC,
    value_change NUMERIC,
    percentage_change NUMERIC,
    
    -- Context
    revaluation_type VARCHAR(32), -- 'general', 'individual', 'appeal'
    appeal_status VARCHAR(32),
    appeal_settlement_code VARCHAR(16),
    
    -- Source information
    source VARCHAR(50),
    source_reference VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- 7. MARKET ANALYSIS TABLE
CREATE TABLE IF NOT EXISTS market_analysis (
    id SERIAL PRIMARY KEY,
    analysis_date DATE NOT NULL,
    lad_code VARCHAR(10),
    property_category_code VARCHAR(16),
    
    -- Market indicators
    average_rateable_value NUMERIC,
    median_rateable_value NUMERIC,
    market_trend VARCHAR(20), -- 'increasing', 'decreasing', 'stable'
    market_volatility NUMERIC,
    
    -- Supply and demand
    total_properties_count INTEGER,
    vacant_properties_count INTEGER,
    new_properties_count INTEGER,
    demolished_properties_count INTEGER,
    
    -- Economic indicators
    local_economic_growth_rate NUMERIC,
    employment_rate NUMERIC,
    business_formation_rate NUMERIC,
    
    -- Analysis results
    market_outlook VARCHAR(20), -- 'positive', 'negative', 'neutral'
    confidence_score NUMERIC, -- 0-100 confidence in analysis
    
    analysis_data JSONB, -- Detailed analysis data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    notes TEXT
);

-- 8. COMPLIANCE AND ENFORCEMENT TABLE
CREATE TABLE IF NOT EXISTS compliance_enforcement (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES master_gazetteer(id),
    
    -- Compliance status
    compliance_status VARCHAR(32), -- 'compliant', 'non_compliant', 'under_investigation'
    compliance_score NUMERIC, -- 0-100 compliance score
    
    -- Enforcement actions
    enforcement_action_type VARCHAR(50), -- 'notice', 'penalty', 'prosecution'
    enforcement_action_date DATE,
    enforcement_action_description TEXT,
    enforcement_action_amount NUMERIC,
    
    -- Investigation details
    investigation_start_date DATE,
    investigation_end_date DATE,
    investigation_outcome VARCHAR(50),
    investigation_notes TEXT,
    
    -- Risk assessment
    risk_level VARCHAR(20), -- 'low', 'medium', 'high', 'critical'
    risk_factors JSONB, -- Factors contributing to risk
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    notes TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS forecasts_model_id_idx ON forecasts(model_id);
CREATE INDEX IF NOT EXISTS forecasts_property_id_idx ON forecasts(property_id);
CREATE INDEX IF NOT EXISTS forecasts_period_idx ON forecasts(forecast_period_start, forecast_period_end);
CREATE INDEX IF NOT EXISTS forecasts_date_idx ON forecasts(forecast_date);

CREATE INDEX IF NOT EXISTS non_rated_properties_uprn_idx ON non_rated_properties(uprn);
CREATE INDEX IF NOT EXISTS non_rated_properties_lad_idx ON non_rated_properties(lad_code);
CREATE INDEX IF NOT EXISTS non_rated_properties_status_idx ON non_rated_properties(investigation_status);
CREATE INDEX IF NOT EXISTS non_rated_properties_potential_idx ON non_rated_properties(rating_potential_score);
CREATE INDEX IF NOT EXISTS non_rated_properties_geom_idx ON non_rated_properties USING GIST(geom);

CREATE INDEX IF NOT EXISTS property_valuation_history_property_idx ON property_valuation_history(property_id);
CREATE INDEX IF NOT EXISTS property_valuation_history_date_idx ON property_valuation_history(valuation_date);

CREATE INDEX IF NOT EXISTS market_analysis_lad_category_idx ON market_analysis(lad_code, property_category_code);
CREATE INDEX IF NOT EXISTS market_analysis_date_idx ON market_analysis(analysis_date);

CREATE INDEX IF NOT EXISTS compliance_enforcement_property_idx ON compliance_enforcement(property_id);
CREATE INDEX IF NOT EXISTS compliance_enforcement_status_idx ON compliance_enforcement(compliance_status);
CREATE INDEX IF NOT EXISTS compliance_enforcement_risk_idx ON compliance_enforcement(risk_level);

-- Comments for documentation
COMMENT ON TABLE forecasting_models IS 'Machine learning and statistical models used for business rate forecasting';
COMMENT ON TABLE forecasts IS 'Individual property forecasts for business rates';
COMMENT ON TABLE non_rated_properties IS 'Properties identified as potentially rateable but not currently rated';
COMMENT ON TABLE forecasting_scenarios IS 'Different economic and policy scenarios for forecasting';
COMMENT ON TABLE forecasting_reports IS 'Generated forecasting reports and summaries';
COMMENT ON TABLE property_valuation_history IS 'Historical valuation changes for properties';
COMMENT ON TABLE market_analysis IS 'Market analysis and trends for different areas and property types';
COMMENT ON TABLE compliance_enforcement IS 'Compliance monitoring and enforcement actions'; 