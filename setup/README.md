# NNDR Insight - Setup Directory

This directory contains all database setup, configuration, and utility scripts for the NNDR Insight system. The setup has been organized into logical subdirectories for better maintainability and clarity.

## Directory Structure

```
setup/
├── database/          # Core database setup and migration files
├── config/           # Configuration files
├── scripts/          # Utility and ingestion scripts
└── docs/            # Documentation files
```

## Database Setup (`database/`)

Contains all core database-related files:

### Core Files
- `migration_tracker.py` - Migration system for managing database schema changes
- `run_migrations.py` - CLI tool for running migrations
- `run_complete_db_setup.py` - Complete database setup script
- `create_fresh_db.py` - Fresh database creation
- `init_db.py` - Database initialization
- `setup_db.py` - Database setup utilities
- `db_config.py` - Database configuration

### Schema Files
- `master_gazetteer_schema.sql` - Master gazetteer table schema
- `forecasting_system_schema.sql` - Business rate forecasting system schema

### Data Population
- `populate_master_gazetteer.py` - Populates the master gazetteer table
- `add_missing_tables.py` - Adds missing tables to existing database

## Configuration (`config/`)

Contains configuration files:
- `env.example` - Environment variables template
- `postgresql.conf` - PostgreSQL configuration

## Scripts (`scripts/`)

Contains utility and data ingestion scripts:

### Data Ingestion Scripts
- `ingest_*.py` - Various data ingestion scripts for different data sources
- `ingest_gazetteer.py` - Gazetteer data ingestion
- `ingest_nndr_*.py` - NNDR-specific data ingestion

### Diagnostic Scripts
- `generate_sample_nndr.py` - Generate sample NNDR data
- `count_null_latlong_properties.py` - Data quality checks
- `debug_null_latlong.py` - Debug scripts

### Quality Assurance
- `data_quality_checks.py` - Data quality validation
- `fix_database.py` - Database fixes

## Documentation (`docs/`)

Contains all setup-related documentation:
- `DATABASE_SETUP.md` - Database setup instructions
- `MIGRATION_README.md` - Migration system documentation
- `MIGRATION_IMPLEMENTATION_SUMMARY.md` - Migration implementation details
- `FRESH_DB_SETUP.md` - Fresh database setup guide
- `DATABASE_FIX.md` - Database fix documentation

## Quick Start

### 1. Set up Environment
```bash
cd setup/config
cp env.example .env
# Edit .env with your database credentials
```

### 2. Run Complete Database Setup
```bash
cd setup/database
python run_complete_db_setup.py
```

### 3. Run Migrations (if needed)
```bash
cd setup/database
python run_migrations.py --list
python run_migrations.py --run-all
```

### 4. Ingest Data
```bash
cd setup/scripts
python ingest_gazetteer.py
python ingest_nndr_properties.py
```

## Migration System

The migration system provides:
- **Sequential Execution**: Migrations run in order
- **Idempotent Operations**: Safe to run multiple times
- **Error Handling**: Rollback on failures
- **Progress Tracking**: Detailed logging and status
- **CLI Interface**: Easy command-line management

### Migration Commands
```bash
# List all migrations
python run_migrations.py --list

# Run all pending migrations
python run_migrations.py --run-all

# Run specific migration
python run_migrations.py --run 001

# Check migration status
python run_migrations.py --status
```

## Data Sources

The system ingests data from multiple sources:
- **CodePoint Open**: Postcode data
- **OS Open Names**: Geographic names
- **OS Open MapLocal**: Detailed mapping data
- **NNDR Data**: Business rates data
- **LAD Boundaries**: Local authority boundaries

## Best Practices

1. **Always backup** before running migrations
2. **Test migrations** in development first
3. **Use the migration system** for all schema changes
4. **Check data quality** after ingestion
5. **Document changes** in the docs directory

## Troubleshooting

### Common Issues
1. **Database connection errors**: Check `.env` configuration
2. **Migration failures**: Check logs in `setup/database/migration_logs/`
3. **Data quality issues**: Run diagnostic scripts in `setup/scripts/`

### Getting Help
- Check the documentation in `setup/docs/`
- Review migration logs for detailed error information
- Use diagnostic scripts to identify data issues

## Development Workflow

1. **Schema Changes**: Create new migration files
2. **Data Ingestion**: Add new ingestion scripts
3. **Testing**: Use diagnostic scripts to validate
4. **Documentation**: Update relevant docs
5. **Deployment**: Run migrations in order

This organization makes the setup process more maintainable and easier to understand for new team members. 