import os
import sqlalchemy
from sqlalchemy import text

# Database connection info from environment variables (with defaults)
USER = os.getenv("PGUSER", "nndr")
PASSWORD = os.getenv("PGPASSWORD", "nndrpass")
HOST = os.getenv("PGHOST", "localhost")
PORT = os.getenv("PGPORT", "5432")
DBNAME = os.getenv("PGDATABASE", "nndr_db")

def get_engine():
    return sqlalchemy.create_engine(
        f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
    )

def batch_insert(conn, insert_stmt, rows, batch_size=1000):
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        conn.execute(insert_stmt, batch) 