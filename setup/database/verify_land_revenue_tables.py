#!/usr/bin/env python3
"""
Verify that all land revenue and property sales tables were created successfully
"""

import psycopg2
from db_config import get_connection_string

def verify_land_revenue_tables():
    conn_str = get_connection_string()
    try:
        with psycopg2.connect(conn_str) as conn:
            with conn.cursor() as cur:
                # Check for new tables
                new_tables = [
                    'property_sales',
                    'land_revenue', 
                    'property_valuations',
                    'market_analysis',
                    'economic_indicators'
                ]
                
                print("Land Revenue and Property Sales Tables:")
                for table in new_tables:
                    cur.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = %s
                        )
                    """, (table,))
                    result = cur.fetchone()
                    exists = result[0] if result else False
                    status = "✓" if exists else "❌"
                    print(f"  {status} {table}")
                
                # Show column structure for key tables
                print("\nProperty Sales table structure:")
                cur.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name='property_sales' 
                    ORDER BY ordinal_position
                """)
                columns = cur.fetchall()
                for col in columns:
                    print(f"  - {col[0]} ({col[1]})")
                
                print("\nLand Revenue table structure:")
                cur.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name='land_revenue' 
                    ORDER BY ordinal_position
                """)
                columns = cur.fetchall()
                for col in columns:
                    print(f"  - {col[0]} ({col[1]})")
                
                # Check indexes
                print("\nIndexes created:")
                index_tables = ['property_sales', 'land_revenue', 'property_valuations', 'market_analysis', 'economic_indicators']
                for table in index_tables:
                    cur.execute("""
                        SELECT indexname 
                        FROM pg_indexes 
                        WHERE tablename = %s
                    """, (table,))
                    indexes = cur.fetchall()
                    if indexes:
                        print(f"  {table}:")
                        for idx in indexes:
                            print(f"    - {idx[0]}")
                
                print("\n✓ Land revenue and property sales schema verification completed!")
                
    except Exception as e:
        print(f"❌ Schema verification failed: {e}")

if __name__ == "__main__":
    verify_land_revenue_tables() 