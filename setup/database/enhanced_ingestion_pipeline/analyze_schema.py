#!/usr/bin/env python3
"""
Comprehensive Schema Analysis Script
Analyzes all reference data tables and their current structure
"""

import psycopg2
import pandas as pd
import logging
from db_config import get_connection_string

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_database_schema():
    """Analyze all reference data tables"""
    
    reference_tables = [
        'os_open_uprn',
        'code_point_open', 
        'onspd',
        'os_open_names',
        'lad_boundaries',
        'os_open_map_local',
        'os_open_usrn'
    ]
    
    try:
        conn = psycopg2.connect(get_connection_string())
        cur = conn.cursor()
        
        print("=" * 80)
        print("COMPREHENSIVE DATABASE SCHEMA ANALYSIS")
        print("=" * 80)
        
        for table in reference_tables:
            print(f"\n📋 {table.upper()}:")
            print("-" * 50)
            
            # Check if table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (table,))
            
            if not cur.fetchone()[0]:
                print(f"  ❌ Table '{table}' does not exist")
                continue
            
            # Get table schema
            cur.execute("""
                SELECT column_name, data_type, character_maximum_length, 
                       is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position;
            """, (table,))
            
            columns = cur.fetchall()
            print(f"  📊 Columns ({len(columns)}):")
            
            for col in columns:
                col_name, data_type, max_length, nullable, default = col
                length_info = f"({max_length})" if max_length else ""
                nullable_info = "NULL" if nullable == "YES" else "NOT NULL"
                default_info = f" DEFAULT {default}" if default else ""
                print(f"    • {col_name}: {data_type}{length_info} {nullable_info}{default_info}")
            
            # Get row count
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            row_count = cur.fetchone()[0]
            print(f"  📈 Row count: {row_count:,}")
            
            # Get sample data
            if row_count > 0:
                cur.execute(f"SELECT * FROM {table} LIMIT 3;")
                sample_rows = cur.fetchall()
                print(f"  🔍 Sample data:")
                for i, row in enumerate(sample_rows, 1):
                    print(f"    Row {i}: {row}")
            
            print()
        
        conn.close()
        print("=" * 80)
        print("SCHEMA ANALYSIS COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Schema analysis failed: {e}")
        raise

def analyze_data_files():
    """Analyze the actual data files to understand their format"""
    
    print("\n" + "=" * 80)
    print("DATA FILE ANALYSIS")
    print("=" * 80)
    
    # CodePoint data analysis
    try:
        print("\n📁 CodePoint Data Analysis:")
        codepoint_file = "../../../backend/data/codepo_gb/Data/CSV/ab.csv"
        df = pd.read_csv(codepoint_file, header=None, nrows=5)
        print(f"  Columns: {len(df.columns)}")
        print(f"  Sample data:")
        print(df.head())
        
        # Check postcode lengths
        postcode_lengths = df[0].str.len()
        print(f"  Postcode length range: {postcode_lengths.min()} - {postcode_lengths.max()}")
        print(f"  Max postcode: {df[0].str.len().max()} characters")
        
    except Exception as e:
        print(f"  ❌ Error analyzing CodePoint data: {e}")
    
    # ONSPD data analysis
    try:
        print("\n📁 ONSPD Data Analysis:")
        onspd_file = "../../../backend/data/ONSPD_Online_Latest_Centroids.csv"
        df = pd.read_csv(onspd_file, nrows=5)
        print(f"  Columns: {len(df.columns)}")
        print(f"  Column names: {list(df.columns)}")
        print(f"  Sample data:")
        print(df.head())
        
    except Exception as e:
        print(f"  ❌ Error analyzing ONSPD data: {e}")
    
    # OS Open Names analysis
    try:
        print("\n📁 OS Open Names Analysis:")
        names_file = "../../../backend/data/opname_csv_gb/Data/HP40.csv"
        df = pd.read_csv(names_file, nrows=5)
        print(f"  Columns: {len(df.columns)}")
        print(f"  Column names: {list(df.columns)}")
        print(f"  Sample data:")
        print(df.head())
        
    except Exception as e:
        print(f"  ❌ Error analyzing OS Open Names data: {e}")

if __name__ == "__main__":
    analyze_database_schema()
    analyze_data_files() 