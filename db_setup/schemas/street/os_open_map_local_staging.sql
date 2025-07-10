-- public.os_open_map_local_staging definition

CREATE TABLE IF NOT EXISTS public.os_open_map_local_staging (
    id TEXT,
    fid TEXT,
    gml_id TEXT,
    feature_code TEXT,
    geometry geometry(GEOMETRY, 27700),
    feature_type TEXT,
    properties TEXT,
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