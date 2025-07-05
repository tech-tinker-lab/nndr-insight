from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from app.models import (
    GeocodeRequest, GeocodeResponse, SpatialQueryRequest, 
    PropertySearchRequest, StatisticsResponse, DatasetInfo
)
from app.services.database_service import DatabaseService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/geospatial", tags=["Geospatial Data"])

def get_db_service():
    return DatabaseService()

@router.get("/", summary="Geospatial API Overview")
async def geospatial_overview():
    """Get an overview of available geospatial endpoints"""
    return {
        "message": "NNDR Insight Geospatial API",
        "description": "Comprehensive API for UK geospatial datasets including UPRNs, postcodes, place names, and administrative boundaries",
        "endpoints": {
            "statistics": "/geospatial/statistics - Get database statistics",
            "datasets": "/geospatial/datasets - Get dataset information",
            "geocode": "/geospatial/geocode - Geocode addresses and postcodes",
            "search": "/geospatial/search - Search for properties",
            "spatial": "/geospatial/spatial - Spatial queries around points",
            "postcodes": "/geospatial/postcodes/{postcode} - Get postcode details",
            "boundaries": "/geospatial/boundaries - Get LAD boundaries",
            "uprn": "/geospatial/uprn/{uprn} - Get UPRN details"
        }
    }

@router.get("/statistics", response_model=StatisticsResponse, summary="Get Database Statistics")
async def get_statistics(db: DatabaseService = Depends(get_db_service)):
    """Get comprehensive statistics about all ingested datasets"""
    try:
        stats = db.get_statistics()
        return StatisticsResponse(
            total_properties=stats.get('total_uprns', 0),
            total_postcodes=stats.get('total_postcodes', 0),
            total_places=stats.get('total_places', 0),
            coverage_by_region=stats.get('coverage_by_region', {}),
            last_updated=stats.get('last_updated', '')
        )
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")

@router.get("/datasets", response_model=List[DatasetInfo], summary="Get Dataset Information")
async def get_datasets(db: DatabaseService = Depends(get_db_service)):
    """Get information about all available datasets"""
    try:
        datasets = db.get_dataset_info()
        return [
            DatasetInfo(
                name=dataset['name'],
                description=dataset['description'],
                record_count=dataset.get('record_count', 0),
                last_updated="2025-01-01",  # Placeholder
                source=dataset['source']
            )
            for dataset in datasets
        ]
    except Exception as e:
        logger.error(f"Error getting datasets: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dataset information")

@router.post("/geocode", response_model=GeocodeResponse, summary="Geocode Address or Postcode")
async def geocode_address(request: GeocodeRequest, db: DatabaseService = Depends(get_db_service)):
    """Geocode an address or postcode using multiple datasets"""
    try:
        results = db.geocode_address(request.query, request.limit)
        return GeocodeResponse(
            query=request.query,
            results=results,
            total_found=len(results)
        )
    except Exception as e:
        logger.error(f"Error geocoding address: {e}")
        raise HTTPException(status_code=500, detail="Failed to geocode address")

@router.post("/search", summary="Search Properties")
async def search_properties(request: PropertySearchRequest, db: DatabaseService = Depends(get_db_service)):
    """Search for properties using various criteria"""
    try:
        results = db.search_properties(
            postcode=request.postcode,
            address=request.address,
            uprn=request.uprn,
            limit=request.limit
        )
        return {
            "query": {
                "postcode": request.postcode,
                "address": request.address,
                "uprn": request.uprn
            },
            "results": results,
            "total_found": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching properties: {e}")
        raise HTTPException(status_code=500, detail="Failed to search properties")

@router.post("/spatial", summary="Spatial Query")
async def spatial_query(request: SpatialQueryRequest, db: DatabaseService = Depends(get_db_service)):
    """Perform spatial queries around a point"""
    try:
        results = db.spatial_query(
            latitude=request.latitude,
            longitude=request.longitude,
            radius_meters=request.radius_meters,
            datasets=request.datasets
        )
        return {
            "query": {
                "latitude": request.latitude,
                "longitude": request.longitude,
                "radius_meters": request.radius_meters,
                "datasets": request.datasets
            },
            "results": results
        }
    except Exception as e:
        logger.error(f"Error in spatial query: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform spatial query")

@router.get("/postcodes/{postcode}", summary="Get Postcode Details")
async def get_postcode_details(postcode: str, db: DatabaseService = Depends(get_db_service)):
    """Get comprehensive details for a specific postcode"""
    try:
        details = db.get_postcode_details(postcode)
        return details
    except Exception as e:
        logger.error(f"Error getting postcode details: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve postcode details")

@router.get("/boundaries", summary="Get LAD Boundaries")
async def get_lad_boundaries(
    lad_code: Optional[str] = Query(None, description="Specific LAD code to retrieve"),
    db: DatabaseService = Depends(get_db_service)
):
    """Get Local Authority District boundaries"""
    try:
        boundaries = db.get_lad_boundaries(lad_code)
        return {
            "lad_code": lad_code,
            "boundaries": boundaries,
            "total_found": len(boundaries)
        }
    except Exception as e:
        logger.error(f"Error getting LAD boundaries: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve LAD boundaries")

@router.get("/uprn/{uprn}", summary="Get UPRN Details")
async def get_uprn_details(uprn: int, db: DatabaseService = Depends(get_db_service)):
    """Get details for a specific UPRN"""
    try:
        results = db.search_properties(uprn=uprn, limit=1)
        if not results:
            raise HTTPException(status_code=404, detail="UPRN not found")
        return results[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting UPRN details: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve UPRN details")

@router.get("/health", summary="Health Check")
async def health_check(db: DatabaseService = Depends(get_db_service)):
    """Check the health of the geospatial API and database connection"""
    try:
        # Try to get basic statistics to test database connection
        stats = db.get_statistics()
        return {
            "status": "healthy",
            "database": "connected",
            "total_uprns": stats.get('total_uprns', 0),
            "total_postcodes": stats.get('total_postcodes', 0)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy") 