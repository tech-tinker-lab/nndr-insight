#!/usr/bin/env python3
"""
Debug script to see what data the pipeline is generating
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from comprehensive_ingestion_pipeline import ComprehensiveIngestionPipeline
import pandas as pd

def debug_pipeline():
    """Debug the pipeline to see what data is being generated"""
    pipeline = ComprehensiveIngestionPipeline()
    
    # Test with sample NNDR data first
    sample_file = os.path.join(pipeline.data_directory, 'sample_nndr.csv')
    
    if os.path.exists(sample_file):
        print(f"Testing with sample file: {sample_file}")
        
        try:
            # Process the sample file
            for chunk in pipeline.process_local_council_data(sample_file):
                print(f"\n=== CHUNK DATA ===")
                print(f"Shape: {chunk.shape}")
                print(f"Columns: {chunk.columns.tolist()}")
                print(f"First few rows:")
                print(chunk.head(3).to_string())
                
                # Check for any problematic data
                print(f"\n=== DATA TYPES ===")
                print(chunk.dtypes)
                
                print(f"\n=== NULL VALUES ===")
                print(chunk.isnull().sum())
                
                # Try to detect duplicates
                print(f"\n=== DUPLICATE DETECTION ===")
                chunk_with_duplicates = pipeline.detect_duplicates(chunk)
                print(f"Duplicate groups found: {chunk_with_duplicates['duplicate_group_id'].notna().sum()}")
                
                # Try a small insert
                print(f"\n=== TESTING SMALL INSERT ===")
                try:
                    pipeline.bulk_insert_data(chunk.head(1), 'master_gazetteer')
                    print("✅ Small insert successful!")
                except Exception as e:
                    print(f"❌ Small insert failed: {e}")
                
                break  # Just test the first chunk
                
        except Exception as e:
            print(f"Error processing sample file: {e}")
    else:
        print(f"Sample file not found: {sample_file}")

if __name__ == "__main__":
    debug_pipeline() 