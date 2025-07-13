-- public.os_open_usrn_staging definition

CREATE TABLE IF NOT EXISTS public.os_open_usrn_staging (
    -- OS Open USRN Data Columns
    geometry public.geometry(geometryz, 27700) NULL,
    usrn int8 NULL,
    street_type text NULL,
    -- Standard metadata columns (9 columns)
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

-- Create spatial index for geometry column
CREATE INDEX IF NOT EXISTS idx_os_open_usrn_staging_geometry ON public.os_open_usrn_staging USING gist (geometry); 