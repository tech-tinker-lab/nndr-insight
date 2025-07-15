-- Drop existing tables if they exist to ensure a clean slate
DROP TABLE IF EXISTS design.stage_validations CASCADE;
DROP TABLE IF EXISTS design.upload_processing_logs CASCADE;
DROP TABLE IF EXISTS design.dataset_uploads CASCADE;
DROP TABLE IF EXISTS design.pipeline_stages CASCADE;
DROP TABLE IF EXISTS design.datasets CASCADE;

-- Dataset Pipeline Schema for Design System
-- This schema supports dataset management with pipeline stages and approval workflows

-- Create the design schema
CREATE SCHEMA IF NOT EXISTS design;

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

-- Create pipeline stages table
CREATE TABLE IF NOT EXISTS design.pipeline_stages (
    stage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID NOT NULL REFERENCES design.datasets(dataset_id) ON DELETE CASCADE,
    stage_name VARCHAR(255) NOT NULL,
    stage_type VARCHAR(50) NOT NULL, -- upload, staging, filtered, final, custom
    stage_config JSONB DEFAULT '{}',
    validation_rules JSONB DEFAULT '[]',
    approval_required BOOLEAN DEFAULT false,
    approvers JSONB DEFAULT '[]', -- Array of user IDs who can approve
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active', -- active, inactive
    sequence_order INTEGER NOT NULL,

    -- Constraints
    CONSTRAINT valid_stage_type CHECK (stage_type IN ('upload', 'staging', 'filtered', 'final', 'custom')),
    CONSTRAINT valid_stage_status CHECK (status IN ('active', 'inactive')),
    CONSTRAINT unique_stage_sequence UNIQUE (dataset_id, sequence_order)
);

-- Create dataset uploads table
CREATE TABLE IF NOT EXISTS design.dataset_uploads (
    upload_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID NOT NULL REFERENCES design.datasets(dataset_id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(100),
    file_path VARCHAR(500),
    metadata JSONB DEFAULT '{}',
    uploaded_by VARCHAR(100) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'uploaded', -- uploaded, processing, approved, rejected, completed
    current_stage VARCHAR(50) DEFAULT 'upload',
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    approval_notes TEXT,
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    error_message TEXT,

    -- Constraints
    CONSTRAINT valid_upload_status CHECK (status IN ('uploaded', 'processing', 'approved', 'rejected', 'completed')),
    CONSTRAINT valid_current_stage CHECK (current_stage IN ('upload', 'staging', 'filtered', 'final'))
);

-- Create upload processing logs table
CREATE TABLE IF NOT EXISTS design.upload_processing_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upload_id UUID NOT NULL REFERENCES design.dataset_uploads(upload_id) ON DELETE CASCADE,
    stage_name VARCHAR(255) NOT NULL,
    stage_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL, -- started, completed, failed, skipped
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    records_processed INTEGER DEFAULT 0,
    records_valid INTEGER DEFAULT 0,
    records_invalid INTEGER DEFAULT 0,
    validation_errors JSONB DEFAULT '[]',
    processing_notes TEXT,

    -- Constraints
    CONSTRAINT valid_processing_status CHECK (status IN ('started', 'completed', 'failed', 'skipped'))
);

-- Create stage validations table
CREATE TABLE IF NOT EXISTS design.stage_validations (
    validation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upload_id UUID NOT NULL REFERENCES design.dataset_uploads(upload_id) ON DELETE CASCADE,
    stage_id UUID NOT NULL REFERENCES design.pipeline_stages(stage_id) ON DELETE CASCADE,
    validation_rule_name VARCHAR(255) NOT NULL,
    validation_type VARCHAR(100) NOT NULL, -- schema, business_rule, data_quality, custom
    validation_config JSONB DEFAULT '{}',
    status VARCHAR(50) NOT NULL, -- passed, failed, warning
    error_message TEXT,
    affected_records INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_validation_type CHECK (validation_type IN ('schema', 'business_rule', 'data_quality', 'custom')),
    CONSTRAINT valid_validation_status CHECK (status IN ('passed', 'failed', 'warning'))
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_datasets_status ON design.datasets(status);
CREATE INDEX IF NOT EXISTS idx_datasets_created_by ON design.datasets(created_by);
CREATE INDEX IF NOT EXISTS idx_datasets_business_owner ON design.datasets(business_owner);

CREATE INDEX IF NOT EXISTS idx_pipeline_stages_dataset_id ON design.pipeline_stages(dataset_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_stages_stage_type ON design.pipeline_stages(stage_type);
CREATE INDEX IF NOT EXISTS idx_pipeline_stages_sequence ON design.pipeline_stages(dataset_id, sequence_order);

CREATE INDEX IF NOT EXISTS idx_dataset_uploads_dataset_id ON design.dataset_uploads(dataset_id);
CREATE INDEX IF NOT EXISTS idx_dataset_uploads_status ON design.dataset_uploads(status);
CREATE INDEX IF NOT EXISTS idx_dataset_uploads_current_stage ON design.dataset_uploads(current_stage);
CREATE INDEX IF NOT EXISTS idx_dataset_uploads_uploaded_by ON design.dataset_uploads(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_dataset_uploads_uploaded_at ON design.dataset_uploads(uploaded_at);

CREATE INDEX IF NOT EXISTS idx_upload_processing_logs_upload_id ON design.upload_processing_logs(upload_id);
CREATE INDEX IF NOT EXISTS idx_upload_processing_logs_stage_type ON design.upload_processing_logs(stage_type);
CREATE INDEX IF NOT EXISTS idx_upload_processing_logs_status ON design.upload_processing_logs(status);

CREATE INDEX IF NOT EXISTS idx_stage_validations_upload_id ON design.stage_validations(upload_id);
CREATE INDEX IF NOT EXISTS idx_stage_validations_stage_id ON design.stage_validations(stage_id);
CREATE INDEX IF NOT EXISTS idx_stage_validations_status ON design.stage_validations(status);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_datasets_updated_at
    BEFORE UPDATE ON design.datasets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pipeline_stages_updated_at
    BEFORE UPDATE ON design.pipeline_stages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column(); 