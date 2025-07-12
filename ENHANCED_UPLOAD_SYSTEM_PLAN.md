# Enhanced Upload System - Comprehensive Implementation Plan

## Overview

This document outlines the comprehensive enhancements needed to meet all user requirements for the Side Bar 'Upload' Data Section. The plan addresses each requirement systematically while building upon the existing robust foundation.

## Current System Status

### ✅ **Already Implemented (Strong Foundation)**
- **Staging Schema**: Separate `staging` schema with proper isolation
- **AI Analysis**: Comprehensive file type detection and standards compliance
- **File Upload**: Drag & drop and file selection functionality
- **Configuration Management**: Staging configs with column mappings
- **Metadata Tracking**: Upload history and audit trails
- **Multiple File Types**: CSV, JSON, XML, GML, ZIP, GeoPackage, Shapefile support
- **Action Suggestions**: Upload action suggestions after file selection

### 🔄 **Required Enhancements**
1. **Real-time table name search** during mapping design
2. **75% match threshold** for auto-loading existing configs
3. **Comprehensive mapping design** with source file data integration
4. **ZIP file handling** with separate header files
5. **Fixed-length text file** analysis
6. **Create table functionality** after config save
7. **Enhanced metadata tracking** with detailed audit history

## Detailed Enhancement Plan

### 1. Real-Time Table Name Search

**Current State**: Table suggestions are generated once during file analysis
**Enhancement**: Real-time search as user types in mapping interface

#### Implementation:
```javascript
// Enhanced StagingTableAutocomplete component
const StagingTableAutocomplete = ({ 
  value, 
  onChange, 
  onTableSelect,
  realTimeSearch = true 
}) => {
  const [suggestions, setSuggestions] = useState([]);
  const [searching, setSearching] = useState(false);
  
  // Real-time search as user types
  const handleInputChange = async (inputValue) => {
    if (realTimeSearch && inputValue.length >= 2) {
      setSearching(true);
      try {
        const response = await api.post('/admin/staging/search-tables', {
          query: inputValue,
          limit: 10
        });
        setSuggestions(response.data.suggestions);
      } catch (error) {
        console.error('Table search failed:', error);
      } finally {
        setSearching(false);
      }
    }
  };
  
  return (
    <div className="relative">
      <input
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
          handleInputChange(e.target.value);
        }}
        placeholder="Search or type table name..."
        className="w-full px-3 py-2 border rounded-lg"
      />
      {searching && <div className="absolute right-3 top-2">🔍</div>}
      {suggestions.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg">
          {suggestions.map((suggestion, index) => (
            <div
              key={index}
              onClick={() => onTableSelect(suggestion)}
              className="px-3 py-2 hover:bg-gray-100 cursor-pointer"
            >
              <div className="font-medium">{suggestion.name}</div>
              <div className="text-sm text-gray-600">{suggestion.description}</div>
              <div className="text-xs text-gray-500">Match: {suggestion.confidence}%</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

#### Backend API Enhancement:
```python
@router.post("/staging/search-tables")
async def search_staging_tables(
    request: dict,
    db: Session = Depends(get_db)
):
    """Real-time table name search"""
    query = request.get("query", "").lower()
    limit = request.get("limit", 10)
    
    # Search existing tables
    existing_tables = []
    if query:
        tables_query = text("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns 
                    WHERE table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public' 
            AND table_name LIKE :pattern
            ORDER BY table_name
            LIMIT :limit
        """)
        
        result = db.execute(tables_query, {
            "pattern": f"%{query}%",
            "limit": limit
        })
        
        for row in result.fetchall():
            existing_tables.append({
                "name": row[0],
                "type": "existing",
                "confidence": calculate_name_similarity(query, row[0]),
                "description": f"Existing table with {row[1]} columns"
            })
    
    # Generate AI suggestions
    ai_suggestions = generate_table_suggestions(query)
    
    # Combine and sort by confidence
    all_suggestions = existing_tables + ai_suggestions
    all_suggestions.sort(key=lambda x: x["confidence"], reverse=True)
    
    return {
        "suggestions": all_suggestions[:limit],
        "query": query
    }
```

### 2. 75% Match Threshold for Auto-Loading Configs

**Current State**: Configs are suggested but not auto-loaded
**Enhancement**: Auto-load configs with ≥75% similarity

#### Implementation:
```javascript
// Enhanced config matching logic
const useConfigMatching = (headers, fileType, fileName) => {
  const [matchedConfig, setMatchedConfig] = useState(null);
  const [similarConfigs, setSimilarConfigs] = useState([]);
  
  const findMatchingConfigs = async () => {
    try {
      const response = await api.post('/admin/staging/configs/match', {
        headers,
        file_type: fileType,
        file_name: fileName
      });
      
      const { configs, best_match } = response.data;
      
      // Auto-load if best match ≥75%
      if (best_match && best_match.similarity >= 0.75) {
        setMatchedConfig(best_match);
        toast.success(`Auto-loaded config: ${best_match.config_name} (${Math.round(best_match.similarity * 100)}% match)`);
      }
      
      // Show other similar configs
      setSimilarConfigs(configs.filter(c => c.similarity >= 0.5));
      
    } catch (error) {
      console.error('Config matching failed:', error);
    }
  };
  
  return { matchedConfig, similarConfigs, findMatchingConfigs };
};
```

#### Backend Enhancement:
```python
def calculate_config_similarity(headers, file_name, file_type, config):
    """Enhanced similarity calculation with 75% threshold logic"""
    score = 0.0
    
    # Header similarity (weighted by importance)
    header_similarity = calculate_header_similarity(headers, config.get("headers", []))
    score += header_similarity * 0.6  # 60% weight for headers
    
    # File pattern matching
    if config.get("file_pattern") and file_name:
        pattern_match = calculate_pattern_match(file_name, config["file_pattern"])
        score += pattern_match * 0.2  # 20% weight for file patterns
    
    # File type matching
    if config.get("file_type") == file_type:
        score += 0.1  # 10% weight for file type
    
    # Content analysis matching
    content_similarity = analyze_content_similarity(headers, config)
    score += content_similarity * 0.1  # 10% weight for content
    
    return min(score, 1.0)

def calculate_header_similarity(source_headers, config_headers):
    """Calculate header similarity with semantic matching"""
    if not config_headers:
        return 0.0
    
    source_set = set(h.lower() for h in source_headers)
    config_set = set(h.lower() for h in config_headers)
    
    # Exact matches
    exact_matches = len(source_set.intersection(config_set))
    
    # Semantic matches (using AI analysis)
    semantic_matches = calculate_semantic_matches(source_headers, config_headers)
    
    total_possible = max(len(source_headers), len(config_headers))
    similarity = (exact_matches + semantic_matches * 0.8) / total_possible
    
    return similarity
```

### 3. Comprehensive Mapping Design with Source Data

**Current State**: Basic column mapping interface
**Enhancement**: Rich mapping interface with source data preview and validation

#### Implementation:
```javascript
// Enhanced Column Mapping Interface
const ComprehensiveMappingDesign = ({ 
  file, 
  headers, 
  sourceData, 
  onMappingComplete 
}) => {
  const [mappings, setMappings] = useState([]);
  const [selectedColumn, setSelectedColumn] = useState(null);
  const [sourcePreview, setSourcePreview] = useState({});
  
  // Load source data preview for selected column
  const loadSourcePreview = async (columnIndex) => {
    try {
      const response = await api.post('/admin/staging/preview-column', {
        file_id: file.id,
        column_index: columnIndex,
        sample_size: 50
      });
      
      setSourcePreview({
        column: headers[columnIndex],
        values: response.data.values,
        dataTypes: response.data.data_types,
        patterns: response.data.patterns,
        quality: response.data.quality_metrics
      });
    } catch (error) {
      console.error('Failed to load column preview:', error);
    }
  };
  
  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Left: Mapping Configuration */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Column Mappings</h3>
        
        {headers.map((header, index) => (
          <ColumnMappingCard
            key={index}
            header={header}
            index={index}
            mapping={mappings[index]}
            onMappingChange={(mapping) => {
              const newMappings = [...mappings];
              newMappings[index] = mapping;
              setMappings(newMappings);
            }}
            onSelect={() => {
              setSelectedColumn(index);
              loadSourcePreview(index);
            }}
            isSelected={selectedColumn === index}
          />
        ))}
      </div>
      
      {/* Right: Source Data Preview */}
      {selectedColumn !== null && sourcePreview.column && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">
            Source Data: {sourcePreview.column}
          </h3>
          
          {/* Data Type Analysis */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium mb-2">Detected Data Types</h4>
            <div className="space-y-2">
              {sourcePreview.dataTypes?.map((type, idx) => (
                <div key={idx} className="flex justify-between">
                  <span>{type.type}</span>
                  <span className="text-gray-600">{Math.round(type.confidence * 100)}%</span>
                </div>
              ))}
            </div>
          </div>
          
          {/* Sample Values */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium mb-2">Sample Values</h4>
            <div className="max-h-40 overflow-y-auto space-y-1">
              {sourcePreview.values?.map((value, idx) => (
                <div key={idx} className="text-sm font-mono bg-white p-1 rounded">
                  {value}
                </div>
              ))}
            </div>
          </div>
          
          {/* Quality Metrics */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium mb-2">Quality Metrics</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Completeness</span>
                <span>{Math.round(sourcePreview.quality?.completeness * 100)}%</span>
              </div>
              <div className="flex justify-between">
                <span>Consistency</span>
                <span>{Math.round(sourcePreview.quality?.consistency * 100)}%</span>
              </div>
              <div className="flex justify-between">
                <span>Uniqueness</span>
                <span>{Math.round(sourcePreview.quality?.uniqueness * 100)}%</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
```

### 4. ZIP File Handling with Separate Header Files

**Current State**: Basic ZIP analysis
**Enhancement**: Intelligent ZIP processing with header file detection

#### Implementation:
```javascript
// Enhanced ZIP Analyzer
const ZIPIntelligentAnalyzer = ({ zipContents, onFileSelection }) => {
  const [selectedFiles, setSelectedFiles] = useState({
    headers: null,
    data: [],
    metadata: []
  });
  
  const analyzeZIPStructure = (contents) => {
    const analysis = {
      headerFiles: [],
      dataFiles: [],
      metadataFiles: [],
      structure: {}
    };
    
    // Identify header files
    analysis.headerFiles = contents.files.filter(file => {
      const name = file.name.toLowerCase();
      return name.includes('header') || 
             name.includes('schema') || 
             name.includes('readme') ||
             name.includes('metadata') ||
             (name.endsWith('.csv') && file.size < 10000); // Small CSV likely header
    });
    
    // Identify data files
    analysis.dataFiles = contents.files.filter(file => {
      const name = file.name.toLowerCase();
      const isDataDir = name.includes('data') || 
                       name.includes('records') || 
                       name.includes('values');
      const isLargeFile = file.size > 10000;
      return isDataDir || (isLargeFile && name.endsWith('.csv'));
    });
    
    // Identify metadata files
    analysis.metadataFiles = contents.files.filter(file => {
      const name = file.name.toLowerCase();
      return name.includes('metadata') || 
             name.includes('info') || 
             name.includes('description') ||
             name.endsWith('.json') ||
             name.endsWith('.xml');
    });
    
    return analysis;
  };
  
  const handleFileSelection = (file, type) => {
    setSelectedFiles(prev => ({
      ...prev,
      [type]: file
    }));
    
    // Auto-detect related files
    if (type === 'headers' && file) {
      const relatedDataFiles = findRelatedDataFiles(file, zipContents);
      setSelectedFiles(prev => ({
        ...prev,
        data: relatedDataFiles
      }));
    }
  };
  
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">ZIP File Analysis</h3>
      
      {/* Header Files */}
      {analysis.headerFiles.length > 0 && (
        <div className="bg-blue-50 p-4 rounded-lg">
          <h4 className="font-medium mb-2">Header/Schema Files</h4>
          <div className="space-y-2">
            {analysis.headerFiles.map((file, idx) => (
              <FileSelectionCard
                key={idx}
                file={file}
                type="headers"
                onSelect={() => handleFileSelection(file, 'headers')}
                isSelected={selectedFiles.headers?.name === file.name}
              />
            ))}
          </div>
        </div>
      )}
      
      {/* Data Files */}
      {analysis.dataFiles.length > 0 && (
        <div className="bg-green-50 p-4 rounded-lg">
          <h4 className="font-medium mb-2">Data Files</h4>
          <div className="space-y-2">
            {analysis.dataFiles.map((file, idx) => (
              <FileSelectionCard
                key={idx}
                file={file}
                type="data"
                onSelect={() => handleFileSelection(file, 'data')}
                isSelected={selectedFiles.data.some(f => f.name === file.name)}
              />
            ))}
          </div>
        </div>
      )}
      
      {/* Directory Structure */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="font-medium mb-2">Directory Structure</h4>
        <DirectoryTree node={zipContents.directoryStructure} />
      </div>
    </div>
  );
};
```

### 5. Fixed-Length Text File Analysis

**Current State**: Basic text file detection
**Enhancement**: AI-powered fixed-length text analysis

#### Implementation:
```python
# Enhanced text file analysis
def analyze_fixed_length_text(content: str, file_name: str) -> Dict[str, Any]:
    """Analyze fixed-length text files with AI pattern detection"""
    
    analysis = {
        'type': 'fixed_length_text',
        'detected_format': None,
        'field_definitions': [],
        'sample_records': [],
        'quality_metrics': {},
        'suggested_mappings': []
    }
    
    # Split into lines and analyze
    lines = content.split('\n')
    if not lines:
        return analysis
    
    # Detect record length
    record_lengths = [len(line) for line in lines if line.strip()]
    if not record_lengths:
        return analysis
    
    # Find most common record length
    from collections import Counter
    length_counts = Counter(record_lengths)
    common_length = length_counts.most_common(1)[0][0]
    
    analysis['record_length'] = common_length
    analysis['total_records'] = len([l for l in lines if len(l) == common_length])
    
    # Analyze field patterns
    field_patterns = detect_field_patterns(lines, common_length)
    analysis['field_definitions'] = field_patterns
    
    # Generate sample records
    sample_lines = [line for line in lines if len(line) == common_length][:5]
    analysis['sample_records'] = [
        {
            'raw': line,
            'parsed': parse_fixed_length_record(line, field_patterns)
        }
        for line in sample_lines
    ]
    
    # Suggest mappings
    analysis['suggested_mappings'] = generate_fixed_length_mappings(field_patterns)
    
    return analysis

def detect_field_patterns(lines: List[str], record_length: int) -> List[Dict]:
    """Detect field patterns in fixed-length text"""
    
    patterns = []
    current_pos = 0
    
    # Analyze multiple records to detect patterns
    sample_records = [line for line in lines if len(line) == record_length][:10]
    
    while current_pos < record_length:
        # Extract column at current position
        column_values = [record[current_pos:current_pos+1] for record in sample_records]
        
        # Analyze pattern
        pattern = analyze_column_pattern(column_values, current_pos)
        patterns.append(pattern)
        
        # Move to next position
        current_pos += pattern.get('width', 1)
    
    return patterns

def analyze_column_pattern(values: List[str], position: int) -> Dict:
    """Analyze pattern of values in a column"""
    
    # Detect data type
    data_type = infer_fixed_length_data_type(values)
    
    # Detect field width
    width = detect_field_width(values, position)
    
    # Detect field name
    field_name = suggest_field_name(values, data_type, position)
    
    return {
        'position': position,
        'width': width,
        'data_type': data_type,
        'field_name': field_name,
        'sample_values': values[:5],
        'confidence': calculate_pattern_confidence(values, data_type)
    }
```

### 6. Create Table Functionality

**Current State**: Configs are saved but tables aren't created
**Enhancement**: Automatic table creation after config save

#### Implementation:
```javascript
// Enhanced config saving with table creation
const saveConfigAndCreateTable = async (config) => {
  try {
    // Step 1: Save configuration
    const saveResponse = await api.post('/admin/staging/configs', config);
    const configId = saveResponse.data.config_id;
    
    // Step 2: Create table
    const createResponse = await api.post('/admin/staging/create-table', {
      config_id: configId,
      table_name: config.staging_table_name
    });
    
    toast.success(`Configuration saved and table created: ${config.staging_table_name}`);
    
    return {
      configId,
      tableName: config.staging_table_name,
      success: true
    };
    
  } catch (error) {
    console.error('Failed to save config and create table:', error);
    toast.error('Failed to save configuration');
    throw error;
  }
};
```

#### Backend Implementation:
```python
@router.post("/staging/create-table")
async def create_staging_table(
    request: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """Create staging table from configuration"""
    
    config_id = request.get("config_id")
    table_name = request.get("table_name")
    
    # Get configuration
    config = get_staging_config(config_id, db)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Generate CREATE TABLE SQL
    create_sql = generate_create_table_sql(config, table_name)
    
    try:
        # Execute CREATE TABLE
        db.execute(text(create_sql))
        db.commit()
        
        # Log table creation
        log_table_creation(db, table_name, config_id, user.username)
        
        return {
            "success": True,
            "table_name": table_name,
            "message": f"Table {table_name} created successfully"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create table {table_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create table: {str(e)}")

def generate_create_table_sql(config: Dict, table_name: str) -> str:
    """Generate CREATE TABLE SQL from configuration"""
    
    # Start CREATE TABLE statement
    sql_parts = [f"CREATE TABLE IF NOT EXISTS {table_name} ("]
    
    # Add column definitions
    column_definitions = []
    for mapping in config.get("column_mappings", []):
        column_def = f"    {mapping['target_column']} {mapping['data_type']}"
        
        # Add constraints
        if mapping.get("is_required"):
            column_def += " NOT NULL"
        if mapping.get("is_primary_key"):
            column_def += " PRIMARY KEY"
        if mapping.get("is_unique"):
            column_def += " UNIQUE"
        
        column_definitions.append(column_def)
    
    # Add standard metadata columns
    metadata_columns = [
        "    source_name TEXT",
        "    upload_user TEXT",
        "    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "    batch_id TEXT",
        "    source_file TEXT",
        "    file_size BIGINT",
        "    file_modified TIMESTAMP",
        "    session_id TEXT",
        "    client_name TEXT"
    ]
    
    all_columns = column_definitions + metadata_columns
    sql_parts.append(",\n".join(all_columns))
    sql_parts.append(");")
    
    return "\n".join(sql_parts)
```

### 7. Enhanced Metadata Tracking

**Current State**: Basic upload history
**Enhancement**: Comprehensive audit trail with detailed tracking

#### Implementation:
```python
# Enhanced metadata tracking
@router.post("/staging/upload-with-metadata")
async def upload_with_comprehensive_metadata(
    file: UploadFile = File(...),
    config_id: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    client_name: Optional[str] = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload file with comprehensive metadata tracking"""
    
    # Generate unique identifiers
    batch_id = generate_batch_id()
    upload_id = str(uuid.uuid4())
    
    # File metadata
    file_metadata = {
        'filename': file.filename,
        'size': file.size,
        'content_type': file.content_type,
        'upload_timestamp': datetime.now(),
        'file_hash': calculate_file_hash(file)
    }
    
    # User metadata
    user_metadata = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'session_id': session_id or generate_session_id(),
        'client_name': client_name or 'web_upload'
    }
    
    # Process metadata
    process_metadata = {
        'batch_id': batch_id,
        'upload_id': upload_id,
        'config_id': config_id,
        'processing_start': datetime.now(),
        'status': 'uploaded'
    }
    
    try:
        # Save file
        file_path = save_uploaded_file(file, batch_id)
        
        # Log comprehensive metadata
        log_comprehensive_metadata(
            db, 
            file_metadata, 
            user_metadata, 
            process_metadata,
            file_path
        )
        
        # Start processing if config provided
        if config_id:
            process_metadata['status'] = 'processing'
            update_metadata_status(db, upload_id, 'processing')
            
            # Trigger background processing
            background_tasks.add_task(
                process_uploaded_file,
                upload_id,
                file_path,
                config_id,
                batch_id
            )
        
        return {
            "success": True,
            "upload_id": upload_id,
            "batch_id": batch_id,
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        # Log error
        log_upload_error(db, upload_id, str(e), user_metadata)
        raise HTTPException(status_code=500, detail=str(e))

def log_comprehensive_metadata(
    db: Session,
    file_metadata: Dict,
    user_metadata: Dict,
    process_metadata: Dict,
    file_path: str
):
    """Log comprehensive metadata for audit trail"""
    
    # Insert into upload_metadata table
    metadata_sql = text("""
        INSERT INTO upload_metadata (
            upload_id, batch_id, config_id, filename, file_size, 
            content_type, file_hash, file_path, upload_timestamp,
            user_id, username, user_role, session_id, client_name,
            processing_start, status, created_at
        ) VALUES (
            :upload_id, :batch_id, :config_id, :filename, :file_size,
            :content_type, :file_hash, :file_path, :upload_timestamp,
            :user_id, :username, :user_role, :session_id, :client_name,
            :processing_start, :status, NOW()
        )
    """)
    
    db.execute(metadata_sql, {
        'upload_id': process_metadata['upload_id'],
        'batch_id': process_metadata['batch_id'],
        'config_id': process_metadata['config_id'],
        'filename': file_metadata['filename'],
        'file_size': file_metadata['size'],
        'content_type': file_metadata['content_type'],
        'file_hash': file_metadata['file_hash'],
        'file_path': file_path,
        'upload_timestamp': file_metadata['upload_timestamp'],
        'user_id': user_metadata['user_id'],
        'username': user_metadata['username'],
        'user_role': user_metadata['role'],
        'session_id': user_metadata['session_id'],
        'client_name': user_metadata['client_name'],
        'processing_start': process_metadata['processing_start'],
        'status': process_metadata['status']
    })
    
    db.commit()
```

## Database Schema Enhancements

### New Tables for Enhanced Functionality:

```sql
-- Enhanced metadata tracking
CREATE TABLE IF NOT EXISTS upload_metadata (
    id SERIAL PRIMARY KEY,
    upload_id UUID NOT NULL,
    batch_id TEXT NOT NULL,
    config_id UUID REFERENCES staging_configs(id),
    filename TEXT NOT NULL,
    file_size BIGINT,
    content_type TEXT,
    file_hash TEXT,
    file_path TEXT,
    upload_timestamp TIMESTAMP WITH TIME ZONE,
    user_id INTEGER,
    username TEXT,
    user_role TEXT,
    session_id TEXT,
    client_name TEXT,
    processing_start TIMESTAMP WITH TIME ZONE,
    processing_end TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'uploaded',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit trail for all operations
CREATE TABLE IF NOT EXISTS audit_trail (
    id SERIAL PRIMARY KEY,
    operation_type TEXT NOT NULL, -- 'upload', 'config_save', 'table_create', 'data_process'
    operation_id TEXT NOT NULL,
    user_id INTEGER,
    username TEXT,
    table_name TEXT,
    record_count INTEGER,
    operation_details JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fixed-length text file configurations
CREATE TABLE IF NOT EXISTS fixed_length_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    record_length INTEGER NOT NULL,
    field_definitions JSONB NOT NULL,
    created_by TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Implementation Timeline

### Phase 1: Core Enhancements (Week 1-2)
1. ✅ Real-time table name search
2. ✅ 75% config matching threshold
3. ✅ Enhanced metadata tracking

### Phase 2: Advanced Features (Week 3-4)
1. ✅ Comprehensive mapping design
2. ✅ Create table functionality
3. ✅ ZIP file handling improvements

### Phase 3: Specialized Formats (Week 5-6)
1. ✅ Fixed-length text file analysis
2. ✅ Enhanced AI analysis for all formats
3. ✅ Quality improvements and testing

## Testing Strategy

### Unit Tests
- Table search functionality
- Config matching algorithms
- File type detection
- Metadata tracking

### Integration Tests
- End-to-end upload workflow
- ZIP file processing
- Fixed-length text analysis
- Table creation process

### Performance Tests
- Large file uploads
- Real-time search performance
- Database query optimization

## Success Metrics

1. **User Experience**: Reduced time from file selection to data ingestion
2. **Accuracy**: Improved config matching and table creation success rate
3. **Performance**: Faster upload and processing times
4. **Reliability**: Reduced errors and improved error handling
5. **Audit Compliance**: Complete audit trail for all operations

This comprehensive plan addresses all user requirements while building upon the existing robust foundation, ensuring a smooth and efficient data ingestion experience. 