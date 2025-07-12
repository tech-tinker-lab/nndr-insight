-- Drop Enhanced Design System Schemas
-- This script drops all enhanced design system schemas and related objects

-- Drop the enhanced design schema and all its objects
DROP SCHEMA IF EXISTS design_enhanced CASCADE;

-- Drop the original design schema and all its objects  
DROP SCHEMA IF EXISTS design CASCADE;

-- Drop the staging schema and all its objects
DROP SCHEMA IF EXISTS staging CASCADE;

-- Reset search path
SET search_path TO public; 