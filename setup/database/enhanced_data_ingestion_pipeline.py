#!/usr/bin/env python3
"""
Enhanced Data Ingestion Pipeline for NNDR Insight Project
Handles multiple data sources, duplicate detection, and performance optimization
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
import geopandas as gpd
from shapely.geometry import Point
import concurrent.futures
from datetime import datetime, timedelta
import json
import re
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_config import get_database_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedDataIngestionPipeline:
    """Enhanced data ingestion pipeline with multi-source support and duplicate detection"""
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.conn = None
        self.data_sources = {
            'voa_2023': {
                'priority': 1,
                'description': 'VOA 2023 NNDR Compiled List',
                'file_pattern': 'uk-englandwales-ndr-2023-listentries-compiled-epoch-0015-baseline-csv.csv',
                'format': 'pipe_delimited',
                'coordinate_system': 'wgs84',
                'quality_score': 0.95
            },
            'local_council_2015': {
                'priority': 2,
                'description': 'Local Council NNDR Data 2015',
                'file_pattern': 'NNDR Rating List  March 2015_0.csv',
                'format': 'csv',
                'coordinate_system': 'unknown',
                'quality_score': 0.85
            },
            'os_uprn': {
                'priority': 1,
                'description': 'OS Open UPRN',
                'file_pattern': 'osopenuprn_202506_csv/osopenuprn_202506.csv',
                'format': 'csv',
                'coordinate_system': 'osgb',
                'quality_score': 0.98
            },
            'codepoint': {
                'priority': 2,
                'description': 'CodePoint Open Postcodes',
                'file_pattern': 'codepo_gb/Data/CSV/*.csv',
                'format': 'csv',
                'coordinate_system': 'osgb',
                'quality_score': 0.90
            },
            'onspd': {
                'priority': 1,
                'description': 'ONS Postcode Directory',
                'file_pattern': 'ONSPD_Online_Latest_Centroids.csv',
                'format': 'csv',
                'coordinate_system': 'osgb',
                'quality_score': 0.95
            }
        }
        
    def connect_database(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def initialize_data_sources(self):
        """Initialize data sources table"""
        try:
            with self.conn.cursor() as cursor:
                # Create data sources table if not exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS data_sources (
                        id SERIAL PRIMARY KEY,
                        source_name VARCHAR(100) UNIQUE,
                        source_type VARCHAR(50),
                        source_description TEXT,
                        source_priority INTEGER,
                        source_quality_score NUMERIC(3,2),
                        source_update_frequency VARCHAR(50),
                        source_coordinate_system VARCHAR(50),
                        source_file_pattern VARCHAR(255),
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert data sources
                for source_name, source_config in self.data_sources.items():
                    cursor.execute("""
                        INSERT INTO data_sources 
                        (source_name, source_type, source_description, source_priority, 
                         source_quality_score, source_coordinate_system, source_file_pattern)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (source_name) DO UPDATE SET
                        source_priority = EXCLUDED.source_priority,
                        source_quality_score = EXCLUDED.source_quality_score
                    """, (
                        source_name,
                        'nndr' if 'nndr' in source_name else 'reference',
                        source_config['description'],
                        source_config['priority'],
                        source_config['quality_score'],
                        source_config['coordinate_system'],
                        source_config['file_pattern']
                    ))
                
                self.conn.commit()
                logger.info("Data sources initialized")
        except Exception as e:
            logger.error(f"Failed to initialize data sources: {e}")
            self.conn.rollback()
            raise
    
    def add_source_tracking_columns(self):
        """Add source tracking columns to master_gazetteer"""
        try:
            with self.conn.cursor() as cursor:
                # Add source tracking columns
                columns_to_add = [
                    "data_source VARCHAR(100)",
                    "source_priority INTEGER",
                    "source_confidence_score NUMERIC(3,2)",
                    "last_source_update TIMESTAMP",
                    "source_file_reference VARCHAR(255)",
                    "duplicate_group_id INTEGER",
                    "is_preferred_record BOOLEAN DEFAULT FALSE"
                ]
                
                for column_def in columns_to_add:
                    column_name = column_def.split()[0]
                    try:
                        cursor.execute(f"ALTER TABLE master_gazetteer ADD COLUMN {column_def}")
                        logger.info(f"Added column: {column_name}")
                    except psycopg2.errors.DuplicateColumn:
                        logger.info(f"Column {column_name} already exists")
                
                self.conn.commit()
                logger.info("Source tracking columns added")
        except Exception as e:
            logger.error(f"Failed to add source tracking columns: {e}")
            self.conn.rollback()
            raise
    
    def create_duplicate_management_table(self):
        """Create duplicate management table"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS duplicate_management (
                        id SERIAL PRIMARY KEY,
                        property_id INTEGER REFERENCES master_gazetteer(id),
                        duplicate_group_id INTEGER,
                        duplicate_confidence_score NUMERIC(3,2),
                        duplicate_reason TEXT,
                        preferred_record BOOLEAN DEFAULT FALSE,
                        merged_from_sources JSONB,
                        merge_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create index for performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_duplicate_management_group_id 
                    ON duplicate_management(duplicate_group_id)
                """)
                
                self.conn.commit()
                logger.info("Duplicate management table created")
        except Exception as e:
            logger.error(f"Failed to create duplicate management table: {e}")
            self.conn.rollback()
            raise
    
    def process_voa_data(self, file_path: str) -> pd.DataFrame:
        """Process VOA pipe-delimited data"""
        logger.info(f"Processing VOA data: {file_path}")
        
        # Define field positions for pipe-delimited data
        field_positions = {
            'record_id': 0,
            'ba_code': 1,
            'ba_reference': 2,
            'property_category': 3,
            'description': 4,
            'scat_code': 5,
            'full_address': 6,
            'property_name': 7,
            'street': 8,
            'town': 9,
            'locality': 10,
            'postcode': 11,
            'rateable_value': 12,
            'uprn': 13,
            'appeal_code': 14,
            'effective_date': 15
        }
        
        data_rows = []
        chunk_size = 10000
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file):
                    if line_num % 100000 == 0:
                        logger.info(f"Processed {line_num} lines")
                    
                    fields = line.strip().split('*')
                    
                    if len(fields) < 16:
                        continue
                    
                    try:
                        row = {
                            'ba_code': fields[field_positions['ba_code']] if len(fields) > field_positions['ba_code'] else None,
                            'ba_reference': fields[field_positions['ba_reference']] if len(fields) > field_positions['ba_reference'] else None,
                            'property_category': fields[field_positions['property_category']] if len(fields) > field_positions['property_category'] else None,
                            'description': fields[field_positions['description']] if len(fields) > field_positions['description'] else None,
                            'scat_code': fields[field_positions['scat_code']] if len(fields) > field_positions['scat_code'] else None,
                            'property_name': fields[field_positions['property_name']] if len(fields) > field_positions['property_name'] else None,
                            'street': fields[field_positions['street']] if len(fields) > field_positions['street'] else None,
                            'town': fields[field_positions['town']] if len(fields) > field_positions['town'] else None,
                            'locality': fields[field_positions['locality']] if len(fields) > field_positions['locality'] else None,
                            'postcode': fields[field_positions['postcode']] if len(fields) > field_positions['postcode'] else None,
                            'rateable_value': self._parse_rateable_value(fields[field_positions['rateable_value']]) if len(fields) > field_positions['rateable_value'] else None,
                            'uprn': fields[field_positions['uprn']] if len(fields) > field_positions['uprn'] else None,
                            'effective_date': self._parse_date(fields[field_positions['effective_date']]) if len(fields) > field_positions['effective_date'] else None,
                            'data_source': 'voa_2023',
                            'source_priority': 1,
                            'source_confidence_score': 0.95
                        }
                        
                        data_rows.append(row)
                        
                        # Process in chunks to manage memory
                        if len(data_rows) >= chunk_size:
                            yield pd.DataFrame(data_rows)
                            data_rows = []
                            
                    except Exception as e:
                        logger.warning(f"Error processing line {line_num}: {e}")
                        continue
            
            # Yield remaining data
            if data_rows:
                yield pd.DataFrame(data_rows)
                
        except Exception as e:
            logger.error(f"Error processing VOA file: {e}")
            raise
    
    def process_local_council_data(self, file_path: str) -> pd.DataFrame:
        """Process local council CSV data"""
        logger.info(f"Processing local council data: {file_path}")
        
        try:
            # Read CSV in chunks
            chunk_size = 10000
            for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
                # Map fields to standard schema
                chunk['data_source'] = 'local_council_2015'
                chunk['source_priority'] = 2
                chunk['source_confidence_score'] = 0.85
                
                # Rename columns to match schema
                column_mapping = {
                    'BAReference': 'ba_reference',
                    'PropertyCategoryCode': 'property_category',
                    'PropertyDescription': 'description',
                    'PropertyAddress': 'full_address',
                    'StreetDescriptor': 'street',
                    'Locality': 'locality',
                    'PostTown': 'town',
                    'PostCode': 'postcode',
                    'RateableValue': 'rateable_value',
                    'SCATCode': 'scat_code',
                    'UniquePropertyRef': 'uprn'
                }
                
                chunk = chunk.rename(columns=column_mapping)
                
                # Clean and validate data
                chunk['rateable_value'] = pd.to_numeric(chunk['rateable_value'], errors='coerce')
                chunk['postcode'] = chunk['postcode'].str.strip().str.upper()
                
                yield chunk
                
        except Exception as e:
            logger.error(f"Error processing local council file: {e}")
            raise
    
    def process_os_uprn_data(self, file_path: str) -> pd.DataFrame:
        """Process OS UPRN data"""
        logger.info(f"Processing OS UPRN data: {file_path}")
        
        try:
            chunk_size = 50000
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                # Transform coordinates from OSGB to WGS84
                chunk['latitude_wgs84'] = chunk['LATITUDE']
                chunk['longitude_wgs84'] = chunk['LONGITUDE']
                
                # Add source information
                chunk['data_source'] = 'os_uprn'
                chunk['source_priority'] = 1
                chunk['source_confidence_score'] = 0.98
                
                # Rename columns
                chunk = chunk.rename(columns={
                    'UPRN': 'uprn',
                    'X_COORDINATE': 'x_coordinate_osgb',
                    'Y_COORDINATE': 'y_coordinate_osgb'
                })
                
                yield chunk
                
        except Exception as e:
            logger.error(f"Error processing OS UPRN file: {e}")
            raise
    
    def process_codepoint_data(self, directory_path: str) -> pd.DataFrame:
        """Process CodePoint data files"""
        logger.info(f"Processing CodePoint data: {directory_path}")
        
        csv_files = [f for f in os.listdir(directory_path) if f.endswith('.csv')]
        
        for csv_file in csv_files:
            file_path = os.path.join(directory_path, csv_file)
            logger.info(f"Processing CodePoint file: {csv_file}")
            
            try:
                chunk_size = 10000
                for chunk in pd.read_csv(file_path, chunksize=chunk_size, header=None, 
                                       names=['postcode', 'positional_quality', 'easting', 'northing', 
                                             'country_code', 'nhs_regional_ha', 'nhs_ha', 'admin_county', 
                                             'admin_district', 'admin_ward']):
                    
                    # Add source information
                    chunk['data_source'] = 'codepoint'
                    chunk['source_priority'] = 2
                    chunk['source_confidence_score'] = 0.90
                    
                    # Clean postcodes
                    chunk['postcode'] = chunk['postcode'].str.strip().str.upper()
                    
                    yield chunk
                    
            except Exception as e:
                logger.error(f"Error processing CodePoint file {csv_file}: {e}")
                continue
    
    def detect_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect and mark duplicates across data sources"""
        logger.info("Detecting duplicates")
        
        # Create duplicate groups based on multiple criteria
        duplicate_criteria = [
            # Exact match on BA Reference + Postcode
            ['ba_reference', 'postcode'],
            # Exact match on UPRN
            ['uprn'],
            # Fuzzy match on address + coordinates
            ['street', 'town', 'postcode']
        ]
        
        df['duplicate_group_id'] = None
        group_counter = 1
        
        for criteria in duplicate_criteria:
            # Group by criteria
            groups = df.groupby(criteria).size().reset_index(name='count')
            duplicate_groups = groups[groups['count'] > 1]
            
            for _, group in duplicate_groups.iterrows():
                # Find matching records
                mask = True
                for col in criteria:
                    if col in df.columns:
                        mask = mask & (df[col] == group[col])
                
                duplicate_indices = df[mask].index
                
                if len(duplicate_indices) > 1:
                    # Assign group ID
                    df.loc[duplicate_indices, 'duplicate_group_id'] = group_counter
                    
                    # Mark preferred record (highest priority source)
                    preferred_idx = df.loc[duplicate_indices, 'source_priority'].idxmin()
                    df.loc[preferred_idx, 'is_preferred_record'] = True
                    
                    group_counter += 1
        
        return df
    
    def bulk_insert_data(self, df: pd.DataFrame, table_name: str):
        """Bulk insert data with performance optimization"""
        logger.info(f"Bulk inserting {len(df)} records into {table_name}")
        
        try:
            # Disable indexes for faster insertion
            with self.conn.cursor() as cursor:
                cursor.execute(f"ALTER TABLE {table_name} SET UNLOGGED")
            
            # Prepare data for insertion
            columns = df.columns.tolist()
            data = [tuple(row) for row in df[columns].values]
            
            # Bulk insert
            with self.conn.cursor() as cursor:
                execute_values(
                    cursor,
                    f"INSERT INTO {table_name} ({','.join(columns)}) VALUES %s",
                    data,
                    template=None,
                    page_size=1000
                )
            
            # Re-enable logging and rebuild indexes
            with self.conn.cursor() as cursor:
                cursor.execute(f"ALTER TABLE {table_name} SET LOGGED")
                cursor.execute(f"REINDEX TABLE {table_name}")
            
            self.conn.commit()
            logger.info(f"Successfully inserted {len(df)} records")
            
        except Exception as e:
            logger.error(f"Bulk insert failed: {e}")
            self.conn.rollback()
            raise
    
    def run_parallel_processing(self, data_files: List[str]):
        """Run parallel processing for multiple data files"""
        logger.info("Starting parallel processing")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            
            for file_path in data_files:
                if 'voa' in file_path:
                    future = executor.submit(self.process_voa_data, file_path)
                elif 'local_council' in file_path:
                    future = executor.submit(self.process_local_council_data, file_path)
                elif 'os_uprn' in file_path:
                    future = executor.submit(self.process_os_uprn_data, file_path)
                
                futures.append(future)
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    # Process result chunks
                    for chunk in result:
                        # Detect duplicates
                        chunk = self.detect_duplicates(chunk)
                        # Insert data
                        self.bulk_insert_data(chunk, 'master_gazetteer')
                except Exception as e:
                    logger.error(f"Processing failed: {e}")
    
    def _parse_rateable_value(self, value_str: str) -> Optional[float]:
        """Parse rateable value from string"""
        if not value_str or value_str.strip() == '':
            return None
        try:
            return float(value_str.strip())
        except (ValueError, TypeError):
            return None
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date from string"""
        if not date_str or date_str.strip() == '':
            return None
        try:
            # Handle various date formats
            date_formats = ['%d-%b-%Y', '%d/%m/%Y', '%Y-%m-%d']
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str.strip(), fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue
            return None
        except Exception:
            return None
    
    def run_complete_ingestion(self, data_directory: str):
        """Run complete ingestion pipeline"""
        logger.info("Starting complete ingestion pipeline")
        
        try:
            # Initialize database
            self.connect_database()
            self.initialize_data_sources()
            self.add_source_tracking_columns()
            self.create_duplicate_management_table()
            
            # Process data files
            data_files = [
                os.path.join(data_directory, 'uk-englandwales-ndr-2023-listentries-compiled-epoch-0015-baseline-csv.csv'),
                os.path.join(data_directory, 'NNDR Rating List  March 2015_0.csv'),
                os.path.join(data_directory, 'osopenuprn_202506_csv/osopenuprn_202506.csv')
            ]
            
            # Run parallel processing
            self.run_parallel_processing(data_files)
            
            # Process CodePoint data
            codepoint_dir = os.path.join(data_directory, 'codepo_gb/Data/CSV')
            if os.path.exists(codepoint_dir):
                for chunk in self.process_codepoint_data(codepoint_dir):
                    chunk = self.detect_duplicates(chunk)
                    self.bulk_insert_data(chunk, 'master_gazetteer')
            
            logger.info("Complete ingestion pipeline finished successfully")
            
        except Exception as e:
            logger.error(f"Ingestion pipeline failed: {e}")
            raise
        finally:
            if self.conn:
                self.conn.close()

def main():
    """Main execution function"""
    # Get database configuration
    db_config = get_database_connection()
    
    # Initialize pipeline
    pipeline = EnhancedDataIngestionPipeline(db_config)
    
    # Run complete ingestion
    data_directory = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'data')
    pipeline.run_complete_ingestion(data_directory)

if __name__ == "__main__":
    main() 