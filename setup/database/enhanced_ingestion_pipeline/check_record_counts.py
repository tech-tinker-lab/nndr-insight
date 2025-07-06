#!/usr/bin/env python3
"""
Check Record Counts for All Reference Data Tables
"""

import psycopg2
from db_config import get_connection_string

def check_record_counts():
    """Check record counts for all reference data tables"""
    
    reference_tables = [
        'os_open_uprn',
        'code_point_open', 
        'onspd',
        'os_open_names',
        'lad_boundaries',
        'os_open_map_local',
        'os_open_usrn'
    ]
    
    try:
        conn = psycopg2.connect(get_connection_string())
        cur = conn.cursor()
        
        print("=" * 60)
        print("CURRENT DATABASE RECORD COUNTS")
        print("=" * 60)
        
        total_records = 0
        
        for table in reference_tables:
            # Check if table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (table,))
            
            if not cur.fetchone()[0]:
                print(f"{table:20}: ❌ Table does not exist")
                continue
            
            # Get record count
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            count = cur.fetchone()[0]
            total_records += count
            
            print(f"{table:20}: {count:>10,} records")
        
        print("-" * 60)
        print(f"{'TOTAL':20}: {total_records:>10,} records")
        print("=" * 60)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking record counts: {e}")
        raise

if __name__ == "__main__":
    check_record_counts() 