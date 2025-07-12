#!/usr/bin/env python3
"""
Simple test script to verify the new endpoints are working
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000/api"

def test_admin_router():
    """Test if admin router is working"""
    print("🔍 Testing admin router...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/admin/test")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Admin router working: {data}")
            return True
        else:
            print(f"❌ Admin router failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Admin router test failed: {str(e)}")
        return False

def test_search_tables_simple():
    """Test the simple search tables endpoint"""
    print("\n🔍 Testing simple search tables endpoint...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/admin/staging/search-tables-simple",
            json={"query": "uprn", "limit": 5},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Simple search working: {data}")
            return True
        else:
            print(f"❌ Simple search failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Simple search test failed: {str(e)}")
        return False

def test_search_tables_full():
    """Test the full search tables endpoint"""
    print("\n🔍 Testing full search tables endpoint...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/admin/staging/search-tables",
            json={"query": "uprn", "limit": 5},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Full search working: {data}")
            return True
        else:
            print(f"❌ Full search failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Full search test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing New Endpoints")
    print("=" * 40)
    
    # Test admin router
    admin_working = test_admin_router()
    
    # Test simple search
    simple_working = test_search_tables_simple()
    
    # Test full search
    full_working = test_search_tables_full()
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 Test Results")
    print("=" * 40)
    print(f"Admin Router: {'✅ Working' if admin_working else '❌ Failed'}")
    print(f"Simple Search: {'✅ Working' if simple_working else '❌ Failed'}")
    print(f"Full Search: {'✅ Working' if full_working else '❌ Failed'}")
    
    if admin_working and simple_working:
        print("\n🎉 Basic functionality is working!")
        print("The frontend should now be able to search for tables.")
    else:
        print("\n⚠️  Some endpoints are not working.")
        print("Please restart the backend server and try again.")

if __name__ == "__main__":
    main() 