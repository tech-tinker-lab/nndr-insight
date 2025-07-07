# Database Setup and Ingestion Scripts

This directory contains all scripts and resources for setting up and managing the database schema, as well as scripts for ingesting data into the core reference and business tables for the project.

## Directory Structure

- `schemas/` — Database schema creation and setup scripts (Python/SQL)
- `ingest/`  — Data ingestion scripts for each dataset (Python)

## Schema/Database Setup Scripts

| Script                        | Tables Created (examples)                | Drop Table? | Notes                        |
|-------------------------------|------------------------------------------|-------------|------------------------------|
| setup_db.py                   | gazetteer, os_open_uprn, code_point, ... | No          | Core reference tables        |
| create_fresh_db.py            | properties, ratepayers, valuations, ...  | No          | Full fresh DB setup          |
| init_db.py                    | properties, ratepayers, gazetteer, ...   | No          | Initial setup, similar scope |
| run_enhanced_schema_setup.py  | staging, geography, BI, mapping, ...     | No          | Data warehouse, advanced     |
| add_missing_tables.py         | os_open_map_local, staging               | No          | Patch missing tables         |
| create_onspd_table.py         | onspd                                    | No          | ONSPD only                   |

- All scripts use `CREATE TABLE IF NOT EXISTS` — **safe to run repeatedly** (idempotent, no data loss).
- Some scripts (e.g., `run_enhanced_schema_setup.py`) create advanced/warehouse tables for BI, mapping, forecasting, and data quality.
- For a new environment, run `create_fresh_db.py` or `run_enhanced_schema_setup.py` for a full schema setup.
- For patching, use `add_missing_tables.py` or focused scripts.
- For schema changes, add migration scripts or use a migration tool (e.g., Alembic).

## Ingestion Scripts

All ingestion scripts for each dataset are in `ingest/`. Each script is responsible for loading data into its corresponding table(s) after the schema is set up.

## Recommendations

- **Initial setup:** Run a comprehensive schema script (see above) before running any ingestion scripts.
- **Safe to rerun:** All schema scripts are idempotent and will not drop or overwrite existing data.
- **Schema changes:** For structural changes, use migrations or manually update the schema as needed.
- **Documentation:** Update this README as you add new scripts or datasets.

---

For questions or to add new datasets, follow the structure above and update this documentation accordingly. 