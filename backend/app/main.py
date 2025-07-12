import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# FastAPI entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, forecast, map, property_compare, tables, geospatial, analytics, admin, admin_user, ai_analysis, design_system

app = FastAPI()

# Add this block:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(forecast.router, prefix="/api")
app.include_router(map.router, prefix="/api")
app.include_router(property_compare.router, prefix="/api")
app.include_router(tables.router, prefix="/api")
app.include_router(geospatial.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(admin_user.router, prefix="/api")
app.include_router(ai_analysis.router)
app.include_router(design_system.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "NNDR Insight Backend Running"}
