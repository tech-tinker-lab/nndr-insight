-- Performance Tuning Script for NNDR Database
-- Run this after the container is up and running
-- Connect as superuser (postgres) to apply these settings

-- =====================================================
-- MEMORY SETTINGS
-- =====================================================

-- Set shared buffers (25% of available RAM, max 8GB)
ALTER SYSTEM SET shared_buffers = '2GB';

-- Set effective cache size (75% of available RAM)
ALTER SYSTEM SET effective_cache_size = '6GB';

-- Set work memory for complex operations
ALTER SYSTEM SET work_mem = '64MB';

-- Set maintenance work memory for maintenance operations
ALTER SYSTEM SET maintenance_work_mem = '512MB';

-- =====================================================
-- WAL (Write-Ahead Logging) SETTINGS
-- =====================================================

-- Set WAL buffer size
ALTER SYSTEM SET wal_buffers = '16MB';

-- Set checkpoint segments (deprecated in newer versions, using checkpoint_completion_target instead)
ALTER SYSTEM SET checkpoint_completion_target = '0.9';

-- Set WAL file size (16MB default, can be increased for better performance)
ALTER SYSTEM SET max_wal_size = '2GB';
ALTER SYSTEM SET min_wal_size = '80MB';

-- =====================================================
-- CONNECTION AND CONCURRENCY SETTINGS
-- =====================================================

-- Set maximum connections
ALTER SYSTEM SET max_connections = '200';

-- Set default transaction isolation level
ALTER SYSTEM SET default_transaction_isolation = 'read committed';

-- Set statement timeout (prevent long-running queries)
ALTER SYSTEM SET statement_timeout = '300000'; -- 5 minutes

-- Set idle transaction timeout
ALTER SYSTEM SET idle_in_transaction_session_timeout = '600000'; -- 10 minutes

-- =====================================================
-- QUERY PLANNER SETTINGS
-- =====================================================

-- Set random page cost (lower for SSDs)
ALTER SYSTEM SET random_page_cost = '1.1';

-- Set effective io concurrency (higher for SSDs)
ALTER SYSTEM SET effective_io_concurrency = '200';

-- Set seq page cost
ALTER SYSTEM SET seq_page_cost = '1.0';

-- Set cpu tuple cost
ALTER SYSTEM SET cpu_tuple_cost = '0.01';

-- Set cpu index tuple cost
ALTER SYSTEM SET cpu_index_tuple_cost = '0.005';

-- Set cpu operator cost
ALTER SYSTEM SET cpu_operator_cost = '0.0025';

-- =====================================================
-- LOGGING AND MONITORING
-- =====================================================

-- Enable query logging for slow queries (>1 second)
ALTER SYSTEM SET log_min_duration_statement = '1000';

-- Enable logging of connections and disconnections
ALTER SYSTEM SET log_connections = 'on';
ALTER SYSTEM SET log_disconnections = 'on';

-- Set log destination
ALTER SYSTEM SET log_destination = 'stderr';

-- Set logging format
ALTER SYSTEM SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';

-- =====================================================
-- AUTOVACUUM SETTINGS
-- =====================================================

-- Enable autovacuum
ALTER SYSTEM SET autovacuum = 'on';

-- Set autovacuum max workers
ALTER SYSTEM SET autovacuum_max_workers = '3';

-- Set autovacuum naptime
ALTER SYSTEM SET autovacuum_naptime = '60';

-- Set autovacuum vacuum threshold
ALTER SYSTEM SET autovacuum_vacuum_threshold = '50';

-- Set autovacuum analyze threshold
ALTER SYSTEM SET autovacuum_analyze_threshold = '50';

-- Set autovacuum vacuum scale factor
ALTER SYSTEM SET autovacuum_vacuum_scale_factor = '0.2';

-- Set autovacuum analyze scale factor
ALTER SYSTEM SET autovacuum_analyze_scale_factor = '0.1';

-- =====================================================
-- STATISTICS SETTINGS
-- =====================================================

-- Set default statistics target
ALTER SYSTEM SET default_statistics_target = '100';

-- Enable track activities
ALTER SYSTEM SET track_activities = 'on';

-- Enable track counts
ALTER SYSTEM SET track_counts = 'on';

-- Enable track io timing
ALTER SYSTEM SET track_io_timing = 'on';

-- =====================================================
-- POSTGIS SPECIFIC SETTINGS
-- =====================================================

-- Set PostGIS raster settings
ALTER SYSTEM SET postgis.gdal_enabled_drivers = 'ENABLE_ALL';

-- Set PostGIS outdb rasters
ALTER SYSTEM SET postgis.enable_outdb_rasters = 'on';

-- =====================================================
-- APPLY SETTINGS
-- =====================================================

-- Reload configuration (doesn't require restart)
SELECT pg_reload_conf();

-- Display current settings for verification
SELECT name, setting, unit, context, category 
FROM pg_settings 
WHERE name IN (
    'shared_buffers', 'effective_cache_size', 'work_mem', 'maintenance_work_mem',
    'wal_buffers', 'max_wal_size', 'checkpoint_completion_target',
    'max_connections', 'random_page_cost', 'effective_io_concurrency',
    'autovacuum', 'default_statistics_target'
)
ORDER BY category, name;

-- =====================================================
-- CREATE USEFUL INDEXES FOR NNDR DATA
-- =====================================================

-- Note: These should be run after your tables are created
-- Uncomment and modify as needed for your specific schema

/*
-- Example indexes for NNDR data (modify table names as needed)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_location ON properties USING GIST (location);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_postcode ON properties (postcode);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_rateable_value ON properties (rateable_value);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_business_type ON properties (business_type);

-- Composite indexes for common queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_postcode_value ON properties (postcode, rateable_value);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_type_value ON properties (business_type, rateable_value);

-- Full text search index for property descriptions
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_description_fts ON properties USING GIN (to_tsvector('english', description));
*/ 