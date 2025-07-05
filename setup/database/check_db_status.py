#!/usr/bin/env python3
"""
Check database status and table information.
"""
import sqlalchemy
from sqlalchemy import text
from db_config import get_connection_string

def check_database_status():
    """Check what tables exist and their row counts."""
    print("🔍 Checking database status...")
    
    try:
        engine = sqlalchemy.create_engine(get_connection_string())
        
        with engine.connect() as conn:
            # Check if any tables exist
            result = conn.execute(text("""
                SELECT schemaname, relname as tablename, n_tup_ins as rows 
                FROM pg_stat_user_tables 
                ORDER BY n_tup_ins DESC
            """))
            
            tables = result.fetchall()
            
            if not tables:
                print("📋 Database is empty - no tables with data found")
                print("   Ready for data ingestion!")
            else:
                print(f"📋 Found {len(tables)} tables with data:")
                for table in tables:
                    schema, table_name, rows = table
                    print(f"   {schema}.{table_name}: {rows:,} rows")
            
            # Check for specific NNDR tables
            print("\n🔍 Checking for NNDR-specific tables...")
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%nndr%'
                ORDER BY table_name
            """))
            
            nndr_tables = result.fetchall()
            if nndr_tables:
                print(f"✅ Found {len(nndr_tables)} NNDR tables:")
                for table in nndr_tables:
                    print(f"   - {table[0]}")
            else:
                print("📝 No NNDR tables found - ready for ingestion")
            
            # Check for reference data tables
            print("\n🔍 Checking for reference data tables...")
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND (table_name LIKE '%postcode%' OR table_name LIKE '%address%' OR table_name LIKE '%uprn%')
                ORDER BY table_name
            """))
            
            ref_tables = result.fetchall()
            if ref_tables:
                print(f"✅ Found {len(ref_tables)} reference data tables:")
                for table in ref_tables:
                    print(f"   - {table[0]}")
            else:
                print("📝 No reference data tables found - ready for ingestion")
                
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False
    
    print("\n✅ Database status check completed!")
    return True

if __name__ == "__main__":
    check_database_status() 