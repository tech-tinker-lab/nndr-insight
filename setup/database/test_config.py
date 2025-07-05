#!/usr/bin/env python3
"""
Test script to verify database configuration and connection.
"""
import sqlalchemy
from sqlalchemy import text
from db_config import get_connection_string, print_config, DB_CONFIG

def test_connection():
    """Test database connection."""
    print("Testing database configuration...")
    print_config()
    
    try:
        # Test connection to postgres database
        print("\n🔍 Testing connection to postgres database...")
        admin_engine = sqlalchemy.create_engine(get_connection_string("postgres"))
        with admin_engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL: {version}")
        
        # Test connection to target database
        print(f"\n🔍 Testing connection to target database '{DB_CONFIG['DBNAME']}'...")
        engine = sqlalchemy.create_engine(get_connection_string())
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"✅ Connected to database: {db_name}")
            
            # Test PostGIS extension
            result = conn.execute(text("SELECT PostGIS_Version()"))
            postgis_version = result.scalar()
            print(f"✅ PostGIS version: {postgis_version}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    print("\n✅ All connection tests passed!")
    return True

if __name__ == "__main__":
    test_connection() 