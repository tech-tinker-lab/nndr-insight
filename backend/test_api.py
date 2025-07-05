#!/usr/bin/env python3
"""
Simple test script for the NNDR Insight API
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 Testing {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict) and len(result) > 0:
                print(f"📊 Response keys: {list(result.keys())}")
                if 'total_found' in result:
                    print(f"📈 Total found: {result['total_found']}")
                elif 'summary' in result:
                    print(f"📈 Summary: {result['summary']}")
            elif isinstance(result, list):
                print(f"📊 Response items: {len(result)}")
        else:
            print(f"❌ Error: {response.text}")
            
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run API tests"""
    print("🚀 Starting NNDR Insight API Tests")
    print("=" * 50)
    
    # Test basic endpoints
    tests = [
        ("/", "GET"),
        ("/geospatial/", "GET"),
        ("/geospatial/health", "GET"),
        ("/analytics/", "GET"),
        ("/analytics/health", "GET"),
        ("/geospatial/statistics", "GET"),
        ("/geospatial/datasets", "GET"),
        ("/analytics/coverage", "GET"),
        ("/analytics/regions", "GET"),
        ("/analytics/postcode-analysis", "GET"),
    ]
    
    # Test POST endpoints separately
    post_tests = [
        ("/geospatial/geocode", "POST", {"query": "London", "limit": 5}),
        ("/geospatial/search", "POST", {"postcode": "SW1A", "limit": 10}),
        ("/geospatial/spatial", "POST", {"latitude": 51.5074, "longitude": -0.1278, "radius_meters": 1000}),
    ]
    
    # Run GET tests
    passed = 0
    total = len(tests) + len(post_tests)
    
    for endpoint, method in tests:
        success = test_endpoint(endpoint, method)
        if success:
            passed += 1
        time.sleep(0.5)  # Small delay between requests
    
    # Run POST tests
    for endpoint, method, data in post_tests:
        success = test_endpoint(endpoint, method, data)
        if success:
            passed += 1
        time.sleep(0.5)  # Small delay between requests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the API logs for details.")

if __name__ == "__main__":
    main() 