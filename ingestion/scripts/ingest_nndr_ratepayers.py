import csv
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import argparse
from tqdm import tqdm
from datetime import datetime
import os

engine = sqlalchemy.create_engine(
    "postgresql://nndr:nndrpass@localhost:5432/nndr_db"
)
Session = sessionmaker(bind=engine)
session = Session()

# Add argument parsing for --source-path, --source, --client, --session-id, --batch-id
parser = argparse.ArgumentParser(description='NNDR Ratepayers Ingestion')
parser.add_argument('--source-path', required=True, help='Path to CSV file or directory')
parser.add_argument('--source', help='Source identifier (e.g., "NNDR_RATEPAYERS_2024")')
parser.add_argument('--client', help='Client identifier (e.g., "client_001")')
parser.add_argument('--session-id', help='Session identifier (auto-generated if not provided)')
parser.add_argument('--batch-id', help='Batch identifier (auto-generated if not provided)')
args = parser.parse_args()

batch_id = args.batch_id or f"nndr_ratepayers_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
session_id = args.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
source_name = args.source or "NNDR_RATEPAYERS_DEFAULT"
client_name = args.client or "default_client"

# Determine if source-path is a file or directory
if os.path.isdir(args.source_path):
    csv_files = [os.path.join(args.source_path, f) for f in os.listdir(args.source_path) if f.lower().endswith('.csv')]
    if not csv_files:
        print(f"No CSV files found in directory: {args.source_path}")
        exit(1)
elif os.path.isfile(args.source_path):
    csv_files = [args.source_path]
else:
    print(f"source-path is not a valid file or directory: {args.source_path}")
    exit(1)

# Improved file metadata logging
if len(csv_files) == 1:
    print(f"File path: {csv_files[0]}")
    print(f"File size: {os.path.getsize(csv_files[0])}")
    print(f"File modified: {datetime.fromtimestamp(os.path.getmtime(csv_files[0]))}")
else:
    print(f"Number of files: {len(csv_files)}")
    print(f"First file: {csv_files[0]}")
    print(f"First file size: {os.path.getsize(csv_files[0])}")
    print(f"First file modified: {datetime.fromtimestamp(os.path.getmtime(csv_files[0]))}")
    total_size = sum(os.path.getsize(f) for f in csv_files)
    print(f"Total size of all files: {total_size}")

def parse_date(date_str):
    if not date_str or not date_str.strip():
        return None
    for fmt in ("%d-%b-%y", "%d/%m/%Y", "%Y-%m-%d", "%d-%b-%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except Exception:
            continue
    return None

def ingest_nndr_ratepayers(csv_files):
    inserted = 0
    skipped = 0
    for csv_path in csv_files:
        file_size = os.path.getsize(csv_path)
        file_modified = datetime.fromtimestamp(os.path.getmtime(csv_path))
        file_name = os.path.basename(csv_path)
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            pbar = tqdm(reader, desc=f"Ingesting {file_name}")
            for row in pbar:
                ba_reference = row.get('PropertyRateableValuePlaceRef', '').strip() or None
                # Find property_id by ba_reference
                result = session.execute(
                    text("SELECT id FROM properties WHERE ba_reference = :ba_reference"),
                    {'ba_reference': ba_reference}
                ).fetchone()
                if not result:
                    skipped += 1
                    continue  # Skip if property not found
                property_id = result[0]
                # Add audit/metadata columns
                session.execute(
                    text("""
                    INSERT INTO ratepayers (
                        property_id, name, address, company_number, liability_start_date, liability_end_date, annual_charge, exemption_amount, exemption_code,
                        mandatory_amount, mandatory_relief, charity_relief_amount, disc_relief_amount, discretionary_charitable_relief, additional_rlf, additional_relief,
                        sbr_applied, sbr_supplement, sbr_amount, charge_type, report_date, notes,
                        source_name, upload_user, upload_timestamp, batch_id, source_file, file_size, file_modified, session_id, client_name
                    ) VALUES (
                        :property_id, :name, :address, :company_number, :liability_start_date, :liability_end_date, :annual_charge, :exemption_amount, :exemption_code,
                        :mandatory_amount, :mandatory_relief, :charity_relief_amount, :disc_relief_amount, :discretionary_charitable_relief, :additional_rlf, :additional_relief,
                        :sbr_applied, :sbr_supplement, :sbr_amount, :charge_type, :report_date, :notes,
                        :source_name, :upload_user, :upload_timestamp, :batch_id, :source_file, :file_size, :file_modified, :session_id, :client_name
                    )
                    """),
                    {
                        'property_id': property_id,
                        'name': row.get('Name', '').strip() or None,
                        'address': row.get('Address', '').strip() or None,
                        'company_number': row.get('CompanyNumber', '').strip() or None,
                        'liability_start_date': parse_date(row.get('LiabilityPeriodStartDate', '')),
                        'liability_end_date': parse_date(row.get('LiabilityPeriodEndDate', '')),
                        'annual_charge': row.get('AnnualCharge', '') or None,
                        'exemption_amount': row.get('ExemptionAmount', '') or None,
                        'exemption_code': row.get('ExemptionCode', '').strip() or None,
                        'mandatory_amount': row.get('MandatoryAmount', '') or None,
                        'mandatory_relief': row.get('MandatoryRelief', '').strip() or None,
                        'charity_relief_amount': row.get('CharityReliefAmount', '') or None,
                        'disc_relief_amount': row.get('DiscReliefAmount', '') or None,
                        'discretionary_charitable_relief': row.get('DiscretionaryCharitableRelief', '').strip() or None,
                        'additional_rlf': row.get('AdditionalRlf', '').strip() or None,
                        'additional_relief': row.get('AdditionalRelief', '').strip() or None,
                        'sbr_applied': row.get('SBRApplied', '').strip() or None,
                        'sbr_supplement': row.get('SBRSupplement', '').strip() or None,
                        'sbr_amount': row.get('SBRAmount', '') or None,
                        'charge_type': row.get('ChargeTypeVEmptyCommercialPropertyOOccupied', '').strip() or None,
                        'report_date': parse_date(row.get('ReportDate', '')),
                        'notes': row.get('Notes', '').strip() or None,
                        # Metadata columns
                        'source_name': source_name,
                        'upload_user': os.getenv("PGUSER", ""),
                        'upload_timestamp': datetime.now().isoformat(),
                        'batch_id': batch_id,
                        'source_file': file_name,
                        'file_size': file_size,
                        'file_modified': file_modified.isoformat(),
                        'session_id': session_id,
                        'client_name': client_name
                    }
                )
                inserted += 1
            pbar.close()
        session.commit()
    print(f"Ratepayers ingestion complete. Inserted: {inserted}, Skipped: {skipped}")

if __name__ == "__main__":
    ingest_nndr_ratepayers(csv_files)
