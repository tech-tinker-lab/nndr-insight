#!/usr/bin/env python3
"""
Quick script to examine the structure of the NNDR CSV file
"""

import csv
import os

def examine_csv_structure(file_path):
    """Examine the structure of a CSV file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            print(f"File: {file_path}")
            print(f"File size: {os.path.getsize(file_path):,} bytes")
            print(f"Number of columns: {len(header)}")
            print("\nColumns:")
            for i, col in enumerate(header):
                print(f"  {i+1:2d}. {col}")
            
            # Read first few data rows
            print("\nFirst 3 data rows:")
            for i, row in enumerate(reader):
                if i >= 3:
                    break
                print(f"  Row {i+1}: {row[:5]}...")  # Show first 5 columns
                
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    csv_file = "data/uk-englandwales-ndr-2010-summaryvaluations-compiled-epoch-0052-baseline-csv/uk-englandwales-ndr-2010-summaryvaluations-compiled-epoch-0052-baseline-csv.csv"
    
    if os.path.exists(csv_file):
        examine_csv_structure(csv_file)
    else:
        print(f"File not found: {csv_file}")
        print("Available files in data directory:")
        for root, dirs, files in os.walk("data"):
            for file in files:
                if file.endswith('.csv'):
                    print(f"  {os.path.join(root, file)}") 