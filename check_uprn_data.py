#!/usr/bin/env python3
"""
Script to examine UPRN table structure and sample data
"""

import sys
import os
sys.path.append('setup/database')

from db_config import get_connection_string
import pandas as pd
import psycopg2

def main():
    try:
        # Connect to database
        conn_string = get_connection_string()
        conn = psycopg2.connect(conn_string)
        print("Connected to database successfully")
        
        # Check table structure
        print("\n=== UPRN Table Structure ===")
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default 
                FROM information_schema.columns 
                WHERE table_name = 'os_open_uprn' 
                ORDER BY ordinal_position
            """)
            result = cursor.fetchall()
        
        for row in result:
            print(f"{row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        # Check record count
        print("\n=== Record Count ===")
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM os_open_uprn")
            count = cursor.fetchone()[0]
        print(f"Total records in os_open_uprn: {count}")
        
        # Show sample data
        if count > 0:
            print("\n=== Sample Data (first 5 records) ===")
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM os_open_uprn LIMIT 5")
                sample_data = cursor.fetchall()
                
                # Get column names
                columns = [desc[0] for desc in cursor.description]
                print("Columns:", columns)
                
                for i, row in enumerate(sample_data, 1):
                    print(f"\nRecord {i}:")
                    for col, val in zip(columns, row):
                        print(f"  {col}: {val}")
        
        # Check for UPRN data files
        print("\n=== Looking for UPRN Data Files ===")
        data_dirs = [
            'backend/data',
            'setup/database/data',
            'data',
            'setup/scripts/data'
        ]
        
        for data_dir in data_dirs:
            if os.path.exists(data_dir):
                print(f"\nChecking directory: {data_dir}")
                try:
                    files = os.listdir(data_dir)
                    uprn_files = [f for f in files if 'uprn' in f.lower() or 'osopenuprn' in f.lower()]
                    if uprn_files:
                        print(f"Found UPRN files: {uprn_files}")
                        for file in uprn_files[:3]:  # Show first 3 files
                            file_path = os.path.join(data_dir, file)
                            if os.path.isfile(file_path):
                                size = os.path.getsize(file_path)
                                print(f"  {file}: {size:,} bytes")
                    else:
                        print("No UPRN files found")
                except Exception as e:
                    print(f"Error reading directory: {e}")
            else:
                print(f"Directory not found: {data_dir}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 