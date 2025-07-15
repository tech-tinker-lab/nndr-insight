from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

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