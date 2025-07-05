from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict
from app.services.database_service import DatabaseService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["Analytics"])

def get_db_service():
    return DatabaseService()

@router.get("/", summary="Analytics API Overview")
async def analytics_overview():
    """Get an overview of available analytics endpoints"""
    return {
        "message": "NNDR Insight Analytics API",
        "description": "Data analysis and insights for UK geospatial datasets",
        "endpoints": {
            "coverage": "/analytics/coverage - Get data coverage analysis",
            "density": "/analytics/density - Get property density analysis",
            "regions": "/analytics/regions - Get regional statistics",
            "postcode_analysis": "/analytics/postcode-analysis - Get postcode distribution analysis"
        }
    }

@router.get("/coverage", summary="Data Coverage Analysis")
async def get_coverage_analysis(db: DatabaseService = Depends(get_db_service)):
    """Get comprehensive data coverage analysis across all datasets"""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get overall statistics
                stats = db.get_statistics()
                
                # Get coverage by region
                cur.execute("""
                    SELECT 
                        rgn as region,
                        COUNT(*) as postcode_count,
                        COUNT(DISTINCT oslaua) as lad_count
                    FROM onspd 
                    WHERE rgn IS NOT NULL 
                    GROUP BY rgn 
                    ORDER BY postcode_count DESC
                """)
                regional_coverage = [dict(row) for row in cur.fetchall()]
                
                # Get UPRN density by region
                cur.execute("""
                    SELECT 
                        o.rgn as region,
                        COUNT(u.uprn) as uprn_count
                    FROM onspd o
                    LEFT JOIN os_open_uprn u ON ST_DWithin(
                        ST_Transform(ST_SetSRID(ST_MakePoint(u.longitude, u.latitude), 4326), 27700),
                        ST_Transform(ST_SetSRID(ST_MakePoint(o.long, o.lat), 4326), 27700),
                        1000
                    )
                    WHERE o.rgn IS NOT NULL
                    GROUP BY o.rgn
                    ORDER BY uprn_count DESC
                """)
                uprn_density = [dict(row) for row in cur.fetchall()]
                
                return {
                    "overall_statistics": stats,
                    "regional_coverage": regional_coverage,
                    "uprn_density_by_region": uprn_density,
                    "coverage_summary": {
                        "total_regions": len(regional_coverage),
                        "total_lads": sum(row['lad_count'] for row in regional_coverage),
                        "total_postcodes": stats.get('total_postcodes', 0),
                        "total_uprns": stats.get('total_uprns', 0)
                    }
                }
    except Exception as e:
        logger.error(f"Error getting coverage analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve coverage analysis")

@router.get("/density", summary="Property Density Analysis")
async def get_density_analysis(
    region: Optional[str] = Query(None, description="Filter by region"),
    db: DatabaseService = Depends(get_db_service)
):
    """Get property density analysis"""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                if region:
                    # Get density for specific region
                    cur.execute("""
                        SELECT 
                            o.rgn as region,
                            o.oslaua as lad_code,
                            COUNT(u.uprn) as uprn_count,
                            COUNT(DISTINCT o.pcds) as postcode_count,
                            ROUND(COUNT(u.uprn)::numeric / COUNT(DISTINCT o.pcds), 2) as uprns_per_postcode
                        FROM onspd o
                        LEFT JOIN os_open_uprn u ON ST_DWithin(
                            ST_Transform(ST_SetSRID(ST_MakePoint(u.longitude, u.latitude), 4326), 27700),
                            ST_Transform(ST_SetSRID(ST_MakePoint(o.long, o.lat), 4326), 27700),
                            1000
                        )
                        WHERE o.rgn = %s
                        GROUP BY o.rgn, o.oslaua
                        ORDER BY uprn_count DESC
                    """, (region,))
                else:
                    # Get density for all regions
                    cur.execute("""
                        SELECT 
                            o.rgn as region,
                            COUNT(u.uprn) as uprn_count,
                            COUNT(DISTINCT o.pcds) as postcode_count,
                            ROUND(COUNT(u.uprn)::numeric / COUNT(DISTINCT o.pcds), 2) as uprns_per_postcode
                        FROM onspd o
                        LEFT JOIN os_open_uprn u ON ST_DWithin(
                            ST_Transform(ST_SetSRID(ST_MakePoint(u.longitude, u.latitude), 4326), 27700),
                            ST_Transform(ST_SetSRID(ST_MakePoint(o.long, o.lat), 4326), 27700),
                            1000
                        )
                        WHERE o.rgn IS NOT NULL
                        GROUP BY o.rgn
                        ORDER BY uprn_count DESC
                    """)
                
                density_data = [dict(row) for row in cur.fetchall()]
                
                return {
                    "region": region,
                    "density_analysis": density_data,
                    "summary": {
                        "total_regions": len(density_data),
                        "total_uprns": sum(row['uprn_count'] for row in density_data),
                        "total_postcodes": sum(row['postcode_count'] for row in density_data),
                        "average_uprns_per_postcode": sum(row['uprns_per_postcode'] for row in density_data) / len(density_data) if density_data else 0
                    }
                }
    except Exception as e:
        logger.error(f"Error getting density analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve density analysis")

@router.get("/regions", summary="Regional Statistics")
async def get_regional_statistics(db: DatabaseService = Depends(get_db_service)):
    """Get detailed regional statistics"""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get comprehensive regional stats
                cur.execute("""
                    SELECT 
                        rgn as region,
                        COUNT(*) as postcode_count,
                        COUNT(DISTINCT oslaua) as lad_count,
                        COUNT(DISTINCT osward) as ward_count,
                        COUNT(DISTINCT parish) as parish_count,
                        COUNT(DISTINCT lsoa11) as lsoa_count,
                        COUNT(DISTINCT msoa11) as msoa_count
                    FROM onspd 
                    WHERE rgn IS NOT NULL 
                    GROUP BY rgn 
                    ORDER BY postcode_count DESC
                """)
                regional_stats = [dict(row) for row in cur.fetchall()]
                
                # Get place name statistics by region
                cur.execute("""
                    SELECT 
                        region,
                        COUNT(*) as place_count,
                        COUNT(DISTINCT type) as place_types,
                        COUNT(DISTINCT local_type) as local_place_types
                    FROM os_open_names 
                    WHERE region IS NOT NULL 
                    GROUP BY region 
                    ORDER BY place_count DESC
                """)
                place_stats = [dict(row) for row in cur.fetchall()]
                
                return {
                    "regional_statistics": regional_stats,
                    "place_statistics": place_stats,
                    "summary": {
                        "total_regions": len(regional_stats),
                        "total_postcodes": sum(row['postcode_count'] for row in regional_stats),
                        "total_lads": sum(row['lad_count'] for row in regional_stats),
                        "total_places": sum(row['place_count'] for row in place_stats)
                    }
                }
    except Exception as e:
        logger.error(f"Error getting regional statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve regional statistics")

@router.get("/postcode-analysis", summary="Postcode Distribution Analysis")
async def get_postcode_analysis(db: DatabaseService = Depends(get_db_service)):
    """Get postcode distribution and analysis"""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get postcode length distribution
                cur.execute("""
                    SELECT 
                        LENGTH(pcds) as postcode_length,
                        COUNT(*) as count
                    FROM onspd 
                    GROUP BY LENGTH(pcds)
                    ORDER BY postcode_length
                """)
                length_distribution = [dict(row) for row in cur.fetchall()]
                
                # Get postcode area distribution (first 1-2 characters)
                cur.execute("""
                    SELECT 
                        LEFT(pcds, 2) as postcode_area,
                        COUNT(*) as count
                    FROM onspd 
                    GROUP BY LEFT(pcds, 2)
                    ORDER BY count DESC
                    LIMIT 20
                """)
                area_distribution = [dict(row) for row in cur.fetchall()]
                
                # Get postcode quality analysis
                cur.execute("""
                    SELECT 
                        positional_quality_indicator,
                        COUNT(*) as count
                    FROM code_point_open 
                    WHERE positional_quality_indicator IS NOT NULL
                    GROUP BY positional_quality_indicator
                    ORDER BY count DESC
                """)
                quality_analysis = [dict(row) for row in cur.fetchall()]
                
                return {
                    "length_distribution": length_distribution,
                    "area_distribution": area_distribution,
                    "quality_analysis": quality_analysis,
                    "summary": {
                        "total_postcodes": sum(row['count'] for row in length_distribution),
                        "unique_areas": len(area_distribution),
                        "quality_levels": len(quality_analysis)
                    }
                }
    except Exception as e:
        logger.error(f"Error getting postcode analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve postcode analysis")

@router.get("/health", summary="Analytics Health Check")
async def analytics_health_check(db: DatabaseService = Depends(get_db_service)):
    """Check the health of the analytics API"""
    try:
        # Test basic database connectivity
        stats = db.get_statistics()
        return {
            "status": "healthy",
            "analytics": "operational",
            "database": "connected",
            "datasets_available": len(stats) > 0
        }
    except Exception as e:
        logger.error(f"Analytics health check failed: {e}")
        raise HTTPException(status_code=503, detail="Analytics service unhealthy") 