-- Enhanced Schema Update for NNDR Insight
-- Idempotent schema changes for source tracking, duplicate management, and data quality

-- 1. Add source tracking columns to master_gazetteer
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='master_gazetteer' AND column_name='data_source') THEN
        ALTER TABLE master_gazetteer ADD COLUMN data_source VARCHAR(100);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='master_gazetteer' AND column_name='source_priority') THEN
        ALTER TABLE master_gazetteer ADD COLUMN source_priority INTEGER;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='master_gazetteer' AND column_name='source_confidence_score') THEN
        ALTER TABLE master_gazetteer ADD COLUMN source_confidence_score NUMERIC(3,2);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='master_gazetteer' AND column_name='last_source_update') THEN
        ALTER TABLE master_gazetteer ADD COLUMN last_source_update TIMESTAMP;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='master_gazetteer' AND column_name='source_file_reference') THEN
        ALTER TABLE master_gazetteer ADD COLUMN source_file_reference VARCHAR(255);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='master_gazetteer' AND column_name='duplicate_group_id') THEN
        ALTER TABLE master_gazetteer ADD COLUMN duplicate_group_id INTEGER;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='master_gazetteer' AND column_name='is_preferred_record') THEN
        ALTER TABLE master_gazetteer ADD COLUMN is_preferred_record BOOLEAN DEFAULT FALSE;
    END IF;
END $$;

-- 2. Data source management table
CREATE TABLE IF NOT EXISTS data_sources (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) UNIQUE,
    source_type VARCHAR(50),
    source_description TEXT,
    source_priority INTEGER,
    source_quality_score NUMERIC(3,2),
    source_update_frequency VARCHAR(50),
    source_coordinate_system VARCHAR(50),
    source_file_pattern VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Duplicate management table
CREATE TABLE IF NOT EXISTS duplicate_management (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES master_gazetteer(id),
    duplicate_group_id INTEGER,
    duplicate_confidence_score NUMERIC(3,2),
    duplicate_reason TEXT,
    preferred_record BOOLEAN DEFAULT FALSE,
    merged_from_sources JSONB,
    merge_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_duplicate_management_group_id ON duplicate_management(duplicate_group_id);

-- 4. Land Revenue and Property Sales Tables

-- Property Sales Information
CREATE TABLE IF NOT EXISTS property_sales (
    id SERIAL PRIMARY KEY,
    ba_reference VARCHAR(50),
    uprn BIGINT,
    sale_date DATE,
    sale_price NUMERIC(12,2),
    sale_type VARCHAR(50), -- 'freehold', 'leasehold', 'assignment', etc.
    transaction_type VARCHAR(50), -- 'arm_length', 'non_arm_length', 'auction', etc.
    buyer_type VARCHAR(50), -- 'individual', 'company', 'trust', 'government'
    seller_type VARCHAR(50),
    property_condition VARCHAR(50), -- 'good', 'fair', 'poor', 'development'
    planning_permission VARCHAR(50), -- 'none', 'outline', 'full', 'implemented'
    development_potential VARCHAR(50), -- 'none', 'low', 'medium', 'high'
    source_name VARCHAR(100), -- 'land_registry', 'rightmove', 'zoopla', etc.
    source_confidence_score NUMERIC(3,2),
    data_source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Land Revenue Information
CREATE TABLE IF NOT EXISTS land_revenue (
    id SERIAL PRIMARY KEY,
    ba_reference VARCHAR(50),
    uprn BIGINT,
    revenue_year INTEGER,
    revenue_type VARCHAR(50), -- 'rental_income', 'service_charges', 'ground_rent', 'other'
    revenue_amount NUMERIC(12,2),
    revenue_frequency VARCHAR(20), -- 'monthly', 'quarterly', 'annually', 'one_off'
    tenant_type VARCHAR(50), -- 'retail', 'office', 'industrial', 'residential', 'mixed'
    lease_start_date DATE,
    lease_end_date DATE,
    lease_term_years INTEGER,
    rent_review_frequency VARCHAR(20), -- '3_years', '5_years', '10_years', 'none'
    break_clause BOOLEAN,
    break_date DATE,
    source_name VARCHAR(100),
    source_confidence_score NUMERIC(3,2),
    data_source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Property Valuations (Historic and Current)
CREATE TABLE IF NOT EXISTS property_valuations (
    id SERIAL PRIMARY KEY,
    ba_reference VARCHAR(50),
    uprn BIGINT,
    valuation_date DATE,
    valuation_type VARCHAR(50), -- 'market_value', 'investment_value', 'development_value', 'rateable_value'
    valuation_method VARCHAR(50), -- 'comparable_sales', 'income_capitalisation', 'cost_approach', 'residual'
    valuation_amount NUMERIC(12,2),
    valuer_name VARCHAR(100),
    valuer_qualification VARCHAR(50),
    confidence_level VARCHAR(20), -- 'high', 'medium', 'low'
    assumptions TEXT,
    market_conditions VARCHAR(50), -- 'stable', 'rising', 'falling', 'volatile'
    source_name VARCHAR(100),
    source_confidence_score NUMERIC(3,2),
    data_source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Property Market Analysis
CREATE TABLE IF NOT EXISTS market_analysis (
    id SERIAL PRIMARY KEY,
    lad_code VARCHAR(20),
    lad_name VARCHAR(100),
    analysis_date DATE,
    property_type VARCHAR(50), -- 'retail', 'office', 'industrial', 'mixed'
    market_indicator VARCHAR(50), -- 'yield', 'capital_growth', 'rental_growth', 'vacancy_rate'
    indicator_value NUMERIC(8,4),
    trend_direction VARCHAR(10), -- 'up', 'down', 'stable'
    trend_strength VARCHAR(10), -- 'strong', 'moderate', 'weak'
    data_source VARCHAR(100),
    source_confidence_score NUMERIC(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Economic Indicators
CREATE TABLE IF NOT EXISTS economic_indicators (
    id SERIAL PRIMARY KEY,
    indicator_name VARCHAR(100),
    indicator_category VARCHAR(50), -- 'macroeconomic', 'property_specific', 'regional'
    geographic_level VARCHAR(20), -- 'national', 'regional', 'local'
    geographic_code VARCHAR(20),
    geographic_name VARCHAR(100),
    indicator_date DATE,
    indicator_value NUMERIC(12,4),
    unit_of_measure VARCHAR(20),
    data_source VARCHAR(100),
    source_confidence_score NUMERIC(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_property_sales_ba_reference ON property_sales(ba_reference);
CREATE INDEX IF NOT EXISTS idx_property_sales_uprn ON property_sales(uprn);
CREATE INDEX IF NOT EXISTS idx_property_sales_date ON property_sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_property_sales_price ON property_sales(sale_price);

CREATE INDEX IF NOT EXISTS idx_land_revenue_ba_reference ON land_revenue(ba_reference);
CREATE INDEX IF NOT EXISTS idx_land_revenue_uprn ON land_revenue(uprn);
CREATE INDEX IF NOT EXISTS idx_land_revenue_year ON land_revenue(revenue_year);

CREATE INDEX IF NOT EXISTS idx_property_valuations_ba_reference ON property_valuations(ba_reference);
CREATE INDEX IF NOT EXISTS idx_property_valuations_uprn ON property_valuations(uprn);
CREATE INDEX IF NOT EXISTS idx_property_valuations_date ON property_valuations(valuation_date);

CREATE INDEX IF NOT EXISTS idx_market_analysis_lad_date ON market_analysis(lad_code, analysis_date);
CREATE INDEX IF NOT EXISTS idx_market_analysis_type ON market_analysis(property_type);

CREATE INDEX IF NOT EXISTS idx_economic_indicators_date ON economic_indicators(indicator_date);
CREATE INDEX IF NOT EXISTS idx_economic_indicators_category ON economic_indicators(indicator_category);

-- 5. Data quality rules (example insertions)
INSERT INTO data_quality.quality_rules (rule_name, rule_description, table_name, column_name, rule_type, rule_definition, severity)
VALUES
('coordinate_validation_lat', 'Validate latitude for UK', 'master_gazetteer', 'latitude', 'range', 'latitude BETWEEN 49.0 AND 61.0', 'error'),
('coordinate_validation_lon', 'Validate longitude for UK', 'master_gazetteer', 'longitude', 'range', 'longitude BETWEEN -8.0 AND 2.0', 'error'),
('postcode_format', 'Validate UK postcode format', 'master_gazetteer', 'postcode', 'format', 'regex pattern for UK postcodes', 'warning'),
('rateable_value_range', 'Validate rateable value ranges', 'master_gazetteer', 'rateable_value', 'range', 'rateable_value > 0 AND rateable_value < 100000000', 'error'),
('sale_price_validation', 'Validate property sale prices', 'property_sales', 'sale_price', 'range', 'sale_price > 0 AND sale_price < 1000000000', 'error'),
('revenue_amount_validation', 'Validate land revenue amounts', 'land_revenue', 'revenue_amount', 'range', 'revenue_amount >= 0 AND revenue_amount < 10000000', 'error')
ON CONFLICT DO NOTHING; 