import sqlalchemy
from sqlalchemy import text

engine = sqlalchemy.create_engine(
    "postgresql://nndr:nndrpass@localhost:5432/nndr_db"
)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT COUNT(*) AS null_latlong_count
        FROM properties
        WHERE latitude IS NULL OR longitude IS NULL
    """))
    count = result.scalar()
    print(f"Properties with NULL latitude or longitude: {count}")
