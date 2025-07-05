#!/usr/bin/env python3
"""
Verify that the enhanced schema update was successful
"""

import psycopg2
from db_config import get_connection_string

def verify_schema_update():
    conn_str = get_connection_string()
    try:
        with psycopg2.connect(conn_str) as conn:
            with conn.cursor() as cur:
                # Check new columns in master_gazetteer
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='master_gazetteer' 
                    AND column_name IN ('data_source', 'source_priority', 'duplicate_group_id', 'is_preferred_record') 
                    ORDER BY column_name
                """)
                new_columns = [row[0] for row in cur.fetchall()]
                print("New columns in master_gazetteer:")
                for col in new_columns:
                    print(f"  ✓ {col}")
                
                # Check new tables
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name IN ('data_sources', 'duplicate_management')
                """)
                new_tables = [row[0] for row in cur.fetchall()]
                print("\nNew tables created:")
                for table in new_tables:
                    print(f"  ✓ {table}")
                
                # Check data_sources content
                cur.execute("SELECT COUNT(*) FROM data_sources")
                result = cur.fetchone()
                source_count = result[0] if result else 0
                print(f"\nData sources configured: {source_count}")
                
                if source_count > 0:
                    cur.execute("SELECT source_name, source_priority FROM data_sources ORDER BY source_priority")
                    print("Configured sources:")
                    for row in cur.fetchall():
                        print(f"  - {row[0]} (priority: {row[1]})")
                
                print("\n✓ Schema update verification completed successfully!")
                
    except Exception as e:
        print(f"❌ Schema verification failed: {e}")

if __name__ == "__main__":
    verify_schema_update() 