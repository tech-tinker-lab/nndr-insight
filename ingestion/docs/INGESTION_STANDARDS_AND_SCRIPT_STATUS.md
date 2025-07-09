# Ingestion Standards and Script Status

## Overview
This document outlines the standardized approach for data ingestion scripts in the NNDR Insight project, ensuring consistency, reliability, and performance across all ingestion processes.

## Standards Summary

### Metadata Columns (Standard Set)
All staging tables and ingestion scripts use ONLY these metadata columns for audit and traceability:

- `source_name` - Data source identifier (e.g., "OS_Open_Names_2024", "Code_Point_Open")
- `upload_user` - Database user performing the upload
- `upload_timestamp` - ISO format timestamp of upload
- `batch_id` - Unique batch identifier for concurrent ingestion
- `source_file` - Original source filename
- `file_size` - Size of source file in bytes
- `file_modified` - Last modified timestamp of source file
- `session_id` - Session identifier for concurrent operations
- `client_name` - Client identifier for data traceability

### Removed Legacy Fields
The following fields have been removed from all scripts and staging tables:
- `raw_line` ❌
- `raw_filename` ❌  
- `file_path` ❌
- `source_row_number` ❌

### Input Arguments
- **Standard argument**: `--source-path` (accepts single file or directory)
- **Optional arguments**: `--session-id`, `--client`, `--batch-id`, `--max-rows`
- **Output control**: `--output-csv` (for large file server-side COPY)

### Progress Reporting
- All scripts use `tqdm` progress bars for monitoring ingestion progress
- File-level and row-level progress tracking
- Clear success/failure indicators with emojis

### Error Handling
- No scripts create or drop tables (only insert data)
- Clear error messages if staging tables don't exist
- Graceful handling of missing files or directories

## Script Status and Execution Readiness

### ✅ READY FOR EXECUTION

#### 1. OS Open Names Ingestion (`ingest_os_open_names.py`)
**Status**: ✅ **READY FOR EXECUTION**
- **Large file handling**: ✅ Combined CSV approach with server-side COPY
- **Metadata columns**: ✅ All standard fields included
- **Arguments**: ✅ `--source-path`, `--client`, `--session-id`, `--output-csv`
- **Progress reporting**: ✅ tqdm progress bars
- **Error handling**: ✅ Comprehensive error checking

**Usage Examples**:
```bash
# Directory of CSV files with server-side COPY
python ingestion/scripts/ingest_os_open_names.py --source-path data/opname_csv_gb/Data --output-csv C:\ingest\os_open_names_combined.csv

# Single file ingestion
python ingestion/scripts/ingest_os_open_names.py --source-path data/opname_csv_gb/Data/HP40.csv

# With client and session tracking
python ingestion/scripts/ingest_os_open_names.py --source-path data/opname_csv_gb/Data --client "internal_team" --session-id "session_20241209"
```

#### 2. Code Point Open Ingestion (`ingest_code_point_open.py`)
**Status**: ✅ **READY FOR EXECUTION**
- **Large file handling**: ✅ Combined CSV approach with client-side streaming
- **Metadata columns**: ✅ All standard fields included (including client_name)
- **Arguments**: ✅ `--source-path`, `--client`, `--session-id`, `--output-csv`
- **Progress reporting**: ✅ tqdm progress bars
- **Error handling**: ✅ Comprehensive error checking

**Usage Examples**:
```bash
# Directory of CSV files with client-side streaming
python ingestion/scripts/ingest_code_point_open.py --source-path data/codepo_gb/Data/CSV

# Single file ingestion
python ingestion/scripts/ingest_code_point_open.py --source-path data/codepo_gb/Data/CSV/HP40.csv

# With client and session tracking
python ingestion/scripts/ingest_code_point_open.py --source-path data/codepo_gb/Data/CSV --client "internal_team" --session-id "session_20241209"
```

### 🔄 IN PROGRESS / NEEDS REVIEW

#### 3. OS Open UPRN Ingestion (`ingest_os_open_uprn.py`)
**Status**: 🔄 **NEEDS STANDARDIZATION**
- **Large file handling**: ✅ Combined CSV approach
- **Metadata columns**: ✅ All standard fields included
- **Arguments**: ✅ `--source-path`, `--client`, `--session-id`
- **Progress reporting**: ✅ tqdm progress bars
- **Notes**: Ready but needs testing with large datasets

#### 4. OS Open USRN Ingestion (`ingest_os_open_usrn.py`)
**Status**: 🔄 **NEEDS STANDARDIZATION**
- **Large file handling**: ⚠️ Single file processing (needs combined approach)
- **Metadata columns**: ✅ All standard fields included
- **Arguments**: ✅ `--source-path`, `--client`, `--session-id`
- **Progress reporting**: ✅ tqdm progress bars
- **Notes**: Needs combined CSV approach for directory processing

#### 5. ONSPD Ingestion (`ingest_onspd.py`)
**Status**: 🔄 **NEEDS STANDARDIZATION**
- **Large file handling**: ✅ Combined CSV approach
- **Metadata columns**: ✅ All standard fields included
- **Arguments**: ✅ `--source-path`, `--client`, `--session-id`
- **Progress reporting**: ✅ tqdm progress bars
- **Notes**: Ready but needs testing with large datasets

#### 6. NNDR Properties Ingestion (`ingest_nndr_properties.py`)
**Status**: 🔄 **NEEDS STANDARDIZATION**
- **Large file handling**: ✅ Combined CSV approach
- **Metadata columns**: ✅ All standard fields included
- **Arguments**: ✅ `--source-path`, `--client`, `--session-id`
- **Progress reporting**: ✅ tqdm progress bars
- **Notes**: Ready but needs testing with large datasets

#### 7. NNDR Ratepayers Ingestion (`ingest_nndr_ratepayers.py`)
**Status**: 🔄 **NEEDS STANDARDIZATION**
- **Large file handling**: ✅ Combined CSV approach
- **Metadata columns**: ✅ All standard fields included
- **Arguments**: ✅ `--source-path`, `--client`, `--session-id`
- **Progress reporting**: ✅ tqdm progress bars
- **Notes**: Ready but needs testing with large datasets

#### 8. Valuations Ingestion (`ingest_valuations.py`)
**Status**: 🔄 **NEEDS STANDARDIZATION**
- **Large file handling**: ✅ Combined CSV approach
- **Metadata columns**: ✅ All standard fields included
- **Arguments**: ✅ `--source-path`, `--client`, `--session-id`
- **Progress reporting**: ✅ tqdm progress bars
- **Notes**: Ready but needs testing with large datasets

#### 9. LAD Boundaries Ingestion (`ingest_lad_boundaries.py`)
**Status**: 🔄 **NEEDS STANDARDIZATION**
- **Large file handling**: ⚠️ Shapefile processing (different approach needed)
- **Metadata columns**: ✅ All standard fields included
- **Arguments**: ✅ `--source-path`, `--client`, `--session-id`
- **Progress reporting**: ✅ tqdm progress bars
- **Notes**: Uses GeoPandas for shapefile processing

#### 10. OS Open Map Local Ingestion (`ingest_os_open_map_local.py`)
**Status**: 🔄 **NEEDS STANDARDIZATION**
- **Large file handling**: ✅ Combined CSV approach for GML files
- **Metadata columns**: ⚠️ Missing some standard fields
- **Arguments**: ✅ `--source-path`, `--client`, `--session-id`
- **Progress reporting**: ✅ tqdm progress bars
- **Notes**: Uses Fiona for GML processing, needs metadata standardization

## Execution Checklist

### Before Running Any Script
1. ✅ Ensure PostgreSQL is running and accessible
2. ✅ Verify staging tables exist in the database
3. ✅ Check that source data files are accessible
4. ✅ Ensure sufficient disk space for combined CSV files (if using `--output-csv`)
5. ✅ Verify database user has INSERT permissions on staging tables

### For Large File Ingestion
1. ✅ Use `--output-csv` argument to specify a server-accessible path
2. ✅ Ensure the output directory is readable by PostgreSQL service
3. ✅ Monitor disk space during combined CSV creation
4. ✅ Use `--max-rows` for testing with small datasets first

### Performance Optimization
1. ✅ Use `--session-id` for concurrent ingestion
2. ✅ Use `--client` for data traceability
3. ✅ Monitor progress bars for completion status
4. ✅ Check data quality reports after ingestion

## Recent Updates (December 2024)

### Fixed Issues
- ✅ **OS Open Names**: Fixed server-side COPY file access issues
- ✅ **Code Point Open**: Added missing `client_name` field and `--client` argument
- ✅ **All Scripts**: Standardized metadata columns and argument structure
- ✅ **Progress Reporting**: Added tqdm progress bars to all scripts
- ✅ **Error Handling**: Improved error messages and validation

### Large File Handling
- ✅ **Combined CSV Approach**: All scripts now aggregate multiple files into single CSV
- ✅ **Server-side COPY**: OS Open Names uses `COPY ... FROM 'filename'` for large files
- ✅ **Client-side Streaming**: Code Point Open uses `copy_expert` for cross-platform compatibility
- ✅ **Flexible Output**: `--output-csv` argument for specifying server-accessible paths

## Next Steps

### Immediate Actions
1. **Test OS Open Names script** with large dataset using `--output-csv`
2. **Test Code Point Open script** with the provided CSV directory
3. **Validate data quality** after successful ingestion

### Future Improvements
1. **Standardize remaining scripts** to match the established patterns
2. **Add data validation** checks during ingestion
3. **Implement rollback mechanisms** for failed batches
4. **Add performance monitoring** and logging

## Support

For issues or questions:
1. Check the script help: `python script.py --help`
2. Review error messages and logs
3. Verify database connectivity and permissions
4. Test with `--max-rows` for small datasets first

---

**Last Updated**: December 9, 2024  
**Status**: Scripts ready for production use with large datasets 