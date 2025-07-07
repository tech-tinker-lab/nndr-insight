import sqlalchemy
from sqlalchemy import text

# Connect to DB
engine = sqlalchemy.create_engine(
    "postgresql://nndr:nndrpass@localhost:5432/nndr_db"
)

# 1. Extract unique category codes and descriptions from the properties table
with engine.begin() as conn:
    result = conn.execute(text("""
        SELECT DISTINCT category_code, description
        FROM properties
        WHERE category_code IS NOT NULL AND description IS NOT NULL
    """))
    category_map = {row.category_code.strip(): row.description.strip() for row in result if row.category_code and row.description}

    # 2. Insert or update categories in the categories table
    for code, desc in category_map.items():
        conn.execute(text("""
            INSERT INTO categories (code, description)
            VALUES (:code, :desc)
            ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description
        """), {"code": code, "desc": desc})
    print(f"Inserted/updated {len(category_map)} categories from properties table.")

# 3. (Optional) Update properties with category descriptions via join (if needed for denormalized reporting)
# Uncomment below if you want to denormalize:
# with engine.begin() as conn:
#     conn.execute(text("""
#         UPDATE properties p
#         SET description = c.description
#         FROM categories c
#         WHERE p.category_code = c.code
#     """))
#     print("Properties table updated with category descriptions.")
