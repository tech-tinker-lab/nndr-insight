#!/usr/bin/env python3
"""
Test script for enhanced AI column mapping functionality
"""

import requests
import json
import sys

# Configuration
API_BASE = "http://localhost:8000/api/admin/staging"

def test_ai_column_mappings():
    """Test the AI column mapping generation"""
    print("🧪 Testing AI Column Mapping Generation...")
    
    # Test data for different file types
    test_cases = [
        {
            "name": "ONSPD Postcode Data",
            "headers": ["pcd", "pcd2", "pcds", "x_coord", "y_coord", "lat", "long"],
            "file_name": "onspd_2024.csv",
            "staging_table": "onspd_staging",
            "expected_matches": ["pcd", "pcd2", "pcds", "x_coord", "y_coord", "lat", "long"]
        },
        {
            "name": "UPRN Property Data", 
            "headers": ["uprn", "x_coordinate", "y_coordinate", "latitude", "longitude"],
            "file_name": "uprn_data.csv",
            "staging_table": "os_open_uprn_staging",
            "expected_matches": ["uprn", "x_coordinate", "y_coordinate", "latitude", "longitude"]
        },
        {
            "name": "NNDR Properties",
            "headers": ["rateable_value", "property_address", "postcode", "uprn", "ba_reference"],
            "file_name": "nndr_properties.csv",
            "staging_table": "nndr_properties_staging",
            "expected_matches": ["rateable_value", "property_address", "postcode", "uprn", "ba_reference"]
        },
        {
            "name": "New Custom Table",
            "headers": ["custom_field_1", "custom_field_2", "custom_field_3"],
            "file_name": "custom_data.csv",
            "staging_table": "new_custom_staging",
            "expected_matches": []  # Should generate AI suggestions
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"   Headers: {test_case['headers']}")
        print(f"   Table: {test_case['staging_table']}")
        
        try:
            response = requests.post(
                f"{API_BASE}/generate-mappings",
                json={
                    "headers": test_case["headers"],
                    "staging_table_name": test_case["staging_table"],
                    "file_name": test_case["file_name"],
                    "content_preview": "Sample content for testing"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                mappings = data.get("mappings", [])
                match_status = data.get("match_status", {})
                suggestions = data.get("suggestions", [])
                
                print(f"   ✅ API Response: {response.status_code}")
                print(f"   📊 Generated {len(mappings)} mappings")
                print(f"   🎯 Match Status: {match_status.get('status', 'unknown')} ({match_status.get('confidence', 0):.1%})")
                print(f"   💡 Suggestions: {len(suggestions)}")
                
                # Analyze mapping quality
                exact_matches = sum(1 for m in mappings if m.get("matchStatus") == "exact")
                partial_matches = sum(1 for m in mappings if m.get("matchStatus") == "partial")
                semantic_matches = sum(1 for m in mappings if m.get("matchStatus") == "semantic")
                suggested_matches = sum(1 for m in mappings if m.get("matchStatus") == "suggested")
                
                print(f"   📈 Mapping Quality:")
                print(f"      • Exact matches: {exact_matches}")
                print(f"      • Partial matches: {partial_matches}")
                print(f"      • Semantic matches: {semantic_matches}")
                print(f"      • AI suggested: {suggested_matches}")
                
                # Show top mappings
                print(f"   🔍 Top Mappings:")
                for j, mapping in enumerate(mappings[:3], 1):
                    status = mapping.get("matchStatus", "unknown")
                    confidence = mapping.get("confidence", 0)
                    reason = mapping.get("reason", "No reason")
                    print(f"      {j}. {mapping['sourceColumn']} → {mapping['targetColumn']} ({status}, {confidence:.1%})")
                    print(f"         Reason: {reason}")
                
                # Check for expected matches
                if test_case["expected_matches"]:
                    found_expected = []
                    for expected in test_case["expected_matches"]:
                        for mapping in mappings:
                            if expected in mapping.get("targetColumn", ""):
                                found_expected.append(expected)
                                break
                    
                    if found_expected:
                        print(f"   ✅ Found expected matches: {found_expected}")
                    else:
                        print(f"   ⚠️  Missing expected matches: {test_case['expected_matches']}")
                
                # Show suggestions
                if suggestions:
                    print(f"   💡 AI Suggestions:")
                    for suggestion in suggestions:
                        print(f"      • {suggestion.get('message', 'No message')}")
                    
            else:
                print(f"   ❌ API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")

def test_table_suggestions_with_mappings():
    """Test table suggestions that trigger mapping generation"""
    print("\n🧪 Testing Table Suggestions with Auto-Mapping...")
    
    test_cases = [
        {
            "name": "ONSPD Data",
            "headers": ["pcd", "pcd2", "pcds", "x_coord", "y_coord"],
            "file_name": "onspd_2024.csv"
        },
        {
            "name": "UPRN Data",
            "headers": ["uprn", "x_coordinate", "y_coordinate"],
            "file_name": "uprn_data.csv"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        
        try:
            # First get table suggestions
            suggestion_response = requests.post(
                f"{API_BASE}/suggest-table-name",
                json={
                    "headers": test_case["headers"],
                    "file_name": test_case["file_name"],
                    "content_preview": "Sample content"
                },
                timeout=10
            )
            
            if suggestion_response.status_code == 200:
                suggestion_data = suggestion_response.json()
                suggestions = suggestion_data.get("suggestions", [])
                
                if suggestions:
                    # Use the top suggestion to generate mappings
                    top_suggestion = suggestions[0]
                    print(f"   🎯 Top suggestion: {top_suggestion['name']} ({top_suggestion['confidence']:.1%})")
                    
                    # Generate mappings for the suggested table
                    mapping_response = requests.post(
                        f"{API_BASE}/generate-mappings",
                        json={
                            "headers": test_case["headers"],
                            "staging_table_name": top_suggestion["name"],
                            "file_name": test_case["file_name"],
                            "content_preview": "Sample content"
                        },
                        timeout=10
                    )
                    
                    if mapping_response.status_code == 200:
                        mapping_data = mapping_response.json()
                        mappings = mapping_data.get("mappings", [])
                        match_status = mapping_data.get("match_status", {})
                        
                        print(f"   ✅ Generated {len(mappings)} mappings")
                        print(f"   🎯 Match status: {match_status.get('status', 'unknown')} ({match_status.get('confidence', 0):.1%})")
                        
                        # Show mapping summary
                        exact_count = sum(1 for m in mappings if m.get("matchStatus") == "exact")
                        print(f"   📊 Exact matches: {exact_count}/{len(mappings)}")
                        
                    else:
                        print(f"   ❌ Mapping generation failed: {mapping_response.status_code}")
                else:
                    print(f"   ⚠️  No table suggestions found")
            else:
                print(f"   ❌ Suggestion API failed: {suggestion_response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")

def main():
    """Main test function"""
    print("🚀 Enhanced AI Column Mapping Test Suite")
    print("=" * 60)
    
    # Test AI column mapping generation
    test_ai_column_mappings()
    
    # Test table suggestions with auto-mapping
    test_table_suggestions_with_mappings()
    
    print("\n" + "=" * 60)
    print("✅ Enhanced mapping test suite completed!")
    print("\n💡 Key Features Tested:")
    print("   • AI-powered column mapping generation")
    print("   • Color-coded match statuses (exact, partial, semantic, suggested)")
    print("   • Automatic mapping when table is selected")
    print("   • Confidence scoring and suggestions")
    print("   • Support for new/non-existent tables")

if __name__ == "__main__":
    main() 