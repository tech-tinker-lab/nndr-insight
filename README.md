## Database Setup Details

The project uses PostgreSQL with PostGIS as the database, managed via Docker Compose. We recommend using the official Kartoza PostGIS image for production use.

### Quick Start

```sh
# From project root directory
cd setup/docker
docker-compose -f docker-compose.official-kartoza.yml up -d
```

### Database Configuration

- **Image:** kartoza/postgis:17-3.5 (recommended) or postgres:16 (simple)
- **User:** nndr
- **Password:** nndrpass
- **Database:** nndr_db
- **Port:** 5432 (exposed to host)
- **Data Volume:** db_data (persists database data between container restarts)

### Performance Tuning for Large Datasets

For optimal performance with large NNDR datasets, apply the included performance tuning:

```sh
# After starting the database
cd setup/database/tuning
./apply_tuning.sh  # Linux/macOS
# or
apply_tuning.bat   # Windows
```

The tuning script optimizes:
- Memory allocation (shared_buffers, work_mem, etc.)
- WAL settings for better write performance
- Query planner settings for SSD storage
- Autovacuum settings for large tables
- Connection and timeout settings

See `setup/database/tuning/README.md` for detailed tuning documentation.

### Available Docker Compose Files

- `docker-compose.official-kartoza.yml` - Production-ready with Kartoza PostGIS
- `docker-compose.simple.yml` - Simple setup with official PostgreSQL
- `docker-compose.enhanced.yml` - Enhanced setup with monitoring and backups

The database will be accessible at `localhost:5432` with the above credentials. Update the environment variables in the docker-compose files if you need to change the user, password, or database name.

## What Forms the Gazetteer?

The "gazetteer" in this project is a comprehensive table of properties, addresses, and locations, serving as the backbone for spatial analysis, linking, and forecasting. It is constructed by combining:

- **OS Open UPRN**: Provides the Unique Property Reference Number (UPRN) and coordinates for every property.
- **Code-Point Open**: Adds postcode-to-coordinate mapping for geocoding and postcode lookups.
- **ONSPD**: Adds postcode centroids and administrative/statistical geographies.
- **OS Open USRN**: Links properties to streets using Unique Street Reference Numbers.
- **OS Open Names**: Adds place names, settlements, and street names for geocoding and enrichment.
- **OS Open Map – Local**: Adds building footprints and spatial context for visualization and spatial joins.
- **Local Authority District Shapefiles**: Adds administrative boundaries for spatial joins and mapping.

The `gazetteer` table in the database is designed to hold the core property/location information, and can be enriched by joining with the above datasets. It typically includes:

- `property_id` (or UPRN)
- `address`
- `postcode`
- `latitude`, `longitude`
- `property_type`
- `district`

Other tables (e.g., `os_open_uprn`, `onspd`, etc.) provide additional reference and lookup data to enrich the gazetteer.

---
## Recommended Data Loading Order

To ensure referential integrity and enable rich joins, load your data into the database in the following order:

1. **OS Open UPRN** (`osopenuprn_202506_csv/osopenuprn_202506.csv`)
   - Loads the backbone property reference and coordinates.
2. **Code-Point Open** (`codepo_gb/Data/CSV/*.csv`)
   - Loads postcode to coordinate mapping for geocoding and postcode lookups.
3. **ONSPD (ONS Postcode Directory)** (`ONSPD_Online_Latest_Centroids.csv`)
   - Loads postcode centroids and administrative/statistical geographies.
4. **OS Open USRN** (`osopenusrn_202507_gpkg.zip`)
   - Loads street reference numbers and names for address-to-street linkage.
5. **OS Open Names** (`opname_csv_gb.zip`)
   - Loads place names, settlements, and street names for geocoding and enrichment.
6. **OS Open Map – Local** (`opmplc_gml3_gb.zip` and `opmplc_gml3_gb/`)
   - Loads building footprints and spatial context for property visualization and spatial joins.
7. **Local Authority District Shapefiles** (`LAD_MAY_2025_UK_BFC.*`)
   - Loads administrative boundaries for spatial joins and mapping.
8. **NNDR/VOA Rating List and Valuations** (various CSVs/folders)
   - Loads business rates, ratepayer, and valuation data for analysis and forecasting.

## Marking Data Source in the Database

To track the origin of each record, add a `source` or `dataset` column to each table (or as metadata in a related table). For example:

```sql
ALTER TABLE os_open_uprn ADD COLUMN source TEXT DEFAULT 'OS Open UPRN 2025-06';
ALTER TABLE code_point_open ADD COLUMN source TEXT DEFAULT 'Code-Point Open 2025-06';
-- Repeat for other tables as needed
```

This allows you to:
- Filter or audit records by source
- Support future updates or incremental loads
- Provide provenance in your data pipeline and APIs

## Future: Automated File Upload, Detection, and Preview

To streamline data ingestion, consider building a file upload system (via SFTP or REST endpoint) with these features:

1. **Upload:** User uploads a file via SFTP or REST API.
2. **Detection:** System inspects the file (headers, sample rows, file type) to auto-detect the dataset type.
3. **Preview:** System displays a preview (first N rows) and a description of the dataset, its use, and how it will be processed.
4. **Processing:** User confirms and triggers ingestion, or system auto-processes if valid.

**Implementation tips:**
- Use file name patterns, header matching, and sample data to detect dataset type.
- Store a record of each upload (filename, detected type, upload date, user, etc.) in a database table for audit and provenance.
- Provide clear feedback and documentation to users at each step.

This approach will make your data pipeline robust, user-friendly, and auditable.
# Data Directory Documentation

This project uses several open datasets for UK property, address, and spatial analysis. Below is a summary of each major file or folder in the `backend/data` directory:

## Folders and Their Contents

- **codepo_gb/**: Contains Code-Point Open postcode data. Subfolders:
  - `Data/CSV/`: Individual CSVs for each postcode area (e.g., ab.csv, al.csv, etc.).
  - `Doc/`: Documentation, column headers, metadata, and code lists for Code-Point Open.
- **osopenuprn_202506_csv/**: Contains the OS Open UPRN CSV file and licence/version info.
- **opmplc_gml3_gb/**: Contains GML data for OS Open Map – Local, organized by grid square.

## Main Data Files

- **codepo_gb.zip**: Zip archive of the Code-Point Open data (extracts to `codepo_gb/`).
- **osopenuprn_202506_csv.zip**: Zip archive of OS Open UPRN (extracts to `osopenuprn_202506_csv/`).
- **opmplc_gml3_gb.zip**: Zip archive of OS Open Map – Local (extracts to `opmplc_gml3_gb/`).
- **osopenusrn_202507_gpkg.zip**: GeoPackage for OS Open USRN (Unique Street Reference Numbers).
- **opname_csv_gb.zip**: Zip archive of OS Open Names (place names, settlements, etc.).
- **ONSPD_Online_Latest_Centroids.csv**: ONS Postcode Directory, mapping postcodes to centroid coordinates and metadata.
- **LAD_MAY_2025_UK_BFC.*:** Shapefiles for local authority district boundaries (multiple files: .shp, .dbf, .prj, etc.).
- **NNDR Rating List  March 2015_0.csv**: NNDR rating list for March 2015.
- **nndr-ratepayers March 2015_0.csv**: Ratepayer data for March 2015.
- **uk-englandwales-ndr-*-listentries-compiled-epoch-*-baseline-csv/**: Folders containing rating list entries for 2010, 2017, 2023.
- **uk-englandwales-ndr-*-summaryvaluations-compiled-epoch-*-baseline-csv/**: Folders containing summary valuations for 2010, 2017, 2023.

## Dataset Descriptions

### OS Open UPRN
- **Folder:** `osopenuprn_202506_csv/`
- **File:** `osopenuprn_202506.csv`
- **Description:** Contains Unique Property Reference Numbers (UPRNs) with X/Y coordinates and latitude/longitude for every property in Great Britain. This is the backbone for property-level analysis and spatial joins.

### Code-Point Open
- **Folder:** `codepo_gb/`
- **Files:** `Data/CSV/*.csv`
- **Description:** Provides postcode to coordinate mapping for the UK. Each CSV (e.g., `ab.csv`, `al.csv`, etc.) contains postcodes and their corresponding eastings/northings, positional quality, and administrative codes. Useful for postcode-level geocoding and lookups.

### ONSPD (ONS Postcode Directory)
- **File:** `ONSPD_Online_Latest_Centroids.csv`
- **Description:** Official ONS directory mapping postcodes to centroid coordinates and a wide range of administrative and statistical geographies.

### OS Open USRN
- **File:** `osopenusrn_202507_gpkg.zip`
- **Description:** Unique Street Reference Numbers (USRNs) for every street in Great Britain, provided as a GeoPackage. Useful for linking addresses to street records and spatial navigation.

### OS Open Names
- **File:** `opname_csv_gb.zip`
- **Description:** Gazetteer of place names, including settlements, streets, post towns, and other geographical names. Useful for geocoding and place-based lookups.

### OS Open Map – Local
- **File:** `opmplc_gml3_gb.zip` and `opmplc_gml3_gb/`
- **Description:** Lightweight vector map with layers for buildings, roads, railways, etc. Includes building footprints for spatial joins with UPRNs.

### Local Authority District Shapefiles
- **Files:** `LAD_MAY_2025_UK_BFC.*`
- **Description:** Shapefiles for local authority district boundaries. Useful for spatial joins and mapping properties to administrative areas.

### NNDR/VOA Rating List and Valuations
- **Files/Folders:**
  - `NNDR Rating List  March 2015_0.csv`
  - `nndr-ratepayers March 2015_0.csv`
  - `uk-englandwales-ndr-2010-listentries-compiled-epoch-0052-baseline-csv/`
  - `uk-englandwales-ndr-2010-summaryvaluations-compiled-epoch-0052-baseline-csv/`
  - `uk-englandwales-ndr-2017-listentries-compiled-epoch-0051-baseline-csv/`
  - `uk-englandwales-ndr-2017-summaryvaluations-compiled-epoch-0051-baseline-csv/`
  - `uk-englandwales-ndr-2023-listentries-compiled-epoch-0015-baseline-csv/`
  - `uk-englandwales-ndr-2023-summaryvaluations-compiled-epoch-0015-baseline-csv/`
- **Description:** Business rates (NNDR) rating lists and summary valuations for England and Wales, for multiple years. Used for property/ratepayer analysis and forecasting.

---

**Note:** Some files are compressed archives (e.g., `.zip`) and may need to be extracted before use. Some spatial files (e.g., shapefiles, GeoPackages, GML) require GIS tools or libraries (e.g., GeoPandas, GDAL) for processing.
# NNDR Insight

A comprehensive business rate forecasting and non-rated property identification system for South Cambridgeshire District Council.

## Project Structure

```
nndr-insight/
├── backend/           # FastAPI backend application
├── frontend/          # React frontend application
├── setup/            # Database setup and configuration
│   ├── database/     # Core database setup and migrations
│   ├── config/       # Configuration files
│   ├── scripts/      # Utility and ingestion scripts
│   └── docs/         # Setup documentation
├── services/         # Shared services
└── data/            # Data files (backend/data/)
```

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Prophet (forecasting)
- **Frontend**: React, Tailwind CSS, Leaflet (mapping)
- **Database**: PostgreSQL with PostGIS extension
- **Migration System**: Custom Python-based migration tracker

## Git Configuration

The project includes comprehensive `.gitignore` files to prevent large data files and build artifacts from being tracked:

- **Root `.gitignore`**: Ignores all data files, build artifacts, and common temporary files
- **`backend/data/.gitignore`**: Specifically ignores all files in the data directory (except the README)
- **`backend/.gitignore`**: Ignores Python-specific files and virtual environments
- **`frontend/.gitignore`**: Ignores Node.js dependencies and build artifacts
- **`setup/.gitignore`**: Ignores temporary files and configuration artifacts

### Data Files
All data files in `backend/data/` are ignored by Git due to their large size. See `backend/data/README.md` for information on required data files and sources.

## Quick Start

### 1. Database Setup
```bash
cd setup/database
python run_complete_db_setup.py
```

### 2. Start Services
```bash
# Start database
cd setup/docker
docker compose -f docker-compose.simple.yml up -d

# Start backend (if needed)
cd ../..
docker compose -f setup/docker/docker-compose.yml up -d backend
```

### 3. Run Migrations (if needed)
```bash
cd setup/database
python run_migrations.py --run-all
```

### 4. Ingest Data
```bash
cd setup/scripts
python ingest_gazetteer.py
python ingest_nndr_properties.py
```

## Key Features

- **Business Rate Forecasting**: Prophet-based forecasting models
- **Non-Rated Property Identification**: Spatial analysis for missing properties
- **Geospatial Analysis**: PostGIS-powered spatial queries and mapping
- **Migration System**: Version-controlled database schema management
- **Data Quality Assurance**: Comprehensive validation and diagnostic tools

## API Endpoints

- `/api/postcode-centroid?postcode=CB1 1AA` — Postcode lookup using ONSPD
- `/api/districts-geojson` — Local Authority District boundaries
- `/api/forecast/business-rates` — Business rate forecasting
- `/api/geospatial/non-rated` — Non-rated property analysis
   cd setup/docker
   docker compose -f docker-compose.simple.yml up -d
   ```

3. Initialize the database and tables (this will also create the database if it doesn't exist):
   ```sh
   python backend/init_db.py
   ```

4. Ingest NNDR data (example for the 2015 rating list):
   ```sh
   python backend/ingest_nndr_rating_list.py
   ```

## TODO: Jupyter Notebook for Ad Hoc Analysis and Reporting
- [ ] Use the provided `NNDR_AdHoc_Analysis_and_Reporting.ipynb` notebook for interactive data analysis and reporting.
    - Includes: database connection, ad hoc SQL queries, data visualization, and a template for automated reporting scripts.
- [ ] Expand the notebook with additional queries, visualizations, or reporting as needed for your workflow.

# NNDR Insight Data Pipeline: Data Dictionary & Forecasting Guidance

## Data Dictionary

### Table: properties
- **id**: Internal unique identifier for the property (serial primary key).
- **list_altered**: List alteration code (e.g., for revaluations or changes).
- **community_code**: Local authority or community code.
- **ba_reference**: Billing Authority Reference (unique property identifier, used for linking across datasets).
- **property_category_code**: Property category code (e.g., SCAT code).
- **property_description**: Description of the property (e.g., "SHOP AND PREMISES").
- **property_address**: Full address string.
- **street_descriptor**: Street name or descriptor.
- **locality**: Locality or village/town.
- **post_town**: Post town.
- **administrative_area**: Administrative area (e.g., county or district).
- **postcode**: Postcode (may be normalized).
- **effective_date**: Date the property record became effective.
- **partially_domestic_signal**: Indicator if the property is partially domestic (e.g., mixed use).
- **rateable_value**: Current rateable value (RV) for the property.
- **scat_code**: Standard Classification of All Types (property type code).
- **appeal_settlement_code**: Code for appeal/settlement status.
- **unique_property_ref**: Unique property reference number (UPRN or similar).

### Table: ratepayers
- **id**: Internal unique identifier.
- **property_id**: Foreign key to `properties`.
- **name**: Name of the ratepayer (company or individual).
- **address**: Ratepayer's address.
- **company_number**: Company registration number (if applicable).
- **liability_start_date**: Start date of ratepayer's liability.
- **liability_end_date**: End date of liability.
- **annual_charge**: Annual NNDR charge.
- **exemption_amount**: Amount of any exemption.
- **exemption_code**: Code for exemption type.
- **mandatory_amount**: Amount of mandatory relief.
- **mandatory_relief**: Type of mandatory relief.
- **charity_relief_amount**: Amount of charity relief.
- **disc_relief_amount**: Amount of discretionary relief.
- **discretionary_charitable_relief**: Type of discretionary charitable relief.
- **additional_rlf**: Additional relief code.
- **additional_relief**: Additional relief amount/type.
- **sbr_applied**: Small Business Rate relief applied (Y/N or code).
- **sbr_supplement**: SBR supplement (if any).
- **sbr_amount**: Amount of SBR relief.
- **charge_type**: Type of charge (e.g., occupied, empty).
- **report_date**: Date of report/extract.
- **notes**: Any additional notes.

### Table: valuations (VOA current valuations)
- **id**: Internal unique identifier.
- **property_id**: Foreign key to `properties`.
- **row_id**: Row number or unique row identifier from VOA file.
- **billing_auth_code**: Billing authority code.
- **empty1**: (Unused/unknown field, present for alignment with source file).
- **ba_reference**: Billing Authority Reference (for linkage).
- **scat_code**: Property type code.
- **description**: Description of property.
- **herid**: Hereditament ID (VOA unique property identifier).
- **address_full**: Full address string from VOA.
- **empty2**: (Unused/unknown field).
- **address1** to **address5**: Address components.
- **postcode**: Postcode.
- **effective_date**: Date valuation became effective.
- **empty3**: (Unused/unknown field).
- **rateable_value**: Rateable value for this valuation.
- **empty4**: (Unused/unknown field).
- **uprn**: Unique Property Reference Number.
- **compiled_list_date**: Date the compiled list was created.
- **list_code**: List code (e.g., 2010, 2017, 2023).
- **empty5** to **empty9**: (Unused/unknown fields).
- **property_link_number**: Property link number (VOA).
- **entry_date**: Date the entry was made.
- **source**: Source label (e.g., "2010", "2017").

### Table: historic_valuations (VOA historic valuations)
- **id**: Internal unique identifier.
- **property_id**: Foreign key to `properties`.
- **billing_auth_code**: Billing authority code.
- **empty1**: (Unused/unknown field).
- **ba_reference**: Billing Authority Reference.
- **scat_code**: Property type code.
- **description**: Description of property.
- **herid**: Hereditament ID.
- **effective_date**: Date this valuation became effective.
- **empty2**: (Unused/unknown field).
- **rateable_value**: Rateable value for this historic record.
- **uprn**: Unique Property Reference Number.
- **change_date**: Date of change (e.g., revaluation, appeal outcome).
- **list_code**: List code (e.g., 2010, 2017).
- **property_link_number**: Property link number.
- **entry_date**: Date the entry was made.
- **removal_date**: Date the record was removed (if applicable).
- **source**: Source label (e.g., "2010-historic").

## How to Use These Data for NNDR Forecasting

1. **Property Baseline:**
   - Use the `properties` table to establish the universe of rateable properties, their types, locations, and current RVs.
   - Join with `valuations` and `historic_valuations` to get the full valuation history for each property.

2. **Ratepayer Dynamics:**
   - Use the `ratepayers` table to analyze turnover, liability periods, and reliefs/exemptions applied to each property.
   - This helps model occupancy, churn, and relief take-up rates.

3. **Valuation Trends:**
   - Use `valuations` and `historic_valuations` to analyze how RVs change over time (due to revaluations, appeals, or property changes).
   - This is critical for forecasting future RVs and NNDR yield.

4. **Forecasting NNDR Yield:**
   - For each property, forecast future RVs using historic trends, property type, and local economic indicators.
   - Apply relief/exemption rules (from `ratepayers`) to estimate net collectable NNDR.
   - Aggregate by geography, property type, or other dimensions as needed.

5. **Scenario Analysis:**
   - Simulate the impact of policy changes (e.g., new reliefs, revaluation cycles) by adjusting the relevant fields and re-running the forecast.

6. **Geospatial Analysis:**
   - Use postcode and address fields to map properties and analyze spatial patterns in RVs, reliefs, and NNDR yield.

7. **Appeals and Volatility:**
   - Use `historic_valuations` to model the impact of appeals and removals on the NNDR base and forecast volatility.

---

**This data model provides a robust foundation for detailed NNDR forecasting, scenario analysis, and reporting at property, ratepayer, and area level.**
