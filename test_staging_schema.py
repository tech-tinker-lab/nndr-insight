#!/usr/bin/env python3
"""
Test script to verify staging schema integration
"""

import requests
import json
import time

API_BASE = "http://localhost:8000/api"

def test_staging_schema():
    """Test the staging schema integration"""
    
    print("🧪 Testing Staging Schema Integration")
    print("=" * 50)
    
    # Test 1: Check if staging schema exists
    print("\n1. Testing staging schema existence...")
    try:
        response = requests.get(f"{API_BASE}/admin/staging/tables")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Staging tables endpoint working")
            print(f"   Total tables: {data.get('total_count', 0)}")
            print(f"   Public schema: {data.get('public_count', 0)}")
            print(f"   Staging schema: {data.get('staging_count', 0)}")
        else:
            print(f"❌ Failed to get staging tables: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing staging tables: {e}")
    
    # Test 2: Test table search
    print("\n2. Testing table search...")
    try:
        search_data = {"query": "uprn", "limit": 5}
        response = requests.post(f"{API_BASE}/admin/staging/search-tables", json=search_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Table search working")
            print(f"   Found {data.get('total_found', 0)} suggestions")
            for suggestion in data.get('suggestions', [])[:3]:
                print(f"   - {suggestion.get('full_name', suggestion.get('name'))} ({suggestion.get('confidence', 0):.2f})")
        else:
            print(f"❌ Failed to search tables: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing table search: {e}")
    
    # Test 3: Test simple search endpoint
    print("\n3. Testing simple search endpoint...")
    try:
        search_data = {"query": "test", "limit": 3}
        response = requests.post(f"{API_BASE}/admin/staging/search-tables-simple", json=search_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Simple search working")
            print(f"   Found {len(data.get('suggestions', []))} suggestions")
        else:
            print(f"❌ Failed simple search: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing simple search: {e}")
    
    # Test 4: Test admin router
    print("\n4. Testing admin router...")
    try:
        response = requests.get(f"{API_BASE}/admin/test")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Admin router working: {data.get('message', 'Unknown')}")
        else:
            print(f"❌ Admin router failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing admin router: {e}")
    
    # Test 5: Test staging configs
    print("\n5. Testing staging configs...")
    try:
        response = requests.get(f"{API_BASE}/admin/staging/configs")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Staging configs endpoint working")
            print(f"   Found {len(data.get('configs', []))} configurations")
        else:
            print(f"❌ Failed to get staging configs: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing staging configs: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Staging Schema Integration Test Complete")
    print("\nNext steps:")
    print("1. Restart the backend server to pick up changes")
    print("2. Test file upload functionality")
    print("3. Verify staging schema tables are being used")

if __name__ == "__main__":
    test_staging_schema() 