#!/usr/bin/env python3
"""
Test to simulate typing in the Staging Table Name field
"""

import requests
import json

API_BASE = "http://localhost:8000/api"

def test_table_search_simulation():
    """Simulate what happens when typing in the table name field"""
    
    print("🔍 Testing Table Name Field Behavior")
    print("=" * 50)
    
    # Test different search queries that a user might type
    test_queries = [
        "uprn",           # Should find UPRN tables
        "postcode",       # Should find postcode tables
        "test",           # Should find test tables
        "new_table",      # Should suggest new table
        "staging",        # Should find staging tables
        "os_open",        # Should find OS Open tables
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        try:
            # Test the simple endpoint (what the frontend uses)
            response = requests.post(f"{API_BASE}/admin/staging/search-tables-simple", 
                                   json={"query": query, "limit": 5})
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get('suggestions', [])
                print(f"✅ Found {len(suggestions)} suggestions:")
                
                for i, suggestion in enumerate(suggestions, 1):
                    confidence = suggestion.get('confidence', 0)
                    name = suggestion.get('name', 'Unknown')
                    description = suggestion.get('description', 'No description')
                    suggestion_type = suggestion.get('type', 'unknown')
                    
                    print(f"   {i}. {name} ({suggestion_type}) - {confidence:.1%}")
                    print(f"      {description}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Complete")
    print("\nExpected behavior in frontend:")
    print("1. Type 2+ characters to trigger search")
    print("2. See dropdown with suggestions")
    print("3. Click or use arrow keys to select")
    print("4. Press Enter to confirm selection")

if __name__ == "__main__":
    test_table_search_simulation() 