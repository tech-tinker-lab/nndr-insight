-- Staging Configuration Management Schema
-- This schema stores comprehensive mapping configurations for data ingestion

-- Enable UUID extension for unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. STAGING CONFIGURATIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS staging_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    file_pattern VARCHAR(255), -- Pattern to match files (e.g., "*.csv", "nndr-*.csv")
    file_type VARCHAR(50) NOT NULL, -- csv, json, xml, gml, zip, etc.
    staging_table_name VARCHAR(255) NOT NULL,
    source_schema VARCHAR(100) DEFAULT 'public',
    target_schema VARCHAR(100) DEFAULT 'staging',
    
    -- Configuration metadata
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Status and versioning
    is_active BOOLEAN DEFAULT true,
    version INTEGER DEFAULT 1,
    parent_config_id UUID REFERENCES staging_configs(id), -- For versioning
    
    -- Processing options
    skip_header_rows INTEGER DEFAULT 1,
    delimiter VARCHAR(10) DEFAULT ',',
    quote_char VARCHAR(5) DEFAULT '"',
    encoding VARCHAR(20) DEFAULT 'UTF-8',
    
    -- Validation and constraints
    max_errors INTEGER DEFAULT 100,
    validate_data BOOLEAN DEFAULT true,
    
    -- JSON configuration for complex settings
    settings JSONB DEFAULT '{}',
    
    -- Constraints
    CONSTRAINT staging_configs_name_unique UNIQUE (name),
    CONSTRAINT staging_configs_table_name_unique UNIQUE (staging_table_name)
);

-- =====================================================
-- 2. COLUMN MAPPINGS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS column_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_id UUID NOT NULL REFERENCES staging_configs(id) ON DELETE CASCADE,
    
    -- Source column information
    source_column_name VARCHAR(255) NOT NULL,
    source_column_index INTEGER, -- Position in source file
    source_column_type VARCHAR(50), -- text, number, date, etc.
    
    -- Target column information
    target_column_name VARCHAR(255) NOT NULL,
    target_column_type VARCHAR(50) NOT NULL, -- text, integer, decimal, date, timestamp, boolean
    target_column_length INTEGER, -- For varchar/text fields
    target_column_precision INTEGER, -- For decimal fields
    target_column_scale INTEGER, -- For decimal fields
    
    -- Mapping configuration
    mapping_type VARCHAR(50) NOT NULL DEFAULT 'direct', -- direct, merge, default, transform, conditional
    is_required BOOLEAN DEFAULT false,
    is_primary_key BOOLEAN DEFAULT false,
    is_unique BOOLEAN DEFAULT false,
    
    -- Default values and transformations
    default_value TEXT,
    transformation_config JSONB DEFAULT '{}', -- Store transformation parameters
    
    -- Merge configuration (for merge type mappings)
    merge_columns TEXT[], -- Array of column names to merge
    merge_separator VARCHAR(10) DEFAULT ' ', -- Separator for merged values
    
    -- Conditional mapping
    condition_expression TEXT, -- SQL-like condition for conditional mapping
    
    -- Order and display
    display_order INTEGER DEFAULT 0,
    is_visible BOOLEAN DEFAULT true,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT column_mappings_config_target_unique UNIQUE (config_id, target_column_name)
);

-- =====================================================
-- 3. TRANSFORMATION FUNCTIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS transformation_functions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Function definition
    function_type VARCHAR(50) NOT NULL, -- builtin, custom, sql
    function_code TEXT, -- For custom functions
    sql_template TEXT, -- For SQL transformations
    
    -- Parameters
    parameters JSONB DEFAULT '[]', -- Array of parameter definitions
    
    -- Metadata
    category VARCHAR(100), -- text, number, date, validation, etc.
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT transformation_functions_name_unique UNIQUE (name)
);

-- =====================================================
-- 4. DATA VALIDATION RULES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS validation_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_id UUID NOT NULL REFERENCES staging_configs(id) ON DELETE CASCADE,
    column_mapping_id UUID REFERENCES column_mappings(id) ON DELETE CASCADE,
    
    -- Rule definition
    rule_name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(50) NOT NULL, -- regex, range, length, custom, etc.
    rule_expression TEXT NOT NULL, -- The actual validation rule
    
    -- Error handling
    error_message TEXT,
    error_severity VARCHAR(20) DEFAULT 'error', -- error, warning, info
    action_on_violation VARCHAR(20) DEFAULT 'reject', -- reject, log, transform
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT validation_rules_config_column_unique UNIQUE (config_id, column_mapping_id, rule_name)
);

-- =====================================================
-- 5. CONFIGURATION TEMPLATES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS config_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(100), -- business_rates, addresses, boundaries, etc.
    
    -- Template configuration
    template_config JSONB NOT NULL, -- Complete configuration as JSON
    file_type VARCHAR(50) NOT NULL,
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_public BOOLEAN DEFAULT false, -- Can be used by other users
    
    -- Constraints
    CONSTRAINT config_templates_name_unique UNIQUE (name)
);

-- =====================================================
-- 6. CONFIGURATION EXECUTION LOGS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS config_execution_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_id UUID NOT NULL REFERENCES staging_configs(id),
    
    -- Execution details
    execution_id VARCHAR(100) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT,
    file_hash VARCHAR(64), -- For duplicate detection
    
    -- Status and progress
    status VARCHAR(50) NOT NULL, -- pending, running, completed, failed, cancelled
    progress_percentage INTEGER DEFAULT 0,
    rows_processed INTEGER DEFAULT 0,
    rows_successful INTEGER DEFAULT 0,
    rows_failed INTEGER DEFAULT 0,
    
    -- Error information
    error_message TEXT,
    error_details JSONB,
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    
    -- Metadata
    executed_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 7. ZIP FILE CONFIGURATIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS zip_file_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_id UUID NOT NULL REFERENCES staging_configs(id) ON DELETE CASCADE,
    
    -- ZIP file structure
    zip_file_pattern VARCHAR(255), -- Pattern to match files within ZIP
    header_file_pattern VARCHAR(255), -- Pattern for header files
    data_file_pattern VARCHAR(255), -- Pattern for data files
    
    -- File relationships
    header_file_name VARCHAR(255),
    data_file_name VARCHAR(255),
    header_delimiter VARCHAR(10) DEFAULT ',',
    data_delimiter VARCHAR(10) DEFAULT ',',
    
    -- Processing options
    skip_header_in_data BOOLEAN DEFAULT true,
    merge_strategy VARCHAR(50) DEFAULT 'append', -- append, replace, merge
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Staging configs indexes
CREATE INDEX IF NOT EXISTS idx_staging_configs_file_type ON staging_configs(file_type);
CREATE INDEX IF NOT EXISTS idx_staging_configs_created_by ON staging_configs(created_by);
CREATE INDEX IF NOT EXISTS idx_staging_configs_is_active ON staging_configs(is_active);
CREATE INDEX IF NOT EXISTS idx_staging_configs_created_at ON staging_configs(created_at);

-- Column mappings indexes
CREATE INDEX IF NOT EXISTS idx_column_mappings_config_id ON column_mappings(config_id);
CREATE INDEX IF NOT EXISTS idx_column_mappings_source_column ON column_mappings(source_column_name);
CREATE INDEX IF NOT EXISTS idx_column_mappings_target_column ON column_mappings(target_column_name);
CREATE INDEX IF NOT EXISTS idx_column_mappings_mapping_type ON column_mappings(mapping_type);

-- Validation rules indexes
CREATE INDEX IF NOT EXISTS idx_validation_rules_config_id ON validation_rules(config_id);
CREATE INDEX IF NOT EXISTS idx_validation_rules_column_mapping_id ON validation_rules(column_mapping_id);

-- Execution logs indexes
CREATE INDEX IF NOT EXISTS idx_execution_logs_config_id ON config_execution_logs(config_id);
CREATE INDEX IF NOT EXISTS idx_execution_logs_status ON config_execution_logs(status);
CREATE INDEX IF NOT EXISTS idx_execution_logs_executed_by ON config_execution_logs(executed_by);
CREATE INDEX IF NOT EXISTS idx_execution_logs_started_at ON config_execution_logs(started_at);
CREATE INDEX IF NOT EXISTS idx_execution_logs_file_hash ON config_execution_logs(file_hash);

-- ZIP configs indexes
CREATE INDEX IF NOT EXISTS idx_zip_file_configs_config_id ON zip_file_configs(config_id);

-- =====================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_staging_configs_updated_at 
    BEFORE UPDATE ON staging_configs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_column_mappings_updated_at 
    BEFORE UPDATE ON column_mappings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_zip_file_configs_updated_at 
    BEFORE UPDATE ON zip_file_configs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SAMPLE DATA - TRANSFORMATION FUNCTIONS
-- =====================================================

INSERT INTO transformation_functions (name, display_name, description, function_type, category, parameters) VALUES
('uppercase', 'Convert to Uppercase', 'Converts text to uppercase', 'builtin', 'text', '[]'),
('lowercase', 'Convert to Lowercase', 'Converts text to lowercase', 'builtin', 'text', '[]'),
('trim', 'Trim Whitespace', 'Removes leading and trailing whitespace', 'builtin', 'text', '[]'),
('replace', 'Replace Text', 'Replaces text in a string', 'builtin', 'text', '[{"name": "search", "type": "string"}, {"name": "replace", "type": "string"}]'),
('substring', 'Extract Substring', 'Extracts a portion of text', 'builtin', 'text', '[{"name": "start", "type": "integer"}, {"name": "length", "type": "integer"}]'),
('date_format', 'Format Date', 'Formats date strings', 'builtin', 'date', '[{"name": "input_format", "type": "string"}, {"name": "output_format", "type": "string"}]'),
('number_format', 'Format Number', 'Formats numbers with decimal places', 'builtin', 'number', '[{"name": "decimal_places", "type": "integer"}]'),
('concatenate', 'Concatenate Strings', 'Joins multiple strings together', 'builtin', 'text', '[{"name": "separator", "type": "string"}]'),
('split', 'Split String', 'Splits string by delimiter', 'builtin', 'text', '[{"name": "delimiter", "type": "string"}]'),
('validate_postcode', 'Validate UK Postcode', 'Validates UK postcode format', 'builtin', 'validation', '[]')
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- VIEWS FOR EASY QUERYING
-- =====================================================

-- View for complete configuration with mappings
CREATE OR REPLACE VIEW staging_configs_complete AS
SELECT 
    sc.*,
    COUNT(cm.id) as mapping_count,
    COUNT(vr.id) as validation_rule_count,
    COUNT(zfc.id) as zip_config_count
FROM staging_configs sc
LEFT JOIN column_mappings cm ON sc.id = cm.config_id
LEFT JOIN validation_rules vr ON sc.id = vr.config_id
LEFT JOIN zip_file_configs zfc ON sc.id = zfc.config_id
WHERE sc.is_active = true
GROUP BY sc.id;

-- View for recent executions
CREATE OR REPLACE VIEW recent_executions AS
SELECT 
    cel.*,
    sc.name as config_name,
    sc.staging_table_name
FROM config_execution_logs cel
JOIN staging_configs sc ON cel.config_id = sc.id
ORDER BY cel.started_at DESC;

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE staging_configs IS 'Main table for storing data ingestion configuration templates';
COMMENT ON TABLE column_mappings IS 'Maps source columns to target columns with transformation rules';
COMMENT ON TABLE transformation_functions IS 'Available transformation functions for data processing';
COMMENT ON TABLE validation_rules IS 'Data validation rules for ensuring data quality';
COMMENT ON TABLE config_templates IS 'Reusable configuration templates for common data types';
COMMENT ON TABLE config_execution_logs IS 'Logs of configuration executions for monitoring and debugging';
COMMENT ON TABLE zip_file_configs IS 'Special configurations for handling ZIP files with separate header/data files'; 