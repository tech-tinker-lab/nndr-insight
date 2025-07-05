#!/usr/bin/env python3
"""
Comprehensive Data Ingestion Pipeline for NNDR Insight
Enhanced with source tracking, duplicate detection, and performance optimization
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
from typing import Dict, List, Tuple, Optional, Any, Generator
import warnings
from pathlib import Path
import tempfile
import zipfile
import shutil
import sqlalchemy

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_config import get_connection_string

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveIngestionPipeline:
    """Comprehensive data ingestion pipeline with enhanced schema support"""
    
    def __init__(self, data_directory: Optional[str] = None):
        self.data_directory = data_directory or os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', 'data')
        self.conn_str = get_connection_string()
        self.stats = {
            'total_files_processed': 0,
            'total_records_processed': 0,
            'total_records_inserted': 0,
            'total_duplicates_found': 0,
            'total_errors': 0,
            'processing_time': 0
        }
        
        # Data source configurations
        self.data_sources = {
            'voa_2023': {
                'priority': 1,
                'description': 'VOA 2023 NNDR Compiled List',
                'file_pattern': 'uk-englandwales-ndr-2023-listentries-compiled-epoch-0015-baseline-csv.csv',
                'format': 'pipe_delimited',
                'coordinate_system': 'wgs84',
                'quality_score': 0.95,
                'processor': self.process_voa_data
            },
            'local_council_2015': {
                'priority': 2,
                'description': 'Local Council NNDR Data 2015',
                'file_pattern': 'NNDR Rating List  March 2015_0.csv',
                'format': 'csv',
                'coordinate_system': 'unknown',
                'quality_score': 0.85,
                'processor': self.process_local_council_data
            },
            'os_uprn': {
                'priority': 1,
                'description': 'OS Open UPRN',
                'file_pattern': 'osopenuprn_202506_csv/osopenuprn_202506.csv',
                'format': 'csv',
                'coordinate_system': 'osgb',
                'quality_score': 0.98,
                'processor': self.process_os_uprn_data
            },
            # 'codepoint': {
            #     'priority': 2,
            #     'description': 'CodePoint Open Postcodes',
            #     'file_pattern': 'codepo_gb/Data/CSV/*.csv',
            #     'format': 'csv',
            #     'coordinate_system': 'osgb',
            #     'quality_score': 0.90,
            #     'processor': self.process_codepoint_data
            # },
            'onspd': {
                'priority': 1,
                'description': 'ONS Postcode Directory',
                'file_pattern': 'ONSPD_Online_Latest_Centroids.csv',
                'format': 'csv',
                'coordinate_system': 'osgb',
                'quality_score': 0.95,
                'processor': self.process_onspd_data
            }
        }
    
    def connect_database(self):
        """Establish database connection"""
        try:
            conn = psycopg2.connect(self.conn_str)
            logger.info("Database connection established")
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def initialize_pipeline(self):
        """Initialize the pipeline and verify schema"""
        logger.info("Initializing comprehensive ingestion pipeline")
        
        try:
            with self.connect_database() as conn:
                with conn.cursor() as cur:
                    # Verify enhanced schema exists
                    cur.execute("""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name='master_gazetteer' 
                        AND column_name IN ('data_source', 'source_priority', 'duplicate_group_id')
                    """)
                    enhanced_columns = [row[0] for row in cur.fetchall()]
                    
                    if len(enhanced_columns) < 3:
                        logger.error("Enhanced schema not found. Please run enhanced_schema_update.py first.")
                        return False
                    
                    logger.info("Enhanced schema verified successfully")
                    return True
                    
        except Exception as e:
            logger.error(f"Pipeline initialization failed: {e}")
            return False
    
    MASTER_GAZETTEER_COLUMNS = [
        'uprn', 'ba_reference', 'property_id', 'property_address', 'street_descriptor',
        'locality', 'post_town', 'administrative_area', 'postcode',
        'property_category_code', 'property_description', 'rateable_value',
        'effective_date', 'x_coordinate', 'y_coordinate', 'latitude', 'longitude'
    ]

    def _align_to_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure DataFrame has all master_gazetteer columns in correct order, filling missing with None."""
        for col in self.MASTER_GAZETTEER_COLUMNS:
            if col not in df.columns:
                df[col] = None
        
        # Generate property_id from UPRN if not present
        needs_property_id = 'property_id' not in df.columns
        if not needs_property_id and 'property_id' in df.columns:
            needs_property_id = df['property_id'].isna().all()
        
        if needs_property_id:
            if 'uprn' in df.columns:
                df['property_id'] = df['uprn'].astype(str)
            else:
                df['property_id'] = None
        
        # Clean data: replace NaN with None and handle data types
        df = df.replace({pd.NA: None, pd.NaT: None})
        df = df.where(pd.notnull(df), None)
        
        # Convert specific columns to proper types
        if 'uprn' in df.columns:
            df['uprn'] = pd.to_numeric(df['uprn'], errors='coerce')
        
        if 'rateable_value' in df.columns:
            df['rateable_value'] = pd.to_numeric(df['rateable_value'], errors='coerce')
        
        if 'x_coordinate' in df.columns:
            df['x_coordinate'] = pd.to_numeric(df['x_coordinate'], errors='coerce')
        
        if 'y_coordinate' in df.columns:
            df['y_coordinate'] = pd.to_numeric(df['y_coordinate'], errors='coerce')
        
        if 'latitude' in df.columns:
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        
        if 'longitude' in df.columns:
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        
        # Filter out rows with invalid UPRN (None, NaN, or 0)
        if 'uprn' in df.columns:
            df = df.dropna(subset=['uprn'])
            df = df[df['uprn'].astype(float) != 0]
        
        return df[self.MASTER_GAZETTEER_COLUMNS]
    
    def process_voa_data(self, file_path: str) -> pd.DataFrame:
        """Process VOA pipe-delimited data with enhanced field mapping"""
        logger.info(f"Processing VOA data: {file_path}")
        field_positions = {
            'uprn': 19,  # UPRN is the primary property identifier
            'ba_reference': 3,  # BA Reference is billing authority reference
            'property_address': 7,  # Full address
            'street_descriptor': 9,  # Street name
            'locality': 11,  # Locality
            'post_town': 10,  # Post town
            'administrative_area': None,  # Not present in VOA data
            'postcode': 14,  # Postcode
            'property_category_code': 4,  # SCAT code
            'property_description': 5,  # Property description
            'rateable_value': 17,  # Rateable value
            'effective_date': 15,  # Effective date
            'x_coordinate': None,  # Not present in VOA data
            'y_coordinate': None,  # Not present in VOA data
            'latitude': None,  # Not present in VOA data
            'longitude': None  # Not present in VOA data
        }
        data_rows = []
        chunk_size = 10000
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file):
                    if line_num % 100000 == 0:
                        logger.info(f"Processed {line_num} VOA lines")
                    fields = line.strip().split('*')
                    if len(fields) < 29:  # VOA data has 29 fields
                        continue
                    try:
                        row = {}
                        for col in self.MASTER_GAZETTEER_COLUMNS:
                            pos = field_positions.get(col)
                            row[col] = fields[pos] if pos is not None else None
                        
                        # Generate property_id from UPRN (gazetteer standard)
                        if row.get('uprn'):
                            row['property_id'] = str(row['uprn'])
                        else:
                            row['property_id'] = None
                        
                        # Type conversions
                        row['rateable_value'] = self._parse_rateable_value(row['rateable_value'])
                        row['effective_date'] = self._parse_date(row['effective_date'])
                        data_rows.append(row)
                        if len(data_rows) >= chunk_size:
                            df = pd.DataFrame(data_rows)
                            yield self._align_to_schema(df)
                            data_rows = []
                    except Exception as e:
                        logger.warning(f"Error processing VOA line {line_num}: {e}")
                        continue
            if data_rows:
                df = pd.DataFrame(data_rows)
                yield self._align_to_schema(df)
        except Exception as e:
            logger.error(f"Error processing VOA file: {e}")
            raise
    
    def process_local_council_data(self, file_path: str) -> pd.DataFrame:
        """Process local council CSV data"""
        logger.info(f"Processing local council data: {file_path}")
        
        try:
            chunk_size = 10000
            for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
                # Explicit mapping according to gazetteer standards
                chunk['uprn'] = chunk.get('UniquePropertyRef', None)  # Primary identifier
                chunk['ba_reference'] = chunk.get('BAReference', None)  # Billing reference
                chunk['property_id'] = chunk['uprn'].astype(str) if 'uprn' in chunk.columns else None  # Derived from UPRN
                chunk['property_address'] = chunk.get('PropertyAddress', None)
                chunk['street_descriptor'] = chunk.get('StreetDescriptor', None)
                chunk['locality'] = chunk.get('Locality', None)
                chunk['post_town'] = chunk.get('PostTown', None)
                chunk['administrative_area'] = chunk.get('AdministrativeArea', None)
                chunk['postcode'] = chunk.get('PostCode', None)
                chunk['property_category_code'] = chunk.get('PropertyCategoryCode', None)
                chunk['property_description'] = chunk.get('PropertyDescription', None)
                chunk['rateable_value'] = pd.to_numeric(chunk.get('RateableValue', None), errors='coerce')
                chunk['effective_date'] = pd.to_datetime(chunk.get('EffectiveDate', None), errors='coerce')
                chunk['x_coordinate'] = None
                chunk['y_coordinate'] = None
                chunk['latitude'] = None
                chunk['longitude'] = None
                yield self._align_to_schema(chunk)
                
        except Exception as e:
            logger.error(f"Error processing local council file: {e}")
            raise
    
    def process_os_uprn_data(self, file_path: str) -> pd.DataFrame:
        """Process OS UPRN data"""
        logger.info(f"Processing OS UPRN data: {file_path}")
        
        try:
            chunk_size = 50000
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                # OS UPRN data provides the primary property identifier
                chunk['uprn'] = chunk.get('UPRN', None)  # Primary identifier
                chunk['ba_reference'] = None  # Not provided by OS UPRN
                chunk['property_id'] = chunk['uprn'].astype(str) if 'uprn' in chunk.columns else None  # Derived from UPRN
                chunk['property_address'] = None
                chunk['street_descriptor'] = None
                chunk['locality'] = None
                chunk['post_town'] = None
                chunk['administrative_area'] = None
                chunk['postcode'] = None
                chunk['property_category_code'] = None
                chunk['property_description'] = None
                chunk['rateable_value'] = None
                chunk['effective_date'] = None
                chunk['x_coordinate'] = chunk.get('X_COORDINATE', None)
                chunk['y_coordinate'] = chunk.get('Y_COORDINATE', None)
                chunk['latitude'] = chunk.get('LATITUDE', None)
                chunk['longitude'] = chunk.get('LONGITUDE', None)
                yield self._align_to_schema(chunk)
                
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
                    chunk['last_source_update'] = datetime.now()
                    chunk['source_file_reference'] = csv_file
                    
                    # Clean postcodes
                    chunk['postcode'] = chunk['postcode'].str.strip().str.upper()
                    
                    yield chunk
                    
            except Exception as e:
                logger.error(f"Error processing CodePoint file {csv_file}: {e}")
                continue
    
    def process_onspd_data(self, file_path: str) -> pd.DataFrame:
        """Process ONSPD data"""
        logger.info(f"Processing ONSPD data: {file_path}")
        
        try:
            chunk_size = 50000
            for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
                chunk['uprn'] = None
                chunk['ba_reference'] = None
                chunk['property_address'] = None
                chunk['street_descriptor'] = None
                chunk['locality'] = None
                chunk['post_town'] = None
                chunk['administrative_area'] = None
                chunk['postcode'] = chunk.get('PCD', None)
                chunk['property_category_code'] = None
                chunk['property_description'] = None
                chunk['rateable_value'] = None
                chunk['effective_date'] = None
                chunk['x_coordinate'] = chunk.get('x', None)
                chunk['y_coordinate'] = chunk.get('y', None)
                chunk['latitude'] = chunk.get('lat', None)
                chunk['longitude'] = chunk.get('long', None)
                yield self._align_to_schema(chunk)
                
        except Exception as e:
            logger.error(f"Error processing ONSPD file: {e}")
            raise
    
    def detect_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect and mark duplicates across data sources"""
        logger.info("Detecting duplicates")
        
        # Create duplicate groups based on multiple criteria
        duplicate_criteria = [
            ['ba_reference', 'postcode'],
            ['uprn'],
            ['street_descriptor', 'post_town', 'postcode']
        ]
        
        df['duplicate_group_id'] = None
        group_counter = 1
        
        for criteria in duplicate_criteria:
            # Check if all criteria columns exist in the dataframe
            available_criteria = [col for col in criteria if col in df.columns]
            if not available_criteria:
                continue
                
            try:
                # Group by criteria
                groups = df.groupby(available_criteria).size().reset_index(name='count')
                duplicate_groups = groups[groups['count'] > 1]
                
                for _, group in duplicate_groups.iterrows():
                    # Find matching records
                    mask = True
                    for col in available_criteria:
                        if col in df.columns:
                            mask = mask & (df[col] == group[col])
                    
                    duplicate_indices = df[mask].index
                    
                    if len(duplicate_indices) > 1:
                        # Assign group ID
                        df.loc[duplicate_indices, 'duplicate_group_id'] = group_counter
                        
                        # Mark preferred record (highest priority source)
                        if 'source_priority' in df.columns:
                            preferred_idx = df.loc[duplicate_indices, 'source_priority'].idxmin()
                            df.loc[preferred_idx, 'is_preferred_record'] = True
                        
                        group_counter += 1
            except Exception as e:
                logger.warning(f"Error in duplicate detection for criteria {available_criteria}: {e}")
                continue
        
        return df
    
    def bulk_insert_data(self, df: pd.DataFrame, table_name: str):
        """Bulk insert data with performance optimization"""
        logger.info(f"Bulk inserting {len(df)} records into {table_name}")
        
        try:
            with self.connect_database() as conn:
                # Disable indexes for faster insertion (skip if table has foreign key references)
                with conn.cursor() as cursor:
                    try:
                        cursor.execute(f"ALTER TABLE {table_name} SET UNLOGGED")
                    except Exception as e:
                        if "references" in str(e).lower():
                            logger.warning(f"Skipping UNLOGGED for {table_name} due to foreign key references")
                        else:
                            raise
                # Prepare data for insertion
                columns = df.columns.tolist()
                data = list(df.itertuples(index=False, name=None))
                # Bulk insert
                with conn.cursor() as cursor:
                    try:
                        execute_values(
                            cursor,
                            f"INSERT INTO {table_name} ({','.join(columns)}) VALUES %s",
                            data,
                            template=None,
                            page_size=1000
                        )
                    except Exception as e:
                        logger.error(f"Bulk insert failed for table {table_name}.")
                        logger.error(f"First row: {data[0] if data else 'NO DATA'}")
                        logger.error(f"Exception: {e}")
                        raise
                # Re-enable logging and rebuild indexes
                with conn.cursor() as cursor:
                    try:
                        cursor.execute(f"ALTER TABLE {table_name} SET LOGGED")
                    except Exception as e:
                        if "references" in str(e).lower():
                            logger.warning(f"Skipping LOGGED for {table_name} due to foreign key references")
                        else:
                            raise
                    cursor.execute(f"REINDEX TABLE {table_name}")
                conn.commit()
                logger.info(f"Successfully inserted {len(df)} records")
                self.stats['total_records_inserted'] += len(df)
        except Exception as e:
            logger.error(f"Bulk insert failed: {e}")
            self.stats['total_errors'] += 1
            raise
    
    # Add a mapping from source_name to target table
    REFERENCE_TABLE_MAP = {
        'os_uprn': 'os_open_uprn',
        'onspd': 'onspd',
        'codepoint': 'code_point_open',
        'os_open_names': 'os_open_names',
        'lad_boundaries': 'lad_boundaries',
        'os_open_map_local': 'os_open_map_local',
    }

    def _align_to_table_schema(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Align DataFrame columns to match the target table schema."""
        engine = sqlalchemy.create_engine(get_connection_string())
        insp = sqlalchemy.inspect(engine)
        columns = [col['name'] for col in insp.get_columns(table_name)]
        # Filter out auto-generated columns (like 'id' with SERIAL/sequence)
        auto_generated_columns = []
        for col in insp.get_columns(table_name):
            if col.get('autoincrement', False) or (col.get('default') and 'nextval' in str(col.get('default'))):
                auto_generated_columns.append(col['name'])
        # Only keep columns that exist in the table and are not auto-generated
        insertable_columns = [col for col in columns if col not in auto_generated_columns]
        # Only keep columns that exist in the DataFrame and are insertable
        aligned = df[[col for col in insertable_columns if col in df.columns]].copy()
        # Add missing columns as None
        for col in insertable_columns:
            if col not in aligned.columns:
                aligned[col] = None
        return aligned[insertable_columns]

    def run_parallel_processing(self, data_files: List[Tuple[str, str]]):
        """Run parallel processing for multiple data files"""
        logger.info("Starting parallel processing")
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for file_path, source_name in data_files:
                if source_name in self.data_sources:
                    future = executor.submit(self.process_single_file, file_path, source_name)
                    futures.append((future, source_name))
            # Collect results
            for future, source_name in futures:
                try:
                    result = future.result()
                    for chunk in result:
                        chunk = self.detect_duplicates(chunk)
                        # Determine target table
                        if source_name in self.REFERENCE_TABLE_MAP:
                            table_name = self.REFERENCE_TABLE_MAP[source_name]
                            chunk = self._align_to_table_schema(chunk, table_name)
                        else:
                            table_name = 'master_gazetteer'
                            chunk = self._align_to_schema(chunk)
                        self.bulk_insert_data(chunk, table_name)
                except Exception as e:
                    logger.error(f"Processing failed: {e}")
                    self.stats['total_errors'] += 1
    
    def process_single_file(self, file_path: str, source_name: str):
        """Process a single file with the appropriate processor"""
        if source_name in self.data_sources:
            processor = self.data_sources[source_name]['processor']
            return processor(file_path)
        else:
            logger.warning(f"No processor found for source: {source_name}")
            return []
    
    def find_data_files(self) -> List[Tuple[str, str]]:
        """Find all data files in the data directory"""
        data_files = []
        
        for source_name, config in self.data_sources.items():
            file_pattern = config['file_pattern']
            
            if '*' in file_pattern:
                # Handle wildcard patterns
                pattern_path = os.path.join(self.data_directory, file_pattern)
                matching_files = Path(self.data_directory).glob(file_pattern)
                for file_path in matching_files:
                    if file_path.is_file():
                        data_files.append((str(file_path), source_name))
            else:
                # Handle specific file patterns
                file_path = os.path.join(self.data_directory, file_pattern)
                if os.path.exists(file_path):
                    data_files.append((file_path, source_name))
        
        return data_files
    
    def run_complete_ingestion(self):
        """Run complete ingestion pipeline"""
        start_time = datetime.now()
        logger.info("Starting complete ingestion pipeline")
        
        try:
            # Initialize pipeline
            if not self.initialize_pipeline():
                return False
            
            # Find data files
            data_files = self.find_data_files()
            logger.info(f"Found {len(data_files)} data files to process")
            
            # Run parallel processing
            self.run_parallel_processing(data_files)
            
            # Calculate processing time
            self.stats['processing_time'] = (datetime.now() - start_time).total_seconds()
            
            # Print summary
            self._print_summary()
            
            logger.info("Complete ingestion pipeline finished successfully")
            return True
            
        except Exception as e:
            logger.error(f"Ingestion pipeline failed: {e}")
            self.stats['total_errors'] += 1
            return False
    
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
            date_formats = ['%d-%b-%Y', '%d/%m/%Y', '%Y-%m-%d']
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str.strip(), fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue
            return None
        except Exception:
            return None
    
    def _print_summary(self):
        """Print ingestion summary"""
        logger.info("=" * 60)
        logger.info("INGESTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total files processed: {self.stats['total_files_processed']}")
        logger.info(f"Total records processed: {self.stats['total_records_processed']}")
        logger.info(f"Total records inserted: {self.stats['total_records_inserted']}")
        logger.info(f"Total duplicates found: {self.stats['total_duplicates_found']}")
        logger.info(f"Total errors: {self.stats['total_errors']}")
        logger.info(f"Processing time: {self.stats['processing_time']:.2f} seconds")
        logger.info("=" * 60)

def main():
    """Main execution function"""
    # Initialize pipeline
    pipeline = ComprehensiveIngestionPipeline()
    
    # Run complete ingestion
    success = pipeline.run_complete_ingestion()
    
    if success:
        logger.info("✅ Ingestion pipeline completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Ingestion pipeline failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 