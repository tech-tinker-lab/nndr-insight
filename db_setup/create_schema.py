import os
import sys
import argparse
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

"""
create_schema.py: Unified Database Schema Creation Script (SQL File Runner)

Changelog:
- v1.0: Initial version, executes hardcoded SQL_FILES list.
- v1.1: Enhanced to accept a text file (--file) listing .sql files to execute, one per line. If not provided, uses default SQL_FILES list. (2024-06-10)
- v1.1: Updated to include all staging and master tables for reference, postcode, address, and street datasets. (2024-06-10)

Usage:
    python create_schema.py [--drop] [--file schema_files.txt]

- If --drop is provided, all relevant tables are dropped before creation (fresh start).
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

engine = sqlalchemy.create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}")

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), 'schemas')

# List the .sql files in the exact order you want them executed
SQL_FILES = [
    # Reference tables (staging and master)
    'reference/os_open_uprn_staging.sql',
    'reference/os_open_uprn.sql',
    'reference/nndr_rating_list_staging.sql',
    'reference/nndr_rating_list.sql',
    'reference/nndr_ratepayers_staging.sql',
    'reference/nndr_ratepayers.sql',
    'reference/nndr_summary_valuation_staging.sql',
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
    'street/usrn_streets.sql',
]

def get_sql_files_from_txt(file_path):
    files = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                files.append(line)
    return files

def main(drop_tables=False):
    # Check that all files exist
    missing = [f for f in SQL_FILES if not os.path.exists(os.path.join(SCHEMA_DIR, f))]
    if missing:
        print(f"Missing .sql files: {missing}")
        return

    with engine.begin() as conn:
        if drop_tables:
            print("Dropping all tables defined in SQL_FILES list...")
            for sql_file in SQL_FILES:
                table_name = os.path.splitext(sql_file)[0]
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE;"))
                    print(f"Dropped table {table_name}.")
                except Exception as e:
                    print(f"[ERROR] Could not drop table {table_name}: {e}")
            print("All relevant tables dropped.")

        print("Creating tables from SQL_FILES list...")
        for sql_file in SQL_FILES:
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
    parser.add_argument('--drop', action='store_true', help='Drop all relevant tables before creation')
    parser.add_argument('--file', type=str, help='Text file listing .sql files to execute (one per line)')
    args = parser.parse_args()

    if args.file:
        sql_files = get_sql_files_from_txt(args.file)
    else:
        sql_files = SQL_FILES
    
    def main_with_files(drop_tables, sql_files):
        # Check that all files exist
        missing = [f for f in sql_files if not os.path.exists(os.path.join(SCHEMA_DIR, f))]
        if missing:
            print(f"Missing .sql files: {missing}")
            return

        with engine.begin() as conn:
            if drop_tables:
                print("Dropping all tables defined in SQL_FILES list...")
                for sql_file in sql_files:
                    table_name = os.path.splitext(sql_file)[0]
                    try:
                        conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE;"))
                        print(f"Dropped table {table_name}.")
                    except Exception as e:
                        print(f"[ERROR] Could not drop table {table_name}: {e}")
                print("All relevant tables dropped.")

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

    main_with_files(args.drop, sql_files) 