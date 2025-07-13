# AI-Powered Dataset Type Creation Guide

## Overview

The AI-Powered Dataset Type Creator is a sophisticated system designed to handle large files (up to 10GB) and automatically generate dataset types with intelligent field analysis, validation, and standards compliance. This system combines client-side and server-side processing to provide optimal performance and accuracy.

## Key Features

### 🚀 Large File Support
- **File Size Limit**: Up to 10GB files
- **Chunked Processing**: Efficient memory usage for large files
- **Adaptive Sampling**: Intelligent sampling for very large files
- **Progress Tracking**: Real-time progress indicators

### 🤖 AI-Powered Analysis
- **Intelligent Field Detection**: Automatic data type detection
- **Pattern Recognition**: Identifies common field patterns (postcodes, coordinates, etc.)
- **Data Standards Compliance**: Matches against known data standards
- **Validation Rules**: Generates appropriate validation rules
- **User Override**: Allows manual adjustment of AI suggestions

### 📊 Multi-Format Support
- **CSV Files**: Delimiter detection, header analysis
- **JSON Files**: Structure analysis, nested object handling
- **XML Files**: Element structure, attribute analysis
- **Text Files**: Pattern-based analysis

## How It Works

### 1. File Upload & Analysis
```
User Uploads File → Size Check → Format Detection → Sample Analysis → AI Enhancement
```

### 2. Field Configuration
```
AI Field Detection → User Review → Manual Adjustments → Validation → Final Configuration
```

### 3. Dataset Type Creation
```
Field Mapping → Standards Compliance → Validation Rules → Database Schema → Type Creation
```

## Usage Instructions

### Step 1: Access the AI Creator
1. Navigate to **Dataset Structures** in the sidebar
2. Click **"AI-Powered Creator"** button
3. The creator opens in a full-screen dialog

### Step 2: Upload Your File
1. **Select File**: Choose your data file (CSV, JSON, XML, etc.)
2. **File Validation**: System checks file size and format
3. **Analysis Options**: Configure analysis parameters
   - **Client-Side Analysis**: Recommended for large files
   - **Sample Size**: Number of rows to analyze
   - **AI Enhancement**: Enable intelligent field detection
   - **Validation**: Enable automatic validation rules

### Step 3: AI Analysis
1. **Click "Start Analysis"**: System begins processing
2. **Progress Tracking**: Monitor analysis progress
3. **Results Review**: Examine detected fields and data types
4. **Standards Identification**: Review identified data standards

### Step 4: Field Configuration
1. **Review AI Suggestions**: Check automatically detected fields
2. **Manual Adjustments**: Modify field names, types, constraints
3. **Add/Remove Fields**: Customize field structure
4. **Set Primary Keys**: Mark required fields as primary keys

### Step 5: Validation & Standards
1. **Dataset Information**: Enter name, description, category
2. **Governing Body**: Specify data source organization
3. **Standards Compliance**: Review identified standards
4. **Validation Rules**: Configure field validation

### Step 6: Review & Create
1. **Final Review**: Check all configurations
2. **Validation Check**: Ensure all requirements are met
3. **Create Dataset Type**: Generate the final dataset type

## Field Type Detection

### Automatic Detection Rules

| Field Pattern | Detected Type | Description |
|---------------|---------------|-------------|
| `*id`, `*uprn`, `*code` | `bigint` | Unique identifiers |
| `*postcode`, `*pcd` | `varchar(10)` | UK postcodes |
| `*date`, `*time` | `date` | Date values |
| `*amount`, `*value`, `*rate` | `numeric(12,2)` | Currency amounts |
| `*lat`, `*long`, `*x`, `*y` | `geometry` | Spatial coordinates |
| `*active`, `*enabled`, `*flag` | `boolean` | Boolean flags |
| `*email` | `varchar(255)` | Email addresses |
| `*phone` | `varchar(20)` | Phone numbers |

### Data Type Mapping

| Detected Type | Database Type | PostGIS Type | Constraints |
|---------------|---------------|--------------|-------------|
| `text` | `TEXT` | - | - |
| `varchar` | `VARCHAR(255)` | - | - |
| `integer` | `INTEGER` | - | - |
| `bigint` | `BIGINT` | - | - |
| `numeric` | `NUMERIC(12,2)` | - | - |
| `date` | `DATE` | - | - |
| `timestamp` | `TIMESTAMP` | - | - |
| `boolean` | `BOOLEAN` | - | - |
| `geometry` | `GEOMETRY` | `POINT` | Spatial index |
| `uuid` | `UUID` | - | Unique constraint |

## Data Standards Compliance

### Supported Standards

#### UK Government Standards
- **BS7666**: Address and location referencing
- **GDS**: Government Digital Service Standards
- **VOA_NNDR**: Valuation Office Agency standards
- **ONS_Standards**: Office for National Statistics
- **OS_Standards**: Ordnance Survey standards
- **Land_Registry**: Land Registry standards

#### European Standards
- **INSPIRE**: European spatial data infrastructure
- **EU_Open_Data**: European Union open data standards

#### International Standards
- **SDMX**: Statistical Data and Metadata eXchange
- **ISO_20022**: Financial services messaging

### Compliance Scoring
- **0.8-1.0**: Excellent compliance
- **0.6-0.8**: Good compliance
- **0.4-0.6**: Fair compliance
- **0.0-0.4**: Poor compliance

## Performance Optimization

### Large File Handling
- **Chunked Reading**: 1MB chunks to manage memory
- **Adaptive Sampling**: Sample size based on file size
- **Progress Tracking**: Real-time progress updates
- **Background Processing**: Non-blocking analysis

### Memory Management
- **Streaming Processing**: Process files without loading entirely into memory
- **Garbage Collection**: Automatic memory cleanup
- **Resource Monitoring**: Track memory usage during processing

## Error Handling

### Common Issues & Solutions

#### "File too large" Error
- **Cause**: File exceeds 10GB limit
- **Solution**: Use client-side analysis or split file

#### "Invalid CSV format" Error
- **Cause**: CSV parsing issues
- **Solution**: Check delimiter, encoding, or use different format

#### "Analysis timeout" Error
- **Cause**: Large file taking too long
- **Solution**: Increase timeout or use client-side analysis

#### "Memory error" Error
- **Cause**: Insufficient memory for large file
- **Solution**: Use client-side analysis or reduce sample size

## Best Practices

### File Preparation
1. **Clean Data**: Remove unnecessary columns and rows
2. **Consistent Format**: Ensure consistent data types within columns
3. **Proper Headers**: Use descriptive, unique column headers
4. **Encoding**: Use UTF-8 encoding for international characters

### Analysis Configuration
1. **Sample Size**: Use larger samples for better accuracy
2. **AI Enhancement**: Enable for better field detection
3. **Validation**: Enable for data quality checks
4. **Standards**: Enable for compliance checking

### Field Configuration
1. **Review AI Suggestions**: Always review automatic detections
2. **Set Primary Keys**: Mark unique identifier fields
3. **Add Constraints**: Set appropriate field constraints
4. **Documentation**: Add clear field descriptions

## Advanced Features

### Custom Field Types
- **Postcode**: UK postcode validation
- **UPRN**: Unique Property Reference Number
- **USRN**: Unique Street Reference Number
- **Geometry**: Spatial data handling
- **Currency**: Monetary value handling

### Validation Rules
- **Pattern Matching**: Regular expression validation
- **Range Checking**: Numeric value ranges
- **Required Fields**: Mandatory field validation
- **Unique Constraints**: Duplicate prevention

### Transformation Rules
- **Data Cleaning**: Automatic data formatting
- **Type Conversion**: Automatic type casting
- **Coordinate Transformation**: Spatial data conversion
- **Standardization**: Format standardization

## Troubleshooting

### Performance Issues
1. **Large Files**: Use client-side analysis
2. **Slow Processing**: Reduce sample size
3. **Memory Issues**: Close other applications
4. **Network Issues**: Check internet connection

### Analysis Issues
1. **Incorrect Types**: Manually adjust field types
2. **Missing Fields**: Add fields manually
3. **Wrong Standards**: Review and correct standards
4. **Validation Errors**: Fix data format issues

### Creation Issues
1. **Validation Failures**: Check all required fields
2. **Database Errors**: Verify database connection
3. **Permission Issues**: Check user permissions
4. **Duplicate Names**: Use unique dataset type names

## Support & Resources

### Documentation
- **API Documentation**: Backend endpoint documentation
- **Component Guide**: Frontend component usage
- **Database Schema**: Database structure documentation

### Tools & Utilities
- **File Validator**: Pre-upload file validation
- **Format Converter**: File format conversion tools
- **Data Cleaner**: Data cleaning utilities
- **Schema Viewer**: Database schema visualization

### Community Support
- **User Forum**: Community discussion and support
- **Issue Tracker**: Bug reports and feature requests
- **Knowledge Base**: Common questions and answers
- **Training Materials**: User training resources

## Future Enhancements

### Planned Features
- **Machine Learning**: Enhanced AI field detection
- **Real-time Collaboration**: Multi-user editing
- **Version Control**: Dataset type versioning
- **Template Library**: Pre-built dataset templates
- **Integration APIs**: Third-party system integration

### Performance Improvements
- **Parallel Processing**: Multi-threaded analysis
- **Caching**: Analysis result caching
- **Compression**: File compression support
- **Streaming**: Real-time data streaming

This AI-powered system provides a robust, scalable solution for creating dataset types from large files with intelligent analysis and user-friendly configuration options. 