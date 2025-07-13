-- public.code_point_open_staging definition

CREATE TABLE IF NOT EXISTS public.code_point_open_staging (
    postcode TEXT,
    positional_quality_indicator TEXT,
    easting TEXT,
    northing TEXT,
    country_code TEXT,
    nhs_regional_ha_code TEXT,
    nhs_ha_code TEXT,
    admin_county_code TEXT,
    admin_district_code TEXT,
    admin_ward_code TEXT,
    source_name TEXT,
    upload_user TEXT,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch_id TEXT,
    source_file TEXT,
    file_size BIGINT,
    file_modified TIMESTAMP,
    session_id TEXT,
    client_name TEXT
); 