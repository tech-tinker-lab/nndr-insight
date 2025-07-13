-- Drop lad_boundaries_staging table
-- This script will completely remove the lad_boundaries_staging table and all its data

DROP TABLE IF EXISTS public.lad_boundaries_staging CASCADE;

-- Verify the table has been dropped
DO $$
BEGIN
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'lad_boundaries_staging'
    ) THEN
        RAISE NOTICE 'Table lad_boundaries_staging still exists after drop attempt';
    ELSE
        RAISE NOTICE 'Table lad_boundaries_staging successfully dropped';
    END IF;
END $$; 