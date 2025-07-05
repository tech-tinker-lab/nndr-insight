#!/usr/bin/env python3
"""
Script to create os_open_map_local table
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
        
        # Create os_open_map_local table
        print("\n=== Creating os_open_map_local table ===")
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS os_open_map_local (
                    id SERIAL PRIMARY KEY,
                    feature_id VARCHAR(255) NOT NULL,
                    feature_type VARCHAR(100),
                    theme VARCHAR(100),
                    geometry GEOMETRY(GEOMETRY, 27700),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create spatial index
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_os_open_map_local_geometry 
                ON os_open_map_local USING GIST (geometry)
            """)
            
            # Create index on feature_id
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_os_open_map_local_feature_id 
                ON os_open_map_local (feature_id)
            """)
            
            # Create index on feature_type
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_os_open_map_local_feature_type 
                ON os_open_map_local (feature_type)
            """)
            
            # Create index on theme
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_os_open_map_local_theme 
                ON os_open_map_local (theme)
            """)
            
            conn.commit()
            print("os_open_map_local table created successfully")
        
        # Verify table structure
        print("\n=== Verifying table structure ===")
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default 
                FROM information_schema.columns 
                WHERE table_name = 'os_open_map_local' 
                ORDER BY ordinal_position
            """)
            result = cursor.fetchall()
            for row in result:
                print(f"{row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        # Check record count
        print("\n=== Record Count ===")
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM os_open_map_local")
            count = cursor.fetchone()[0]
            print(f"Total records in os_open_map_local: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 