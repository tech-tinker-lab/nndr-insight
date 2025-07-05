import os
import sys
import logging
import psycopg2
from psycopg2 import sql
from db_config import get_connection_string

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('run_enhanced_schema_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

SQL_FILE = os.path.join(os.path.dirname(__file__), 'enhanced_schema_update.sql')

def run_schema_update():
    conn_str = get_connection_string()
    try:
        with psycopg2.connect(conn_str) as conn:
            with conn.cursor() as cur:
                logger.info(f"Reading SQL file: {SQL_FILE}")
                with open(SQL_FILE, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                logger.info("Executing schema update SQL...")
                cur.execute(sql.SQL(sql_content))
                conn.commit()
                logger.info("Schema update completed successfully.")
    except Exception as e:
        logger.error(f"Schema update failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_schema_update() 