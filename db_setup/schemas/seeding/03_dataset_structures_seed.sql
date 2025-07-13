-- Dataset Structures Seeding Script
-- Provides predefined dataset structures for AI-powered ingestion
-- Includes ONS Postcode Directory and other key government datasets

-- =============================================================================
-- DATASET STRUCTURES SEEDING
-- =============================================================================

-- Insert ONS Postcode Directory Dataset Structure
INSERT INTO design_enhanced.dataset_structures (
    dataset_name, dataset_type, source_type, target_schema_type,
    governing_body, data_standards, sector_code, description,
    field_definitions, validation_rules, sample_file_info, is_active, created_by
) VALUES (
    'ONS Postcode Directory',
    'postcode_reference',
    'file',
    'staging',
    'Office for National Statistics',
    '["BS7666", "OS_Standards"]',
    'GOV_CENTRAL',
    'Comprehensive postcode directory with geographic and administrative data',
    '[
        {"field_name": "pcd", "data_type": "VARCHAR(8)", "description": "Postcode", "is_required": true, "validation": "postcode_format"},
        {"field_name": "pcd2", "data_type": "VARCHAR(8)", "description": "Postcode with spaces", "is_required": false, "validation": "postcode_format"},
        {"field_name": "pcds", "data_type": "VARCHAR(8)", "description": "Postcode sector", "is_required": false, "validation": "sector_format"},
        {"field_name": "dointr", "data_type": "INTEGER", "description": "Date of introduction", "is_required": false, "validation": "date_format"},
        {"field_name": "doterm", "data_type": "INTEGER", "description": "Date of termination", "is_required": false, "validation": "date_format"},
        {"field_name": "usertype", "data_type": "INTEGER", "description": "User type", "is_required": false, "validation": "range_1_2"},
        {"field_name": "oseast1m", "data_type": "INTEGER", "description": "OS Easting", "is_required": false, "validation": "coordinate_range"},
        {"field_name": "osnrth1m", "data_type": "INTEGER", "description": "OS Northing", "is_required": false, "validation": "coordinate_range"},
        {"field_name": "osgrdind", "data_type": "INTEGER", "description": "OS Grid reference indicator", "is_required": false, "validation": "range_1_9"},
        {"field_name": "oa11", "data_type": "VARCHAR(9)", "description": "2011 Output Area", "is_required": false, "validation": "oa_format"},
        {"field_name": "cty", "data_type": "VARCHAR(9)", "description": "County", "is_required": false, "validation": "text_length"},
        {"field_name": "ced", "data_type": "VARCHAR(9)", "description": "County Electoral Division", "is_required": false, "validation": "text_length"},
        {"field_name": "laua", "data_type": "VARCHAR(9)", "description": "Local Authority District", "is_required": false, "validation": "text_length"},
        {"field_name": "ward", "data_type": "VARCHAR(9)", "description": "Electoral Ward", "is_required": false, "validation": "text_length"},
        {"field_name": "hlthau", "data_type": "VARCHAR(9)", "description": "Health Authority", "is_required": false, "validation": "text_length"},
        {"field_name": "nhser", "data_type": "VARCHAR(9)", "description": "NHS England Region", "is_required": false, "validation": "text_length"},
        {"field_name": "ctry", "data_type": "VARCHAR(9)", "description": "Country", "is_required": false, "validation": "text_length"},
        {"field_name": "rgn", "data_type": "VARCHAR(9)", "description": "Region", "is_required": false, "validation": "text_length"},
        {"field_name": "pcon", "data_type": "VARCHAR(9)", "description": "Parliamentary Constituency", "is_required": false, "validation": "text_length"},
        {"field_name": "eer", "data_type": "VARCHAR(9)", "description": "European Electoral Region", "is_required": false, "validation": "text_length"},
        {"field_name": "teclec", "data_type": "VARCHAR(9)", "description": "Local Learning and Skills Council", "is_required": false, "validation": "text_length"},
        {"field_name": "ttwa", "data_type": "VARCHAR(9)", "description": "Travel to Work Area", "is_required": false, "validation": "text_length"},
        {"field_name": "pct", "data_type": "VARCHAR(9)", "description": "Primary Care Trust", "is_required": false, "validation": "text_length"},
        {"field_name": "nuts", "data_type": "VARCHAR(5)", "description": "NUTS code", "is_required": false, "validation": "nuts_format"},
        {"field_name": "statsward", "data_type": "VARCHAR(6)", "description": "Statistical Ward", "is_required": false, "validation": "text_length"},
        {"field_name": "oa01", "data_type": "VARCHAR(10)", "description": "2001 Output Area", "is_required": false, "validation": "oa_format"},
        {"field_name": "casward", "data_type": "VARCHAR(10)", "description": "Census Area Statistics Ward", "is_required": false, "validation": "text_length"},
        {"field_name": "park", "data_type": "VARCHAR(9)", "description": "National Park", "is_required": false, "validation": "text_length"},
        {"field_name": "lsoa01", "data_type": "VARCHAR(9)", "description": "2001 Lower Layer Super Output Area", "is_required": false, "validation": "lsoa_format"},
        {"field_name": "msoa01", "data_type": "VARCHAR(9)", "description": "2001 Middle Layer Super Output Area", "is_required": false, "validation": "msoa_format"},
        {"field_name": "ur01ind", "data_type": "VARCHAR(1)", "description": "2001 Urban/Rural Indicator", "is_required": false, "validation": "ur_indicator"},
        {"field_name": "oac01", "data_type": "VARCHAR(3)", "description": "2001 Output Area Classification", "is_required": false, "validation": "oac_format"},
        {"field_name": "oa11cd", "data_type": "VARCHAR(9)", "description": "2011 Output Area Classification", "is_required": false, "validation": "oa_format"},
        {"field_name": "lsoa11", "data_type": "VARCHAR(9)", "description": "2011 Lower Layer Super Output Area", "is_required": false, "validation": "lsoa_format"},
        {"field_name": "msoa11", "data_type": "VARCHAR(9)", "description": "2011 Middle Layer Super Output Area", "is_required": false, "validation": "msoa_format"},
        {"field_name": "wz11", "data_type": "VARCHAR(9)", "description": "2011 Workplace Zone", "is_required": false, "validation": "text_length"},
        {"field_name": "ccg", "data_type": "VARCHAR(9)", "description": "Clinical Commissioning Group", "is_required": false, "validation": "text_length"},
        {"field_name": "bua11", "data_type": "VARCHAR(9)", "description": "2011 Built-up Area", "is_required": false, "validation": "text_length"},
        {"field_name": "buasd11", "data_type": "VARCHAR(9)", "description": "2011 Built-up Area Sub-division", "is_required": false, "validation": "text_length"},
        {"field_name": "ru11ind", "data_type": "VARCHAR(2)", "description": "2011 Rural/Urban Indicator", "is_required": false, "validation": "ru_indicator"},
        {"field_name": "oac11", "data_type": "VARCHAR(3)", "description": "2011 Output Area Classification", "is_required": false, "validation": "oac_format"},
        {"field_name": "lat", "data_type": "DECIMAL(10,8)", "description": "Latitude", "is_required": false, "validation": "latitude_range"},
        {"field_name": "long", "data_type": "DECIMAL(11,8)", "description": "Longitude", "is_required": false, "validation": "longitude_range"},
        {"field_name": "lep1", "data_type": "VARCHAR(9)", "description": "Local Enterprise Partnership 1", "is_required": false, "validation": "text_length"},
        {"field_name": "lep2", "data_type": "VARCHAR(9)", "description": "Local Enterprise Partnership 2", "is_required": false, "validation": "text_length"},
        {"field_name": "pfa", "data_type": "VARCHAR(9)", "description": "Police Force Area", "is_required": false, "validation": "text_length"},
        {"field_name": "imd", "data_type": "INTEGER", "description": "Index of Multiple Deprivation", "is_required": false, "validation": "imd_range"}
    ]',
    '[
        {"rule_name": "postcode_format", "rule_type": "regex", "rule_value": "^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$", "error_message": "Invalid postcode format"},
        {"rule_name": "coordinate_range", "rule_type": "range", "rule_value": {"min": 0, "max": 999999}, "error_message": "Coordinate out of valid range"},
        {"rule_name": "latitude_range", "rule_type": "range", "rule_value": {"min": 49.0, "max": 61.0}, "error_message": "Latitude out of UK range"},
        {"rule_name": "longitude_range", "rule_type": "range", "rule_value": {"min": -8.0, "max": 2.0}, "error_message": "Longitude out of UK range"},
        {"rule_name": "imd_range", "rule_type": "range", "rule_value": {"min": 1, "max": 32844}, "error_message": "IMD rank out of valid range"}
    ]',
    '{"file_format": "csv", "encoding": "utf-8", "delimiter": ",", "has_header": true, "sample_filename": "ONSPD_MAY_2023_UK.csv", "file_size_mb": 150, "record_count": 2800000}',
    true,
    'system'
) ON CONFLICT (dataset_name) DO NOTHING;

-- Insert Code-Point Open Dataset Structure
INSERT INTO design_enhanced.dataset_structures (
    dataset_name, dataset_type, source_type, target_schema_type,
    governing_body, data_standards, sector_code, description,
    field_definitions, validation_rules, sample_file_info, is_active, created_by
) VALUES (
    'Code-Point Open',
    'postcode_coordinates',
    'file',
    'staging',
    'Ordnance Survey',
    '["OS_Standards", "BS7666"]',
    'GOV_AGENCIES',
    'Postcode to coordinate mapping with high precision',
    '[
        {"field_name": "postcode", "data_type": "VARCHAR(8)", "description": "Postcode", "is_required": true, "validation": "postcode_format"},
        {"field_name": "positional_quality_indicator", "data_type": "INTEGER", "description": "Positional quality indicator", "is_required": true, "validation": "pqi_range"},
        {"field_name": "eastings", "data_type": "INTEGER", "description": "OS Easting coordinate", "is_required": true, "validation": "easting_range"},
        {"field_name": "northings", "data_type": "INTEGER", "description": "OS Northing coordinate", "is_required": true, "validation": "northing_range"},
        {"field_name": "country_code", "data_type": "VARCHAR(1)", "description": "Country code", "is_required": true, "validation": "country_code"},
        {"field_name": "nhs_regional_ha_code", "data_type": "VARCHAR(3)", "description": "NHS Regional Health Authority code", "is_required": false, "validation": "nhs_code"},
        {"field_name": "nhs_ha_code", "data_type": "VARCHAR(3)", "description": "NHS Health Authority code", "is_required": false, "validation": "nhs_code"},
        {"field_name": "admin_county_code", "data_type": "VARCHAR(2)", "description": "Administrative county code", "is_required": false, "validation": "county_code"},
        {"field_name": "admin_district_code", "data_type": "VARCHAR(2)", "description": "Administrative district code", "is_required": false, "validation": "district_code"},
        {"field_name": "admin_ward_code", "data_type": "VARCHAR(2)", "description": "Administrative ward code", "is_required": false, "validation": "ward_code"}
    ]',
    '[
        {"rule_name": "postcode_format", "rule_type": "regex", "rule_value": "^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$", "error_message": "Invalid postcode format"},
        {"rule_name": "pqi_range", "rule_type": "range", "rule_value": {"min": 1, "max": 9}, "error_message": "PQI must be between 1 and 9"},
        {"rule_name": "easting_range", "rule_type": "range", "rule_value": {"min": 0, "max": 700000}, "error_message": "Easting coordinate out of range"},
        {"rule_name": "northing_range", "rule_type": "range", "rule_value": {"min": 0, "max": 1300000}, "error_message": "Northing coordinate out of range"},
        {"rule_name": "country_code", "rule_type": "enum", "rule_value": ["E", "W", "S", "N"], "error_message": "Invalid country code"}
    ]',
    '{"file_format": "csv", "encoding": "utf-8", "delimiter": ",", "has_header": true, "sample_filename": "codepo_gb.zip", "file_size_mb": 25, "record_count": 1700000}',
    true,
    'system'
) ON CONFLICT (dataset_name) DO NOTHING;

-- Insert NNDR Properties Dataset Structure
INSERT INTO design_enhanced.dataset_structures (
    dataset_name, dataset_type, source_type, target_schema_type,
    governing_body, data_standards, sector_code, description,
    field_definitions, validation_rules, sample_file_info, is_active, created_by
) VALUES (
    'NNDR Properties',
    'business_rates',
    'file',
    'staging',
    'Valuation Office Agency',
    '["NNDR_Standard", "VOA_Standards"]',
    'GOV_AGENCIES',
    'National Non-Domestic Rates property data',
    '[
        {"field_name": "ba_reference", "data_type": "VARCHAR(20)", "description": "Billing Authority Reference", "is_required": true, "validation": "ba_ref_format"},
        {"field_name": "list_altered", "data_type": "DATE", "description": "Date list was altered", "is_required": false, "validation": "date_format"},
        {"field_name": "community_code", "data_type": "VARCHAR(10)", "description": "Community code", "is_required": false, "validation": "text_length"},
        {"field_name": "rateable_value", "data_type": "DECIMAL(12,2)", "description": "Rateable value", "is_required": true, "validation": "positive_amount"},
        {"field_name": "property_type", "data_type": "VARCHAR(50)", "description": "Property type", "is_required": false, "validation": "text_length"},
        {"field_name": "occupier_name", "data_type": "VARCHAR(200)", "description": "Occupier name", "is_required": false, "validation": "text_length"},
        {"field_name": "property_address", "data_type": "TEXT", "description": "Property address", "is_required": false, "validation": "address_format"},
        {"field_name": "postcode", "data_type": "VARCHAR(8)", "description": "Postcode", "is_required": false, "validation": "postcode_format"},
        {"field_name": "uprn", "data_type": "VARCHAR(12)", "description": "Unique Property Reference Number", "is_required": false, "validation": "uprn_format"},
        {"field_name": "usrn", "data_type": "VARCHAR(8)", "description": "Unique Street Reference Number", "is_required": false, "validation": "usrn_format"},
        {"field_name": "latitude", "data_type": "DECIMAL(10,8)", "description": "Latitude", "is_required": false, "validation": "latitude_range"},
        {"field_name": "longitude", "data_type": "DECIMAL(11,8)", "description": "Longitude", "is_required": false, "validation": "longitude_range"}
    ]',
    '[
        {"rule_name": "ba_ref_format", "rule_type": "regex", "rule_value": "^[0-9]{1,20}$", "error_message": "Invalid BA reference format"},
        {"rule_name": "positive_amount", "rule_type": "range", "rule_value": {"min": 0.01}, "error_message": "Rateable value must be positive"},
        {"rule_name": "postcode_format", "rule_type": "regex", "rule_value": "^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$", "error_message": "Invalid postcode format"},
        {"rule_name": "uprn_format", "rule_type": "regex", "rule_value": "^[0-9]{12}$", "error_message": "Invalid UPRN format"},
        {"rule_name": "usrn_format", "rule_type": "regex", "rule_value": "^[0-9]{8}$", "error_message": "Invalid USRN format"},
        {"rule_name": "latitude_range", "rule_type": "range", "rule_value": {"min": 49.0, "max": 61.0}, "error_message": "Latitude out of UK range"},
        {"rule_name": "longitude_range", "rule_type": "range", "rule_value": {"min": -8.0, "max": 2.0}, "error_message": "Longitude out of UK range"}
    ]',
    '{"file_format": "csv", "encoding": "utf-8", "delimiter": ",", "has_header": true, "sample_filename": "nndr_properties_2023.csv", "file_size_mb": 500, "record_count": 2000000}',
    true,
    'system'
) ON CONFLICT (dataset_name) DO NOTHING;

-- Update timestamps
UPDATE design_enhanced.dataset_structures SET
    created_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE created_at IS NULL; 