import csv
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from datetime import datetime

engine = sqlalchemy.create_engine(
    "postgresql://nndr:nndrpass@localhost:5432/nndr_db"
)
Session = sessionmaker(bind=engine)
session = Session()

def parse_date(date_str):
    if not date_str or not date_str.strip():
        return None
    for fmt in ("%d-%b-%y", "%d/%m/%Y", "%Y-%m-%d", "%d-%b-%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except Exception:
            continue
    return None

def parse_numeric(val):
    if val is None:
        return None
    val = str(val).strip()
    if val == '':
        return None
    try:
        return float(val)
    except Exception:
        return None

def ingest_historic_valuations(csv_path, source_label):
    # Preload ba_reference to id mapping
    prop_map = {}
    for row in session.execute(text("SELECT ba_reference, id FROM properties")):
        prop_map[row.ba_reference.strip()] = row.id

    voa_hist_columns = [
        "billing_auth_code",     # 0
        "empty1",                # 1
        "ba_reference",          # 2
        "scat_code",             # 3
        "description",           # 4
        "herid",                 # 5
        "effective_date",        # 6
        "empty2",                # 7
        "rateable_value",        # 8
        "uprn",                  # 9
        "change_date",           # 10
        "list_code",             # 11
        "property_link_number",  # 12
        "entry_date",            # 13
        "removal_date"           # 14
    ]

    batch = []
    batch_size = 1000
    inserted = 0
    skipped = 0
    malformed = 0
    row_count = 0

    with open(csv_path, newline='', encoding='utf-8') as f:
        for line in f:
            # Split line by ':' to get individual records (if present)
            records = [rec.strip() for rec in line.strip().split(':') if rec.strip()]
            for rec in records:
                row_count += 1
                fields = rec.split('*')
                if len(fields) < 15:
                    malformed += 1
                    if malformed <= 5:
                        print(f"Malformed record at line {row_count}: {fields}")
                    continue
                # Map fields to columns
                row = dict(zip(voa_hist_columns, fields))
                ba_reference = row.get('ba_reference', '').strip() or None
                effective_date = parse_date(row.get('effective_date', ''))
                rateable_value = parse_numeric(row.get('rateable_value', ''))
                property_id = prop_map.get(ba_reference)
                if not ba_reference or not property_id:
                    skipped += 1
                    if skipped <= 5:
                        print(f"Skipped: ba_reference missing or not found in properties for line {row_count}: {row}")
                    continue
                record = {
                    'property_id': property_id,
                    'billing_auth_code': row.get('billing_auth_code'),
                    'empty1': row.get('empty1'),
                    'ba_reference': ba_reference,
                    'scat_code': row.get('scat_code'),
                    'description': row.get('description'),
                    'herid': row.get('herid'),
                    'effective_date': effective_date,
                    'empty2': row.get('empty2'),
                    'rateable_value': rateable_value,
                    'uprn': row.get('uprn'),
                    'change_date': row.get('change_date'),
                    'list_code': row.get('list_code'),
                    'property_link_number': row.get('property_link_number'),
                    'entry_date': row.get('entry_date'),
                    'removal_date': row.get('removal_date'),
                    'source': source_label
                }
                batch.append(record)
                if len(batch) >= batch_size:
                    print(f"Inserting batch at line {row_count} (batch size: {len(batch)})")
                    session.execute(
                        text("""
                        INSERT INTO historic_valuations (
                            property_id, billing_auth_code, empty1, ba_reference, scat_code, description, herid, effective_date, empty2, rateable_value, uprn, change_date, list_code, property_link_number, entry_date, removal_date, source
                        ) VALUES (
                            :property_id, :billing_auth_code, :empty1, :ba_reference, :scat_code, :description, :herid, :effective_date, :empty2, :rateable_value, :uprn, :change_date, :list_code, :property_link_number, :entry_date, :removal_date, :source
                        )
                        """), batch
                    )
                    inserted += len(batch)
                    batch = []
    if batch:
        print(f"Inserting final batch at line {row_count} (batch size: {len(batch)})")
        session.execute(
            text("""
            INSERT INTO historic_valuations (
                property_id, billing_auth_code, empty1, ba_reference, scat_code, description, herid, effective_date, empty2, rateable_value, uprn, change_date, list_code, property_link_number, entry_date, removal_date, source
            ) VALUES (
                :property_id, :billing_auth_code, :empty1, :ba_reference, :scat_code, :description, :herid, :effective_date, :empty2, :rateable_value, :uprn, :change_date, :list_code, :property_link_number, :entry_date, :removal_date, :source
            )
            """), batch
        )
        inserted += len(batch)
    session.commit()
    print(f"VOA Historic valuations ingestion complete for {source_label}. Inserted: {inserted}, Skipped: {skipped}, Malformed: {malformed}")

if __name__ == "__main__":
    ingest_historic_valuations(
        "data/uk-englandwales-ndr-2010-listentries-compiled-epoch-0052-baseline-csv/uk-englandwales-ndr-2010-listentries-compiled-epoch-0052-baseline-historic-csv.csv",
        "2010-historic"
    )
