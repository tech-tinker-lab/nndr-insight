#!/usr/bin/env python3
"""
Script to examine onspd table structure and sample data
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
        # Check table structure
        print("\n=== onspd Table Structure ===")
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default 
                FROM information_schema.columns 
                WHERE table_name = 'onspd' 
                ORDER BY ordinal_position
            """)
            result = cursor.fetchall()
            for row in result:
                print(f"{row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        # Check record count
        print("\n=== Record Count ===")
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM onspd")
            count = cursor.fetchone()[0]
            print(f"Total records in onspd: {count}")
        # Show sample data
        if count > 0:
            print("\n=== Sample Data (first 5 records) ===")
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM onspd LIMIT 5")
                sample_data = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                print("Columns:", columns)
                for i, row in enumerate(sample_data, 1):
                    print(f"\nRecord {i}:")
                    for col, val in zip(columns, row):
                        print(f"  {col}: {val}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 