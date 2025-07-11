#!/usr/bin/env python3
"""
Comprehensive AI Functionality Test Script
Tests all AI analysis features for government data processing
"""

import sys
import os
import json
import traceback
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_dependencies():
    """Test that all required AI dependencies are available"""
    print("🔍 Testing AI Dependencies...")
    
    # Core packages (required for basic functionality)
    core_packages = [
        'pandas', 'numpy', 'scikit-learn', 'scipy'
    ]
    
    # AI packages (required for advanced features)
    ai_packages = [
        'nltk', 'spacy', 'great_expectations', 'pandera',
        'statsmodels', 'feature_engine', 'joblib'
    ]
    
    # Visualization packages (optional but recommended)
    viz_packages = [
        'matplotlib', 'plotly', 'seaborn'
    ]
    
    # Utility packages (optional)
    util_packages = [
        'lxml', 'xmltodict', 'regex', 'pyyaml',
        'numba', 'psutil', 'diskcache', 'zstandard'
    ]
    
    all_packages = core_packages + ai_packages + viz_packages + util_packages
    missing_core = []
    missing_ai = []
    missing_viz = []
    missing_util = []
    
    for package in all_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            if package in core_packages:
                missing_core.append(package)
            elif package in ai_packages:
                missing_ai.append(package)
            elif package in viz_packages:
                missing_viz.append(package)
            elif package in util_packages:
                missing_util.append(package)
    
    # Report missing packages by category
    if missing_core:
        print(f"\n❌ Missing CORE packages: {', '.join(missing_core)}")
        print("These are required for basic functionality!")
        return False
    
    if missing_ai:
        print(f"\n⚠️  Missing AI packages: {', '.join(missing_ai)}")
        print("These are required for advanced AI features!")
    
    if missing_viz:
        print(f"\nℹ️  Missing visualization packages: {', '.join(missing_viz)}")
        print("These are optional but recommended for better analysis!")
    
    if missing_util:
        print(f"\nℹ️  Missing utility packages: {', '.join(missing_util)}")
        print("These are optional for enhanced functionality!")
    
    if not missing_core:
        print("\n✅ Core dependencies are available!")
        if not missing_ai:
            print("✅ All AI dependencies are available!")
        return True
    
    return False

def test_ai_analysis_service():
    """Test the AI analysis service"""
    print("\n🤖 Testing AI Analysis Service...")
    
    try:
        from backend.app.services.ai_analysis_service import GovernmentDataAnalyzer
        
        # Initialize analyzer
        analyzer = GovernmentDataAnalyzer()
        print("  ✅ AI Analyzer initialized successfully")
        
        # Test CSV content
        csv_content = """uprn,postcode,address,rateable_value,business_type
123456789012,SW1A 1AA,10 Downing Street,50000,Office
123456789013,SW1A 2AA,11 Downing Street,55000,Retail
123456789014,SW1A 3AA,12 Downing Street,60000,Industrial"""
        
        print("  📊 Testing CSV analysis...")
        analysis = analyzer.analyze_dataset(
            file_content=csv_content,
            file_type='csv',
            file_name='test_business_rates.csv'
        )
        
        print(f"  ✅ Analysis completed with confidence: {analysis.get('confidence_score', 0):.2f}")
        
        # Check for detected standards
        standards = analysis.get('standards_compliance', {}).get('detected_standards', [])
        if standards:
            print(f"  🏛️  Detected standards: {[s['name'] for s in standards]}")
        
        # Check for mapping suggestions
        mappings = analysis.get('mapping_suggestions', {}).get('column_mappings', [])
        if mappings:
            print(f"  🗺️  Generated {len(mappings)} mapping suggestions")
        
        return True
        
    except Exception as e:
        print(f"  ❌ AI analysis service test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_ai_api_endpoints():
    """Test AI API endpoints"""
    print("\n🌐 Testing AI API Endpoints...")
    
    try:
        import requests
        
        # Test if backend is running
        try:
            response = requests.get('http://localhost:8000/', timeout=5)
            if response.status_code == 200:
                print("  ✅ Backend server is running")
            else:
                print("  ⚠️  Backend server responded with unexpected status")
                return False
        except requests.exceptions.RequestException:
            print("  ❌ Backend server is not running")
            print("  💡 Start the backend with: cd backend && uvicorn app.main:app --reload")
            return False
        
        # Test AI analysis endpoint
        test_data = {
            "content": "uprn,postcode,address\n123456789012,SW1A 1AA,10 Downing Street"
        }
        
        try:
            response = requests.post(
                'http://localhost:8000/api/ai/detect-types',
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print("  ✅ AI detect-types endpoint working")
                print(f"  📊 Detected {len(result.get('field_types', []))} field types")
            else:
                print(f"  ❌ AI endpoint failed with status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ AI endpoint request failed: {str(e)}")
            return False
        
        return True
        
    except ImportError:
        print("  ⚠️  requests library not available, skipping API tests")
        return True
    except Exception as e:
        print(f"  ❌ API endpoint test failed: {str(e)}")
        return False

def test_frontend_ai_integration():
    """Test frontend AI integration"""
    print("\n🎨 Testing Frontend AI Integration...")
    
    try:
        # Check if frontend AI service exists
        ai_service_path = 'frontend/src/services/aiDataAnalyzer.js'
        if os.path.exists(ai_service_path):
            print("  ✅ Frontend AI service file exists")
            
            # Check if it has required methods
            with open(ai_service_path, 'r') as f:
                content = f.read()
                
            required_methods = [
                'analyzeDataset',
                'analyzeContent', 
                'detectSchema',
                'identifyStandards',
                'generateMappingSuggestions'
            ]
            
            missing_methods = []
            for method in required_methods:
                if method not in content:
                    missing_methods.append(method)
            
            if missing_methods:
                print(f"  ❌ Missing methods: {', '.join(missing_methods)}")
                return False
            else:
                print("  ✅ All required AI methods present")
                
        else:
            print("  ❌ Frontend AI service file not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Frontend AI integration test failed: {str(e)}")
        return False

def test_government_data_patterns():
    """Test government data pattern detection"""
    print("\n🏛️  Testing Government Data Pattern Detection...")
    
    try:
        from backend.app.services.ai_analysis_service import GovernmentDataAnalyzer
        
        analyzer = GovernmentDataAnalyzer()
        
        # Test BS7666 patterns
        bs7666_content = """uprn,usrn,address,postcode
123456789012,12345678,10 Downing Street,SW1A 1AA
123456789013,12345679,11 Downing Street,SW1A 2AA"""
        
        analysis = analyzer.analyze_dataset(
            file_content=bs7666_content,
            file_type='csv',
            file_name='test_bs7666.csv'
        )
        
        standards = analysis.get('standards_compliance', {}).get('detected_standards', [])
        bs7666_found = any(s['name'] == 'BS7666' for s in standards)
        
        if bs7666_found:
            print("  ✅ BS7666 address standard detected")
        else:
            print("  ⚠️  BS7666 address standard not detected")
        
        # Test business rates patterns
        business_content = """rateable_value,business_type,valuation_date
50000,Office,2023-01-01
55000,Retail,2023-01-01"""
        
        analysis = analyzer.analyze_dataset(
            file_content=business_content,
            file_type='csv',
            file_name='test_business_rates.csv'
        )
        
        patterns = analysis.get('content_analysis', {}).get('data_patterns', [])
        business_patterns = [p for p in patterns if 'rateable' in p.get('header', '').lower()]
        
        if business_patterns:
            print("  ✅ Business rates patterns detected")
        else:
            print("  ⚠️  Business rates patterns not detected")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Government data pattern test failed: {str(e)}")
        return False

def main():
    """Run all AI functionality tests"""
    print("🚀 NNDR Insight AI Functionality Test Suite")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Dependencies", test_dependencies),
        ("AI Analysis Service", test_ai_analysis_service),
        ("AI API Endpoints", test_ai_api_endpoints),
        ("Frontend AI Integration", test_frontend_ai_integration),
        ("Government Data Patterns", test_government_data_patterns)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All AI functionality tests passed! The system is ready for government data processing.")
    else:
        print("⚠️  Some tests failed. Please check the errors above and fix any issues.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 