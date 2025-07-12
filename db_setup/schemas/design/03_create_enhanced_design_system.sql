-- Enhanced Design System Schema for Dataset Structure and PostGIS Field Mapping
-- Supports dataset details capture, structure definition, table creation for ingestion, and field mapping with PostGIS

-- Drop existing schema if it exists (for clean recreation)
DROP SCHEMA IF EXISTS design_enhanced CASCADE;

-- Create enhanced design schema
CREATE SCHEMA design_enhanced;

-- Enable PostGIS extension if not already enabled
CREATE EXTENSION IF NOT EXISTS postgis;

-- Dataset Structure Definition Table
CREATE TABLE IF NOT EXISTS design_enhanced.dataset_structures (
    structure_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    source_type VARCHAR(50) DEFAULT 'file', -- file, api, database, stream
    file_formats JSONB DEFAULT '[]', -- Supported file formats (CSV, JSON, XML, etc.)
    governing_body VARCHAR(255), -- ONS, Ordinance Survey, etc.
    data_standards JSONB DEFAULT '[]', -- SDMX, ISO 20022, etc.
    business_owner VARCHAR(255),
    data_steward VARCHAR(255),
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, inactive, archived
    is_active BOOLEAN DEFAULT true,
    tags JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',

    -- Constraints
    CONSTRAINT valid_source_type CHECK (source_type IN ('file', 'api', 'database', 'stream')),
    CONSTRAINT valid_status CHECK (status IN ('draft', 'active', 'inactive', 'archived'))
);

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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_dataset_structures_status ON design_enhanced.dataset_structures(status);
CREATE INDEX IF NOT EXISTS idx_dataset_structures_source_type ON design_enhanced.dataset_structures(source_type);
CREATE INDEX IF NOT EXISTS idx_dataset_structures_created_by ON design_enhanced.dataset_structures(created_by);

CREATE INDEX IF NOT EXISTS idx_field_definitions_structure ON design_enhanced.field_definitions(structure_id);
CREATE INDEX IF NOT EXISTS idx_field_definitions_type ON design_enhanced.field_definitions(field_type);
CREATE INDEX IF NOT EXISTS idx_field_definitions_postgis ON design_enhanced.field_definitions(postgis_type);

CREATE INDEX IF NOT EXISTS idx_table_templates_type ON design_enhanced.table_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_table_templates_structure ON design_enhanced.table_templates(structure_id);

CREATE INDEX IF NOT EXISTS idx_generated_tables_name ON design_enhanced.generated_tables(table_name);
CREATE INDEX IF NOT EXISTS idx_generated_tables_type ON design_enhanced.generated_tables(table_type);
CREATE INDEX IF NOT EXISTS idx_generated_tables_status ON design_enhanced.generated_tables(status);

CREATE INDEX IF NOT EXISTS idx_field_mappings_structure ON design_enhanced.field_mappings(structure_id);
CREATE INDEX IF NOT EXISTS idx_field_mappings_type ON design_enhanced.field_mappings(mapping_type);

CREATE INDEX IF NOT EXISTS idx_dataset_uploads_structure ON design_enhanced.dataset_uploads(structure_id);
CREATE INDEX IF NOT EXISTS idx_dataset_uploads_status ON design_enhanced.dataset_uploads(processing_status);
CREATE INDEX IF NOT EXISTS idx_dataset_uploads_uploaded_by ON design_enhanced.dataset_uploads(uploaded_by);

CREATE INDEX IF NOT EXISTS idx_review_workflow_upload ON design_enhanced.review_workflow(upload_id);
CREATE INDEX IF NOT EXISTS idx_review_workflow_type ON design_enhanced.review_workflow(review_type);
CREATE INDEX IF NOT EXISTS idx_review_workflow_status ON design_enhanced.review_workflow(review_status);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION design_enhanced.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

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

-- Insert sample dataset structures
INSERT INTO design_enhanced.dataset_structures (
    dataset_name, description, source_type, file_formats, governing_body, 
    data_standards, business_owner, data_steward, created_by, status
) VALUES 
(
    'OS Open Names',
    'Ordnance Survey Open Names dataset for place names and addresses',
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
    'CodePoint Open',
    'Royal Mail CodePoint Open postcode data with coordinates',
    'file',
    '["csv"]'::jsonb,
    'Royal Mail',
    '["CodePoint Standard"]'::jsonb,
    'Address Management Team',
    'Data Quality Team',
    'admin',
    'active'
) ON CONFLICT (dataset_name) DO NOTHING;

-- Insert sample field definitions for OS Open Names
INSERT INTO design_enhanced.field_definitions (
    structure_id, field_name, field_type, postgis_type, srid, is_required, 
    is_primary_key, description, sequence_order, created_by
)
SELECT 
    ds.structure_id,
    'name',
    'text',
    NULL,
    4326,
    true,
    false,
    'Place name',
    1,
    'admin'
FROM design_enhanced.dataset_structures ds WHERE ds.dataset_name = 'OS Open Names'
UNION ALL
SELECT 
    ds.structure_id,
    'local_type',
    'text',
    NULL,
    4326,
    true,
    false,
    'Type of place',
    2,
    'admin'
FROM design_enhanced.dataset_structures ds WHERE ds.dataset_name = 'OS Open Names'
UNION ALL
SELECT 
    ds.structure_id,
    'easting',
    'integer',
    NULL,
    4326,
    true,
    false,
    'OS Grid Easting',
    3,
    'admin'
FROM design_enhanced.dataset_structures ds WHERE ds.dataset_name = 'OS Open Names'
UNION ALL
SELECT 
    ds.structure_id,
    'northing',
    'integer',
    NULL,
    4326,
    true,
    false,
    'OS Grid Northing',
    4,
    'admin'
FROM design_enhanced.dataset_structures ds WHERE ds.dataset_name = 'OS Open Names'
UNION ALL
SELECT 
    ds.structure_id,
    'geometry',
    'geometry',
    'POINT',
    27700,
    false,
    false,
    'Point geometry in OSGB projection',
    5,
    'admin'
FROM design_enhanced.dataset_structures ds WHERE ds.dataset_name = 'OS Open Names'
UNION ALL
SELECT 
    ds.structure_id,
    'latitude',
    'numeric',
    NULL,
    4326,
    false,
    false,
    'Latitude in WGS84',
    6,
    'admin'
FROM design_enhanced.dataset_structures ds WHERE ds.dataset_name = 'OS Open Names'
UNION ALL
SELECT 
    ds.structure_id,
    'longitude',
    'numeric',
    NULL,
    4326,
    false,
    false,
    'Longitude in WGS84',
    7,
    'admin'
FROM design_enhanced.dataset_structures ds WHERE ds.dataset_name = 'OS Open Names'
ON CONFLICT (structure_id, sequence_order) DO NOTHING;

-- Insert sample table templates
INSERT INTO design_enhanced.table_templates (
    template_name, template_type, structure_id, table_name_pattern, 
    schema_name, include_audit_fields, include_source_tracking, 
    include_processing_metadata, postgis_enabled, created_by
)
SELECT 
    'OS Open Names Staging',
    'staging',
    ds.structure_id,
    '{dataset_name}_staging',
    'public',
    true,
    true,
    true,
    true,
    'admin'
FROM design_enhanced.dataset_structures ds WHERE ds.dataset_name = 'OS Open Names'
UNION ALL
SELECT 
    'OS Open Names Master',
    'master',
    ds.structure_id,
    '{dataset_name}',
    'public',
    true,
    false,
    false,
    true,
    'admin'
FROM design_enhanced.dataset_structures ds WHERE ds.dataset_name = 'OS Open Names'
ON CONFLICT (template_name) DO NOTHING;

-- Create views for easier querying
CREATE OR REPLACE VIEW design_enhanced.dataset_structure_overview AS
SELECT 
    ds.structure_id,
    ds.dataset_name,
    ds.description,
    ds.source_type,
    ds.governing_body,
    ds.status as dataset_status,
    COUNT(fd.field_id) as total_fields,
    COUNT(CASE WHEN fd.postgis_type IS NOT NULL THEN 1 END) as postgis_fields,
    COUNT(CASE WHEN fd.is_required = true THEN 1 END) as required_fields,
    COUNT(gt.table_id) as generated_tables,
    ds.created_at,
    ds.updated_at
FROM design_enhanced.dataset_structures ds
LEFT JOIN design_enhanced.field_definitions fd ON ds.structure_id = fd.structure_id
LEFT JOIN design_enhanced.generated_tables gt ON ds.structure_id = gt.structure_id
WHERE ds.is_active = true
GROUP BY ds.structure_id, ds.dataset_name, ds.description, ds.source_type, 
         ds.governing_body, ds.status, ds.created_at, ds.updated_at;

CREATE OR REPLACE VIEW design_enhanced.field_mapping_summary AS
SELECT 
    ds.dataset_name,
    fd.field_name,
    fd.field_type,
    fd.postgis_type,
    fd.srid,
    fd.is_required,
    fd.is_primary_key,
    fd.description,
    fm.mapping_type,
    fm.source_field_name,
    fm.target_field_name
FROM design_enhanced.dataset_structures ds
JOIN design_enhanced.field_definitions fd ON ds.structure_id = fd.structure_id
LEFT JOIN design_enhanced.field_mappings fm ON ds.structure_id = fm.structure_id 
    AND fd.field_name = fm.target_field_name
WHERE ds.is_active = true
ORDER BY ds.dataset_name, fd.sequence_order;

-- Grant permissions (commented out - role may not exist)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA design_enhanced TO authenticated;
-- GRANT SELECT ON design_enhanced.dataset_structure_overview TO authenticated;
-- GRANT SELECT ON design_enhanced.field_mapping_summary TO authenticated;

-- Add comments for documentation
COMMENT ON SCHEMA design_enhanced IS 'Enhanced design system schema for dataset structure capture, field mapping with PostGIS support, and table creation for ingestion';
COMMENT ON TABLE design_enhanced.dataset_structures IS 'Dataset structure definitions with metadata and governance information';
COMMENT ON TABLE design_enhanced.field_definitions IS 'Field definitions with PostGIS support and validation rules';
COMMENT ON TABLE design_enhanced.table_templates IS 'Templates for generating staging and master tables';
COMMENT ON TABLE design_enhanced.generated_tables IS 'Registry of tables generated from templates with DDL scripts';
COMMENT ON TABLE design_enhanced.field_mappings IS 'Field mapping configurations for data transformation';
COMMENT ON TABLE design_enhanced.dataset_uploads IS 'Upload tracking with field mapping and validation results';
COMMENT ON TABLE design_enhanced.review_workflow IS 'Review and verification workflow for dataset approval'; 