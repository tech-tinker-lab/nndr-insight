-- Data Standards Seeding Script
-- Provides comprehensive data standards for AI-powered compliance checking
-- Includes ISO, UK Government, and sector-specific standards

-- =============================================================================
-- DATA STANDARDS SEEDING
-- =============================================================================

-- Insert ISO Standards
INSERT INTO design_enhanced.data_standards (standard_code, standard_name, standard_type, governing_body, description, compliance_level, version, is_active) VALUES
('ISO_19115', 'Geographic Information - Metadata', 'ISO', 'International Organization for Standardization', 'Standard for describing geographic information and services', 'mandatory', '2014', true),
('ISO_19139', 'Geographic Information - Metadata - XML Schema Implementation', 'ISO', 'International Organization for Standardization', 'XML schema implementation for ISO 19115 metadata', 'mandatory', '2007', true),
('ISO_19110', 'Geographic Information - Feature Cataloguing Methodology', 'ISO', 'International Organization for Standardization', 'Methodology for cataloguing geographic features', 'mandatory', '2016', true),
('ISO_19111', 'Geographic Information - Spatial Referencing by Coordinates', 'ISO', 'International Organization for Standardization', 'Standard for spatial referencing using coordinates', 'mandatory', '2019', true),
('ISO_19112', 'Geographic Information - Spatial Referencing by Geographic Identifiers', 'ISO', 'International Organization for Standardization', 'Standard for spatial referencing using geographic identifiers', 'mandatory', '2019', true);

-- Insert UK Government Standards
INSERT INTO design_enhanced.data_standards (standard_code, standard_name, standard_type, governing_body, description, compliance_level, version, is_active) VALUES
('BS7666', 'Spatial Datasets for Geographical Referencing', 'UK_Standard', 'British Standards Institution', 'UK standard for address and street data', 'mandatory', '2006', true),
('GDS_Standards', 'Government Digital Service Standards', 'UK_Government', 'Government Digital Service', 'Standards for government digital services', 'mandatory', '2023', true),
('INSPIRE_UK', 'UK INSPIRE Implementation', 'EU_Directive', 'UK Government', 'UK implementation of INSPIRE directive', 'mandatory', '2021', true),
('OS_Standards', 'Ordnance Survey Standards', 'UK_Government', 'Ordnance Survey', 'Standards for OS geographic data', 'mandatory', '2023', true),
('VOA_Standards', 'Valuation Office Agency Standards', 'UK_Government', 'Valuation Office Agency', 'Standards for property valuation data', 'mandatory', '2023', true);

-- Insert Sector-Specific Standards
INSERT INTO design_enhanced.data_standards (standard_code, standard_name, standard_type, governing_body, description, compliance_level, version, is_active) VALUES
('NNDR_Standard', 'National Non-Domestic Rates Standard', 'Sector_Specific', 'Valuation Office Agency', 'Standard for business rates data', 'mandatory', '2023', true),
('Planning_Standard', 'Planning Application Data Standard', 'Sector_Specific', 'Ministry of Housing, Communities and Local Government', 'Standard for planning application data', 'mandatory', '2023', true),
('Highways_Standard', 'Highways Data Standard', 'Sector_Specific', 'Department for Transport', 'Standard for highways and transport data', 'mandatory', '2023', true),
('Environmental_Standard', 'Environmental Data Standard', 'Sector_Specific', 'Department for Environment, Food and Rural Affairs', 'Standard for environmental data', 'mandatory', '2023', true),
('Health_Standard', 'Public Health Data Standard', 'Sector_Specific', 'Department of Health and Social Care', 'Standard for public health data', 'mandatory', '2023', true);

-- Insert Data Quality Standards
INSERT INTO design_enhanced.data_standards (standard_code, standard_name, standard_type, governing_body, description, compliance_level, version, is_active) VALUES
('DQ_Completeness', 'Data Quality - Completeness', 'Quality_Standard', 'Data Quality Framework', 'Standard for data completeness assessment', 'mandatory', '2023', true),
('DQ_Accuracy', 'Data Quality - Accuracy', 'Quality_Standard', 'Data Quality Framework', 'Standard for data accuracy assessment', 'mandatory', '2023', true),
('DQ_Consistency', 'Data Quality - Consistency', 'Quality_Standard', 'Data Quality Framework', 'Standard for data consistency assessment', 'mandatory', '2023', true),
('DQ_Timeliness', 'Data Quality - Timeliness', 'Quality_Standard', 'Data Quality Framework', 'Standard for data timeliness assessment', 'mandatory', '2023', true),
('DQ_Accessibility', 'Data Quality - Accessibility', 'Quality_Standard', 'Data Quality Framework', 'Standard for data accessibility assessment', 'mandatory', '2023', true);

-- Insert Open Data Standards
INSERT INTO design_enhanced.data_standards (standard_code, standard_name, standard_type, governing_body, description, compliance_level, version, is_active) VALUES
('Open_Data_Standard', 'Open Data Standard', 'Open_Data', 'Open Data Institute', 'Standard for open government data', 'mandatory', '2023', true),
('5_Star_Data', '5-Star Open Data', 'Open_Data', 'Tim Berners-Lee', '5-star rating system for open data', 'mandatory', '2010', true),
('DCAT_UK', 'Data Catalog Vocabulary for UK Government', 'Open_Data', 'UK Government', 'UK profile of DCAT for government data catalogs', 'mandatory', '2023', true);

-- Update timestamps
UPDATE design_enhanced.data_standards SET
    created_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE created_at IS NULL; 