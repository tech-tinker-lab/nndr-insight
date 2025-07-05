#!/usr/bin/env python3
"""
Script to add admin_district_code and admin_ward_code columns to code_point_open table
"""

import sys
import os
sys.path.append('setup/database')

from db_config import get_connection_string
import psycopg2

def main():
    try:
        conn_string = get_connection_string()
        conn = psycopg2.connect(conn_string)
        print("Connected to database successfully")
        with conn.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE code_point_open
                ADD COLUMN IF NOT EXISTS admin_district_code VARCHAR,
                ADD COLUMN IF NOT EXISTS admin_ward_code VARCHAR;
            """)
        conn.commit()
        print("Columns added successfully.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 