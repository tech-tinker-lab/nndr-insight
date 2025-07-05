#!/usr/bin/env python3
"""
Test script for NNDR Properties Ingestion
"""

import os
import sys
import tempfile
import csv
from ingest_nndr_properties import NNDRPropertiesIngestion

def create_test_csv():
    """Create a test CSV file with sample NNDR data"""
    test_data = [
        {
            'ListAltered': 'Y',
            'CommunityCode': 'TEST001',
            'BAReference': 'BA123456',
            'PropertyCategoryCode': 'CAT001',
            'PropertyDescription': 'Test Property 1',
            'PropertyAddress': '123 Test Street',
            'StreetDescriptor': 'Street',
            'Locality': 'Test Town',
            'PostTown': 'Test City',
            'AdministrativeArea': 'Test County',
            'PostCode': 'TE1 1ST',
            'EffectiveDate': '01-Jan-15',
            'PartiallyDomesticSignal': 'N',
            'RateableValue': '50000',
            'SCATCode': 'SCAT001',
            'AppealSettlementCode': 'ASC001',
            'UniquePropertyRef': 'UPR001'
        },
        {
            'ListAltered': 'N',
            'CommunityCode': 'TEST002',
            'BAReference': 'BA789012',
            'PropertyCategoryCode': 'CAT002',
            'PropertyDescription': 'Test Property 2',
            'PropertyAddress': '456 Sample Road',
            'StreetDescriptor': 'Road',
            'Locality': 'Sample Village',
            'PostTown': 'Sample City',
            'AdministrativeArea': 'Sample County',
            'PostCode': 'SA1 2MP',
            'EffectiveDate': '15-Mar-15',
            'PartiallyDomesticSignal': 'Y',
            'RateableValue': '75000',
            'SCATCode': 'SCAT002',
            'AppealSettlementCode': 'ASC002',
            'UniquePropertyRef': 'UPR002'
        }
    ]
    
    # Create temporary CSV file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    
    with temp_file:
        writer = csv.DictWriter(temp_file, fieldnames=test_data[0].keys())
        writer.writeheader()
        writer.writerows(test_data)
    
    return temp_file.name

def test_ingestion():
    """Test the NNDR properties ingestion"""
    print("Testing NNDR Properties Ingestion...")
    
    # Create test CSV
    test_csv_path = create_test_csv()
    print(f"Created test CSV: {test_csv_path}")
    
    try:
        # Initialize ingestion
        ingestion = NNDRPropertiesIngestion()
        
        # Test table creation
        print("Testing table creation...")
        ingestion.create_properties_table()
        
        # Test ingestion
        print("Testing data ingestion...")
        ingestion.ingest_nndr_rating_list(test_csv_path)
        
        # Verify results
        print("\nVerifying results...")
        with ingestion.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM properties")
                count = cur.fetchone()['count']
                print(f"Total properties in database: {count}")
                
                cur.execute("SELECT ba_reference, property_description, rateable_value FROM properties ORDER BY ba_reference")
                properties = cur.fetchall()
                for prop in properties:
                    print(f"  - {prop['ba_reference']}: {prop['property_description']} (£{prop['rateable_value']})")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    
    finally:
        # Clean up test file
        try:
            os.unlink(test_csv_path)
            print(f"Cleaned up test file: {test_csv_path}")
        except:
            pass
    
    return True

if __name__ == "__main__":
    success = test_ingestion()
    sys.exit(0 if success else 1) 