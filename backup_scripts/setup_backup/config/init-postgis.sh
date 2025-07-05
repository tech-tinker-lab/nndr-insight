#!/bin/bash
set -e

# Initialize PostGIS extensions and optimizations
echo "Initializing PostGIS extensions..."

# Create extensions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable PostGIS extensions
    CREATE EXTENSION IF NOT EXISTS postgis;
    CREATE EXTENSION IF NOT EXISTS postgis_topology;
    CREATE EXTENSION IF NOT EXISTS postgis_raster;
    CREATE EXTENSION IF NOT EXISTS address_standardizer;
    CREATE EXTENSION IF NOT EXISTS address_standardizer_data_us;
    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
    
    -- Performance optimizations
    ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
    ALTER SYSTEM SET max_connections = 200;
    ALTER SYSTEM SET shared_buffers = '256MB';
    ALTER SYSTEM SET effective_cache_size = '1GB';
    ALTER SYSTEM SET maintenance_work_mem = '64MB';
    ALTER SYSTEM SET checkpoint_completion_target = 0.9;
    ALTER SYSTEM SET wal_buffers = '16MB';
    ALTER SYSTEM SET default_statistics_target = 100;
    ALTER SYSTEM SET random_page_cost = 1.1;
    ALTER SYSTEM SET effective_io_concurrency = 200;
    ALTER SYSTEM SET work_mem = '4MB';
    ALTER SYSTEM SET min_wal_size = '1GB';
    ALTER SYSTEM SET max_wal_size = '4GB';
    
    -- PostGIS specific optimizations
    ALTER SYSTEM SET postgis.enable_outdb_rasters = true;
    ALTER SYSTEM SET postgis.gdal_enabled_drivers = 'ENABLE_ALL';
    
    -- Reload configuration
    SELECT pg_reload_conf();
EOSQL

echo "PostGIS initialization completed successfully!" 