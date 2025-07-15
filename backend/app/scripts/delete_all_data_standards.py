import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models.registry.standards import DataStandard
from app.models.base import Base
from app.db.db_config import get_connection_string


def main():
    engine = create_engine(get_connection_string())
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        count = session.query(DataStandard).count()
        session.query(DataStandard).delete()
        session.commit()
        print(f"Deleted {count} records from design_enhanced.data_standards.")
    except Exception as e:
        session.rollback()
        print(f"Error deleting records: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    main() 