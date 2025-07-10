-- Create OS Open USRN Staging Table
-- This script creates the staging table with correct PostGIS geometry column

-- Create the staging table with correct PostGIS geometry column
CREATE TABLE IF NOT EXISTS public.os_open_usrn_staging (
    geometry GEOMETRY(GEOMETRYZ, 27700),  -- British National Grid (EPSG:27700) with Z dimension
    usrn TEXT,
    street_type TEXT,
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_os_open_usrn_staging_batch ON public.os_open_usrn_staging (batch_id);
CREATE INDEX IF NOT EXISTS idx_os_open_usrn_staging_session ON public.os_open_usrn_staging (session_id);
CREATE INDEX IF NOT EXISTS idx_os_open_usrn_staging_usrn ON public.os_open_usrn_staging (usrn);
CREATE INDEX IF NOT EXISTS idx_os_open_usrn_staging_geometry ON public.os_open_usrn_staging USING GIST (geometry); 