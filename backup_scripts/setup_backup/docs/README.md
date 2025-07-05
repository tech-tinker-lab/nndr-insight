# Database Scripts

This directory contains database initialization and setup scripts for the NNDR Insight project.

## Configuration

All scripts now use environment variables for database connection settings. Create a `.env` file in the `backend` directory with your database configuration:

```bash
# Copy the example file
cp env.example .env

# Edit .env with your actual database settings
```

### Environment Variables

- `PGUSER`: Database username (default: nndr)
- `PGPASSWORD`: Database password (default: nndrpass)
- `PGHOST`: Database host (default: localhost)
- `PGPORT`: Database port (default: 5432)
- `PGDATABASE`: Database name (default: nndr_db)

## Scripts

### 1. init_db.py

Initializes the database with the core NNDR schema and PostGIS support.

**Usage:**
```bash
# Normal initialization (creates database if it doesn't exist)
python init_db.py

# Drop and recreate database
python init_db.py --drop-recreate
```

**Features:**
- Creates database if it doesn't exist
- Enables PostGIS extension
- Creates core NNDR tables (properties, ratepayers, valuations, etc.)
- Creates geospatial tables (gazetteer, os_open_uprn, etc.)

### 2. setup_db.py

Sets up a comprehensive database schema with all tables and spatial indexes.

**Usage:**
```bash
# Normal setup (creates database if it doesn't exist)
python setup_db.py

# Drop and recreate database
python setup_db.py --drop-recreate
```

**Features:**
- Creates database if it doesn't exist
- Enables PostGIS extension
- Creates comprehensive schema with staging tables
- Adds spatial indexes for geospatial queries

### 3. add_missing_tables.py

Adds missing tables to an existing database without dropping it.

**Usage:**
```bash
python add_missing_tables.py
```

**Features:**
- Safe operation - never drops existing data
- Adds only missing tables
- Useful for schema updates

### 4. create_fresh_db.py

Creates a complete database schema with all tables and indexes in one go. This is the recommended script for setting up a fresh database.

**Usage:**
```bash
# Create fresh database with all tables
python create_fresh_db.py

# Drop and recreate database with all tables
python create_fresh_db.py --drop-recreate
```

**Features:**
- Creates all tables from both init_db.py and setup_db.py
- Includes all staging tables for data ingestion
- Adds spatial indexes for geospatial queries
- Adds performance indexes for common queries
- Enables PostGIS extension
- Comprehensive schema in one script

## Command Line Arguments

### --drop-recreate

When provided, this argument will:
1. Drop the existing database (if it exists)
2. Create a new database
3. Initialize the schema

**Warning:** This will delete all existing data in the database.

## Examples

### Development Setup
```bash
# First time setup
cp env.example .env
# Edit .env with your settings
python create_fresh_db.py
```

### Production Setup
```bash
# Create production database
PGDATABASE=nndr_prod python create_fresh_db.py
```

### Testing Setup
```bash
# Create test database
PGDATABASE=nndr_test python create_fresh_db.py --drop-recreate
```

### Schema Updates
```bash
# Add new tables without affecting existing data
python add_missing_tables.py
```

## Dependencies

Make sure you have the required Python packages installed:

```bash
pip install sqlalchemy psycopg2-binary python-dotenv
```

## Troubleshooting

### Database Connection Issues
1. Check your `.env` file configuration
2. Ensure PostgreSQL is running
3. Verify database user permissions
4. Check firewall settings

### Permission Errors
Make sure your database user has:
- CREATE DATABASE permission (for init_db.py and setup_db.py)
- CREATE permission on the target database
- USAGE permission on the postgis extension

### Environment File Not Found
The scripts look for `.env` in the `backend` directory. Make sure:
1. The file exists: `backend/.env`
2. The file has the correct format
3. You're running the scripts from the correct directory 