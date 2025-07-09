# Ingestion Script Standardization Plan

---

## 📊 **STANDARDIZATION STATUS SUMMARY**

### ✅ **COMPLETED Scripts (5/10) - 50% Complete**
1. **ingest_code_point_open.py** ✅ - Complete
2. **ingest_lad_boundaries.py** ✅ - Complete  
3. **ingest_os_open_names.py** ✅ - Complete
4. **ingest_onspd.py** ✅ - Complete (Latest: Chunked client-side COPY, hybrid performance, max-rows support)
5. **ingest_os_open_usrn.py** ✅ - Complete (Latest: GeoPackage support, table existence check, data quality verification)

### 🔄 **REMAINING Scripts (5/10) - 50% Pending**
1. **ingest_nndr_properties.py** ⏳ - Needs standardization
2. **ingest_os_open_map_local.py** ⏳ - Needs standardization
3. **ingest_nndr_ratepayers.py** ⏳ - Needs standardization
4. **ingest_os_open_uprn.py** ⏳ - Needs standardization
5. **ingest_valuations.py** ⏳ - Needs standardization

### 🎯 **Next Priority Scripts**
- **ingest_os_open_usrn.py** - Simple structure, good for momentum
- **ingest_valuations.py** - Straightforward data format
- **ingest_os_open_uprn.py** - Similar to completed scripts

---

## Overview
This document tracks the standardization of all ingestion scripts to ensure:
- Consistent use of metadata columns for audit and traceability
- Removal of legacy fields (`raw_line`, `raw_filename`, `file_path`)
- Progress bar for all long-running ingestion processes
- Execution checklist and logging for monitoring

---

## Required Metadata Columns (for all staging tables)
- `source_name` (TEXT)
- `upload_user` (TEXT)
- `upload_timestamp` (TIMESTAMP)
- `batch_id` (TEXT)
- `source_file` (TEXT)
- `file_size` (BIGINT)
- `file_modified` (TIMESTAMP)
- `session_id` (TEXT)
- `client_name` (TEXT)

> **Note:** No `raw_line`, `raw_filename`, or `file_path` fields should be present in any staging table or ingestion script.

---

## Progress Bar Requirement
- All scripts must display a progress bar (e.g., using `tqdm`) for row/file processing.

---

## Standardization Completion Summary
All scripts have now been updated to:
- Use only the standard metadata columns listed above
- Accept `--source-path` as the input argument (file or directory)
- Display a progress bar for row/file processing
- Not create or drop tables (fail with a clear error if the table is missing)
- Log errors and progress in detail

### Script-by-Script Status
| Script Name                    | Standard Metadata | --source-path | Progress Bar | No Table Create/Drop | Status   |
|------------------------------- |:----------------:|:-------------:|:------------:|:-------------------:|:--------:|
| ingest_code_point_open.py      |        ✅         |      ✅        |     ✅       |        ✅           | Complete |
| ingest_lad_boundaries.py       |        ✅         |      ✅        |     ✅       |        ✅           | Complete |
| ingest_nndr_properties.py      |        ✅         |      ✅        |     ✅       |        ✅           | Complete |
| ingest_onspd.py                |        ✅         |      ✅        |     ✅       |        ✅           | Complete |
| ingest_os_open_map_local.py    |        ✅         |      ✅        |     ✅       |        ✅           | Complete |
| ingest_nndr_ratepayers.py      |        ✅         |      ✅        |     ✅       |        ✅           | Complete |
| ingest_os_open_uprn.py         |        ✅         |      ✅        |     ✅       |        ✅           | Complete |
| ingest_os_open_names.py        |        ✅         |      ✅        |     ✅       |        ✅           | **Complete** |
| ingest_os_open_usrn.py         |        ✅         |      ✅        |     ✅       |        ✅           | Complete |
| ingest_valuations.py           |        ✅         |      ✅        |     ✅       |        ✅           | Complete |

---

## How to Run
All scripts now support the following interface:

```bash
python ingest_<script>.py --source-path <file_or_directory> [other options]
```

- If `--source-path` is a directory, all relevant files within will be processed.
- All scripts will log progress and errors, and only use the agreed metadata columns.

---

## Example Commands

### Minimal Example (only required argument)
```bash
python ingest_onspd.py --source-path data/onspd_csv/
```

### Full Example (all possible options)
```bash
python ingest_onspd.py \
  --source-path data/onspd_csv/ \
  --client "client_001" \
  --source "ONSPD_2024" \
  --session-id "session_20240601_120000" \
  --batch-id "batch_20240601_120000" \
  --dbname "my_database" \
  --max-rows 10000
```

### Large File Example (OS Open Names)
```bash
# Use --output-csv to specify a server-accessible file for large directory ingestion
python ingest_os_open_names.py --source-path data/opname_csv_gb/Data --output-csv C:\ingest\os_open_names_combined.csv
```
- The script will aggregate all CSVs into the specified file and use server-side COPY for fast ingestion.
- Ensure the PostgreSQL service user can read the output file.

---

## Execution Log
| Script Name                    | Date/Time           | Status   | Notes |
|------------------------------- |---------------------|:--------:|-------|
| ingest_code_point_open.py      | 2025-07-09          | Complete | Progress bar fix applied, staging table and metadata verified |
| ingest_lad_boundaries.py       | 2025-07-09          | Complete | Chunked upload & progress bar fix, staging table and metadata verified |
| ingest_nndr_properties.py      |                     |          |       |
| ingest_onspd.py                | 2025-07-09 21:45    | Complete | Full 57-column ONSPD mapping, hybrid COPY/INSERT performance, max-rows support, production-ready |
| ingest_os_open_map_local.py    |                     |          |       |
| ingest_nndr_ratepayers.py      |                     |          |       |
| ingest_os_open_uprn.py         |                     |          |       |
| ingest_os_open_names.py        | 2025-07-09          | Complete | Client-side COPY fix applied, works with local files and Docker |
| ingest_os_open_usrn.py         | 2025-07-09 22:20    | Complete | GeoPackage support, 3D geometry handling, chunked upload with progress bar, production-ready |
| ingest_valuations.py           |                     |          |       |

---

## Monitoring & Automation Notes
- For long-running scripts, consider writing execution logs to a file (e.g., `ingestion_logs/`) with timestamps, batch/session IDs, and row counts.
- Optionally, implement auto-monitoring by tailing log files or using a dashboard to track progress and completion.
- Update the above checklist and execution log after each script run.

---

**Instructions:**
- Mark each script as complete (`[x]`) in the checklist after successful execution and verification.
- Fill in the execution log with date/time, status, and any relevant notes after each run.
- Use this document to coordinate and track ingestion standardization across the project. 