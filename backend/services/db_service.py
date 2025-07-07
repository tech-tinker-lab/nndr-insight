import sqlalchemy
from sqlalchemy import text
from setup.database.db_config import get_connection_string

def get_engine(user=None, password=None, host=None, port=None, dbname=None):
    """Get database engine. If no parameters provided, uses environment variables."""
    if all([user, password, host, port, dbname]):
        return sqlalchemy.create_engine(
            f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        )
    else:
        return sqlalchemy.create_engine(get_connection_string(dbname))

def batch_insert(conn, insert_stmt, rows, batch_size=1000):
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        conn.execute(insert_stmt, batch) 