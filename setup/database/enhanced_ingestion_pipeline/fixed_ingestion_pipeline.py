#!/usr/bin/env python3
"""
Fixed Data Ingestion Pipeline
Properly handles actual data formats and fixes all schema issues
"""

import psycopg2
import pandas as pd
import geopandas as gpd
import logging
import os
import glob
from typing import Dict, List, Optional, Tuple
from db_config import get_connection_string

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FixedIngestionPipeline:
    def __init__(self, data_directory: str = None):
        self.data_directory = data_directory or "../../../backend/data"
        self.conn_string = get_connection_string()
        
    def fix_database_schemas(self):
        """Fix all database schemas to match actual data formats"""
        logger.info("🔧 Fixing database schemas...")
        
        try:
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            
            # Fix CodePoint table - postcode field is already correct (VARCHAR(16))
            logger.info("✅ CodePoint table schema is correct")
            
            # Fix ONSPD table - create proper schema
            logger.info("🔧 Fixing ONSPD table schema...")
            cur.execute("""
                DROP TABLE IF EXISTS onspd CASCADE;
                CREATE TABLE onspd (
                    id SERIAL PRIMARY KEY,
                    pcd VARCHAR(10),
                    pcd2 VARCHAR(10),
                    pcds VARCHAR(10),
                    dointr DATE,
                    doterm DATE,
                    oscty VARCHAR(10),
                    ced VARCHAR(10),
                    oslaua VARCHAR(10),
                    osward VARCHAR(10),
                    parish VARCHAR(10),
                    usertype VARCHAR(10),
                    oseast1m INTEGER,
                    osnrth1m INTEGER,
                    osgrdind VARCHAR(10),
                    oshlthau VARCHAR(10),
                    nhser VARCHAR(10),
                    ctry VARCHAR(10),
                    rgn VARCHAR(10),
                    streg VARCHAR(10),
                    pcon VARCHAR(10),
                    eer VARCHAR(10),
                    teclec VARCHAR(10),
                    ttwa VARCHAR(10),
                    pct VARCHAR(10),
                    itl VARCHAR(10),
                    statsward VARCHAR(10),
                    oa01 VARCHAR(10),
                    casward VARCHAR(10),
                    npark VARCHAR(10),
                    lsoa01 VARCHAR(10),
                    msoa01 VARCHAR(10),
                    ur01ind VARCHAR(10),
                    oac01 VARCHAR(10),
                    oa11 VARCHAR(10),
                    lsoa11 VARCHAR(10),
                    msoa11 VARCHAR(10),
                    wz11 VARCHAR(10),
                    sicbl VARCHAR(10),
                    bua24 VARCHAR(10),
                    ru11ind VARCHAR(10),
                    oac11 VARCHAR(10),
                    lat DOUBLE PRECISION,
                    long DOUBLE PRECISION,
                    lep1 VARCHAR(10),
                    lep2 VARCHAR(10),
                    pfa VARCHAR(10),
                    imd VARCHAR(10),
                    calncv VARCHAR(10),
                    icb VARCHAR(10),
                    oa21 VARCHAR(10),
                    lsoa21 VARCHAR(10),
                    msoa21 VARCHAR(10),
                    ruc21ind VARCHAR(10),
                    globalid VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Fix OS Open Names table - create proper schema
            logger.info("🔧 Fixing OS Open Names table schema...")
            cur.execute("""
                DROP TABLE IF EXISTS os_open_names CASCADE;
                CREATE TABLE os_open_names (
                    id SERIAL PRIMARY KEY,
                    os_id VARCHAR(50),
                    names_uri TEXT,
                    name1 VARCHAR(255),
                    name1_lang VARCHAR(10),
                    name2 VARCHAR(255),
                    name2_lang VARCHAR(10),
                    type VARCHAR(100),
                    local_type VARCHAR(100),
                    geometry_x DOUBLE PRECISION,
                    geometry_y DOUBLE PRECISION,
                    most_detail_view_res INTEGER,
                    least_detail_view_res INTEGER,
                    mbr_xmin DOUBLE PRECISION,
                    mbr_ymin DOUBLE PRECISION,
                    mbr_xmax DOUBLE PRECISION,
                    mbr_ymax DOUBLE PRECISION,
                    postcode_district VARCHAR(10),
                    postcode_district_uri TEXT,
                    populated_place VARCHAR(255),
                    populated_place_uri TEXT,
                    admin_area VARCHAR(255),
                    admin_area_uri TEXT,
                    country VARCHAR(100),
                    country_uri TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create OS Open USRN table
            logger.info("🔧 Creating OS Open USRN table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS os_open_usrn (
                    id SERIAL PRIMARY KEY,
                    usrn VARCHAR(20),
                    street_name VARCHAR(255),
                    locality VARCHAR(255),
                    town VARCHAR(255),
                    administrative_area VARCHAR(255),
                    postcode VARCHAR(10),
                    geometry_x DOUBLE PRECISION,
                    geometry_y DOUBLE PRECISION,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ Database schemas fixed successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to fix database schemas: {e}")
            raise
    
    def ingest_codepoint_data(self):
        """Ingest CodePoint data with proper schema"""
        logger.info("📁 Ingesting CodePoint data...")
        
        try:
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            
            # Get all CodePoint CSV files
            codepoint_dir = os.path.join(self.data_directory, "codepo_gb/Data/CSV")
            csv_files = glob.glob(os.path.join(codepoint_dir, "*.csv"))
            
            total_inserted = 0
            
            for file_path in csv_files:
                logger.info(f"Processing: {os.path.basename(file_path)}")
                
                # Read CSV with proper column names
                df = pd.read_csv(file_path, header=None, names=[
                    'postcode', 'positional_quality_indicator', 'eastings', 'northings',
                    'country_code', 'nhs_regional_ha_code', 'nhs_ha_code', 'admin_county_code',
                    'admin_district_code', 'admin_ward_code'
                ])
                
                # Clean data
                df['postcode'] = df['postcode'].str.strip().str.upper()
                df = df.dropna(subset=['postcode'])
                
                # Insert data
                for _, row in df.iterrows():
                    cur.execute("""
                        INSERT INTO code_point_open (
                            postcode, positional_quality_indicator, eastings, northings,
                            country_code, nhs_regional_ha_code, nhs_ha_code, admin_county_code,
                            admin_district_code, admin_ward_code
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (postcode) DO NOTHING
                    """, (
                        row['postcode'], row['positional_quality_indicator'], row['eastings'], row['northings'],
                        row['country_code'], row['nhs_regional_ha_code'], row['nhs_ha_code'], row['admin_county_code'],
                        row['admin_district_code'], row['admin_ward_code']
                    ))
                
                total_inserted += len(df)
                logger.info(f"Inserted {len(df)} records from {os.path.basename(file_path)}")
            
            conn.commit()
            conn.close()
            logger.info(f"✅ CodePoint ingestion complete: {total_inserted:,} records")
            
        except Exception as e:
            logger.error(f"❌ CodePoint ingestion failed: {e}")
            raise
    
    def ingest_onspd_data(self):
        """Ingest ONSPD data with proper schema"""
        logger.info("📁 Ingesting ONSPD data...")
        
        try:
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            
            onspd_file = os.path.join(self.data_directory, "ONSPD_Online_Latest_Centroids.csv")
            
            # Read in chunks to handle large file
            chunk_size = 10000
            total_inserted = 0
            
            for chunk in pd.read_csv(onspd_file, chunksize=chunk_size):
                # Clean and prepare data
                chunk = chunk.fillna('')
                
                for _, row in chunk.iterrows():
                    cur.execute("""
                        INSERT INTO onspd (
                            pcd, pcd2, pcds, dointr, doterm, oscty, ced, oslaua, osward, parish,
                            usertype, oseast1m, osnrth1m, osgrdind, oshlthau, nhser, ctry, rgn,
                            streg, pcon, eer, teclec, ttwa, pct, itl, statsward, oa01, casward,
                            npark, lsoa01, msoa01, ur01ind, oac01, oa11, lsoa11, msoa11, wz11,
                            sicbl, bua24, ru11ind, oac11, lat, long, lep1, lep2, pfa, imd,
                            calncv, icb, oa21, lsoa21, msoa21, ruc21ind, globalid
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (pcd) DO NOTHING
                    """, (
                        row['PCD'], row['PCD2'], row['PCDS'], row['DOINTR'], row['DOTERM'], row['OSCTY'], row['CED'], row['OSLAUA'], row['OSWARD'], row['PARISH'],
                        row['USERTYPE'], row['OSEAST1M'], row['OSNRTH1M'], row['OSGRDIND'], row['OSHLTHAU'], row['NHSER'], row['CTRY'], row['RGN'],
                        row['STREG'], row['PCON'], row['EER'], row['TECLEC'], row['TTWA'], row['PCT'], row['ITL'], row['STATSWARD'], row['OA01'], row['CASWARD'],
                        row['NPARK'], row['LSOA01'], row['MSOA01'], row['UR01IND'], row['OAC01'], row['OA11'], row['LSOA11'], row['MSOA11'], row['WZ11'],
                        row['SICBL'], row['BUA24'], row['RU11IND'], row['OAC11'], row['LAT'], row['LONG'], row['LEP1'], row['LEP2'], row['PFA'], row['IMD'],
                        row['CALNCV'], row['ICB'], row['OA21'], row['LSOA21'], row['MSOA21'], row['RUC21IND'], row['GlobalID']
                    ))
                
                total_inserted += len(chunk)
                logger.info(f"Processed {total_inserted:,} records...")
            
            conn.commit()
            conn.close()
            logger.info(f"✅ ONSPD ingestion complete: {total_inserted:,} records")
            
        except Exception as e:
            logger.error(f"❌ ONSPD ingestion failed: {e}")
            raise
    
    def ingest_os_open_names_data(self):
        """Ingest OS Open Names data with proper schema"""
        logger.info("📁 Ingesting OS Open Names data...")
        
        try:
            conn = psycopg2.connect(self.conn_string)
            cur = conn.cursor()
            
            # Get all OS Open Names CSV files
            names_dir = os.path.join(self.data_directory, "opname_csv_gb/Data")
            csv_files = glob.glob(os.path.join(names_dir, "*.csv"))
            
            total_inserted = 0
            
            for file_path in csv_files:
                logger.info(f"Processing: {os.path.basename(file_path)}")
                
                # Read CSV - OS Open Names has a specific format
                df = pd.read_csv(file_path)
                
                # Map columns based on actual data structure
                for _, row in df.iterrows():
                    # Extract data from the complex structure
                    os_id = str(row.iloc[0]) if pd.notna(row.iloc[0]) else None
                    names_uri = str(row.iloc[1]) if pd.notna(row.iloc[1]) else None
                    name1 = str(row.iloc[2]) if pd.notna(row.iloc[2]) else None
                    name1_lang = str(row.iloc[3]) if pd.notna(row.iloc[3]) else None
                    name2 = str(row.iloc[4]) if pd.notna(row.iloc[4]) else None
                    name2_lang = str(row.iloc[5]) if pd.notna(row.iloc[5]) else None
                    type_val = str(row.iloc[6]) if pd.notna(row.iloc[6]) else None
                    local_type = str(row.iloc[7]) if pd.notna(row.iloc[7]) else None
                    
                    # Extract coordinates
                    geometry_x = float(row.iloc[8]) if pd.notna(row.iloc[8]) else None
                    geometry_y = float(row.iloc[9]) if pd.notna(row.iloc[9]) else None
                    
                    # Extract other fields
                    most_detail_view_res = int(row.iloc[10]) if pd.notna(row.iloc[10]) else None
                    least_detail_view_res = int(row.iloc[11]) if pd.notna(row.iloc[11]) else None
                    
                    # Extract bounding box
                    mbr_xmin = float(row.iloc[12]) if pd.notna(row.iloc[12]) else None
                    mbr_ymin = float(row.iloc[13]) if pd.notna(row.iloc[13]) else None
                    mbr_xmax = float(row.iloc[14]) if pd.notna(row.iloc[14]) else None
                    mbr_ymax = float(row.iloc[15]) if pd.notna(row.iloc[15]) else None
                    
                    # Extract postcode district
                    postcode_district = str(row.iloc[16]) if pd.notna(row.iloc[16]) else None
                    postcode_district_uri = str(row.iloc[17]) if pd.notna(row.iloc[17]) else None
                    
                    # Extract populated place
                    populated_place = str(row.iloc[18]) if pd.notna(row.iloc[18]) else None
                    populated_place_uri = str(row.iloc[19]) if pd.notna(row.iloc[19]) else None
                    
                    # Extract admin area
                    admin_area = str(row.iloc[20]) if pd.notna(row.iloc[20]) else None
                    admin_area_uri = str(row.iloc[21]) if pd.notna(row.iloc[21]) else None
                    
                    # Extract country
                    country = str(row.iloc[22]) if pd.notna(row.iloc[22]) else None
                    country_uri = str(row.iloc[23]) if pd.notna(row.iloc[23]) else None
                    
                    cur.execute("""
                        INSERT INTO os_open_names (
                            os_id, names_uri, name1, name1_lang, name2, name2_lang, type, local_type,
                            geometry_x, geometry_y, most_detail_view_res, least_detail_view_res,
                            mbr_xmin, mbr_ymin, mbr_xmax, mbr_ymax, postcode_district, postcode_district_uri,
                            populated_place, populated_place_uri, admin_area, admin_area_uri, country, country_uri
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (os_id) DO NOTHING
                    """, (
                        os_id, names_uri, name1, name1_lang, name2, name2_lang, type_val, local_type,
                        geometry_x, geometry_y, most_detail_view_res, least_detail_view_res,
                        mbr_xmin, mbr_ymin, mbr_xmax, mbr_ymax, postcode_district, postcode_district_uri,
                        populated_place, populated_place_uri, admin_area, admin_area_uri, country, country_uri
                    ))
                
                total_inserted += len(df)
                logger.info(f"Inserted {len(df)} records from {os.path.basename(file_path)}")
            
            conn.commit()
            conn.close()
            logger.info(f"✅ OS Open Names ingestion complete: {total_inserted:,} records")
            
        except Exception as e:
            logger.error(f"❌ OS Open Names ingestion failed: {e}")
            raise
    
    def run_complete_ingestion(self):
        """Run the complete fixed ingestion pipeline"""
        logger.info("🚀 Starting Fixed Data Ingestion Pipeline")
        
        try:
            # Step 1: Fix database schemas
            self.fix_database_schemas()
            
            # Step 2: Ingest CodePoint data
            self.ingest_codepoint_data()
            
            # Step 3: Ingest ONSPD data
            self.ingest_onspd_data()
            
            # Step 4: Ingest OS Open Names data
            self.ingest_os_open_names_data()
            
            logger.info("✅ Fixed Data Ingestion Pipeline completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Fixed Data Ingestion Pipeline failed: {e}")
            raise

if __name__ == "__main__":
    pipeline = FixedIngestionPipeline()
    pipeline.run_complete_ingestion() 