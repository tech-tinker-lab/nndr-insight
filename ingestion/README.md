# NNDR Insight Data Ingestion Pipeline

This directory contains the organized ingestion scripts for the NNDR Insight data pipeline.

## Directory Structure

```
ingestion/
├── scripts/          # Working ingestion scripts
├── archive/          # Archived/old scripts
└── docs/            # Documentation and guides
```

## Working Ingestion Scripts

### Reference Datasets
- `ingest_os_open_uprn.py` - OS Open UPRN (Unique Property Reference Numbers)
- `ingest_code_point_open.py` - Code Point Open (Postcode data)
- `ingest_onspd.py` - ONSPD (Office for National Statistics Postcode Directory)

### Address Datasets
- `ingest_os_open_names.py` - OS Open Names (Address data)

### Street Datasets
- `ingest_os_open_map_local.py` - OS Open Map Local (Street data)
- `ingest_os_open_usrn.py` - OS Open USRN (Unique Street Reference Numbers)

### NNDR Datasets
- `ingest_nndr_properties.py` - NNDR Properties data
- `ingest_nndr_ratepayers.py` - NNDR Ratepayers data
- `ingest_valuations.py` - Valuation data

## Master Script

### `run_all_ingestion.py`

This script runs all ingestion scripts in the correct order with proper error handling and logging.

**Usage:**
```bash
# Run all ingestion scripts
python run_all_ingestion.py

# Skip specific categories
python run_all_ingestion.py --skip-reference
python run_all_ingestion.py --skip-address
python run_all_ingestion.py --skip-street
python run_all_ingestion.py --skip-nndr

# Run only specific categories
python run_all_ingestion.py --skip-address --skip-street --skip-nndr
```

**Features:**
- Automatic logging to timestamped files
- Error handling and reporting
- Progress tracking
- Summary report at the end

## Setup Requirements

1. **Database Connection**: Ensure your `.env` file in `db_setup/` is configured for your PostGIS server
2. **Python Dependencies**: Install required packages:
   ```bash
   pip install sqlalchemy python-dotenv psycopg2-binary pandas
   ```
3. **Data Files**: Place your data files in the appropriate directories as expected by each script

## Running Individual Scripts

Each script can be run independently:

```bash
cd ingestion/scripts
python ingest_os_open_uprn.py
python ingest_code_point_open.py
# etc.
```

## Logging

All scripts generate logs with timestamps:
- `ingestion_YYYYMMDD_HHMMSS.log` - Master script logs
- Individual script logs (if implemented)

## Troubleshooting

1. **Database Connection Issues**: Check your `.env` file and ensure PostGIS is running
2. **Missing Data Files**: Verify data files are in the expected locations
3. **Permission Issues**: Ensure scripts have execute permissions
4. **Memory Issues**: Some scripts may require significant memory for large datasets

## Archive

The `archive/` directory contains:
- Old/experimental versions of scripts
- Deprecated approaches
- Test scripts
- Comparison documents

## Documentation

The `docs/` directory contains:
- Detailed guides for each dataset
- Performance comparisons
- Troubleshooting guides
- Best practices 