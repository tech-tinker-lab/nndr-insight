# NNDR Insight Geospatial API

A comprehensive REST API for UK geospatial datasets including UPRNs, postcodes, place names, and administrative boundaries.

## Overview

This API provides access to multiple UK geospatial datasets that have been ingested and processed:

- **OS Open UPRN**: Unique Property Reference Numbers with coordinates
- **Code-Point Open**: Postcode to coordinate mapping
- **ONSPD**: ONS Postcode Directory with administrative geographies
- **OS Open Names**: Place names and settlements
- **LAD Boundaries**: Local Authority District boundaries
- **OS Open Map Local**: Building footprints and spatial features

## Quick Start

### 1. Start the API Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test the API

```bash
python test_api.py
```

### 3. Access the API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Base URL
```
http://localhost:8000/api
```

### Geospatial Endpoints

#### Overview
- `GET /geospatial/` - API overview and available endpoints

#### Statistics & Information
- `GET /geospatial/statistics` - Get comprehensive database statistics
- `GET /geospatial/datasets` - Get information about all datasets
- `GET /geospatial/health` - Health check

#### Geocoding & Search
- `POST /geospatial/geocode` - Geocode addresses and postcodes
- `POST /geospatial/search` - Search for properties
- `GET /geospatial/postcodes/{postcode}` - Get postcode details
- `GET /geospatial/uprn/{uprn}` - Get UPRN details

#### Spatial Queries
- `POST /geospatial/spatial` - Spatial queries around points
- `GET /geospatial/boundaries` - Get LAD boundaries

### Analytics Endpoints

#### Overview
- `GET /analytics/` - Analytics API overview

#### Data Analysis
- `GET /analytics/coverage` - Data coverage analysis
- `GET /analytics/density` - Property density analysis
- `GET /analytics/regions` - Regional statistics
- `GET /analytics/postcode-analysis` - Postcode distribution analysis
- `GET /analytics/health` - Health check

## Usage Examples

### 1. Geocode an Address

```bash
curl -X POST "http://localhost:8000/api/geospatial/geocode" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "London",
    "limit": 5
  }'
```

### 2. Search Properties by Postcode

```bash
curl -X POST "http://localhost:8000/api/geospatial/search" \
  -H "Content-Type: application/json" \
  -d '{
    "postcode": "SW1A",
    "limit": 10
  }'
```

### 3. Spatial Query Around a Point

```bash
curl -X POST "http://localhost:8000/api/geospatial/spatial" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 51.5074,
    "longitude": -0.1278,
    "radius_meters": 1000,
    "datasets": ["uprn", "names"]
  }'
```

### 4. Get Database Statistics

```bash
curl "http://localhost:8000/api/geospatial/statistics"
```

### 5. Get Regional Coverage Analysis

```bash
curl "http://localhost:8000/api/analytics/coverage"
```

### 6. Get Postcode Details

```bash
curl "http://localhost:8000/api/geospatial/postcodes/SW1A1AA"
```

## Request/Response Models

### GeocodeRequest
```json
{
  "query": "string",
  "limit": 10
}
```

### SpatialQueryRequest
```json
{
  "latitude": 51.5074,
  "longitude": -0.1278,
  "radius_meters": 1000,
  "datasets": ["uprn", "names", "map_local"]
}
```

### PropertySearchRequest
```json
{
  "postcode": "SW1A",
  "address": "Buckingham Palace",
  "uprn": 123456789,
  "limit": 50
}
```

## Response Examples

### Geocoding Response
```json
{
  "query": "London",
  "results": [
    {
      "source": "os_names",
      "name": "London",
      "type": "PopulatedPlace",
      "longitude": -0.1278,
      "latitude": 51.5074,
      "populated_place": "London",
      "district_borough": "City of London",
      "county_unitary": "Greater London",
      "region": "London",
      "country": "England"
    }
  ],
  "total_found": 1
}
```

### Statistics Response
```json
{
  "total_properties": 45000000,
  "total_postcodes": 1700000,
  "total_places": 800000000,
  "coverage_by_region": {
    "London": 250000,
    "South East": 1800000,
    "North West": 1200000
  },
  "last_updated": "2025-01-01T12:00:00"
}
```

### Spatial Query Response
```json
{
  "query": {
    "latitude": 51.5074,
    "longitude": -0.1278,
    "radius_meters": 1000,
    "datasets": ["uprn", "names"]
  },
  "results": {
    "uprns": [
      {
        "uprn": 123456789,
        "latitude": 51.5074,
        "longitude": -0.1278,
        "distance_meters": 0.0
      }
    ],
    "places": [
      {
        "os_id": "123456",
        "name1": "Buckingham Palace",
        "type": "PopulatedPlace",
        "distance_meters": 150.5
      }
    ]
  }
}
```

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (resource not found)
- `500` - Internal Server Error
- `503` - Service Unavailable (database connection issues)

Error responses include a detail message:

```json
{
  "detail": "Failed to geocode address"
}
```

## Performance Considerations

- **Large Datasets**: Some endpoints may return large datasets. Use pagination parameters where available.
- **Spatial Queries**: Spatial queries are computationally expensive. Limit radius and use appropriate indexes.
- **Caching**: Consider implementing caching for frequently accessed data.
- **Connection Pooling**: The API uses connection pooling for database efficiency.

## Development

### Running Tests
```bash
python test_api.py
```

### Adding New Endpoints
1. Create new router in `app/routers/`
2. Add models in `app/models.py`
3. Update `app/main.py` to include the router
4. Add tests to `test_api.py`

### Database Schema
The API connects to a PostgreSQL database with PostGIS extension. Key tables:

- `os_open_uprn` - UPRN data
- `code_point_open` - Postcode data
- `onspd` - ONS Postcode Directory
- `os_open_names` - Place names
- `lad_boundaries` - Administrative boundaries
- `os_open_map_local` - Map features

## Environment Variables

The API uses the following environment variables:

```bash
PGUSER=nndr
PGPASSWORD=nndrpass
PGHOST=localhost
PGPORT=5432
PGDATABASE=nndr_db
```

## Dependencies

Key dependencies:
- FastAPI
- SQLAlchemy
- psycopg2-binary
- geoalchemy2
- uvicorn

See `requirements.txt` for complete list.

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the test script for usage examples
3. Check database connectivity and data availability
4. Review server logs for detailed error messages 