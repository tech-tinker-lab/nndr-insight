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

-- Insert sample data for testing
INSERT INTO design.datasets (
    dataset_name, description, source_type, business_owner, data_steward, created_by, status
) VALUES 
(
    'NNDR Ratepayers',
    'National Non-Domestic Rates ratepayer data',
    'file',
    'Business Rates Team',
    'Data Management Team',
    'admin',
    'active'
),
(
    'Property Boundaries',
    'Property boundary and address data',
    'file',
    'Property Team',
    'GIS Team',
    'admin',
    'active'
),
(
    'Business Classifications',
    'Business classification and SIC codes',
    'api',
    'Business Intelligence Team',
    'Data Quality Team',
    'admin',
    'draft'
) ON CONFLICT (dataset_name) DO NOTHING;

-- Insert sample pipeline stages
INSERT INTO design.pipeline_stages (
    dataset_id, stage_name, stage_type, approval_required, approvers, created_by, sequence_order
) 
SELECT 
    d.dataset_id,
    'File Upload',
    'upload',
    false,
    '[]',
    'admin',
    1
FROM design.datasets d WHERE d.dataset_name = 'NNDR Ratepayers'
UNION ALL
SELECT 
    d.dataset_id,
    'Staging Validation',
    'staging',
    true,
    '["admin", "power_user"]',
    'admin',
    2
FROM design.datasets d WHERE d.dataset_name = 'NNDR Ratepayers'
UNION ALL
SELECT 
    d.dataset_id,
    'Business Rules Check',
    'filtered',
    true,
    '["admin"]',
    'admin',
    3
FROM design.datasets d WHERE d.dataset_name = 'NNDR Ratepayers'
UNION ALL
SELECT 
    d.dataset_id,
    'Production Ready',
    'final',
    true,
    '["admin"]',
    'admin',
    4
FROM design.datasets d WHERE d.dataset_name = 'NNDR Ratepayers'
ON CONFLICT (dataset_id, sequence_order) DO NOTHING;

-- Create views for easier querying
CREATE OR REPLACE VIEW design.dataset_pipeline_summary AS
SELECT 
    d.dataset_id,
    d.dataset_name,
    d.description,
    d.business_owner,
    d.data_steward,
    d.status as dataset_status,
    COUNT(ps.stage_id) as total_stages,
    COUNT(du.upload_id) as total_uploads,
    COUNT(CASE WHEN du.status = 'completed' THEN 1 END) as completed_uploads,
    COUNT(CASE WHEN du.status = 'processing' THEN 1 END) as processing_uploads,
    COUNT(CASE WHEN du.status = 'uploaded' THEN 1 END) as pending_uploads,
    d.created_at,
    d.updated_at
FROM design.datasets d
LEFT JOIN design.pipeline_stages ps ON d.dataset_id = ps.dataset_id AND ps.status = 'active'
LEFT JOIN design.dataset_uploads du ON d.dataset_id = du.dataset_id
WHERE d.is_active = true
GROUP BY d.dataset_id, d.dataset_name, d.description, d.business_owner, d.data_steward, 
         d.status, d.created_at, d.updated_at;

CREATE OR REPLACE VIEW design.upload_pipeline_status AS
SELECT 
    du.upload_id,
    du.dataset_id,
    d.dataset_name,
    du.file_name,
    du.status as upload_status,
    du.current_stage,
    du.uploaded_by,
    du.uploaded_at,
    du.approved_by,
    du.approved_at,
    ps.stage_name,
    ps.approval_required,
    ps.approvers,
    CASE 
        WHEN du.status = 'completed' THEN 'Completed'
        WHEN du.status = 'processing' THEN 'Processing'
        WHEN du.status = 'approved' THEN 'Approved'
        WHEN du.status = 'rejected' THEN 'Rejected'
        WHEN du.status = 'uploaded' THEN 'Pending Approval'
        ELSE 'Unknown'
    END as status_display
FROM design.dataset_uploads du
JOIN design.datasets d ON du.dataset_id = d.dataset_id
LEFT JOIN design.pipeline_stages ps ON du.dataset_id = ps.dataset_id AND du.current_stage = ps.stage_type
WHERE d.is_active = true
ORDER BY du.uploaded_at DESC;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA design TO authenticated;
GRANT SELECT ON design.dataset_pipeline_summary TO authenticated;
GRANT SELECT ON design.upload_pipeline_status TO authenticated; 