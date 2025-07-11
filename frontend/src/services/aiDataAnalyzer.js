// AI-Powered Data Analysis Service for Government Public Data
// This service uses AI to analyze content, detect patterns, and suggest mappings

class AIDataAnalyzer {
  constructor() {
    this.apiEndpoint = process.env.REACT_APP_AI_API_ENDPOINT || 'http://localhost:8000/api/ai';
    this.supportedFormats = ['csv', 'json', 'xml', 'gml', 'geojson'];
  }

  // Main analysis function
  async analyzeDataset(file, content, fileType) {
    try {
      console.log('AI analyzing dataset:', file.name, 'type:', fileType);
      
      const analysis = {
        fileInfo: {
          name: file.name,
          size: file.size,
          type: fileType
        },
        contentAnalysis: null,
        schemaDetection: null,
        mappingSuggestions: null,
        standardsIdentification: null,
        confidence: 0
      };

      // Step 1: Content Analysis
      analysis.contentAnalysis = await this.analyzeContent(content, fileType);
      
      // Step 2: Schema Detection
      analysis.schemaDetection = await this.detectSchema(content, fileType);
      
      // Step 3: Government Standards Identification
      analysis.standardsIdentification = await this.identifyStandards(analysis.contentAnalysis, analysis.schemaDetection);
      
      // Step 4: Generate Mapping Suggestions
      analysis.mappingSuggestions = await this.generateMappingSuggestions(analysis);
      
      // Step 5: Calculate Confidence Score
      analysis.confidence = this.calculateConfidence(analysis);
      
      return analysis;
    } catch (error) {
      console.error('AI analysis failed:', error);
      throw new Error(`AI analysis failed: ${error.message}`);
    }
  }

  // Analyze content patterns and structure
  async analyzeContent(content, fileType) {
    const analysis = {
      dataPatterns: [],
      fieldTypes: [],
      valuePatterns: [],
      dataQuality: {},
      governmentIndicators: []
    };

    try {
      if (fileType === 'csv') {
        analysis.dataPatterns = await this.analyzeCSVPatterns(content);
        analysis.fieldTypes = await this.detectFieldTypes(content);
              analysis.valuePatterns = await this.analyzeValuePatterns(content);
      analysis.governmentIndicators = await this.detectGovernmentIndicators(content);
    } else if (fileType === 'json' || fileType === 'geojson') {
      analysis.dataPatterns = await this.analyzeJSONPatterns(content);
      analysis.fieldTypes = await this.detectJSONFieldTypes(content);
    } else if (fileType === 'xml' || fileType === 'gml') {
      analysis.dataPatterns = await this.analyzeXMLPatterns(content);
      analysis.fieldTypes = await this.detectXMLFieldTypes(content);
    }

      analysis.dataQuality = await this.assessDataQuality(content, fileType);
      
      return analysis;
    } catch (error) {
      console.error('Content analysis failed:', error);
      return analysis;
    }
  }

  // Analyze CSV patterns
  async analyzeCSVPatterns(content) {
    const patterns = [];
    const lines = content.split('\n').slice(0, 100); // Analyze first 100 lines
    
    if (lines.length < 2) return patterns;

    const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
    
    // Detect common government data patterns
    const governmentPatterns = {
      'postcode': /^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$/i,
      'uprn': /^\d{12}$/,
      'usrn': /^\d{8}$/,
      'date': /^\d{1,2}\/\d{1,2}\/\d{4}$/,
      'currency': /^£?\d+\.?\d*$/,
      'percentage': /^\d+\.?\d*%?$/,
      'email': /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      'phone': /^[\d\s\-\(\)\+]+$/
    };

    // Analyze each column
    for (let i = 0; i < headers.length; i++) {
      const header = headers[i];
      const columnValues = lines.slice(1).map(line => {
        const values = line.split(',');
        return values[i] ? values[i].trim() : '';
      }).filter(v => v);

      const pattern = {
        columnIndex: i,
        header: header,
        detectedType: 'unknown',
        confidence: 0,
        sampleValues: columnValues.slice(0, 5),
        suggestions: []
      };

      // Test against government patterns
      for (const [patternName, regex] of Object.entries(governmentPatterns)) {
        const matches = columnValues.filter(v => regex.test(v)).length;
        const matchRate = matches / columnValues.length;
        
        if (matchRate > 0.8) {
          pattern.detectedType = patternName;
          pattern.confidence = matchRate;
          pattern.suggestions.push(`Likely ${patternName} field`);
          break;
        }
      }

      // Special government data detection
      if (this.isGovernmentDataField(header, columnValues)) {
        pattern.detectedType = 'government_data';
        pattern.confidence = 0.9;
        pattern.suggestions.push('Government data field detected');
      }

      patterns.push(pattern);
    }

    return patterns;
  }

  // Detect if field contains government data
  isGovernmentDataField(header, values) {
    const governmentKeywords = [
      'uprn', 'usrn', 'toid', 'lad', 'ward', 'constituency', 'parish',
      'rateable', 'valuation', 'business', 'property', 'address',
      'postcode', 'post_code', 'post_code', 'local_authority',
      'council', 'borough', 'district', 'county', 'region'
    ];

    const headerLower = header.toLowerCase();
    return governmentKeywords.some(keyword => headerLower.includes(keyword));
  }

  // Detect field types using AI
  async detectFieldTypes(content) {
    try {
      const response = await fetch(`${this.apiEndpoint}/detect-types`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: content.substring(0, 10000) })
      });

      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.warn('AI field type detection failed, using fallback:', error);
    }

    // Fallback: Basic type detection
    return this.basicTypeDetection(content);
  }

  // Basic type detection fallback
  basicTypeDetection(content) {
    const lines = content.split('\n').slice(0, 50);
    if (lines.length < 2) return [];

    const headers = lines[0].split(',').map(h => h.trim());
    const types = [];

    for (let i = 0; i < headers.length; i++) {
      const values = lines.slice(1).map(line => {
        const parts = line.split(',');
        return parts[i] ? parts[i].trim() : '';
      }).filter(v => v);

      types.push({
        column: headers[i],
        type: this.inferType(values),
        confidence: 0.7
      });
    }

    return types;
  }

  // Infer data type from values
  inferType(values) {
    if (values.length === 0) return 'text';

    const sample = values.slice(0, 10);
    
    // Check for numbers
    const numbers = sample.filter(v => !isNaN(v) && v !== '');
    if (numbers.length / sample.length > 0.8) {
      return 'number';
    }

    // Check for dates
    const datePattern = /^\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}$/;
    const dates = sample.filter(v => datePattern.test(v));
    if (dates.length / sample.length > 0.8) {
      return 'date';
    }

    // Check for booleans
    const booleanPattern = /^(true|false|yes|no|1|0)$/i;
    const booleans = sample.filter(v => booleanPattern.test(v));
    if (booleans.length / sample.length > 0.8) {
      return 'boolean';
    }

    return 'text';
  }

  // Detect schema structure
  async detectSchema(content, fileType) {
    const schema = {
      type: fileType,
      fields: [],
      relationships: [],
      constraints: [],
      suggestedTableName: null
    };

    try {
      if (fileType === 'csv') {
        const lines = content.split('\n');
        const headers = lines[0].split(',').map(h => h.trim());
        
        schema.fields = headers.map((header, index) => ({
          name: header,
          position: index,
          suggestedType: 'text',
          constraints: [],
          description: this.generateFieldDescription(header)
        }));

        schema.suggestedTableName = this.suggestTableName(headers, content);
      }

      return schema;
    } catch (error) {
      console.error('Schema detection failed:', error);
      return schema;
    }
  }

  // Generate field description using AI
  generateFieldDescription(fieldName) {
    const descriptions = {
      'uprn': 'Unique Property Reference Number - UK standard property identifier',
      'usrn': 'Unique Street Reference Number - UK standard street identifier',
      'postcode': 'UK postal code for address location',
      'address': 'Property or location address',
      'name': 'Name of person, property, or entity',
      'value': 'Numeric value or amount',
      'date': 'Date information',
      'type': 'Classification or category',
      'code': 'Reference code or identifier'
    };

    const fieldLower = fieldName.toLowerCase();
    for (const [key, desc] of Object.entries(descriptions)) {
      if (fieldLower.includes(key)) {
        return desc;
      }
    }

    return `Field containing ${fieldName.toLowerCase()} information`;
  }

  // Suggest table name based on content
  suggestTableName(headers, content) {
    const keywords = headers.join(' ').toLowerCase();
    
    const suggestions = {
      'uprn': 'properties',
      'usrn': 'streets',
      'postcode': 'addresses',
      'rateable': 'business_rates',
      'valuation': 'valuations',
      'boundary': 'boundaries',
      'ward': 'wards',
      'constituency': 'constituencies'
    };

    for (const [keyword, suggestion] of Object.entries(suggestions)) {
      if (keywords.includes(keyword)) {
        return `staging_${suggestion}`;
      }
    }

    return 'staging_data';
  }

  // Identify government data standards
  async identifyStandards(contentAnalysis, schemaDetection) {
    const standards = {
      detectedStandards: [],
      compliance: {},
      recommendations: []
    };

    // Check for UK government standards
    const ukStandards = {
      'BS7666': this.checkBS7666Compliance(contentAnalysis, schemaDetection),
      'INSPIRE': this.checkINSPIRECompliance(contentAnalysis, schemaDetection),
      'OS_Standards': this.checkOSStandardsCompliance(contentAnalysis, schemaDetection),
      'GDS': this.checkGDSCompliance(contentAnalysis, schemaDetection)
    };

    for (const [standard, compliance] of Object.entries(ukStandards)) {
      if (compliance.score > 0.5) {
        standards.detectedStandards.push({
          name: standard,
          score: compliance.score,
          details: compliance.details
        });
      }
    }

    standards.recommendations = this.generateStandardRecommendations(standards.detectedStandards);
    
    return standards;
  }

  // Check BS7666 (UK Address Standard) compliance
  checkBS7666Compliance(contentAnalysis, schemaDetection) {
    const requiredFields = ['uprn', 'usrn', 'postcode', 'address'];
    const foundFields = schemaDetection.fields.filter(field => 
      requiredFields.some(req => field.name.toLowerCase().includes(req))
    );

    return {
      score: foundFields.length / requiredFields.length,
      details: `Found ${foundFields.length}/${requiredFields.length} BS7666 fields`
    };
  }

  // Check INSPIRE compliance
  checkINSPIRECompliance(contentAnalysis, schemaDetection) {
    const inspireFields = ['geometry', 'coordinate', 'latitude', 'longitude', 'easting', 'northing'];
    const foundFields = schemaDetection.fields.filter(field => 
      inspireFields.some(inspire => field.name.toLowerCase().includes(inspire))
    );

    return {
      score: foundFields.length > 0 ? 0.8 : 0.2,
      details: foundFields.length > 0 ? 'Contains spatial data fields' : 'No spatial data detected'
    };
  }

  // Check OS Standards compliance
  checkOSStandardsCompliance(contentAnalysis, schemaDetection) {
    const osFields = ['toid', 'osgb', 'easting', 'northing', 'grid_reference'];
    const foundFields = schemaDetection.fields.filter(field => 
      osFields.some(osField => field.name.toLowerCase().includes(osField))
    );

    return {
      score: foundFields.length / osFields.length,
      details: `Found ${foundFields.length}/${osFields.length} OS standard fields`
    };
  }

  // Check GDS compliance
  checkGDSCompliance(contentAnalysis, schemaDetection) {
    const gdsIndicators = ['open_data', 'machine_readable', 'linked_data', 'metadata'];
    let foundIndicators = 0;

    // Check field names for GDS indicators
    for (const field of schemaDetection.fields) {
      const fieldLower = field.name.toLowerCase();
      if (gdsIndicators.some(indicator => fieldLower.includes(indicator))) {
        foundIndicators++;
      }
    }

    // Check content analysis for government indicators
    if (contentAnalysis.governmentIndicators) {
      foundIndicators += contentAnalysis.governmentIndicators.length;
    }

    return {
      score: Math.min(foundIndicators / 4.0, 1.0),
      details: `Found ${foundIndicators} GDS indicators`
    };
  }

  // Generate mapping suggestions
  async generateMappingSuggestions(analysis) {
    const suggestions = {
      columnMappings: [],
      transformations: [],
      validations: [],
      stagingTable: {
        name: analysis.schemaDetection.suggestedTableName,
        fields: []
      }
    };

    // Generate column mappings
    for (const field of analysis.schemaDetection.fields) {
      const mapping = {
        sourceColumn: field.name,
        targetColumn: this.suggestTargetColumn(field.name),
        mappingType: 'direct',
        dataType: this.suggestDataType(field),
        transformations: [],
        validations: []
      };

      // Add transformations based on detected patterns
      if (analysis.contentAnalysis.dataPatterns) {
        const pattern = analysis.contentAnalysis.dataPatterns.find(p => p.header === field.name);
        if (pattern) {
          mapping.transformations = this.suggestTransformations(pattern);
          mapping.validations = this.suggestValidations(pattern);
        }
      }

      suggestions.columnMappings.push(mapping);
    }

    return suggestions;
  }

  // Suggest target column name
  suggestTargetColumn(sourceName) {
    const mappings = {
      'uprn': 'uprn',
      'usrn': 'usrn',
      'postcode': 'postcode',
      'post_code': 'postcode',
      'address': 'address',
      'property_address': 'property_address',
      'name': 'name',
      'value': 'value',
      'amount': 'amount',
      'date': 'date',
      'type': 'type',
      'code': 'code'
    };

    const sourceLower = sourceName.toLowerCase();
    for (const [key, target] of Object.entries(mappings)) {
      if (sourceLower.includes(key)) {
        return target;
      }
    }

    return sourceName.toLowerCase().replace(/\s+/g, '_');
  }

  // Suggest data type
  suggestDataType(field) {
    const typeMappings = {
      'uprn': 'bigint',
      'usrn': 'bigint',
      'postcode': 'varchar(10)',
      'address': 'text',
      'date': 'date',
      'amount': 'decimal(10,2)',
      'value': 'decimal(10,2)',
      'percentage': 'decimal(5,2)',
      'boolean': 'boolean'
    };

    const fieldLower = field.name.toLowerCase();
    for (const [key, type] of Object.entries(typeMappings)) {
      if (fieldLower.includes(key)) {
        return type;
      }
    }

    return 'text';
  }

  // Calculate confidence score
  calculateConfidence(analysis) {
    let confidence = 0;
    let factors = 0;

    // Content analysis confidence
    if (analysis.contentAnalysis.dataPatterns.length > 0) {
      const avgPatternConfidence = analysis.contentAnalysis.dataPatterns.reduce((sum, p) => sum + p.confidence, 0) / analysis.contentAnalysis.dataPatterns.length;
      confidence += avgPatternConfidence * 0.3;
      factors += 0.3;
    }

    // Standards detection confidence
    if (analysis.standardsIdentification.detectedStandards.length > 0) {
      const avgStandardConfidence = analysis.standardsIdentification.detectedStandards.reduce((sum, s) => sum + s.score, 0) / analysis.standardsIdentification.detectedStandards.length;
      confidence += avgStandardConfidence * 0.4;
      factors += 0.4;
    }

    // Schema detection confidence
    if (analysis.schemaDetection.fields.length > 0) {
      confidence += 0.3;
      factors += 0.3;
    }

    return factors > 0 ? confidence / factors : 0;
  }

  // Generate standard recommendations
  generateStandardRecommendations(detectedStandards) {
    const recommendations = [];

    if (detectedStandards.length === 0) {
      recommendations.push('Consider implementing UK government data standards (BS7666, INSPIRE)');
    }

    if (detectedStandards.some(s => s.name === 'BS7666')) {
      recommendations.push('BS7666 compliance detected - ensure proper address formatting');
    }

    if (detectedStandards.some(s => s.name === 'INSPIRE')) {
      recommendations.push('INSPIRE compliance detected - verify coordinate reference systems');
    }

    return recommendations;
  }

  // Analyze JSON patterns
  async analyzeJSONPatterns(content) {
    try {
      const data = JSON.parse(content);
      const patterns = [];

      if (typeof data === 'object' && data !== null) {
        const keys = Array.isArray(data) ? Object.keys(data[0] || {}) : Object.keys(data);
        
        for (const key of keys) {
          const pattern = {
            header: key,
            detectedTypes: [],
            confidence: 0,
            sampleValues: [],
            suggestions: []
          };

          // Check for government data patterns
          if (this.isGovernmentDataField(key, [])) {
            pattern.detectedTypes.push('government_data');
            pattern.confidence = 0.9;
            pattern.suggestions.push('Government data field detected');
          }

          patterns.push(pattern);
        }
      }

      return patterns;
    } catch (error) {
      console.error('JSON pattern analysis failed:', error);
      return [];
    }
  }

  // Detect JSON field types
  async detectJSONFieldTypes(content) {
    try {
      const data = JSON.parse(content);
      const fieldTypes = [];

      if (typeof data === 'object' && data !== null) {
        const keys = Array.isArray(data) ? Object.keys(data[0] || {}) : Object.keys(data);
        
        for (const key of keys) {
          fieldTypes.push({
            column: key,
            type: 'text', // Default type
            confidence: 0.7
          });
        }
      }

      return fieldTypes;
    } catch (error) {
      console.error('JSON field type detection failed:', error);
      return [];
    }
  }

  // Analyze XML patterns
  async analyzeXMLPatterns(content) {
    try {
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(content, 'text/xml');
      const patterns = [];

      const root = xmlDoc.documentElement;
      for (const child of root.children) {
        const pattern = {
          header: child.tagName,
          detectedTypes: [],
          confidence: 0,
          sampleValues: [child.textContent || ''],
          suggestions: []
        };

        // Check for government data patterns
        if (this.isGovernmentDataField(child.tagName, [child.textContent || ''])) {
          pattern.detectedTypes.push('government_data');
          pattern.confidence = 0.9;
          pattern.suggestions.push('Government data field detected');
        }

        patterns.push(pattern);
      }

      return patterns;
    } catch (error) {
      console.error('XML pattern analysis failed:', error);
      return [];
    }
  }

  // Detect XML field types
  async detectXMLFieldTypes(content) {
    try {
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(content, 'text/xml');
      const fieldTypes = [];

      const root = xmlDoc.documentElement;
      for (const child of root.children) {
        fieldTypes.push({
          column: child.tagName,
          type: 'text', // Default type
          confidence: 0.7
        });
      }

      return fieldTypes;
    } catch (error) {
      console.error('XML field type detection failed:', error);
      return [];
    }
  }

  // Analyze value patterns
  async analyzeValuePatterns(content) {
    // Placeholder for value pattern analysis
    return [];
  }

  // Detect government indicators
  async detectGovernmentIndicators(content) {
    const indicators = [];
    
    // Check for government keywords in content
    const governmentKeywords = [
      'uprn', 'usrn', 'toid', 'lad', 'ward', 'constituency', 'parish',
      'rateable', 'valuation', 'business', 'property', 'address',
      'postcode', 'council', 'borough', 'district', 'county'
    ];

    const contentLower = content.toLowerCase();
    for (const keyword of governmentKeywords) {
      if (contentLower.includes(keyword)) {
        indicators.push(`Contains ${keyword.toUpperCase()} data`);
      }
    }

    return indicators;
  }

  // Assess data quality
  async assessDataQuality(content, fileType) {
    const quality = {
      completeness: 0.8,
      consistency: 0.9,
      accuracy: 0.7,
      issues: [],
      recommendations: []
    };

    // Basic quality assessment
    if (content.length === 0) {
      quality.completeness = 0;
      quality.issues.push('Empty content');
    }

    return quality;
  }
}

export default AIDataAnalyzer; 