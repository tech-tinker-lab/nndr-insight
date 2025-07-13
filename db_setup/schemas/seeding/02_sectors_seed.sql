-- Sectors Seeding Script
-- Provides comprehensive sector definitions for AI-powered dataset classification
-- Includes government, private sector, and specific industry sectors

-- =============================================================================
-- SECTORS SEEDING
-- =============================================================================

-- Insert Government Sectors
INSERT INTO design_enhanced.sectors (sector_code, sector_name, sector_category, description, is_active) VALUES
('GOV_CENTRAL', 'Central Government', 'government', 'UK Central Government departments and agencies', true),
('GOV_LOCAL', 'Local Government', 'government', 'Local authorities and councils', true),
('GOV_DEVOLVED', 'Devolved Administrations', 'government', 'Scottish, Welsh, and Northern Irish governments', true),
('GOV_AGENCIES', 'Government Agencies', 'government', 'Non-departmental public bodies and agencies', true);

-- Insert Private Sector Sectors
INSERT INTO design_enhanced.sectors (sector_code, sector_name, sector_category, description, is_active) VALUES
('PRIVATE_FINANCE', 'Financial Services', 'business', 'Banks, insurance, and financial institutions', true),
('PRIVATE_PROPERTY', 'Property and Real Estate', 'business', 'Property development, management, and valuation', true),
('PRIVATE_TRANSPORT', 'Transport and Logistics', 'business', 'Transportation, logistics, and infrastructure', true),
('PRIVATE_UTILITIES', 'Utilities and Energy', 'business', 'Energy, water, and utility providers', true),
('PRIVATE_RETAIL', 'Retail and Commerce', 'business', 'Retail, e-commerce, and commercial services', true);

-- Insert Specific Industry Sectors
INSERT INTO design_enhanced.sectors (sector_code, sector_name, sector_category, description, is_active) VALUES
('HEALTHCARE', 'Healthcare and Social Care', 'health', 'Healthcare providers, hospitals, and social care services', true),
('EDUCATION', 'Education and Training', 'education', 'Schools, universities, and training providers', true),
('ENVIRONMENT', 'Environmental and Conservation', 'environment', 'Environmental protection, conservation, and sustainability', true),
('PLANNING', 'Planning and Development', 'planning', 'Urban planning, development control, and land use', true),
('EMERGENCY', 'Emergency Services', 'emergency', 'Police, fire, ambulance, and emergency response', true);

-- Insert Cross-Sector Categories
INSERT INTO design_enhanced.sectors (sector_code, sector_name, sector_category, description, is_active) VALUES
('INFRASTRUCTURE', 'Infrastructure and Construction', 'infrastructure', 'Infrastructure development, construction, and engineering', true),
('TECHNOLOGY', 'Technology and Digital', 'technology', 'Technology companies, digital services, and IT', true),
('RESEARCH', 'Research and Academia', 'research', 'Research institutions, universities, and academic bodies', true),
('REGULATORY', 'Regulatory and Compliance', 'regulatory', 'Regulatory bodies and compliance organizations', true);

-- Insert Specialized Sectors
INSERT INTO design_enhanced.sectors (sector_code, sector_name, sector_category, description, is_active) VALUES
('DEFENCE', 'Defence and Security', 'defence', 'Defence, security, and intelligence services', true),
('JUSTICE', 'Justice and Legal', 'justice', 'Courts, legal services, and justice system', true),
('CULTURE', 'Culture and Heritage', 'culture', 'Museums, libraries, and cultural institutions', true),
('SPORTS', 'Sports and Recreation', 'sports', 'Sports organizations, recreation, and leisure', true);

-- Update timestamps
UPDATE design_enhanced.sectors SET
    created_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE created_at IS NULL; 