# Pydantic + SQLAlchemy models
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float, BigInteger, Text, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional, List
from datetime import date, datetime

Base = declarative_base()

# Original NNDR models
class NNDRData(Base):
    __tablename__ = "nndr_data"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(String, index=True)
    address = Column(String)
    postcode = Column(String)
    rateable_value = Column(Float)
    description = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    current_rating_status = Column(String)
    last_billed_date = Column(String)

class NNDRDataIn(BaseModel):
    property_id: str
    address: str
    postcode: str
    rateable_value: float
    description: str
    latitude: float
    longitude: float
    current_rating_status: str
    last_billed_date: str

# New comprehensive models for geospatial data
class GazetteerItem(BaseModel):
    id: int
    property_id: Optional[str] = None
    x_coordinate: Optional[float] = None
    y_coordinate: Optional[float] = None
    address: Optional[str] = None
    postcode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    property_type: Optional[str] = None
    district: Optional[str] = None
    source: Optional[str] = None

class UPRNItem(BaseModel):
    uprn: int
    x_coordinate: Optional[float] = None
    y_coordinate: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: Optional[str] = None

class CodePointItem(BaseModel):
    postcode: str
    positional_quality_indicator: Optional[str] = None
    easting: Optional[float] = None
    northing: Optional[float] = None
    country_code: Optional[str] = None
    nhs_regional_ha_code: Optional[str] = None
    nhs_ha_code: Optional[str] = None
    admin_county_code: Optional[str] = None
    admin_district_code: Optional[str] = None
    admin_ward_code: Optional[str] = None
    source: Optional[str] = None

class ONSPDItem(BaseModel):
    pcds: str
    pcd: Optional[str] = None
    lat: Optional[float] = None
    long: Optional[float] = None
    ctry: Optional[str] = None
    oslaua: Optional[str] = None
    osward: Optional[str] = None
    parish: Optional[str] = None
    oa11: Optional[str] = None
    lsoa11: Optional[str] = None
    msoa11: Optional[str] = None
    imd: Optional[str] = None
    rgn: Optional[str] = None
    pcon: Optional[str] = None
    ur01ind: Optional[str] = None
    oac11: Optional[str] = None
    oseast1m: Optional[str] = None
    osnrth1m: Optional[str] = None
    dointr: Optional[str] = None
    doterm: Optional[str] = None

class OSNameItem(BaseModel):
    id: int
    os_id: str
    names_uri: Optional[str] = None
    name1: Optional[str] = None
    name1_lang: Optional[str] = None
    name2: Optional[str] = None
    name2_lang: Optional[str] = None
    type: Optional[str] = None
    local_type: Optional[str] = None
    geometry_x: Optional[float] = None
    geometry_y: Optional[float] = None
    most_detail_view_res: Optional[int] = None
    least_detail_view_res: Optional[int] = None
    postcode_district: Optional[str] = None
    populated_place: Optional[str] = None
    populated_place_type: Optional[str] = None
    district_borough: Optional[str] = None
    district_borough_type: Optional[str] = None
    county_unitary: Optional[str] = None
    county_unitary_type: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None

class LADBoundary(BaseModel):
    id: int
    lad_code: Optional[str] = None
    lad_name: Optional[str] = None
    geometry: Optional[str] = None  # WKT representation

class MapLocalItem(BaseModel):
    id: int
    fid: Optional[str] = None
    theme: Optional[str] = None
    make: Optional[str] = None
    physicalpresence: Optional[str] = None
    descriptivegroup: Optional[str] = None
    descriptiveterm: Optional[str] = None
    fclass: Optional[str] = None
    geometry: Optional[str] = None  # WKT representation

# API Request/Response models
class GeocodeRequest(BaseModel):
    query: str = Field(..., description="Address or postcode to geocode")
    limit: int = Field(10, description="Maximum number of results to return")

class GeocodeResponse(BaseModel):
    query: str
    results: List[dict]
    total_found: int

class SpatialQueryRequest(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    radius_meters: float = Field(1000, description="Search radius in meters")
    datasets: Optional[List[str]] = Field(None, description="Specific datasets to search")

class PropertySearchRequest(BaseModel):
    postcode: Optional[str] = None
    address: Optional[str] = None
    uprn: Optional[int] = None
    limit: int = Field(50, description="Maximum number of results")

class StatisticsResponse(BaseModel):
    total_properties: int
    total_postcodes: int
    total_places: int
    coverage_by_region: dict
    last_updated: str

class DatasetInfo(BaseModel):
    name: str
    description: str
    record_count: int
    last_updated: str
    source: str

# Admin API Models for Staging to Master Migration
class StagingMigrationRequest(BaseModel):
    batch_id: Optional[str] = Field(None, description="Filter by batch ID")
    source_name: Optional[str] = Field(None, description="Filter by source name")
    session_id: Optional[str] = Field(None, description="Filter by session ID")

class StagingMigrationResponse(BaseModel):
    table_name: str
    master_table: str
    records_migrated: int
    final_master_count: int
    migration_timestamp: datetime
    applied_filters: dict

class StagingPreviewResponse(BaseModel):
    table_name: str
    total_count: int
    sample_data: List[dict]
    filter_options: dict
    applied_filters: dict

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    email = Column(String)
    created_at = Column(String)
