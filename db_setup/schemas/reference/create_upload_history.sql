CREATE TABLE IF NOT EXISTS upload_history (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    staging_table TEXT NOT NULL,
    uploaded_by TEXT NOT NULL,
    file_size BIGINT,
    upload_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'uploaded',
    error_message TEXT,
    file_path TEXT
); 