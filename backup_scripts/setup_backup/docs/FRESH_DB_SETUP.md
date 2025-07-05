# Fresh Database Setup Guide

## Overview
The `create_fresh_db.py` script is a comprehensive database initialization script that creates all tables, indexes, and extensions needed for the NNDR Insight project in one go.

## What It Creates

### 🏗️ Core NNDR Tables
- **properties** - Main property records with addresses and categories
- **ratepayers** - Ratepayer information linked to properties
- **valuations** - Current property valuations
- **historic_valuations** - Historical valuation records
- **categories** - Property category codes and descriptions

### 🗺️ Geospatial Tables
- **gazetteer** - Property location data with coordinates
- **os_open_uprn** - OS Open UPRN data with coordinates
- **code_point_open** - Postcode to coordinate mapping
- **onspd** - ONS Postcode Directory data
- **os_open_names** - OS Open Names with spatial geometry
- **lad_boundaries** - Local Authority District boundaries
- **os_open_map_local** - OS Open Map Local features

### 📊 Staging Tables
- **gazetteer_staging** - Temporary UPRN data
- **os_open_uprn_staging** - Temporary OS UPRN data
- **code_point_open_staging** - Temporary postcode data
- **onspd_staging** - Temporary ONSPD data
- **os_open_map_local_staging** - Temporary map features

### ⚡ Performance Features
- **PostGIS extension** - Enables spatial queries
- **Spatial indexes** - GIST indexes on geometry columns
- **Performance indexes** - Indexes on commonly queried columns

## Quick Start

### 1. Environment Setup
```bash
cd backend
cp env.example .env
# Edit .env with your database settings
```

### 2. Create Fresh Database
```bash
# Create database and all tables
python db/create_fresh_db.py

# Or drop and recreate everything
python db/create_fresh_db.py --drop-recreate
```

### 3. Verify Setup
```bash
python db/test_config.py
```

## Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# Database Configuration
PGUSER=nndr
PGPASSWORD=nndrpass
PGHOST=localhost
PGPORT=5432
PGDATABASE=nndr_db
```

## Command Line Options

### Normal Operation
```bash
python db/create_fresh_db.py
```
- Creates database if it doesn't exist
- Creates all tables and indexes
- Preserves existing data

### Drop and Recreate
```bash
python db/create_fresh_db.py --drop-recreate
```
- Drops existing database
- Creates fresh database with all tables
- **Warning**: This will delete all existing data

## Database Schema Summary

| Table Category | Tables | Purpose |
|---------------|--------|---------|
| Core NNDR | 5 tables | Business rates and property data |
| Geospatial | 7 tables | Location and mapping data |
| Staging | 5 tables | Temporary data for ingestion |
| **Total** | **17 tables** | Complete NNDR Insight schema |

## Indexes Created

### Spatial Indexes
- `os_open_names_geom_idx` - Spatial index on OS Open Names
- `lad_boundaries_geom_idx` - Spatial index on LAD boundaries
- `os_open_map_local_geom_idx` - Spatial index on map features

### Performance Indexes
- `properties_ba_reference_idx` - Property reference lookups
- `properties_postcode_idx` - Postcode searches
- `ratepayers_property_id_idx` - Ratepayer lookups
- `valuations_property_id_idx` - Valuation lookups
- `gazetteer_property_id_idx` - Gazetteer lookups
- `code_point_open_postcode_idx` - Postcode coordinate lookups

## Troubleshooting

### Database Connection Issues
1. Check your `.env` file exists and has correct settings
2. Ensure PostgreSQL is running
3. Verify database user has proper permissions

### Permission Errors
Make sure your database user has:
- `CREATE DATABASE` permission
- `CREATE` permission on the target database
- `USAGE` permission on the postgis extension

### Common Issues
- **"relation does not exist"** - Run the script to create tables
- **"extension postgis does not exist"** - Install PostGIS extension
- **"permission denied"** - Check database user permissions

## Next Steps

After running the script:

1. **Test the API**:
   ```bash
   python start_api.py
   ```

2. **Load data** using the ingestion scripts in the `ingest/` directory

3. **Verify data** using the quality scripts in the `quality/` directory

## Comparison with Other Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `create_fresh_db.py` | Complete schema setup | **Recommended for new installations** |
| `init_db.py` | Basic NNDR tables | Legacy, use create_fresh_db.py instead |
| `setup_db.py` | Extended schema | Legacy, use create_fresh_db.py instead |
| `add_missing_tables.py` | Add missing tables | Schema updates only |

The `create_fresh_db.py` script is the recommended choice for all new database setups as it includes everything from the other scripts plus additional optimizations. 