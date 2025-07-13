-- Staging Schema - Unified Schema File
-- This file drops and recreates the staging schema with all its objects

-- Drop existing schema if it exists (for clean recreation)
DROP SCHEMA IF EXISTS staging CASCADE;

-- Create the staging schema
CREATE SCHEMA staging;

-- Set search path to include staging schema
SET search_path TO staging, public;

-- =============================================================================
-- STAGING CONFIGURATIONS
-- =============================================================================

-- Create staging configurations table
CREATE TABLE IF NOT EXISTS staging.staging_configs (
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
-- UPLOAD METADATA
-- =============================================================================

-- Create upload metadata tracking table
CREATE TABLE IF NOT EXISTS staging.upload_metadata (
    id SERIAL PRIMARY KEY,
    upload_id UUID DEFAULT gen_random_uuid(),
    original_filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'uploaded',
    table_name VARCHAR(255),
    config_used_id INTEGER REFERENCES staging.staging_configs(id),
    row_count INTEGER,
    processing_time_ms INTEGER,
    error_message TEXT,
    source_file TEXT,
    metadata JSONB
);

-- =============================================================================
-- AUDIT TRAIL
-- =============================================================================

-- Create audit trail for staging operations
CREATE TABLE IF NOT EXISTS staging.staging_audit_log (
    id SERIAL PRIMARY KEY,
    operation_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(255),
    operation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    performed_by VARCHAR(100),
    operation_details JSONB,
    affected_rows INTEGER
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_staging_configs_name ON staging.staging_configs(config_name);
CREATE INDEX IF NOT EXISTS idx_staging_configs_table ON staging.staging_configs(table_name);
CREATE INDEX IF NOT EXISTS idx_upload_metadata_upload_id ON staging.upload_metadata(upload_id);
CREATE INDEX IF NOT EXISTS idx_upload_metadata_timestamp ON staging.upload_metadata(upload_timestamp);
CREATE INDEX IF NOT EXISTS idx_upload_metadata_status ON staging.upload_metadata(status);
CREATE INDEX IF NOT EXISTS idx_staging_audit_timestamp ON staging.staging_audit_log(operation_timestamp);
CREATE INDEX IF NOT EXISTS idx_staging_audit_table ON staging.staging_audit_log(table_name);

-- =============================================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =============================================================================

-- Create function to update timestamp on staging_configs
CREATE OR REPLACE FUNCTION staging.update_staging_configs_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for staging_configs timestamp update
DROP TRIGGER IF EXISTS trigger_update_staging_configs_timestamp ON staging.staging_configs;
CREATE TRIGGER trigger_update_staging_configs_timestamp
    BEFORE UPDATE ON staging.staging_configs
    FOR EACH ROW
    EXECUTE FUNCTION staging.update_staging_configs_timestamp();

-- =============================================================================
-- SAMPLE CONFIGURATIONS
-- =============================================================================

-- Insert sample staging configurations
INSERT INTO staging.staging_configs (
    config_name, table_name, column_mappings, file_type, delimiter, 
    has_header, encoding, created_by, description
) VALUES 
(
    'OS Open Names CSV',
    'os_open_names_staging',
    '{
        "name": "name",
        "local_type": "local_type", 
        "easting": "easting",
        "northing": "northing",
        "latitude": "latitude",
        "longitude": "longitude",
        "district": "district",
        "county": "county"
    }'::jsonb,
    'csv',
    ',',
    true,
    'utf-8',
    'system',
    'Configuration for OS Open Names CSV files'
),
(
    'NNDR Properties CSV',
    'nndr_properties_staging',
    '{
        "uprn": "uprn",
        "property_address": "property_address",
        "rateable_value": "rateable_value",
        "property_type": "property_type",
        "occupancy_status": "occupancy_status",
        "local_authority": "local_authority"
    }'::jsonb,
    'csv',
    ',',
    true,
    'utf-8',
    'system',
    'Configuration for NNDR Properties CSV files'
),
(
    'ONS Postcode Directory CSV',
    'onspd_staging',
    '{
        "pcd": "pcd",
        "pcd2": "pcd2",
        "oseast1m": "oseast1m",
        "osnrth1m": "osnrth1m",
        "laua": "laua",
        "ward": "ward",
        "ctry": "ctry",
        "rgn": "rgn"
    }'::jsonb,
    'csv',
    ',',
    true,
    'utf-8',
    'system',
    'Configuration for ONS Postcode Directory CSV files'
) ON CONFLICT (config_name) DO NOTHING;

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON SCHEMA staging IS 'Staging area for data uploads and processing';
COMMENT ON TABLE staging.staging_configs IS 'Configuration for staging table mappings';
COMMENT ON TABLE staging.upload_metadata IS 'Metadata tracking for file uploads';
COMMENT ON TABLE staging.staging_audit_log IS 'Audit trail for staging operations';

-- Reset search path
SET search_path TO public; 