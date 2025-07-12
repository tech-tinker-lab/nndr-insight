-- Create Design System Schema
-- This schema manages table designs, mapping configurations, and audit logging

-- Create design schema
CREATE SCHEMA IF NOT EXISTS design;

-- Table Designs
CREATE TABLE IF NOT EXISTS design.table_designs (
    design_id UUID PRIMARY KEY,
    design_name VARCHAR(255) NOT NULL,
    table_name VARCHAR(255) NOT NULL,
    description TEXT,
    columns JSONB NOT NULL, -- Array of column definitions
    table_type VARCHAR(100) NOT NULL DEFAULT 'custom', -- custom, address, property, boundary, etc.
    category VARCHAR(100) NOT NULL DEFAULT 'general', -- general, business, government, etc.
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_by VARCHAR(255),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT unique_design_name UNIQUE (design_name),
    CONSTRAINT unique_table_name UNIQUE (table_name)
);

-- Mapping Configurations
CREATE TABLE IF NOT EXISTS design.mapping_configs (
    config_id UUID PRIMARY KEY,
    config_name VARCHAR(255) NOT NULL,
    design_id UUID NOT NULL REFERENCES design.table_designs(design_id) ON DELETE CASCADE,
    source_patterns JSONB NOT NULL, -- Array of file patterns to match
    mapping_rules JSONB NOT NULL, -- Array of mapping rules
    priority INTEGER NOT NULL DEFAULT 1, -- Higher priority = higher precedence
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_by VARCHAR(255),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT unique_config_name UNIQUE (config_name)
);

-- Audit Logs
CREATE TABLE IF NOT EXISTS design.audit_logs (
    audit_id UUID PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL, -- CREATE, UPDATE, DELETE, MATCH, VIEW, etc.
    resource_type VARCHAR(100) NOT NULL, -- table_design, mapping_config, file_analysis, etc.
    resource_id VARCHAR(255) NOT NULL,
    details JSONB, -- Additional context about the action
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_table_designs_type ON design.table_designs(table_type);
CREATE INDEX IF NOT EXISTS idx_table_designs_category ON design.table_designs(category);
CREATE INDEX IF NOT EXISTS idx_table_designs_active ON design.table_designs(is_active);
CREATE INDEX IF NOT EXISTS idx_table_designs_created_at ON design.table_designs(created_at);

CREATE INDEX IF NOT EXISTS idx_mapping_configs_design_id ON design.mapping_configs(design_id);
CREATE INDEX IF NOT EXISTS idx_mapping_configs_priority ON design.mapping_configs(priority);
CREATE INDEX IF NOT EXISTS idx_mapping_configs_active ON design.mapping_configs(is_active);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON design.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON design.audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON design.audit_logs(resource_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_id ON design.audit_logs(resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON design.audit_logs(timestamp);

-- Sample data for common table types
INSERT INTO design.table_designs (
    design_id, design_name, table_name, description, columns, table_type, category
) VALUES 
-- Address data
(
    gen_random_uuid(),
    'OS Open Names Design',
    'os_open_names_staging',
    'Design for OS Open Names address data',
    '[
        {"name": "name", "type": "text", "description": "Place name", "is_required": true},
        {"name": "local_type", "type": "text", "description": "Type of place", "is_required": true},
        {"name": "easting", "type": "integer", "description": "OS Grid Easting", "is_required": true},
        {"name": "northing", "type": "integer", "description": "OS Grid Northing", "is_required": true},
        {"name": "latitude", "type": "numeric", "description": "Latitude", "is_required": false},
        {"name": "longitude", "type": "numeric", "description": "Longitude", "is_required": false},
        {"name": "district", "type": "text", "description": "District name", "is_required": false},
        {"name": "county", "type": "text", "description": "County name", "is_required": false}
    ]'::jsonb,
    'address',
    'government'
),
-- Property data
(
    gen_random_uuid(),
    'NNDR Properties Design',
    'nndr_properties_staging',
    'Design for NNDR property data',
    '[
        {"name": "uprn", "type": "text", "description": "Unique Property Reference Number", "is_required": true},
        {"name": "property_address", "type": "text", "description": "Property address", "is_required": true},
        {"name": "rateable_value", "type": "numeric", "description": "Rateable value", "is_required": false},
        {"name": "property_type", "type": "text", "description": "Type of property", "is_required": false},
        {"name": "occupancy_status", "type": "text", "description": "Occupancy status", "is_required": false},
        {"name": "local_authority", "type": "text", "description": "Local authority", "is_required": false}
    ]'::jsonb,
    'property',
    'business'
),
-- Postcode data
(
    gen_random_uuid(),
    'CodePoint Open Design',
    'codepoint_open_staging',
    'Design for CodePoint Open postcode data',
    '[
        {"name": "postcode", "type": "text", "description": "Postcode", "is_required": true},
        {"name": "easting", "type": "integer", "description": "OS Grid Easting", "is_required": true},
        {"name": "northing", "type": "integer", "description": "OS Grid Northing", "is_required": true},
        {"name": "latitude", "type": "numeric", "description": "Latitude", "is_required": false},
        {"name": "longitude", "type": "numeric", "description": "Longitude", "is_required": false},
        {"name": "district", "type": "text", "description": "District name", "is_required": false},
        {"name": "county", "type": "text", "description": "County name", "is_required": false}
    ]'::jsonb,
    'postcode',
    'government'
)
ON CONFLICT (table_name) DO NOTHING;

-- Sample mapping configurations
INSERT INTO design.mapping_configs (
    config_id, config_name, design_id, source_patterns, mapping_rules, priority
) 
SELECT 
    gen_random_uuid(),
    'OS Open Names CSV Mapping',
    td.design_id,
    '["osopennames", "names", "places"]'::jsonb,
    '[
        {"source_column": "name", "target_column": "name", "mapping_type": "direct"},
        {"source_column": "local_type", "target_column": "local_type", "mapping_type": "direct"},
        {"source_column": "easting", "target_column": "easting", "mapping_type": "direct"},
        {"source_column": "northing", "target_column": "northing", "mapping_type": "direct"},
        {"source_column": "latitude", "target_column": "latitude", "mapping_type": "direct"},
        {"source_column": "longitude", "target_column": "longitude", "mapping_type": "direct"}
    ]'::jsonb,
    10
FROM design.table_designs td 
WHERE td.table_name = 'os_open_names_staging'
ON CONFLICT (config_name) DO NOTHING;

-- Comments
COMMENT ON SCHEMA design IS 'Design system for managing table designs and mapping configurations';
COMMENT ON TABLE design.table_designs IS 'Table designs defining structure for staging tables';
COMMENT ON TABLE design.mapping_configs IS 'Mapping configurations for matching files to table designs';
COMMENT ON TABLE design.audit_logs IS 'Audit trail for all design system activities'; 