#!/usr/bin/env python3
"""
Script to add missing tables to an existing database.
Supports environment variables for database connection.
"""
import sqlalchemy
from sqlalchemy import text
from db_config import get_connection_string, print_config, DB_CONFIG

def create_engine_for_db(dbname):
    return sqlalchemy.create_engine(get_connection_string(dbname))

def run_ddl(engine, ddl):
    with engine.connect() as conn:
        with conn.begin():
            for stmt in ddl:
                conn.execute(text(stmt))

def main():
    # Print current configuration
    print_config()
    
    # Connect to the existing DB
    engine = create_engine_for_db(DB_CONFIG['DBNAME'])
    
    # DDL for missing tables
    ddl = [
        # OS Open Map Local
        """
        CREATE TABLE IF NOT EXISTS os_open_map_local (
            id SERIAL PRIMARY KEY,
            feature_id TEXT,
            feature_type TEXT,
            feature_description TEXT,
            theme TEXT,
            geometry GEOMETRY(Geometry, 27700),
            source TEXT
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS os_open_map_local_geom_idx ON os_open_map_local USING GIST (geometry);
        """,
        # OS Open Map Local Staging
        """
        CREATE TABLE IF NOT EXISTS os_open_map_local_staging (
            feature_id TEXT,
            feature_type TEXT,
            feature_description TEXT,
            theme TEXT,
            geometry GEOMETRY(Geometry, 27700),
            source TEXT
        );
        """,
        # Add any other missing tables here
    ]
    
    try:
        run_ddl(engine, ddl)
        print("✅ Missing tables added successfully.")
    except Exception as e:
        print(f"❌ Error adding tables: {e}")
        raise

if __name__ == '__main__':
    main() 