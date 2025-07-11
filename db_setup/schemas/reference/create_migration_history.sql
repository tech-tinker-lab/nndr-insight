CREATE TABLE IF NOT EXISTS migration_history (
    id SERIAL PRIMARY KEY,
    staging_table TEXT NOT NULL,
    master_table TEXT,
    migrated_by TEXT,
    filters JSONB,
    records_migrated INTEGER,
    final_master_count INTEGER,
    migration_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    status TEXT,
    error_message TEXT
); 