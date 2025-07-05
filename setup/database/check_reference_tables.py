#!/usr/bin/env python3
"""
Check the schemas of dedicated reference tables.
"""
import sqlalchemy
from sqlalchemy import text
from db_config import get_connection_string

def check_reference_table_schemas():
    """Check the schemas of os_open_uprn and onspd tables."""
    print("🔍 Checking reference table schemas...")
    
    try:
        engine = sqlalchemy.create_engine(get_connection_string())
        
        with engine.connect() as conn:
            # Check os_open_uprn table
            print("\n📋 OS Open UPRN Table Schema:")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'os_open_uprn' 
                ORDER BY ordinal_position
            """))
            
            os_uprn_columns = result.fetchall()
            if os_uprn_columns:
                print(f"   Found {len(os_uprn_columns)} columns:")
                for col in os_uprn_columns:
                    nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                    default = f" DEFAULT {col[3]}" if col[3] else ""
                    print(f"   - {col[0]}: {col[1]} {nullable}{default}")
            else:
                print("   ❌ Table 'os_open_uprn' not found or empty")
            
            # Check onspd table
            print("\n📋 ONSPD Table Schema:")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'onspd' 
                ORDER BY ordinal_position
            """))
            
            onspd_columns = result.fetchall()
            if onspd_columns:
                print(f"   Found {len(onspd_columns)} columns:")
                for col in onspd_columns:
                    nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                    default = f" DEFAULT {col[3]}" if col[3] else ""
                    print(f"   - {col[0]}: {col[1]} {nullable}{default}")
            else:
                print("   ❌ Table 'onspd' not found or empty")
            
            # Check if tables have data
            print("\n📊 Table Data Counts:")
            for table_name in ['os_open_uprn', 'onspd']:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                print(f"   - {table_name}: {count:,} rows")
                
    except Exception as e:
        print(f"❌ Error checking reference tables: {e}")
        return False
    
    print("\n✅ Reference table schema check completed!")
    return True

if __name__ == "__main__":
    check_reference_table_schemas() 