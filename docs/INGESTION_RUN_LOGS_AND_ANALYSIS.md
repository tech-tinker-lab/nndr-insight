# Ingestion Run Logs & Analysis

This document records the results and analysis of each major ingestion run. Use it to track data quality, performance, and any issues for future reference and audits.

---

## ONSPD Ingestion

- **Date/Time:** 2025-07-10 16:21–16:31
- **Command:**
  ```sh
  python ingestion/scripts/ingest_onspd.py --source-path data/ONSPD_Online_Latest_Centroids.csv
  ```
- **Files Processed:** 1
- **Rows Processed:** 2,714,964
- **Data Quality:**
  - Null postcodes: 0
  - Empty rows: 0
  - Valid rows: 2,714,964
- **Batch ID:** onspd_20250710_162148_737195
- **Session ID:** session_20250710_162148
- **Total Time:** ~10 minutes
- **Notes:**
  - Used client-side COPY with chunked processing for large file
  - No data quality issues detected

---

## Code-Point Open Ingestion

- **Date/Time:** 2025-07-10 16:32–16:33
- **Command:**
  ```sh
  python ingestion/scripts/ingest_code_point_open.py --source-path data/codepo_gb/Data/CSV
  ```
- **Files Processed:** 120
- **Rows Processed:** 1,743,449
- **Data Quality:**
  - Null postcodes: 0
  - Valid rows: 1,743,449
- **Batch ID:** codepoint_20250710_163249_102680
- **Session ID:** session_20250710_163249
- **Total Time:** ~40 seconds
- **Notes:**
  - Combined 120 CSV files into a single temporary file for fast COPY
  - No data quality issues detected

---

## [Add future ingestion runs below]

- **Date/Time:**
- **Command:**
- **Files Processed:**
- **Rows Processed:**
- **Data Quality:**
- **Batch ID:**
- **Session ID:**
- **Total Time:**
- **Notes:** 