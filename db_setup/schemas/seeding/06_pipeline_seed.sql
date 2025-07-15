-- Pipeline Sample Data and Views Seeding Script

-- Insert sample data for testing
tRUNCATE TABLE design.pipeline_stages CASCADE;
TRUNCATE TABLE design.datasets CASCADE;

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
    '[]'::jsonb,
    'admin',
    1
FROM design.datasets d WHERE d.dataset_name = 'NNDR Ratepayers'
UNION ALL
SELECT
    d.dataset_id,
    'Staging Validation',
    'staging',
    true,
    '["admin", "power_user"]'::jsonb,
    'admin',
    2
FROM design.datasets d WHERE d.dataset_name = 'NNDR Ratepayers'
UNION ALL
SELECT
    d.dataset_id,
    'Business Rules Check',
    'filtered',
    true,
    '["admin"]'::jsonb,
    'admin',
    3
FROM design.datasets d WHERE d.dataset_name = 'NNDR Ratepayers'
UNION ALL
SELECT
    d.dataset_id,
    'Production Ready',
    'final',
    true,
    '["admin"]'::jsonb,
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