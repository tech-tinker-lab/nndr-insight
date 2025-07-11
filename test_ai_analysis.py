#!/usr/bin/env python3
"""
Simple test script for AI analysis functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.ai_analysis_service import GovernmentDataAnalyzer

def test_ai_analysis():
    """Test the AI analysis functionality"""
    
    # Initialize the analyzer
    analyzer = GovernmentDataAnalyzer()
    
    # Test CSV content
    csv_content = """uprn,postcode,address,rateable_value
123456789012,SW1A 1AA,10 Downing Street,50000
123456789013,SW1A 2AA,11 Downing Street,55000
123456789014,SW1A 3AA,12 Downing Street,60000"""
    
    print("Testing AI analysis with CSV content...")
    
    try:
        # Perform analysis
        analysis = analyzer.analyze_dataset(
            file_content=csv_content,
            file_type='csv',
            file_name='test_business_rates.csv'
        )
        
        print("✅ AI analysis completed successfully!")
        print(f"Confidence score: {analysis.get('confidence_score', 0):.2f}")
        
        # Check for detected standards
        standards = analysis.get('standards_compliance', {}).get('detected_standards', [])
        if standards:
            print(f"Detected standards: {[s['name'] for s in standards]}")
        else:
            print("No standards detected")
        
        # Check for mapping suggestions
        mappings = analysis.get('mapping_suggestions', {}).get('column_mappings', [])
        if mappings:
            print(f"Suggested mappings: {len(mappings)} columns")
            for mapping in mappings[:3]:  # Show first 3
                print(f"  {mapping['source_column']} → {mapping['target_column']} ({mapping['data_type']})")
        
        return True
        
    except Exception as e:
        print(f"❌ AI analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ai_analysis()
    sys.exit(0 if success else 1) 