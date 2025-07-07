import psycopg2
from dotenv import load_dotenv
import os
import time

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

def create_linking_tables():
    """Create tables to store relationships between reference datasets"""
    
    linking_sql = """
    -- 1. UPRN to Postcode Links
    CREATE TABLE IF NOT EXISTS uprn_postcode_links (
        id SERIAL PRIMARY KEY,
        uprn TEXT,
        postcode TEXT,
        distance_meters NUMERIC,
        link_type TEXT DEFAULT 'spatial',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- 2. UPRN to Place Names Links
    CREATE TABLE IF NOT EXISTS uprn_placename_links (
        id SERIAL PRIMARY KEY,
        uprn TEXT,
        place_name_id TEXT,
        place_name TEXT,
        place_type TEXT,
        distance_meters NUMERIC,
        link_type TEXT DEFAULT 'spatial',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- 3. UPRN to Map Features Links
    CREATE TABLE IF NOT EXISTS uprn_mapfeature_links (
        id SERIAL PRIMARY KEY,
        uprn TEXT,
        map_feature_id TEXT,
        feature_code INTEGER,
        distance_meters NUMERIC,
        link_type TEXT DEFAULT 'spatial',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- 4. Postcode to Administrative Areas Links
    CREATE TABLE IF NOT EXISTS postcode_admin_links (
        id SERIAL PRIMARY KEY,
        postcode TEXT,
        lad_code TEXT,
        lad_name TEXT,
        county_code TEXT,
        county_name TEXT,
        region_code TEXT,
        region_name TEXT,
        link_type TEXT DEFAULT 'attribute',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- 5. Place Names to Administrative Areas Links
    CREATE TABLE IF NOT EXISTS placename_admin_links (
        id SERIAL PRIMARY KEY,
        place_name_id TEXT,
        place_name TEXT,
        lad_code TEXT,
        lad_name TEXT,
        county_code TEXT,
        county_name TEXT,
        region_code TEXT,
        region_name TEXT,
        link_type TEXT DEFAULT 'spatial',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Create indexes for performance
    CREATE INDEX IF NOT EXISTS idx_uprn_postcode_uprn ON uprn_postcode_links(uprn);
    CREATE INDEX IF NOT EXISTS idx_uprn_postcode_postcode ON uprn_postcode_links(postcode);
    CREATE INDEX IF NOT EXISTS idx_uprn_placename_uprn ON uprn_placename_links(uprn);
    CREATE INDEX IF NOT EXISTS idx_uprn_mapfeature_uprn ON uprn_mapfeature_links(uprn);
    CREATE INDEX IF NOT EXISTS idx_postcode_admin_postcode ON postcode_admin_links(postcode);
    """
    
    return linking_sql

def link_uprn_to_postcodes(conn):
    """Link UPRNs to nearest postcodes"""
    print("🔗 Linking UPRNs to postcodes...")
    
    sql = """
    INSERT INTO uprn_postcode_links (uprn, postcode, distance_meters, link_type)
    SELECT DISTINCT ON (uprn.uprn) 
           uprn.uprn,
           cp.postcode,
           ST_Distance(uprn.geom, cp.geom) as distance_meters,
           'spatial' as link_type
    FROM os_open_uprn uprn
    CROSS JOIN LATERAL (
        SELECT postcode, geom
        FROM codepoint_open
        WHERE geom IS NOT NULL
        ORDER BY uprn.geom <-> geom
        LIMIT 1
    ) cp
    WHERE uprn.geom IS NOT NULL
    AND ST_Distance(uprn.geom, cp.geom) <= 1000;  -- Within 1km
    """
    
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
        print(f"✅ Linked {cur.rowcount} UPRNs to postcodes")

def link_uprn_to_placenames(conn):
    """Link UPRNs to nearby place names"""
    print("🔗 Linking UPRNs to place names...")
    
    sql = """
    INSERT INTO uprn_placename_links (uprn, place_name_id, place_name, place_type, distance_meters, link_type)
    SELECT DISTINCT ON (uprn.uprn) 
           uprn.uprn,
           names."ID" as place_name_id,
           names."NAME1" as place_name,
           names."TYPE" as place_type,
           ST_Distance(uprn.geom, names.geom) as distance_meters,
           'spatial' as link_type
    FROM os_open_uprn uprn
    CROSS JOIN LATERAL (
        SELECT "ID", "NAME1", "TYPE", geom
        FROM os_open_names
        WHERE geom IS NOT NULL
        AND "TYPE" IN ('Named Place', 'City', 'Town', 'Village')
        ORDER BY uprn.geom <-> geom
        LIMIT 1
    ) names
    WHERE uprn.geom IS NOT NULL
    AND ST_Distance(uprn.geom, names.geom) <= 5000;  -- Within 5km
    """
    
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
        print(f"✅ Linked {cur.rowcount} UPRNs to place names")

def link_uprn_to_mapfeatures(conn):
    """Link UPRNs to nearby map features"""
    print("🔗 Linking UPRNs to map features...")
    
    sql = """
    INSERT INTO uprn_mapfeature_links (uprn, map_feature_id, feature_code, distance_meters, link_type)
    SELECT DISTINCT ON (uprn.uprn) 
           uprn.uprn,
           map.fid as map_feature_id,
           map.feature_code,
           ST_Distance(uprn.geom, map.geom) as distance_meters,
           'spatial' as link_type
    FROM os_open_uprn uprn
    CROSS JOIN LATERAL (
        SELECT fid, feature_code, geom
        FROM os_open_map_local
        WHERE geom IS NOT NULL
        ORDER BY uprn.geom <-> geom
        LIMIT 1
    ) map
    WHERE uprn.geom IS NOT NULL
    AND ST_Distance(uprn.geom, map.geom) <= 100;  -- Within 100m
    """
    
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
        print(f"✅ Linked {cur.rowcount} UPRNs to map features")

def link_postcodes_to_admin(conn):
    """Link postcodes to administrative areas using ONSPD data"""
    print("🔗 Linking postcodes to administrative areas...")
    
    sql = """
    INSERT INTO postcode_admin_links (postcode, lad_code, lad_name, county_code, county_name, region_code, region_name, link_type)
    SELECT DISTINCT
           cp.postcode,
           ons.laua as lad_code,
           ons.launm as lad_name,
           ons.cty as county_code,
           ons.ctynm as county_name,
           ons.rgn as region_code,
           ons.rgnnm as region_name,
           'attribute' as link_type
    FROM codepoint_open cp
    JOIN onspd ons ON cp.postcode = ons.pcds
    WHERE ons.laua IS NOT NULL;
    """
    
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
        print(f"✅ Linked {cur.rowcount} postcodes to administrative areas")

def create_master_reference_view(conn):
    """Create a master view that combines all reference data"""
    print("🔗 Creating master reference view...")
    
    sql = """
    CREATE OR REPLACE VIEW master_reference_data AS
    SELECT 
        uprn.uprn,
        uprn.geom as uprn_geom,
        cp.postcode,
        cp.geom as postcode_geom,
        ons.launm as local_authority,
        ons.ctynm as county,
        ons.rgnnm as region,
        pn.place_name,
        pn.place_type,
        pn.distance_meters as place_distance,
        mf.feature_code,
        mf.distance_meters as feature_distance
    FROM os_open_uprn uprn
    LEFT JOIN uprn_postcode_links upl ON uprn.uprn = upl.uprn
    LEFT JOIN codepoint_open cp ON upl.postcode = cp.postcode
    LEFT JOIN onspd ons ON cp.postcode = ons.pcds
    LEFT JOIN uprn_placename_links pn ON uprn.uprn = pn.uprn
    LEFT JOIN uprn_mapfeature_links mf ON uprn.uprn = mf.uprn
    WHERE uprn.geom IS NOT NULL;
    """
    
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
        print("✅ Created master_reference_data view")

def main():
    print("🔗 Creating Reference Data Links")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        with psycopg2.connect(
            dbname=DBNAME,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        ) as conn:
            
            # Create linking tables
            print("📋 Creating linking tables...")
            with conn.cursor() as cur:
                cur.execute(create_linking_tables())
                conn.commit()
            
            # Create links
            link_uprn_to_postcodes(conn)
            link_uprn_to_placenames(conn)
            link_uprn_to_mapfeatures(conn)
            link_postcodes_to_admin(conn)
            
            # Create master view
            create_master_reference_view(conn)
            
            # Show summary
            print("\n📊 Linking Summary:")
            print("-" * 30)
            
            with conn.cursor() as cur:
                tables = [
                    'uprn_postcode_links',
                    'uprn_placename_links', 
                    'uprn_mapfeature_links',
                    'postcode_admin_links'
                ]
                
                for table in tables:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cur.fetchone()[0]
                    print(f"  {table}: {count:,} links")
            
            elapsed = time.time() - start_time
            print(f"\n✅ Reference data linking completed in {elapsed:.1f} seconds")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main() 