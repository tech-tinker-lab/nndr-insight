import psycopg2
from dotenv import load_dotenv
import os

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

def test_connection():
    print("Testing database connection...")
    try:
        with psycopg2.connect(
            dbname=DBNAME,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        ) as conn:
            with conn.cursor() as cur:
                # Test basic query
                cur.execute("SELECT version();")
                version = cur.fetchone()
                print(f"✅ Database connected: {version[0][:50]}...")
                
                # Create simple test table
                cur.execute("DROP TABLE IF EXISTS test_os_names;")
                cur.execute("""
                    CREATE TABLE test_os_names (
                        id SERIAL PRIMARY KEY,
                        name TEXT,
                        type TEXT,
                        country TEXT
                    );
                """)
                
                # Insert test data
                cur.execute("""
                    INSERT INTO test_os_names (name, type, country) VALUES 
                    ('London', 'City', 'England'),
                    ('Edinburgh', 'City', 'Scotland'),
                    ('Cardiff', 'City', 'Wales')
                """)
                
                conn.commit()
                
                # Check data
                cur.execute("SELECT COUNT(*) FROM test_os_names")
                count = cur.fetchone()[0]
                print(f"✅ Test table created with {count} rows")
                
                return True
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection() 