# Enhanced Staging Table and Column Mapping Features

## Overview

This document summarizes the improvements made to address user feedback regarding:

1. **Table match vs column confidence mismatch** - Fixed alignment between table suggestions and column mapping confidence
2. **New table handling** - Improved data type inference and geometry field detection for new tables
3. **Upload flow enhancements** - Added action suggestions after file selection

## Key Improvements

### 1. Fixed Confidence Alignment

**Problem**: Table suggestions showed 90% match but column mapping showed 5% confidence.

**Solution**: 
- Improved confidence calculation algorithm in `calculate_mapping_match_status()`
- Added weighted scoring system for different match types
- Enhanced new table detection and confidence scoring

**Changes Made**:
```python
# Backend: backend/app/routers/admin.py
def calculate_mapping_match_status(headers, mappings, existing_columns):
    # New table handling with higher confidence
    if not existing_columns:
        new_table_mappings = sum(1 for m in mappings if m["matchStatus"] == "new_table")
        if new_table_mappings > 0:
            return {
                "status": "new_table",
                "confidence": 0.85,  # Higher confidence for new tables
                "color": "blue",
                "message": f"New table - {new_table_mappings} AI-generated mappings"
            }
    
    # Weighted scoring for existing tables
    match_percentage = (
        exact_matches * 1.0 + 
        partial_matches * 0.8 + 
        semantic_matches * 0.6 + 
        suggested_mappings * 0.4
    ) / total
```

### 2. Enhanced New Table Handling

**Problem**: New tables needed better data type inference and geometry field detection.

**Solution**:
- Added comprehensive data type inference with geometry detection
- Improved column mapping generation for new tables
- Added "new_table" match status with higher confidence

**Changes Made**:
```python
# Enhanced data type inference
def infer_data_type(header, content_preview):
    # Check for geometry/geospatial fields first
    geometry_keywords = ['geometry', 'geom', 'shape', 'polygon', 'point', 'line', 
                        'boundary', 'coordinates', 'lat', 'long', 'latitude', 'longitude']
    if any(keyword in header_lower for keyword in geometry_keywords):
        return 'geometry'
    
    # Enhanced numeric field detection
    numeric_keywords = ['amount', 'value', 'price', 'cost', 'rate', 'total', 'sum', 
                       'average', 'count', 'number', 'quantity', 'size', 'length', 
                       'width', 'height', 'area', 'volume']
    
    # Enhanced date/time detection
    date_keywords = ['date', 'time', 'created', 'updated', 'modified', 'timestamp', 
                    'effective', 'expiry']
```

### 3. Upload Action Suggestions

**Problem**: After file selection, users needed guidance on next steps.

**Solution**:
- Created new API endpoint `/admin/staging/suggest-actions`
- Built `UploadActionSuggestions` React component
- Integrated suggestions into the upload flow

**New Features**:
- **Save Configuration**: Always suggested for new files
- **Use Existing Config**: Shows similar configurations with similarity scores
- **AI Analysis**: Suggested for complex files
- **Proceed with Upload**: Direct upload option

**Implementation**:
```javascript
// Frontend: frontend/src/components/UploadActionSuggestions.jsx
const UploadActionSuggestions = ({ 
  file, 
  headers, 
  onAction, 
  onClose,
  onSaveConfig,
  onUseExistingConfig 
}) => {
  // Fetches suggestions from backend
  // Displays priority-based action cards
  // Shows existing configurations with similarity scores
}
```

## Technical Implementation

### Backend Changes

#### 1. Enhanced Column Mapping Generation
- **File**: `backend/app/routers/admin.py`
- **Function**: `generate_ai_column_mappings()`
- **Improvements**:
  - New table detection logic
  - Higher confidence for new table mappings
  - Better data type inference

#### 2. New API Endpoint
- **Endpoint**: `POST /admin/staging/suggest-actions`
- **Purpose**: Suggest actions after file selection
- **Features**:
  - Analyzes file headers and type
  - Finds similar existing configurations
  - Generates priority-based suggestions

#### 3. Improved Match Status Calculation
- **Function**: `calculate_mapping_match_status()`
- **Improvements**:
  - Weighted scoring system
  - New table status handling
  - Better confidence alignment

### Frontend Changes

#### 1. Enhanced Column Mapping Component
- **File**: `frontend/src/components/EnhancedColumnMapping.jsx`
- **Improvements**:
  - Added "new_table" status support
  - Enhanced visual indicators
  - Better confidence display

#### 2. New Action Suggestions Component
- **File**: `frontend/src/components/UploadActionSuggestions.jsx`
- **Features**:
  - Priority-based action cards
  - Existing configuration matching
  - Interactive action handling

#### 3. Upload Page Integration
- **File**: `frontend/src/pages/Upload.jsx`
- **Improvements**:
  - Integrated action suggestions
  - Enhanced file analysis flow
  - Better user guidance

## Data Type Inference Improvements

### Geometry Field Detection
```python
geometry_keywords = [
    'geometry', 'geom', 'shape', 'polygon', 'point', 'line', 
    'boundary', 'coordinates', 'lat', 'long', 'latitude', 
    'longitude', 'x_coord', 'y_coord', 'x_coordinate', 'y_coordinate'
]
```

### Enhanced Numeric Detection
```python
numeric_keywords = [
    'amount', 'value', 'price', 'cost', 'rate', 'total', 'sum', 
    'average', 'count', 'number', 'quantity', 'size', 'length', 
    'width', 'height', 'area', 'volume'
]
```

### Date/Time Detection
```python
date_keywords = [
    'date', 'time', 'created', 'updated', 'modified', 'timestamp', 
    'effective', 'expiry'
]
```

## Visual Improvements

### 1. Color-Coded Status Indicators
- **Green**: Exact matches (high confidence)
- **Yellow**: Partial matches (medium confidence)
- **Blue**: Semantic matches (moderate confidence)
- **Purple**: AI suggested (new suggestions)
- **Indigo**: New table mappings (high confidence for new tables)
- **Red**: Unmatched (low confidence)

### 2. Enhanced Confidence Display
- Progress bars for confidence levels
- Percentage-based confidence scoring
- Detailed breakdown of match types

### 3. Action Suggestion Cards
- Priority-based color coding
- Interactive action buttons
- Similarity scores for existing configs

## Testing

### Test Script
- **File**: `test_enhanced_features.py`
- **Tests**:
  - Table name suggestions
  - Column mapping generation
  - New table handling
  - Geometry field detection
  - Upload action suggestions
  - Confidence alignment

### Test Coverage
1. **Existing Tables**: Verify proper mapping to known table patterns
2. **New Tables**: Test AI-generated mappings with appropriate data types
3. **Geometry Tables**: Ensure geometry fields are properly detected
4. **Action Suggestions**: Verify suggestion generation and similarity scoring
5. **Confidence Alignment**: Ensure table and column confidence are consistent

## Usage Examples

### 1. New Table Creation
```javascript
// When user selects a new table name
const mappings = await generateColumnMappings({
  headers: ["property_id", "address", "value", "geometry"],
  staging_table_name: "custom_properties_staging"
});

// Results in:
// - property_id → property_id (text) - new_table
// - address → address (text) - new_table  
// - value → value (decimal) - new_table
// - geometry → geometry (geometry) - new_table
// Overall confidence: 85%
```

### 2. Action Suggestions
```javascript
// After file selection
const suggestions = await getActionSuggestions({
  headers: ["postcode", "property_address", "rateable_value"],
  file_name: "property_data.csv"
});

// Returns:
// - Save Configuration (high priority)
// - Use 'Property Config 2023' (85% similarity) - high priority
// - AI Analysis (medium priority)
// - Proceed with Upload (low priority)
```

### 3. Confidence Alignment
```javascript
// Table suggestion: onspd_staging (90% confidence)
// Column mappings: 85% confidence (exact + partial matches)
// Result: Aligned confidence levels
```

## Benefits

### 1. Improved User Experience
- **Clear Guidance**: Users know what to do after file selection
- **Confidence Alignment**: Consistent confidence levels across features
- **Better Visual Feedback**: Color-coded status indicators

### 2. Enhanced Data Quality
- **Better Data Types**: Improved inference for new tables
- **Geometry Support**: Proper detection of spatial data
- **Consistent Mappings**: Reliable column mapping generation

### 3. Increased Productivity
- **Faster Setup**: Action suggestions reduce decision time
- **Reusable Configs**: Easy access to existing configurations
- **AI Assistance**: Intelligent suggestions for complex files

## Future Enhancements

### 1. Advanced Data Type Inference
- Machine learning-based type detection
- Content-based type validation
- Custom type pattern definitions

### 2. Enhanced Action Suggestions
- User behavior learning
- Contextual suggestions based on file history
- Integration with external data sources

### 3. Improved Confidence Scoring
- Multi-factor confidence calculation
- User feedback integration
- Historical accuracy tracking

## Conclusion

These enhancements address the user's feedback by:

1. **Fixing confidence alignment** between table suggestions and column mappings
2. **Improving new table handling** with better data type inference and geometry detection
3. **Adding upload action suggestions** to guide users through the workflow

The improvements provide a more intuitive, reliable, and productive data ingestion experience while maintaining backward compatibility with existing functionality. 