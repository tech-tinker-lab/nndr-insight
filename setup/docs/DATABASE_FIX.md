# Database Fix Guide

## Issue
The API is returning errors because it's trying to access columns that don't exist in the database. The error shows:
```
relation "properties" does not exist
```

## Solution

### Step 1: Create Environment File
First, create a `.env` file in the `backend` directory:

```bash
cd backend
cp env.example .env
```

Edit the `.env` file with your database settings:
```bash
PGUSER=nndr
PGPASSWORD=nndrpass
PGHOST=localhost
PGPORT=5432
PGDATABASE=nndr_db
```

### Step 2: Initialize Database
If the database doesn't exist, initialize it:

```bash
# Create database and tables
python db/init_db.py

# Or if you want to drop and recreate
python db/init_db.py --drop-recreate
```

### Step 3: Test Database Connection
Run the database test script:

```bash
python fix_database.py
```

This script will:
- Test the database connection
- Verify the database is accessible

### Step 4: Start the API
Now you can start your API server:

```bash
python start_api.py
```

## What Was Fixed

### API Code Issues
1. **Fixed column names in API queries**:
   - Changed `property_ref` to `ba_reference`
   - Changed `address` to `property_address`
   - Changed `category_code` to `property_category_code`
   - Changed `description` to `property_description`
   - Removed `latitude` and `longitude` (not in original schema)

2. **Fixed type annotations**:
   - Fixed type annotations in `tables.py`
   - Updated database connection to use environment variables
   - Fixed parameter type issues

### Files Modified
- `backend/app/routers/tables.py` - Fixed type annotations
- `backend/app/routers/upload.py` - Fixed column names and database connection
- `backend/fix_database.py` - Updated to only test connection

## Troubleshooting

### Database Connection Issues
1. Check your `.env` file exists and has correct settings
2. Ensure PostgreSQL is running
3. Verify database user has proper permissions

### Permission Errors
Make sure your database user has:
- CREATE permission on the database
- ALTER permission on tables
- USAGE permission on the postgis extension

### Still Getting Errors?
1. Check the database logs for specific error messages
2. Verify the database exists: `python db/test_config.py`
3. Check if tables exist by connecting to the database directly

## API Endpoints Fixed

The following endpoints should now work:
- `GET /api/nndr/properties` - Returns property data
- `GET /api/properties` - Returns property data with search
- `GET /api/ratepayers` - Returns ratepayer data
- `GET /api/valuations` - Returns valuation data
- `GET /api/historic_valuations` - Returns historic valuation data 