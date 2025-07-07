# Reference Data Linking Guide

## Overview

This guide explains how to link and query the various OS reference datasets to create rich, interconnected spatial data. The reference datasets can be linked using both spatial relationships (proximity) and attribute relationships (direct matches).

## Available Reference Datasets

| Dataset | Records | Primary Key | Spatial Data | Description |
|---------|---------|-------------|--------------|-------------|
| **OS Open UPRN** | 41,230,108 | `uprn` | ✅ | Unique Property Reference Numbers |
| **CodePoint Open** | 1,743,449 | `postcode` | ✅ | Postcode centroids |
| **ONSPD** | 2,714,964 | `pcds` | ❌ | Postcode details & admin areas |
| **OS Open Names** | 3,033,655 | `ID` | ✅ | Place names and locations |
| **OS Open Map Local** | X | `fid` | ✅ | Map features (buildings, roads, etc.) |

## Linking Strategies

### 1. Spatial Linking (Distance-Based)
Use geographic proximity to link datasets that don't have direct attribute relationships.

### 2. Attribute Linking (Direct Match)
Use common identifiers to directly join datasets.

### 3. Hybrid Linking
Combine spatial and attribute relationships for comprehensive data enrichment.

---

## 1. UPRN-Based Queries

### Get Postcode for a UPRN
```sql
-- Find the nearest postcode to a UPRN (within 1km)
SELECT 
    uprn.uprn,
    cp.postcode,
    ST_Distance(uprn.geom, cp.geom) as distance_meters
FROM os_open_uprn uprn
CROSS JOIN LATERAL (
    SELECT postcode, geom
    FROM codepoint_open
    WHERE geom IS NOT NULL
    ORDER BY uprn.geom <-> geom
    LIMIT 1
) cp
WHERE uprn.uprn = '123456789'
AND ST_Distance(uprn.geom, cp.geom) <= 1000;
```

### Get Place Names Near a UPRN
```sql
-- Find place names within 5km of a UPRN
SELECT 
    uprn.uprn,
    names."NAME1" as place_name,
    names."TYPE" as place_type,
    ST_Distance(uprn.geom, names.geom) as distance_meters
FROM os_open_uprn uprn
JOIN os_open_names names ON ST_DWithin(uprn.geom, names.geom, 5000)
WHERE uprn.uprn = '123456789'
AND names."TYPE" IN ('Named Place', 'City', 'Town', 'Village')
ORDER BY ST_Distance(uprn.geom, names.geom)
LIMIT 5;
```

### Get Map Features Near a UPRN
```sql
-- Find map features within 100m of a UPRN
SELECT 
    uprn.uprn,
    map.feature_code,
    map.gml_id,
    ST_Distance(uprn.geom, map.geom) as distance_meters
FROM os_open_uprn uprn
JOIN os_open_map_local map ON ST_DWithin(uprn.geom, map.geom, 100)
WHERE uprn.uprn = '123456789'
ORDER BY ST_Distance(uprn.geom, map.geom)
LIMIT 10;
```

---

## 2. Postcode-Based Queries

### Get UPRNs for a Postcode
```sql
-- Find all UPRNs within 1km of a postcode centroid
SELECT 
    uprn.uprn,
    ST_Distance(uprn.geom, cp.geom) as distance_meters
FROM codepoint_open cp
JOIN os_open_uprn uprn ON ST_DWithin(cp.geom, uprn.geom, 1000)
WHERE cp.postcode = 'SW1A 1AA'
ORDER BY ST_Distance(uprn.geom, cp.geom);
```

### Get Place Names Near a Postcode
```sql
-- Find place names within 5km of a postcode
SELECT 
    cp.postcode,
    names."NAME1" as place_name,
    names."TYPE" as place_type,
    ST_Distance(cp.geom, names.geom) as distance_meters
FROM codepoint_open cp
JOIN os_open_names names ON ST_DWithin(cp.geom, names.geom, 5000)
WHERE cp.postcode = 'SW1A 1AA'
AND names."TYPE" IN ('Named Place', 'City', 'Town', 'Village')
ORDER BY ST_Distance(cp.geom, names.geom)
LIMIT 10;
```

### Get Administrative Areas for a Postcode
```sql
-- Get full administrative hierarchy for a postcode
SELECT 
    cp.postcode,
    ons.launm as local_authority,
    ons.ctynm as county,
    ons.rgnnm as region,
    ons.ctrynm as country
FROM codepoint_open cp
JOIN onspd ons ON cp.postcode = ons.pcds
WHERE cp.postcode = 'SW1A 1AA';
```

---

## 3. Place Name-Based Queries

### Get UPRNs Near a Place Name
```sql
-- Find UPRNs within 2km of a specific place
SELECT 
    names."NAME1" as place_name,
    uprn.uprn,
    ST_Distance(names.geom, uprn.geom) as distance_meters
FROM os_open_names names
JOIN os_open_uprn uprn ON ST_DWithin(names.geom, uprn.geom, 2000)
WHERE names."NAME1" ILIKE '%London%'
AND names."TYPE" = 'Named Place'
ORDER BY ST_Distance(names.geom, uprn.geom)
LIMIT 100;
```

### Get Postcodes Near a Place Name
```sql
-- Find postcodes within 3km of a place
SELECT 
    names."NAME1" as place_name,
    cp.postcode,
    ST_Distance(names.geom, cp.geom) as distance_meters
FROM os_open_names names
JOIN codepoint_open cp ON ST_DWithin(names.geom, cp.geom, 3000)
WHERE names."NAME1" ILIKE '%Manchester%'
AND names."TYPE" = 'City'
ORDER BY ST_Distance(names.geom, cp.geom);
```

---

## 4. Administrative Area Queries

### Get All UPRNs in a Local Authority
```sql
-- Find UPRNs in a specific local authority (via postcode)
SELECT 
    uprn.uprn,
    cp.postcode,
    ons.launm as local_authority
FROM os_open_uprn uprn
JOIN codepoint_open cp ON ST_DWithin(uprn.geom, cp.geom, 1000)
JOIN onspd ons ON cp.postcode = ons.pcds
WHERE ons.launm = 'Westminster'
LIMIT 1000;
```

### Get Place Names in a County
```sql
-- Find place names in a specific county
SELECT 
    names."NAME1" as place_name,
    names."TYPE" as place_type,
    ons.ctynm as county
FROM os_open_names names
JOIN codepoint_open cp ON ST_DWithin(names.geom, cp.geom, 1000)
JOIN onspd ons ON cp.postcode = ons.pcds
WHERE ons.ctynm = 'Greater London'
AND names."TYPE" IN ('City', 'Town', 'Village')
ORDER BY names."NAME1";
```

---

## 5. Map Feature-Based Queries

### Get UPRNs Near Specific Map Features
```sql
-- Find UPRNs near buildings (feature_code = 15014)
SELECT 
    uprn.uprn,
    map.feature_code,
    ST_Distance(uprn.geom, map.geom) as distance_meters
FROM os_open_map_local map
JOIN os_open_uprn uprn ON ST_DWithin(map.geom, uprn.geom, 50)
WHERE map.feature_code = 15014
LIMIT 100;
```

### Get Place Names Near Map Features
```sql
-- Find place names near specific map features
SELECT 
    names."NAME1" as place_name,
    map.feature_code,
    ST_Distance(names.geom, map.geom) as distance_meters
FROM os_open_map_local map
JOIN os_open_names names ON ST_DWithin(map.geom, names.geom, 500)
WHERE map.feature_code = 15014  -- Buildings
AND names."TYPE" = 'Named Place'
ORDER BY ST_Distance(names.geom, map.geom);
```

---

## 6. Complex Multi-Dataset Queries

### Complete Property Context
```sql
-- Get comprehensive information for a UPRN
SELECT 
    uprn.uprn,
    cp.postcode,
    ons.launm as local_authority,
    ons.ctynm as county,
    ons.rgnnm as region,
    nearest_place.place_name,
    nearest_place.place_type,
    nearest_place.distance as place_distance,
    nearest_feature.feature_code,
    nearest_feature.distance as feature_distance
FROM os_open_uprn uprn
-- Get nearest postcode
LEFT JOIN LATERAL (
    SELECT postcode, geom
    FROM codepoint_open
    WHERE geom IS NOT NULL
    ORDER BY uprn.geom <-> geom
    LIMIT 1
) cp ON ST_Distance(uprn.geom, cp.geom) <= 1000
-- Get administrative data
LEFT JOIN onspd ons ON cp.postcode = ons.pcds
-- Get nearest place name
LEFT JOIN LATERAL (
    SELECT "NAME1" as place_name, "TYPE" as place_type, geom,
           ST_Distance(uprn.geom, geom) as distance
    FROM os_open_names
    WHERE geom IS NOT NULL
    AND "TYPE" IN ('Named Place', 'City', 'Town', 'Village')
    ORDER BY uprn.geom <-> geom
    LIMIT 1
) nearest_place ON nearest_place.distance <= 5000
-- Get nearest map feature
LEFT JOIN LATERAL (
    SELECT feature_code, geom,
           ST_Distance(uprn.geom, geom) as distance
    FROM os_open_map_local
    WHERE geom IS NOT NULL
    ORDER BY uprn.geom <-> geom
    LIMIT 1
) nearest_feature ON nearest_feature.distance <= 100
WHERE uprn.uprn = '123456789';
```

### Area Analysis
```sql
-- Analyze all properties in a specific area
SELECT 
    ons.launm as local_authority,
    COUNT(DISTINCT uprn.uprn) as total_properties,
    COUNT(DISTINCT cp.postcode) as unique_postcodes,
    COUNT(DISTINCT names."ID") as nearby_places,
    AVG(ST_Distance(uprn.geom, cp.geom)) as avg_postcode_distance
FROM os_open_uprn uprn
JOIN codepoint_open cp ON ST_DWithin(uprn.geom, cp.geom, 1000)
JOIN onspd ons ON cp.postcode = ons.pcds
LEFT JOIN os_open_names names ON ST_DWithin(uprn.geom, names.geom, 2000)
WHERE ons.launm = 'Westminster'
GROUP BY ons.launm;
```

---

## 7. Performance Optimization Tips

### Use Spatial Indexes
```sql
-- Ensure spatial indexes exist
CREATE INDEX IF NOT EXISTS idx_uprn_geom ON os_open_uprn USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_codepoint_geom ON codepoint_open USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_names_geom ON os_open_names USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_map_geom ON os_open_map_local USING GIST (geom);
```

### Limit Distance Searches
- UPRN ↔ Postcode: 1km max
- UPRN ↔ Place Names: 5km max  
- UPRN ↔ Map Features: 100m max
- Postcode ↔ Place Names: 3km max

### Use LATERAL Joins for Nearest Neighbor
```sql
-- More efficient than ORDER BY + LIMIT
SELECT uprn.uprn, cp.postcode
FROM os_open_uprn uprn
CROSS JOIN LATERAL (
    SELECT postcode
    FROM codepoint_open
    WHERE geom IS NOT NULL
    ORDER BY uprn.geom <-> geom
    LIMIT 1
) cp;
```

---

## 8. Common Use Cases

### Property Search
```sql
-- Find properties by postcode
SELECT uprn, ST_AsText(geom) as coordinates
FROM os_open_uprn uprn
JOIN codepoint_open cp ON ST_DWithin(uprn.geom, cp.geom, 1000)
WHERE cp.postcode = 'SW1A 1AA';
```

### Geographic Analysis
```sql
-- Count properties by administrative area
SELECT ons.launm, COUNT(*) as property_count
FROM os_open_uprn uprn
JOIN codepoint_open cp ON ST_DWithin(uprn.geom, cp.geom, 1000)
JOIN onspd ons ON cp.postcode = ons.pcds
GROUP BY ons.launm
ORDER BY property_count DESC;
```

### Spatial Clustering
```sql
-- Find property clusters near place names
SELECT 
    names."NAME1",
    COUNT(uprn.uprn) as nearby_properties,
    ST_Buffer(names.geom, 1000) as area_of_interest
FROM os_open_names names
JOIN os_open_uprn uprn ON ST_DWithin(names.geom, uprn.geom, 1000)
WHERE names."TYPE" = 'City'
GROUP BY names."ID", names."NAME1", names.geom
HAVING COUNT(uprn.uprn) > 100;
```

---

## 9. Data Quality Considerations

### Handle Missing Data
```sql
-- Check for UPRNs without nearby postcodes
SELECT COUNT(*) as uprns_without_postcodes
FROM os_open_uprn uprn
WHERE NOT EXISTS (
    SELECT 1 FROM codepoint_open cp 
    WHERE ST_DWithin(uprn.geom, cp.geom, 1000)
);
```

### Validate Spatial Relationships
```sql
-- Check for unreasonable distances
SELECT 
    uprn.uprn,
    cp.postcode,
    ST_Distance(uprn.geom, cp.geom) as distance
FROM os_open_uprn uprn
JOIN codepoint_open cp ON ST_DWithin(uprn.geom, cp.geom, 1000)
WHERE ST_Distance(uprn.geom, cp.geom) > 500  -- Flag suspicious distances
ORDER BY distance DESC;
```

---

## 10. Summary

This linking guide provides the foundation for creating rich, interconnected spatial queries across all OS reference datasets. The key is to:

1. **Use UPRN as the central reference point** for property-level analysis
2. **Leverage postcodes for administrative area linking**
3. **Apply appropriate distance thresholds** for spatial relationships
4. **Use spatial indexes** for performance optimization
5. **Validate data quality** through distance checks and completeness analysis

By following these patterns, you can build comprehensive spatial queries that combine the strengths of all reference datasets for powerful geographic analysis and property intelligence. 