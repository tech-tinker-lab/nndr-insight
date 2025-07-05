#!/usr/bin/env python3
"""
Check the actual structure of master_gazetteer table
"""

import psycopg2
from db_config import get_connection_string

def check_table_structure():
    conn_str = get_connection_string()
    try:
        with psycopg2.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name='master_gazetteer' 
                    ORDER BY ordinal_position
                """)
                columns = cur.fetchall()
                
                print("master_gazetteer table structure:")
                for col in columns:
                    print(f"  - {col[0]} ({col[1]})")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_table_structure() 