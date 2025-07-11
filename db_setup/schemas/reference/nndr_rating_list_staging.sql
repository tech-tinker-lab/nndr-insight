-- public.nndr_rating_list_staging definition

CREATE TABLE IF NOT EXISTS public.nndr_rating_list_staging (
    list_altered TEXT,
    community_code TEXT,
    ba_reference TEXT,
    property_category_code TEXT,
    property_description TEXT,
    property_address TEXT,
    street_descriptor TEXT,
    locality TEXT,
    post_town TEXT,
    administrative_area TEXT,
    postcode TEXT,
    effective_date TEXT,
    partially_domestic_signal TEXT,
    rateable_value TEXT,
    scat_code TEXT,
    appeal_settlement_code TEXT,
    unique_property_ref TEXT,
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