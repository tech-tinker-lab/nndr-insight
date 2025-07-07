#!/usr/bin/env python3
"""
Check and print database connection details
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('db_setup/.env')

print("=" * 50)
print("DATABASE CONNECTION DETAILS")
print("=" * 50)
print(f"PGUSER: {os.getenv('PGUSER', 'Not set')}")
print(f"PGPASSWORD: {'*' * len(os.getenv('PGPASSWORD', '')) if os.getenv('PGPASSWORD') else 'Not set'}")
print(f"PGHOST: {os.getenv('PGHOST', 'Not set')}")
print(f"PGPORT: {os.getenv('PGPORT', 'Not set')}")
print(f"PGDATABASE: {os.getenv('PGDATABASE', 'Not set')}")
print("=" * 50)

# Test connection
try:
    import psycopg2
    conn = psycopg2.connect(
        dbname=os.getenv('PGDATABASE'),
        user=os.getenv('PGUSER'),
        password=os.getenv('PGPASSWORD'),
        host=os.getenv('PGHOST'),
        port=os.getenv('PGPORT')
    )
    print("✅ Database connection successful!")
    
    # Get database info
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"PostgreSQL Version: {version.split(',')[0]}")
        
        cur.execute("SELECT current_database(), current_user;")
        db_info = cur.fetchone()
        print(f"Current Database: {db_info[0]}")
        print(f"Current User: {db_info[1]}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Database connection failed: {e}") 