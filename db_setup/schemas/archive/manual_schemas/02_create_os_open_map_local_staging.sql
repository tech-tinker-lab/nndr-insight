-- Create OS Open Map Local Staging Table
-- This script creates the staging table with correct PostGIS geometry column

-- Create the staging table with correct PostGIS geometry column
CREATE TABLE IF NOT EXISTS public.os_open_map_local_staging (
    id TEXT,
    fid TEXT,
    gml_id TEXT,
    feature_code TEXT,
    geometry GEOMETRY(GEOMETRY, 27700),  -- British National Grid (EPSG:27700)
    feature_type TEXT,
    properties TEXT,
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
CREATE INDEX IF NOT EXISTS idx_os_open_map_local_staging_batch ON public.os_open_map_local_staging (batch_id);
CREATE INDEX IF NOT EXISTS idx_os_open_map_local_staging_session ON public.os_open_map_local_staging (session_id);
CREATE INDEX IF NOT EXISTS idx_os_open_map_local_staging_feature_code ON public.os_open_map_local_staging (feature_code);
CREATE INDEX IF NOT EXISTS idx_os_open_map_local_staging_geometry ON public.os_open_map_local_staging USING GIST (geometry); 