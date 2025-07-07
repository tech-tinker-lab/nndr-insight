import sqlalchemy
from sqlalchemy import text

# Connect to DB
engine = sqlalchemy.create_engine(
    "postgresql://nndr:nndrpass@localhost:5432/nndr_db"
)

# This script updates properties.latitude and longitude from the onspd table using normalized postcode join
with engine.begin() as conn:  # <-- ensures commit!
    result = conn.execute(text("""
        UPDATE properties p
        SET latitude = o.lat,
            longitude = o.long
        FROM onspd o
        WHERE
            (p.latitude IS NULL OR p.longitude IS NULL)
            AND p.postcode IS NOT NULL
            AND REPLACE(UPPER(p.postcode), ' ', '') = REPLACE(UPPER(o.pcds), ' ', '')
            AND o.lat IS NOT NULL
            AND o.long IS NOT NULL
        RETURNING p.id
    """))
    updated_count = len(result.fetchall())
    print(f"Properties table updated with latitude/longitude from ONSPD. Rows updated: {updated_count}")
