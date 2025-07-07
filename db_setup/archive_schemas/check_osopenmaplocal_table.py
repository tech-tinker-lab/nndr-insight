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

def check_table():
    try:
        with psycopg2.connect(
            dbname=DBNAME,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        ) as conn:
            with conn.cursor() as cur:
                # Check if table exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'os_open_map_local'
                    );
                """)
                table_exists = cur.fetchone()[0]
                
                if not table_exists:
                    print("❌ Table 'os_open_map_local' does not exist!")
                    return
                
                # Get table structure
                cur.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'os_open_map_local' 
                    ORDER BY ordinal_position
                """)
                columns = cur.fetchall()
                
                print("📊 OS Open Map Local Table Structure:")
                print("-" * 50)
                for col in columns:
                    print(f"  {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
                
                # Get row count
                cur.execute("SELECT COUNT(*) FROM os_open_map_local")
                row_count = cur.fetchone()[0]
                print(f"\n📈 Total rows: {row_count}")
                
                # Get sample data
                cur.execute("SELECT * FROM os_open_map_local LIMIT 3")
                rows = cur.fetchall()
                
                print(f"\n📋 Sample Data (first 3 rows):")
                print("-" * 50)
                for i, row in enumerate(rows):
                    print(f"Row {i+1}:")
                    for j, value in enumerate(row):
                        col_name = columns[j][0] if j < len(columns) else f"col_{j}"
                        print(f"  {col_name}: {value}")
                    print()
                
                # Check for non-null values in each column
                print("🔍 Non-null value counts:")
                print("-" * 50)
                for col in columns:
                    col_name = col[0]
                    cur.execute(f"SELECT COUNT(*) FROM os_open_map_local WHERE {col_name} IS NOT NULL")
                    non_null_count = cur.fetchone()[0]
                    print(f"  {col_name}: {non_null_count}/{row_count} ({non_null_count/row_count*100:.1f}%)")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_table() 