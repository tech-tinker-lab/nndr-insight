-- Design Enhanced Schema - Unified Schema File
-- This file drops and recreates the design_enhanced schema with all its objects
-- Combines design/03_create_enhanced_design_system.sql and design/04_create_missing_tables.sql

-- Drop existing schema if it exists (for clean recreation)
DROP SCHEMA IF EXISTS design_enhanced CASCADE;

-- Create dataset structures schema
CREATE SCHEMA design_enhanced;

-- Enable PostGIS extension if not already enabled
CREATE EXTENSION IF NOT EXISTS postgis;

-- =============================================================================
-- DATASET STRUCTURES
-- =============================================================================

-- Dataset Structure Definition Table
CREATE TABLE IF NOT EXISTS design_enhanced.dataset_structures (
    structure_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    dataset_type VARCHAR(100) NOT NULL, -- property, address, postcode, boundary, business, financial, etc.
    source_type VARCHAR(50) DEFAULT 'file', -- file, api, database, stream
    file_formats JSONB DEFAULT '[]', -- Supported file formats (CSV, JSON, XML, etc.)
    governing_body VARCHAR(255), -- ONS, Ordinance Survey, etc.
    data_standards JSONB DEFAULT '[]', -- SDMX, ISO 20022, etc.
    business_owner VARCHAR(255),
    data_steward VARCHAR(255),
    ingestion_pattern VARCHAR(100) DEFAULT 'standard', -- standard, batch, realtime, scheduled
    target_schema_type VARCHAR(50) DEFAULT 'staging', -- staging, intermediate, master, archive
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, inactive, archived
    is_active BOOLEAN DEFAULT true,
    tags JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    sector_code VARCHAR(100),
    field_definitions JSONB DEFAULT '[]',
    validation_rules JSONB DEFAULT '[]',
    sample_file_info JSONB DEFAULT '{}',

    -- Constraints
    CONSTRAINT valid_source_type CHECK (source_type IN ('file', 'api', 'database', 'stream')),
    CONSTRAINT valid_status CHECK (status IN ('draft', 'active', 'inactive', 'archived')),
    CONSTRAINT valid_ingestion_pattern CHECK (ingestion_pattern IN ('standard', 'batch', 'realtime', 'scheduled')),
    CONSTRAINT valid_target_schema_type CHECK (target_schema_type IN ('staging', 'intermediate', 'master', 'archive'))
);

-- =============================================================================
-- FIELD DEFINITIONS
-- =============================================================================

-- Field Definition Table with PostGIS Support
CREATE TABLE IF NOT EXISTS design_enhanced.field_definitions (
    field_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    structure_id UUID NOT NULL REFERENCES design_enhanced.dataset_structures(structure_id) ON DELETE CASCADE,
    field_name VARCHAR(255) NOT NULL,
    field_type VARCHAR(100) NOT NULL, -- text, integer, numeric, boolean, date, timestamp, geometry, geography
    postgis_type VARCHAR(100), -- POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, MULTIPOLYGON, GEOMETRYCOLLECTION
    srid INTEGER DEFAULT 4326, -- Spatial Reference System Identifier
    field_length INTEGER, -- For VARCHAR fields
    field_precision INTEGER, -- For DECIMAL fields
    field_scale INTEGER, -- For DECIMAL fields
    is_required BOOLEAN DEFAULT false,
    is_primary_key BOOLEAN DEFAULT false,
    is_unique BOOLEAN DEFAULT false,
    has_index BOOLEAN DEFAULT false,
    default_value TEXT,
    description TEXT,
    validation_rules JSONB DEFAULT '[]',
    transformation_rules JSONB DEFAULT '[]',
    sequence_order INTEGER NOT NULL,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_field_type CHECK (field_type IN ('text', 'varchar', 'integer', 'bigint', 'numeric', 'decimal', 'boolean', 'date', 'timestamp', 'geometry', 'geography', 'jsonb')),
    CONSTRAINT valid_postgis_type CHECK (postgis_type IS NULL OR postgis_type IN ('POINT', 'LINESTRING', 'POLYGON', 'MULTIPOINT', 'MULTILINESTRING', 'MULTIPOLYGON', 'GEOMETRYCOLLECTION')),
    CONSTRAINT valid_srid CHECK (srid >= 0),
    CONSTRAINT unique_field_sequence UNIQUE (structure_id, sequence_order)
);

-- =============================================================================
-- TABLE TEMPLATES
-- =============================================================================

-- Table Generation Templates
CREATE TABLE IF NOT EXISTS design_enhanced.table_templates (
    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_name VARCHAR(255) NOT NULL UNIQUE,
    template_type VARCHAR(100) NOT NULL, -- staging, master, intermediate, archive
    structure_id UUID REFERENCES design_enhanced.dataset_structures(structure_id) ON DELETE CASCADE,
    table_name_pattern VARCHAR(255), -- Pattern for table naming (e.g., {dataset_name}_staging)
    schema_name VARCHAR(100) DEFAULT 'public',
    include_audit_fields BOOLEAN DEFAULT true,
    include_source_tracking BOOLEAN DEFAULT true,
    include_processing_metadata BOOLEAN DEFAULT true,
    postgis_enabled BOOLEAN DEFAULT false,
    indexes_config JSONB DEFAULT '[]',
    constraints_config JSONB DEFAULT '[]',
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    
    -- Constraints
    CONSTRAINT valid_template_type CHECK (template_type IN ('staging', 'master', 'intermediate', 'archive'))
);

-- =============================================================================
-- GENERATED TABLES
-- =============================================================================

-- Generated Tables Registry
CREATE TABLE IF NOT EXISTS design_enhanced.generated_tables (
    table_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID REFERENCES design_enhanced.table_templates(template_id) ON DELETE CASCADE,
    structure_id UUID REFERENCES design_enhanced.dataset_structures(structure_id) ON DELETE CASCADE,
    table_name VARCHAR(255) NOT NULL UNIQUE,
    schema_name VARCHAR(100) NOT NULL,
    table_type VARCHAR(100) NOT NULL,
    ddl_script TEXT NOT NULL, -- The actual CREATE TABLE script
    postgis_fields JSONB DEFAULT '[]', -- List of PostGIS fields in this table
    field_mappings JSONB DEFAULT '[]', -- Mapping from structure fields to table fields
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'created', -- created, deployed, active, inactive, archived
    
    -- Constraints
    CONSTRAINT valid_table_type CHECK (table_type IN ('staging', 'master', 'intermediate', 'archive')),
    CONSTRAINT valid_status CHECK (status IN ('created', 'deployed', 'active', 'inactive', 'archived'))
);

-- =============================================================================
-- FIELD MAPPINGS
-- =============================================================================

-- Field Mapping Configuration
CREATE TABLE IF NOT EXISTS design_enhanced.field_mappings (
    mapping_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    structure_id UUID NOT NULL REFERENCES design_enhanced.dataset_structures(structure_id) ON DELETE CASCADE,
    source_field_name VARCHAR(255) NOT NULL,
    target_field_name VARCHAR(255) NOT NULL,
    mapping_type VARCHAR(100) NOT NULL, -- direct, transformation, calculation, lookup
    transformation_script TEXT, -- SQL or Python transformation script
    lookup_config JSONB DEFAULT '{}', -- Configuration for lookup mappings
    validation_rules JSONB DEFAULT '[]',
    is_required BOOLEAN DEFAULT false,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_mapping_type CHECK (mapping_type IN ('direct', 'transformation', 'calculation', 'lookup'))
);

-- =============================================================================
-- DATASET UPLOADS
-- =============================================================================

-- Dataset Upload and Processing
CREATE TABLE IF NOT EXISTS design_enhanced.dataset_uploads (
    upload_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    structure_id UUID NOT NULL REFERENCES design_enhanced.dataset_structures(structure_id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(100),
    file_path VARCHAR(500),
    detected_schema JSONB DEFAULT '{}', -- AI-detected schema from file
    field_mapping_results JSONB DEFAULT '{}', -- Results of field mapping process
    validation_results JSONB DEFAULT '{}', -- Validation results
    processing_status VARCHAR(50) DEFAULT 'uploaded', -- uploaded, mapping, validating, processing, completed, failed
    target_table_name VARCHAR(255), -- The table where data will be loaded
    records_processed INTEGER DEFAULT 0,
    records_valid INTEGER DEFAULT 0,
    records_invalid INTEGER DEFAULT 0,
    error_message TEXT,
    uploaded_by VARCHAR(100) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_processing_status CHECK (processing_status IN ('uploaded', 'mapping', 'validating', 'processing', 'completed', 'failed'))
);

-- =============================================================================
-- DATASET TYPES
-- =============================================================================

-- Dataset Type Definitions
CREATE TABLE IF NOT EXISTS design_enhanced.dataset_types (
    type_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL, -- government, business, financial, property, address, etc.
    governing_body VARCHAR(255),
    data_standards JSONB DEFAULT '[]',
    required_fields JSONB DEFAULT '[]',
    optional_fields JSONB DEFAULT '[]',
    validation_rules JSONB DEFAULT '[]',
    sample_data JSONB DEFAULT '{}',
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    
    -- Constraints
    CONSTRAINT valid_category CHECK (category IN ('government', 'business', 'financial', 'property', 'address', 'postcode', 'boundary', 'economic', 'demographic', 'environmental', 'transport', 'health', 'education', 'other'))
);

-- =============================================================================
-- REVIEW WORKFLOW
-- =============================================================================

-- Review and Verification Workflow
CREATE TABLE IF NOT EXISTS design_enhanced.review_workflow (
    review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upload_id UUID NOT NULL REFERENCES design_enhanced.dataset_uploads(upload_id) ON DELETE CASCADE,
    structure_id UUID NOT NULL REFERENCES design_enhanced.dataset_structures(structure_id) ON DELETE CASCADE,
    review_type VARCHAR(100) NOT NULL, -- structure_review, mapping_review, data_quality_review, final_approval
    reviewer_id VARCHAR(100) NOT NULL,
    review_status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected, needs_changes
    review_notes TEXT,
    required_changes JSONB DEFAULT '[]',
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    next_reviewer_id VARCHAR(100),
    
    -- Constraints
    CONSTRAINT valid_review_type CHECK (review_type IN ('structure_review', 'mapping_review', 'data_quality_review', 'final_approval')),
    CONSTRAINT valid_review_status CHECK (review_status IN ('pending', 'approved', 'rejected', 'needs_changes'))
);

-- =============================================================================
-- DATA STANDARDS
-- =============================================================================

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

-- =============================================================================
-- SECTORS
-- =============================================================================

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

-- =============================================================================
-- GOVERNING BODIES
-- =============================================================================

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

-- =============================================================================
-- SAMPLE DATASETS
-- =============================================================================

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

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Dataset structures indexes
CREATE INDEX IF NOT EXISTS idx_dataset_structures_type ON design_enhanced.dataset_structures(dataset_type);
CREATE INDEX IF NOT EXISTS idx_dataset_structures_source_type ON design_enhanced.dataset_structures(source_type);
CREATE INDEX IF NOT EXISTS idx_dataset_structures_status ON design_enhanced.dataset_structures(status);
CREATE INDEX IF NOT EXISTS idx_dataset_structures_created_by ON design_enhanced.dataset_structures(created_by);

-- Field definitions indexes
CREATE INDEX IF NOT EXISTS idx_field_definitions_structure ON design_enhanced.field_definitions(structure_id);
CREATE INDEX IF NOT EXISTS idx_field_definitions_type ON design_enhanced.field_definitions(field_type);
CREATE INDEX IF NOT EXISTS idx_field_definitions_postgis ON design_enhanced.field_definitions(postgis_type);

-- Table templates indexes
CREATE INDEX IF NOT EXISTS idx_table_templates_type ON design_enhanced.table_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_table_templates_structure ON design_enhanced.table_templates(structure_id);

-- Generated tables indexes
CREATE INDEX IF NOT EXISTS idx_generated_tables_name ON design_enhanced.generated_tables(table_name);
CREATE INDEX IF NOT EXISTS idx_generated_tables_type ON design_enhanced.generated_tables(table_type);
CREATE INDEX IF NOT EXISTS idx_generated_tables_status ON design_enhanced.generated_tables(status);

-- Field mappings indexes
CREATE INDEX IF NOT EXISTS idx_field_mappings_structure ON design_enhanced.field_mappings(structure_id);
CREATE INDEX IF NOT EXISTS idx_field_mappings_type ON design_enhanced.field_mappings(mapping_type);

-- Dataset uploads indexes
CREATE INDEX IF NOT EXISTS idx_dataset_uploads_structure ON design_enhanced.dataset_uploads(structure_id);
CREATE INDEX IF NOT EXISTS idx_dataset_uploads_status ON design_enhanced.dataset_uploads(processing_status);
CREATE INDEX IF NOT EXISTS idx_dataset_uploads_uploaded_by ON design_enhanced.dataset_uploads(uploaded_by);

-- Review workflow indexes
CREATE INDEX IF NOT EXISTS idx_review_workflow_upload ON design_enhanced.review_workflow(upload_id);
CREATE INDEX IF NOT EXISTS idx_review_workflow_type ON design_enhanced.review_workflow(review_type);
CREATE INDEX IF NOT EXISTS idx_review_workflow_status ON design_enhanced.review_workflow(review_status);

-- Dataset types indexes
CREATE INDEX IF NOT EXISTS idx_dataset_types_category ON design_enhanced.dataset_types(category);
CREATE INDEX IF NOT EXISTS idx_dataset_types_governing_body ON design_enhanced.dataset_types(governing_body);
CREATE INDEX IF NOT EXISTS idx_dataset_types_active ON design_enhanced.dataset_types(is_active);

-- Data standards indexes
CREATE INDEX IF NOT EXISTS idx_data_standards_code ON design_enhanced.data_standards(standard_code);
CREATE INDEX IF NOT EXISTS idx_data_standards_type ON design_enhanced.data_standards(standard_type);
CREATE INDEX IF NOT EXISTS idx_data_standards_active ON design_enhanced.data_standards(is_active);

-- Sectors indexes
CREATE INDEX IF NOT EXISTS idx_sectors_code ON design_enhanced.sectors(sector_code);
CREATE INDEX IF NOT EXISTS idx_sectors_category ON design_enhanced.sectors(sector_category);
CREATE INDEX IF NOT EXISTS idx_sectors_active ON design_enhanced.sectors(is_active);

-- Governing bodies indexes
CREATE INDEX IF NOT EXISTS idx_governing_bodies_code ON design_enhanced.governing_bodies(body_code);
CREATE INDEX IF NOT EXISTS idx_governing_bodies_type ON design_enhanced.governing_bodies(body_type);
CREATE INDEX IF NOT EXISTS idx_governing_bodies_active ON design_enhanced.governing_bodies(is_active);

-- Sample datasets indexes
CREATE INDEX IF NOT EXISTS idx_sample_datasets_name ON design_enhanced.sample_datasets(dataset_name);
CREATE INDEX IF NOT EXISTS idx_sample_datasets_type ON design_enhanced.sample_datasets(dataset_type);
CREATE INDEX IF NOT EXISTS idx_sample_datasets_active ON design_enhanced.sample_datasets(is_active);

-- =============================================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION design_enhanced.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER update_dataset_structures_updated_at 
    BEFORE UPDATE ON design_enhanced.dataset_structures 
    FOR EACH ROW EXECUTE FUNCTION design_enhanced.update_updated_at_column();

CREATE TRIGGER update_field_definitions_updated_at 
    BEFORE UPDATE ON design_enhanced.field_definitions 
    FOR EACH ROW EXECUTE FUNCTION design_enhanced.update_updated_at_column();

CREATE TRIGGER update_table_templates_updated_at 
    BEFORE UPDATE ON design_enhanced.table_templates 
    FOR EACH ROW EXECUTE FUNCTION design_enhanced.update_updated_at_column();

CREATE TRIGGER update_generated_tables_updated_at 
    BEFORE UPDATE ON design_enhanced.generated_tables 
    FOR EACH ROW EXECUTE FUNCTION design_enhanced.update_updated_at_column();

CREATE TRIGGER update_field_mappings_updated_at 
    BEFORE UPDATE ON design_enhanced.field_mappings 
    FOR EACH ROW EXECUTE FUNCTION design_enhanced.update_updated_at_column();

CREATE TRIGGER update_dataset_types_updated_at 
    BEFORE UPDATE ON design_enhanced.dataset_types 
    FOR EACH ROW EXECUTE FUNCTION design_enhanced.update_updated_at_column();

-- Create triggers for the new tables
CREATE TRIGGER trigger_update_data_standards_timestamp
    BEFORE UPDATE ON design_enhanced.data_standards
    FOR EACH ROW EXECUTE FUNCTION design_enhanced.update_updated_at_column();

CREATE TRIGGER trigger_update_sectors_timestamp
    BEFORE UPDATE ON design_enhanced.sectors
    FOR EACH ROW EXECUTE FUNCTION design_enhanced.update_updated_at_column();

CREATE TRIGGER trigger_update_governing_bodies_timestamp
    BEFORE UPDATE ON design_enhanced.governing_bodies
    FOR EACH ROW EXECUTE FUNCTION design_enhanced.update_updated_at_column();

CREATE TRIGGER trigger_update_sample_datasets_timestamp
    BEFORE UPDATE ON design_enhanced.sample_datasets
    FOR EACH ROW EXECUTE FUNCTION design_enhanced.update_updated_at_column();

-- =============================================================================
-- SAMPLE DATA
-- =============================================================================

-- Insert sample dataset types
INSERT INTO design_enhanced.dataset_types (
    type_name, display_name, description, category, governing_body, 
    data_standards, required_fields, optional_fields, created_by
) VALUES 
(
    'address',
    'Address Data',
    'Address and location data with coordinates',
    'address',
    'Ordnance Survey',
    '["BS7666", "OS_Standards"]'::jsonb,
    '["address", "postcode", "coordinates"]'::jsonb,
    '["building_name", "street_name", "locality", "town", "county"]'::jsonb,
    'admin'
),
(
    'property',
    'Property Data',
    'Property information and valuations',
    'property',
    'Valuation Office Agency',
    '["VOA_Standards", "NNDR_Standard"]'::jsonb,
    '["property_reference", "address", "rateable_value"]'::jsonb,
    '["property_type", "occupancy_status", "floor_area"]'::jsonb,
    'admin'
),
(
    'postcode',
    'Postcode Data',
    'Postcode and geographic reference data',
    'postcode',
    'Royal Mail',
    '["OS_Standards"]'::jsonb,
    '["postcode", "easting", "northing"]'::jsonb,
    '["latitude", "longitude", "district", "county"]'::jsonb,
    'admin'
),
(
    'boundary',
    'Boundary Data',
    'Administrative and geographic boundary data',
    'boundary',
    'Office for National Statistics',
    '["ONS_Standards", "INSPIRE"]'::jsonb,
    '["boundary_code", "boundary_name", "geometry"]'::jsonb,
    '["parent_boundary", "boundary_type", "effective_date"]'::jsonb,
    'admin'
),
(
    'business',
    'Business Data',
    'Business registration and classification data',
    'business',
    'Companies House',
    '["ONS_Standards"]'::jsonb,
    '["company_number", "company_name", "sic_code"]'::jsonb,
    '["registered_address", "incorporation_date", "status"]'::jsonb,
    'admin'
) ON CONFLICT (type_name) DO NOTHING;

-- Insert sample dataset structures
INSERT INTO design_enhanced.dataset_structures (
    dataset_name, description, dataset_type, source_type, file_formats, governing_body, 
    data_standards, business_owner, data_steward, created_by, status
) VALUES 
(
    'OS Open Names',
    'Ordnance Survey Open Names dataset for place names and addresses',
    'address',
    'file',
    '["csv", "geojson"]'::jsonb,
    'Ordnance Survey',
    '["OS Open Data", "INSPIRE"]'::jsonb,
    'GIS Team',
    'Data Management Team',
    'admin',
    'active'
),
(
    'NNDR Properties',
    'National Non-Domestic Rates property data with valuations',
    'property',
    'file',
    '["csv", "xlsx"]'::jsonb,
    'Valuation Office Agency',
    '["NNDR Standard", "VOA Data"]'::jsonb,
    'Business Rates Team',
    'Finance Team',
    'admin',
    'active'
),
(
    'ONS Postcode Directory',
    'ONS Postcode Directory with geographic and administrative data',
    'postcode',
    'file',
    '["csv"]'::jsonb,
    'Office for National Statistics',
    '["ONS Standards", "BS7666"]'::jsonb,
    'Geographic Data Team',
    'Data Standards Team',
    'admin',
    'active'
) ON CONFLICT (dataset_name) DO NOTHING;

-- =============================================================================
-- VIEWS FOR EASY QUERYING
-- =============================================================================

-- View for complete dataset structure overview
CREATE OR REPLACE VIEW design_enhanced.dataset_structure_overview AS
SELECT
    ds.structure_id,
    ds.dataset_name,
    ds.dataset_type,
    ds.governing_body,
    ds.status,
    ds.is_active,
    COUNT(fd.field_id) as field_count,
    COUNT(gt.table_id) as generated_table_count,
    ds.created_at,
    ds.updated_at
FROM design_enhanced.dataset_structures ds
LEFT JOIN design_enhanced.field_definitions fd ON ds.structure_id = fd.structure_id
LEFT JOIN design_enhanced.generated_tables gt ON ds.structure_id = gt.structure_id
GROUP BY ds.structure_id, ds.dataset_name, ds.dataset_type, ds.governing_body, ds.status, ds.is_active, ds.created_at, ds.updated_at;

-- View for field mapping summary
CREATE OR REPLACE VIEW design_enhanced.field_mapping_summary AS
SELECT
    ds.dataset_name,
    fm.source_field_name,
    fm.target_field_name,
    fm.mapping_type,
    fm.is_required,
    fm.created_at
FROM design_enhanced.field_mappings fm
JOIN design_enhanced.dataset_structures ds ON fm.structure_id = ds.structure_id
ORDER BY ds.dataset_name, fm.source_field_name;

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON SCHEMA design_enhanced IS 'Enhanced design system for dataset structures and field definitions';
COMMENT ON TABLE design_enhanced.dataset_structures IS 'Dataset structure definitions for AI-powered ingestion';
COMMENT ON TABLE design_enhanced.field_definitions IS 'Field definitions with PostGIS support for dataset structures';
COMMENT ON TABLE design_enhanced.table_templates IS 'Table generation templates for different schema types';
COMMENT ON TABLE design_enhanced.generated_tables IS 'Registry of tables generated from templates';
COMMENT ON TABLE design_enhanced.field_mappings IS 'Field mapping configurations for data transformation';
COMMENT ON TABLE design_enhanced.dataset_uploads IS 'Dataset upload and processing tracking';
COMMENT ON TABLE design_enhanced.dataset_types IS 'Dataset type definitions for classification';
COMMENT ON TABLE design_enhanced.review_workflow IS 'Review and verification workflow for datasets';
COMMENT ON TABLE design_enhanced.data_standards IS 'Data standards and compliance rules for different types of datasets';
COMMENT ON TABLE design_enhanced.sectors IS 'Sector definitions for classifying datasets and organizations';
COMMENT ON TABLE design_enhanced.governing_bodies IS 'Governing bodies and organizations responsible for data standards';
COMMENT ON TABLE design_enhanced.sample_datasets IS 'Sample datasets for AI training and pattern recognition'; 