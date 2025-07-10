-- public.historic_valuations_staging definition

CREATE TABLE IF NOT EXISTS public.historic_valuations_staging (
    billing_auth_code TEXT,
    ba_reference TEXT,
    scat_code TEXT,
    description TEXT,
    herid TEXT,
    effective_date TEXT,
    rateable_value TEXT,
    uprn TEXT,
    change_date TEXT,
    list_code TEXT,
    property_link_number TEXT,
    entry_date TEXT,
    removal_date TEXT,
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