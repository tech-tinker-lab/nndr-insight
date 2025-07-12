#!/usr/bin/env python3
"""
Test script for enhanced staging table autocomplete functionality
"""

import requests
import json
import sys

# Configuration
API_BASE = "http://localhost:8000/api/admin/staging"

def test_table_suggestions():
    """Test the table name suggestion API"""
    print("🧪 Testing Staging Table Name Suggestions...")
    
    # Test data for different file types
    test_cases = [
        {
            "name": "ONSPD Postcode Data",
            "headers": ["pcd", "pcd2", "pcds", "x_coord", "y_coord", "lat", "long"],
            "file_name": "onspd_2024.csv",
            "expected": "onspd_staging"
        },
        {
            "name": "UPRN Property Data", 
            "headers": ["uprn", "x_coordinate", "y_coordinate", "latitude", "longitude"],
            "file_name": "uprn_data.csv",
            "expected": "os_open_uprn_staging"
        },
        {
            "name": "USRN Street Data",
            "headers": ["usrn", "street_type", "geometry"],
            "file_name": "street_data.csv", 
            "expected": "os_open_usrn_staging"
        },
        {
            "name": "NNDR Properties",
            "headers": ["rateable_value", "property_address", "postcode", "uprn"],
            "file_name": "nndr_properties.csv",
            "expected": "nndr_properties_staging"
        },
        {
            "name": "LAD Boundaries",
            "headers": ["boundary_name", "geometry", "lad_code"],
            "file_name": "lad_boundaries.csv",
            "expected": "lad_boundaries_staging"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"   Headers: {test_case['headers']}")
        print(f"   File: {test_case['file_name']}")
        
        try:
            response = requests.post(
                f"{API_BASE}/suggest-table-name",
                json={
                    "headers": test_case["headers"],
                    "file_name": test_case["file_name"],
                    "content_preview": "Sample content for testing"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get("suggestions", [])
                
                print(f"   ✅ API Response: {response.status_code}")
                print(f"   📊 Found {len(suggestions)} suggestions")
                
                # Check if expected suggestion is in top results
                top_suggestions = [s["name"] for s in suggestions[:3]]
                if test_case["expected"] in top_suggestions:
                    print(f"   🎯 Expected '{test_case['expected']}' found in top suggestions")
                else:
                    print(f"   ⚠️  Expected '{test_case['expected']}' not in top suggestions: {top_suggestions}")
                
                # Show top suggestions
                for j, suggestion in enumerate(suggestions[:3], 1):
                    confidence = suggestion.get("confidence", 0)
                    reason = suggestion.get("reason", "No reason provided")
                    print(f"   {j}. {suggestion['name']} ({confidence:.1%}) - {reason}")
                    
            else:
                print(f"   ❌ API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")

def test_existing_tables():
    """Test getting existing staging tables"""
    print("\n🧪 Testing Existing Tables API...")
    
    try:
        response = requests.get(f"{API_BASE}/tables", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            tables = data.get("staging_tables", [])
            
            print(f"   ✅ Found {len(tables)} existing staging tables")
            for table in tables:
                print(f"   📋 {table}")
        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")

def test_config_management():
    """Test configuration management APIs"""
    print("\n🧪 Testing Configuration Management...")
    
    # Test getting configurations
    try:
        response = requests.get(f"{API_BASE}/configs", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            configs = data.get("configs", [])
            
            print(f"   ✅ Found {len(configs)} saved configurations")
            for config in configs:
                print(f"   📋 {config['name']} -> {config['staging_table_name']} ({config['mapping_count']} mappings)")
        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")

def main():
    """Main test function"""
    print("🚀 Enhanced Staging Table Autocomplete Test Suite")
    print("=" * 60)
    
    # Test existing tables first
    test_existing_tables()
    
    # Test table suggestions
    test_table_suggestions()
    
    # Test configuration management
    test_config_management()
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("\n💡 To test the frontend:")
    print("   1. Start the backend: python -m uvicorn backend.app.main:app --reload")
    print("   2. Start the frontend: npm start (in frontend directory)")
    print("   3. Go to Upload page and test the enhanced autocomplete")

if __name__ == "__main__":
    main() 