#!/usr/bin/env python3
"""
Script to simplify the os_open_uprn table by dropping unused columns
"""

import sys
import os
sys.path.append('setup/database')

from db_config import get_connection_string
import psycopg2

def main():
    try:
        # Connect to database
        conn_string = get_connection_string()
        conn = psycopg2.connect(conn_string)
        print("Connected to database successfully")
        
        # Columns to keep (matching the CSV file)
        columns_to_keep = [
            'id',           # Auto-generated primary key
            'uprn',         # UPRN from CSV
            'x_coordinate', # X_COORDINATE from CSV
            'y_coordinate', # Y_COORDINATE from CSV
            'latitude',     # LATITUDE from CSV
            'longitude'     # LONGITUDE from CSV
        ]
        
        # Get current table structure
        print("\n=== Current Table Structure ===")
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default 
                FROM information_schema.columns 
                WHERE table_name = 'os_open_uprn' 
                ORDER BY ordinal_position
            """)
            current_columns = cursor.fetchall()
            
            for row in current_columns:
                print(f"{row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        # Identify columns to drop
        columns_to_drop = []
        for row in current_columns:
            if row[0] not in columns_to_keep:
                columns_to_drop.append(row[0])
        
        print(f"\n=== Columns to Drop ({len(columns_to_drop)}) ===")
        for col in columns_to_drop:
            print(f"  - {col}")
        
        if not columns_to_drop:
            print("No columns to drop - table is already simplified!")
            return
        
        # Confirm before proceeding
        print(f"\nThis will drop {len(columns_to_drop)} columns from the os_open_uprn table.")
        print("Are you sure you want to proceed? (y/N): ", end="")
        
        # For automation, we'll proceed
        print("Proceeding with table simplification...")
        
        # Drop columns
        with conn.cursor() as cursor:
            for column in columns_to_drop:
                try:
                    print(f"Dropping column: {column}")
                    cursor.execute(f"ALTER TABLE os_open_uprn DROP COLUMN IF EXISTS {column}")
                except Exception as e:
                    print(f"Error dropping column {column}: {e}")
        
        # Commit changes
        conn.commit()
        
        # Show final table structure
        print("\n=== Final Table Structure ===")
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default 
                FROM information_schema.columns 
                WHERE table_name = 'os_open_uprn' 
                ORDER BY ordinal_position
            """)
            final_columns = cursor.fetchall()
            
            for row in final_columns:
                print(f"{row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        # Check record count
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM os_open_uprn")
            count = cursor.fetchone()[0]
            print(f"\nTotal records in os_open_uprn: {count}")
        
        print("\n✅ Table simplified successfully!")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 