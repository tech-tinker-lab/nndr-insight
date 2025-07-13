-- Governing Bodies Seeding Script
-- Provides comprehensive list of governing bodies for AI-powered dataset classification
-- Includes UK government departments, agencies, and data providers

-- =============================================================================
-- GOVERNING BODIES SEEDING
-- =============================================================================

-- Insert Central Government Departments (no parent references)
INSERT INTO design_enhanced.governing_bodies (body_code, body_name, body_type, parent_body, description, data_standards, contact_info, website_url, is_active) VALUES
('ONS', 'Office for National Statistics', 'Central_Government', NULL, 'UK national statistical institute and largest producer of official statistics', '["GDS_Standards", "Open_Data_Standard", "ISO_19115"]', '{"email": "data@ons.gov.uk", "phone": "0845 601 3034"}', 'https://www.ons.gov.uk', true),
('OS', 'Ordnance Survey', 'Government_Agency', NULL, 'National mapping agency for Great Britain', '["OS_Standards", "BS7666", "ISO_19115"]', '{"email": "customerservices@os.uk", "phone": "03456 05 05 05"}', 'https://www.ordnancesurvey.co.uk', true),
('DWP', 'Department for Work and Pensions', 'Central_Government', NULL, 'Department responsible for welfare, pensions, and child maintenance policy', '["GDS_Standards", "DQ_Accuracy"]', '{"email": "correspondence@dwp.gov.uk", "phone": "0800 731 0469"}', 'https://www.gov.uk/government/organisations/department-for-work-pensions', true),
('DfT', 'Department for Transport', 'Central_Government', NULL, 'Department responsible for transport policy and infrastructure', '["Highways_Standard", "ISO_19111"]', '{"email": "dft@dft.gov.uk", "phone": "0300 330 3000"}', 'https://www.gov.uk/government/organisations/department-for-transport', true),
('DEFRA', 'Department for Environment, Food and Rural Affairs', 'Central_Government', NULL, 'Department responsible for environmental protection and rural affairs', '["Environmental_Standard", "ISO_19115"]', '{"email": "defra.helpline@defra.gov.uk", "phone": "03459 33 55 77"}', 'https://www.gov.uk/government/organisations/department-for-environment-food-rural-affairs', true),
('MHCLG', 'Ministry of Housing, Communities and Local Government', 'Central_Government', NULL, 'Department responsible for housing, communities, and local government', '["Planning_Standard", "BS7666"]', '{"email": "enquiries@communities.gov.uk", "phone": "0303 444 0000"}', 'https://www.gov.uk/government/organisations/ministry-of-housing-communities-and-local-government', true),
('DHSC', 'Department of Health and Social Care', 'Central_Government', NULL, 'Department responsible for health and social care policy', '["Health_Standard", "DQ_Accuracy"]', '{"email": "dhsc@dhsc.gov.uk", "phone": "020 7210 4850"}', 'https://www.gov.uk/government/organisations/department-of-health-and-social-care', true),
('HMRC', 'HM Revenue and Customs', 'Central_Government', NULL, 'Tax authority for the UK', '["DQ_Accuracy", "DQ_Completeness"]', '{"email": "enquiries@hmrc.gov.uk", "phone": "0300 200 3300"}', 'https://www.gov.uk/government/organisations/hm-revenue-customs', true),
('MOJ', 'Ministry of Justice', 'Central_Government', NULL, 'Department responsible for justice, courts, and prisons', '["DQ_Completeness", "DQ_Accuracy"]', '{"email": "public.enquiries@justice.gov.uk", "phone": "020 3334 3555"}', 'https://www.gov.uk/government/organisations/ministry-of-justice', true),
('DfE', 'Department for Education', 'Central_Government', NULL, 'Department responsible for education policy', '["DQ_Completeness", "DQ_Consistency"]', '{"email": "enquiries@education.gov.uk", "phone": "0370 000 2288"}', 'https://www.gov.uk/government/organisations/department-for-education', true),
('HMT', 'HM Treasury', 'Central_Government', NULL, 'UK government department responsible for economic policy', '["DQ_Accuracy", "ISO_19115"]', '{"email": "public.enquiries@hmtreasury.gov.uk", "phone": "020 7270 5000"}', 'https://www.gov.uk/government/organisations/hm-treasury', true),
('BEIS', 'Department for Business, Energy and Industrial Strategy', 'Central_Government', NULL, 'Department responsible for business, energy and industrial strategy', '["Environmental_Standard", "DQ_Accuracy"]', '{"email": "enquiries@beis.gov.uk", "phone": "020 7215 5000"}', 'https://www.gov.uk/government/organisations/department-for-business-energy-and-industrial-strategy', true);

-- Insert VOA with HMRC parent (now that HMRC exists)
INSERT INTO design_enhanced.governing_bodies (body_code, body_name, body_type, parent_body, description, data_standards, contact_info, website_url, is_active) VALUES
('VOA', 'Valuation Office Agency', 'Government_Agency', 'HMRC', 'Government agency responsible for business rates and council tax valuations', '["VOA_Standards", "NNDR_Standard"]', '{"email": "voa@voa.gov.uk", "phone": "03000 501 501"}', 'https://www.gov.uk/government/organisations/valuation-office-agency', true);

-- Insert Government Agencies and NDPBs (with existing parents)
INSERT INTO design_enhanced.governing_bodies (body_code, body_name, body_type, parent_body, description, data_standards, contact_info, website_url, is_active) VALUES
('EA', 'Environment Agency', 'Government_Agency', 'DEFRA', 'Executive agency responsible for environmental protection and regulation', '["Environmental_Standard", "ISO_19115"]', '{"email": "enquiries@environment-agency.gov.uk", "phone": "03708 506 506"}', 'https://www.gov.uk/government/organisations/environment-agency', true),
('HE', 'Highways England', 'Government_Agency', 'DfT', 'Government company responsible for motorways and major A roads in England', '["Highways_Standard", "OS_Standards"]', '{"email": "info@highwaysengland.co.uk", "phone": "0300 123 5000"}', 'https://www.gov.uk/government/organisations/highways-england', true),
('NHS_Digital', 'NHS Digital', 'Government_Agency', 'DHSC', 'National information and technology partner for the health and care system', '["Health_Standard", "DQ_Accuracy"]', '{"email": "enquiries@nhsdigital.nhs.uk", "phone": "0300 303 5678"}', 'https://digital.nhs.uk', true),
('PHE', 'Public Health England', 'Government_Agency', 'DHSC', 'Executive agency responsible for public health protection and improvement', '["Health_Standard", "DQ_Accuracy"]', '{"email": "enquiries@phe.gov.uk", "phone": "020 7654 8000"}', 'https://www.gov.uk/government/organisations/public-health-england', true),
('CQC', 'Care Quality Commission', 'Regulatory_Body', 'DHSC', 'Independent regulator of health and social care in England', '["Health_Standard", "DQ_Completeness"]', '{"email": "enquiries@cqc.org.uk", "phone": "03000 616161"}', 'https://www.cqc.org.uk', true),
('Ofsted', 'Office for Standards in Education', 'Regulatory_Body', 'DfE', 'Non-ministerial department responsible for inspecting schools and other services', '["DQ_Completeness", "DQ_Consistency"]', '{"email": "enquiries@ofsted.gov.uk", "phone": "0300 123 1231"}', 'https://www.gov.uk/government/organisations/ofsted', true),
('FCA', 'Financial Conduct Authority', 'Regulatory_Body', 'HMT', 'Financial regulatory body in the UK', '["DQ_Accuracy", "ISO_19115"]', '{"email": "consumer.queries@fca.org.uk", "phone": "0800 111 6768"}', 'https://www.fca.org.uk', true),
('Ofgem', 'Office of Gas and Electricity Markets', 'Regulatory_Body', 'BEIS', 'Regulator for gas and electricity markets in Great Britain', '["Environmental_Standard", "DQ_Accuracy"]', '{"email": "consumeraffairs@ofgem.gov.uk", "phone": "020 7901 7000"}', 'https://www.ofgem.gov.uk', true);

-- Insert Local Government Bodies
INSERT INTO design_enhanced.governing_bodies (body_code, body_name, body_type, parent_body, description, data_standards, contact_info, website_url, is_active) VALUES
('LGA', 'Local Government Association', 'Local_Government', NULL, 'Membership body for local authorities in England and Wales', '["BS7666", "INSPIRE_UK"]', '{"email": "info@local.gov.uk", "phone": "020 7664 3000"}', 'https://www.local.gov.uk', true),
('GLA', 'Greater London Authority', 'Local_Government', NULL, 'Strategic authority for Greater London', '["BS7666", "Planning_Standard"]', '{"email": "enquiries@london.gov.uk", "phone": "020 7983 4000"}', 'https://www.london.gov.uk', true),
('TfL', 'Transport for London', 'Local_Government', 'GLA', 'Local government body responsible for transport in London', '["Highways_Standard", "OS_Standards"]', '{"email": "enquiries@tfl.gov.uk", "phone": "0343 222 1234"}', 'https://tfl.gov.uk', true);

-- Insert Devolved Administration Bodies
INSERT INTO design_enhanced.governing_bodies (body_code, body_name, body_type, parent_body, description, data_standards, contact_info, website_url, is_active) VALUES
('SG', 'Scottish Government', 'Devolved_Government', NULL, 'Devolved government for Scotland', '["ISO_19115", "GDS_Standards"]', '{"email": "scottish.ministers@gov.scot", "phone": "0300 244 4000"}', 'https://www.gov.scot', true),
('WG', 'Welsh Government', 'Devolved_Government', NULL, 'Devolved government for Wales', '["ISO_19115", "GDS_Standards"]', '{"email": "correspondence@gov.wales", "phone": "0300 060 4400"}', 'https://gov.wales', true),
('NI_Executive', 'Northern Ireland Executive', 'Devolved_Government', NULL, 'Devolved government for Northern Ireland', '["ISO_19115", "GDS_Standards"]', '{"email": "info@executiveoffice-ni.gov.uk", "phone": "028 9052 8400"}', 'https://www.executiveoffice-ni.gov.uk', true);

-- Insert Research and Academic Bodies (with existing parents)
INSERT INTO design_enhanced.governing_bodies (body_code, body_name, body_type, parent_body, description, data_standards, contact_info, website_url, is_active) VALUES
('UKRI', 'UK Research and Innovation', 'Research_Body', 'BEIS', 'Non-departmental public body that directs research and innovation funding', '["ISO_19115", "DCAT_UK"]', '{"email": "info@ukri.org", "phone": "01793 444000"}', 'https://www.ukri.org', true),
('ESRC', 'Economic and Social Research Council', 'Research_Body', 'UKRI', 'UK research council for social and economic research', '["ISO_19115", "DCAT_UK"]', '{"email": "esrc@esrc.ukri.org", "phone": "01793 413000"}', 'https://esrc.ukri.org', true),
('NERC', 'Natural Environment Research Council', 'Research_Body', 'UKRI', 'UK research council for environmental science', '["Environmental_Standard", "ISO_19115"]', '{"email": "info@nerc.ukri.org", "phone": "01793 411500"}', 'https://nerc.ukri.org', true);

-- Insert International and Standards Bodies
INSERT INTO design_enhanced.governing_bodies (body_code, body_name, body_type, parent_body, description, data_standards, contact_info, website_url, is_active) VALUES
('ISO', 'International Organization for Standardization', 'International_Standards', NULL, 'International standard-setting body', '["ISO_19115", "ISO_19139", "ISO_19110"]', '{"email": "central@iso.org", "phone": "+41 22 749 01 11"}', 'https://www.iso.org', true),
('BSI', 'British Standards Institution', 'Standards_Body', NULL, 'UK national standards body', '["BS7666", "GDS_Standards"]', '{"email": "info@bsigroup.com", "phone": "020 8996 9000"}', 'https://www.bsigroup.com', true),
('ODI', 'Open Data Institute', 'Standards_Body', NULL, 'Non-profit organization promoting open data', '["Open_Data_Standard", "5_Star_Data"]', '{"email": "info@theodi.org", "phone": "020 7012 1360"}', 'https://theodi.org', true);

-- Update timestamps
UPDATE design_enhanced.governing_bodies SET
    created_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE created_at IS NULL; 