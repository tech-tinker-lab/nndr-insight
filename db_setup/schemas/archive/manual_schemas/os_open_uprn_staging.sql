-- public.os_open_uprn_staging definition

CREATE TABLE IF NOT EXISTS public.os_open_uprn_staging (
    id SERIAL PRIMARY KEY,
    uprn TEXT,
    x_coordinate TEXT,
    y_coordinate TEXT,
    latitude TEXT,
    longitude TEXT,
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

CREATE INDEX IF NOT EXISTS idx_os_open_uprn_staging_batch ON public.os_open_uprn_staging (batch_id);
CREATE INDEX IF NOT EXISTS idx_os_open_uprn_staging_session ON public.os_open_uprn_staging (session_id);
CREATE INDEX IF NOT EXISTS idx_os_open_uprn_staging_upload_time ON public.os_open_uprn_staging (upload_timestamp); 