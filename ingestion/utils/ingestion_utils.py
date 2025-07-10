"""
Ingestion Utilities Module
=========================

This module provides a flexible, reusable set of utilities for bulk data ingestion into PostgreSQL staging tables. It is designed to support a wide range of data sources, formats, and ingestion scenarios commonly encountered in geospatial, property, and business rates projects.

Planned Features:
-----------------
1. **Flexible Bulk Import**
   - Supports CSV, TXT, ZIP (with data files inside), GML (geospatial), and more.
   - Handles different delimiters (comma, asterisk, tab, pipe, etc.).
   - Can process a single file, all files in a directory, or recursively through subdirectories.

2. **Configurable via Property File**
   - Accepts JSON, YAML, or TXT config files specifying:
     - Source file or directory
     - Target table and columns
     - Source-to-target column mapping
     - Metadata columns/values
     - Delimiter, header presence, required fields, etc.

3. **Column Mapping & Metadata**
   - Maps source columns (by name or index) to target columns.
   - Appends metadata columns (e.g., source, batch_id, upload_user) to each row.
   
4. **Quality Checks & Validation**
   - Validates column count per row.
   - Checks for nulls in required fields.
   - Optionally checks for duplicates or other quality metrics.

5. **Logging**
   - Logs each step, errors, and summary statistics for traceability.

6. **Bulk Loading**
   - Uses PostgreSQL COPY for fast, efficient data loading.

7. **Database Connectivity via .env**
   - All database connection details (host, port, user, password, dbname) are loaded from an `.env` file using environment variables, never from the config file.
   - Uses `python-dotenv` to load these variables for security and flexibility.
   - This is a security best practice and keeps credentials out of code and config files.

8. **Extensibility**
   - Designed to be easily extended for new file types, validation rules, or ingestion patterns.

Typical Usage:
--------------
- Import a single CSV, a ZIP of CSVs, a GML file, or a whole directory of files into a staging table.
- Specify all ingestion parameters in a config file for reproducibility and automation.
- Run quality checks and log results for data governance.
- Database credentials are always loaded from the `.env` file/environment variables, never from the config file.

"""

import os
import csv
import json
import logging
import zipfile
import psycopg2
from dotenv import load_dotenv
from io import StringIO
from datetime import datetime
from typing import List, Dict, Optional, Any

try:
    import yaml
except ImportError:
    yaml = None

# GML/geospatial support is optional
try:
    import geopandas as gpd
except ImportError:
    gpd = None

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

# ----------------------
# Logging Setup
# ----------------------
def setup_logging(name=__name__, level=logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(name)

# ----------------------
# Config Loader
# ----------------------
def load_config(config_path: str) -> dict:
    """Load config from JSON or YAML file."""
    if config_path.lower().endswith('.json'):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif config_path.lower().endswith(('.yaml', '.yml')):
        if not yaml:
            raise ImportError("PyYAML is required for YAML config files. Install with 'pip install pyyaml'.")
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        raise ValueError(f"Unsupported config file type: {config_path}")

# ----------------------
# File Discovery
# ----------------------
def find_files(source_path: str, file_types: List[str], recursive: bool = True) -> List[str]:
    files = []
    if os.path.isfile(source_path):
        if any(source_path.lower().endswith(f'.{ext}') for ext in file_types):
            files.append(source_path)
    elif os.path.isdir(source_path):
        if recursive:
            for root, dirs, filenames in os.walk(source_path):
                for filename in filenames:
                    if any(filename.lower().endswith(f'.{ext}') for ext in file_types):
                        files.append(os.path.join(root, filename))
        else:
            for filename in os.listdir(source_path):
                if any(filename.lower().endswith(f'.{ext}') for ext in file_types):
                    files.append(os.path.join(source_path, filename))
    else:
        raise FileNotFoundError(f"Source path not found: {source_path}")
    return files

# ----------------------
# Database Connection
# ----------------------
def get_db_connection():
    load_dotenv()
    return psycopg2.connect(
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT")
    )

# ----------------------
# File Type Handlers
# ----------------------
def read_csv_file(file_path: str, delimiter: str = ',', header: bool = True) -> List[List[str]]:
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=delimiter)
        if header:
            next(reader, None)  # skip header
        for row in reader:
            rows.append(row)
    return rows

def read_zip_file(zip_path: str, inner_file: Optional[str] = None, delimiter: str = ',', header: bool = True) -> List[List[str]]:
    rows = []
    with zipfile.ZipFile(zip_path, 'r') as z:
        file_list = z.namelist()
        target_file = inner_file or next((f for f in file_list if f.lower().endswith('.csv')), None)
        if not target_file:
            raise FileNotFoundError("No CSV file found in ZIP archive.")
        with z.open(target_file) as f:
            reader = csv.reader((line.decode('utf-8') for line in f), delimiter=delimiter)
            if header:
                next(reader, None)
            for row in reader:
                rows.append(row)
    return rows

def read_gml_file(gml_path: str, gml_layer: Optional[str] = None) -> List[Dict[str, Any]]:
    if not gpd:
        raise ImportError("geopandas is required for GML ingestion. Install with 'pip install geopandas'.")
    gdf = gpd.read_file(gml_path, layer=gml_layer) if gml_layer else gpd.read_file(gml_path)
    return gdf.to_dict('records')

# ----------------------
# Column Mapping & Metadata
# ----------------------
def map_row(row: List[Any], source_columns: List[str], target_columns: List[str], mapping: Optional[Dict[str, str]] = None) -> List[Any]:
    if mapping:
        mapped = [row[source_columns.index(mapping.get(tc, tc))] if mapping.get(tc, tc) in source_columns else '' for tc in target_columns]
    else:
        mapped = row[:len(target_columns)] + [''] * (len(target_columns) - len(row))
    return mapped

def append_metadata(row: List[Any], metadata_values: Dict[str, Any], metadata_columns: List[str]) -> List[Any]:
    return row + [metadata_values.get(col, '') for col in metadata_columns]

# ----------------------
# Validation & Quality Checks
# ----------------------
def validate_row(row: List[Any], expected_columns: int) -> bool:
    return len(row) == expected_columns

def check_nulls(rows: List[List[Any]], required_fields: List[int]) -> Dict[int, int]:
    null_counts = {idx: 0 for idx in required_fields}
    for row in rows:
        for idx in required_fields:
            if idx < len(row) and (row[idx] is None or row[idx] == ''):
                null_counts[idx] += 1
    return null_counts

# ----------------------
# Bulk Loading (PostgreSQL COPY)
# ----------------------
def bulk_copy_to_db(conn, table: str, columns: List[str], rows: List[List[Any]], logger=None):
    output_buffer = StringIO()
    writer = csv.writer(output_buffer)
    writer.writerow(columns)
    # Add progress bar for writing rows to buffer
    row_iter = tqdm(rows, desc=f"Buffering rows for {table}") if tqdm else rows
    for row in row_iter:
        writer.writerow(row)
    output_buffer.seek(0)
    with conn.cursor() as cur:
        copy_sql = f"""
            COPY {table} ({', '.join(columns)})
            FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
        """
        if tqdm:
            with tqdm(total=len(rows), desc=f"Loading to {table}", unit="rows") as pbar:
                cur.copy_expert(sql=copy_sql, file=output_buffer)
                pbar.update(len(rows))
        else:
            cur.copy_expert(sql=copy_sql, file=output_buffer)
        conn.commit()
        if logger:
            logger.info(f"Loaded {len(rows)} rows into {table}")

# ----------------------
# Main Entry Function
# ----------------------
def bulk_ingest_with_validation(config_path: str, logger=None):
    """
    Main entry point for bulk ingestion with validation.
    Reads config, discovers files, processes each file, validates, and loads to DB.
    """
    config = load_config(config_path)
    logger = logger or setup_logging()

    # Extract config
    source_path = config.get('source_path') or config.get('source_file')
    if not source_path:
        raise ValueError("Config must specify 'source_path' or 'source_file'.")
    file_types = config.get('file_types', ['csv', 'txt', 'gml', 'zip'])
    recursive = config.get('recursive', True)
    delimiter = config.get('delimiter', ',')
    header = config.get('header', True)
    target_table = config['target_table']
    target_columns = config['target_columns']
    mapping = config.get('source_to_target_mapping')
    metadata_values = config.get('metadata_values', {})
    metadata_columns = [col for col in target_columns if col in metadata_values]
    required_fields = config.get('required_fields', [])
    gml_layer = config.get('gml_layer')

    # Discover files
    files = find_files(source_path, file_types, recursive=recursive)
    logger.info(f"Discovered {len(files)} file(s) for ingestion.")

    all_rows = []
    for file_path in files:
        ext = os.path.splitext(file_path)[1].lower()
        logger.info(f"Processing file: {file_path}")
        if ext in ['.csv', '.txt']:
            rows = read_csv_file(file_path, delimiter=delimiter, header=header)
            source_columns = None
            if header:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=delimiter)
                    source_columns = next(reader)
            else:
                source_columns = [f'col{i+1}' for i in range(len(target_columns))]
            row_iter = tqdm(rows, desc=f"Processing {os.path.basename(file_path)}") if tqdm else rows
            for row in row_iter:
                mapped = map_row(row, source_columns, target_columns, mapping)
                mapped = append_metadata(mapped, metadata_values, metadata_columns)
                all_rows.append(mapped)
        elif ext == '.zip':
            inner_file = config.get('inner_file')
            rows = read_zip_file(file_path, inner_file=inner_file, delimiter=delimiter, header=header)
            source_columns = None
            with zipfile.ZipFile(file_path, 'r') as z:
                target_file = inner_file or next((f for f in z.namelist() if f.lower().endswith('.csv')), None)
                if not target_file:
                    raise FileNotFoundError("No CSV file found in ZIP archive.")
                with z.open(target_file) as f:
                    reader = csv.reader((line.decode('utf-8') for line in f), delimiter=delimiter)
                    if header:
                        source_columns = next(reader)
                    else:
                        source_columns = [f'col{i+1}' for i in range(len(target_columns))]
            row_iter = tqdm(rows, desc=f"Processing {os.path.basename(file_path)} (zip)") if tqdm else rows
            for row in row_iter:
                mapped = map_row(row, source_columns, target_columns, mapping)
                mapped = append_metadata(mapped, metadata_values, metadata_columns)
                all_rows.append(mapped)
        elif ext == '.gml':
            if not gpd:
                raise ImportError("geopandas is required for GML ingestion. Install with 'pip install geopandas'.")
            records = read_gml_file(file_path, gml_layer=gml_layer)
            row_iter = tqdm(records, desc=f"Processing {os.path.basename(file_path)} (gml)") if tqdm else records
            for rec in row_iter:
                row = [rec.get(col, '') for col in target_columns]
                row = append_metadata(row, metadata_values, metadata_columns)
                all_rows.append(row)
        else:
            logger.warning(f"Unsupported file type: {file_path}")
            continue

    # Validation
    logger.info(f"Validating {len(all_rows)} rows...")
    expected_columns = len(target_columns)
    valid_rows = [row for row in all_rows if validate_row(row, expected_columns)]
    invalid_rows = len(all_rows) - len(valid_rows)
    if invalid_rows > 0:
        logger.warning(f"{invalid_rows} row(s) had incorrect column count and were skipped.")

    # Quality checks
    if required_fields:
        # Convert required_fields to indices if they are column names
        if isinstance(required_fields[0], str):
            required_indices = [target_columns.index(f) for f in required_fields if f in target_columns]
        else:
            required_indices = required_fields
        null_counts = check_nulls(valid_rows, required_indices)
        for idx, count in null_counts.items():
            logger.info(f"Nulls in column {target_columns[idx]}: {count}")

    # Bulk load
    logger.info(f"Loading {len(valid_rows)} valid rows into {target_table}...")
    conn = get_db_connection()
    try:
        bulk_copy_to_db(conn, target_table, target_columns, valid_rows, logger=logger)
    finally:
        conn.close()
    logger.info("Ingestion complete.")

# ----------------------
# Example Usage (as comment)
# ----------------------
'''
Example config file (JSON):
{
  "source_path": "data/my_bulk_folder",
  "recursive": true,
  "file_types": ["csv", "gml"],
  "delimiter": ",",
  "header": true,
  "target_table": "my_table",
  "target_columns": ["field_1", "field_2", "field_3", "source_name", "upload_user"],
  "source_to_target_mapping": {},
  "metadata_values": {"source_name": "VOA_2010", "upload_user": "admin"},
  "required_fields": ["field_1", "field_2"]
}

# To run ingestion:
# from ingestion.utils.ingestion_utils import bulk_ingest_with_validation
# bulk_ingest_with_validation('my_ingest_config.json')
''' 

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ingestion/utils/ingestion_utils.py <config_path>")
        sys.exit(1)
    config_path = sys.argv[1]
    bulk_ingest_with_validation(config_path) 