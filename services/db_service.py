import sqlalchemy
from sqlalchemy import text
from backend.db.db_config import get_connection_string

def get_engine():
    return sqlalchemy.create_engine(get_connection_string())

def batch_insert(conn, insert_stmt, rows, batch_size=1000):
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        conn.execute(insert_stmt, batch) 