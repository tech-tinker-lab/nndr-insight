#!/usr/bin/env python3
"""
Check ONSPD tables and database connection
"""
import psycopg2
from dotenv import load_dotenv
import os

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

print(f"Database config:")
print(f"  HOST: {HOST}")
print(f"  PORT: {PORT}")
print(f"  DBNAME: {DBNAME}")
print(f"  USER: {USER}")

try:
    with psycopg2.connect(
        dbname=DBNAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    ) as conn:
        with conn.cursor() as cur:
            # Check if onspd table exists
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'onspd');")
            onspd_exists = cur.fetchone()[0]
            print(f"onspd table exists: {onspd_exists}")
            
            # Check if onspd_staging table exists
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'onspd_staging');")
            staging_exists = cur.fetchone()[0]
            print(f"onspd_staging table exists: {staging_exists}")
            
            # If onspd exists, get count
            if onspd_exists:
                cur.execute("SELECT COUNT(*) FROM onspd;")
                count = cur.fetchone()[0]
                print(f"Records in onspd table: {count:,}")
            
            print("✅ Database connection successful!")
            
except Exception as e:
    print(f"❌ Database connection failed: {e}") 