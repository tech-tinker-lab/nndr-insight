#!/usr/bin/env python3
"""
Script to add all missing ONSPD columns to the onspd table
"""

import sys
import os
sys.path.append('setup/database')

from db_config import get_connection_string
import psycopg2

# List of all ONSPD columns and their types (simplified: coordinates and lat/long as DOUBLE PRECISION, rest as TEXT)
COLUMNS = [
    ("x", "DOUBLE PRECISION"),
    ("y", "DOUBLE PRECISION"),
    ("objectid", "TEXT"),
    ("pcd", "TEXT"),
    ("pcd2", "TEXT"),
    ("pcds", "TEXT"),
    ("dointr", "TEXT"),
    ("doterm", "TEXT"),
    ("oscty", "TEXT"),
    ("ced", "TEXT"),
    ("oslaua", "TEXT"),
    ("osward", "TEXT"),
    ("parish", "TEXT"),
    ("usertype", "TEXT"),
    ("oseast1m", "DOUBLE PRECISION"),
    ("osnrth1m", "DOUBLE PRECISION"),
    ("osgrdind", "TEXT"),
    ("oshlthau", "TEXT"),
    ("nhser", "TEXT"),
    ("ctry", "TEXT"),
    ("rgn", "TEXT"),
    ("streg", "TEXT"),
    ("pcon", "TEXT"),
    ("eer", "TEXT"),
    ("teclec", "TEXT"),
    ("ttwa", "TEXT"),
    ("pct", "TEXT"),
    ("itl", "TEXT"),
    ("statsward", "TEXT"),
    ("oa01", "TEXT"),
    ("casward", "TEXT"),
    ("npark", "TEXT"),
    ("lsoa01", "TEXT"),
    ("msoa01", "TEXT"),
    ("ur01ind", "TEXT"),
    ("oac01", "TEXT"),
    ("oa11", "TEXT"),
    ("lsoa11", "TEXT"),
    ("msoa11", "TEXT"),
    ("wz11", "TEXT"),
    ("sicbl", "TEXT"),
    ("bua24", "TEXT"),
    ("ru11ind", "TEXT"),
    ("oac11", "TEXT"),
    ("lat", "DOUBLE PRECISION"),
    ("long", "DOUBLE PRECISION"),
    ("lep1", "TEXT"),
    ("lep2", "TEXT"),
    ("pfa", "TEXT"),
    ("imd", "TEXT"),
    ("calncv", "TEXT"),
    ("icb", "TEXT"),
    ("oa21", "TEXT"),
    ("lsoa21", "TEXT"),
    ("msoa21", "TEXT"),
    ("ruc21ind", "TEXT"),
    ("globalid", "TEXT")
]

def main():
    try:
        conn_string = get_connection_string()
        conn = psycopg2.connect(conn_string)
        print("Connected to database successfully")
        with conn.cursor() as cursor:
            # Get current columns
            cursor.execute("""
                SELECT column_name FROM information_schema.columns WHERE table_name = 'onspd'
            """)
            existing = set(row[0].lower() for row in cursor.fetchall())
            # Add missing columns
            for col, typ in COLUMNS:
                if col.lower() not in existing:
                    print(f"Adding column: {col} {typ}")
                    cursor.execute(f"ALTER TABLE onspd ADD COLUMN IF NOT EXISTS {col} {typ}")
        conn.commit()
        print("All missing columns added successfully.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 