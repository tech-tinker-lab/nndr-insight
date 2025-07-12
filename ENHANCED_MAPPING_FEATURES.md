# Enhanced AI Column Mapping Features

## Overview

The enhanced staging table system now includes intelligent AI-powered column mapping generation with color-coded match statuses, automatic mapping refresh, and comprehensive visual feedback.

## 🎯 Key Features Implemented

### 1. **AI-Generated Column Mappings**
When a staging table is selected from the autocomplete, the system automatically generates intelligent column mappings using AI analysis.

**How it works:**
- Analyzes file headers against known table patterns
- Generates mappings with confidence scores
- Provides reasoning for each mapping decision
- Supports both existing and new tables

### 2. **Color-Coded Match Statuses**
Each column mapping is visually categorized with distinct colors and icons:

| Status | Color | Icon | Description | Confidence |
|--------|-------|------|-------------|------------|
| **Exact Match** | 🟢 Green | ✅ CheckCircle | Perfect header-to-column match | 100% |
| **Partial Match** | 🟡 Yellow | ⚠️ AlertCircle | Header contains target column name | 80% |
| **Semantic Match** | 🔵 Blue | 🕐 Clock | Related concepts (e.g., "postcode" → "pcds") | 60% |
| **AI Suggested** | 🟣 Purple | ✨ Sparkles | AI-generated default mapping | 40% |
| **Unmatched** | 🔴 Red | ❌ AlertCircle | No match found | 0% |

### 3. **Automatic Mapping Refresh**
- **For Existing Tables**: Refreshes mappings when table is selected
- **For New Tables**: Generates AI-suggested mappings with sensible defaults
- **Regenerate Button**: Allows manual regeneration of mappings with updated AI analysis

## 🔧 Technical Implementation

### Backend API: `/api/admin/staging/generate-mappings`

**Request:**
```json
{
  "headers": ["pcd", "pcd2", "pcds", "x_coord", "y_coord"],
  "staging_table_name": "onspd_staging",
  "file_name": "onspd_2024.csv",
  "content_preview": "Sample content..."
}
```

**Response:**
```json
{
  "mappings": [
    {
      "id": "mapping_0",
      "sourceColumn": "pcd",
      "targetColumn": "pcd",
      "mappingType": "direct",
      "dataType": "varchar(8)",
      "isRequired": true,
      "confidence": 1.0,
      "matchStatus": "exact",
      "reason": "Exact match for onspd_staging"
    },
    {
      "id": "mapping_1",
      "sourceColumn": "postcode",
      "targetColumn": "pcds",
      "mappingType": "direct",
      "dataType": "varchar(8)",
      "isRequired": true,
      "confidence": 0.8,
      "matchStatus": "semantic",
      "reason": "Semantic match: 'postcode' relates to 'postcode'"
    }
  ],
  "match_status": {
    "status": "excellent",
    "confidence": 0.9,
    "color": "green",
    "message": "Excellent match (90.0%)"
  },
  "suggestions": [
    {
      "type": "info",
      "message": "Consider mapping 'date_field' to a date/timestamp field",
      "action": "suggest_date_mapping"
    }
  ]
}
```

### Frontend Component: `EnhancedColumnMapping`

**Features:**
- **Visual Status Indicators**: Color-coded backgrounds and icons
- **Confidence Scoring**: Percentage-based confidence with color coding
- **Expandable Details**: Click to show advanced mapping options
- **Real-time Updates**: Live updates as mappings are modified
- **Summary Statistics**: Overview of mapping quality

## 🎨 Visual Design System

### Color Scheme
```css
/* Exact Match - Green */
.exact-match {
  background-color: rgb(240 253 244); /* bg-green-50 */
  border-color: rgb(187 247 208);     /* border-green-200 */
  color: rgb(22 101 52);              /* text-green-800 */
}

/* Partial Match - Yellow */
.partial-match {
  background-color: rgb(254 252 232); /* bg-yellow-50 */
  border-color: rgb(254 240 138);     /* border-yellow-200 */
  color: rgb(113 63 18);              /* text-yellow-800 */
}

/* Semantic Match - Blue */
.semantic-match {
  background-color: rgb(239 246 255); /* bg-blue-50 */
  border-color: rgb(191 219 254);     /* border-blue-200 */
  color: rgb(30 64 175);              /* text-blue-800 */
}

/* AI Suggested - Purple */
.suggested-match {
  background-color: rgb(250 245 255); /* bg-purple-50 */
  border-color: rgb(233 213 255);     /* border-purple-200 */
  color: rgb(88 28 135);              /* text-purple-800 */
}

/* Unmatched - Red */
.unmatched {
  background-color: rgb(254 242 242); /* bg-red-50 */
  border-color: rgb(254 202 202);     /* border-red-200 */
  color: rgb(153 27 27);              /* text-red-800 */
}
```

### Icon System
- ✅ **CheckCircle** (Green): Exact matches
- ⚠️ **AlertCircle** (Yellow): Partial matches
- 🕐 **Clock** (Blue): Semantic matches
- ✨ **Sparkles** (Purple): AI suggestions
- ❌ **AlertCircle** (Red): Unmatched

## 🧠 AI Mapping Algorithm

### 1. **Pattern Recognition**
```python
# Table-specific mapping patterns
patterns = {
    'onspd_staging': {
        'pcd': {'target': 'pcd', 'type': 'varchar(8)', 'required': True},
        'pcd2': {'target': 'pcd2', 'type': 'varchar(8)', 'required': False},
        'pcds': {'target': 'pcds', 'type': 'varchar(8)', 'required': True},
        'x_coord': {'target': 'x_coord', 'type': 'numeric(10,6)', 'required': False},
        'y_coord': {'target': 'y_coord', 'type': 'numeric(10,6)', 'required': False}
    }
}
```

### 2. **Semantic Matching**
```python
semantic_matches = {
    'postcode': ['postcode', 'post_code', 'pcd', 'pcds'],
    'address': ['address', 'property_address', 'full_address'],
    'name': ['name', 'names', 'title', 'description'],
    'value': ['value', 'amount', 'rateable_value', 'valuation'],
    'coordinate': ['coordinate', 'coord', 'x_coord', 'y_coord', 'lat', 'long'],
    'geometry': ['geometry', 'geom', 'shape', 'polygon'],
    'id': ['id', 'identifier', 'reference', 'code']
}
```

### 3. **Data Type Inference**
```python
def infer_data_type(header, content_preview):
    header_lower = header.lower()
    
    if any(keyword in header_lower for keyword in ['date', 'time']):
        return 'timestamp'
    elif any(keyword in header_lower for keyword in ['amount', 'value', 'price']):
        return 'decimal'
    elif any(keyword in header_lower for keyword in ['count', 'number', 'id']):
        return 'integer'
    elif any(keyword in header_lower for keyword in ['flag', 'is_', 'has_']):
        return 'boolean'
    elif any(keyword in header_lower for keyword in ['geometry', 'geom']):
        return 'geometry'
    else:
        return 'text'
```

## 📊 Match Status Calculation

### Overall Match Status
```python
def calculate_mapping_match_status(headers, mappings, existing_columns):
    if not existing_columns:
        return {
            "status": "new_table",
            "confidence": 0.7,
            "color": "blue",
            "message": "New table - AI-generated mappings"
        }
    
    # Calculate weighted match percentage
    exact_matches = sum(1 for m in mappings if m["matchStatus"] == "exact")
    partial_matches = sum(1 for m in mappings if m["matchStatus"] == "partial")
    semantic_matches = sum(1 for m in mappings if m["matchStatus"] == "semantic")
    
    total = len(mappings)
    match_percentage = (exact_matches + partial_matches * 0.8 + semantic_matches * 0.6) / total
    
    # Return status based on percentage
    if match_percentage >= 0.8:
        return {"status": "excellent", "confidence": match_percentage, "color": "green"}
    elif match_percentage >= 0.6:
        return {"status": "good", "confidence": match_percentage, "color": "yellow"}
    elif match_percentage >= 0.4:
        return {"status": "fair", "confidence": match_percentage, "color": "orange"}
    else:
        return {"status": "poor", "confidence": match_percentage, "color": "red"}
```

## 🚀 Usage Examples

### 1. **Select Existing Table**
```jsx
<StagingTableAutocomplete
  value={stagingTableName}
  onChange={setStagingTableName}
  headers={fileHeaders}
  fileName={fileName}
  onTableSelect={(data) => {
    // Automatically generates mappings when table is selected
    setMappings(data.mappings);
    setMatchStatus(data.match_status);
    setSuggestions(data.suggestions);
  }}
/>
```

### 2. **Enhanced Column Mapping Display**
```jsx
<EnhancedColumnMapping
  mappings={mappings}
  onMappingsChange={setMappings}
  matchStatus={matchStatus}
  suggestions={suggestions}
/>
```

### 3. **Regenerate Mappings**
```jsx
<button
  onClick={() => {
    // Regenerate mappings with updated AI analysis
    api.post('/api/admin/staging/generate-mappings', {
      headers: fileHeaders,
      staging_table_name: selectedTable,
      file_name: fileName
    }).then(response => {
      setMappings(response.data.mappings);
      setMatchStatus(response.data.match_status);
    });
  }}
>
  <RefreshCw className="w-4 h-4" />
  Regenerate AI
</button>
```

## 📈 Benefits

### 1. **Improved User Experience**
- **Visual Clarity**: Color-coded statuses make mapping quality immediately apparent
- **Reduced Errors**: AI suggestions prevent incorrect mappings
- **Faster Setup**: Automatic mapping generation saves time
- **Better Feedback**: Clear confidence scores and reasoning

### 2. **Enhanced Data Quality**
- **Consistent Mappings**: AI ensures consistent column naming
- **Type Safety**: Automatic data type inference
- **Validation**: Required field detection and warnings
- **Best Practices**: Follows established patterns

### 3. **Developer Productivity**
- **Reusable Logic**: AI patterns can be extended for new data types
- **Maintainable Code**: Clear separation of concerns
- **Extensible System**: Easy to add new mapping patterns
- **Comprehensive Testing**: Full test coverage

## 🔮 Future Enhancements

### 1. **Advanced AI Features**
- **Machine Learning**: Train models on successful mappings
- **Natural Language**: Support for natural language column descriptions
- **Data Profiling**: Advanced data type and pattern detection
- **Context Awareness**: Consider file content and metadata

### 2. **Enhanced Visual Features**
- **Interactive Mapping**: Drag-and-drop column mapping
- **Bulk Operations**: Apply mappings to multiple files
- **Mapping Templates**: Pre-built templates for common data types
- **Visual Diff**: Show differences between current and suggested mappings

### 3. **Collaboration Features**
- **Shared Configurations**: Share successful mappings between users
- **Mapping History**: Track changes and improvements over time
- **Approval Workflows**: Review and approve mapping changes
- **Comments**: Add notes and explanations to mappings

## 🎉 Conclusion

The enhanced AI column mapping system provides a significant improvement to the data ingestion workflow by:

1. **Automatically generating** intelligent column mappings when tables are selected
2. **Visually communicating** mapping quality through color-coded statuses
3. **Providing clear feedback** on confidence levels and reasoning
4. **Supporting both existing and new** table scenarios
5. **Enabling easy regeneration** of mappings with updated AI analysis

This creates a more intuitive, efficient, and error-free data mapping experience that scales with the complexity of government data processing requirements. 