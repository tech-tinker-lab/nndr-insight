-- Example Queries for Filtering, Visualization, and Source Management

-- 1. Filter properties by data source
SELECT * FROM master_gazetteer WHERE data_source = 'voa_2023';

-- 2. Show all duplicate groups with more than one record
SELECT duplicate_group_id, COUNT(*) as num_records
FROM master_gazetteer
WHERE duplicate_group_id IS NOT NULL
GROUP BY duplicate_group_id
HAVING COUNT(*) > 1;

-- 3. Show preferred record for each duplicate group
SELECT * FROM master_gazetteer WHERE is_preferred_record = TRUE;

-- 4. Show properties with low data quality score
SELECT * FROM master_gazetteer WHERE source_confidence_score < 0.7;

-- 5. List all active data sources
SELECT * FROM data_sources WHERE is_active = TRUE;

-- 6. Show merge history for a property
SELECT * FROM duplicate_management WHERE property_id = <PROPERTY_ID> ORDER BY merge_date DESC;

-- 7. Count properties by source and confidence
SELECT data_source, COUNT(*), AVG(source_confidence_score)
FROM master_gazetteer
GROUP BY data_source;

-- 8. Find properties updated in the last 30 days
SELECT * FROM master_gazetteer WHERE last_source_update > NOW() - INTERVAL '30 days'; 