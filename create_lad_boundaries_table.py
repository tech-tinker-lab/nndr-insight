#!/usr/bin/env python3
"""
Script to create lad_boundaries table
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
        
        # Create lad_boundaries table
        print("\n=== Creating lad_boundaries table ===")
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lad_boundaries (
                    id SERIAL PRIMARY KEY,
                    lad_code VARCHAR(10) NOT NULL,
                    lad_name VARCHAR(255) NOT NULL,
                    geometry GEOMETRY(MULTIPOLYGON, 27700),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create spatial index
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_lad_boundaries_geometry 
                ON lad_boundaries USING GIST (geometry)
            """)
            
            # Create index on lad_code
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_lad_boundaries_lad_code 
                ON lad_boundaries (lad_code)
            """)
            
            conn.commit()
            print("lad_boundaries table created successfully")
        
        # Verify table structure
        print("\n=== Verifying table structure ===")
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default 
                FROM information_schema.columns 
                WHERE table_name = 'lad_boundaries' 
                ORDER BY ordinal_position
            """)
            result = cursor.fetchall()
            for row in result:
                print(f"{row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        # Check record count
        print("\n=== Record Count ===")
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM lad_boundaries")
            count = cursor.fetchone()[0]
            print(f"Total records in lad_boundaries: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 