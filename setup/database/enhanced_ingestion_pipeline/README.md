# Comprehensive Data Ingestion Pipeline

## Overview

The Comprehensive Data Ingestion Pipeline is a robust, production-ready system designed to handle multiple data sources for the NNDR (National Non-Domestic Rates) Insight project. It features enhanced schema support, source tracking, duplicate detection, and performance optimization.

## Key Features

### 🎯 **Enhanced Schema Support**
- Multi-source data integration with source tracking
- Duplicate detection and resolution
- Data quality validation and scoring
- Comprehensive field mapping for all data sources

### 📊 **Data Source Types**
- **NNDR Data**: VOA compiled lists, local council data, historic valuations
- **Reference Data**: OS UPRN, CodePoint Open, ONSPD
- **Property Sales**: Land Registry, Rightmove (configurable)
- **Market Analysis**: Estates Gazette, economic indicators (configurable)

### ⚡ **Performance Optimizations**
- Parallel processing with configurable worker pools
- Chunked data processing to handle large files
- Bulk database operations with index optimization
- Memory-efficient streaming for large datasets

### 🔍 **Data Quality Framework**
- Automated duplicate detection across sources
- Coordinate validation and transformation
- Postcode format validation
- Rateable value range checking
- Source confidence scoring

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│  Pipeline Config │───▶│  Data Processors │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Quality Rules  │◀───│  Validation      │◀───│  Duplicate      │
│                 │    │  Framework       │    │  Detection      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Enhanced       │◀───│  Bulk Insertion  │◀───│  Source Tracking│
│  Schema         │    │  Engine          │    │  & Metadata     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+ with PostGIS extension
- Enhanced database schema (run `enhanced_schema_update.py` first)

### Setup
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure database connection**:
   ```bash
   cp ../db_config.py .
   # Edit db_config.py with your database credentials
   ```

3. **Verify enhanced schema**:
   ```bash
   python ../enhanced_schema_update.py
   ```

## Usage

### Basic Usage

```bash
# Show pipeline information
python run_pipeline.py --info

# Run dry-run to see what would be processed
python run_pipeline.py --dry-run

# Run complete ingestion
python run_pipeline.py

# Run with custom data directory
python run_pipeline.py --data-dir /path/to/data

# Run specific source type only
python run_pipeline.py --source-type nndr

# Run with debug logging
python run_pipeline.py --log-level DEBUG
```

### Advanced Usage

```bash
# Process only reference data sources
python run_pipeline.py --source-type reference

# Process with custom configuration
python run_pipeline.py --data-dir /custom/data/path --log-level INFO
```

## Configuration

### Data Source Configuration

The pipeline uses a centralized configuration system in `pipeline_config.py`:

```python
ENHANCED_DATA_SOURCES = {
    'voa_2023': {
        'priority': 1,                    # Processing priority
        'description': 'VOA 2023 NNDR Compiled List',
        'file_pattern': 'uk-englandwales-ndr-2023-*.csv',
        'format': 'pipe_delimited',       # Data format
        'coordinate_system': 'wgs84',     # Coordinate system
        'quality_score': 0.95,           # Source quality score
        'enabled': True,                 # Enable/disable source
        'field_mapping': {               # Field mapping configuration
            'ba_reference': 2,
            'property_address': 6,
            # ... more mappings
        }
    }
}
```

### Performance Configuration

```python
PERFORMANCE_CONFIG = {
    'batch_size': 10000,           # Records per batch
    'chunk_size': 50000,           # Records per chunk
    'max_workers': 4,              # Parallel workers
    'memory_limit_gb': 8,          # Memory limit
    'index_disable_during_load': True,  # Performance optimization
}
```

### Data Quality Rules

```python
DATA_QUALITY_RULES = {
    'coordinate_validation': {
        'latitude_range': (49.0, 61.0),
        'longitude_range': (-8.0, 2.0),
        'severity': 'error'
    },
    'postcode_format': {
        'pattern': r'^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$',
        'severity': 'warning'
    }
}
```

## Data Sources

### Enabled Sources (Default)

| Source | Type | Priority | Quality | Description |
|--------|------|----------|---------|-------------|
| `voa_2023` | NNDR | 1 | 0.95 | VOA 2023 NNDR Compiled List |
| `local_council_2015` | NNDR | 2 | 0.85 | Local Council NNDR Data 2015 |
| `sample_nndr` | NNDR | 3 | 0.80 | Sample NNDR Data (testing) |
| `os_uprn` | Reference | 1 | 0.98 | OS Open UPRN |
| `codepoint` | Reference | 2 | 0.90 | CodePoint Open Postcodes |
| `onspd` | Reference | 1 | 0.95 | ONS Postcode Directory |

### Disabled Sources (Available for Future Use)

| Source | Type | Priority | Quality | Description |
|--------|------|----------|---------|-------------|
| `land_registry` | Property Sales | 1 | 0.98 | HM Land Registry |
| `rightmove` | Property Sales | 2 | 0.85 | Rightmove Listings |
| `estates_gazette` | Market Analysis | 1 | 0.90 | Estates Gazette |
| `ons_economic` | Economic Indicators | 1 | 0.95 | ONS Economic Data |

## Data Processing Flow

### 1. **Source Discovery**
- Scan data directory for configured file patterns
- Validate file existence and format
- Group sources by type and priority

### 2. **Data Extraction**
- Parse files according to format specification
- Apply field mappings and transformations
- Handle encoding and format variations

### 3. **Quality Validation**
- Validate coordinates and postcodes
- Check value ranges and formats
- Apply business rules and constraints

### 4. **Duplicate Detection**
- Identify duplicates across sources
- Group similar records
- Mark preferred records based on priority

### 5. **Bulk Insertion**
- Optimize database performance
- Insert data in batches
- Rebuild indexes after completion

### 6. **Source Tracking**
- Record metadata for each source
- Track processing statistics
- Maintain audit trail

## Monitoring and Logging

### Log Files
- `comprehensive_ingestion.log` - Main pipeline log
- `pipeline_run_YYYYMMDD_HHMMSS.log` - Per-run logs

### Statistics Tracking
```python
stats = {
    'total_files_processed': 0,
    'total_records_processed': 0,
    'total_records_inserted': 0,
    'total_duplicates_found': 0,
    'total_errors': 0,
    'processing_time': 0
}
```

### Performance Monitoring
- Memory usage tracking
- Processing time per source
- Database connection monitoring
- Parallel processing efficiency

## Error Handling

### Common Issues and Solutions

1. **Schema Mismatch**
   ```
   Error: Enhanced schema not found
   Solution: Run enhanced_schema_update.py first
   ```

2. **File Not Found**
   ```
   Error: Data file not found
   Solution: Check file patterns in pipeline_config.py
   ```

3. **Database Connection**
   ```
   Error: Database connection failed
   Solution: Verify db_config.py settings
   ```

4. **Memory Issues**
   ```
   Error: Memory limit exceeded
   Solution: Reduce chunk_size in PERFORMANCE_CONFIG
   ```

## Extending the Pipeline

### Adding New Data Sources

1. **Update Configuration**:
   ```python
   'new_source': {
       'priority': 2,
       'description': 'New Data Source',
       'file_pattern': 'new_data_*.csv',
       'format': 'csv',
       'enabled': True,
       'field_mapping': {
           'source_field': 'target_field',
           # ... more mappings
       }
   }
   ```

2. **Add Processor Method**:
   ```python
   def process_new_source_data(self, file_path: str) -> Generator[pd.DataFrame, None, None]:
       # Implementation here
       pass
   ```

3. **Update Data Sources Dictionary**:
   ```python
   self.data_sources['new_source'] = {
       # ... configuration
       'processor': self.process_new_source_data
   }
   ```

### Custom Validation Rules

```python
def custom_validation_rule(self, df: pd.DataFrame) -> pd.DataFrame:
    # Add custom validation logic
    return df
```

## Performance Tuning

### Database Optimization
- Use `index_disable_during_load: True` for large datasets
- Adjust `batch_size` based on available memory
- Monitor database connection pool usage

### Memory Management
- Set appropriate `memory_limit_gb`
- Use chunked processing for large files
- Monitor memory usage during processing

### Parallel Processing
- Adjust `max_workers` based on CPU cores
- Balance between CPU and I/O bottlenecks
- Monitor worker pool efficiency

## Troubleshooting

### Debug Mode
```bash
python run_pipeline.py --log-level DEBUG
```

### Dry Run Mode
```bash
python run_pipeline.py --dry-run
```

### Source-Specific Processing
```bash
python run_pipeline.py --source-type nndr --dry-run
```

## Best Practices

1. **Always run dry-run first** for new data sources
2. **Monitor logs** for warnings and errors
3. **Validate data quality** before production runs
4. **Backup database** before large ingestion runs
5. **Test with sample data** before processing full datasets
6. **Monitor system resources** during processing

## Support

For issues and questions:
1. Check the logs for detailed error messages
2. Verify configuration settings
3. Test with dry-run mode
4. Review data quality reports

## License

This pipeline is part of the NNDR Insight project and follows the same licensing terms. 