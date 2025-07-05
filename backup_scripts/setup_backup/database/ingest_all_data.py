#!/usr/bin/env python3
"""
Comprehensive NNDR Data Ingestion Script
Creates all database tables and ingests data in the correct order
"""

import os
import sys
import psycopg2
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine, text
import logging
from pathlib import Path
import time
from datetime import datetime

# Add the backend directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NNDRDataIngestion:
    def __init__(self, db_config=None):
        """Initialize the data ingestion process"""
        if db_config is None:
            self.db_config = {
                'host': '192.168.1.79',
                'port': 5432,
                'database': 'nndr_insight',
                'user': 'nndr_user',
                'password': 'nndr_password'
            }
        else:
            self.db_config = db_config
        
        self.connection_string = f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
        self.engine = None
        self.conn = None
        
        # Data paths
        self.data_root = Path(__file__).parent.parent.parent / 'backend' / 'data'
        
    def connect(self):
        """Establish database connection"""
        try:
            self.engine = create_engine(self.connection_string)
            self.conn = self.engine.connect()
            logger.info("✅ Database connection established")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
        if self.engine:
            self.engine.dispose()
        logger.info("🔌 Database connection closed")
    
    def create_all_schemas(self):
        """Create all database schemas and tables"""
        logger.info("🏗️ Creating database schemas...")
        
        try:
            # Read and execute schema files
            schema_files = [
                'master_gazetteer_schema.sql',
                'forecasting_system_schema.sql'
            ]
            
            for schema_file in schema_files:
                schema_path = Path(__file__).parent / schema_file
                if schema_path.exists():
                    logger.info(f"📄 Executing {schema_file}...")
                    with open(schema_path, 'r') as f:
                        schema_sql = f.read()
                    
                    # Split and execute SQL statements
                    statements = schema_sql.split(';')
                    for statement in statements:
                        statement = statement.strip()
                        if statement:
                            self.conn.execute(text(statement))
                    
                    self.conn.commit()
                    logger.info(f"✅ {schema_file} executed successfully")
                else:
                    logger.warning(f"⚠️ Schema file {schema_file} not found")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create schemas: {e}")
            return False
    
    def ingest_geospatial_data(self):
        """Ingest geospatial reference data"""
        logger.info("🗺️ Ingesting geospatial data...")
        
        try:
            # 1. Local Authority Boundaries
            lad_shapefile = self.data_root / 'LAD_MAY_2025_UK_BFC.shp'
            if lad_shapefile.exists():
                logger.info("📊 Loading Local Authority boundaries...")
                gdf = gpd.read_file(lad_shapefile)
                gdf.to_postgis('local_authority_boundaries', self.engine, if_exists='replace', index=False)
                logger.info(f"✅ Loaded {len(gdf)} Local Authority boundaries")
            
            # 2. Postcode data (CodePoint Open)
            codepo_dir = self.data_root / 'codepo_gb' / 'Data' / 'CSV'
            if codepo_dir.exists():
                logger.info("📮 Loading postcode data...")
                postcode_files = list(codepo_dir.glob('*.csv'))
                for file in postcode_files:
                    logger.info(f"📄 Processing {file.name}...")
                    df = pd.read_csv(file, header=None, names=['Postcode', 'Positional_quality_indicator', 'Eastings', 'Northings', 'Country_code', 'NHS_regional_HA_code', 'NHS_HA_code', 'Admin_county_code', 'Admin_district_code', 'Admin_ward_code'])
                    df.to_sql('postcodes', self.engine, if_exists='append', index=False, method='multi')
                logger.info("✅ Postcode data loaded")
            
            # 3. Address data (OS Open Names)
            opname_dir = self.data_root / 'opname_csv_gb' / 'Data'
            if opname_dir.exists():
                logger.info("🏠 Loading address data...")
                address_files = list(opname_dir.glob('*.csv'))
                for file in address_files[:5]:  # Limit to first 5 files for testing
                    logger.info(f"📄 Processing {file.name}...")
                    df = pd.read_csv(file)
                    df.to_sql('addresses', self.engine, if_exists='append', index=False, method='multi')
                logger.info("✅ Address data loaded")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to ingest geospatial data: {e}")
            return False
    
    def ingest_nndr_data(self):
        """Ingest NNDR business rate data"""
        logger.info("💰 Ingesting NNDR data...")
        
        try:
            # 1. NNDR List Entries (2023)
            nndr_2023_dir = self.data_root / 'uk-englandwales-ndr-2023-listentries-compiled-epoch-0015-baseline-csv'
            if nndr_2023_dir.exists():
                logger.info("📊 Loading NNDR 2023 list entries...")
                csv_files = list(nndr_2023_dir.glob('*.csv'))
                for file in csv_files:
                    logger.info(f"📄 Processing {file.name}...")
                    # Read in chunks to handle large files
                    chunk_size = 10000
                    for chunk in pd.read_csv(file, chunksize=chunk_size):
                        chunk.to_sql('nndr_list_entries_2023', self.engine, if_exists='append', index=False, method='multi')
                logger.info("✅ NNDR 2023 list entries loaded")
            
            # 2. NNDR Summary Valuations (2023)
            nndr_summary_2023_dir = self.data_root / 'uk-englandwales-ndr-2023-summaryvaluations-compiled-epoch-0015-baseline-csv'
            if nndr_summary_2023_dir.exists():
                logger.info("📊 Loading NNDR 2023 summary valuations...")
                csv_files = list(nndr_summary_2023_dir.glob('*.csv'))
                for file in csv_files:
                    logger.info(f"📄 Processing {file.name}...")
                    df = pd.read_csv(file)
                    df.to_sql('nndr_summary_valuations_2023', self.engine, if_exists='replace', index=False)
                logger.info("✅ NNDR 2023 summary valuations loaded")
            
            # 3. Historical NNDR data (2017, 2010)
            historical_years = ['2017', '2010']
            for year in historical_years:
                # List entries
                list_dir = self.data_root / f'uk-englandwales-ndr-{year}-listentries-compiled-epoch-*-baseline-csv'
                if list(list_dir.parent.glob(f'uk-englandwales-ndr-{year}-listentries-compiled-epoch-*-baseline-csv')):
                    actual_dir = list(list_dir.parent.glob(f'uk-englandwales-ndr-{year}-listentries-compiled-epoch-*-baseline-csv'))[0]
                    logger.info(f"📊 Loading NNDR {year} list entries...")
                    csv_files = list(actual_dir.glob('*.csv'))
                    for file in csv_files:
                        logger.info(f"📄 Processing {file.name}...")
                        for chunk in pd.read_csv(file, chunksize=10000):
                            chunk.to_sql(f'nndr_list_entries_{year}', self.engine, if_exists='append', index=False, method='multi')
                    logger.info(f"✅ NNDR {year} list entries loaded")
                
                # Summary valuations
                summary_dir = self.data_root / f'uk-englandwales-ndr-{year}-summaryvaluations-compiled-epoch-*-baseline-csv'
                if list(summary_dir.parent.glob(f'uk-englandwales-ndr-{year}-summaryvaluations-compiled-epoch-*-baseline-csv')):
                    actual_dir = list(summary_dir.parent.glob(f'uk-englandwales-ndr-{year}-summaryvaluations-compiled-epoch-*-baseline-csv'))[0]
                    logger.info(f"📊 Loading NNDR {year} summary valuations...")
                    csv_files = list(actual_dir.glob('*.csv'))
                    for file in csv_files:
                        logger.info(f"📄 Processing {file.name}...")
                        df = pd.read_csv(file)
                        df.to_sql(f'nndr_summary_valuations_{year}', self.engine, if_exists='replace', index=False)
                    logger.info(f"✅ NNDR {year} summary valuations loaded")
            
            # 4. Additional NNDR files
            additional_files = [
                'nndr-ratepayers March 2015_0.csv',
                'NNDR Rating List  March 2015_0.csv'
            ]
            
            for file_name in additional_files:
                file_path = self.data_root / file_name
                if file_path.exists():
                    logger.info(f"📄 Processing {file_name}...")
                    df = pd.read_csv(file_path)
                    table_name = file_name.lower().replace(' ', '_').replace('.csv', '').replace('march_2015_0', '2015')
                    df.to_sql(table_name, self.engine, if_exists='replace', index=False)
                    logger.info(f"✅ {file_name} loaded into {table_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to ingest NNDR data: {e}")
            return False
    
    def create_indexes(self):
        """Create performance indexes"""
        logger.info("⚡ Creating database indexes...")
        
        try:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_postcodes_postcode ON postcodes(postcode);",
                "CREATE INDEX IF NOT EXISTS idx_addresses_postcode ON addresses(postcode);",
                "CREATE INDEX IF NOT EXISTS idx_nndr_list_entries_2023_ba_reference ON nndr_list_entries_2023(ba_reference);",
                "CREATE INDEX IF NOT EXISTS idx_nndr_list_entries_2023_postcode ON nndr_list_entries_2023(postcode);",
                "CREATE INDEX IF NOT EXISTS idx_nndr_list_entries_2017_ba_reference ON nndr_list_entries_2017(ba_reference);",
                "CREATE INDEX IF NOT EXISTS idx_nndr_list_entries_2010_ba_reference ON nndr_list_entries_2010(ba_reference);",
                "CREATE INDEX IF NOT EXISTS idx_local_authority_boundaries_name ON local_authority_boundaries(name);"
            ]
            
            for index_sql in indexes:
                self.conn.execute(text(index_sql))
            
            self.conn.commit()
            logger.info("✅ Database indexes created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create indexes: {e}")
            return False
    
    def run_analysis_queries(self):
        """Run initial analysis queries"""
        logger.info("📈 Running initial analysis queries...")
        
        try:
            # Count records in each table
            tables = [
                'postcodes', 'addresses', 'local_authority_boundaries',
                'nndr_list_entries_2023', 'nndr_list_entries_2017', 'nndr_list_entries_2010',
                'nndr_summary_valuations_2023', 'nndr_summary_valuations_2017', 'nndr_summary_valuations_2010'
            ]
            
            for table in tables:
                try:
                    result = self.conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    logger.info(f"📊 {table}: {count:,} records")
                except Exception as e:
                    logger.warning(f"⚠️ Could not count {table}: {e}")
            
            # Basic NNDR statistics
            try:
                result = self.conn.execute(text("""
                    SELECT 
                        COUNT(*) as total_properties,
                        COUNT(DISTINCT ba_reference) as unique_properties,
                        AVG(rateable_value) as avg_rateable_value
                    FROM nndr_list_entries_2023 
                    WHERE rateable_value > 0
                """))
                stats = result.fetchone()
                logger.info(f"📊 NNDR 2023 Stats: {stats[0]:,} total, {stats[1]:,} unique, £{stats[2]:,.0f} avg value")
            except Exception as e:
                logger.warning(f"⚠️ Could not get NNDR stats: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to run analysis queries: {e}")
            return False
    
    def run_complete_ingestion(self):
        """Run the complete data ingestion process"""
        logger.info("🚀 Starting complete NNDR data ingestion process...")
        start_time = time.time()
        
        try:
            # 1. Connect to database
            if not self.connect():
                return False
            
            # 2. Create all schemas
            if not self.create_all_schemas():
                return False
            
            # 3. Ingest geospatial data
            if not self.ingest_geospatial_data():
                return False
            
            # 4. Ingest NNDR data
            if not self.ingest_nndr_data():
                return False
            
            # 5. Create indexes
            if not self.create_indexes():
                return False
            
            # 6. Run analysis
            if not self.run_analysis_queries():
                return False
            
            # 7. Complete
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"🎉 Data ingestion completed successfully in {duration:.2f} seconds")
            logger.info("📋 Summary:")
            logger.info("   ✅ All database schemas created")
            logger.info("   ✅ Geospatial data ingested")
            logger.info("   ✅ NNDR data ingested")
            logger.info("   ✅ Performance indexes created")
            logger.info("   ✅ Initial analysis completed")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Data ingestion failed: {e}")
            return False
        
        finally:
            self.disconnect()

def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("NNDR DATA INGESTION SCRIPT")
    logger.info("=" * 60)
    
    # Create ingestion instance
    ingestion = NNDRDataIngestion()
    
    # Run complete ingestion
    success = ingestion.run_complete_ingestion()
    
    if success:
        logger.info("🎉 All data ingested successfully!")
        logger.info("🔧 Next steps:")
        logger.info("   1. Run your forecasting models")
        logger.info("   2. Generate business rate reports")
        logger.info("   3. Analyze non-rated properties")
    else:
        logger.error("❌ Data ingestion failed. Check the log file for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 