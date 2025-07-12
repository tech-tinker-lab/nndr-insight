import os
import sys
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

"""
create_design_schema.py: Create the design_enhanced schema for the Design System Enhanced feature
"""

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), 'schemas', 'design')

def main():
    print("Creating design_enhanced schema...")
    
    # Check if the schema file exists
    schema_file = os.path.join(SCHEMA_DIR, '03_create_enhanced_design_system.sql')
    if not os.path.exists(schema_file):
        print(f"Schema file not found: {schema_file}")
        return
    
    # Create database connection
    engine = sqlalchemy.create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}")
    
    with engine.begin() as conn:
        print(f"Executing {schema_file}...")
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                sql = f.read()
            conn.execute(text(sql))
            print("Design enhanced schema created successfully!")
        except Exception as e:
            print(f"Error creating design enhanced schema: {e}")
            raise

if __name__ == "__main__":
    main() 