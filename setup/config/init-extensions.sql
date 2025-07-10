-- Initialize database extensions and optimizations
-- This script runs after the database is created

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS postgis_raster;
CREATE EXTENSION IF NOT EXISTS address_standardizer;
CREATE EXTENSION IF NOT EXISTS address_standardizer_data_us;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Create additional useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- Set up PostGIS spatial reference systems
-- Ensure we have the most common SRS for UK data
SELECT UpdateGeometrySRID('geometry_columns', 'geometry', 4326) WHERE EXISTS (
    SELECT 1 FROM geometry_columns WHERE f_table_name = 'geometry_columns'
);

-- Create a function to get PostGIS version info
CREATE OR REPLACE FUNCTION get_postgis_info()
RETURNS TABLE(extension text, version text) AS $$
BEGIN
    RETURN QUERY
    SELECT 'PostGIS'::text, PostGIS_Version()::text
    UNION ALL
    SELECT 'PostGIS Scripts'::text, PostGIS_Scripts_Version()::text
    UNION ALL
    SELECT 'PostGIS Lib'::text, PostGIS_Lib_Version()::text
    UNION ALL
    SELECT 'GEOS'::text, PostGIS_GEOS_Version()::text
    UNION ALL
    SELECT 'PROJ'::text, PostGIS_PROJ_Version()::text
    UNION ALL
    SELECT 'GDAL'::text, PostGIS_GDAL_Version()::text;
END;
$$ LANGUAGE plpgsql;

-- Create a function to check spatial data integrity
CREATE OR REPLACE FUNCTION check_spatial_integrity()
RETURNS TABLE(table_name text, column_name text, geometry_count bigint, invalid_count bigint) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f_table_name::text,
        f_geometry_column::text,
        COUNT(*)::bigint as geometry_count,
        COUNT(*) FILTER (WHERE NOT ST_IsValid(geometry))::bigint as invalid_count
    FROM geometry_columns gc
    JOIN information_schema.tables t ON t.table_name = gc.f_table_name
    WHERE t.table_schema = 'public'
    GROUP BY f_table_name, f_geometry_column;
END;
$$ LANGUAGE plpgsql;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'PostGIS extensions initialized successfully';
    RAISE NOTICE 'PostGIS Version: %', PostGIS_Version();
    RAISE NOTICE 'GEOS Version: %', PostGIS_GEOS_Version();
    RAISE NOTICE 'PROJ Version: %', PostGIS_PROJ_Version();
END $$; 