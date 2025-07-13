-- Reference Schema - Unified Schema File
-- This file drops and recreates the reference schema with all its objects
-- Combines reference schema files for migration history, upload history, users, and staging configs

-- Drop existing schema if it exists (for clean recreation)
DROP SCHEMA IF EXISTS reference CASCADE;

-- Create reference schema
CREATE SCHEMA reference;

-- =============================================================================
-- MIGRATION HISTORY
-- =============================================================================

-- Create migration history table
CREATE TABLE IF NOT EXISTS reference.migration_history (
    id SERIAL PRIMARY KEY,
    migration_name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checksum VARCHAR(64),
    execution_time_ms INTEGER,
    status VARCHAR(50) DEFAULT 'success',
    error_message TEXT,
    applied_by VARCHAR(100) DEFAULT 'system'
);

-- =============================================================================
-- UPLOAD HISTORY
-- =============================================================================

-- Create upload history table
CREATE TABLE IF NOT EXISTS reference.upload_history (
    id SERIAL PRIMARY KEY,
    upload_id UUID DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    file_size BIGINT,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by VARCHAR(100),
    status VARCHAR(50) DEFAULT 'uploaded',
    table_name VARCHAR(255),
    row_count INTEGER,
    processing_time_ms INTEGER,
    error_message TEXT,
    source_file TEXT
);

-- =============================================================================
-- USERS
-- =============================================================================

-- Create users table
CREATE TABLE IF NOT EXISTS reference.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    permissions JSONB DEFAULT '{}',
    
    -- Constraints
    CONSTRAINT valid_role CHECK (role IN ('admin', 'user', 'viewer', 'data_steward'))
);

-- =============================================================================
-- REFERENCE STAGING CONFIGS
-- =============================================================================

-- Create reference staging configs table (separate from staging schema)
CREATE TABLE IF NOT EXISTS reference.staging_configs (
    id SERIAL PRIMARY KEY,
    config_name VARCHAR(255) NOT NULL UNIQUE,
    table_name VARCHAR(255) NOT NULL,
    column_mappings JSONB NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    delimiter VARCHAR(10),
    has_header BOOLEAN DEFAULT true,
    encoding VARCHAR(50) DEFAULT 'utf-8',
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    description TEXT,
    sample_data JSONB,
    validation_rules JSONB
);

-- =============================================================================
-- DATA QUALITY RULES
-- =============================================================================

-- Create data quality rules table
CREATE TABLE IF NOT EXISTS reference.data_quality_rules (
    rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(255) NOT NULL UNIQUE,
    rule_type VARCHAR(100) NOT NULL, -- completeness, accuracy, consistency, validity, uniqueness
    table_name VARCHAR(255),
    column_name VARCHAR(255),
    rule_definition JSONB NOT NULL,
    severity VARCHAR(50) DEFAULT 'warning', -- info, warning, error, critical
    is_active BOOLEAN DEFAULT true,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    
    -- Constraints
    CONSTRAINT valid_rule_type CHECK (rule_type IN ('completeness', 'accuracy', 'consistency', 'validity', 'uniqueness')),
    CONSTRAINT valid_severity CHECK (severity IN ('info', 'warning', 'error', 'critical'))
);

-- =============================================================================
-- DATA STANDARDS REFERENCE
-- =============================================================================

-- Create data standards reference table
CREATE TABLE IF NOT EXISTS reference.data_standards_ref (
    standard_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    standard_code VARCHAR(100) NOT NULL UNIQUE,
    standard_name VARCHAR(255) NOT NULL,
    standard_type VARCHAR(100) NOT NULL, -- ISO, UK_Standard, UK_Government, EU_Directive, Sector_Specific
    governing_body VARCHAR(255),
    description TEXT,
    version VARCHAR(50),
    effective_date DATE,
    expiry_date DATE,
    website_url TEXT,
    contact_info JSONB DEFAULT '{}',
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- =============================================================================
-- SECTORS REFERENCE
-- =============================================================================

-- Create sectors reference table
CREATE TABLE IF NOT EXISTS reference.sectors_ref (
    sector_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sector_code VARCHAR(100) NOT NULL UNIQUE,
    sector_name VARCHAR(255) NOT NULL,
    sector_category VARCHAR(100), -- government, business, financial, property, etc.
    parent_sector_code VARCHAR(100) REFERENCES reference.sectors_ref(sector_code),
    description TEXT,
    governing_bodies JSONB DEFAULT '[]',
    data_standards JSONB DEFAULT '[]',
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- =============================================================================
-- GOVERNING BODIES REFERENCE
-- =============================================================================

-- Create governing bodies reference table
CREATE TABLE IF NOT EXISTS reference.governing_bodies_ref (
    body_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    body_code VARCHAR(100) NOT NULL UNIQUE,
    body_name VARCHAR(255) NOT NULL,
    body_type VARCHAR(100) NOT NULL, -- Central_Government, Local_Government, Agency, Regulator, etc.
    parent_body VARCHAR(100) REFERENCES reference.governing_bodies_ref(body_code),
    description TEXT,
    data_standards JSONB DEFAULT '[]',
    contact_info JSONB DEFAULT '{}',
    website_url TEXT,
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Migration history indexes
CREATE INDEX IF NOT EXISTS idx_migration_history_name ON reference.migration_history(migration_name);
CREATE INDEX IF NOT EXISTS idx_migration_history_applied_at ON reference.migration_history(applied_at);
CREATE INDEX IF NOT EXISTS idx_migration_history_status ON reference.migration_history(status);

-- Upload history indexes
CREATE INDEX IF NOT EXISTS idx_upload_history_upload_id ON reference.upload_history(upload_id);
CREATE INDEX IF NOT EXISTS idx_upload_history_timestamp ON reference.upload_history(upload_timestamp);
CREATE INDEX IF NOT EXISTS idx_upload_history_status ON reference.upload_history(status);
CREATE INDEX IF NOT EXISTS idx_upload_history_table_name ON reference.upload_history(table_name);

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON reference.users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON reference.users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON reference.users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON reference.users(is_active);

-- Staging configs indexes
CREATE INDEX IF NOT EXISTS idx_ref_staging_configs_name ON reference.staging_configs(config_name);
CREATE INDEX IF NOT EXISTS idx_ref_staging_configs_table ON reference.staging_configs(table_name);
CREATE INDEX IF NOT EXISTS idx_ref_staging_configs_active ON reference.staging_configs(is_active);

-- Data quality rules indexes
CREATE INDEX IF NOT EXISTS idx_data_quality_rules_name ON reference.data_quality_rules(rule_name);
CREATE INDEX IF NOT EXISTS idx_data_quality_rules_type ON reference.data_quality_rules(rule_type);
CREATE INDEX IF NOT EXISTS idx_data_quality_rules_table ON reference.data_quality_rules(table_name);
CREATE INDEX IF NOT EXISTS idx_data_quality_rules_active ON reference.data_quality_rules(is_active);

-- Data standards indexes
CREATE INDEX IF NOT EXISTS idx_data_standards_ref_code ON reference.data_standards_ref(standard_code);
CREATE INDEX IF NOT EXISTS idx_data_standards_ref_type ON reference.data_standards_ref(standard_type);
CREATE INDEX IF NOT EXISTS idx_data_standards_ref_active ON reference.data_standards_ref(is_active);

-- Sectors indexes
CREATE INDEX IF NOT EXISTS idx_sectors_ref_code ON reference.sectors_ref(sector_code);
CREATE INDEX IF NOT EXISTS idx_sectors_ref_category ON reference.sectors_ref(sector_category);
CREATE INDEX IF NOT EXISTS idx_sectors_ref_active ON reference.sectors_ref(is_active);

-- Governing bodies indexes
CREATE INDEX IF NOT EXISTS idx_governing_bodies_ref_code ON reference.governing_bodies_ref(body_code);
CREATE INDEX IF NOT EXISTS idx_governing_bodies_ref_type ON reference.governing_bodies_ref(body_type);
CREATE INDEX IF NOT EXISTS idx_governing_bodies_ref_active ON reference.governing_bodies_ref(is_active);

-- =============================================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION reference.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON reference.users 
    FOR EACH ROW EXECUTE FUNCTION reference.update_updated_at_column();

CREATE TRIGGER update_staging_configs_updated_at 
    BEFORE UPDATE ON reference.staging_configs 
    FOR EACH ROW EXECUTE FUNCTION reference.update_updated_at_column();

CREATE TRIGGER update_data_quality_rules_updated_at 
    BEFORE UPDATE ON reference.data_quality_rules 
    FOR EACH ROW EXECUTE FUNCTION reference.update_updated_at_column();

CREATE TRIGGER update_data_standards_ref_updated_at 
    BEFORE UPDATE ON reference.data_standards_ref 
    FOR EACH ROW EXECUTE FUNCTION reference.update_updated_at_column();

CREATE TRIGGER update_sectors_ref_updated_at 
    BEFORE UPDATE ON reference.sectors_ref 
    FOR EACH ROW EXECUTE FUNCTION reference.update_updated_at_column();

CREATE TRIGGER update_governing_bodies_ref_updated_at 
    BEFORE UPDATE ON reference.governing_bodies_ref 
    FOR EACH ROW EXECUTE FUNCTION reference.update_updated_at_column();

-- =============================================================================
-- SAMPLE DATA
-- =============================================================================

-- Insert default admin user
INSERT INTO reference.users (
    username, email, full_name, role, is_active, permissions
) VALUES 
(
    'admin',
    'admin@nndr-insight.local',
    'System Administrator',
    'admin',
    true,
    '{"all": true}'::jsonb
) ON CONFLICT (username) DO NOTHING;

-- Insert sample data quality rules
INSERT INTO reference.data_quality_rules (
    rule_name, rule_type, table_name, column_name, rule_definition, severity, created_by, description
) VALUES 
(
    'postcode_format',
    'validity',
    'onspd_staging',
    'pcd',
    '{"pattern": "^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$", "description": "UK postcode format validation"}'::jsonb,
    'error',
    'system',
    'Validates UK postcode format'
),
(
    'required_uprn',
    'completeness',
    'nndr_properties_staging',
    'uprn',
    '{"not_null": true, "description": "UPRN must not be null"}'::jsonb,
    'error',
    'system',
    'Ensures UPRN field is populated'
),
(
    'positive_rateable_value',
    'validity',
    'nndr_properties_staging',
    'rateable_value',
    '{"min_value": 0, "description": "Rateable value must be positive"}'::jsonb,
    'warning',
    'system',
    'Validates rateable value is positive'
) ON CONFLICT (rule_name) DO NOTHING;

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON SCHEMA reference IS 'Reference data and system configuration tables';
COMMENT ON TABLE reference.migration_history IS 'History of database migrations applied';
COMMENT ON TABLE reference.upload_history IS 'History of file uploads and processing';
COMMENT ON TABLE reference.users IS 'System users and their permissions';
COMMENT ON TABLE reference.staging_configs IS 'Reference staging configurations';
COMMENT ON TABLE reference.data_quality_rules IS 'Data quality validation rules';
COMMENT ON TABLE reference.data_standards_ref IS 'Reference data standards and compliance rules';
COMMENT ON TABLE reference.sectors_ref IS 'Reference sector definitions';
COMMENT ON TABLE reference.governing_bodies_ref IS 'Reference governing bodies and organizations'; 