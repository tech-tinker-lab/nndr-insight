import sqlalchemy
from sqlalchemy import text
import csv

engine = sqlalchemy.create_engine(
    "postgresql://nndr:nndrpass@localhost:5432/nndr_db"
)

summary = []

def export_to_csv(rows, headers, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

# 1. Properties with no valuations
with engine.connect() as conn:
    rows = list(conn.execute(text("""
        SELECT p.id, p.property_ref, p.address
        FROM properties p
        LEFT JOIN valuations v ON p.id = v.property_id
        WHERE v.id IS NULL;
    """)))
    export_to_csv(rows, ['id', 'property_ref', 'address'], 'properties_no_valuations.csv')
    print(f"Properties with no valuations: {len(rows)} (see properties_no_valuations.csv)")
    summary.append(("Properties with no valuations", len(rows), 'properties_no_valuations.csv'))

# 2. Properties with no ratepayers
with engine.connect() as conn:
    rows = list(conn.execute(text("""
        SELECT p.id, p.property_ref, p.address
        FROM properties p
        LEFT JOIN ratepayers r ON p.id = r.property_id
        WHERE r.id IS NULL;
    """)))
    export_to_csv(rows, ['id', 'property_ref', 'address'], 'properties_no_ratepayers.csv')
    print(f"Properties with no ratepayers: {len(rows)} (see properties_no_ratepayers.csv)")
    summary.append(("Properties with no ratepayers", len(rows), 'properties_no_ratepayers.csv'))

# 3. Valuations with no matching property
with engine.connect() as conn:
    rows = list(conn.execute(text("""
        SELECT v.id, v.property_id, v.effective_date, v.rateable_value
        FROM valuations v
        LEFT JOIN properties p ON v.property_id = p.id
        WHERE p.id IS NULL;
    """)))
    export_to_csv(rows, ['id', 'property_id', 'effective_date', 'rateable_value'], 'valuations_no_property.csv')
    print(f"Valuations with no matching property: {len(rows)} (see valuations_no_property.csv)")
    summary.append(("Valuations with no matching property", len(rows), 'valuations_no_property.csv'))

# 4. Ratepayers with no matching property
with engine.connect() as conn:
    rows = list(conn.execute(text("""
        SELECT r.id, r.property_id, r.name
        FROM ratepayers r
        LEFT JOIN properties p ON r.property_id = p.id
        WHERE p.id IS NULL;
    """)))
    export_to_csv(rows, ['id', 'property_id', 'name'], 'ratepayers_no_property.csv')
    print(f"Ratepayers with no matching property: {len(rows)} (see ratepayers_no_property.csv)")
    summary.append(("Ratepayers with no matching property", len(rows), 'ratepayers_no_property.csv'))

# Print summary
def print_summary():
    print("\n==== Data Quality Summary ====")
    for label, count, filename in summary:
        print(f"{label}: {count} (see {filename})")

print_summary()
