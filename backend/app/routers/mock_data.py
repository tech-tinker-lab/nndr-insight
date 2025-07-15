from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

# --- MOCK DATA ---

MOCK_FORECAST = {
    "area": "South Cambridgeshire",
    "year": 2024,
    "totalIncome": 1234567,
    "breakdown": [
        {"sector": "Retail", "value": 400000},
        {"sector": "Office", "value": 300000},
        {"sector": "Industrial", "value": 200000},
        {"sector": "Other", "value": 333567},
    ],
    "properties": [
        {
            "id": 1,
            "uprn": "100010001",
            "address": "1 High St, Cambourne",
            "rateableValue": 12000,
            "sector": "Retail",
            "geometry": "POINT(-0.0701 52.2234)"
        },
        {
            "id": 2,
            "uprn": "100010002",
            "address": "2 Market Rd, Sawston",
            "rateableValue": 18000,
            "sector": "Office",
            "geometry": "POINT(-0.1502 52.1201)"
        },
        {
            "id": 3,
            "uprn": "100010003",
            "address": "3 Main St, Bar Hill",
            "rateableValue": 22000,
            "sector": "Industrial",
            "geometry": "POINT(-0.0303 52.2502)"
        },
    ]
}

MOCK_AREAS = [
    {
        "id": 1,
        "name": "Cambridge North",
        "geometry": "POLYGON((0.1 52.3, 0.2 52.3, 0.2 52.4, 0.1 52.4, 0.1 52.3))",
        "summary": {"properties": 120, "totalRateableValue": 1500000}
    },
    {
        "id": 2,
        "name": "Cambourne",
        "geometry": "POLYGON((-0.1 52.2, -0.05 52.2, -0.05 52.25, -0.1 52.25, -0.1 52.2))",
        "summary": {"properties": 80, "totalRateableValue": 900000}
    }
]

MOCK_AREA_DETAIL = {
    1: {
        "id": 1,
        "name": "Cambridge North",
        "geometry": "POLYGON((0.1 52.3, 0.2 52.3, 0.2 52.4, 0.1 52.4, 0.1 52.3))",
        "properties": [
            {
                "id": 10,
                "uprn": "100020001",
                "address": "10 Science Park, Cambridge",
                "rateableValue": 35000,
                "sector": "Office",
                "geometry": "POINT(0.15 52.35)"
            },
            {
                "id": 11,
                "uprn": "100020002",
                "address": "11 Science Park, Cambridge",
                "rateableValue": 37000,
                "sector": "Office",
                "geometry": "POINT(0.16 52.36)"
            }
        ]
    },
    2: {
        "id": 2,
        "name": "Cambourne",
        "geometry": "POLYGON((-0.1 52.2, -0.05 52.2, -0.05 52.25, -0.1 52.25, -0.1 52.2))",
        "properties": [
            {
                "id": 20,
                "uprn": "100030001",
                "address": "20 High St, Cambourne",
                "rateableValue": 15000,
                "sector": "Retail",
                "geometry": "POINT(-0.08 52.22)"
            }
        ]
    }
}

MOCK_PROPERTIES = [
    {
        "id": 1,
        "uprn": "100010001",
        "address": "1 High St, Cambourne",
        "rateableValue": 12000,
        "sector": "Retail",
        "geometry": "POINT(-0.0701 52.2234)"
    },
    {
        "id": 2,
        "uprn": "100010002",
        "address": "2 Market Rd, Sawston",
        "rateableValue": 18000,
        "sector": "Office",
        "geometry": "POINT(-0.1502 52.1201)"
    },
    {
        "id": 3,
        "uprn": "100010003",
        "address": "3 Main St, Bar Hill",
        "rateableValue": 22000,
        "sector": "Industrial",
        "geometry": "POINT(-0.0303 52.2502)"
    }
]

MOCK_INDICATORS = [
    {
        "id": 1,
        "name": "Retail Rateable Value Index",
        "description": "Average rateable value for retail properties.",
        "trend": [
            {"year": 2020, "value": 11000},
            {"year": 2021, "value": 11500},
            {"year": 2022, "value": 12000},
            {"year": 2023, "value": 12500},
            {"year": 2024, "value": 13000}
        ],
        "values": [
            {"year": 2024, "area": "South Cambs", "value": 13000},
            {"year": 2024, "area": "Cambourne", "value": 12000}
        ]
    },
    {
        "id": 2,
        "name": "Office Occupancy Rate",
        "description": "Proportion of offices occupied.",
        "trend": [
            {"year": 2020, "value": 0.85},
            {"year": 2021, "value": 0.88},
            {"year": 2022, "value": 0.90},
            {"year": 2023, "value": 0.91},
            {"year": 2024, "value": 0.92}
        ],
        "values": [
            {"year": 2024, "area": "South Cambs", "value": 0.92},
            {"year": 2024, "area": "Cambourne", "value": 0.89}
        ]
    }
]

MOCK_INDICATOR_DETAIL = {
    1: MOCK_INDICATORS[0],
    2: MOCK_INDICATORS[1]
}

# --- ENDPOINTS ---

@router.get("/forecast", tags=["Mock Data"])
def get_forecast():
    """Get forecast for main area (mock, PostGIS-ready)."""
    return JSONResponse(content=MOCK_FORECAST)

@router.get("/areas", tags=["Mock Data"])
def get_areas():
    """Get all areas (mock, PostGIS-ready)."""
    return JSONResponse(content=MOCK_AREAS)

@router.get("/area/{area_id}", tags=["Mock Data"])
def get_area_detail(area_id: int):
    """Get area detail by ID (mock, PostGIS-ready)."""
    return JSONResponse(content=MOCK_AREA_DETAIL.get(area_id, {}))

@router.get("/properties", tags=["Mock Data"])
def get_properties():
    """Get all properties (mock, PostGIS-ready)."""
    return JSONResponse(content=MOCK_PROPERTIES)

@router.get("/indicators", tags=["Mock Data"])
def get_indicators():
    """Get all indicators (mock, PostGIS-ready)."""
    return JSONResponse(content=MOCK_INDICATORS)

@router.get("/indicator/{indicator_id}", tags=["Mock Data"])
def get_indicator_detail(indicator_id: int):
    """Get indicator detail by ID (mock, PostGIS-ready)."""
    return JSONResponse(content=MOCK_INDICATOR_DETAIL.get(indicator_id, {}))

@router.get("/datasets", tags=["Mock Data"])
def get_datasets():
    """Get all datasets (mock)."""
    return JSONResponse(content=[
        {"id": 1, "name": "NNDR Property List", "status": "loaded"},
        {"id": 2, "name": "UPRN Master List", "status": "pending"},
        {"id": 3, "name": "Historic Billing Data", "status": "pending"},
        {"id": 4, "name": "Council Tax Property List", "status": "pending"}
    ])

# ---
# For production, replace the mock data with SQL queries to PostGIS, e.g.:
# SELECT id, uprn, address, rateable_value, sector, ST_AsText(geom) as geometry FROM properties; 