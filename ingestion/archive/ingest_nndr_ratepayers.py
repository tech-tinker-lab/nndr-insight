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

def ingest_nndr_ratepayers(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        inserted = 0
        skipped = 0
        for row in reader:
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
            session.execute(
                text("""
                INSERT INTO ratepayers (
                    property_id, name, address, company_number, liability_start_date, liability_end_date, annual_charge, exemption_amount, exemption_code,
                    mandatory_amount, mandatory_relief, charity_relief_amount, disc_relief_amount, discretionary_charitable_relief, additional_rlf, additional_relief,
                    sbr_applied, sbr_supplement, sbr_amount, charge_type, report_date, notes
                ) VALUES (
                    :property_id, :name, :address, :company_number, :liability_start_date, :liability_end_date, :annual_charge, :exemption_amount, :exemption_code,
                    :mandatory_amount, :mandatory_relief, :charity_relief_amount, :disc_relief_amount, :discretionary_charitable_relief, :additional_rlf, :additional_relief,
                    :sbr_applied, :sbr_supplement, :sbr_amount, :charge_type, :report_date, :notes
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
                    'notes': row.get('Notes', '').strip() or None
                }
            )
            inserted += 1
        session.commit()
    print(f"Ratepayers ingestion complete. Inserted: {inserted}, Skipped: {skipped}")

if __name__ == "__main__":
    ingest_nndr_ratepayers("data/nndr-ratepayers March 2015_0.csv")
