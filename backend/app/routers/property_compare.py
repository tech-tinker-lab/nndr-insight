from fastapi import APIRouter, Query
from pathlib import Path
from app.services.flexible_csv_loader import load_csv_flexibly

router = APIRouter()

@router.get("/non-rated-properties")
def non_rated_properties(
    nndr_dataset: str,
    all_props_dataset: str,
    nndr_postcode_col: str,
    all_postcode_col: str,
    limit: int = 100
):
    data_dir = Path(__file__).parent.parent.parent / "data"
    nndr = load_csv_flexibly(data_dir / nndr_dataset)
    all_props = load_csv_flexibly(data_dir / all_props_dataset)
    nndr_postcodes = set(row[nndr_postcode_col].replace(" ", "").upper() for row in nndr if row.get(nndr_postcode_col))
    missing = [
        row for row in all_props
        if row.get(all_postcode_col) and row[all_postcode_col].replace(" ", "").upper() not in nndr_postcodes
    ]
    return {"missing_properties": missing[:limit], "total_missing": len(missing)}