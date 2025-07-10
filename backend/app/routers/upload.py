# Upload NNDR data router
from fastapi import APIRouter
from sqlalchemy import create_engine, text
import os
import math

router = APIRouter()

# --- File upload endpoints are commented out for future implementation ---
# @router.post("/upload")
# async def upload_nndr_data(file: UploadFile = File(...)):
#     # TODO: Accept file upload, detect dataset type, and process accordingly
#     # For now, upload is disabled. Use this endpoint in the future for file uploads.
#     return {"filename": file.filename, "message": "Upload endpoint (not yet implemented)"}

# --- End future upload endpoints ---

# Database connection using environment variables
import os
connection_string = (
    f"postgresql://{os.getenv('PGUSER', 'nndr')}:{os.getenv('PGPASSWORD', 'nndrpass')}@"
    f"{os.getenv('PGHOST', 'localhost')}:{os.getenv('PGPORT', '5432')}/"
    f"{os.getenv('PGDATABASE', 'nndr_test')}"
)
engine = create_engine(connection_string)

def clean_for_json(records):
    for row in records:
        for k, v in row.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                row[k] = None
    return records

@router.get("/nndr/properties")
def get_nndr_properties(skip: int = 0, limit: int = 100):
    # Returns paginated property data from the database
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, ba_reference, property_address, postcode, property_category_code, property_description
            FROM properties
            ORDER BY id
            OFFSET :skip LIMIT :limit
        """), {"skip": skip, "limit": limit})
        records = [dict(row._mapping) for row in result]
    return {"data": clean_for_json(records), "skip": skip, "limit": limit}

@router.get("/nndr/categories")
def get_nndr_categories():
    # Returns all property categories
    with engine.connect() as conn:
        result = conn.execute(text("SELECT code, description FROM categories ORDER BY code"))
        records = [dict(row) for row in result]
    return {"categories": records}

# --- The following endpoints are deprecated or for future use ---
# @router.get("/nndr-data")
# def get_nndr_data(...):
#     # Deprecated: Use /nndr/properties instead
#     pass
# @router.get("/datasets")
# def list_datasets():
#     # Deprecated: Use database-driven endpoints
#     pass
# @router.get("/dataset-columns")
# def get_dataset_columns(...):
#     # Deprecated: Use database-driven endpoints
#     pass
