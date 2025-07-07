import csv
import os
from dotenv import load_dotenv

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'data', 'opname_csv_gb', 'Data')

# Official OS Open Names columns from OS_Open_Names_Header.csv
OS_OPEN_NAMES_COLUMNS = [
    'ID', 'NAMES_URI', 'NAME1', 'NAME1_LANG', 'NAME2', 'NAME2_LANG', 'TYPE', 'LOCAL_TYPE',
    'GEOMETRY_X', 'GEOMETRY_Y', 'MOST_DETAIL_VIEW_RES', 'LEAST_DETAIL_VIEW_RES',
    'MBR_XMIN', 'MBR_YMIN', 'MBR_XMAX', 'MBR_YMAX', 'POSTCODE_DISTRICT', 'POSTCODE_DISTRICT_URI',
    'POPULATED_PLACE', 'POPULATED_PLACE_URI', 'POPULATED_PLACE_TYPE', 'DISTRICT_BOROUGH',
    'DISTRICT_BOROUGH_URI', 'DISTRICT_BOROUGH_TYPE', 'COUNTY_UNITARY', 'COUNTY_UNITARY_URI',
    'COUNTY_UNITARY_TYPE', 'REGION', 'REGION_URI', 'COUNTRY', 'COUNTRY_URI',
    'RELATED_SPATIAL_OBJECT', 'SAME_AS_DBPEDIA', 'SAME_AS_GEONAMES'
]

def examine_csv_files():
    """Examine the first few rows of CSV files to understand the data structure"""
    csv_files = []
    if os.path.exists(DATA_DIR):
        for file in os.listdir(DATA_DIR):
            if file.endswith('.csv'):
                csv_files.append(os.path.join(DATA_DIR, file))
    
    csv_files = sorted(csv_files)
    print(f"Found {len(csv_files)} CSV files")
    
    # Examine first 5 files
    for i, file_path in enumerate(csv_files[:5]):
        print(f"\n=== File {i+1}: {os.path.basename(file_path)} ===")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                # Read first 3 rows
                for row_num, row in enumerate(reader):
                    if row_num >= 3:
                        break
                    print(f"Row {row_num + 1}: {len(row)} columns")
                    print(f"  Data: {row[:5]}...")  # Show first 5 values
                    
                    # Check if row matches expected column count
                    if len(row) != len(OS_OPEN_NAMES_COLUMNS):
                        print(f"  WARNING: Expected {len(OS_OPEN_NAMES_COLUMNS)} columns, got {len(row)}")
                    
                    # Check data types for numeric columns
                    if row_num == 0:  # First row
                        for j, col_name in enumerate(OS_OPEN_NAMES_COLUMNS):
                            if j < len(row):
                                value = row[j]
                                if col_name in ['GEOMETRY_X', 'GEOMETRY_Y', 'MBR_XMIN', 'MBR_YMIN', 'MBR_XMAX', 'MBR_YMAX']:
                                    try:
                                        float(value) if value else None
                                        print(f"    {col_name}: {value} (numeric OK)")
                                    except ValueError:
                                        print(f"    {col_name}: {value} (NOT numeric!)")
                                elif col_name in ['MOST_DETAIL_VIEW_RES', 'LEAST_DETAIL_VIEW_RES']:
                                    try:
                                        int(value) if value else None
                                        print(f"    {col_name}: {value} (integer OK)")
                                    except ValueError:
                                        print(f"    {col_name}: {value} (NOT integer!)")
                                else:
                                    print(f"    {col_name}: {value} (text)")
        except Exception as e:
            print(f"Error reading file: {e}")

if __name__ == "__main__":
    examine_csv_files() 