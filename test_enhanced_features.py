#!/usr/bin/env python3
"""
Test script for enhanced staging table and column mapping features
Tests the improvements made to address user feedback:
1. Table match vs column confidence alignment
2. New table handling with proper data types
3. Geometry field detection
4. Upload action suggestions
"""

import requests
import json
import time
from typing import Dict, List, Any

# Configuration
API_BASE_URL = "http://localhost:8000/api"
TEST_HEADERS = [
    "postcode", "property_address", "rateable_value", "uprn", 
    "latitude", "longitude", "geometry", "effective_date"
]
TEST_FILE_NAME = "test_property_data.csv"

def test_table_name_suggestions():
    """Test table name suggestions with improved confidence scoring"""
    print("=== Testing Table Name Suggestions ===")
    
    try:
        response = requests.post(f"{API_BASE_URL}/admin/staging/suggest-table-name", json={
            "headers": TEST_HEADERS,
            "file_name": TEST_FILE_NAME,
            "content_preview": "Sample content with postcodes and property data"
        })
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Table suggestions received successfully")
            print(f"Found {len(data.get('suggestions', []))} suggestions")
            
            for i, suggestion in enumerate(data.get('suggestions', [])[:3]):
                print(f"  {i+1}. {suggestion['name']} ({suggestion['confidence']:.1%} confidence)")
                print(f"     Type: {suggestion['type']}, Reason: {suggestion['reason']}")
            
            return data.get('suggestions', [])
        else:
            print(f"❌ Failed to get table suggestions: {response.status_code}")
            print(response.text)
            return []
            
    except Exception as e:
        print(f"❌ Error testing table suggestions: {e}")
        return []

def test_column_mapping_generation():
    """Test column mapping generation with new table handling"""
    print("\n=== Testing Column Mapping Generation ===")
    
    # Test with existing table
    print("Testing with existing table (onspd_staging):")
    test_existing_table_mapping("onspd_staging")
    
    # Test with new table
    print("\nTesting with new table (custom_properties_staging):")
    test_new_table_mapping("custom_properties_staging")
    
    # Test with geometry table
    print("\nTesting with geometry table (boundaries_staging):")
    test_geometry_table_mapping("boundaries_staging")

def test_existing_table_mapping(table_name: str):
    """Test mapping generation for existing table"""
    try:
        response = requests.post(f"{API_BASE_URL}/admin/staging/generate-mappings", json={
            "headers": TEST_HEADERS,
            "staging_table_name": table_name,
            "file_name": TEST_FILE_NAME,
            "content_preview": "Sample content"
        })
        
        if response.status_code == 200:
            data = response.json()
            mappings = data.get('mappings', [])
            match_status = data.get('match_status', {})
            
            print(f"✅ Generated {len(mappings)} mappings for {table_name}")
            print(f"Match status: {match_status.get('status')} ({match_status.get('confidence', 0):.1%})")
            print(f"Message: {match_status.get('message')}")
            
            # Check for specific mapping types
            exact_matches = [m for m in mappings if m['matchStatus'] == 'exact']
            partial_matches = [m for m in mappings if m['matchStatus'] == 'partial']
            semantic_matches = [m for m in mappings if m['matchStatus'] == 'semantic']
            
            print(f"  - Exact matches: {len(exact_matches)}")
            print(f"  - Partial matches: {len(partial_matches)}")
            print(f"  - Semantic matches: {len(semantic_matches)}")
            
            # Show some example mappings
            for mapping in mappings[:3]:
                print(f"    {mapping['sourceColumn']} → {mapping['targetColumn']} ({mapping['dataType']}) - {mapping['matchStatus']}")
            
        else:
            print(f"❌ Failed to generate mappings: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error testing existing table mapping: {e}")

def test_new_table_mapping(table_name: str):
    """Test mapping generation for new table"""
    try:
        response = requests.post(f"{API_BASE_URL}/admin/staging/generate-mappings", json={
            "headers": TEST_HEADERS,
            "staging_table_name": table_name,
            "file_name": TEST_FILE_NAME,
            "content_preview": "Sample content"
        })
        
        if response.status_code == 200:
            data = response.json()
            mappings = data.get('mappings', [])
            match_status = data.get('match_status', {})
            
            print(f"✅ Generated {len(mappings)} mappings for new table {table_name}")
            print(f"Match status: {match_status.get('status')} ({match_status.get('confidence', 0):.1%})")
            print(f"Message: {match_status.get('message')}")
            
            # Check for new table mappings
            new_table_mappings = [m for m in mappings if m['matchStatus'] == 'new_table']
            suggested_mappings = [m for m in mappings if m['matchStatus'] == 'suggested']
            
            print(f"  - New table mappings: {len(new_table_mappings)}")
            print(f"  - Suggested mappings: {len(suggested_mappings)}")
            
            # Check data type inference
            geometry_fields = [m for m in mappings if m['dataType'] == 'geometry']
            date_fields = [m for m in mappings if m['dataType'] in ['date', 'timestamp']]
            numeric_fields = [m for m in mappings if m['dataType'] in ['integer', 'decimal']]
            
            print(f"  - Geometry fields: {len(geometry_fields)}")
            print(f"  - Date fields: {len(date_fields)}")
            print(f"  - Numeric fields: {len(numeric_fields)}")
            
            # Show some example mappings
            for mapping in mappings[:3]:
                print(f"    {mapping['sourceColumn']} → {mapping['targetColumn']} ({mapping['dataType']}) - {mapping['matchStatus']}")
            
        else:
            print(f"❌ Failed to generate mappings: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error testing new table mapping: {e}")

def test_geometry_table_mapping(table_name: str):
    """Test mapping generation for geometry table"""
    geometry_headers = ["boundary_name", "geometry", "lad_code", "area_hectares", "created_date"]
    
    try:
        response = requests.post(f"{API_BASE_URL}/admin/staging/generate-mappings", json={
            "headers": geometry_headers,
            "staging_table_name": table_name,
            "file_name": "test_boundaries.csv",
            "content_preview": "Sample geometry content"
        })
        
        if response.status_code == 200:
            data = response.json()
            mappings = data.get('mappings', [])
            match_status = data.get('match_status', {})
            
            print(f"✅ Generated {len(mappings)} mappings for geometry table {table_name}")
            print(f"Match status: {match_status.get('status')} ({match_status.get('confidence', 0):.1%})")
            
            # Check geometry field detection
            geometry_mappings = [m for m in mappings if m['dataType'] == 'geometry']
            print(f"  - Geometry fields detected: {len(geometry_mappings)}")
            
            for mapping in geometry_mappings:
                print(f"    {mapping['sourceColumn']} → {mapping['targetColumn']} (geometry)")
            
        else:
            print(f"❌ Failed to generate geometry mappings: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error testing geometry table mapping: {e}")

def test_upload_action_suggestions():
    """Test upload action suggestions"""
    print("\n=== Testing Upload Action Suggestions ===")
    
    try:
        response = requests.post(f"{API_BASE_URL}/admin/staging/suggest-actions", json={
            "headers": TEST_HEADERS,
            "file_name": TEST_FILE_NAME,
            "file_type": "csv",
            "content_preview": "Sample content"
        })
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            existing_configs = data.get('existing_configs', [])
            
            print(f"✅ Generated {len(suggestions)} action suggestions")
            print(f"Found {len(existing_configs)} similar existing configurations")
            
            for suggestion in suggestions:
                print(f"  - {suggestion['title']} ({suggestion['priority']} priority)")
                print(f"    {suggestion['description']}")
            
            if existing_configs:
                print("\nSimilar existing configurations:")
                for config in existing_configs[:3]:
                    print(f"  - {config['config_name']} ({config['similarity']:.1%} match)")
            
        else:
            print(f"❌ Failed to get action suggestions: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error testing action suggestions: {e}")

def test_confidence_alignment():
    """Test that table confidence and column confidence are aligned"""
    print("\n=== Testing Confidence Alignment ===")
    
    try:
        # Get table suggestions
        table_response = requests.post(f"{API_BASE_URL}/admin/staging/suggest-table-name", json={
            "headers": TEST_HEADERS,
            "file_name": TEST_FILE_NAME,
            "content_preview": "Sample content"
        })
        
        if table_response.status_code == 200:
            table_data = table_response.json()
            best_table = table_data.get('suggestions', [{}])[0]
            table_confidence = best_table.get('confidence', 0)
            
            print(f"Best table suggestion: {best_table.get('name')} ({table_confidence:.1%})")
            
            # Get column mappings for this table
            mapping_response = requests.post(f"{API_BASE_URL}/admin/staging/generate-mappings", json={
                "headers": TEST_HEADERS,
                "staging_table_name": best_table.get('name'),
                "file_name": TEST_FILE_NAME,
                "content_preview": "Sample content"
            })
            
            if mapping_response.status_code == 200:
                mapping_data = mapping_response.json()
                mapping_confidence = mapping_data.get('match_status', {}).get('confidence', 0)
                
                print(f"Column mapping confidence: {mapping_confidence:.1%}")
                
                # Check alignment
                confidence_diff = abs(table_confidence - mapping_confidence)
                if confidence_diff < 0.2:  # Within 20%
                    print("✅ Confidence levels are reasonably aligned")
                else:
                    print(f"⚠️  Confidence levels differ significantly ({confidence_diff:.1%})")
                
                # Show breakdown
                mappings = mapping_data.get('mappings', [])
                exact_count = len([m for m in mappings if m['matchStatus'] == 'exact'])
                partial_count = len([m for m in mappings if m['matchStatus'] == 'partial'])
                semantic_count = len([m for m in mappings if m['matchStatus'] == 'semantic'])
                
                print(f"  - Exact matches: {exact_count}")
                print(f"  - Partial matches: {partial_count}")
                print(f"  - Semantic matches: {semantic_count}")
                
            else:
                print(f"❌ Failed to get column mappings: {mapping_response.status_code}")
                
        else:
            print(f"❌ Failed to get table suggestions: {table_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing confidence alignment: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing Enhanced Staging Table and Column Mapping Features")
    print("=" * 70)
    
    # Test table name suggestions
    test_table_name_suggestions()
    
    # Test column mapping generation
    test_column_mapping_generation()
    
    # Test upload action suggestions
    test_upload_action_suggestions()
    
    # Test confidence alignment
    test_confidence_alignment()
    
    print("\n" + "=" * 70)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main() 