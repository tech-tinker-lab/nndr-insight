import csv
import os
import io
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NNDRPropertiesIngestion:
    def __init__(self):
        self.connection_string = (
            f"postgresql://{os.getenv('PGUSER', 'nndr')}:{os.getenv('PGPASSWORD', 'nndrpass')}@"
            f"{os.getenv('PGHOST', 'localhost')}:{os.getenv('PGPORT', '5432')}/"
            f"{os.getenv('PGDATABASE', 'nndr_test')}"
)
        self.stats = {
            'total_rows': 0,
            'inserted': 0,
            'skipped': 0,
            'errors': 0
        }
    
    def get_connection(self):
        """Get a database connection with RealDictCursor"""
        return psycopg2.connect(self.connection_string, cursor_factory=RealDictCursor)

    def parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string in various formats"""
    if not date_str or not date_str.strip():
            return None
        
        date_str = date_str.strip()
        formats = [
            "%d-%b-%y", "%d/%m/%Y", "%Y-%m-%d", "%d-%b-%Y",
            "%d/%m/%y", "%d-%m-%Y", "%Y/%m/%d"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def parse_numeric(self, val: Any) -> Optional[float]:
        """Parse numeric value, handling various formats"""
        if val is None:
            return None
        
        val_str = str(val).strip()
        if val_str == '' or val_str.lower() in ['null', 'none', 'nan']:
            return None
        
        # Remove common currency symbols and commas
        val_str = val_str.replace('£', '').replace(',', '').replace('$', '')
        
        try:
            return float(val_str)
        except ValueError:
            logger.warning(f"Could not parse numeric value: {val}")
    return None

    def clean_string(self, val: Any) -> Optional[str]:
        """Clean and validate string values"""
    if val is None:
        return None
        
        val_str = str(val).strip()
        return val_str if val_str else None
    
    def create_properties_table(self):
        """Create the properties table if it doesn't exist"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS properties (
                            id SERIAL PRIMARY KEY,
                            list_altered VARCHAR(50),
                            community_code VARCHAR(20),
                            ba_reference VARCHAR(50) UNIQUE NOT NULL,
                            property_category_code VARCHAR(20),
                            property_description TEXT,
                            property_address TEXT,
                            street_descriptor VARCHAR(255),
                            locality VARCHAR(255),
                            post_town VARCHAR(255),
                            administrative_area VARCHAR(255),
                            postcode VARCHAR(10),
                            effective_date DATE,
                            partially_domestic_signal VARCHAR(10),
                            rateable_value DECIMAL(15,2),
                            scat_code VARCHAR(20),
                            appeal_settlement_code VARCHAR(20),
                            unique_property_ref VARCHAR(50),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        
                        CREATE INDEX IF NOT EXISTS idx_properties_ba_reference ON properties(ba_reference);
                        CREATE INDEX IF NOT EXISTS idx_properties_postcode ON properties(postcode);
                        CREATE INDEX IF NOT EXISTS idx_properties_rateable_value ON properties(rateable_value);
                    """)
                    conn.commit()
                    logger.info("Properties table created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating properties table: {e}")
            raise

    def ingest_nndr_rating_list(self, csv_path: str):
        """Ingest NNDR properties from CSV file"""
        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found: {csv_path}")
            return
        
        logger.info(f"Starting NNDR properties ingestion from: {csv_path}")
        
        # Create table if it doesn't exist
        self.create_properties_table()
        
        try:
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
                
                # Fix the linter error by checking if fieldnames exist
                if reader.fieldnames is None:
                    logger.error("CSV file has no headers")
                    return
                
                # Clean field names
        reader.fieldnames = [f.strip() for f in reader.fieldnames]
                logger.info(f"CSV columns: {reader.fieldnames}")
                
                # Process rows in batches
                batch_size = 1000
                batch = []
                
                for row_num, row in enumerate(reader, 1):
                    self.stats['total_rows'] += 1
                    
                    try:
                        # Extract and validate BA Reference
                        ba_reference = self.clean_string(
                            row.get('BAReference') or row.get('BAReference ', '')
                        )
                        
            if not ba_reference:
                            self.stats['skipped'] += 1
                            continue
                        
                        # Prepare data for insertion
                        property_data = {
                            'list_altered': self.clean_string(row.get('ListAltered')),
                            'community_code': self.clean_string(row.get('CommunityCode')),
                            'ba_reference': ba_reference,
                            'property_category_code': self.clean_string(row.get('PropertyCategoryCode')),
                            'property_description': self.clean_string(row.get('PropertyDescription')),
                            'property_address': self.clean_string(row.get('PropertyAddress')),
                            'street_descriptor': self.clean_string(row.get('StreetDescriptor')),
                            'locality': self.clean_string(row.get('Locality')),
                            'post_town': self.clean_string(row.get('PostTown')),
                            'administrative_area': self.clean_string(row.get('AdministrativeArea')),
                            'postcode': self.clean_string(row.get('PostCode')),
                            'effective_date': self.parse_date(row.get('EffectiveDate')),
                            'partially_domestic_signal': self.clean_string(row.get('PartiallyDomesticSignal')),
                            'rateable_value': self.parse_numeric(row.get('RateableValue')),
                            'scat_code': self.clean_string(row.get('SCATCode')),
                            'appeal_settlement_code': self.clean_string(row.get('AppealSettlementCode')),
                            'unique_property_ref': self.clean_string(row.get('UniquePropertyRef'))
                        }
                        
                        batch.append(property_data)
                        
                        # Insert batch when it reaches the batch size
                        if len(batch) >= batch_size:
                            self._insert_batch(batch)
                            batch = []
                        
                        # Log progress every 10,000 rows
                        if row_num % 10000 == 0:
                            logger.info(f"Processed {row_num} rows...")
                    
                    except Exception as e:
                        self.stats['errors'] += 1
                        logger.error(f"Error processing row {row_num}: {e}")
                        continue
                
                # Insert remaining batch
                if batch:
                    self._insert_batch(batch)
                
                logger.info("Ingestion completed successfully")
                self._print_summary()
                
        except Exception as e:
            logger.error(f"Error during ingestion: {e}")
            raise
    
    def _insert_batch(self, batch: list):
        """Insert a batch of properties using bulk COPY"""
        if not batch:
            return
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Use COPY for bulk insertion
                    columns = [
                        'list_altered', 'community_code', 'ba_reference', 'property_category_code',
                        'property_description', 'property_address', 'street_descriptor', 'locality',
                        'post_town', 'administrative_area', 'postcode', 'effective_date',
                        'partially_domestic_signal', 'rateable_value', 'scat_code',
                        'appeal_settlement_code', 'unique_property_ref'
                    ]
                    
                    # Prepare COPY data
                    copy_data = []
                    for row in batch:
                        copy_row = [
                            row.get(col) for col in columns
                        ]
                        copy_data.append(copy_row)
                    
                    # Execute COPY
                    cur.copy_from(
                        io.StringIO('\n'.join(['\t'.join(str(val) if val is not None else '' for val in row) for row in copy_data])),
                        'properties',
                        columns=columns,
                        null=''
                    )
                    
                    conn.commit()
                    self.stats['inserted'] += len(batch)
                    
        except Exception as e:
            logger.error(f"Error inserting batch: {e}")
            # Fallback to individual inserts
            self._insert_individual(batch)
    
    def _insert_individual(self, batch: list):
        """Fallback method for individual property insertion"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    for property_data in batch:
                        cur.execute("""
                INSERT INTO properties (
                                list_altered, community_code, ba_reference, property_category_code,
                                property_description, property_address, street_descriptor, locality,
                                post_town, administrative_area, postcode, effective_date,
                                partially_domestic_signal, rateable_value, scat_code,
                                appeal_settlement_code, unique_property_ref
                ) VALUES (
                                %(list_altered)s, %(community_code)s, %(ba_reference)s, %(property_category_code)s,
                                %(property_description)s, %(property_address)s, %(street_descriptor)s, %(locality)s,
                                %(post_town)s, %(administrative_area)s, %(postcode)s, %(effective_date)s,
                                %(partially_domestic_signal)s, %(rateable_value)s, %(scat_code)s,
                                %(appeal_settlement_code)s, %(unique_property_ref)s
                )
                            ON CONFLICT (ba_reference) DO NOTHING
                        """, property_data)
                    
                    conn.commit()
                    self.stats['inserted'] += len(batch)
                    
        except Exception as e:
            logger.error(f"Error in individual insertion: {e}")
            raise
    
    def _print_summary(self):
        """Print ingestion summary"""
        logger.info("=" * 50)
        logger.info("NNDR PROPERTIES INGESTION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total rows processed: {self.stats['total_rows']:,}")
        logger.info(f"Successfully inserted: {self.stats['inserted']:,}")
        logger.info(f"Skipped (no BA reference): {self.stats['skipped']:,}")
        logger.info(f"Errors: {self.stats['errors']:,}")
        logger.info(f"Success rate: {(self.stats['inserted'] / max(self.stats['total_rows'], 1) * 100):.1f}%")
        logger.info("=" * 50)

def main():
    """Main function to run the ingestion"""
    import sys
    
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        csv_path = "data/NNDR Rating List  March 2015_0.csv"
    
    try:
        ingestion = NNDRPropertiesIngestion()
        ingestion.ingest_nndr_rating_list(csv_path)
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
