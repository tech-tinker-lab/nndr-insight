import os
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.connection_string = (
            f"postgresql://{os.getenv('PGUSER', 'nndr')}:{os.getenv('PGPASSWORD', 'nndrpass')}@"
            f"{os.getenv('PGHOST', 'localhost')}:{os.getenv('PGPORT', '5432')}/"
            f"{os.getenv('PGDATABASE', 'nndr_test')}"
        )
        self.engine = create_engine(self.connection_string)
    
    def get_connection(self):
        """Get a database connection with RealDictCursor for dictionary-like results"""
        return psycopg2.connect(self.connection_string, cursor_factory=RealDictCursor)
    
    def get_statistics(self) -> Dict:
        """Get overall statistics about the database"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get counts from each table
                    stats: Dict[str, Any] = {}
                    
                    # UPRN count
                    try:
                        cur.execute("SELECT COUNT(*) FROM os_open_uprn")
                        result = cur.fetchone()
                        stats['total_uprns'] = result[0] if result else 0
                    except Exception:
                        stats['total_uprns'] = 0
                    
                    # Postcodes count
                    try:
                        cur.execute("SELECT COUNT(*) FROM code_point_open")
                        result = cur.fetchone()
                        stats['total_postcodes'] = result[0] if result else 0
                    except Exception:
                        stats['total_postcodes'] = 0
                    
                    # ONSPD count
                    try:
                        cur.execute("SELECT COUNT(*) FROM onspd")
                        result = cur.fetchone()
                        stats['total_onspd'] = result[0] if result else 0
                    except Exception:
                        stats['total_onspd'] = 0
                    
                    # OS Names count
                    try:
                        cur.execute("SELECT COUNT(*) FROM os_open_names")
                        result = cur.fetchone()
                        stats['total_places'] = result[0] if result else 0
                    except Exception:
                        stats['total_places'] = 0
                    
                    # LAD boundaries count
                    try:
                        cur.execute("SELECT COUNT(*) FROM lad_boundaries")
                        result = cur.fetchone()
                        stats['total_lads'] = result[0] if result else 0
                    except Exception:
                        stats['total_lads'] = 0
                    
                    # Map Local features count
                    try:
                        cur.execute("SELECT COUNT(*) FROM os_open_map_local")
                        result = cur.fetchone()
                        stats['total_map_features'] = result[0] if result else 0
                    except Exception:
                        stats['total_map_features'] = 0
                    
                    # NNDR Properties count
                    try:
                        cur.execute("SELECT COUNT(*) FROM properties")
                        result = cur.fetchone()
                        stats['total_properties'] = result[0] if result else 0
                    except Exception:
                        stats['total_properties'] = 0
                    
                    # Coverage by region (using ONSPD)
                    try:
                        cur.execute("""
                            SELECT rgn, COUNT(*) as count 
                            FROM onspd 
                            WHERE rgn IS NOT NULL 
                            GROUP BY rgn 
                            ORDER BY count DESC
                        """)
                        coverage_results = cur.fetchall()
                        stats['coverage_by_region'] = {row['rgn']: row['count'] for row in coverage_results}
                    except Exception:
                        stats['coverage_by_region'] = {}
                    
                    stats['last_updated'] = datetime.now().isoformat()
                    
                    return stats
                    
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            raise
    
    def geocode_address(self, query: str, limit: int = 10) -> List[Dict]:
        """Geocode an address or postcode using multiple datasets"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Search in OS Open Names
                    cur.execute("""
                        SELECT 
                            'os_names' as source,
                            name1 as name,
                            type,
                            local_type,
                            geometry_x as longitude,
                            geometry_y as latitude,
                            populated_place,
                            district_borough,
                            county_unitary,
                            region,
                            country
                        FROM os_open_names 
                        WHERE name1 ILIKE %s OR name2 ILIKE %s
                        ORDER BY 
                            CASE 
                                WHEN name1 ILIKE %s THEN 1
                                WHEN name1 ILIKE %s THEN 2
                                ELSE 3
                            END,
                            most_detail_view_res ASC
                        LIMIT %s
                    """, (f"%{query}%", f"%{query}%", query, f"{query}%", limit))
                    
                    os_names_results = cur.fetchall()
                    
                    # Search in Code-Point Open
                    cur.execute("""
                        SELECT 
                            'codepoint' as source,
                            postcode as name,
                            'Postcode' as type,
                            'Postcode' as local_type,
                            NULL as longitude,
                            NULL as latitude,
                            NULL as populated_place,
                            NULL as district_borough,
                            NULL as county_unitary,
                            NULL as region,
                            country_code as country
                        FROM code_point_open 
                        WHERE postcode ILIKE %s
                        LIMIT %s
                    """, (f"%{query}%", limit))
                    
                    codepoint_results = cur.fetchall()
                    
                    # Combine and rank results
                    all_results = []
                    
                    # Add OS Names results first (higher priority)
                    for row in os_names_results:
                        all_results.append(dict(row))
                    
                    # Add Code-Point results
                    for row in codepoint_results:
                        all_results.append(dict(row))
                    
                    return all_results[:limit]
                    
        except Exception as e:
            logger.error(f"Error geocoding address: {e}")
            raise
    
    def search_properties(self, postcode: Optional[str] = None, 
                         address: Optional[str] = None, 
                         uprn: Optional[int] = None,
                         limit: int = 50) -> List[Dict]:
        """Search for properties using various criteria"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    if uprn:
                        # Direct UPRN lookup
                        cur.execute("""
                            SELECT 
                                uprn,
                                x_coordinate,
                                y_coordinate,
                                latitude,
                                longitude,
                                'os_open_uprn' as source
                            FROM os_open_uprn 
                            WHERE uprn = %s
                        """, (uprn,))
                        
                    elif postcode:
                        # Postcode-based search
                        cur.execute("""
                            SELECT 
                                pcds as postcode,
                                lat as latitude,
                                long as longitude,
                                oslaua as local_authority,
                                osward as ward,
                                parish,
                                lsoa11,
                                msoa11,
                                rgn as region,
                                'onspd' as source
                            FROM onspd 
                            WHERE pcds ILIKE %s
                            ORDER BY pcds
                            LIMIT %s
                        """, (f"%{postcode}%", limit))
                        
                    elif address:
                        # Address-based search using OS Names
                        cur.execute("""
                            SELECT 
                                os_id,
                                name1,
                                type,
                                local_type,
                                geometry_x as longitude,
                                geometry_y as latitude,
                                populated_place,
                                district_borough,
                                county_unitary,
                                region,
                                country,
                                'os_open_names' as source
                            FROM os_open_names 
                            WHERE name1 ILIKE %s
                            ORDER BY most_detail_view_res ASC
                            LIMIT %s
                        """, (f"%{address}%", limit))
                    
                    else:
                        return []
                    
                    return [dict(row) for row in cur.fetchall()]
                    
        except Exception as e:
            logger.error(f"Error searching properties: {e}")
            raise
    
    def spatial_query(self, latitude: float, longitude: float, 
                     radius_meters: float = 1000,
                     datasets: Optional[List[str]] = None) -> Dict:
        """Perform spatial queries around a point"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    results = {}
                    
                    # Convert lat/lon to British National Grid (EPSG:27700)
                    cur.execute("""
                        SELECT ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326), 27700) as point
                    """, (longitude, latitude))
                    result = cur.fetchone()
                    point = result[0] if result else None
                    
                    # Search UPRNs within radius
                    if not datasets or 'uprn' in datasets:
                        cur.execute("""
                            SELECT 
                                uprn,
                                x_coordinate,
                                y_coordinate,
                                latitude,
                                longitude,
                                ST_Distance(ST_Transform(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326), 27700), %s) as distance_meters
                            FROM os_open_uprn 
                            WHERE ST_DWithin(
                                ST_Transform(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326), 27700), 
                                %s, 
                                %s
                            )
                            ORDER BY distance_meters
                            LIMIT 100
                        """, (point, point, radius_meters))
                        results['uprns'] = [dict(row) for row in cur.fetchall()]
                    
                    # Search OS Names within radius
                    if not datasets or 'names' in datasets:
                        cur.execute("""
                            SELECT 
                                os_id,
                                name1,
                                type,
                                local_type,
                                geometry_x,
                                geometry_y,
                                populated_place,
                                district_borough,
                                county_unitary,
                                ST_Distance(geom, %s) as distance_meters
                            FROM os_open_names 
                            WHERE ST_DWithin(geom, %s, %s)
                            ORDER BY distance_meters
                            LIMIT 100
                        """, (point, point, radius_meters))
                        results['places'] = [dict(row) for row in cur.fetchall()]
                    
                    # Search Map Local features within radius
                    if not datasets or 'map_local' in datasets:
                        cur.execute("""
                            SELECT 
                                id,
                                fid,
                                theme,
                                descriptivegroup,
                                descriptiveterm,
                                fclass,
                                ST_Distance(geometry, %s) as distance_meters
                            FROM os_open_map_local 
                            WHERE ST_DWithin(geometry, %s, %s)
                            ORDER BY distance_meters
                            LIMIT 100
                        """, (point, point, radius_meters))
                        results['map_features'] = [dict(row) for row in cur.fetchall()]
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Error in spatial query: {e}")
            raise
    
    def get_lad_boundaries(self, lad_code: Optional[str] = None) -> List[Dict]:
        """Get Local Authority District boundaries"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    if lad_code:
                        cur.execute("""
                            SELECT 
                                id,
                                lad_code,
                                lad_name,
                                ST_AsGeoJSON(ST_Transform(geometry, 4326)) as geometry
                            FROM lad_boundaries 
                            WHERE lad_code = %s
                        """, (lad_code,))
                    else:
                        cur.execute("""
                            SELECT 
                                id,
                                lad_code,
                                lad_name,
                                ST_AsGeoJSON(ST_Transform(geometry, 4326)) as geometry
                            FROM lad_boundaries 
                            ORDER BY lad_name
                        """)
                    
                    return [dict(row) for row in cur.fetchall()]
                    
        except Exception as e:
            logger.error(f"Error getting LAD boundaries: {e}")
            raise
    
    def get_dataset_info(self) -> List[Dict]:
        """Get information about all datasets"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    datasets = [
                        {
                            'name': 'OS Open UPRN',
                            'description': 'Unique Property Reference Numbers with coordinates',
                            'table': 'os_open_uprn',
                            'source': 'Ordnance Survey'
                        },
                        {
                            'name': 'Code-Point Open',
                            'description': 'Postcode to coordinate mapping',
                            'table': 'code_point_open',
                            'source': 'Ordnance Survey'
                        },
                        {
                            'name': 'ONSPD',
                            'description': 'ONS Postcode Directory with administrative geographies',
                            'table': 'onspd',
                            'source': 'Office for National Statistics'
                        },
                        {
                            'name': 'OS Open Names',
                            'description': 'Place names and settlements',
                            'table': 'os_open_names',
                            'source': 'Ordnance Survey'
                        },
                        {
                            'name': 'LAD Boundaries',
                            'description': 'Local Authority District boundaries',
                            'table': 'lad_boundaries',
                            'source': 'Office for National Statistics'
                        },
                        {
                            'name': 'OS Open Map Local',
                            'description': 'Building footprints and spatial features',
                            'table': 'os_open_map_local',
                            'source': 'Ordnance Survey'
                        }
                    ]
                    
                    # Get record counts for each dataset
                    for dataset in datasets:
                        try:
                            cur.execute(f"SELECT COUNT(*) FROM {dataset['table']}")
                            result = cur.fetchone()
                            dataset['record_count'] = int(result[0]) if result else 0
                        except Exception:
                            dataset['record_count'] = 0
                    
                    return datasets
                    
        except Exception as e:
            logger.error(f"Error getting dataset info: {e}")
            raise
    
    def get_postcode_details(self, postcode: str) -> Dict:
        """Get comprehensive details for a postcode"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get Code-Point data
                    cur.execute("""
                        SELECT * FROM code_point_open 
                        WHERE postcode = %s
                    """, (postcode,))
                    codepoint = cur.fetchone()
                    
                    # Get ONSPD data
                    cur.execute("""
                        SELECT * FROM onspd 
                        WHERE pcds = %s
                    """, (postcode,))
                    onspd = cur.fetchone()
                    
                    # Get nearby UPRNs
                    if codepoint and codepoint['easting'] and codepoint['northing']:  # easting and northing columns
                        cur.execute("""
                            SELECT 
                                uprn,
                                latitude,
                                longitude,
                                ST_Distance(
                                    ST_Transform(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326), 27700),
                                    ST_SetSRID(ST_MakePoint(%s, %s), 27700)
                                ) as distance_meters
                            FROM os_open_uprn 
                            WHERE ST_DWithin(
                                ST_Transform(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326), 27700),
                                ST_SetSRID(ST_MakePoint(%s, %s), 27700),
                                1000
                            )
                            ORDER BY distance_meters
                            LIMIT 50
                        """, (codepoint['easting'], codepoint['northing'], codepoint['easting'], codepoint['northing']))
                        nearby_uprns = [dict(row) for row in cur.fetchall()]
                    else:
                        nearby_uprns = []
                    
                    return {
                        'postcode': postcode,
                        'codepoint': dict(codepoint) if codepoint else None,
                        'onspd': dict(onspd) if onspd else None,
                        'nearby_uprns': nearby_uprns
                    }
                    
        except Exception as e:
            logger.error(f"Error getting postcode details: {e}")
            raise 