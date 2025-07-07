import sqlalchemy
from sqlalchemy import text

engine = sqlalchemy.create_engine(
    "postgresql://nndr:nndrpass@localhost:5432/nndr_db"
)

with engine.connect() as conn:
    # Count properties with null lat/long and non-null postcode
    result = conn.execute(text("""
        SELECT COUNT(*) FROM properties
        WHERE (latitude IS NULL OR longitude IS NULL)
          AND postcode IS NOT NULL
    """))
    count = result.scalar()
    print(f"Properties with NULL latitude or longitude and a postcode: {count}")

    # Show a sample of such records for debugging
    sample = conn.execute(text("""
        SELECT id, property_ref, postcode FROM properties
        WHERE (latitude IS NULL OR longitude IS NULL)
          AND postcode IS NOT NULL
        LIMIT 10
    """))
    print("Sample properties with missing lat/long:")
    for row in sample:
        print(dict(row._mapping))
