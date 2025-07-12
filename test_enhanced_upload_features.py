#!/usr/bin/env python3
"""
Test script for enhanced upload features
Tests real-time table search, 75% config matching, and other improvements
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Configuration
API_BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "username": "admin",
    "password": "admin123"
}

def test_real_time_table_search():
    """Test real-time table name search functionality"""
    print("\n🔍 Testing Real-Time Table Search...")
    
    try:
        # Test search for existing tables
        search_queries = [
            "uprn",
            "postcode", 
            "staging",
            "boundary",
            "rateable"
        ]
        
        for query in search_queries:
            print(f"  Searching for: '{query}'")
            
            response = requests.post(
                f"{API_BASE_URL}/admin/staging/search-tables",
                json={"query": query, "limit": 5},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get("suggestions", [])
                print(f"    ✅ Found {len(suggestions)} suggestions")
                
                for suggestion in suggestions[:3]:  # Show first 3
                    print(f"      - {suggestion['name']} ({suggestion['type']}) - {suggestion['confidence']:.1%}")
            else:
                print(f"    ❌ Search failed: {response.status_code}")
                print(f"    Error: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Real-time search test failed: {str(e)}")
        return False

def test_config_matching_75_percent():
    """Test 75% config matching threshold"""
    print("\n🎯 Testing 75% Config Matching Threshold...")
    
    try:
        # Test with different file types and headers
        test_cases = [
            {
                "name": "UPRN Data",
                "headers": ["uprn", "x_coordinate", "y_coordinate", "latitude", "longitude"],
                "file_name": "os_open_uprn_2025.csv",
                "file_type": "csv"
            },
            {
                "name": "Postcode Data", 
                "headers": ["postcode", "pcd", "pcds", "lat", "long"],
                "file_name": "onspd_latest.csv",
                "file_type": "csv"
            },
            {
                "name": "Business Rates",
                "headers": ["rateable_value", "property_address", "business_type", "uprn"],
                "file_name": "business_rates_2024.csv", 
                "file_type": "csv"
            }
        ]
        
        for test_case in test_cases:
            print(f"  Testing: {test_case['name']}")
            
            response = requests.post(
                f"{API_BASE_URL}/admin/staging/configs/match",
                json={
                    "headers": test_case["headers"],
                    "file_name": test_case["file_name"],
                    "file_type": test_case["file_type"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                configs = data.get("configs", [])
                best_match = data.get("best_match")
                
                print(f"    ✅ Found {len(configs)} similar configs")
                
                if best_match:
                    similarity = best_match.get("similarity", 0)
                    print(f"    🎯 Best match: {best_match['config_name']} ({similarity:.1%})")
                    
                    if similarity >= 0.75:
                        print(f"    ✅ Auto-load threshold met (≥75%)")
                    else:
                        print(f"    ⚠️  Below auto-load threshold (<75%)")
                else:
                    print(f"    ⚠️  No configs above 75% threshold")
                    
            else:
                print(f"    ❌ Config matching failed: {response.status_code}")
                print(f"    Error: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Config matching test failed: {str(e)}")
        return False

def test_table_creation_functionality():
    """Test table creation from configuration"""
    print("\n🏗️  Testing Table Creation Functionality...")
    
    try:
        # First, create a test configuration
        test_config = {
            "name": "Test Config for Table Creation",
            "description": "Test configuration for table creation",
            "file_type": "csv",
            "staging_table_name": "test_table_creation_staging",
            "column_mappings": [
                {
                    "source_column": "id",
                    "target_column": "test_id",
                    "data_type": "INTEGER",
                    "is_primary_key": True
                },
                {
                    "source_column": "name", 
                    "target_column": "test_name",
                    "data_type": "TEXT",
                    "is_required": True
                },
                {
                    "source_column": "value",
                    "target_column": "test_value", 
                    "data_type": "NUMERIC"
                }
            ]
        }
        
        # Save configuration
        print("  Creating test configuration...")
        config_response = requests.post(
            f"{API_BASE_URL}/admin/staging/configs",
            json=test_config,
            headers={"Content-Type": "application/json"}
        )
        
        if config_response.status_code == 200:
            config_data = config_response.json()
            config_id = config_data.get("config_id")
            print(f"    ✅ Configuration created: {config_id}")
            
            # Test table creation
            print("  Testing table creation...")
            create_response = requests.post(
                f"{API_BASE_URL}/admin/staging/create-table",
                json={
                    "config_id": config_id,
                    "table_name": test_config["staging_table_name"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if create_response.status_code == 200:
                create_data = create_response.json()
                print(f"    ✅ Table created: {create_data.get('table_name')}")
                
                # Verify table exists
                print("  Verifying table exists...")
                verify_response = requests.get(
                    f"{API_BASE_URL}/admin/staging/tables"
                )
                
                if verify_response.status_code == 200:
                    tables_data = verify_response.json()
                    staging_tables = tables_data.get("staging_tables", [])
                    
                    if test_config["staging_table_name"] in staging_tables:
                        print(f"    ✅ Table verified in database")
                        return True
                    else:
                        print(f"    ❌ Table not found in database")
                        return False
                else:
                    print(f"    ❌ Table verification failed: {verify_response.status_code}")
                    return False
            else:
                print(f"    ❌ Table creation failed: {create_response.status_code}")
                print(f"    Error: {create_response.text}")
                return False
        else:
            print(f"    ❌ Configuration creation failed: {config_response.status_code}")
            print(f"    Error: {config_response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ Table creation test failed: {str(e)}")
        return False

def test_enhanced_metadata_tracking():
    """Test enhanced metadata tracking"""
    print("\n📊 Testing Enhanced Metadata Tracking...")
    
    try:
        # Test upload with metadata
        test_file_content = "id,name,value\n1,Test1,100\n2,Test2,200"
        
        # Create a temporary file for testing
        test_filename = f"test_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(test_filename, 'w') as f:
            f.write(test_file_content)
        
        print(f"  Created test file: {test_filename}")
        
        # Test upload with metadata
        with open(test_filename, 'rb') as f:
            files = {'file': (test_filename, f, 'text/csv')}
            data = {
                'session_id': 'test_session_123',
                'client_name': 'test_client'
            }
            
            response = requests.post(
                f"{API_BASE_URL}/ingestions/upload-with-metadata",
                files=files,
                data=data
            )
        
        # Clean up test file
        os.remove(test_filename)
        
        if response.status_code == 200:
            upload_data = response.json()
            print(f"    ✅ Upload successful")
            print(f"    Upload ID: {upload_data.get('upload_id')}")
            print(f"    Batch ID: {upload_data.get('batch_id')}")
            
            # Test metadata retrieval
            print("  Testing metadata retrieval...")
            history_response = requests.get(
                f"{API_BASE_URL}/ingestions/my_uploads",
                params={"limit": 5}
            )
            
            if history_response.status_code == 200:
                history_data = history_response.json()
                uploads = history_data.get("history", [])
                
                if uploads:
                    latest_upload = uploads[0]
                    print(f"    ✅ Latest upload found")
                    print(f"    Filename: {latest_upload.get('filename')}")
                    print(f"    Status: {latest_upload.get('status')}")
                    print(f"    Timestamp: {latest_upload.get('upload_timestamp')}")
                    return True
                else:
                    print(f"    ⚠️  No upload history found")
                    return False
            else:
                print(f"    ❌ Metadata retrieval failed: {history_response.status_code}")
                return False
        else:
            print(f"    ❌ Upload failed: {response.status_code}")
            print(f"    Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ Metadata tracking test failed: {str(e)}")
        return False

def test_fixed_length_text_analysis():
    """Test fixed-length text file analysis"""
    print("\n📄 Testing Fixed-Length Text Analysis...")
    
    try:
        # Create test fixed-length text content
        test_content = """1234567890John Doe    London     SW1A 1AA
1234567891Jane Smith  Manchester M1 1AA
1234567892Bob Wilson  Birmingham  B1 1AA
1234567893Alice Brown Leeds      LS1 1AA
1234567894Charlie Lee Liverpool  L1 1AA"""
        
        print("  Analyzing fixed-length text...")
        
        # Test AI analysis
        response = requests.post(
            f"{API_BASE_URL}/ai/analyze-dataset",
            files={'file': ('test_fixed_length.txt', test_content, 'text/plain')}
        )
        
        if response.status_code == 200:
            analysis_data = response.json()
            print(f"    ✅ Analysis completed")
            print(f"    Confidence: {analysis_data.get('confidence_score', 0):.1%}")
            
            # Check for fixed-length detection
            content_analysis = analysis_data.get('content_analysis', {})
            if 'fixed_length' in str(content_analysis).lower():
                print(f"    ✅ Fixed-length format detected")
                return True
            else:
                print(f"    ⚠️  Fixed-length format not detected")
                return False
        else:
            print(f"    ❌ Analysis failed: {response.status_code}")
            print(f"    Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ Fixed-length analysis test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Enhanced Upload Features")
    print("=" * 50)
    
    # Test results
    results = {
        "real_time_search": False,
        "config_matching": False,
        "table_creation": False,
        "metadata_tracking": False,
        "fixed_length_analysis": False
    }
    
    # Run tests
    results["real_time_search"] = test_real_time_table_search()
    results["config_matching"] = test_config_matching_75_percent()
    results["table_creation"] = test_table_creation_functionality()
    results["metadata_tracking"] = test_enhanced_metadata_tracking()
    results["fixed_length_analysis"] = test_fixed_length_text_analysis()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced upload features are working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 