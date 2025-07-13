-- public.lad_boundaries_staging definition

CREATE TABLE IF NOT EXISTS public.lad_boundaries_staging (
    -- Original shapefile data columns
    lad25cd TEXT,
    lad25nm TEXT,
    lad25nmw TEXT,
    bng_e DOUBLE PRECISION,
    bng_n DOUBLE PRECISION,
    long DOUBLE PRECISION,
    lat DOUBLE PRECISION,
    globalid TEXT,
    geometry geometry(GEOMETRY, 27700),
    
    -- Standard metadata columns
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