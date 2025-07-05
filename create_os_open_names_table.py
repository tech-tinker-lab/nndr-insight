#!/usr/bin/env python3
"""
Script to create the os_open_names table with all columns from OS Open Names CSV
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
        
        # Create table with all OS Open Names columns
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS os_open_names (
            id SERIAL PRIMARY KEY,
            os_id TEXT,
            names_uri TEXT,
            name1 TEXT,
            name1_lang TEXT,
            name2 TEXT,
            name2_lang TEXT,
            type TEXT,
            local_type TEXT,
            geometry_x DOUBLE PRECISION,
            geometry_y DOUBLE PRECISION,
            most_detail_view_res INTEGER,
            least_detail_view_res INTEGER,
            mbr_xmin DOUBLE PRECISION,
            mbr_ymin DOUBLE PRECISION,
            mbr_xmax DOUBLE PRECISION,
            mbr_ymax DOUBLE PRECISION,
            postcode_district TEXT,
            postcode_district_uri TEXT,
            populated_place TEXT,
            populated_place_uri TEXT,
            populated_place_type TEXT,
            district_borough TEXT,
            district_borough_uri TEXT,
            district_borough_type TEXT,
            county_unitary TEXT,
            county_unitary_uri TEXT,
            county_unitary_type TEXT,
            region TEXT,
            region_uri TEXT,
            country TEXT,
            country_uri TEXT,
            related_spatial_object TEXT,
            same_as_dbpedia TEXT,
            same_as_geonames TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        with conn.cursor() as cursor:
            cursor.execute(create_table_sql)
        
        conn.commit()
        print("os_open_names table created successfully.")
        
        # Verify table structure
        print("\n=== os_open_names Table Structure ===")
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default 
                FROM information_schema.columns 
                WHERE table_name = 'os_open_names' 
                ORDER BY ordinal_position
            """)
            result = cursor.fetchall()
            for row in result:
                print(f"{row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 