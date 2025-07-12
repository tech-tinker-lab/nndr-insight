import os
import sys
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv('db_setup/.env')

USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

def main():
    print("Running staging schema creation...")
    
    # Check environment variables
    if not all([USER, PASSWORD, HOST, PORT, DBNAME]):
        print("Error: Missing database environment variables. Please check db_setup/.env file.")
        return
    
    # SQL file path
    sql_file = "db_setup/schemas/create_staging_schema.sql"
    
    if not os.path.exists(sql_file):
        print(f"Error: SQL file not found: {sql_file}")
        return
    
    # Create database connection
    engine = sqlalchemy.create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}")
    
    try:
        with engine.begin() as conn:
            print(f"=== Executing {sql_file} ===")
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql = f.read()
            conn.execute(text(sql))
            print(f"Executed {sql_file} successfully.")
            print("Staging schema created successfully!")
            
    except Exception as e:
        print(f"[ERROR] Failed to execute {sql_file}: {e}")
        return

if __name__ == "__main__":
    main() 