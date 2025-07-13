-- Create Missing Tables for Seeding Scripts
-- This file creates the tables that the seeding scripts expect to exist in design_enhanced schema

-- =============================================================================
-- MISSING TABLES FOR SEEDING SCRIPTS
-- =============================================================================

-- Add missing columns to existing dataset_structures table
ALTER TABLE design_enhanced.dataset_structures 
ADD COLUMN IF NOT EXISTS sector_code VARCHAR(100);

-- Add missing columns that the seeding script expects
ALTER TABLE design_enhanced.dataset_structures 
ADD COLUMN IF NOT EXISTS field_definitions JSONB DEFAULT '[]';

ALTER TABLE design_enhanced.dataset_structures 
ADD COLUMN IF NOT EXISTS validation_rules JSONB DEFAULT '[]';

ALTER TABLE design_enhanced.dataset_structures 
ADD COLUMN IF NOT EXISTS sample_file_info JSONB DEFAULT '{}';

-- Data Standards Table
CREATE TABLE IF NOT EXISTS design_enhanced.data_standards (
    standard_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    standard_code VARCHAR(100) NOT NULL UNIQUE,
    standard_name VARCHAR(255) NOT NULL,
    standard_type VARCHAR(100) NOT NULL, -- ISO, UK_Standard, UK_Government, EU_Directive, Sector_Specific, Quality_Standard, Open_Data
    governing_body VARCHAR(255),
    description TEXT,
    compliance_level VARCHAR(50), -- mandatory, recommended, optional
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

-- Sectors Table
CREATE TABLE IF NOT EXISTS design_enhanced.sectors (
    sector_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sector_code VARCHAR(100) NOT NULL UNIQUE,
    sector_name VARCHAR(255) NOT NULL,
    sector_category VARCHAR(100), -- government, business, financial, property, etc.
    parent_sector_code VARCHAR(100) REFERENCES design_enhanced.sectors(sector_code),
    description TEXT,
    governing_bodies JSONB DEFAULT '[]',
    data_standards JSONB DEFAULT '[]',
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Governing Bodies Table
CREATE TABLE IF NOT EXISTS design_enhanced.governing_bodies (
    body_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    body_code VARCHAR(100) NOT NULL UNIQUE,
    body_name VARCHAR(255) NOT NULL,
    body_type VARCHAR(100) NOT NULL, -- Central_Government, Local_Government, Agency, Regulator, etc.
    parent_body VARCHAR(100) REFERENCES design_enhanced.governing_bodies(body_code),
    description TEXT,
    data_standards JSONB DEFAULT '[]',
    contact_info JSONB DEFAULT '{}',
    website_url TEXT,
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Sample Datasets Table
CREATE TABLE IF NOT EXISTS design_enhanced.sample_datasets (
    sample_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_name VARCHAR(255) NOT NULL,
    dataset_type VARCHAR(100) NOT NULL,
    source_type VARCHAR(50) DEFAULT 'file',
    governing_body VARCHAR(255),
    data_standards JSONB DEFAULT '[]',
    sector_code VARCHAR(100),
    description TEXT,
    field_definitions JSONB DEFAULT '[]',
    validation_rules JSONB DEFAULT '[]',
    sample_file_info JSONB DEFAULT '{}',
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_data_standards_code ON design_enhanced.data_standards(standard_code);
CREATE INDEX IF NOT EXISTS idx_data_standards_type ON design_enhanced.data_standards(standard_type);
CREATE INDEX IF NOT EXISTS idx_data_standards_active ON design_enhanced.data_standards(is_active);

CREATE INDEX IF NOT EXISTS idx_sectors_code ON design_enhanced.sectors(sector_code);
CREATE INDEX IF NOT EXISTS idx_sectors_category ON design_enhanced.sectors(sector_category);
CREATE INDEX IF NOT EXISTS idx_sectors_active ON design_enhanced.sectors(is_active);

CREATE INDEX IF NOT EXISTS idx_governing_bodies_code ON design_enhanced.governing_bodies(body_code);
CREATE INDEX IF NOT EXISTS idx_governing_bodies_type ON design_enhanced.governing_bodies(body_type);
CREATE INDEX IF NOT EXISTS idx_governing_bodies_active ON design_enhanced.governing_bodies(is_active);

CREATE INDEX IF NOT EXISTS idx_sample_datasets_name ON design_enhanced.sample_datasets(dataset_name);
CREATE INDEX IF NOT EXISTS idx_sample_datasets_type ON design_enhanced.sample_datasets(dataset_type);
CREATE INDEX IF NOT EXISTS idx_sample_datasets_active ON design_enhanced.sample_datasets(is_active);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION design_enhanced.update_missing_tables_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for the new tables
DROP TRIGGER IF EXISTS trigger_update_data_standards_timestamp ON design_enhanced.data_standards;
CREATE TRIGGER trigger_update_data_standards_timestamp
    BEFORE UPDATE ON design_enhanced.data_standards
    FOR EACH ROW EXECUTE FUNCTION design_enhanced.update_missing_tables_timestamp();

DROP TRIGGER IF EXISTS trigger_update_sectors_timestamp ON design_enhanced.sectors;
CREATE TRIGGER trigger_update_sectors_timestamp
    BEFORE UPDATE ON design_enhanced.sectors
    FOR EACH ROW EXECUTE FUNCTION design_enhanced.update_missing_tables_timestamp();

DROP TRIGGER IF EXISTS trigger_update_governing_bodies_timestamp ON design_enhanced.governing_bodies;
CREATE TRIGGER trigger_update_governing_bodies_timestamp
    BEFORE UPDATE ON design_enhanced.governing_bodies
    FOR EACH ROW EXECUTE FUNCTION design_enhanced.update_missing_tables_timestamp();

DROP TRIGGER IF EXISTS trigger_update_sample_datasets_timestamp ON design_enhanced.sample_datasets;
CREATE TRIGGER trigger_update_sample_datasets_timestamp
    BEFORE UPDATE ON design_enhanced.sample_datasets
    FOR EACH ROW EXECUTE FUNCTION design_enhanced.update_missing_tables_timestamp();

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE design_enhanced.data_standards IS 'Data standards and compliance rules for different types of datasets';
COMMENT ON TABLE design_enhanced.sectors IS 'Sector definitions for classifying datasets and organizations';
COMMENT ON TABLE design_enhanced.governing_bodies IS 'Governing bodies and organizations responsible for data standards';
COMMENT ON TABLE design_enhanced.sample_datasets IS 'Sample datasets for AI training and pattern recognition';
COMMENT ON TABLE design_enhanced.migration_history IS 'Audit trail of database migrations and schema changes'; 