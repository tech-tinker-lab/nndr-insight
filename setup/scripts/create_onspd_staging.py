#!/usr/bin/env python3
"""
Create ONSPD staging table
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

def create_onspd_staging_table():
    """Create the onspd_staging table"""
    try:
        with psycopg2.connect(
            dbname=DBNAME,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        ) as conn:
            with conn.cursor() as cur:
                # Create staging table with all columns from CSV
                staging_schema = """
                CREATE TABLE IF NOT EXISTS onspd_staging (
                    x TEXT,
                    y TEXT,
                    objectid TEXT,
                    pcd TEXT,
                    pcd2 TEXT,
                    pcds TEXT,
                    dointr TEXT,
                    doterm TEXT,
                    oscty TEXT,
                    ced TEXT,
                    oslaua TEXT,
                    osward TEXT,
                    parish TEXT,
                    usertype TEXT,
                    oseast1m TEXT,
                    osnrth1m TEXT,
                    osgrdind TEXT,
                    oshlthau TEXT,
                    nhser TEXT,
                    ctry TEXT,
                    rgn TEXT,
                    streg TEXT,
                    pcon TEXT,
                    eer TEXT,
                    teclec TEXT,
                    ttwa TEXT,
                    pct TEXT,
                    itl TEXT,
                    statsward TEXT,
                    oa01 TEXT,
                    casward TEXT,
                    npark TEXT,
                    lsoa01 TEXT,
                    msoa01 TEXT,
                    ur01ind TEXT,
                    oac01 TEXT,
                    oa11 TEXT,
                    lsoa11 TEXT,
                    msoa11 TEXT,
                    wz11 TEXT,
                    sicbl TEXT,
                    bua24 TEXT,
                    ru11ind TEXT,
                    oac11 TEXT,
                    lat TEXT,
                    long TEXT,
                    lep1 TEXT,
                    lep2 TEXT,
                    pfa TEXT,
                    imd TEXT,
                    calncv TEXT,
                    icb TEXT,
                    oa21 TEXT,
                    lsoa21 TEXT,
                    msoa21 TEXT,
                    ruc21ind TEXT,
                    globalid TEXT
                );
                """
                
                cur.execute(staging_schema)
                conn.commit()
                print("✅ onspd_staging table created successfully!")
                
    except Exception as e:
        print(f"❌ Error creating onspd_staging table: {e}")
        raise

if __name__ == "__main__":
    create_onspd_staging_table() 