# Database Setup Guide

## Database Configuration

The backend uses PostgreSQL with PostGIS extension for geospatial data. Here are the default database settings:

### Default Database Settings
- **Host**: localhost
- **Port**: 5432
- **Database**: nndr_test
- **Username**: nndr
- **Password**: nndrpass

### Environment Variables
Create a `.env` file in the `backend` directory with the following variables:

```env
# Database Configuration
PGUSER=nndr
PGPASSWORD=nndrpass
PGHOST=localhost
PGPORT=5432
PGDATABASE=nndr_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Logging
LOG_LEVEL=INFO
```

## Database Setup Steps

### 1. Install PostgreSQL with PostGIS
Make sure you have PostgreSQL installed with the PostGIS extension.

### 2. Create Database and Tables
Run the database setup script:

```bash
cd backend/db
python setup_db.py
```

This will:
- Create the database if it doesn't exist
- Create all required tables with spatial indexes
- Set up staging tables for data ingestion

### 3. Add Missing Tables (if needed)
If you encounter missing table errors, run:

```bash
cd backend/db
python add_missing_tables.py
```

### 4. Verify Database Connection
Test the database connection:

```bash
cd backend
python -c "from app.services.database_service import DatabaseService; db = DatabaseService(); print('Database connection successful')"
```

## Database Tables

The following tables are created:

- `os_open_uprn` - Unique Property Reference Numbers
- `code_point_open` - Postcode coordinates
- `onspd` - ONS Postcode Directory
- `os_open_names` - Place names and settlements
- `lad_boundaries` - Local Authority District boundaries
- `os_open_map_local` - Building footprints and spatial features
- `nndr_rating_list` - Business rates data
- Various staging tables for data ingestion

## Troubleshooting

### Common Issues

1. **"relation does not exist" errors**
   - Run `python add_missing_tables.py` to add missing tables
   - Or recreate the database with `python setup_db.py`

2. **Connection refused**
   - Check if PostgreSQL is running
   - Verify host, port, and credentials in `.env` file

3. **PostGIS extension not found**
   - Install PostGIS extension: `CREATE EXTENSION postgis;`

4. **Permission denied**
   - Ensure the database user has proper permissions
   - Check if the user can create databases and tables

### Database Commands

```sql
-- Check if tables exist
\dt

-- Check table structure
\d os_open_uprn

-- Check PostGIS extension
SELECT PostGIS_Version();

-- Count records in tables
SELECT 'os_open_uprn' as table_name, COUNT(*) as count FROM os_open_uprn
UNION ALL
SELECT 'code_point_open', COUNT(*) FROM code_point_open
UNION ALL
SELECT 'onspd', COUNT(*) FROM onspd
UNION ALL
SELECT 'os_open_names', COUNT(*) FROM os_open_names
UNION ALL
SELECT 'lad_boundaries', COUNT(*) FROM lad_boundaries
UNION ALL
SELECT 'os_open_map_local', COUNT(*) FROM os_open_map_local;
``` 