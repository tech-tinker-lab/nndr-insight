# NNDR Data Ingestion: Individual Scripts vs. Parallel Pipeline

This document summarizes and compares the ingestion logic, table mappings, and data flow for the main individual ingestion scripts and the comprehensive parallel pipeline in the NNDR Insight system.

---

## 1. Individual Ingestion Scripts

### 1.1 `ingest_gazetteer.py`
- **Target Table:** `gazetteer_staging`
- **Source:** OS Open UPRN CSV
- **Logic:**
  - Loads UPRN, x/y coordinates, latitude, longitude from CSV into `gazetteer_staging` using PostgreSQL `COPY`.
  - Truncates the staging table before load.
  - No deduplication or transformation beyond column mapping.

### 1.2 `ingest_nndr_properties.py`
- **Target Table:** `properties`
- **Source:** NNDR Rating List CSV
- **Logic:**
  - Creates the `properties` table if it does not exist.
  - Reads and cleans each row, mapping fields to columns (e.g., BA Reference, address, category, value, etc.).
  - Inserts in batches using `COPY` or individual inserts on failure.
  - Skips rows without a BA Reference.
  - No parallelism or duplicate detection.

### 1.3 `ingest_usrn.py`
- **Target Table:** `usrn_streets`
- **Source:** OS Open USRN GeoPackage
- **Logic:**
  - Loads features from a GeoPackage layer into PostGIS using GeoPandas.
  - Writes in chunks, logs progress, skips invalid geometries.
  - Table and column mapping is direct from GeoPackage fields.

### 1.4 `ingest_onspd.py`
- **Target Table:** `onspd` (via `onspd_staging`)
- **Source:** ONS Postcode Directory CSV
- **Logic:**
  - Loads CSV into `onspd_staging` using `COPY`.
  - Upserts distinct records into `onspd` with deduplication on `pcds`.
  - Updates all columns on conflict.

### 1.5 `ingest_valuations.py`
- **Target Table:** `valuations`
- **Source:** Valuations CSV (custom or VOA format)
- **Logic:**
  - Maps BA Reference to property ID using the `properties` table.
  - Inserts valuation records (property_id, effective_date, rateable_value, etc.) in batches.
  - Skips rows with missing or unmatched BA Reference.
  - Handles both custom and VOA formats with field mapping.

---

## 2. Parallel Pipeline (`comprehensive_ingestion_pipeline.py`)

- **Entry Point:** `run_pipeline.py`
- **Parallelism:** Uses ThreadPoolExecutor to process multiple sources/files concurrently.
- **Source Config:** Each data source (NNDR, reference, etc.) is defined with file pattern, type, and processor method.
- **Target Tables:**
  - **NNDR Data:** Inserted into `master_gazetteer` (with enhanced schema, duplicate detection, and source tracking).
  - **Reference Data:** Inserted into specific tables:
    - `os_uprn` → `os_open_uprn`
    - `codepoint` → `code_point_open`
    - `onspd` → `onspd`
    - `os_open_names` → `os_open_names`
    - `os_open_usrn` → `os_open_usrn`
    - `lad_boundaries` → `lad_boundaries`
    - `os_open_map_local` → `os_open_map_local`
- **Logic:**
  - For each file, applies the appropriate processor (custom logic for each source type).
  - Aligns DataFrame columns to match the target table schema.
  - Bulk inserts data, disables/re-enables indexes for performance.
  - Detects and marks duplicates (for NNDR data).
  - Logs summary statistics.

---

## 3. Comparison Table

| Data Source         | Individual Script Target Table(s) | Parallel Pipeline Target Table |
|--------------------|------------------------------------|-------------------------------|
| OS Open UPRN       | gazetteer_staging                  | os_open_uprn                  |
| NNDR Properties    | properties                         | master_gazetteer              |
| OS Open USRN       | usrn_streets                       | os_open_usrn                  |
| ONSPD              | onspd (via onspd_staging)          | onspd                         |
| CodePoint Open     | (not in main scripts)              | code_point_open               |
| OS Open Names      | (not in main scripts)              | os_open_names                 |
| LAD Boundaries     | (not in main scripts)              | lad_boundaries                |
| OS Open Map Local  | (not in main scripts)              | os_open_map_local             |
| Valuations         | valuations                         | (not handled in pipeline)     |

---

## 4. Key Differences

- **Coverage:**
  - Individual scripts cover only a subset of reference data (mainly UPRN, USRN, ONSPD, NNDR, Valuations).
  - Parallel pipeline covers all configured reference sources and NNDR data, but not valuations.
- **Schema Alignment:**
  - Individual scripts use direct field mapping or staging tables, sometimes requiring manual post-processing.
  - Pipeline auto-aligns columns to match the target table schema for each reference source.
- **Performance:**
  - Pipeline uses parallel processing and bulk insert optimizations.
  - Individual scripts are single-threaded and may be slower for large datasets.
- **Deduplication:**
  - Only the pipeline includes duplicate detection and marking (for NNDR data).
- **Extensibility:**
  - Pipeline is easily extensible for new sources by adding to the config and implementing a processor.
  - Individual scripts require new scripts for each new source.

---

## 5. Recommendations

- Use the parallel pipeline for comprehensive, repeatable, and high-performance ingestion of all reference and NNDR data.
- Use individual scripts for targeted, manual loads or for sources not yet supported in the pipeline (e.g., valuations).
- Consider extending the pipeline to handle valuations and any other custom sources for full automation. 