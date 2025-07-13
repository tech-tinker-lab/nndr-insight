-- Sample Datasets Seeding Script
-- Provides sample dataset examples for AI-powered pattern recognition and matching
-- Includes various data types, formats, and sources for training the AI system

-- =============================================================================
-- SAMPLE DATASETS SEEDING
-- =============================================================================

-- Insert Sample Dataset Examples
INSERT INTO design_enhanced.sample_datasets (
    dataset_name, dataset_type, source_type, governing_body, description, field_definitions, validation_rules, sample_file_info, is_active
) VALUES
('ONS Postcode Directory Sample', 'postcode_reference', 'file', 'ONS', 'Sample of ONS Postcode Directory with key fields for pattern recognition', '[{"pcd": "SW1A 1AA", "oseast1m": 529090, "osnrth1m": 179645}]', '[{"pattern": "postcode", "regex": "^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$", "confidence": 0.95}]', '{"file_format": "csv", "encoding": "utf-8", "delimiter": ",", "has_header": true}', true),
('Code-Point Open Sample', 'postcode_coordinates', 'file', 'OS', 'Sample of Code-Point Open with coordinate data for spatial analysis', '[{"postcode": "SW1A 1AA", "eastings": 529090, "northings": 179645}]', '[{"pattern": "postcode", "regex": "^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$", "confidence": 0.95}]', '{"file_format": "csv", "encoding": "utf-8", "delimiter": ",", "has_header": true}', true),
('NNDR Properties Sample', 'business_rates', 'file', 'VOA', 'Sample of NNDR properties data with business rates information', '[{"ba_reference": "123456789", "rateable_value": 50000.00, "property_type": "Office"}]', '[{"pattern": "ba_reference", "regex": "^[0-9]{9}$", "confidence": 0.90}]', '{"file_format": "csv", "encoding": "utf-8", "delimiter": ",", "has_header": true}', true);

-- Update timestamps
UPDATE design_enhanced.sample_datasets SET
    created_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE created_at IS NULL; 