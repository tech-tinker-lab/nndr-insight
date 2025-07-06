#!/usr/bin/env python3
"""
Fix CodePoint Table Schema
Update VARCHAR field lengths to accommodate the actual data
"""

import psycopg2
from db_config import get_connection_string

def fix_codepoint_schema():
    """Fix the CodePoint table schema"""
    
    try:
        conn = psycopg2.connect(get_connection_string())
        cur = conn.cursor()
        
        print("🔧 Fixing CodePoint table schema...")
        
        # Update VARCHAR field lengths
        alter_queries = [
            "ALTER TABLE code_point_open ALTER COLUMN country_code TYPE VARCHAR(20);",
            "ALTER TABLE code_point_open ALTER COLUMN nhs_regional_ha_code TYPE VARCHAR(20);",
            "ALTER TABLE code_point_open ALTER COLUMN nhs_ha_code TYPE VARCHAR(20);",
            "ALTER TABLE code_point_open ALTER COLUMN admin_county_code TYPE VARCHAR(20);",
            "ALTER TABLE code_point_open ALTER COLUMN admin_district_code TYPE VARCHAR(20);",
            "ALTER TABLE code_point_open ALTER COLUMN admin_ward_code TYPE VARCHAR(20);"
        ]
        
        for query in alter_queries:
            cur.execute(query)
            print(f"✅ Executed: {query}")
        
        conn.commit()
        conn.close()
        print("✅ CodePoint table schema fixed successfully!")
        
    except Exception as e:
        print(f"❌ Failed to fix CodePoint schema: {e}")
        raise

if __name__ == "__main__":
    fix_codepoint_schema() 