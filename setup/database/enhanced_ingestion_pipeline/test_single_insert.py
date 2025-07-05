#!/usr/bin/env python3
"""
Test script to insert a single record and identify the exact error
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from db_config import get_connection_string
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from datetime import datetime

def test_single_insert():
    """Test inserting a single record to identify the issue"""
    try:
        conn = psycopg2.connect(get_connection_string())
        
        # Create a simple test record
        test_data = [{
            'uprn': 123456789,
            'ba_reference': 'TEST001',
            'property_address': '123 Test Street',
            'street_descriptor': 'Test Street',
            'locality': 'Test Locality',
            'post_town': 'Test Town',
            'postcode': 'TE1 1ST',
            'property_category_code': '001',
            'property_description': 'Test Property',
            'rateable_value': 1000.0,
            'effective_date': '2023-01-01',
            'x_coordinate': 123456.0,
            'y_coordinate': 654321.0,
            'latitude': 51.5074,
            'longitude': -0.1278,
            'data_source': 'test',
            'source_priority': 1,
            'source_confidence_score': 0.95,
            'last_source_update': datetime.now(),
            'source_file_reference': 'test.csv',
            'duplicate_group_id': None,
            'is_preferred_record': True
        }]
        
        df = pd.DataFrame(test_data)
        
        print("Test data:")
        print(df.to_string())
        
        # Try to insert
        columns = df.columns.tolist()
        data = list(df.itertuples(index=False, name=None))
        
        print(f"\nColumns: {columns}")
        print(f"Data: {data}")
        
        with conn.cursor() as cursor:
            try:
                execute_values(
                    cursor,
                    f"INSERT INTO master_gazetteer ({','.join(columns)}) VALUES %s",
                    data,
                    template=None,
                    page_size=1
                )
                conn.commit()
                print("✅ Single record inserted successfully!")
                
            except Exception as e:
                print(f"❌ Insert failed: {e}")
                conn.rollback()
                
                # Try to get more details about the error
                if hasattr(e, 'pgcode'):
                    print(f"PostgreSQL error code: {e.pgcode}")
                if hasattr(e, 'pgerror'):
                    print(f"PostgreSQL error message: {e.pgerror}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error in test: {e}")

if __name__ == "__main__":
    test_single_insert() 