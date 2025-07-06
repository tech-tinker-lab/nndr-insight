#!/usr/bin/env python3
"""
Add unique constraint to code_point_open.postcode
"""
import psycopg2
from db_config import get_connection_string

def add_unique_constraint():
    try:
        conn = psycopg2.connect(get_connection_string())
        cur = conn.cursor()
        print("Adding unique constraint to code_point_open.postcode ...")
        cur.execute("""
            ALTER TABLE code_point_open
            ADD CONSTRAINT code_point_open_postcode_unique UNIQUE (postcode);
        """)
        conn.commit()
        conn.close()
        print("✅ Unique constraint added successfully!")
    except Exception as e:
        print(f"❌ Failed to add unique constraint: {e}")
        raise

if __name__ == "__main__":
    add_unique_constraint() 