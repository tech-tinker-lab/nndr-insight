# File Monitor and Auto-Processing System

## Overview

The File Monitor and Auto-Processing System is a comprehensive solution that automatically detects files placed in a designated directory and processes them using the appropriate ingestion scripts. This system provides:

- **Automatic file detection** using file system monitoring
- **Intelligent script selection** based on file patterns
- **Robust error handling** and file management
- **Comprehensive logging** and status monitoring
- **Easy configuration** through JSON files

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Incoming      │    │   Processing    │    │   Processed     │
│   Directory     │───▶│   Directory     │───▶│   Directory     │
│                 │    │                 │    │                 │
│ - osopenuprn.csv│    │ - File being    │    │ - Successfully  │
│ - codepo_*.csv  │    │   processed     │    │   processed     │
│ - ONSPD_*.csv   │    │                 │    │   files         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Failed        │
                       │   Directory     │
                       │                 │
                       │ - Files that    │
                       │   failed to     │
                       │   process       │
                       └─────────────────┘
```

## Directory Structure

```
setup/
├── data/
│   ├── incoming/          # Place files here for processing
│   ├── processing/        # Files currently being processed
│   ├── processed/         # Successfully processed files
│   └── failed/           # Files that failed to process
├── scripts/
│   ├── file_monitor.py           # Main monitoring script
│   ├── file_monitor_config.json  # Configuration file
│   ├── monitor_status.py         # Status checking script
│   ├── start_file_monitor.bat    # Windows startup script
│   ├── ingest_os_uprn_fast.py    # UPRN ingestion script
│   └── [other ingestion scripts]
└── logs/
    └── file_monitor.log   # Processing logs
```

## File Pattern Configuration

The system uses pattern matching to determine which ingestion script to run for each file:

| File Pattern | Script | Description | Priority |
|--------------|--------|-------------|----------|
| `osopenuprn_*.csv` | `ingest_os_uprn_fast.py` | OS Open UPRN Data | 1 |
| `codepo_*.csv` | `ingest_codepoint.py` | CodePoint Open Postcodes | 2 |
| `ONSPD_*.csv` | `ingest_onspd.py` | ONS Postcode Directory | 2 |
| `opname_*.csv` | `ingest_os_open_names.py` | OS Open Names | 2 |
| `LAD_*.shp` | `ingest_lad_boundaries.py` | LAD Boundaries | 1 |
| `*.gml` | `ingest_os_open_map_local.py` | OS Open Map Local | 3 |
| `*.gpkg` | `ingest_os_open_usrn.py` | OS Open USRN | 2 |
| `*.csv` | `ingest_generic_csv.py` | Generic CSV Data | 5 |

## How It Works

### 1. File Detection
- The system monitors the `incoming` directory for new files
- Uses the `watchdog` library for efficient file system monitoring
- Ignores temporary files and system files

### 2. Pattern Matching
- When a file is detected, the system matches it against configured patterns
- Patterns are checked in priority order (lower numbers = higher priority)
- The first matching pattern determines which script to run

### 3. File Processing
- File is moved to the `processing` directory
- Appropriate ingestion script is executed with the file path
- Script output is captured and logged

### 4. File Management
- On success: File is moved to `processed` directory
- On failure: File is moved to `failed` directory
- All actions are logged with timestamps

## Usage Instructions

### Starting the File Monitor

**Option 1: Windows Batch Script**
```bash
# Double-click or run from command line
setup/scripts/start_file_monitor.bat
```

**Option 2: Python Script Directly**
```bash
# From project root
python setup/scripts/file_monitor.py
```

### Processing Files

1. **Place files** in the `setup/data/incoming` directory
2. **File monitor detects** the new file automatically
3. **System processes** the file using the appropriate script
4. **File is moved** to `processed` or `failed` directory
5. **Check logs** for processing results

### Checking System Status

```bash
# Check overall system status
python setup/scripts/monitor_status.py
```

This provides:
- Directory status and file counts
- Database table record counts
- Recent processing activity
- System health information

## Configuration

### File Monitor Configuration (`file_monitor_config.json`)

```json
{
  "file_patterns": {
    "osopenuprn_*.csv": {
      "script": "ingest_os_uprn_fast.py",
      "description": "OS Open UPRN Data",
      "priority": 1,
      "table": "os_open_uprn",
      "source_type": "reference"
    }
  },
  "directories": {
    "incoming": "setup/data/incoming",
    "processing": "setup/data/processing",
    "processed": "setup/data/processed",
    "failed": "setup/data/failed"
  },
  "settings": {
    "log_file": "file_monitor.log",
    "max_retries": 3,
    "retry_delay": 5,
    "file_check_interval": 1,
    "cleanup_old_files": true,
    "old_file_days": 30
  }
}
```

### Adding New File Patterns

1. **Edit** `file_monitor_config.json`
2. **Add** new pattern with script mapping
3. **Create** corresponding ingestion script
4. **Restart** file monitor

## Monitoring and Logging

### Log Files
- **`file_monitor.log`**: Main processing log
- **Console output**: Real-time status updates

### Log Format
```
2024-01-15 10:30:45 - INFO - Processing file: osopenuprn_202506.csv
2024-01-15 10:30:45 - INFO - Using script: ingest_os_uprn_fast.py for OS Open UPRN Data
2024-01-15 10:30:46 - INFO - Moved osopenuprn_202506.csv to processing directory
2024-01-15 10:32:15 - INFO - Successfully processed osopenuprn_202506.csv
2024-01-15 10:32:15 - INFO - Moved osopenuprn_202506.csv to processed directory
```

### Status Monitoring

The status script provides comprehensive system information:

```bash
python setup/scripts/monitor_status.py
```

**Output includes:**
- Directory file counts and sizes
- Database table record counts
- Recent processing activity
- System health status
- Processing queue status

## Error Handling

### File Processing Errors
- **Script failures**: Files moved to `failed` directory
- **Pattern mismatches**: Files moved to `failed` directory
- **Database errors**: Logged with full error details
- **File access errors**: Retry mechanism with delays

### System Errors
- **Connection failures**: Automatic retry with exponential backoff
- **Disk space issues**: Warnings logged, processing continues
- **Permission errors**: Detailed error messages in logs

## Performance Considerations

### File Processing
- **Parallel processing**: Multiple files can be processed simultaneously
- **Memory efficient**: Files processed in streaming fashion
- **Fast detection**: File system events for immediate response

### Resource Usage
- **Low CPU**: Minimal overhead for file monitoring
- **Low memory**: Efficient file handling without loading entire files
- **Disk I/O**: Optimized file moves and database operations

## Security Features

### File Safety
- **No file modification**: Original files preserved
- **Backup locations**: Files moved to safe directories
- **Error isolation**: Failed files don't affect others

### Access Control
- **Directory permissions**: Controlled access to processing directories
- **Script validation**: Only configured scripts can be executed
- **Logging**: All actions logged for audit trail

## Troubleshooting

### Common Issues

**1. File Monitor Not Starting**
```bash
# Check Python installation
python --version

# Check required packages
pip install watchdog

# Check file permissions
ls -la setup/scripts/file_monitor.py
```

**2. Files Not Being Processed**
```bash
# Check if monitor is running
python setup/scripts/monitor_status.py

# Check incoming directory
ls -la setup/data/incoming/

# Check log files
tail -f file_monitor.log
```

**3. Script Execution Failures**
```bash
# Check script permissions
chmod +x setup/scripts/*.py

# Test script manually
python setup/scripts/ingest_os_uprn_fast.py test_file.csv

# Check database connection
python setup/scripts/test_db_connection.py
```

### Debug Mode

Enable debug logging by modifying the logging level in `file_monitor.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_monitor.log'),
        logging.StreamHandler()
    ]
)
```

## Best Practices

### File Naming
- **Use descriptive names**: Include data type and date
- **Follow patterns**: Match configured file patterns exactly
- **Avoid special characters**: Use underscores instead of spaces

### File Management
- **Monitor disk space**: Regular cleanup of processed files
- **Backup important files**: Keep copies before processing
- **Check logs regularly**: Monitor for errors and issues

### System Maintenance
- **Regular status checks**: Use monitor_status.py daily
- **Log rotation**: Archive old log files
- **Script updates**: Keep ingestion scripts current

## Future Enhancements

### Planned Features
- **Web interface**: Browser-based monitoring and control
- **Email notifications**: Alerts for processing failures
- **Scheduled processing**: Time-based file processing
- **Data validation**: Pre-processing file validation
- **Performance metrics**: Processing time and throughput tracking

### Extensibility
- **Plugin system**: Easy addition of new file types
- **API integration**: REST API for external control
- **Cloud storage**: Support for cloud-based file sources
- **Distributed processing**: Multi-node processing support

## Conclusion

The File Monitor and Auto-Processing System provides a robust, efficient solution for automated data ingestion. With its intelligent file pattern matching, comprehensive error handling, and detailed monitoring capabilities, it significantly reduces manual intervention while ensuring reliable data processing.

The system is designed to be:
- **Easy to use**: Simple file placement triggers processing
- **Reliable**: Robust error handling and recovery
- **Scalable**: Handles multiple file types and sizes
- **Maintainable**: Clear logging and status monitoring
- **Extensible**: Easy to add new file types and scripts 