# OS Open Names Ingestion Comparison

## Overview

This document compares two approaches for ingesting OS Open Names data:
1. **Individual Fast Script** (`ingest_osopennames_fast.py`)
2. **Parallel Pipeline** (`enhanced_ingestion_pipeline.py`)

## Data Source

- **Location**: `backend/data/opname_csv_gb/Data/`
- **Format**: Multiple CSV files organized by grid squares (e.g., NR22.csv, NS00.csv, etc.)
- **Total Files**: ~400+ CSV files
- **Estimated Records**: Millions of place names across Great Britain

## Individual Fast Script Approach

### Features
- ✅ **Fast COPY Operations**: Uses PostgreSQL COPY for bulk insertion
- ✅ **Dynamic Schema**: Automatically detects and creates table with all CSV columns
- ✅ **No Staging**: Direct insertion into final table
- ✅ **Geometry Creation**: Automatically creates PostGIS geometry from coordinates
- ✅ **Batch Processing**: Processes all CSV files in sequence
- ✅ **Progress Tracking**: Shows progress for each file
- ✅ **Error Handling**: Continues processing if individual files fail
- ✅ **Memory Efficient**: Commits every 10 files to avoid long transactions

### Performance Characteristics
- **Speed**: Very fast due to COPY operations
- **Memory Usage**: Low - processes files sequentially
- **Disk Space**: Minimal - no staging tables
- **Error Recovery**: Good - continues on file errors

### Data Quality
- **Column Preservation**: Captures ALL columns from source CSV
- **Data Types**: Automatically maps to appropriate PostgreSQL types
- **Geometry**: Creates PostGIS geometry from X/Y coordinates
- **Validation**: Basic count and geometry validation

## Parallel Pipeline Approach

### Features
- ⚠️ **Staging Tables**: Uses intermediate staging for data validation
- ⚠️ **Complex Processing**: Multiple validation and transformation steps
- ⚠️ **Deduplication**: Checks for duplicates during insertion
- ⚠️ **Schema Validation**: Validates against predefined schema
- ⚠️ **Error Logging**: Comprehensive error tracking
- ⚠️ **Data Quality Checks**: Multiple validation layers

### Performance Characteristics
- **Speed**: Slower due to staging and validation overhead
- **Memory Usage**: Higher - maintains staging data
- **Disk Space**: Higher - requires staging tables
- **Error Recovery**: Excellent - detailed error reporting

### Data Quality
- **Column Validation**: Validates against expected schema
- **Data Types**: Strict type checking and conversion
- **Geometry**: Validates coordinate data before geometry creation
- **Validation**: Comprehensive quality checks

## Key Differences

| Aspect | Individual Fast Script | Parallel Pipeline |
|--------|----------------------|-------------------|
| **Speed** | ⭐⭐⭐⭐⭐ Very Fast | ⭐⭐⭐ Moderate |
| **Data Quality** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| **Error Handling** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| **Memory Usage** | ⭐⭐⭐⭐⭐ Low | ⭐⭐⭐ Moderate |
| **Disk Usage** | ⭐⭐⭐⭐⭐ Low | ⭐⭐⭐ Moderate |
| **Maintenance** | ⭐⭐⭐⭐⭐ Simple | ⭐⭐⭐ Complex |
| **Flexibility** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |

## Column Handling Comparison

### Individual Fast Script
```sql
-- Dynamically creates table with all CSV columns
CREATE TABLE os_open_names (
    "os_id" TEXT,
    "names_uri" TEXT,
    "name1" TEXT,
    "name1_lang" TEXT,
    "name2" TEXT,
    "name2_lang" TEXT,
    "type" TEXT,
    "local_type" TEXT,
    "geometry_x" NUMERIC,
    "geometry_y" NUMERIC,
    "most_detail_view_res" INTEGER,
    "least_detail_view_res" INTEGER,
    "mbr_xmin" NUMERIC,
    "mbr_ymin" NUMERIC,
    "mbr_xmax" NUMERIC,
    "mbr_ymax" NUMERIC,
    "postcode_district" TEXT,
    "postcode_district_uri" TEXT,
    "populated_place" TEXT,
    "populated_place_uri" TEXT,
    "populated_place_type" TEXT,
    "district_borough" TEXT,
    "district_borough_uri" TEXT,
    "district_borough_type" TEXT,
    "county_unitary" TEXT,
    "county_unitary_uri" TEXT,
    "county_unitary_type" TEXT,
    "region" TEXT,
    "region_uri" TEXT,
    "country" TEXT,
    "country_uri" TEXT,
    "related_spatial_object" TEXT,
    "same_as_dbpedia" TEXT,
    "same_as_geonames" TEXT,
    geom GEOMETRY(POINT, 27700)
);
```

### Parallel Pipeline
```sql
-- Uses predefined schema with validation
CREATE TABLE os_open_names (
    os_id TEXT PRIMARY KEY,
    names_uri TEXT,
    name1 TEXT,
    name1_lang TEXT,
    name2 TEXT,
    name2_lang TEXT,
    type TEXT,
    local_type TEXT,
    geometry_x NUMERIC,
    geometry_y NUMERIC,
    most_detail_view_res INTEGER,
    least_detail_view_res INTEGER,
    mbr_xmin NUMERIC,
    mbr_ymin NUMERIC,
    mbr_xmax NUMERIC,
    mbr_ymax NUMERIC,
    postcode_district TEXT,
    postcode_district_uri TEXT,
    populated_place TEXT,
    populated_place_uri TEXT,
    populated_place_type TEXT,
    district_borough TEXT,
    district_borough_uri TEXT,
    district_borough_type TEXT,
    county_unitary TEXT,
    county_unitary_uri TEXT,
    county_unitary_type TEXT,
    region TEXT,
    region_uri TEXT,
    country TEXT,
    country_uri TEXT,
    related_spatial_object TEXT,
    same_as_dbpedia TEXT,
    same_as_geonames TEXT,
    geom GEOMETRY(POINT, 27700)
);
```

## Recommendations

### Use Individual Fast Script When:
- ✅ **Speed is priority** - Need to process large datasets quickly
- ✅ **Simple requirements** - Basic data loading without complex validation
- ✅ **Resource constraints** - Limited memory or disk space
- ✅ **Initial data load** - First-time loading of reference data
- ✅ **Batch processing** - Processing all files at once

### Use Parallel Pipeline When:
- ✅ **Data quality is critical** - Need comprehensive validation
- ✅ **Complex transformations** - Require data cleaning and enrichment
- ✅ **Production environment** - Need robust error handling
- ✅ **Incremental updates** - Regular data updates with validation
- ✅ **Integration requirements** - Need to integrate with other systems

## Current Status

**Recommendation**: Use the **Individual Fast Script** for OS Open Names data

**Reasoning**:
1. **Large Dataset**: OS Open Names contains millions of records across hundreds of files
2. **Reference Data**: This is reference data that doesn't require complex validation
3. **Speed Priority**: Fast ingestion is more important than extensive validation
4. **Simple Structure**: The data structure is relatively clean and consistent

## Implementation

The fast script has been created and is ready for use:
- **Script**: `setup/scripts/ingest_osopennames_fast.py`
- **Batch File**: `setup/scripts/run_osopennames_fast.bat`
- **Data Source**: `backend/data/opname_csv_gb/Data/`

## Next Steps

1. **Run the fast ingestion script** to load OS Open Names data
2. **Verify data quality** after ingestion
3. **Update file monitor configuration** to use the fast script
4. **Proceed to next dataset** (OS Open Map Local or LAD Boundaries) 