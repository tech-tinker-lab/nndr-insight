import os
import sys
import argparse
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv
import time

"""
create_schema.py: Unified Database Schema Creation Script (SQL File Runner)

Changelog:
- v1.0: Initial version, executes hardcoded SQL_FILES list.
- v1.1: Enhanced to accept a text file (--file) listing .sql files to execute, one per line. If not provided, uses default SQL_FILES list. (2024-06-10)
- v1.1: Updated to include all staging and master tables for reference, postcode, address, and street datasets. (2024-06-10)
- v1.2: Added --recreate-db option to drop and recreate the target database before table creation. (2024-07-09)
- v1.3: Removed per-table drop logic and --drop option. Only --recreate-db is supported for full DB reset. (2024-07-09)

Usage:
    python create_schema.py [--recreate-db] [--file schema_files.txt]

- If --recreate-db is provided, the target database is dropped and recreated before any table creation.
- If --file is provided, reads the list of .sql files to execute from the file (one per line).
- If not, tables are only created if they do not exist (idempotent).
- Each .sql file in db_setup/schemas/ should handle only one table.
- The order of .sql execution is controlled by the SQL_FILES list or the provided file.
"""

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), 'schemas')

# List the .sql files in the exact order you want them executed
SQL_FILES = [
    '00_enable_postgis.sql',
    # Reference tables (staging and master)
    'reference/create_migration_history.sql',
    'reference/staging_configs.sql',
    'reference/os_open_uprn_staging.sql',
    'reference/os_open_uprn.sql',
    'reference/nndr_rating_list_staging.sql',
    'reference/nndr_rating_list.sql',
    'reference/nndr_ratepayers_staging.sql',
    'reference/nndr_ratepayers.sql',
    'reference/nndr_summary_valuation_staging.sql',
    'reference/nndr_properties_staging.sql',
    'reference/lad_boundaries_staging.sql',
    'reference/lad_boundaries.sql',
    'reference/valuations_staging.sql',
    'reference/historic_valuations_staging.sql',
    'reference/gazetteer_staging.sql',
    # Postcode tables (staging and master)
    'postcode/code_point_open_staging.sql',
    'postcode/code_point_open.sql',
    'postcode/onspd_staging.sql',
    'postcode/onspd.sql',
    # Address tables (staging and master)
    'address/os_open_names_staging.sql',
    'address/os_open_names.sql',
    # Street tables (staging and master)
    'street/os_open_map_local_staging.sql',
    'street/os_open_map_local.sql',
    'street/os_open_usrn_staging.sql',
    'street/os_open_usrn.sql',
]

def get_sql_files_from_txt(file_path):
    files = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                files.append(line)
    return files

def recreate_database():
    print(f"Connecting to maintenance database to drop and recreate '{DBNAME}'...")
    maintenance_engine = sqlalchemy.create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/postgres")
    with maintenance_engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        # Terminate all connections to the target DB
        print(f"Terminating all connections to '{DBNAME}'...")
        conn.execute(text(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{DBNAME}' AND pid <> pg_backend_pid();"))
        # Drop and recreate
        print(f"Dropping database '{DBNAME}' if it exists...")
        conn.execute(text(f"DROP DATABASE IF EXISTS {DBNAME};"))
        print(f"Creating database '{DBNAME}'...")
        conn.execute(text(f"CREATE DATABASE {DBNAME};"))
    print(f"Database '{DBNAME}' dropped and recreated successfully.")
    # Wait a moment to ensure DB is ready
    time.sleep(2)

def main(recreate_db=False, sql_files=None):
    if recreate_db:
        recreate_database()
    if sql_files is None:
        sql_files = SQL_FILES
    # Check that all files exist
    missing = [f for f in sql_files if not os.path.exists(os.path.join(SCHEMA_DIR, f))]
    if missing:
        print(f"Missing .sql files: {missing}")
        return
    engine = sqlalchemy.create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}")
    with engine.begin() as conn:
        print("Creating tables from SQL_FILES list...")
        for sql_file in sql_files:
            sql_path = os.path.join(SCHEMA_DIR, sql_file)
            print(f"\n=== Executing {sql_file} ===")
            try:
                with open(sql_path, 'r', encoding='utf-8') as f:
                    sql = f.read()
                conn.execute(text(sql))
                print(f"Executed {sql_file} successfully.")
            except Exception as e:
                print(f"[ERROR] Failed to execute {sql_file}: {e}")
        print("\nAll schema .sql files executed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unified Database Schema Creation Script (SQL File Runner)")
    parser.add_argument('--recreate-db', action='store_true', help='Drop and recreate the target database before table creation')
    parser.add_argument('--file', type=str, help='Text file listing .sql files to execute (one per line, default: full_schema.txt)')
    args = parser.parse_args()

    # Get SQL files list
    if args.file:
        sql_files = get_sql_files_from_txt(args.file)
    else:
        # Try to use full_schema.txt if it exists, otherwise fall back to hardcoded list
        default_schema_file = os.path.join(SCHEMA_DIR, 'full_schema.txt')
        if os.path.exists(default_schema_file):
            sql_files = get_sql_files_from_txt(default_schema_file)
        else:
            sql_files = SQL_FILES

    # Call main with both recreate_db flag and sql_files
    main(recreate_db=args.recreate_db, sql_files=sql_files) 