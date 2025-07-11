# 🤖 AI Integration Guide for Government Data Analysis

## Overview

The NNDR Insight system now includes **AI-powered analysis** for government datasets, providing intelligent content detection, pattern recognition, standards compliance checking, and automatic mapping suggestions.

## 🎯 Key Features

### 1. **Intelligent Content Analysis**
- **Pattern Detection**: Automatically identifies UK government data patterns (UPRN, USRN, postcodes, etc.)
- **Field Type Inference**: Uses machine learning to detect data types and formats
- **Data Quality Assessment**: Evaluates completeness, consistency, and accuracy
- **Government Indicators**: Recognizes government-specific data fields and structures

### 2. **Standards Compliance Detection**
- **BS7666**: UK Address Standard compliance checking
- **INSPIRE**: EU spatial data directive compliance
- **OS Standards**: Ordnance Survey standards validation
- **GDS**: Government Digital Service standards

### 3. **Automatic Mapping Suggestions**
- **Column Mapping**: Suggests optimal source-to-target column mappings
- **Data Type Recommendations**: Proposes appropriate PostgreSQL data types
- **Transformation Suggestions**: Recommends data cleaning and transformation steps
- **Validation Rules**: Suggests data validation patterns

### 4. **Confidence Scoring**
- **Pattern Confidence**: Measures reliability of detected patterns
- **Standards Compliance**: Quantifies adherence to government standards
- **Overall Confidence**: Combined score for analysis reliability

## 🚀 How It Works

### Frontend Integration

```javascript
// AI analysis is automatically triggered during file upload
const aiAnalyzer = new AIDataAnalyzer();
const analysis = await aiAnalyzer.analyzeDataset(file, content, fileType);

// Results include:
// - contentAnalysis: Pattern detection and field types
// - schemaDetection: Structure and relationships
// - standardsIdentification: Compliance assessment
// - mappingSuggestions: Column mapping recommendations
// - confidence: Overall analysis confidence score
```

### Backend Processing

```python
# AI analysis service provides comprehensive analysis
analyzer = GovernmentDataAnalyzer()
analysis = analyzer.analyze_dataset(
    file_content=content,
    file_type=file_type,
    file_name=filename
)
```

## 📊 Supported Data Formats

### Primary Formats (Full AI Analysis)
- **CSV**: Complete pattern detection and mapping
- **JSON**: Structure analysis and field detection
- **XML/GML**: Element analysis and spatial data detection
- **GeoJSON**: Geospatial feature analysis

### Secondary Formats (Basic Analysis)
- **ZIP**: Directory structure and file grouping
- **GeoPackage**: Basic format detection
- **Shapefile**: Component analysis
- **SDMX**: Statistical data structure detection

## 🎯 Government Data Patterns

### UK Address Standards (BS7666)
```javascript
// Detected patterns
{
  'uprn': /^\d{12}$/,           // Unique Property Reference Number
  'usrn': /^\d{8}$/,           // Unique Street Reference Number
  'postcode': /^[A-Z]{1,2}[0-9][A-Z0-9]?\s*[0-9][A-Z]{2}$/,
  'address': 'Property address fields'
}
```

### Spatial Data (INSPIRE)
```javascript
// Spatial field detection
{
  'geometry': 'Spatial geometry fields',
  'coordinate': 'Coordinate reference systems',
  'latitude': 'Latitude coordinates',
  'longitude': 'Longitude coordinates',
  'easting': 'OSGB easting coordinates',
  'northing': 'OSGB northing coordinates'
}
```

### Business Data
```javascript
// Business rate patterns
{
  'rateable_value': 'Rateable value fields',
  'business_type': 'Business classification',
  'property_type': 'Property categorization',
  'valuation_date': 'Valuation timestamps'
}
```

## 🔧 API Endpoints

### Main Analysis Endpoint
```http
POST /api/ai/analyze-dataset
Content-Type: multipart/form-data

file: [uploaded file]
```

**Response:**
```json
{
  "file_info": {
    "name": "business_rates.csv",
    "type": "csv",
    "analyzed_at": "2024-01-15T10:30:00Z"
  },
  "content_analysis": {
    "data_patterns": [...],
    "field_types": [...],
    "government_indicators": [...]
  },
  "schema_detection": {
    "fields": [...],
    "suggested_table_name": "staging_business_rates"
  },
  "standards_compliance": {
    "detected_standards": [
      {
        "name": "BS7666",
        "score": 0.85,
        "details": "Found 3/4 BS7666 fields"
      }
    ]
  },
  "mapping_suggestions": {
    "column_mappings": [...],
    "transformations": [...],
    "validations": [...]
  },
  "confidence_score": 0.87,
  "recommendations": [...]
}
```

### Field Type Detection
```http
POST /api/ai/detect-types
Content-Type: application/json

{
  "content": "file content string"
}
```

### Standards Compliance Check
```http
POST /api/ai/check-standards
Content-Type: application/json

{
  "content_analysis": {...},
  "schema_detection": {...}
}
```

### Mapping Validation
```http
POST /api/ai/validate-mapping
Content-Type: application/json

{
  "source_columns": [...],
  "target_columns": [...],
  "transformations": [...],
  "validations": [...]
}
```

## 🎨 UI Integration

### File Preview with AI Analysis
The upload interface now displays AI analysis results including:

1. **Standards Compliance Badges**
   - BS7666, INSPIRE, OS Standards indicators
   - Compliance percentage scores

2. **Pattern Detection Results**
   - Detected field types with confidence scores
   - Government data indicators
   - Sample values and suggestions

3. **Mapping Suggestions**
   - Recommended column mappings
   - Data type suggestions
   - Transformation recommendations

4. **Quality Assessment**
   - Data completeness indicators
   - Consistency warnings
   - Accuracy metrics

### Example UI Display
```
📊 AI Analysis (Confidence: 87%)

🏛️ Detected Standards:
   BS7666 (85%) ✓ INSPIRE (72%)

🔍 Detected Patterns:
   uprn: uprn, government_data ✓ High confidence
   postcode: postcode ✓ High confidence
   rateable_value: currency_gbp

💡 Recommendations:
   • Consider implementing UK government data standards
   • Add validation rules for postcode format
   • Standardize date formats for valuation_date

🗺️ Suggested Mappings:
   uprn → uprn (bigint)
   postcode → postcode (varchar(10))
   rateable_value → amount (decimal(10,2))
```

## 🔧 Configuration

### Environment Variables
```bash
# AI Analysis API endpoint
REACT_APP_AI_API_ENDPOINT=http://localhost:8000/api/ai

# Analysis confidence thresholds
AI_PATTERN_CONFIDENCE_THRESHOLD=0.7
AI_STANDARDS_CONFIDENCE_THRESHOLD=0.5
AI_OVERALL_CONFIDENCE_THRESHOLD=0.6
```

### Backend Configuration
```python
# AI Analysis settings
AI_ANALYSIS_CONFIG = {
    'max_content_size': 1024 * 100,  # 100KB
    'pattern_confidence_threshold': 0.7,
    'standards_confidence_threshold': 0.5,
    'enable_ml_analysis': True,
    'cache_results': True
}
```

## 📈 Performance Considerations

### Optimization Strategies
1. **Content Size Limits**: Analysis limited to first 100KB for performance
2. **Caching**: Analysis results cached to avoid re-processing
3. **Async Processing**: Non-blocking analysis during file upload
4. **Progressive Enhancement**: Basic analysis with optional ML features

### Memory Management
- Streaming file processing for large datasets
- Garbage collection for analysis objects
- Memory monitoring and limits

## 🧪 Testing

### Test Data
```bash
# Sample government datasets for testing
test_data/
├── business_rates_sample.csv
├── property_addresses.json
├── spatial_boundaries.gml
└── statistical_data.sdmx
```

### Test Commands
```bash
# Run AI analysis tests
pytest tests/test_ai_analysis.py

# Test pattern detection
python -m pytest tests/test_pattern_detection.py

# Test standards compliance
python -m pytest tests/test_standards_compliance.py
```

## 🔮 Future Enhancements

### Planned Features
1. **Machine Learning Models**
   - Custom trained models for UK government data
   - Pattern learning from user feedback
   - Adaptive confidence scoring

2. **Advanced Analytics**
   - Data lineage tracking
   - Quality trend analysis
   - Anomaly detection

3. **Integration Capabilities**
   - External government data APIs
   - Real-time standards updates
   - Cross-reference validation

4. **User Experience**
   - Interactive mapping suggestions
   - Visual pattern recognition
   - Guided data preparation

## 🛠️ Troubleshooting

### Common Issues

1. **AI Analysis Fails**
   ```bash
   # Check backend logs
   tail -f logs/ai_analysis.log
   
   # Verify dependencies
   pip install -r requirements-ai.txt
   ```

2. **Low Confidence Scores**
   - Check data format and encoding
   - Verify file content is readable
   - Review pattern detection thresholds

3. **Standards Not Detected**
   - Ensure field names match expected patterns
   - Check data format compliance
   - Review standards configuration

### Debug Mode
```javascript
// Enable debug logging
localStorage.setItem('ai_debug', 'true');

// Check analysis results
console.log('AI Analysis:', file.analysis.aiAnalysis);
```

## 📚 Resources

### Documentation
- [UK Government Data Standards](https://www.gov.uk/government/publications)
- [BS7666 Address Standard](https://www.bsi.uk.com/standards)
- [INSPIRE Directive](https://inspire.ec.europa.eu/)
- [OS Data Standards](https://www.ordnancesurvey.co.uk/business-government/tools-support)

### Code Examples
- [AI Analysis Examples](examples/ai_analysis/)
- [Pattern Detection Samples](examples/patterns/)
- [Standards Compliance Tests](examples/standards/)

---

**🎉 The AI integration transforms government data ingestion from manual mapping to intelligent, automated analysis with confidence scoring and standards compliance!** 