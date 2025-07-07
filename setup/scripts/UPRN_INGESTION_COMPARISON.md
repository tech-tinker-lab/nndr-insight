# UPRN Data Ingestion Approaches Comparison

## Overview

This document compares two different approaches for ingesting OS Open UPRN data:

1. **Individual Script Approach** (`ingest_gazetteer.py` + `ingest_os_uprn_fast.py`)
2. **Parallel Pipeline Approach** (`run_pipeline.py` + `comprehensive_ingestion_pipeline.py`)

## Individual Script Approach

### Files
- `ingest_gazetteer.py` - Original simple approach
- `ingest_os_uprn_fast.py` - New optimized approach

### Characteristics

#### Advantages
- **Speed**: Uses PostgreSQL COPY for ultra-fast bulk insertion
- **Simplicity**: Straightforward, easy to understand and maintain
- **Efficiency**: No duplicate checking overhead
- **Memory Efficient**: Processes data in chunks without loading entire file
- **Direct Control**: Precise control over table schema and data flow

#### Disadvantages
- **Limited Scope**: Only handles one data source at a time
- **Manual Process**: Requires separate scripts for each data type
- **No Integration**: Doesn't integrate with broader data pipeline

### Key Features
- Drops and recreates `os_open_uprn` table with simplified schema
- Uses UPRN as PRIMARY KEY (enforces uniqueness at database level)
- Fast COPY operation for bulk data insertion
- Built-in data quality verification
- Comprehensive logging and error handling

### Schema
```sql
CREATE TABLE os_open_uprn (
    uprn BIGINT PRIMARY KEY,
    x_coordinate NUMERIC(10,3),
    y_coordinate NUMERIC(10,3),
    latitude NUMERIC(10,8),
    longitude NUMERIC(11,8)
);
```

## Parallel Pipeline Approach

### Files
- `run_pipeline.py` - Pipeline runner
- `comprehensive_ingestion_pipeline.py` - Main pipeline logic

### Characteristics

#### Advantages
- **Comprehensive**: Handles multiple data sources simultaneously
- **Scalable**: Can process different data types in parallel
- **Integrated**: Part of larger data ingestion ecosystem
- **Flexible**: Supports different source types and formats
- **Advanced Features**: Duplicate detection, schema alignment, source tracking

#### Disadvantages
- **Complexity**: More complex codebase with multiple layers
- **Overhead**: Duplicate checking and schema alignment add processing time
- **Memory Usage**: May load more data into memory for processing
- **Slower**: Additional processing steps reduce overall speed

### Key Features
- Parallel processing of multiple data sources
- Duplicate detection across sources
- Schema alignment and validation
- Source tracking and quality scoring
- Integration with master gazetteer system

## Performance Comparison

### Speed
- **Individual Script**: ~10-50x faster due to direct COPY operations
- **Parallel Pipeline**: Slower due to pandas processing and duplicate checking

### Memory Usage
- **Individual Script**: Low memory usage, processes in chunks
- **Parallel Pipeline**: Higher memory usage for data processing

### Scalability
- **Individual Script**: Limited to single data source
- **Parallel Pipeline**: Can handle multiple sources simultaneously

## Use Cases

### Individual Script Approach Best For:
- **Single Data Source**: When you only need to ingest OS UPRN data
- **Speed Critical**: When fast ingestion is the primary requirement
- **Simple Requirements**: When you don't need complex data integration
- **Resource Constrained**: When memory and processing resources are limited
- **Development/Testing**: Quick iterations and testing

### Parallel Pipeline Approach Best For:
- **Multiple Data Sources**: When ingesting various reference datasets
- **Data Integration**: When you need to combine data from multiple sources
- **Quality Assurance**: When duplicate detection and data quality are important
- **Production Systems**: When you need robust, scalable data processing
- **Complex Requirements**: When you need advanced features like source tracking

## Recommendations

### For OS UPRN Data Specifically:
**Use the Individual Script Approach** (`ingest_os_uprn_fast.py`) because:

1. **UPRN is Unique**: Each UPRN is inherently unique, so duplicate checking is unnecessary
2. **Fast COPY Operations**: PostgreSQL COPY is the fastest way to bulk insert data
3. **Simple Schema**: OS UPRN data has a simple, well-defined schema
4. **Performance**: Speed is critical for large datasets (millions of records)

### For Overall System:
**Use the Parallel Pipeline Approach** for:
- Initial setup of all reference data
- When you need to process multiple data sources together
- When data quality and integration are priorities

## Implementation Notes

### Running Individual Script
```bash
# From project root
python setup/scripts/ingest_os_uprn_fast.py

# Or with custom CSV path
python setup/scripts/ingest_os_uprn_fast.py path/to/your/uprn_data.csv
```

### Running Parallel Pipeline
```bash
# From enhanced_ingestion_pipeline directory
python run_pipeline.py --source-type reference

# Or for specific data sources
python run_pipeline.py --dry-run --info
```

## Conclusion

Both approaches have their merits, but for OS UPRN data specifically, the individual script approach provides the best balance of speed, simplicity, and reliability. The parallel pipeline approach is better suited for comprehensive data ingestion scenarios where multiple sources need to be processed together.

Choose the approach that best fits your specific requirements and constraints. 