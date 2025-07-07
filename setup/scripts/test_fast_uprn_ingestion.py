#!/usr/bin/env python3
"""
Test script for fast OS UPRN data ingestion
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

# Database configuration
USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

def get_connection():
    """Get database connection"""
    return psycopg2.connect(
        dbname=DBNAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )

def test_table_exists():
    """Test if os_open_uprn table exists and has correct schema"""
    print("Testing table existence and schema...")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Check if table exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'os_open_uprn'
                    );
                """)
                table_exists = cur.fetchone()[0]
                
                if not table_exists:
                    print("❌ os_open_uprn table does not exist")
                    return False
                
                print("✅ os_open_uprn table exists")
                
                # Check table schema
                cur.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'os_open_uprn' 
                    ORDER BY ordinal_position
                """)
                columns = cur.fetchall()
                
                print("\nTable Schema:")
                print("-" * 60)
                for col in columns:
                    print(f"{col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
                
                # Check if UPRN is primary key
                cur.execute("""
                    SELECT COUNT(*) FROM information_schema.table_constraints 
                    WHERE table_name = 'os_open_uprn' 
                    AND constraint_type = 'PRIMARY KEY'
                """)
                pk_count = cur.fetchone()[0]
                
                if pk_count > 0:
                    print("\n✅ UPRN is set as PRIMARY KEY")
                else:
                    print("\n❌ UPRN is not set as PRIMARY KEY")
                    return False
                
                return True
                
    except Exception as e:
        print(f"❌ Error testing table: {e}")
        return False

def test_data_loaded():
    """Test if data has been loaded into the table"""
    print("\nTesting data loading...")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Check record count
                cur.execute("SELECT COUNT(*) FROM os_open_uprn;")
                count = cur.fetchone()[0]
                
                if count == 0:
                    print("❌ No data found in os_open_uprn table")
                    return False
                
                print(f"✅ Found {count:,} records in os_open_uprn table")
                
                # Check for sample data
                cur.execute("SELECT * FROM os_open_uprn LIMIT 3;")
                sample_data = cur.fetchall()
                
                print("\nSample Data:")
                print("-" * 60)
                for i, row in enumerate(sample_data, 1):
                    print(f"Record {i}: UPRN={row[0]}, X={row[1]}, Y={row[2]}, Lat={row[3]}, Lon={row[4]}")
                
                # Check for null UPRNs
                cur.execute("SELECT COUNT(*) FROM os_open_uprn WHERE uprn IS NULL;")
                null_count = cur.fetchone()[0]
                
                if null_count > 0:
                    print(f"⚠️  Found {null_count} records with null UPRN")
                else:
                    print("✅ No null UPRN values found")
                
                return True
                
    except Exception as e:
        print(f"❌ Error testing data: {e}")
        return False

def test_indexes():
    """Test if performance indexes exist"""
    print("\nTesting indexes...")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Check for indexes
                cur.execute("""
                    SELECT indexname, indexdef 
                    FROM pg_indexes 
                    WHERE tablename = 'os_open_uprn'
                """)
                indexes = cur.fetchall()
                
                if not indexes:
                    print("❌ No indexes found on os_open_uprn table")
                    return False
                
                print("✅ Found indexes:")
                for index in indexes:
                    print(f"  - {index[0]}")
                
                return True
                
    except Exception as e:
        print(f"❌ Error testing indexes: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("FAST OS UPRN INGESTION TEST")
    print("=" * 60)
    
    tests = [
        ("Table Existence and Schema", test_table_exists),
        ("Data Loading", test_data_loaded),
        ("Performance Indexes", test_indexes)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Fast UPRN ingestion is working correctly.")
        return True
    else:
        print("💥 Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 