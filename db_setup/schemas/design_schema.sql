-- Design Schema - Unified Schema File
-- This file drops and recreates the design schema with all its objects
-- Combines design/01_create_design_schema.sql and design/02_create_dataset_pipeline_schema.sql

-- Drop existing schema if it exists (for clean recreation)
DROP SCHEMA IF EXISTS design CASCADE;

-- Create design schema
CREATE SCHEMA design;

-- =============================================================================
-- TABLE DESIGNS
-- =============================================================================

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

-- =============================================================================
-- MAPPING CONFIGURATIONS
-- =============================================================================

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

-- =============================================================================
-- AUDIT LOGS
-- =============================================================================

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

-- =============================================================================
-- DATASETS
-- =============================================================================

-- Create datasets table
CREATE TABLE IF NOT EXISTS design.datasets (
    dataset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    source_type VARCHAR(50) DEFAULT 'file', -- file, api, database
    pipeline_config JSONB DEFAULT '{}',
    business_owner VARCHAR(255),
    data_steward VARCHAR(255),
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, inactive, archived
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    
    -- Constraints
    CONSTRAINT valid_source_type CHECK (source_type IN ('file', 'api', 'database')),
    CONSTRAINT valid_status CHECK (status IN ('draft', 'active', 'inactive', 'archived'))
);

-- =============================================================================
-- PIPELINE STAGES
-- =============================================================================

-- Create pipeline stages table
CREATE TABLE IF NOT EXISTS design.pipeline_stages (
    stage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID NOT NULL REFERENCES design.datasets(dataset_id) ON DELETE CASCADE,
    stage_name VARCHAR(255) NOT NULL,
    stage_order INTEGER NOT NULL,
    stage_type VARCHAR(100) NOT NULL, -- validation, transformation, enrichment, etc.
    stage_config JSONB DEFAULT '{}',
    is_required BOOLEAN DEFAULT true,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_stage_type CHECK (stage_type IN ('validation', 'transformation', 'enrichment', 'approval', 'notification')),
    CONSTRAINT unique_stage_order UNIQUE (dataset_id, stage_order)
);

-- =============================================================================
-- APPROVAL WORKFLOWS
-- =============================================================================

-- Create approval workflows table
CREATE TABLE IF NOT EXISTS design.approval_workflows (
    workflow_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID NOT NULL REFERENCES design.datasets(dataset_id) ON DELETE CASCADE,
    workflow_name VARCHAR(255) NOT NULL,
    workflow_type VARCHAR(100) NOT NULL, -- single_approver, multi_approver, conditional
    approvers JSONB NOT NULL, -- Array of approver configurations
    conditions JSONB DEFAULT '[]', -- Array of approval conditions
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    
    -- Constraints
    CONSTRAINT valid_workflow_type CHECK (workflow_type IN ('single_approver', 'multi_approver', 'conditional'))
);

-- =============================================================================
-- APPROVAL REQUESTS
-- =============================================================================

-- Create approval requests table
CREATE TABLE IF NOT EXISTS design.approval_requests (
    request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES design.approval_workflows(workflow_id) ON DELETE CASCADE,
    dataset_id UUID NOT NULL REFERENCES design.datasets(dataset_id) ON DELETE CASCADE,
    requester_id VARCHAR(100) NOT NULL,
    request_data JSONB NOT NULL, -- Data being approved
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected, cancelled
    current_approver VARCHAR(100),
    approval_chain JSONB DEFAULT '[]', -- Array of approval decisions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled'))
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Table designs indexes
CREATE INDEX IF NOT EXISTS idx_table_designs_type ON design.table_designs(table_type);
CREATE INDEX IF NOT EXISTS idx_table_designs_category ON design.table_designs(category);
CREATE INDEX IF NOT EXISTS idx_table_designs_active ON design.table_designs(is_active);
CREATE INDEX IF NOT EXISTS idx_table_designs_created_at ON design.table_designs(created_at);

-- Mapping configs indexes
CREATE INDEX IF NOT EXISTS idx_mapping_configs_design_id ON design.mapping_configs(design_id);
CREATE INDEX IF NOT EXISTS idx_mapping_configs_priority ON design.mapping_configs(priority);
CREATE INDEX IF NOT EXISTS idx_mapping_configs_active ON design.mapping_configs(is_active);

-- Audit logs indexes
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON design.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON design.audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON design.audit_logs(resource_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_id ON design.audit_logs(resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON design.audit_logs(timestamp);

-- Datasets indexes
CREATE INDEX IF NOT EXISTS idx_datasets_source_type ON design.datasets(source_type);
CREATE INDEX IF NOT EXISTS idx_datasets_status ON design.datasets(status);
CREATE INDEX IF NOT EXISTS idx_datasets_active ON design.datasets(is_active);
CREATE INDEX IF NOT EXISTS idx_datasets_created_at ON design.datasets(created_at);

-- Pipeline stages indexes
CREATE INDEX IF NOT EXISTS idx_pipeline_stages_dataset_id ON design.pipeline_stages(dataset_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_stages_type ON design.pipeline_stages(stage_type);
CREATE INDEX IF NOT EXISTS idx_pipeline_stages_order ON design.pipeline_stages(stage_order);

-- Approval workflows indexes
CREATE INDEX IF NOT EXISTS idx_approval_workflows_dataset_id ON design.approval_workflows(dataset_id);
CREATE INDEX IF NOT EXISTS idx_approval_workflows_type ON design.approval_workflows(workflow_type);
CREATE INDEX IF NOT EXISTS idx_approval_workflows_active ON design.approval_workflows(is_active);

-- Approval requests indexes
CREATE INDEX IF NOT EXISTS idx_approval_requests_workflow_id ON design.approval_requests(workflow_id);
CREATE INDEX IF NOT EXISTS idx_approval_requests_dataset_id ON design.approval_requests(dataset_id);
CREATE INDEX IF NOT EXISTS idx_approval_requests_status ON design.approval_requests(status);
CREATE INDEX IF NOT EXISTS idx_approval_requests_requester_id ON design.approval_requests(requester_id);
CREATE INDEX IF NOT EXISTS idx_approval_requests_created_at ON design.approval_requests(created_at);

-- =============================================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION design.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER update_table_designs_updated_at 
    BEFORE UPDATE ON design.table_designs 
    FOR EACH ROW EXECUTE FUNCTION design.update_updated_at_column();

CREATE TRIGGER update_mapping_configs_updated_at 
    BEFORE UPDATE ON design.mapping_configs 
    FOR EACH ROW EXECUTE FUNCTION design.update_updated_at_column();

CREATE TRIGGER update_datasets_updated_at 
    BEFORE UPDATE ON design.datasets 
    FOR EACH ROW EXECUTE FUNCTION design.update_updated_at_column();

CREATE TRIGGER update_pipeline_stages_updated_at 
    BEFORE UPDATE ON design.pipeline_stages 
    FOR EACH ROW EXECUTE FUNCTION design.update_updated_at_column();

CREATE TRIGGER update_approval_workflows_updated_at 
    BEFORE UPDATE ON design.approval_workflows 
    FOR EACH ROW EXECUTE FUNCTION design.update_updated_at_column();

CREATE TRIGGER update_approval_requests_updated_at 
    BEFORE UPDATE ON design.approval_requests 
    FOR EACH ROW EXECUTE FUNCTION design.update_updated_at_column();

-- =============================================================================
-- SAMPLE DATA
-- =============================================================================

-- Sample data for common table types
INSERT INTO design.table_designs (
    design_id, design_name, table_name, description, columns, table_type, category, created_by
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
    'government',
    'system'
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
    'business',
    'system'
),
-- Postcode data
(
    gen_random_uuid(),
    'ONS Postcode Directory Design',
    'onspd_staging',
    'Design for ONS Postcode Directory data',
    '[
        {"name": "pcd", "type": "text", "description": "Postcode", "is_required": true},
        {"name": "pcd2", "type": "text", "description": "Postcode with spaces", "is_required": false},
        {"name": "oseast1m", "type": "integer", "description": "OS Easting", "is_required": false},
        {"name": "osnrth1m", "type": "integer", "description": "OS Northing", "is_required": false},
        {"name": "laua", "type": "text", "description": "Local Authority District", "is_required": false},
        {"name": "ward", "type": "text", "description": "Electoral Ward", "is_required": false},
        {"name": "ctry", "type": "text", "description": "Country", "is_required": false},
        {"name": "rgn", "type": "text", "description": "Region", "is_required": false}
    ]'::jsonb,
    'postcode',
    'government',
    'system'
)
ON CONFLICT (design_name) DO NOTHING;

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON SCHEMA design IS 'Design system for managing table designs and mapping configurations';
COMMENT ON TABLE design.table_designs IS 'Table designs defining structure for staging tables';
COMMENT ON TABLE design.mapping_configs IS 'Mapping configurations for matching files to table designs';
COMMENT ON TABLE design.audit_logs IS 'Audit trail for all design system activities';
COMMENT ON TABLE design.datasets IS 'Dataset definitions for pipeline management';
COMMENT ON TABLE design.pipeline_stages IS 'Pipeline stages for dataset processing workflows';
COMMENT ON TABLE design.approval_workflows IS 'Approval workflow definitions for datasets';
COMMENT ON TABLE design.approval_requests IS 'Approval requests and their status tracking'; 