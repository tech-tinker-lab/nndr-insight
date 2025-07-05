Certainly! Here’s a refined and well-structured **Markdown** version of your README content, polished for clarity and better flow, without adding new information but improving description and ordering of ingestion scripts.

---

# NNDR Insight Project: Data Pipeline and Setup

## Overview

This project uses multiple open datasets for UK property, address, and spatial analysis, enabling forecasting, mapping, and business rates (NNDR) insights.

The backend is a FastAPI + SQLAlchemy Python service with PostgreSQL for data storage and spatial queries. The frontend is a React app with Tailwind CSS.

---

## Database Setup

### PostgreSQL via Docker Compose

* **Image:** `postgres:16`
* **User:** `nndr`
* **Password:** `nndrpass`
* **Database:** `nndr_db`
* **Port:** `5432` (exposed to host)
* **Data Volume:** `db_data` (persists data)

Start the database with:

```bash
docker-compose up -d db
```

Connect to the DB at `localhost:5432` using the above credentials. Modify environment variables in `docker-compose.yml` if needed.

---

## Gazetteer Overview

The *gazetteer* is a master table of properties, addresses, and locations, essential for spatial analysis, linking datasets, and forecasting.

It is constructed by integrating:

* **OS Open UPRN:** Unique Property Reference Numbers with coordinates (backbone dataset)
* **Code-Point Open:** Postcode-to-coordinate mappings
* **ONSPD (ONS Postcode Directory):** Postcode centroids and admin/statistical geographies
* **OS Open USRN:** Unique Street Reference Numbers, linking properties to streets
* **OS Open Names:** Place names, settlements, street names
* **OS Open Map – Local:** Building footprints and spatial context
* **Local Authority District Shapefiles:** Administrative boundaries

The main `gazetteer` table includes fields such as:

* `property_id` (UPRN)
* `address`
* `postcode`
* `latitude`, `longitude`
* `property_type`
* `district`

Other tables provide additional reference data for enrichment.

---

## Data Loading Order and Ingestion Scripts

To maintain data integrity and enable rich spatial joins, follow this order when loading data:

1. **OS Open UPRN**
   File: `osopenuprn_202506_csv/osopenuprn_202506.csv`
   Loads property reference numbers and coordinates.
   *Ingestion script:* `ingest_osopenuprn.py`

2. **Code-Point Open**
   Folder: `codepo_gb/Data/CSV/*.csv`
   Loads postcode-to-coordinate mappings.
   *Ingestion script:* `ingest_codepoint.py`

3. **ONSPD (ONS Postcode Directory)**
   File: `ONSPD_Online_Latest_Centroids.csv`
   Loads postcode centroids and administrative geographies.
   *Ingestion script:* `ingest_onspd.py`

4. **OS Open USRN**
   File: `osopenusrn_202507_gpkg.zip`
   Loads street references and names.
   *Ingestion script:* `ingest_osopenusrn.py`

5. **OS Open Names**
   File: `opname_csv_gb.zip`
   Loads place names and settlements.
   *Ingestion script:* `ingest_osopennames.py`

6. **OS Open Map – Local**
   File: `opmplc_gml3_gb.zip` and folder `opmplc_gml3_gb/`
   Loads building footprints and spatial layers.
   *Ingestion script:* `ingest_osopenmaplocal.py`

7. **Local Authority District Shapefiles**
   Files: `LAD_MAY_2025_UK_BFC.*`
   Loads local authority boundaries.
   *Ingestion script:* `ingest_lad_shapefiles.py`

8. **NNDR/VOA Rating Lists and Valuations**
   Various CSVs and folders containing rating list entries, ratepayers, and valuations for multiple years.
   *Ingestion scripts:*

   * `ingest_nndr_rating_list.py` (e.g., 2015 data)
   * Similar scripts for other years and datasets

---

## Marking Data Source for Provenance

To track the origin of each record, add a `source` or `dataset` column to tables, e.g.:

```sql
ALTER TABLE os_open_uprn ADD COLUMN source TEXT DEFAULT 'OS Open UPRN 2025-06';
ALTER TABLE code_point_open ADD COLUMN source TEXT DEFAULT 'Code-Point Open 2025-06';
```

This helps with:

* Filtering or auditing by source
* Incremental updates
* Provenance tracking in APIs and pipelines

---

## Future Enhancements: Automated File Upload & Processing

To streamline data ingestion:

1. **Upload:** Accept files via SFTP or REST API.
2. **Detection:** Auto-detect dataset type by inspecting file headers and content.
3. **Preview:** Show a preview of rows, dataset description, and intended processing.
4. **Process:** User confirms or system auto-processes ingestion.

Store upload metadata (filename, user, date, detected type) for auditing.

---

## Data Directory Summary

### Folders and Contents

* `codepo_gb/` — Code-Point Open postcode data
* `osopenuprn_202506_csv/` — OS Open UPRN CSV
* `opmplc_gml3_gb/` — OS Open Map – Local GML data
* `uk-englandwales-ndr-*-listentries-compiled-epoch-*-baseline-csv/` — NNDR rating list entries
* `uk-englandwales-ndr-*-summaryvaluations-compiled-epoch-*-baseline-csv/` — Summary valuations

### Key Files

* `ONSPD_Online_Latest_Centroids.csv` — ONS Postcode Directory
* `osopenusrn_202507_gpkg.zip` — OS Open USRN GeoPackage
* `opname_csv_gb.zip` — OS Open Names data
* `LAD_MAY_2025_UK_BFC.*` — Local Authority District shapefiles
* Various NNDR CSV files for ratings, ratepayers, and valuations

---

## Data Dictionary: Main Tables

### properties

| Column                      | Description                                       |
| --------------------------- | ------------------------------------------------- |
| id                          | Internal unique identifier                        |
| list\_altered               | List alteration code (e.g., revaluation)          |
| community\_code             | Local authority/community code                    |
| ba\_reference               | Billing Authority Reference (property identifier) |
| property\_category\_code    | Property category code (SCAT)                     |
| property\_description       | Description of the property                       |
| property\_address           | Full address string                               |
| street\_descriptor          | Street name or descriptor                         |
| locality                    | Locality/town                                     |
| post\_town                  | Post town                                         |
| administrative\_area        | Administrative area (county/district)             |
| postcode                    | Postcode                                          |
| effective\_date             | Effective date of record                          |
| partially\_domestic\_signal | Indicator if partially domestic                   |
| rateable\_value             | Current rateable value                            |
| scat\_code                  | SCAT property type code                           |
| appeal\_settlement\_code    | Appeal/settlement status code                     |
| unique\_property\_ref       | Unique Property Reference Number (UPRN)           |

---

### ratepayers

| Column                            | Description                          |
| --------------------------------- | ------------------------------------ |
| id                                | Unique identifier                    |
| property\_id                      | Foreign key to `properties`          |
| name                              | Ratepayer name                       |
| address                           | Ratepayer address                    |
| company\_number                   | Company registration number          |
| liability\_start\_date            | Start date of liability              |
| liability\_end\_date              | End date of liability                |
| annual\_charge                    | Annual NNDR charge                   |
| exemption\_amount                 | Exemption amount                     |
| exemption\_code                   | Exemption type code                  |
| mandatory\_amount                 | Mandatory relief amount              |
| mandatory\_relief                 | Type of mandatory relief             |
| charity\_relief\_amount           | Charity relief amount                |
| disc\_relief\_amount              | Discretionary relief amount          |
| discretionary\_charitable\_relief | Discretionary charitable relief type |
| additional\_rlf                   | Additional relief code               |
| additional\_relief                | Additional relief amount/type        |
| sbr\_applied                      | Small Business Rate relief applied   |
| sbr\_supplement                   | SBR supplement amount                |
| sbr\_amount                       | SBR relief amount                    |
| charge\_type                      | Charge type (occupied, empty, etc.)  |
| report\_date                      | Report date                          |
| notes                             | Additional notes                     |

---

### valuations (VOA current valuations)

Contains VOA valuation data for properties with fields like:

* property\_id (foreign key)
* row\_id (source file row)
* billing authority code
* ba\_reference
* scat\_code
* description
* herid (hereditament id)
* full address
* postcode
* effective\_date
* rateable\_value
* uprn
* compiled\_list\_date
* list\_code (valuation year)
* property\_link\_number
* entry\_date
* source label

---

### historic\_valuations (VOA historic valuations)

Similar to `valuations` but stores historic valuation records with additional fields like:

* change\_date
* removal\_date

---

## Using These Data for NNDR Forecasting

1. **Establish Property Baseline:** Use `properties` as the foundation.
2. **Analyze Ratepayer Dynamics:** Examine ratepayer turnover, reliefs, and exemptions.
3. **Track Valuation Trends:** Use valuation tables to study changes over time.
4. **Forecast NNDR Yield:** Combine property valuations with relief rules.
5. **Scenario Analysis:** Simulate policy or economic changes.
6. **Geospatial Analysis:** Map properties and valuations using coordinates and boundaries.
7. **Model Appeals & Volatility:** Incorporate historic valuation changes for volatility.

---

## Backend Setup Instructions

1. Install Python dependencies:

   ```bash
   pip install -r backend/requirements.txt
   ```

2. Start PostgreSQL:

   ```bash
   docker-compose up -d db
   ```

3. Initialize database and tables:

   ```bash
   python backend/init_db.py
   ```

4. Ingest NNDR data (example for 2015 rating list):

   ```bash
   python backend/ingest_nndr_rating_list.py
   ```

---

## API Highlights

* `/api/postcode-centroid?postcode=CB1 1AA`
  Returns latitude and longitude for a postcode.

* `/api/districts-geojson`
  Returns Local Authority District boundaries as GeoJSON.

---

## Jupyter Notebook for Analysis and Reporting (TODO)

* Use `NNDR_AdHoc_Analysis_and_Reporting.ipynb` for ad hoc queries, visualization, and reporting.
* Extend with custom queries and forecasts.

---

*This README provides a comprehensive guide to the data pipeline, ingestion order, database schema, and usage guidance for the NNDR Insight project.*

---

If you want, I can also help you create a minimal TOC or split into sections for easier navigation. Would you like that?
