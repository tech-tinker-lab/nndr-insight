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
                'source_type': 'nndr',
                'processor': self.process_voa_data
            },
            'local_council_2015': {
                'priority': 2,
                'description': 'Local Council NNDR Data 2015',
                'file_pattern': 'NNDR Rating List  March 2015_0.csv',
                'format': 'csv',
                'coordinate_system': 'unknown',
                'quality_score': 0.85,
                'source_type': 'nndr',
                'processor': self.process_local_council_data
            },
            'os_uprn': {
                'priority': 1,
                'description': 'OS Open UPRN',
                'file_pattern': 'osopenuprn_202506_csv/osopenuprn_202506.csv',
                'format': 'csv',
                'coordinate_system': 'osgb',
                'quality_score': 0.98,
                'source_type': 'reference',
                'processor': self.process_os_uprn_data
            },
            'codepoint': {
                'priority': 2,
                'description': 'CodePoint Open Postcodes',
                'file_pattern': 'codepo_gb/Data/CSV/*.csv',
                'format': 'csv',
                'coordinate_system': 'osgb',
                'quality_score': 0.90,
                'source_type': 'reference',
                'processor': self.process_codepoint_data
            },
            'onspd': {
                'priority': 1,
                'description': 'ONS Postcode Directory',
                'file_pattern': 'ONSPD_Online_Latest_Centroids.csv',
                'format': 'csv',
                'coordinate_system': 'osgb',
                'quality_score': 0.95,
                'source_type': 'reference',
                'processor': self.process_onspd_data
            },
            'os_open_names': {
                'priority': 1,
                'description': 'OS Open Names',
                'file_pattern': 'opname_csv_gb/Data/*.csv',
                'format': 'csv',
                'coordinate_system': 'osgb',
                'quality_score': 0.95,
                'source_type': 'reference',
                'processor': self.process_os_open_names_data
            },
            'os_open_usrn': {
                'priority': 1,
                'description': 'OS Open USRN',
                'file_pattern': 'osopenusrn_202507_gpkg/*.gpkg',
                'format': 'gpkg',
                'coordinate_system': 'osgb',
                'quality_score': 0.98,
                'source_type': 'reference',
                'processor': self.process_os_open_usrn_data
            },
            'lad_boundaries': {
                'priority': 1,
                'description': 'Local Authority District Boundaries',
                'file_pattern': 'LAD_MAY_2025_UK_BFC.shp',
                'format': 'shapefile',
                'coordinate_system': 'osgb',
                'quality_score': 0.98,
                'source_type': 'reference',
                'processor': self.process_lad_boundaries_data
            },
            'os_open_map_local': {
                'priority': 1,
                'description': 'OS Open Map Local',
                'file_pattern': 'opmplc_gml3_gb/data/*/*.gml',
                'format': 'gml',
                'coordinate_system': 'osgb',
                'quality_score': 0.95,
                'source_type': 'reference',
                'processor': self.process_os_open_map_local_data
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
            needs_property_id = df['property_id'].isna().all().item() if hasattr(df['property_id'].isna().all(), 'item') else df['property_id'].isna().all()
        
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
        """Process OS UPRN data for os_open_uprn table"""
        logger.info(f"Processing OS UPRN data: {file_path}")
        
        try:
            chunk_size = 50000
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                # OS UPRN data for reference table - keep original structure
                # Only keep the columns that exist in the os_open_uprn table
                required_columns = ['uprn', 'x_coordinate', 'y_coordinate', 'latitude', 'longitude']
                
                # Map column names if needed
                column_mapping = {
                    'UPRN': 'uprn',
                    'X_COORDINATE': 'x_coordinate', 
                    'Y_COORDINATE': 'y_coordinate',
                    'LATITUDE': 'latitude',
                    'LONGITUDE': 'longitude'
                }
                
                # Rename columns if they exist
                for old_name, new_name in column_mapping.items():
                    if old_name in chunk.columns:
                        chunk[new_name] = chunk[old_name]
                
                # Keep only the required columns
                chunk = chunk[[col for col in required_columns if col in chunk.columns]]
                
                # Add missing columns as None
                for col in required_columns:
                    if col not in chunk.columns:
                        chunk[col] = None
                
                yield chunk[required_columns]
                
        except Exception as e:
            logger.error(f"Error processing OS UPRN file: {e}")
            raise

    def process_onspd_data(self, file_path: str) -> pd.DataFrame:
        """Process ONSPD data"""
        logger.info(f"Processing ONSPD data: {file_path}")
        
        try:
            chunk_size = 50000
            for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
                # Keep only the columns that exist in the onspd table
                required_columns = ['pcds', 'pcd', 'lat', 'long', 'ctry', 'oslaua', 'osward', 'parish', 
                                  'oa11', 'lsoa11', 'msoa11', 'imd', 'rgn', 'pcon', 'ur01ind', 'oac11', 
                                  'oseast1m', 'osnrth1m', 'dointr', 'doterm']
                
                # Map column names if needed
                column_mapping = {
                    'PCDS': 'pcds',
                    'PCD': 'pcd', 
                    'LAT': 'lat',
                    'LONG': 'long',
                    'CTRY': 'ctry',
                    'OSLAUA': 'oslaua',
                    'OSWARD': 'osward',
                    'PARISH': 'parish',
                    'OA11': 'oa11',
                    'LSOA11': 'lsoa11',
                    'MSOA11': 'msoa11',
                    'IMD': 'imd',
                    'RGN': 'rgn',
                    'PCON': 'pcon',
                    'UR01IND': 'ur01ind',
                    'OAC11': 'oac11',
                    'OSEAST1M': 'oseast1m',
                    'OSNRTH1M': 'osnrth1m',
                    'DOINTR': 'dointr',
                    'DOTERM': 'doterm'
                }
                
                # Rename columns if they exist
                for old_name, new_name in column_mapping.items():
                    if old_name in chunk.columns:
                        chunk[new_name] = chunk[old_name]
                
                # Keep only the required columns that exist
                chunk = chunk[[col for col in required_columns if col in chunk.columns]]
                
                # Add missing columns as None
                for col in required_columns:
                    if col not in chunk.columns:
                        chunk[col] = None
                
                yield chunk[required_columns]
                
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
        'os_open_usrn': 'os_open_usrn',
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
                        # Determine target table based on source type
                        source_config = self.data_sources.get(source_name, {})
                        source_type = source_config.get('source_type', 'unknown')
                        
                        if source_type == 'reference':
                            # Reference data goes to specific tables, not master_gazetteer
                            if source_name in self.REFERENCE_TABLE_MAP:
                                table_name = self.REFERENCE_TABLE_MAP[source_name]
                                chunk = self._align_to_table_schema(chunk, table_name)
                                self.bulk_insert_data(chunk, table_name)
                            else:
                                logger.warning(f"No table mapping found for reference source: {source_name}")
                                continue
                        else:
                            # NNDR data: skip insertion, just log for now
                            logger.info(f"Skipping insertion for NNDR data source: {source_name} (gather only)")
                            continue
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
            # Skip NNDR data sources completely - don't process them at all
            if config.get('source_type') == 'nndr':
                logger.info(f"Skipping NNDR data source: {source_name} (not processing)")
                continue
                
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
            
            # Clean reference tables before insertion
            self.clean_reference_tables()
            
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

    def process_lad_boundaries_data(self, file_path: str) -> pd.DataFrame:
        """Process LAD boundaries shapefile data"""
        logger.info(f"Processing LAD boundaries data: {file_path}")
        
        try:
            import geopandas as gpd
            
            # Read the shapefile
            gdf = gpd.read_file(file_path)
            
            # Convert to DataFrame and keep only necessary columns
            df = gdf.drop(columns=['geometry'])
            
            # Add any missing columns that the lad_boundaries table expects
            expected_columns = ['lad_code', 'lad_name', 'lad_type']
            
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = None
            
            yield df
            
        except Exception as e:
            logger.error(f"Error processing LAD boundaries file: {e}")
            raise

    def process_os_open_map_local_data(self, file_path: str) -> pd.DataFrame:
        """Process OS Open Map Local GML data"""
        logger.info(f"Processing OS Open Map Local data: {file_path}")
        
        try:
            import geopandas as gpd
            
            # Read the GML file
            gdf = gpd.read_file(file_path)
            
            # Convert to DataFrame and keep only necessary columns
            df = gdf.drop(columns=['geometry'])
            
            # Add any missing columns that the os_open_map_local table expects
            expected_columns = ['feature_id', 'feature_type', 'theme', 'created_at', 'updated_at']
            
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = None
            
            yield df[expected_columns]
            
        except Exception as e:
            logger.error(f"Error processing OS Open Map Local file: {e}")
            raise

    def process_codepoint_data(self, file_path: str) -> pd.DataFrame:
        """Process CodePoint Open postcode data"""
        logger.info(f"Processing CodePoint data: {file_path}")
        
        try:
            chunk_size = 10000
            for chunk in pd.read_csv(file_path, chunksize=chunk_size, header=None, 
                                   names=['postcode', 'positional_quality_indicator', 'eastings', 'northings', 
                                         'country_code', 'nhs_regional_ha_code', 'nhs_ha_code', 'admin_county_code', 
                                         'admin_district_code', 'admin_ward_code']):
                
                # Clean postcodes
                chunk['postcode'] = chunk['postcode'].str.strip().str.upper()
                
                # Keep only the columns that exist in the code_point_open table
                required_columns = ['postcode', 'positional_quality_indicator', 'eastings', 'northings', 
                                  'country_code', 'nhs_regional_ha_code', 'nhs_ha_code', 'admin_county_code', 
                                  'admin_district_code', 'admin_ward_code']
                
                # Add missing columns that exist in the actual table
                chunk['id'] = None  # Will be auto-generated
                chunk['location'] = None
                chunk['created_at'] = None
                
                yield chunk[required_columns]
                
        except Exception as e:
            logger.error(f"Error processing CodePoint file: {e}")
            raise

    def process_os_open_names_data(self, file_path: str) -> pd.DataFrame:
        """Process OS Open Names address data"""
        logger.info(f"Processing OS Open Names data: {file_path}")
        
        try:
            chunk_size = 10000
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                # Keep only the columns that exist in the os_open_names table
                required_columns = ['id', 'os_id', 'names_uri', 'name1', 'name1_lang', 'name2', 'name2_lang',
                                  'type', 'local_type', 'geometry_x', 'geometry_y', 'most_detail_view_res',
                                  'least_detail_view_res', 'mbr_xmin', 'mbr_ymin', 'mbr_xmax', 'mbr_ymax',
                                  'postcode_district', 'postcode_district_uri', 'populated_place', 'populated_place_uri',
                                  'admin_area', 'admin_area_uri', 'country', 'country_uri', 'created_at']
                
                # Map column names if needed
                column_mapping = {
                    'ID': 'id',
                    'NAMES_URI': 'names_uri',
                    'NAME1': 'name1',
                    'NAME1_LANG': 'name1_lang',
                    'NAME2': 'name2',
                    'NAME2_LANG': 'name2_lang',
                    'TYPE': 'type',
                    'LOCAL_TYPE': 'local_type',
                    'GEOMETRY_X': 'geometry_x',
                    'GEOMETRY_Y': 'geometry_y'
                }
                
                # Rename columns if they exist
                for old_name, new_name in column_mapping.items():
                    if old_name in chunk.columns:
                        chunk[new_name] = chunk[old_name]
                
                # Keep only the required columns that exist
                chunk = chunk[[col for col in required_columns if col in chunk.columns]]
                
                # Add missing columns as None
                for col in required_columns:
                    if col not in chunk.columns:
                        chunk[col] = None
                
                yield chunk[required_columns]
                
        except Exception as e:
            logger.error(f"Error processing OS Open Names file: {e}")
            raise

    def process_os_open_usrn_data(self, file_path: str) -> pd.DataFrame:
        """Process OS Open USRN data"""
        logger.info(f"Processing OS Open USRN data: {file_path}")
        
        try:
            import geopandas as gpd
            
            # Read the GeoPackage file
            gdf = gpd.read_file(file_path)
            
            # Convert to DataFrame and keep only necessary columns
            df = gdf.drop(columns=['geometry'])
            
            # Add any missing columns that the os_open_usrn table expects
            expected_columns = ['usrn', 'street_name', 'locality', 'town', 'administrative_area', 'postcode', 'geometry_x', 'geometry_y']
            
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = None
            
            yield df[expected_columns]
            
        except Exception as e:
            logger.error(f"Error processing OS Open USRN file: {e}")
            raise

    def clean_reference_tables(self):
        """Clean (truncate) all reference tables before insertion"""
        logger.info("Cleaning reference tables before insertion...")
        
        reference_tables = list(self.REFERENCE_TABLE_MAP.values())
        
        try:
            with self.connect_database() as conn:
                with conn.cursor() as cursor:
                    for table_name in reference_tables:
                        try:
                            cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE")
                            logger.info(f"[OK] Cleaned table: {table_name}")
                        except Exception as e:
                            logger.warning(f"[WARN] Could not clean table {table_name}: {e}")
                    
                    conn.commit()
                    logger.info("[OK] All reference tables cleaned successfully")
                    
        except Exception as e:
            logger.error(f"[ERROR] Failed to clean reference tables: {e}")
            raise

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