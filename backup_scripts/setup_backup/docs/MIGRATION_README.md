# Database Migration System

This directory contains a comprehensive database migration system similar to Liquibase, designed to manage database schema changes in a controlled and trackable manner.

## Overview

The migration system provides:
- **Sequential migration execution** - Migrations run in order
- **Migration tracking** - Records which migrations have been applied
- **Idempotent operations** - Safe to run multiple times
- **Rollback support** - Track migration history for potential rollbacks
- **Command-line interface** - Easy to use CLI for migration management

## Files

### Core Migration Files
- `run_complete_db_setup.py` - Complete database setup script (all-in-one)
- `run_migrations.py` - Command-line migration runner (Liquibase-style)
- `migration_tracker.py` - Migration tracking and management
- `db_config.py` - Database configuration and connection

### Schema Files
- `master_gazetteer_schema.sql` - Master gazetteer table schema
- `forecasting_system_schema.sql` - Forecasting system tables schema
- `create_fresh_db.py` - Original database creation script

### Data Population
- `populate_master_gazetteer.py` - Master gazetteer data population

## Quick Start

### Option 1: Complete Setup (Recommended)
Run the complete database setup in one go:

```bash
cd backend/db
python run_complete_db_setup.py
```

This will:
1. Create the database if it doesn't exist
2. Enable PostGIS extension
3. Create all tables (Core NNDR, Geospatial, Staging, Master Gazetteer, Forecasting)
4. Create all indexes
5. Optionally populate the master gazetteer

### Option 2: Liquibase-Style Migrations
Use the migration system for more control:

```bash
cd backend/db

# Create database
python run_migrations.py create-db

# Run all pending migrations
python run_migrations.py run

# Check migration status
python run_migrations.py status

# Show pending migrations
python run_migrations.py pending
```

## Migration Commands

### Basic Commands

```bash
# Create database
python run_migrations.py create-db

# Run all pending migrations
python run_migrations.py run

# Run specific migration
python run_migrations.py run --migration 001_create_core_tables

# Check migration status
python run_migrations.py status

# Show pending migrations
python run_migrations.py pending

# Reset migration tracking (development only)
python run_migrations.py reset
```

### Advanced Usage

```bash
# Force run migrations (skip checks)
python run_migrations.py run --force

# Run specific migration with force
python run_migrations.py run --migration 002_create_geospatial_tables --force
```

## Migration System Features

### 1. Migration Tracking
The system maintains a `db_migrations` table that tracks:
- Migration name and version
- Execution timestamp
- Execution time
- Success/failure status
- Error messages (if failed)

### 2. Idempotent Operations
- Migrations are tracked by name and content hash
- Already-applied migrations are skipped
- Modified migrations trigger warnings

### 3. Sequential Execution
Migrations run in this order:
1. `001_create_core_tables` - Core NNDR tables
2. `002_create_geospatial_tables` - Geospatial tables
3. `003_create_staging_tables` - Staging tables
4. `004_create_master_gazetteer` - Master gazetteer table
5. `005_create_forecasting_tables` - Forecasting system tables
6. `006_create_indexes` - Database indexes
7. `007_populate_master_gazetteer` - Data population

### 4. Error Handling
- Failed migrations are recorded with error details
- Option to continue or stop on failure
- Clear error reporting and logging

## Migration Status

### Check Current Status
```bash
python run_migrations.py status
```

Example output:
```
📊 Migration Status:
================================================================================
Migration Name                           Applied At            Status     Time (ms)
--------------------------------------------------------------------------------
001_create_core_tables                   2024-01-15 10:30:15  ✅ SUCCESS  1250
002_create_geospatial_tables             2024-01-15 10:30:18  ✅ SUCCESS  890
003_create_staging_tables                2024-01-15 10:30:20  ✅ SUCCESS  450

📈 Migration Summary:
   Total Migrations: 3
   Successful: 3
   Failed: 0
   Running: 0
   Total Execution Time: 2590ms
```

### Check Pending Migrations
```bash
python run_migrations.py pending
```

Example output:
```
📋 Pending migrations (2):
  1. 004_create_master_gazetteer
  2. 005_create_forecasting_tables
```

## Adding New Migrations

### 1. Create Migration Function
Add a new migration function to `migration_tracker.py`:

```python
def run_migration_008_add_new_table(engine):
    """Migration 008: Add new table"""
    sql = """
    CREATE TABLE IF NOT EXISTS new_table (
        id SERIAL PRIMARY KEY,
        name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text(sql))
```

### 2. Register Migration
Add to the migration registry:

```python
MIGRATION_REGISTRY = {
    # ... existing migrations ...
    "008_add_new_table": run_migration_008_add_new_table,
}
```

### 3. Add to Available Migrations
Update the available migrations list:

```python
def get_available_migrations():
    return [
        # ... existing migrations ...
        "008_add_new_table"
    ]
```

## Environment Configuration

### Database Configuration
Create a `.env` file in the `backend` directory:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nndr_insight
DB_USER=your_username
DB_PASSWORD=your_password
```

### Configuration Priority
1. Environment variables
2. `.env` file
3. Default values

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check database configuration
python test_config.py

# Verify database exists
python run_migrations.py create-db
```

#### 2. Migration Already Applied
```bash
# Check migration status
python run_migrations.py status

# Reset if needed (development only)
python run_migrations.py reset
```

#### 3. PostGIS Extension Error
```bash
# Ensure PostGIS is installed
# On Ubuntu/Debian:
sudo apt-get install postgresql-13-postgis-3

# On macOS with Homebrew:
brew install postgis
```

### Debug Mode
For detailed logging, modify the migration scripts to include debug output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

### 1. Migration Naming
- Use descriptive names: `001_create_core_tables`
- Include version numbers for ordering
- Use lowercase with underscores

### 2. Migration Content
- Make migrations idempotent (safe to run multiple times)
- Use `CREATE TABLE IF NOT EXISTS`
- Include proper error handling

### 3. Testing
- Test migrations in development first
- Use the reset command carefully
- Backup production data before running migrations

### 4. Version Control
- Commit migration files to version control
- Don't modify existing migrations (create new ones)
- Document migration purposes

## Comparison with Liquibase

| Feature | This System | Liquibase |
|---------|-------------|-----------|
| Migration Tracking | ✅ | ✅ |
| Sequential Execution | ✅ | ✅ |
| Rollback Support | ⚠️ (Manual) | ✅ |
| XML Configuration | ❌ | ✅ |
| Multiple Database Support | ⚠️ (PostgreSQL) | ✅ |
| Change Sets | ❌ | ✅ |
| Preconditions | ❌ | ✅ |
| Command Line Interface | ✅ | ✅ |

## Next Steps

1. **Run Complete Setup**: Use `run_complete_db_setup.py` for initial setup
2. **Populate Data**: Run data ingestion scripts
3. **Develop Models**: Begin forecasting model development
4. **Add Migrations**: Create new migrations as needed

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review migration logs in the `db_migrations` table
3. Test with the `test_config.py` script
4. Check database connection and permissions 