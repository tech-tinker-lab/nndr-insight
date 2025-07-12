#!/usr/bin/env python3
"""
Debug script to test the exact endpoint that's failing
"""

import requests
import json

API_BASE = "http://localhost:8000/api"

def test_endpoint():
    print("🔍 Testing search-tables-simple endpoint...")
    
    # Test the exact endpoint that's failing
    url = f"{API_BASE}/admin/staging/search-tables-simple"
    payload = {"query": "test", "limit": 5}
    
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error! Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    print("\n" + "="*50)
    
    # Also test the test endpoint to make sure admin router is working
    print("🔍 Testing admin router test endpoint...")
    try:
        test_response = requests.get(f"{API_BASE}/admin/test")
        print(f"Test endpoint status: {test_response.status_code}")
        print(f"Test endpoint response: {test_response.json()}")
    except Exception as e:
        print(f"Test endpoint failed: {e}")

if __name__ == "__main__":
    test_endpoint() 