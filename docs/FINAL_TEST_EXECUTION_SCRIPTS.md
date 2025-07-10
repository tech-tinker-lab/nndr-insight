# Final Test Execution Scripts

This document lists the final test execution commands for running data ingestion and validation scripts in this project. Use these commands from the root of the project directory.

---

## 1. ONSPD Ingestion

```sh
python ingestion/scripts/ingest_onspd.py --source-path data/ONSPD_Online_Latest_Centroids.csv
```

---

## 2. OS Open Map Local Ingestion

```sh
python ingestion/scripts/ingest_os_open_map_local.py --source-path data/opmplc_gml3_gb/data
```

---

## 3. Code-Point Open Ingestion

```sh
python ingestion/scripts/ingest_code_point_open.py --source-path data/codepo_gb/Data/CSV
```

---

## 4. LAD Boundaries Ingestion

```sh
python ingestion/scripts/ingest_lad_boundaries.py --source-path data/LAD_MAY_2025_UK_BFC.shp
```

---

## 5. OS Open USRN Ingestion

```sh
python ingestion/scripts/ingest_os_open_usrn.py --source-path data/osopenusrn_202507_gpkg/osopenusrn_202507.gpkg
```

---

## 6. OS Open Names Ingestion

```sh
python ingestion/scripts/ingest_os_open_names.py --source-path data/opname_csv_gb/opname.csv
```

---

## 7. OS Open UPRN Ingestion

```sh
python ingestion/scripts/ingest_os_open_uprn.py --source-path data/osopenuprn_202506_csv/osopenuprn.csv
```

---

## [Add additional ingestion or validation commands below]

---

**Usage:**
- Run each command from the project root.
- Ensure your Python environment is activated and all dependencies are installed.
- Update file paths as needed for your data files. 