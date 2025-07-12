#!/usr/bin/env python3
"""
Quick test to debug the 404 issue with search-tables-simple endpoint
"""

import requests
import json

API_BASE = "http://localhost:8000/api"

def test_endpoints():
    """Test various endpoints to debug the 404 issue"""
    
    print("🔍 Debugging 404 Issue")
    print("=" * 40)
    
    # Test 1: Check if server is running
    print("\n1. Testing server connectivity...")
    try:
        response = requests.get(f"{API_BASE.replace('/api', '')}/")
        print(f"✅ Server running: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return
    
    # Test 2: Test admin router base
    print("\n2. Testing admin router...")
    try:
        response = requests.get(f"{API_BASE}/admin/test")
        print(f"✅ Admin router: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Admin router error: {e}")
    
    # Test 3: Test staging tables endpoint
    print("\n3. Testing staging tables...")
    try:
        response = requests.get(f"{API_BASE}/admin/staging/tables")
        print(f"✅ Staging tables: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total tables: {data.get('total_count', 0)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Staging tables error: {e}")
    
    # Test 4: Test the problematic endpoint
    print("\n4. Testing search-tables-simple...")
    try:
        search_data = {"query": "test", "limit": 3}
        response = requests.post(f"{API_BASE}/admin/staging/search-tables-simple", json=search_data)
        print(f"✅ Search tables simple: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Suggestions: {len(data.get('suggestions', []))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Search tables simple error: {e}")
    
    # Test 5: Test alternative search endpoint
    print("\n5. Testing main search-tables...")
    try:
        search_data = {"query": "test", "limit": 3}
        response = requests.post(f"{API_BASE}/admin/staging/search-tables", json=search_data)
        print(f"✅ Search tables main: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Suggestions: {len(data.get('suggestions', []))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Search tables main error: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 Debug Complete")
    print("\nIf you see 404 errors:")
    print("1. Restart the backend server")
    print("2. Check the server logs for errors")
    print("3. Verify the admin router is properly imported")

if __name__ == "__main__":
    test_endpoints() 