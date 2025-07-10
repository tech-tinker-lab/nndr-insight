-- public.gazetteer_staging definition

CREATE TABLE IF NOT EXISTS public.gazetteer_staging (
    property_id TEXT,
    address TEXT,
    postcode TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    property_type TEXT,
    district TEXT,
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