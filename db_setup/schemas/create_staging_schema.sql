-- Create dedicated staging schema for upload system
-- This schema will contain all tables created by the upload functionality

-- Create the staging schema
CREATE SCHEMA IF NOT EXISTS staging;

-- Set search path to include staging schema
SET search_path TO staging, public;

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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_staging_configs_name ON staging.staging_configs(config_name);
CREATE INDEX IF NOT EXISTS idx_staging_configs_table ON staging.staging_configs(table_name);
CREATE INDEX IF NOT EXISTS idx_upload_metadata_upload_id ON staging.upload_metadata(upload_id);
CREATE INDEX IF NOT EXISTS idx_upload_metadata_timestamp ON staging.upload_metadata(upload_timestamp);
CREATE INDEX IF NOT EXISTS idx_upload_metadata_status ON staging.upload_metadata(status);
CREATE INDEX IF NOT EXISTS idx_staging_audit_timestamp ON staging.staging_audit_log(operation_timestamp);
CREATE INDEX IF NOT EXISTS idx_staging_audit_table ON staging.staging_audit_log(table_name);

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

-- Create function to log staging operations
CREATE OR REPLACE FUNCTION staging.log_staging_operation(
    p_operation_type VARCHAR(50),
    p_table_name VARCHAR(255),
    p_performed_by VARCHAR(100),
    p_operation_details JSONB DEFAULT NULL,
    p_affected_rows INTEGER DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO staging.staging_audit_log (
        operation_type,
        table_name,
        performed_by,
        operation_details,
        affected_rows
    ) VALUES (
        p_operation_type,
        p_table_name,
        p_performed_by,
        p_operation_details,
        p_affected_rows
    );
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions
-- Note: Adjust these permissions based on your security requirements
GRANT USAGE ON SCHEMA staging TO PUBLIC;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA staging TO PUBLIC;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA staging TO PUBLIC;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA staging TO PUBLIC;

-- Grant permissions for future tables (for dynamic table creation)
ALTER DEFAULT PRIVILEGES IN SCHEMA staging GRANT ALL ON TABLES TO PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA staging GRANT ALL ON SEQUENCES TO PUBLIC;

-- Insert some sample configurations for common file types
INSERT INTO staging.staging_configs (config_name, table_name, column_mappings, file_type, delimiter, has_header, description) VALUES
(
    'CSV Generic',
    'csv_upload',
    '{"columns": [{"name": "column1", "type": "TEXT"}, {"name": "column2", "type": "TEXT"}]}',
    'csv',
    ',',
    true,
    'Generic CSV configuration for basic uploads'
),
(
    'Excel Generic',
    'excel_upload',
    '{"columns": [{"name": "column1", "type": "TEXT"}, {"name": "column2", "type": "TEXT"}]}',
    'excel',
    NULL,
    true,
    'Generic Excel configuration for basic uploads'
),
(
    'Fixed Width Text',
    'fixed_width_upload',
    '{"columns": [{"name": "field1", "type": "TEXT", "start": 1, "length": 10}, {"name": "field2", "type": "TEXT", "start": 11, "length": 15}]}',
    'fixed_width',
    NULL,
    false,
    'Generic fixed-width text configuration'
)
ON CONFLICT (config_name) DO NOTHING;

-- Create a view for easy access to upload statistics
CREATE OR REPLACE VIEW staging.upload_statistics AS
SELECT 
    DATE_TRUNC('day', upload_timestamp) as upload_date,
    COUNT(*) as total_uploads,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_uploads,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_uploads,
    AVG(processing_time_ms) as avg_processing_time_ms,
    SUM(row_count) as total_rows_processed
FROM staging.upload_metadata
GROUP BY DATE_TRUNC('day', upload_timestamp)
ORDER BY upload_date DESC;

-- Create a view for recent staging operations
CREATE OR REPLACE VIEW staging.recent_operations AS
SELECT 
    operation_type,
    table_name,
    performed_by,
    operation_timestamp,
    affected_rows,
    operation_details
FROM staging.staging_audit_log
ORDER BY operation_timestamp DESC
LIMIT 100;

-- Add comments for documentation
COMMENT ON SCHEMA staging IS 'Dedicated schema for staging tables created by the upload system';
COMMENT ON TABLE staging.staging_configs IS 'Stores configurations for different file types and table structures';
COMMENT ON TABLE staging.upload_metadata IS 'Tracks metadata for all file uploads and their processing status';
COMMENT ON TABLE staging.staging_audit_log IS 'Audit trail for all staging operations including table creation, data loading, etc.';

-- Reset search path
SET search_path TO public; 