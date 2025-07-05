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

def ingest_valuations_custom(csv_path, source_label):
    # Preload ba_reference to id mapping
    prop_map = {}
    for row in session.execute(text("SELECT ba_reference, id FROM properties")):
        prop_map[row.ba_reference.strip()] = row.id

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        batch = []
        batch_size = 1000
        inserted = 0
        skipped = 0
        malformed = 0
        for row in reader:
            # Skip malformed rows (e.g., None key or missing expected field)
            if not isinstance(row, dict) or 'BAReference' not in row:
                malformed += 1
                if malformed <= 5:
                    print(f"Skipped: Malformed row: {row}")
                continue
            ba_reference = row.get('BAReference', '').strip() or None
            effective_date = parse_date(row.get('EffectiveDate', ''))
            rateable_value = parse_numeric(row.get('RateableValue', ''))
            source = source_label
            status = row.get('Status', '').strip() or None
            notes = row.get('Notes', '').strip() or None
            if not ba_reference:
                skipped += 1
                if skipped <= 5:
                    print(f"Skipped: Empty ba_reference in row: {row}")
                continue
            property_id = prop_map.get(ba_reference)
            if not property_id:
                skipped += 1
                continue
            batch.append({
                'property_id': property_id,
                'effective_date': effective_date,
                'rateable_value': rateable_value,
                'source': source,
                'status': status,
                'notes': notes
            })
            if len(batch) >= batch_size:
                session.execute(
                    text("""
                    INSERT INTO valuations (property_id, effective_date, rateable_value, source, status, notes)
                    VALUES (:property_id, :effective_date, :rateable_value, :source, :status, :notes)
                    """), batch
                )
                inserted += len(batch)
                batch = []
        # Insert any remaining
        if batch:
            session.execute(
                text("""
                INSERT INTO valuations (property_id, effective_date, rateable_value, source, status, notes)
                VALUES (:property_id, :effective_date, :rateable_value, :source, :status, :notes)
                """), batch
            )
            inserted += len(batch)
        session.commit()
    print(f"Valuations ingestion complete for {source_label}. Inserted: {inserted}, Skipped: {skipped}, Malformed: {malformed}")

def print_voa_header_and_sample(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter='*')
        header = next(reader)
        sample = next(reader)
        print('VOA Header Fields:')
        print(header)
        print('Sample Row:')
        print(sample)

voa_columns = [
    "row_id",                # 0
    "billing_auth_code",     # 1
    "empty1",                # 2
    "ba_reference",          # 3
    "scat_code",             # 4
    "description",           # 5
    "herid",                 # 6
    "address_full",          # 7
    "empty2",                # 8
    "address1",              # 9
    "address2",              # 10
    "address3",              # 11
    "address4",              # 12
    "address5",              # 13
    "postcode",              # 14
    "effective_date",        # 15
    "empty3",                # 16
    "rateable_value",        # 17
    "empty4",                # 18
    "uprn",                  # 19
    "compiled_list_date",    # 20
    "list_code",             # 21
    "empty5",                # 22
    "empty6",                # 23
    "empty7",                # 24
    "property_link_number",  # 25
    "entry_date",            # 26
    "empty8",                # 27
    "empty9"                 # 28
]

def ingest_voa_valuations(csv_path, source_label):
    prop_map = {}
    for row in session.execute(text("SELECT ba_reference, id FROM properties")):
        prop_map[row.ba_reference.strip()] = row.id

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=voa_columns, delimiter='*')
        batch = []
        batch_size = 1000
        inserted = 0
        skipped = 0
        malformed = 0
        row_count = 0
        for row in reader:
            row_count += 1
            if row_count <= 3:
                print(f"Row {row_count}: {row}")
            ba_reference = row.get('ba_reference', '').strip() or None
            effective_date = parse_date(row.get('effective_date', ''))
            rateable_value = parse_numeric(row.get('rateable_value', ''))
            property_id = prop_map.get(ba_reference)
            if not ba_reference or not property_id:
                skipped += 1
                if skipped <= 5:
                    print(f"Skipped: ba_reference missing or not found in properties for row {row_count}: {row}")
                continue
            # Prepare all fields for insert
            record = {
                'property_id': property_id,
                'row_id': row.get('row_id'),
                'billing_auth_code': row.get('billing_auth_code'),
                'empty1': row.get('empty1'),
                'ba_reference': ba_reference,
                'scat_code': row.get('scat_code'),
                'description': row.get('description'),
                'herid': row.get('herid'),
                'address_full': row.get('address_full'),
                'empty2': row.get('empty2'),
                'address1': row.get('address1'),
                'address2': row.get('address2'),
                'address3': row.get('address3'),
                'address4': row.get('address4'),
                'address5': row.get('address5'),
                'postcode': row.get('postcode'),
                'effective_date': effective_date,
                'empty3': row.get('empty3'),
                'rateable_value': rateable_value,
                'empty4': row.get('empty4'),
                'uprn': row.get('uprn'),
                'compiled_list_date': row.get('compiled_list_date'),
                'list_code': row.get('list_code'),
                'empty5': row.get('empty5'),
                'empty6': row.get('empty6'),
                'empty7': row.get('empty7'),
                'property_link_number': row.get('property_link_number'),
                'entry_date': row.get('entry_date'),
                'empty8': row.get('empty8'),
                'empty9': row.get('empty9'),
                'source': source_label
            }
            batch.append(record)
            if len(batch) >= batch_size:
                print(f"Inserting batch at row {row_count} (batch size: {len(batch)})")
                session.execute(
                    text("""
                    INSERT INTO valuations (
                        property_id, row_id, billing_auth_code, empty1, ba_reference, scat_code, description, herid, address_full, empty2, address1, address2, address3, address4, address5, postcode, effective_date, empty3, rateable_value, empty4, uprn, compiled_list_date, list_code, empty5, empty6, empty7, property_link_number, entry_date, empty8, empty9, source
                    ) VALUES (
                        :property_id, :row_id, :billing_auth_code, :empty1, :ba_reference, :scat_code, :description, :herid, :address_full, :empty2, :address1, :address2, :address3, :address4, :address5, :postcode, :effective_date, :empty3, :rateable_value, :empty4, :uprn, :compiled_list_date, :list_code, :empty5, :empty6, :empty7, :property_link_number, :entry_date, :empty8, :empty9, :source
                    )
                    """), batch
                )
                inserted += len(batch)
                batch = []
        if batch:
            print(f"Inserting final batch at row {row_count} (batch size: {len(batch)})")
            session.execute(
                text("""
                INSERT INTO valuations (
                    property_id, row_id, billing_auth_code, empty1, ba_reference, scat_code, description, herid, address_full, empty2, address1, address2, address3, address4, address5, postcode, effective_date, empty3, rateable_value, empty4, uprn, compiled_list_date, list_code, empty5, empty6, empty7, property_link_number, entry_date, empty8, empty9, source
                ) VALUES (
                    :property_id, :row_id, :billing_auth_code, :empty1, :ba_reference, :scat_code, :description, :herid, :address_full, :empty2, :address1, :address2, :address3, :address4, :address5, :postcode, :effective_date, :empty3, :rateable_value, :empty4, :uprn, :compiled_list_date, :list_code, :empty5, :empty6, :empty7, :property_link_number, :entry_date, :empty8, :empty9, :source
                )
                """), batch
            )
            inserted += len(batch)
        session.commit()
    print(f"VOA Valuations ingestion complete for {source_label}. Inserted: {inserted}, Skipped: {skipped}")

if __name__ == "__main__":
    # Example usage for VOA valuations ingestion
    ingest_voa_valuations(
        "data/uk-englandwales-ndr-2010-listentries-compiled-epoch-0052-baseline-csv/uk-englandwales-ndr-2010-listentries-compiled-epoch-0052-baseline-csv.csv",
        "2010"
    )
