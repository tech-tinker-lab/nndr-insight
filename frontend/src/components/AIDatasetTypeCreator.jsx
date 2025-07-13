import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Alert,
  CircularProgress,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Snackbar,
  LinearProgress,
  Tabs,
  Tab
} from '@mui/material';
import {
  Upload as UploadIcon,
  Analytics as AnalyzeIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Refresh as RefreshIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  DataObject as DataIcon,
  Schema as SchemaIcon,
  Security as SecurityIcon,
  CloudUpload as CloudUploadIcon,
  Settings as SettingsIcon,
  Visibility as ViewIcon,
  VisibilityOff as ViewOffIcon,
  Download as DownloadIcon,
  UploadFile as UploadFileIcon,
  FileUpload as FileUploadIcon,
  Storage as StorageIcon,
  TableChart as TableIcon,
  ViewColumn as FieldIcon,
  Build as BuildIcon,
  Assessment as AssessmentIcon,
  AutoFixHigh as AutoFixIcon,
  Psychology as PsychologyIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Cloud as CloudIcon,
  Computer as ComputerIcon,
  Add as AddIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import api from '../api/axios';
import { toast } from 'react-hot-toast';

// Utility function for formatting file sizes
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const AIDatasetTypeCreator = ({ onDatasetTypeCreated, onCancel }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [fileInfo, setFileInfo] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [fieldMappings, setFieldMappings] = useState([]);
  const [datasetType, setDatasetType] = useState({
    name: '',
    description: '',
    category: '',
    governing_body: '',
    version: '1.0',
    data_standards: [],
    tags: [],
    retention_policy: '5_years',
    data_classification: 'general',
    security_level: 'public'
  });

  // Analysis options
  const [analysisOptions, setAnalysisOptions] = useState({
    useClientSide: true,
    sampleSize: 1000,
    maxFileSize: 1024 * 1024 * 1024 * 10, // 10GB
    enableAI: true,
    enableValidation: true,
    enableStandards: true
  });

  // Progress tracking
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');

  // Error handling
  const [errors, setErrors] = useState([]);
  const [warnings, setWarnings] = useState([]);

  // UI states
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);

  const steps = [
    'Upload File',
    'AI Analysis',
    'Field Configuration',
    'Validation & Standards',
    'Review & Create'
  ];

  // File handling with large file support
  const handleFileSelect = useCallback((event) => {
    const selectedFile = event.target.files[0];
    if (!selectedFile) return;

    const fileSize = selectedFile.size;
    const maxSize = analysisOptions.maxFileSize;

    if (fileSize > maxSize) {
      toast.error(`File size (${formatFileSize(fileSize)}) exceeds maximum allowed size (${formatFileSize(maxSize)})`);
      return;
    }

    setFile(selectedFile);
    setFileInfo({
      name: selectedFile.name,
      size: fileSize,
      type: selectedFile.type,
      lastModified: new Date(selectedFile.lastModified)
    });

    // Auto-populate dataset type name from filename
    const baseName = selectedFile.name.replace(/\.[^/.]+$/, '');
    setDatasetType(prev => ({
      ...prev,
      name: baseName,
      description: `Dataset type for ${baseName} files`
    }));

    setErrors([]);
    setWarnings([]);
  }, [analysisOptions.maxFileSize]);

  // Enhanced AI Analysis with large file support
  const performAnalysis = async () => {
    if (!file) {
      toast.error('Please select a file first');
      return;
    }

    setLoading(true);
    setProgress(0);
    setProgressMessage('Starting analysis...');

    try {
      let analysisResult;

      if (analysisOptions.useClientSide) {
        analysisResult = await performClientSideAnalysis();
      } else {
        analysisResult = await performServerSideAnalysis();
      }

      setAnalysis(analysisResult);
      setFieldMappings(analysisResult.field_mappings || []);
      
      // Auto-populate dataset type from analysis
      if (analysisResult.identified_standards?.length > 0) {
        const primaryStandard = analysisResult.identified_standards[0];
        setDatasetType(prev => ({
          ...prev,
          governing_body: primaryStandard.governing_body,
          data_standards: analysisResult.identified_standards.map(s => s.standard_id),
          tags: [primaryStandard.category, primaryStandard.country]
        }));
      }

      setActiveStep(2);
      toast.success('Analysis completed successfully!');
    } catch (error) {
      console.error('Analysis failed:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Analysis failed';
      setErrors([errorMessage]);
      toast.error(`Analysis failed: ${errorMessage}`);
    } finally {
      setLoading(false);
      setProgress(0);
    }
  };

  const performClientSideAnalysis = async () => {
    setProgressMessage('Reading file...');
    setProgress(10);

    const content = await readFileContent(file);
    setProgress(30);
    setProgressMessage('Analyzing file structure...');

    // Determine file type and analyze
    const fileExtension = file.name.split('.').pop().toLowerCase();
    let analysisResult;

    switch (fileExtension) {
      case 'csv':
        analysisResult = await analyzeCSVContent(content);
        break;
      case 'json':
        analysisResult = await analyzeJSONContent(content);
        break;
      case 'xml':
        analysisResult = await analyzeXMLContent(content);
        break;
      default:
        throw new Error(`Unsupported file type: ${fileExtension}`);
    }

    setProgress(70);
    setProgressMessage('Applying AI intelligence...');

    // Apply AI enhancements
    if (analysisOptions.enableAI) {
      analysisResult = await enhanceWithAI(analysisResult);
    }

    setProgress(90);
    setProgressMessage('Finalizing analysis...');

    // Add metadata
    analysisResult.file_info = fileInfo;
    analysisResult.analysis_timestamp = new Date().toISOString();
    analysisResult.analysis_method = 'client_side';

    setProgress(100);
    return analysisResult;
  };

  const performServerSideAnalysis = async () => {
    setProgressMessage('Uploading file to server...');
    setProgress(20);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('options', JSON.stringify(analysisOptions));

    const response = await api.post('/api/design-enhanced/ai/analyze-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setProgress(percentCompleted);
        setProgressMessage(`Uploading: ${percentCompleted}%`);
      },
      timeout: 300000 // 5 minutes timeout for large files
    });

    return response.data;
  };

  const readFileContent = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = reject;
      reader.readAsText(file);
    });
  };

  const analyzeCSVContent = async (content) => {
    const lines = content.split('\n').filter(line => line.trim());
    if (lines.length === 0) {
      throw new Error('Empty CSV file');
    }

    // Use first line as headers and sanitize field names
    const rawHeaders = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    const sanitizedHeaders = rawHeaders.map((header, index) => {
      // Sanitize field name for database use
      let sanitized = header
        .replace(/[^a-zA-Z0-9_]/g, '_') // Replace invalid chars with underscore
        .replace(/^[0-9]/, 'field_$&') // Prefix with 'field_' if starts with number
        .replace(/^_/, 'field_') // Prefix with 'field_' if starts with underscore
        .toLowerCase(); // Convert to lowercase
      
      // Ensure unique names
      if (sanitized === '' || sanitized === '_') {
        sanitized = `field_${index + 1}`;
      }
      
      return sanitized;
    });
    
    // Ensure unique field names
    const headers = ensureUniqueFieldNames(sanitizedHeaders);
    
    const dataLines = lines.slice(1, Math.min(lines.length, analysisOptions.sampleSize + 1));
    
    const sampleData = dataLines
      .filter(line => line.trim())
      .map(line => line.split(',').map(field => field.trim().replace(/"/g, '')));

    const fieldAnalysis = headers.map((header, index) => {
      const columnData = sampleData.map(row => row[index]).filter(val => val && val !== '');
      return analyzeField(header, columnData, index);
    });

    return {
      format: 'csv',
      total_rows: lines.length - 1, // Exclude header
      total_fields: headers.length,
      field_analysis: fieldAnalysis,
      field_mappings: fieldAnalysis,
      identified_standards: [],
      data_quality_score: 0.8,
      confidence_score: 0.9
    };
  };

  const ensureUniqueFieldNames = (fieldNames) => {
    const uniqueNames = [];
    const seen = new Set();
    
    fieldNames.forEach((name, index) => {
      let uniqueName = name;
      let counter = 1;
      
      while (seen.has(uniqueName)) {
        uniqueName = `${name}_${counter}`;
        counter++;
      }
      
      seen.add(uniqueName);
      uniqueNames.push(uniqueName);
    });
    
    return uniqueNames;
  };

  const analyzeJSONContent = async (content) => {
    const data = JSON.parse(content);
    const isArray = Array.isArray(data);
    const sampleData = isArray ? data.slice(0, Math.min(analysisOptions.sampleSize, data.length)) : [data];

    const fieldAnalysis = [];
    if (isArray && sampleData.length > 0) {
      const firstItem = sampleData[0];
      Object.keys(firstItem).forEach((key, index) => {
        const columnData = sampleData.map(item => item[key]).filter(val => val !== null && val !== undefined);
        fieldAnalysis.push(analyzeField(key, columnData, index));
      });
    }

    return {
      format: 'json',
      is_array: isArray,
      field_analysis: fieldAnalysis,
      sample_data: sampleData,
      total_items: isArray ? data.length : 1
    };
  };

  const analyzeXMLContent = async (content) => {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(content, 'text/xml');
    const rootElement = xmlDoc.documentElement;

    // Analyze XML structure
    const fieldAnalysis = [];
    const children = Array.from(rootElement.children);
    
    if (children.length > 0) {
      const firstChild = children[0];
      Array.from(firstChild.children).forEach((child, index) => {
        const columnData = children.map(item => {
          const childElement = item.querySelector(child.tagName);
          return childElement ? childElement.textContent : '';
        }).filter(val => val && val.trim() !== '');

        fieldAnalysis.push(analyzeField(child.tagName, columnData, index));
      });
    }

    return {
      format: 'xml',
      root_element: rootElement.tagName,
      field_analysis: fieldAnalysis,
      total_elements: children.length
    };
  };

  const analyzeField = (fieldName, values, index) => {
    const sampleValues = values.slice(0, 10);
    const allValues = values;
    
    // AI-powered comprehensive field analysis
    const aiAnalysis = performAIFieldAnalysis(fieldName, allValues, sampleValues, index);
    
    return {
      field_name: fieldName,
      display_name: aiAnalysis.displayName,
      data_type: aiAnalysis.dataType,
      postgis_type: aiAnalysis.postgisType,
      is_required: aiAnalysis.isRequired,
      is_primary_key: aiAnalysis.isPrimaryKey,
      is_unique: aiAnalysis.isUnique,
      is_nullable: aiAnalysis.isNullable,
      default_value: aiAnalysis.defaultValue,
      constraints: aiAnalysis.constraints.join(', '),
      description: aiAnalysis.description,
      format: aiAnalysis.format,
      validation_rules: aiAnalysis.validationRules,
      transformation_rules: aiAnalysis.transformationRules,
      confidence_score: aiAnalysis.confidenceScore,
      ai_reasoning: aiAnalysis.reasoning,
      sample_values: sampleValues,
      null_count: allValues.filter(v => !v || v.trim() === '').length,
      unique_count: new Set(allValues).size,
      data_patterns: aiAnalysis.patterns,
      suggested_indexes: aiAnalysis.suggestedIndexes,
      data_quality_score: aiAnalysis.dataQualityScore,
      uniqueness_score: aiAnalysis.uniquenessScore,
      nullability_score: aiAnalysis.nullabilityScore,
      complexity_score: aiAnalysis.complexityScore,
      business_rules: aiAnalysis.businessRules,
      data_lineage: aiAnalysis.dataLineage
    };
  };

  const performAIFieldAnalysis = (fieldName, allValues, sampleValues, index) => {
    const name = fieldName.toLowerCase();
    const analysis = {
      displayName: generateSmartDisplayName(fieldName),
      dataType: 'text',
      postgisType: null,
      isRequired: false,
      isPrimaryKey: false,
      isUnique: false,
      isNullable: true,
      defaultValue: '',
      constraints: [],
      description: '',
      format: null,
      validationRules: [],
      transformationRules: [],
      confidenceScore: 0.0,
      reasoning: [],
      patterns: [],
      suggestedIndexes: [],
      dataQualityScore: 0.0,
      uniquenessScore: 0.0,
      nullabilityScore: 0.0,
      complexityScore: 0.0,
      businessRules: [],
      dataLineage: []
    };

    // Enhanced AI Pattern Recognition
    const patterns = detectAIPatterns(fieldName, allValues, sampleValues);
    analysis.patterns = patterns;

    // Advanced Data Type Detection with Confidence Scoring
    const typeAnalysis = detectAIDataType(fieldName, allValues, sampleValues, patterns);
    analysis.dataType = typeAnalysis.type;
    analysis.postgisType = typeAnalysis.postgisType;
    analysis.confidenceScore = typeAnalysis.confidence;
    analysis.reasoning.push(...typeAnalysis.reasoning);

    // Intelligent Uniqueness Analysis
    const uniquenessAnalysis = detectAIUniqueness(fieldName, allValues, patterns);
    analysis.isUnique = uniquenessAnalysis.isUnique;
    analysis.uniquenessScore = uniquenessAnalysis.score;
    analysis.reasoning.push(...uniquenessAnalysis.reasoning);

    // Advanced Nullability Assessment
    const nullabilityAnalysis = detectAINullability(fieldName, allValues, patterns);
    analysis.isNullable = nullabilityAnalysis.isNullable;
    analysis.nullabilityScore = nullabilityAnalysis.score;
    analysis.reasoning.push(...nullabilityAnalysis.reasoning);

    // Smart Field Requirements with Business Logic
    const requirementAnalysis = detectAIRequirements(fieldName, allValues, patterns);
    analysis.isRequired = requirementAnalysis.isRequired;
    analysis.isPrimaryKey = requirementAnalysis.isPrimaryKey;
    analysis.reasoning.push(...requirementAnalysis.reasoning);

    // AI-Generated Constraints with Advanced Validation
    const constraintAnalysis = generateAIConstraints(fieldName, allValues, typeAnalysis, patterns);
    analysis.constraints = constraintAnalysis.constraints;
    analysis.validationRules = constraintAnalysis.validationRules;
    analysis.transformationRules = constraintAnalysis.transformationRules;
    analysis.businessRules = constraintAnalysis.businessRules;
    analysis.reasoning.push(...constraintAnalysis.reasoning);

    // Intelligent Default Values with Context
    analysis.defaultValue = generateAIDefaultValue(fieldName, allValues, typeAnalysis);

    // Advanced Format Detection
    analysis.format = detectAIFormat(fieldName, allValues, typeAnalysis);

    // AI-Generated Description with Business Context
    analysis.description = generateAIDescription(fieldName, typeAnalysis, patterns, constraintAnalysis);

    // Performance Optimization with AI Recommendations
    analysis.suggestedIndexes = generateAIIndexes(fieldName, typeAnalysis, patterns);

    // Comprehensive Data Quality Assessment
    analysis.dataQualityScore = assessDataQuality(allValues, typeAnalysis, patterns);

    // Data Complexity Analysis
    analysis.complexityScore = assessDataComplexity(allValues, typeAnalysis, patterns);

    // Data Lineage
    analysis.dataLineage = generateDataLineage(fieldName, patterns);

    return analysis;
  };

  const detectAIPatterns = (fieldName, allValues, sampleValues) => {
    const patterns = [];
    const name = fieldName.toLowerCase();
    const nonEmptyValues = allValues.filter(v => v && v.trim() !== '');

    // Pattern recognition based on field name
    if (name.includes('uprn')) {
      patterns.push('UPRN_PATTERN', 'UNIQUE_IDENTIFIER', 'PROPERTY_REFERENCE');
    }
    if (name.includes('usrn')) {
      patterns.push('USRN_PATTERN', 'UNIQUE_IDENTIFIER', 'STREET_REFERENCE');
    }
    if (name.includes('postcode') || name.includes('pcd')) {
      patterns.push('UK_POSTCODE', 'GEOGRAPHIC_CODE', 'ADDRESS_COMPONENT');
    }
    if (name.includes('email')) {
      patterns.push('EMAIL_ADDRESS', 'CONTACT_INFO', 'COMMUNICATION');
    }
    if (name.includes('phone') || name.includes('tel')) {
      patterns.push('PHONE_NUMBER', 'CONTACT_INFO', 'COMMUNICATION');
    }
    if (name.includes('date') || name.includes('time')) {
      patterns.push('TEMPORAL_DATA', 'TIMESTAMP');
    }
    if (name.includes('amount') || name.includes('value') || name.includes('price') || name.includes('rate')) {
      patterns.push('MONETARY_VALUE', 'FINANCIAL_DATA', 'CURRENCY');
    }
    if (name.includes('lat') || name.includes('long') || name.includes('x') || name.includes('y')) {
      patterns.push('COORDINATE', 'SPATIAL_DATA', 'GEOMETRY');
    }
    if (name.includes('active') || name.includes('enabled') || name.includes('flag')) {
      patterns.push('BOOLEAN_FLAG', 'STATUS_INDICATOR');
    }

    // Pattern recognition based on data content
    if (nonEmptyValues.length > 0) {
      const firstValue = nonEmptyValues[0];
      
      // Check for specific data patterns
      if (/^\d{12}$/.test(firstValue)) {
        patterns.push('12_DIGIT_NUMBER', 'LIKELY_UPRN');
      }
      if (/^\d{8}$/.test(firstValue)) {
        patterns.push('8_DIGIT_NUMBER', 'LIKELY_USRN');
      }
      if (/^[A-Z]{1,2}[0-9][0-9A-Z]?\s?[0-9][A-Z]{2}$/i.test(firstValue)) {
        patterns.push('UK_POSTCODE_FORMAT');
      }
      if (/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(firstValue)) {
        patterns.push('EMAIL_FORMAT');
      }
      if (/^\+?[\d\s\-\(\)]+$/.test(firstValue)) {
        patterns.push('PHONE_FORMAT');
      }
      if (/^\d{4}-\d{2}-\d{2}/.test(firstValue) || /^\d{2}\/\d{2}\/\d{4}/.test(firstValue)) {
        patterns.push('DATE_FORMAT');
      }
      if (/^-?\d+\.\d+$/.test(firstValue) && parseFloat(firstValue) >= -180 && parseFloat(firstValue) <= 180) {
        patterns.push('COORDINATE_FORMAT');
      }
    }

    // Statistical patterns
    const uniqueRatio = new Set(nonEmptyValues).size / nonEmptyValues.length;
    if (uniqueRatio > 0.95) {
      patterns.push('HIGH_UNIQUENESS', 'LIKELY_IDENTIFIER');
    }
    if (uniqueRatio < 0.1) {
      patterns.push('LOW_UNIQUENESS', 'LIKELY_CATEGORY');
    }

    return patterns;
  };

  const detectAIDataType = (fieldName, allValues, sampleValues, patterns) => {
    const analysis = {
      type: 'text',
      postgisType: null,
      confidence: 0.0,
      reasoning: []
    };

    const nonEmptyValues = allValues.filter(v => v && v.trim() !== '');
    if (nonEmptyValues.length === 0) {
      analysis.reasoning.push('No data available for type detection');
      return analysis;
    }

    const firstValue = nonEmptyValues[0];
    let confidence = 0.0;

    // Pattern-based type detection
    if (patterns.includes('UPRN_PATTERN') || patterns.includes('12_DIGIT_NUMBER')) {
      analysis.type = 'bigint';
      analysis.confidence = 0.95;
      analysis.reasoning.push('Detected UPRN pattern - 12-digit unique identifier');
    }
    else if (patterns.includes('USRN_PATTERN') || patterns.includes('8_DIGIT_NUMBER')) {
      analysis.type = 'bigint';
      analysis.confidence = 0.95;
      analysis.reasoning.push('Detected USRN pattern - 8-digit unique identifier');
    }
    else if (patterns.includes('UK_POSTCODE_FORMAT')) {
      analysis.type = 'varchar';
      analysis.confidence = 0.90;
      analysis.reasoning.push('Detected UK postcode format');
    }
    else if (patterns.includes('EMAIL_FORMAT')) {
      analysis.type = 'varchar';
      analysis.confidence = 0.90;
      analysis.reasoning.push('Detected email address format');
    }
    else if (patterns.includes('PHONE_FORMAT')) {
      analysis.type = 'varchar';
      analysis.confidence = 0.85;
      analysis.reasoning.push('Detected phone number format');
    }
    else if (patterns.includes('DATE_FORMAT')) {
      analysis.type = 'date';
      analysis.confidence = 0.90;
      analysis.reasoning.push('Detected date format');
    }
    else if (patterns.includes('COORDINATE_FORMAT')) {
      analysis.type = 'geometry';
      analysis.postgisType = 'POINT';
      analysis.confidence = 0.85;
      analysis.reasoning.push('Detected coordinate format');
    }
    else if (patterns.includes('MONETARY_VALUE')) {
      analysis.type = 'numeric';
      analysis.confidence = 0.80;
      analysis.reasoning.push('Detected monetary value pattern');
    }
    else if (patterns.includes('BOOLEAN_FLAG')) {
      analysis.type = 'boolean';
      analysis.confidence = 0.85;
      analysis.reasoning.push('Detected boolean flag pattern');
    }
    else {
      // Content-based type detection
      if (!isNaN(firstValue) && firstValue !== '') {
        if (firstValue.includes('.')) {
          analysis.type = 'numeric';
          analysis.confidence = 0.75;
          analysis.reasoning.push('Detected decimal number from content');
        } else {
          analysis.type = 'integer';
          analysis.confidence = 0.75;
          analysis.reasoning.push('Detected integer from content');
        }
      } else if (['true', 'false', 'yes', 'no', '1', '0'].includes(firstValue.toLowerCase())) {
        analysis.type = 'boolean';
        analysis.confidence = 0.80;
        analysis.reasoning.push('Detected boolean value from content');
      } else {
        // Text analysis
        const maxLength = Math.max(...nonEmptyValues.map(v => v.length));
        if (maxLength <= 50) {
          analysis.type = 'varchar';
          analysis.confidence = 0.70;
          analysis.reasoning.push('Short text detected');
        } else if (maxLength <= 255) {
          analysis.type = 'varchar';
          analysis.confidence = 0.65;
          analysis.reasoning.push('Medium text detected');
        } else {
          analysis.type = 'text';
          analysis.confidence = 0.60;
          analysis.reasoning.push('Long text detected');
        }
      }
    }

    analysis.confidence = Math.min(analysis.confidence, 0.95);
    return analysis;
  };

  const detectAIUniqueness = (fieldName, allValues, patterns) => {
    const analysis = {
      isUnique: false,
      score: 0.0,
      reasoning: []
    };

    const nonEmptyValues = allValues.filter(v => v && v.trim() !== '');
    const uniqueValues = new Set(nonEmptyValues);
    const uniquenessRatio = uniqueValues.size / nonEmptyValues.length;

    // Pattern-based uniqueness detection
    if (patterns.includes('UNIQUE_IDENTIFIER') || patterns.includes('UPRN_PATTERN') || patterns.includes('USRN_PATTERN')) {
      analysis.isUnique = true;
      analysis.score = 0.95;
      analysis.reasoning.push('Standard identifier pattern detected - should be unique');
    }

    // Statistical uniqueness analysis
    if (uniquenessRatio > 0.99) {
      analysis.isUnique = true;
      analysis.score = 0.90;
      analysis.reasoning.push(`Very high uniqueness ratio (${(uniquenessRatio * 100).toFixed(1)}%) suggests unique field`);
    } else if (uniquenessRatio > 0.95) {
      analysis.isUnique = true;
      analysis.score = 0.80;
      analysis.reasoning.push(`High uniqueness ratio (${(uniquenessRatio * 100).toFixed(1)}%) suggests unique field`);
    } else if (uniquenessRatio < 0.1) {
      analysis.isUnique = false;
      analysis.score = 0.10;
      analysis.reasoning.push(`Low uniqueness ratio (${(uniquenessRatio * 100).toFixed(1)}%) suggests categorical field`);
    }

    // Field name-based uniqueness detection
    const name = fieldName.toLowerCase();
    if (name.includes('id') || name.includes('key') || name.includes('code') || name.includes('reference')) {
      if (analysis.score < 0.7) {
        analysis.isUnique = true;
        analysis.score = Math.max(analysis.score, 0.7);
        analysis.reasoning.push('Field name suggests identifier - marking as unique');
      }
    }

    return analysis;
  };

  const detectAINullability = (fieldName, allValues, patterns) => {
    const analysis = {
      isNullable: true,
      score: 0.0,
      reasoning: []
    };

    const nullCount = allValues.filter(v => !v || v.trim() === '').length;
    const nullRatio = nullCount / allValues.length;

    // Pattern-based nullability detection
    if (patterns.includes('UNIQUE_IDENTIFIER') || patterns.includes('UPRN_PATTERN') || patterns.includes('USRN_PATTERN')) {
      analysis.isNullable = false;
      analysis.score = 0.95;
      analysis.reasoning.push('Standard identifier - should not be nullable');
    }

    // Statistical nullability analysis
    if (nullRatio < 0.01) {
      analysis.isNullable = false;
      analysis.score = 0.90;
      analysis.reasoning.push(`Very low null ratio (${(nullRatio * 100).toFixed(1)}%) suggests required field`);
    } else if (nullRatio < 0.05) {
      analysis.isNullable = false;
      analysis.score = 0.80;
      analysis.reasoning.push(`Low null ratio (${(nullRatio * 100).toFixed(1)}%) suggests required field`);
    } else if (nullRatio > 0.5) {
      analysis.isNullable = true;
      analysis.score = 0.90;
      analysis.reasoning.push(`High null ratio (${(nullRatio * 100).toFixed(1)}%) suggests optional field`);
    }

    // Field name-based nullability detection
    const name = fieldName.toLowerCase();
    if (name.includes('id') || name.includes('key') || name.includes('code') || name.includes('reference')) {
      if (analysis.score < 0.7) {
        analysis.isNullable = false;
        analysis.score = Math.max(analysis.score, 0.7);
        analysis.reasoning.push('Field name suggests identifier - marking as not nullable');
      }
    }

    return analysis;
  };

  const detectAIRequirements = (fieldName, allValues, patterns) => {
    const analysis = {
      isRequired: false,
      isPrimaryKey: false,
      reasoning: []
    };

    const name = fieldName.toLowerCase();
    const nonEmptyValues = allValues.filter(v => v && v.trim() !== '');
    const nullCount = allValues.length - nonEmptyValues.length;
    const nullRatio = nullCount / allValues.length;

    // Pattern-based requirement detection
    if (patterns.includes('UNIQUE_IDENTIFIER') || patterns.includes('HIGH_UNIQUENESS')) {
      analysis.isRequired = true;
      analysis.reasoning.push('High uniqueness suggests required identifier');
    }

    if (patterns.includes('UPRN_PATTERN') || patterns.includes('USRN_PATTERN')) {
      analysis.isRequired = true;
      analysis.isPrimaryKey = true;
      analysis.reasoning.push('Standard identifier - marked as primary key');
    }

    if (name.includes('id') || name.includes('key') || name.includes('code')) {
      analysis.isRequired = true;
      analysis.reasoning.push('Field name suggests identifier');
    }

    // Data-based requirement detection
    if (nullRatio < 0.05) {
      analysis.isRequired = true;
      analysis.reasoning.push('Very low null ratio suggests required field');
    } else if (nullRatio > 0.5) {
      analysis.isRequired = false;
      analysis.reasoning.push('High null ratio suggests optional field');
    }

    return analysis;
  };

  const generateAIConstraints = (fieldName, allValues, typeAnalysis, patterns) => {
    const analysis = {
      constraints: [],
      validationRules: [],
      transformationRules: [],
      reasoning: [],
      businessRules: []
    };

    const nonEmptyValues = allValues.filter(v => v && v.trim() !== '');
    const maxLength = Math.max(...nonEmptyValues.map(v => v ? v.length : 0));

    // Type-specific constraints
    if (typeAnalysis.type === 'varchar') {
      if (maxLength <= 50) {
        analysis.constraints.push(`VARCHAR(${Math.max(maxLength, 50)})`);
      } else if (maxLength <= 255) {
        analysis.constraints.push(`VARCHAR(${Math.max(maxLength, 255)})`);
      } else {
        analysis.constraints.push('TEXT');
      }
    }

    if (typeAnalysis.type === 'numeric') {
      analysis.constraints.push('NUMERIC(12,2)');
      analysis.validationRules.push('CHECK (value >= 0)');
    }

    if (typeAnalysis.type === 'geometry') {
      analysis.constraints.push('GEOMETRY');
      analysis.validationRules.push('ST_IsValid(geometry)');
    }

    // Pattern-specific constraints
    if (patterns.includes('UPRN_PATTERN')) {
      analysis.constraints.push('UNIQUE', 'NOT NULL');
      analysis.validationRules.push('CHECK (LENGTH(CAST(value AS TEXT)) = 12)');
      analysis.transformationRules.push('CAST(value AS BIGINT)');
      analysis.businessRules.push('This field is a unique identifier and should not be null.');
    }

    if (patterns.includes('UK_POSTCODE_FORMAT')) {
      analysis.validationRules.push('CHECK (value ~ \'^[A-Z]{1,2}[0-9][0-9A-Z]?\\s?[0-9][A-Z]{2}$\')');
      analysis.transformationRules.push('UPPER(TRIM(value))');
      analysis.businessRules.push('This field is a geographic identifier and should not be null.');
    }

    if (patterns.includes('EMAIL_FORMAT')) {
      analysis.validationRules.push('CHECK (value ~ \'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}$\')');
      analysis.businessRules.push('This field is a contact identifier and should not be null.');
    }

    if (patterns.includes('MONETARY_VALUE')) {
      analysis.constraints.push('CHECK (value >= 0)');
      analysis.transformationRules.push('ROUND(value, 2)');
      analysis.businessRules.push('This field represents a monetary value and should not be negative.');
    }

    return analysis;
  };

  const generateAIDefaultValue = (fieldName, allValues, typeAnalysis) => {
    const name = fieldName.toLowerCase();
    
    if (typeAnalysis.type === 'boolean') {
      return 'false';
    }
    if (typeAnalysis.type === 'date') {
      return 'CURRENT_DATE';
    }
    if (typeAnalysis.type === 'timestamp') {
      return 'CURRENT_TIMESTAMP';
    }
    if (name.includes('active') || name.includes('enabled')) {
      return 'true';
    }
    
    return '';
  };

  const detectAIFormat = (fieldName, allValues, typeAnalysis) => {
    const name = fieldName.toLowerCase();
    
    if (typeAnalysis.type === 'date') {
      return 'YYYY-MM-DD';
    }
    if (typeAnalysis.type === 'timestamp') {
      return 'YYYY-MM-DD HH:MM:SS';
    }
    if (name.includes('postcode')) {
      return 'UK_POSTCODE';
    }
    if (name.includes('email')) {
      return 'EMAIL';
    }
    if (name.includes('phone')) {
      return 'PHONE';
    }
    
    return null;
  };

  const generateAIDescription = (fieldName, typeAnalysis, patterns, constraintAnalysis) => {
    const name = fieldName.toLowerCase();
    let description = `${typeAnalysis.type.toUpperCase()} field`;

    // Pattern-based descriptions
    if (patterns.includes('UPRN_PATTERN')) {
      description = 'Unique Property Reference Number (UPRN) - 12-digit unique identifier for properties';
    } else if (patterns.includes('USRN_PATTERN')) {
      description = 'Unique Street Reference Number (USRN) - 8-digit unique identifier for streets';
    } else if (patterns.includes('UK_POSTCODE_FORMAT')) {
      description = 'UK Postcode - Geographic location identifier';
    } else if (patterns.includes('EMAIL_FORMAT')) {
      description = 'Email Address - Contact information';
    } else if (patterns.includes('MONETARY_VALUE')) {
      description = 'Monetary Value - Financial amount in pounds sterling';
    } else if (patterns.includes('COORDINATE_FORMAT')) {
      description = 'Spatial Coordinate - Geographic location data';
    } else {
      // Generic descriptions based on field name
      if (name.includes('id')) description += ' - Unique identifier';
      if (name.includes('name')) description += ' - Name or title';
      if (name.includes('date')) description += ' - Date value';
      if (name.includes('amount') || name.includes('value')) description += ' - Numeric value';
      if (name.includes('active') || name.includes('enabled')) description += ' - Status indicator';
    }

    // Add constraint information
    if (constraintAnalysis.constraints.length > 0) {
      description += ` (${constraintAnalysis.constraints.join(', ')})`;
    }

    return description;
  };

  const generateAIIndexes = (fieldName, typeAnalysis, patterns) => {
    const indexes = [];
    const name = fieldName.toLowerCase();

    // Primary key indexes
    if (patterns.includes('UNIQUE_IDENTIFIER') || patterns.includes('UPRN_PATTERN') || patterns.includes('USRN_PATTERN')) {
      indexes.push('PRIMARY KEY');
    }

    // Foreign key indexes
    if (name.includes('id') && !name.includes('uprn') && !name.includes('usrn')) {
      indexes.push('FOREIGN KEY INDEX');
    }

    // Spatial indexes
    if (typeAnalysis.type === 'geometry') {
      indexes.push('SPATIAL INDEX');
    }

    // Performance indexes
    if (patterns.includes('HIGH_UNIQUENESS')) {
      indexes.push('UNIQUE INDEX');
    }

    return indexes;
  };

  const assessDataQuality = (allValues, typeAnalysis, patterns) => {
    const nonEmptyValues = allValues.filter(v => v && v.trim() !== '');
    const nullRatio = (allValues.length - nonEmptyValues.length) / allValues.length;
    const uniqueRatio = new Set(nonEmptyValues).size / nonEmptyValues.length;
    
    let qualityScore = 1.0;
    
    // Penalize high null ratios
    if (nullRatio > 0.5) qualityScore -= 0.3;
    else if (nullRatio > 0.2) qualityScore -= 0.1;
    
    // Reward high uniqueness for identifiers
    if (patterns.includes('UNIQUE_IDENTIFIER') && uniqueRatio < 0.9) {
      qualityScore -= 0.2;
    }
    
    // Reward pattern consistency
    if (patterns.length > 0) qualityScore += 0.1;
    
    return Math.max(0.0, Math.min(1.0, qualityScore));
  };

  const assessDataComplexity = (allValues, typeAnalysis, patterns) => {
    const nonEmptyValues = allValues.filter(v => v && v.trim() !== '');
    let complexity = 0.0;

    // Length complexity
    const avgLength = nonEmptyValues.reduce((sum, v) => sum + v.length, 0) / nonEmptyValues.length;
    if (avgLength > 100) complexity += 0.3;
    else if (avgLength > 50) complexity += 0.2;
    else if (avgLength > 20) complexity += 0.1;

    // Pattern complexity
    if (patterns.includes('COORDINATE_FORMAT')) complexity += 0.2;
    if (patterns.includes('EMAIL_FORMAT')) complexity += 0.1;
    if (patterns.includes('UK_POSTCODE_FORMAT')) complexity += 0.1;
    if (patterns.includes('MONETARY_VALUE')) complexity += 0.1;

    // Type complexity
    if (typeAnalysis.type === 'geometry') complexity += 0.3;
    if (typeAnalysis.type === 'numeric') complexity += 0.2;
    if (typeAnalysis.type === 'date' || typeAnalysis.type === 'timestamp') complexity += 0.1;

    return Math.min(1.0, complexity);
  };

  const generateDataLineage = (fieldName, patterns) => {
    const lineage = [];
    const name = fieldName.toLowerCase();

    if (patterns.includes('UPRN_PATTERN')) {
      lineage.push('OS AddressBase Premium', 'Property Gazetteer', 'Unique Property Reference');
    }
    if (patterns.includes('USRN_PATTERN')) {
      lineage.push('OS AddressBase Premium', 'Street Gazetteer', 'Unique Street Reference');
    }
    if (patterns.includes('UK_POSTCODE_FORMAT')) {
      lineage.push('Royal Mail PAF', 'Postcode Address File', 'Geographic Coding');
    }
    if (patterns.includes('MONETARY_VALUE')) {
      lineage.push('Financial System', 'Rate Calculation', 'Valuation Data');
    }

    return lineage;
  };

  const assessSecurityLevel = (fieldName, patterns) => {
    const name = fieldName.toLowerCase();
    
    if (patterns.includes('UPRN_PATTERN') || patterns.includes('USRN_PATTERN')) {
      return 'public'; // Standard identifiers are public
    }
    if (name.includes('email') || name.includes('phone')) {
      return 'restricted'; // Personal contact information
    }
    if (name.includes('amount') || name.includes('value') || name.includes('rate')) {
      return 'confidential'; // Financial data
    }
    if (name.includes('password') || name.includes('secret')) {
      return 'secret'; // Sensitive data
    }
    
    return 'public';
  };

  const generateRetentionPolicy = (fieldName, patterns) => {
    const name = fieldName.toLowerCase();
    
    if (patterns.includes('UPRN_PATTERN') || patterns.includes('USRN_PATTERN')) {
      return 'permanent'; // Standard identifiers are permanent
    }
    if (name.includes('date') || name.includes('time')) {
      return '7_years'; // Temporal data
    }
    if (name.includes('amount') || name.includes('value')) {
      return '10_years'; // Financial data
    }
    if (name.includes('email') || name.includes('phone')) {
      return '3_years'; // Contact information
    }
    
    return '5_years'; // Default retention
  };

  const classifyData = (fieldName, patterns) => {
    const name = fieldName.toLowerCase();
    
    if (patterns.includes('UPRN_PATTERN') || patterns.includes('USRN_PATTERN')) {
      return 'reference'; // Reference data
    }
    if (name.includes('amount') || name.includes('value') || name.includes('rate')) {
      return 'financial'; // Financial data
    }
    if (name.includes('email') || name.includes('phone')) {
      return 'personal'; // Personal data
    }
    if (name.includes('date') || name.includes('time')) {
      return 'temporal'; // Temporal data
    }
    if (patterns.includes('COORDINATE_FORMAT')) {
      return 'spatial'; // Spatial data
    }
    
    return 'general'; // General data
  };

  const generateSmartDisplayName = (fieldName) => {
    // Convert field name to human-readable format
    return fieldName
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase())
      .replace(/\b(Id|Uprn|Usrn|Pcd|Email|Phone|Date|Time|Amount|Value|Rate|Active|Enabled|Flag)\b/gi, 
        (match) => match.toUpperCase());
  };

  const detectDataType = (values) => {
    if (values.length === 0) return 'text';

    const firstValue = values[0];
    
    // Check for geometry/coordinates
    if (isCoordinate(firstValue)) return 'geometry';
    
    // Check for dates
    if (isDate(firstValue)) return 'date';
    
    // Check for numbers
    if (isNumeric(firstValue)) {
      return firstValue.includes('.') ? 'numeric' : 'integer';
    }
    
    // Check for booleans
    if (isBoolean(firstValue)) return 'boolean';
    
    // Check for postcodes
    if (isPostcode(firstValue)) return 'text';
    
    // Check for UUIDs
    if (isUUID(firstValue)) return 'uuid';
    
    return 'text';
  };

  const isCoordinate = (value) => {
    return /^-?\d+\.\d+$/.test(value) && parseFloat(value) >= -180 && parseFloat(value) <= 180;
  };

  const isDate = (value) => {
    return /^\d{4}-\d{2}-\d{2}/.test(value) || /^\d{2}\/\d{2}\/\d{4}/.test(value);
  };

  const isNumeric = (value) => {
    return !isNaN(value) && value !== '';
  };

  const isBoolean = (value) => {
    return ['true', 'false', 'yes', 'no', '1', '0'].includes(value.toLowerCase());
  };

  const isPostcode = (value) => {
    return /^[A-Z]{1,2}[0-9][0-9A-Z]?\s?[0-9][A-Z]{2}$/i.test(value);
  };

  const isUUID = (value) => {
    return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value);
  };

  const detectConstraints = (fieldName, values) => {
    const constraints = [];
    const name = fieldName.toLowerCase();

    // Length constraints
    const maxLength = Math.max(...values.map(v => v ? v.length : 0));
    if (maxLength > 0) {
      if (maxLength <= 255) {
        constraints.push(`VARCHAR(${maxLength})`);
      } else if (maxLength <= 1000) {
        constraints.push('TEXT');
      }
    }

    // Pattern constraints
    if (name.includes('email')) {
      constraints.push('EMAIL_PATTERN');
    }
    if (name.includes('phone')) {
      constraints.push('PHONE_PATTERN');
    }
    if (name.includes('postcode')) {
      constraints.push('POSTCODE_PATTERN');
    }

    return constraints;
  };

  const detectRequired = (fieldName, values) => {
    const name = fieldName.toLowerCase();
    
    // Common required fields
    if (name.includes('id') || name.includes('key') || name.includes('code')) {
      return true;
    }
    
    // Check if field has null/empty values
    const nullCount = values.filter(v => !v || v.trim() === '').length;
    return nullCount === 0;
  };

  const detectFormat = (fieldName, values) => {
    const name = fieldName.toLowerCase();
    
    if (name.includes('date')) return 'YYYY-MM-DD';
    if (name.includes('time')) return 'HH:MM:SS';
    if (name.includes('postcode')) return 'UK_POSTCODE';
    if (name.includes('email')) return 'EMAIL';
    if (name.includes('phone')) return 'PHONE';
    
    return null;
  };

  const generateFieldDescription = (fieldName, dataType, constraints) => {
    const name = fieldName.toLowerCase();
    let description = `${dataType.toUpperCase()} field`;

    if (name.includes('id')) description += ' - Unique identifier';
    if (name.includes('name')) description += ' - Name or title';
    if (name.includes('date')) description += ' - Date value';
    if (name.includes('amount') || name.includes('value')) description += ' - Numeric value';
    if (name.includes('postcode')) description += ' - UK postcode';
    if (name.includes('email')) description += ' - Email address';
    if (name.includes('phone')) description += ' - Phone number';

    if (constraints.length > 0) {
      description += ` (${constraints.join(', ')})`;
    }

    return description;
  };

  const enhanceWithAI = async (analysisResult) => {
    // Apply AI enhancements to field analysis
    const enhancedFields = analysisResult.field_analysis.map(field => {
      // AI-powered field type refinement
      const enhancedField = { ...field };
      
      // Detect specific field types based on patterns
      if (field.field_name.toLowerCase().includes('uprn')) {
        enhancedField.data_type = 'bigint';
        enhancedField.constraints = 'UNIQUE, NOT NULL';
        enhancedField.description = 'Unique Property Reference Number (UPRN)';
      }
      
      if (field.field_name.toLowerCase().includes('usrn')) {
        enhancedField.data_type = 'bigint';
        enhancedField.constraints = 'NOT NULL';
        enhancedField.description = 'Unique Street Reference Number (USRN)';
      }
      
      if (field.field_name.toLowerCase().includes('rateable_value')) {
        enhancedField.data_type = 'numeric';
        enhancedField.constraints = 'CHECK (rateable_value >= 0)';
        enhancedField.description = 'Rateable value in pounds sterling';
      }

      return enhancedField;
    });

    return {
      ...analysisResult,
      field_analysis: enhancedFields,
      ai_enhanced: true
    };
  };

  // Field mapping management
  const updateFieldMapping = (index, updates) => {
    const updatedMappings = [...fieldMappings];
    updatedMappings[index] = { ...updatedMappings[index], ...updates };
    setFieldMappings(updatedMappings);
    
    // Clear errors when user makes changes
    if (errors.length > 0) {
      setErrors([]);
    }
  };

  const addFieldMapping = () => {
    const newField = {
      field_name: '',
      display_name: '',
      data_type: 'text',
      postgis_type: null,
      is_required: false,
      is_primary_key: false,
      is_unique: false,
      is_nullable: true,
      default_value: '',
      constraints: '',
      description: '',
      format: null,
      validation_rules: [],
      transformation_rules: [],
      confidence_score: 0.0,
      ai_reasoning: [],
      data_patterns: [],
      suggested_indexes: [],
      data_quality_score: 0.0,
      uniqueness_score: 0.0,
      nullability_score: 0.0,
      complexity_score: 0.0,
      business_rules: [],
      data_lineage: []
    };
    setFieldMappings([...fieldMappings, newField]);
  };

  const removeFieldMapping = (index) => {
    const updatedMappings = fieldMappings.filter((_, i) => i !== index);
    setFieldMappings(updatedMappings);
  };

  // Validation
  const validateDatasetType = () => {
    const validationErrors = [];

    // Dataset type validation
    if (!datasetType.name.trim()) {
      validationErrors.push('Dataset type name is required');
    }

    if (!datasetType.description.trim()) {
      validationErrors.push('Dataset type description is required');
    }

    // Field mappings validation
    if (fieldMappings.length === 0) {
      validationErrors.push('At least one field mapping is required');
    }

    // Check for empty or invalid field names
    const emptyFieldNames = fieldMappings.filter(f => !f.field_name || !f.field_name.trim());
    if (emptyFieldNames.length > 0) {
      validationErrors.push('All fields must have a valid field name');
    }

    // Check for duplicate field names (case-insensitive)
    const fieldNames = fieldMappings.map(f => f.field_name.toLowerCase().trim());
    const duplicates = fieldNames.filter((name, index) => fieldNames.indexOf(name) !== index);
    if (duplicates.length > 0) {
      const duplicateNames = [...new Set(duplicates)];
      validationErrors.push(`Duplicate field names: ${duplicateNames.join(', ')}`);
    }

    // Check for primary key
    const primaryKeys = fieldMappings.filter(f => f.is_primary_key);
    if (primaryKeys.length === 0) {
      validationErrors.push('At least one field must be marked as primary key');
    }

    // Check for multiple primary keys
    if (primaryKeys.length > 1) {
      validationErrors.push('Only one field can be marked as primary key');
    }

    // Validate field names for special characters
    const invalidFieldNames = fieldMappings.filter(f => {
      const fieldName = f.field_name.trim();
      // Check for invalid characters in field names
      return /[^a-zA-Z0-9_]/g.test(fieldName) || fieldName.startsWith('_') || fieldName.startsWith('0');
    });
    if (invalidFieldNames.length > 0) {
      validationErrors.push('Field names can only contain letters, numbers, and underscores, and cannot start with underscore or number');
    }

    // Dataset-level validation
    if (!datasetType.retention_policy) {
      validationErrors.push('Retention policy is required');
    }

    if (!datasetType.data_classification) {
      validationErrors.push('Data classification is required');
    }

    if (!datasetType.security_level) {
      validationErrors.push('Security level is required');
    }

    setErrors(validationErrors);
    return validationErrors.length === 0;
  };

  // Create dataset type
  const createDatasetType = async () => {
    if (!validateDatasetType()) {
      toast.error('Please fix validation errors before creating dataset type');
      return;
    }

    setLoading(true);
    try {
      const datasetTypeData = {
        ...datasetType,
        field_definitions: fieldMappings
      };

      const response = await api.post('/api/design-enhanced/types', datasetTypeData);
      
      toast.success('Dataset type created successfully!');
      if (onDatasetTypeCreated) {
        onDatasetTypeCreated(response.data);
      }
    } catch (error) {
      console.error('Error creating dataset type:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create dataset type';
      toast.error(errorMessage);
      setErrors([errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (activeStep === 0 && !file) {
      toast.error('Please select a file first');
      return;
    }
    
    if (activeStep === 1 && !analysis) {
      toast.error('Please perform analysis first');
      return;
    }

    // Validate before moving to next step
    if (activeStep === 2) {
      // Validate field configuration
      const fieldErrors = [];
      
      if (fieldMappings.length === 0) {
        fieldErrors.push('At least one field mapping is required');
      }
      
      const emptyFieldNames = fieldMappings.filter(f => !f.field_name || !f.field_name.trim());
      if (emptyFieldNames.length > 0) {
        fieldErrors.push('All fields must have a valid field name');
      }
      
      const primaryKeys = fieldMappings.filter(f => f.is_primary_key);
      if (primaryKeys.length === 0) {
        fieldErrors.push('At least one field must be marked as primary key');
      }
      
      if (fieldErrors.length > 0) {
        setErrors(fieldErrors);
        toast.error('Please fix field configuration errors before proceeding');
        return;
      }
    }

    if (activeStep === steps.length - 1) {
      createDatasetType();
    } else {
      setActiveStep((prevStep) => prevStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setFile(null);
    setFileInfo(null);
    setAnalysis(null);
    setFieldMappings([]);
    setDatasetType({
      name: '',
      description: '',
      category: '',
      governing_body: '',
      version: '1.0',
      data_standards: [],
      tags: [],
      retention_policy: '5_years',
      data_classification: 'general',
      security_level: 'public'
    });
    setErrors([]);
    setWarnings([]);
  };

  const handleDatasetTypeChange = (field, value) => {
    setDatasetType(prev => ({ ...prev, [field]: value }));
    
    // Clear errors when user makes changes
    if (errors.length > 0) {
      setErrors([]);
    }
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Card>
        <CardContent>
          <Typography variant="h4" gutterBottom>
            <PsychologyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            AI-Powered Dataset Type Creator
          </Typography>
          
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Create dataset types with intelligent field analysis, validation, and standards compliance
          </Typography>

          {/* Progress and Status */}
          {loading && (
            <Box sx={{ mb: 3 }}>
              <LinearProgress variant="determinate" value={progress} />
              <Typography variant="body2" sx={{ mt: 1 }}>
                {progressMessage}
              </Typography>
            </Box>
          )}

          {/* Errors and Warnings */}
          {errors.length > 0 && (
            <Alert severity="error" sx={{ mb: 2 }}>
              <Typography variant="h6">Errors:</Typography>
              <List dense>
                {errors.map((error, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <ErrorIcon color="error" />
                    </ListItemIcon>
                    <ListItemText primary={error} />
                  </ListItem>
                ))}
              </List>
            </Alert>
          )}

          {warnings.length > 0 && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              <Typography variant="h6">Warnings:</Typography>
              <List dense>
                {warnings.map((warning, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <WarningIcon color="warning" />
                    </ListItemIcon>
                    <ListItemText primary={warning} />
                  </ListItem>
                ))}
              </List>
            </Alert>
          )}

          {/* Stepper */}
          <Stepper activeStep={activeStep} orientation="vertical" sx={{ mb: 3 }}>
            {steps.map((label, index) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
                <StepContent>
                  {index === 0 && (
                    <FileUploadStep
                      file={file}
                      fileInfo={fileInfo}
                      onFileSelect={handleFileSelect}
                      analysisOptions={analysisOptions}
                      setAnalysisOptions={setAnalysisOptions}
                      showAdvancedOptions={showAdvancedOptions}
                      setShowAdvancedOptions={setShowAdvancedOptions}
                    />
                  )}
                  
                  {index === 1 && (
                    <AnalysisStep
                      file={file}
                      analysis={analysis}
                      loading={loading}
                      onAnalyze={performAnalysis}
                      analysisOptions={analysisOptions}
                    />
                  )}
                  
                  {index === 2 && (
                    <FieldConfigurationStep
                      fieldMappings={fieldMappings}
                      onUpdateField={updateFieldMapping}
                      onAddField={addFieldMapping}
                      onRemoveField={removeFieldMapping}
                      analysis={analysis}
                    />
                  )}
                  
                  {index === 3 && (
                    <ValidationStep
                      datasetType={datasetType}
                      setDatasetType={handleDatasetTypeChange}
                      fieldMappings={fieldMappings}
                      analysis={analysis}
                    />
                  )}
                  
                  {index === 4 && (
                    <ReviewStep
                      datasetType={datasetType}
                      fieldMappings={fieldMappings}
                      analysis={analysis}
                      fileInfo={fileInfo}
                    />
                  )}
                  
                  <Box sx={{ mb: 2 }}>
                    <Button
                      variant="contained"
                      onClick={handleNext}
                      disabled={loading}
                      sx={{ mr: 1 }}
                    >
                      {index === steps.length - 1 ? 'Create Dataset Type' : 'Continue'}
                    </Button>
                    <Button
                      disabled={index === 0}
                      onClick={handleBack}
                      sx={{ mr: 1 }}
                    >
                      Back
                    </Button>
                    <Button onClick={handleReset}>
                      Reset
                    </Button>
                  </Box>
                </StepContent>
              </Step>
            ))}
          </Stepper>
        </CardContent>
      </Card>
    </Box>
  );
};

// Step Components
const FileUploadStep = ({ file, fileInfo, onFileSelect, analysisOptions, setAnalysisOptions, showAdvancedOptions, setShowAdvancedOptions }) => (
  <Box>
    <Typography variant="h6" gutterBottom>
      Upload File for Analysis
    </Typography>
    
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <UploadFileIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              File Upload
            </Typography>
            
            <input
              accept=".csv,.json,.xml,.txt"
              style={{ display: 'none' }}
              id="file-upload"
              type="file"
              onChange={onFileSelect}
            />
            <label htmlFor="file-upload">
              <Button
                variant="contained"
                component="span"
                startIcon={<UploadIcon />}
                sx={{ mb: 2 }}
              >
                Select File
              </Button>
            </label>
            
            {file && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Selected File:
                </Typography>
                <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="body2">
                    <strong>Name:</strong> {file.name}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Size:</strong> {formatFileSize(file.size)}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Type:</strong> {file.type || 'Unknown'}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Modified:</strong> {new Date(file.lastModified).toLocaleString()}
                  </Typography>
                </Paper>
              </Box>
            )}
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <SettingsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Analysis Options
            </Typography>
            
            <FormControlLabel
              control={
                <Switch
                  checked={analysisOptions.useClientSide}
                  onChange={(e) => setAnalysisOptions(prev => ({ ...prev, useClientSide: e.target.checked }))}
                />
              }
              label="Use Client-Side Analysis (Recommended for large files)"
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={analysisOptions.enableAI}
                  onChange={(e) => setAnalysisOptions(prev => ({ ...prev, enableAI: e.target.checked }))}
                />
              }
              label="Enable AI Intelligence"
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={analysisOptions.enableValidation}
                  onChange={(e) => setAnalysisOptions(prev => ({ ...prev, enableValidation: e.target.checked }))}
                />
              }
              label="Enable Validation"
            />
            
            <Button
              size="small"
              onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
              startIcon={<ExpandMoreIcon />}
              sx={{ mt: 1 }}
            >
              {showAdvancedOptions ? 'Hide' : 'Show'} Advanced Options
            </Button>
            
            {showAdvancedOptions && (
              <Box sx={{ mt: 2 }}>
                <TextField
                  label="Sample Size"
                  type="number"
                  value={analysisOptions.sampleSize}
                  onChange={(e) => setAnalysisOptions(prev => ({ ...prev, sampleSize: parseInt(e.target.value) }))}
                  fullWidth
                  size="small"
                  sx={{ mb: 2 }}
                />
                
                <Typography variant="body2" color="text.secondary">
                  Maximum file size: {formatFileSize(analysisOptions.maxFileSize)}
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  </Box>
);

const AnalysisStep = ({ file, analysis, loading, onAnalyze, analysisOptions }) => (
  <Box>
    <Typography variant="h6" gutterBottom>
      <AnalyzeIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
      AI-Powered File Analysis
    </Typography>
    
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              Analysis Method
            </Typography>
            
            <Chip
              icon={analysisOptions.useClientSide ? <ComputerIcon /> : <CloudIcon />}
              label={analysisOptions.useClientSide ? 'Client-Side Analysis' : 'Server-Side Analysis'}
              color={analysisOptions.useClientSide ? 'primary' : 'secondary'}
              sx={{ mb: 2 }}
            />
            
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {analysisOptions.useClientSide 
                ? 'Analysis will be performed in your browser, suitable for large files up to 10GB.'
                : 'Analysis will be performed on the server, suitable for smaller files with enhanced AI capabilities.'
              }
            </Typography>
            
            <Button
              variant="contained"
              onClick={onAnalyze}
              disabled={!file || loading}
              startIcon={loading ? <CircularProgress size={20} /> : <AnalyzeIcon />}
              fullWidth
            >
              {loading ? 'Analyzing...' : 'Start Analysis'}
            </Button>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} md={6}>
        {analysis && (
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Analysis Results
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2">
                  <strong>Format:</strong> {analysis.format}
                </Typography>
                <Typography variant="body2">
                  <strong>Fields Detected:</strong> {analysis.field_analysis?.length || 0}
                </Typography>
                <Typography variant="body2">
                  <strong>Total Rows:</strong> {analysis.total_rows || analysis.total_items || 'Unknown'}
                </Typography>
                {analysis.ai_enhanced && (
                  <Chip
                    icon={<AutoFixIcon />}
                    label="AI Enhanced"
                    color="success"
                    size="small"
                    sx={{ mt: 1 }}
                  />
                )}
              </Box>
              
              {analysis.identified_standards && analysis.identified_standards.length > 0 && (
                <Box>
                  <Typography variant="body2" gutterBottom>
                    <strong>Data Standards Identified:</strong>
                  </Typography>
                  {analysis.identified_standards.map((standard, index) => (
                    <Chip
                      key={index}
                      label={standard.name}
                      size="small"
                      sx={{ mr: 1, mb: 1 }}
                    />
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        )}
      </Grid>
    </Grid>
  </Box>
);

const FieldConfigurationStep = ({ fieldMappings, onUpdateField, onAddField, onRemoveField, analysis }) => (
  <Box>
    <Typography variant="h6" gutterBottom>
      <FieldIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
      AI-Powered Field Configuration
    </Typography>
    
    <Alert severity="info" sx={{ mb: 2 }}>
      <Typography variant="body2">
        <AutoFixIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        AI has analyzed your data and provided intelligent field mappings with auto-detected data types, uniqueness, nullability, and business rules. Review and adjust as needed.
      </Typography>
    </Alert>
    
    <Box sx={{ mb: 2 }}>
      <Button
        variant="outlined"
        onClick={onAddField}
        startIcon={<AddIcon />}
      >
        Add Field
      </Button>
    </Box>
    
    <Grid container spacing={1}>
      {fieldMappings.map((field, index) => (
        <Grid item xs={12} key={index}>
          <Paper variant="outlined" sx={{ p: 2, mb: 1 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                {field.display_name}
              </Typography>
              <Box display="flex" gap={1} alignItems="center">
                {field.confidence_score && (
                  <Chip
                    label={`${Math.round(field.confidence_score * 100)}%`}
                    color={field.confidence_score > 0.8 ? 'success' : field.confidence_score > 0.6 ? 'warning' : 'error'}
                    size="small"
                  />
                )}
                <IconButton
                  onClick={() => onRemoveField(index)}
                  color="error"
                  size="small"
                >
                  <DeleteIcon />
                </IconButton>
              </Box>
            </Box>

            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <TextField
                  label="Field Name"
                  value={field.field_name}
                  onChange={(e) => onUpdateField(index, { field_name: e.target.value })}
                  fullWidth
                  size="small"
                />
              </Grid>
              
              <Grid item xs={12} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Data Type</InputLabel>
                  <Select
                    value={field.data_type}
                    onChange={(e) => onUpdateField(index, { data_type: e.target.value })}
                    label="Data Type"
                  >
                    <MenuItem value="text">Text</MenuItem>
                    <MenuItem value="varchar">Varchar</MenuItem>
                    <MenuItem value="integer">Integer</MenuItem>
                    <MenuItem value="bigint">Big Integer</MenuItem>
                    <MenuItem value="numeric">Numeric</MenuItem>
                    <MenuItem value="date">Date</MenuItem>
                    <MenuItem value="timestamp">Timestamp</MenuItem>
                    <MenuItem value="boolean">Boolean</MenuItem>
                    <MenuItem value="geometry">Geometry</MenuItem>
                    <MenuItem value="uuid">UUID</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <Box display="flex" gap={1} alignItems="center">
                  <FormControlLabel
                    control={
                      <Switch
                        checked={field.is_required}
                        onChange={(e) => onUpdateField(index, { is_required: e.target.checked })}
                        size="small"
                      />
                    }
                    label="Required"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={field.is_primary_key}
                        onChange={(e) => onUpdateField(index, { is_primary_key: e.target.checked })}
                        size="small"
                      />
                    }
                    label="PK"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={field.is_unique}
                        onChange={(e) => onUpdateField(index, { is_unique: e.target.checked })}
                        size="small"
                      />
                    }
                    label="Unique"
                  />
                </Box>
              </Grid>
            </Grid>

            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Default Value"
                  value={field.default_value}
                  onChange={(e) => onUpdateField(index, { default_value: e.target.value })}
                  fullWidth
                  size="small"
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  label="Constraints"
                  value={field.constraints}
                  onChange={(e) => onUpdateField(index, { constraints: e.target.value })}
                  fullWidth
                  size="small"
                />
              </Grid>
            </Grid>

            {/* Compact AI Analysis Results */}
            {field.ai_reasoning && field.ai_reasoning.length > 0 && (
              <Accordion sx={{ mt: 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="caption">
                    <PsychologyIcon sx={{ mr: 1, verticalAlign: 'middle', fontSize: '1rem' }} />
                    AI Analysis ({field.ai_reasoning.length} insights)
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <List dense>
                    {field.ai_reasoning.slice(0, 3).map((reason, reasonIndex) => (
                      <ListItem key={reasonIndex}>
                        <ListItemIcon>
                          <InfoIcon color="info" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={reason} />
                      </ListItem>
                    ))}
                    {field.ai_reasoning.length > 3 && (
                      <ListItem>
                        <ListItemText primary={`... and ${field.ai_reasoning.length - 3} more insights`} />
                      </ListItem>
                    )}
                  </List>
                  
                  {field.data_patterns && field.data_patterns.length > 0 && (
                    <Box mt={1}>
                      <Typography variant="caption" display="block" gutterBottom>
                        Patterns: {field.data_patterns.slice(0, 3).join(', ')}
                        {field.data_patterns.length > 3 && ` (+${field.data_patterns.length - 3} more)`}
                      </Typography>
                    </Box>
                  )}
                </AccordionDetails>
              </Accordion>
            )}

            <TextField
              label="Description"
              value={field.description}
              onChange={(e) => onUpdateField(index, { description: e.target.value })}
              fullWidth
              multiline
              rows={1}
              size="small"
              sx={{ mt: 1 }}
            />
          </Paper>
        </Grid>
      ))}
    </Grid>
  </Box>
);

const ValidationStep = ({ datasetType, setDatasetType, fieldMappings, analysis }) => (
  <Box>
    <Typography variant="h6" gutterBottom>
      <SecurityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
      Validation & Standards
    </Typography>
    
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              Dataset Type Information
            </Typography>
            
            <TextField
              label="Name"
              value={datasetType.name}
              onChange={(e) => setDatasetType('name', e.target.value)}
              fullWidth
              sx={{ mb: 2 }}
            />
            
            <TextField
              label="Description"
              value={datasetType.description}
              onChange={(e) => setDatasetType('description', e.target.value)}
              fullWidth
              multiline
              rows={3}
              sx={{ mb: 2 }}
            />
            
            <TextField
              label="Category"
              value={datasetType.category}
              onChange={(e) => setDatasetType('category', e.target.value)}
              fullWidth
              sx={{ mb: 2 }}
            />
            
            <TextField
              label="Governing Body"
              value={datasetType.governing_body}
              onChange={(e) => setDatasetType('governing_body', e.target.value)}
              fullWidth
              sx={{ mb: 2 }}
            />
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              Data Governance
            </Typography>
            
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Data Classification</InputLabel>
              <Select
                value={datasetType.data_classification || 'general'}
                onChange={(e) => setDatasetType('data_classification', e.target.value)}
                label="Data Classification"
              >
                <MenuItem value="general">General</MenuItem>
                <MenuItem value="reference">Reference</MenuItem>
                <MenuItem value="financial">Financial</MenuItem>
                <MenuItem value="personal">Personal</MenuItem>
                <MenuItem value="temporal">Temporal</MenuItem>
                <MenuItem value="spatial">Spatial</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Security Level</InputLabel>
              <Select
                value={datasetType.security_level || 'public'}
                onChange={(e) => setDatasetType('security_level', e.target.value)}
                label="Security Level"
              >
                <MenuItem value="public">Public</MenuItem>
                <MenuItem value="restricted">Restricted</MenuItem>
                <MenuItem value="confidential">Confidential</MenuItem>
                <MenuItem value="secret">Secret</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Retention Policy</InputLabel>
              <Select
                value={datasetType.retention_policy || '5_years'}
                onChange={(e) => setDatasetType('retention_policy', e.target.value)}
                label="Retention Policy"
              >
                <MenuItem value="permanent">Permanent</MenuItem>
                <MenuItem value="10_years">10 Years</MenuItem>
                <MenuItem value="7_years">7 Years</MenuItem>
                <MenuItem value="5_years">5 Years</MenuItem>
                <MenuItem value="3_years">3 Years</MenuItem>
                <MenuItem value="1_year">1 Year</MenuItem>
              </Select>
            </FormControl>

            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              <strong>Data Classification:</strong> {datasetType.data_classification || 'general'}
              <br />
              <strong>Security Level:</strong> {datasetType.security_level || 'public'}
              <br />
              <strong>Retention Policy:</strong> {datasetType.retention_policy || '5_years'}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              Validation Summary
            </Typography>
            
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <CheckIcon color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary={`${fieldMappings.length} fields configured`}
                  secondary="Field definitions complete"
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon>
                  <CheckIcon color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary={`${fieldMappings.filter(f => f.is_primary_key).length} primary key(s)`}
                  secondary="Primary key configuration"
                />
              </ListItem>
              
              {analysis?.identified_standards && (
                <ListItem>
                  <ListItemIcon>
                    <CheckIcon color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary={`${analysis.identified_standards.length} data standards`}
                    secondary="Standards compliance identified"
                  />
                </ListItem>
              )}
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  </Box>
);

const ReviewStep = ({ datasetType, fieldMappings, analysis, fileInfo }) => (
  <Box>
    <Typography variant="h6" gutterBottom>
      <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
      Review & Create
    </Typography>
    
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              Dataset Type Summary
            </Typography>
            
            <Typography variant="body2" gutterBottom>
              <strong>Name:</strong> {datasetType.name}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Description:</strong> {datasetType.description}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Category:</strong> {datasetType.category}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Governing Body:</strong> {datasetType.governing_body}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Version:</strong> {datasetType.version}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Data Classification:</strong> {datasetType.data_classification || 'general'}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Security Level:</strong> {datasetType.security_level || 'public'}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Retention Policy:</strong> {datasetType.retention_policy || '5_years'}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              File Information
            </Typography>
            
            <Typography variant="body2" gutterBottom>
              <strong>File:</strong> {fileInfo?.name}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Size:</strong> {fileInfo ? formatFileSize(fileInfo.size) : 'Unknown'}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Format:</strong> {analysis?.format}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Fields:</strong> {fieldMappings.length}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              Field Definitions ({fieldMappings.length})
            </Typography>
            
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Field Name</TableCell>
                    <TableCell>Display Name</TableCell>
                    <TableCell>Data Type</TableCell>
                    <TableCell>Required</TableCell>
                    <TableCell>Primary Key</TableCell>
                    <TableCell>Description</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {fieldMappings.map((field, index) => (
                    <TableRow key={index}>
                      <TableCell>{field.field_name}</TableCell>
                      <TableCell>{field.display_name}</TableCell>
                      <TableCell>{field.data_type}</TableCell>
                      <TableCell>
                        {field.is_required ? <CheckIcon color="success" /> : <CancelIcon color="disabled" />}
                      </TableCell>
                      <TableCell>
                        {field.is_primary_key ? <CheckIcon color="success" /> : <CancelIcon color="disabled" />}
                      </TableCell>
                      <TableCell>{field.description}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  </Box>
);

export default AIDatasetTypeCreator; 