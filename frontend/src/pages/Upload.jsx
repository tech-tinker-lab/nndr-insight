import React, { useState, useEffect } from 'react';
import { 
  Upload as UploadIcon, 
  FileText, 
  Database, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  X,
  Download,
  RefreshCw,
  Play,
  Pause,
  Square,
  Settings,
  Info,
  Trash2,
  Eye,
  BarChart3,
  FileArchive,
  FileCode,
  FileSpreadsheet,
  Edit3,
  Save,
  Plus,
  Minus,
  Copy,
  MapPin,
  Columns,
  Table
} from 'lucide-react';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { useUser } from '../context/UserContext';
import AIDataAnalyzer from '../services/aiDataAnalyzer';
import StagingTableAutocomplete from '../components/StagingTableAutocomplete';
import StagingConfigManager from '../components/StagingConfigManager';
import EnhancedColumnMapping from '../components/EnhancedColumnMapping';
import UploadActionSuggestions from '../components/UploadActionSuggestions';

const API_BASE_URL = 'http://localhost:8000/api';

// Column mapping types
const MAPPING_TYPES = {
  DIRECT: 'direct',           // Direct column copy
  MERGE: 'merge',             // Merge multiple columns
  DEFAULT: 'default',         // Set default value
  TRANSFORM: 'transform',     // Apply transformation
  CONDITIONAL: 'conditional'  // Conditional mapping
};

// Transformation functions
const TRANSFORMATIONS = {
  UPPERCASE: 'uppercase',
  LOWERCASE: 'lowercase',
  TRIM: 'trim',
  CONCATENATE: 'concatenate',
  SPLIT: 'split',
  REPLACE: 'replace',
  DATE_FORMAT: 'date_format',
  NUMBER_FORMAT: 'number_format'
};

// Staging table configuration store with persistence
const useStagingConfig = () => {
  const [configs, setConfigs] = useState({});
  const [loaded, setLoaded] = useState(false);

  // Load configurations from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem('staging_configs');
      if (stored) {
        const parsed = JSON.parse(stored);
        setConfigs(parsed);
        console.log('Loaded staging configs from localStorage:', parsed);
      }
    } catch (error) {
      console.error('Failed to load staging configs from localStorage:', error);
    }
    setLoaded(true);
  }, []);

  // Save to localStorage whenever configs change
  useEffect(() => {
    if (loaded) {
      try {
        localStorage.setItem('staging_configs', JSON.stringify(configs));
        console.log('Saved staging configs to localStorage:', configs);
      } catch (error) {
        console.error('Failed to save staging configs to localStorage:', error);
      }
    }
  }, [configs, loaded]);

  const saveConfig = async (datasetId, config) => {
    // Update local state
    setConfigs(prev => ({
      ...prev,
      [datasetId]: config
    }));

    // Also save to backend (optional)
    try {
      await api.post(`${API_BASE_URL}/admin/staging/configs`, {
        dataset_id: datasetId,
        config: config
      });
      console.log('Saved config to backend for dataset:', datasetId);
    } catch (error) {
      console.warn('Failed to save config to backend, using localStorage only:', error);
    }
  };

  const getConfig = (datasetId) => {
    return configs[datasetId] || null;
  };

  const getAllConfigs = () => {
    return configs;
  };

  const deleteConfig = (datasetId) => {
    setConfigs(prev => {
      const newConfigs = { ...prev };
      delete newConfigs[datasetId];
      return newConfigs;
    });
  };

  return { saveConfig, getConfig, getAllConfigs, deleteConfig };
};

// File type detection and analysis utilities
const FileAnalyzer = {
  // Detect file type based on extension and content
  detectFileType: (file) => {
    const extension = file.name.toLowerCase().split('.').pop();
    const mimeType = file.type;
    
    // Check for ZIP files
    if (extension === 'zip' || mimeType === 'application/zip') {
      return 'zip';
    }
    
    // Check for CSV files
    if (extension === 'csv' || mimeType === 'text/csv') {
      return 'csv';
    }
    
    // Check for JSON files
    if (extension === 'json' || mimeType === 'application/json') {
      return 'json';
    }
    
    // Check for XML files
    if (extension === 'xml' || mimeType === 'application/xml' || mimeType === 'text/xml') {
      return 'xml';
    }
    
    // Check for YAML files
    if (extension === 'yml' || extension === 'yaml' || mimeType === 'text/yaml') {
      return 'yaml';
    }
    
    // Check for GML files
    if (extension === 'gml' || mimeType === 'application/gml+xml') {
      return 'gml';
    }
    
    // Check for GeoPackage files
    if (extension === 'gpkg' || mimeType === 'application/geopackage+sqlite3') {
      return 'geopackage';
    }
    
    // Check for Shapefile components
    if (['shp', 'dbf', 'shx', 'prj', 'cpg', 'qix'].includes(extension)) {
      return 'shapefile';
    }
    
    // Check for SDMX files
    if (extension === 'sdmx' || mimeType === 'application/vnd.sdmx.structure+xml') {
      return 'sdmx';
    }
    
    // Check for KML files
    if (extension === 'kml' || mimeType === 'application/vnd.google-earth.kml+xml') {
      return 'kml';
    }
    
    // Check for GeoJSON files
    if (extension === 'geojson' || mimeType === 'application/geo+json') {
      return 'geojson';
    }
    
        // Check for text files
    if (extension === 'txt' || mimeType.startsWith('text/')) {
      return 'text';
    }
    
    // Default to text for unknown types
    return 'text';
  },
  
  // Auto-detect data type from sample values
  detectDataType: (sampleValues) => {
    if (!sampleValues || sampleValues.length === 0) return 'text';
    
    // Check for boolean values
    const booleanPattern = /^(true|false|yes|no|1|0)$/i;
    if (sampleValues.every(val => booleanPattern.test(String(val)))) {
      return 'boolean';
    }
    
    // Check for date values
    const datePatterns = [
      /^\d{4}-\d{2}-\d{2}$/, // YYYY-MM-DD
      /^\d{2}\/\d{2}\/\d{4}$/, // MM/DD/YYYY
      /^\d{2}-\d{2}-\d{4}$/, // MM-DD-YYYY
      /^\d{4}\/\d{2}\/\d{2}$/, // YYYY/MM/DD
      /^\d{1,2}\/\d{1,2}\/\d{2,4}$/, // M/D/YY or M/D/YYYY
    ];
    
    if (sampleValues.every(val => {
      const strVal = String(val);
      return datePatterns.some(pattern => pattern.test(strVal));
    })) {
      return 'date';
    }
    
    // Check for timestamp values
    const timestampPatterns = [
      /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/, // YYYY-MM-DD HH:MM:SS
      /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/, // ISO format
    ];
    
    if (sampleValues.every(val => {
      const strVal = String(val);
      return timestampPatterns.some(pattern => pattern.test(strVal));
    })) {
      return 'timestamp';
    }
    
    // Check for integer values
    const integerPattern = /^-?\d+$/;
    if (sampleValues.every(val => integerPattern.test(String(val)))) {
      return 'integer';
    }
    
    // Check for decimal values
    const decimalPattern = /^-?\d+\.\d+$/;
    if (sampleValues.every(val => {
      const strVal = String(val);
      return decimalPattern.test(strVal) || integerPattern.test(strVal);
    })) {
      return 'decimal';
    }
    
    // Default to text for everything else
    return 'text';
  },
  
  // Auto-detect data type from sample values
  detectDataType: (sampleValues) => {
    if (!sampleValues || sampleValues.length === 0) return 'text';
    
    // Check for boolean values
    const booleanPattern = /^(true|false|yes|no|1|0)$/i;
    if (sampleValues.every(val => booleanPattern.test(String(val)))) {
      return 'boolean';
    }
    
    // Check for date values
    const datePatterns = [
      /^\d{4}-\d{2}-\d{2}$/, // YYYY-MM-DD
      /^\d{2}\/\d{2}\/\d{4}$/, // MM/DD/YYYY
      /^\d{2}-\d{2}-\d{4}$/, // MM-DD-YYYY
      /^\d{4}\/\d{2}\/\d{2}$/, // YYYY/MM/DD
      /^\d{1,2}\/\d{1,2}\/\d{2,4}$/, // M/D/YY or M/D/YYYY
    ];
    
    if (sampleValues.every(val => {
      const strVal = String(val);
      return datePatterns.some(pattern => pattern.test(strVal));
    })) {
      return 'date';
    }
    
    // Check for timestamp values
    const timestampPatterns = [
      /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/, // YYYY-MM-DD HH:MM:SS
      /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/, // ISO format
    ];
    
    if (sampleValues.every(val => {
      const strVal = String(val);
      return timestampPatterns.some(pattern => pattern.test(strVal));
    })) {
      return 'timestamp';
    }
    
    // Check for integer values
    const integerPattern = /^-?\d+$/;
    if (sampleValues.every(val => integerPattern.test(String(val)))) {
      return 'integer';
    }
    
    // Check for decimal values
    const decimalPattern = /^-?\d+\.\d+$/;
    if (sampleValues.every(val => {
      const strVal = String(val);
      return decimalPattern.test(strVal) || integerPattern.test(strVal);
    })) {
      return 'decimal';
    }
    
    // Default to text for everything else
    return 'text';
  },

  // Get file icon based on type
  getFileIcon: (fileType) => {
    switch (fileType) {
      case 'zip':
        return <FileArchive className="w-5 h-5 text-orange-500" />;
      case 'csv':
        return <FileSpreadsheet className="w-5 h-5 text-green-500" />;
      case 'json':
      case 'geojson':
        return <FileCode className="w-5 h-5 text-yellow-500" />;
      case 'xml':
      case 'gml':
      case 'sdmx':
      case 'kml':
        return <FileCode className="w-5 h-5 text-blue-500" />;
      case 'yaml':
        return <FileCode className="w-5 h-5 text-purple-500" />;
      case 'geopackage':
        return <MapPin className="w-5 h-5 text-red-500" />;
      case 'shapefile':
        return <MapPin className="w-5 h-5 text-indigo-500" />;
      case 'text':
        return <FileText className="w-5 h-5 text-gray-500" />;
      default:
        return <FileText className="w-5 h-5 text-gray-400" />;
    }
  },

  // Analyze file contents (peek into data)
  analyzeFile: async (file) => {
    console.log('FileAnalyzer.analyzeFile called for:', file.name);
    const fileType = FileAnalyzer.detectFileType(file);
    console.log('Detected file type:', fileType);
    
    const analysis = {
      type: fileType,
      size: file.size,
      extension: file.name.toLowerCase().split('.').pop(),
      preview: null,
      zipContents: null,
      directoryStructure: null,
      aiAnalysis: null,
      error: null
    };

    try {
      if (fileType === 'zip') {
        console.log('Analyzing ZIP file:', file.name);
        
        // Add retry mechanism for ZIP analysis
        let retryCount = 0;
        const maxRetries = 3;
        
        while (retryCount < maxRetries) {
          try {
            analysis.zipContents = await FileAnalyzer.analyzeZipFile(file);
            analysis.directoryStructure = FileAnalyzer.buildDirectoryStructure(analysis.zipContents);
            console.log('ZIP analysis result:', analysis.zipContents);
            console.log('Directory structure:', analysis.directoryStructure);
            break; // Success, exit retry loop
          } catch (error) {
            retryCount++;
            console.warn(`ZIP analysis attempt ${retryCount} failed:`, error.message);
            
            if (retryCount >= maxRetries) {
              throw error; // Re-throw the error after all retries exhausted
            }
            
            // Wait a bit before retrying
            await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
          }
        }
      } else if (fileType === 'geopackage') {
        console.log('Analyzing GeoPackage file:', file.name);
        analysis.preview = await FileAnalyzer.analyzeGeoPackage(file);
        console.log('GeoPackage analysis result:', analysis.preview);
      } else if (fileType === 'shapefile') {
        console.log('Analyzing Shapefile component:', file.name);
        analysis.preview = await FileAnalyzer.analyzeShapefile(file);
        console.log('Shapefile analysis result:', analysis.preview);
      } else {
        console.log('Getting preview for file type:', fileType);
        analysis.preview = await FileAnalyzer.getFilePreview(file, fileType);
        console.log('Preview result:', analysis.preview);
      }
      
      // Perform AI analysis for government data
      if (['csv', 'json', 'xml', 'gml', 'geojson'].includes(fileType)) {
        try {
          console.log('Starting AI analysis for:', file.name);
          const content = await FileAnalyzer.getFileContent(file);
          const aiAnalyzer = new AIDataAnalyzer();
          analysis.aiAnalysis = await aiAnalyzer.analyzeDataset(file, content, fileType);
          console.log('AI analysis completed for:', file.name, analysis.aiAnalysis);
        } catch (error) {
          console.error('AI analysis failed:', error);
          analysis.aiAnalysis = { error: 'AI analysis failed: ' + error.message };
        }
      }
    } catch (error) {
      console.error('Error in analyzeFile:', error);
      analysis.error = error.message;
    }

    console.log('Final analysis result:', analysis);
    return analysis;
  },

  // Analyze ZIP file contents with directory structure
  analyzeZipFile: async (file) => {
    const JSZip = await import('jszip');
    const zip = new JSZip.default();
    
    try {
      // Create a copy of the file to avoid conflicts with other readers
      const fileCopy = file.slice(0, file.size);
      
      console.log('Starting ZIP analysis for:', file.name, 'Size:', file.size);
      
      const zipData = await zip.loadAsync(fileCopy);
      console.log('ZIP loaded successfully, processing entries...');
      
      const contents = [];
      const fileGroups = {};
      
      for (const [filename, zipEntry] of Object.entries(zipData.files)) {
        if (!zipEntry.dir) {
          const fileType = FileAnalyzer.detectFileType({ name: filename });
          const fileInfo = {
            name: filename,
            path: filename,
            size: zipEntry._data.uncompressedSize,
            type: fileType,
            icon: FileAnalyzer.getFileIcon(fileType),
            isDirectory: false,
            children: []
          };
          
          contents.push(fileInfo);
          
          // Group by file type for easier analysis
          if (!fileGroups[fileType]) {
            fileGroups[fileType] = [];
          }
          fileGroups[fileType].push(fileInfo);
          
          // Special handling for shapefile components
          if (fileType === 'shapefile') {
            const baseName = filename.replace(/\.[^/.]+$/, '');
            if (!fileGroups[`shapefile_${baseName}`]) {
              fileGroups[`shapefile_${baseName}`] = [];
            }
            fileGroups[`shapefile_${baseName}`].push(fileInfo);
          }
        }
      }
      
      console.log('ZIP analysis completed. Found', contents.length, 'files');
      
      return {
        files: contents,
        fileGroups,
        totalFiles: contents.length,
        totalSize: contents.reduce((sum, file) => sum + file.size, 0)
      };
    } catch (error) {
      console.error('ZIP analysis error:', error);
      
      // Provide more specific error messages
      if (error.message.includes('permission') || error.message.includes('could not be read')) {
        throw new Error(`ZIP file access error: The file may be corrupted or in use by another process. Please try again.`);
      } else if (error.message.includes('Invalid file signature')) {
        throw new Error(`Invalid ZIP file: The file does not appear to be a valid ZIP archive.`);
      } else {
        throw new Error(`Failed to analyze ZIP file: ${error.message}`);
      }
    }
  },

  // Build directory structure from ZIP contents
  buildDirectoryStructure: (zipContents) => {
    if (!zipContents.files) return null;
    
    const structure = {
      name: 'root',
      type: 'directory',
      children: []
    };
    
    const pathMap = new Map();
    pathMap.set('', structure);
    
    zipContents.files.forEach(file => {
      const pathParts = file.path.split('/');
      let currentPath = '';
      
      // Build directory structure
      for (let i = 0; i < pathParts.length - 1; i++) {
        const part = pathParts[i];
        const parentPath = currentPath;
        currentPath = currentPath ? `${currentPath}/${part}` : part;
        
        if (!pathMap.has(currentPath)) {
          const dirNode = {
            name: part,
            type: 'directory',
            path: currentPath,
            children: []
          };
          pathMap.set(currentPath, dirNode);
          pathMap.get(parentPath).children.push(dirNode);
        }
      }
      
      // Add file to its parent directory
      const fileName = pathParts[pathParts.length - 1];
      const fileNode = {
        name: fileName,
        type: 'file',
        path: file.path,
        size: file.size,
        fileType: file.type,
        icon: file.icon
      };
      
      const parentPath = pathParts.slice(0, -1).join('/');
      pathMap.get(parentPath).children.push(fileNode);
    });
    
    return structure;
  },

  // Get preview of file contents
  getFilePreview: async (file, fileType) => {
    console.log('getFilePreview called for:', file.name, 'type:', fileType);
    const maxPreviewSize = 1024 * 10; // 10KB preview
    const maxLines = 10;
    
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        console.log('FileReader onload triggered for:', file.name);
        try {
          let content = e.target.result;
          console.log('File content length:', content.length);
          console.log('First 200 chars:', content.substring(0, 200));
          
          let preview = null;
          
          switch (fileType) {
            case 'csv':
              console.log('Processing as CSV');
              preview = FileAnalyzer.previewCSV(content, maxLines);
              break;
            case 'json':
              console.log('Processing as JSON');
              preview = FileAnalyzer.previewJSON(content, maxLines);
              break;
            case 'xml':
            case 'gml':
              console.log('Processing as XML/GML');
              preview = FileAnalyzer.previewXML(content, maxLines);
              break;
            case 'yaml':
              console.log('Processing as YAML');
              preview = FileAnalyzer.previewYAML(content, maxLines);
              break;
            case 'text':
              console.log('Processing as text');
              preview = FileAnalyzer.previewText(content, maxLines);
              break;
            default:
              console.log('Unknown file type, using generic preview');
              preview = { type: 'unknown', content: 'File type not supported for preview' };
          }
          
          console.log('Preview generated:', preview);
          resolve(preview);
        } catch (error) {
          console.error('Error in FileReader onload:', error);
          reject(new Error(`Failed to parse file: ${error.message}`));
        }
      };
      
      reader.onerror = (error) => {
        console.error('FileReader error:', error);
        reject(new Error('Failed to read file'));
      };
      
      if (file.size > maxPreviewSize) {
        console.log('File is large, reading first', maxPreviewSize, 'bytes');
        const blob = file.slice(0, maxPreviewSize);
        reader.readAsText(blob);
      } else {
        console.log('Reading entire file');
        reader.readAsText(file);
      }
    });
  },

  // Preview CSV content with proper quoted field handling
  previewCSV: (content, maxLines) => {
    const lines = content.split('\n').slice(0, maxLines);
    
    // Detect delimiter
    const detectDelimiter = (firstLine) => {
      const delimiters = [',', ';', '\t', '|', ':', ' '];
      const counts = {};
      
      for (const delim of delimiters) {
        counts[delim] = (firstLine.match(new RegExp(`\\${delim === '\\' ? '\\\\' : delim}`, 'g')) || []).length;
      }
      
      // Find delimiter with highest count
      let bestDelimiter = ',';
      let maxCount = 0;
      
      for (const [delim, count] of Object.entries(counts)) {
        if (count > maxCount) {
          maxCount = count;
          bestDelimiter = delim;
        }
      }
      
      return bestDelimiter;
    };
    
    // Parse CSV line with proper quoted field handling
    const parseCSVLine = (line, delimiter = ',') => {
      const result = [];
      let current = '';
      let inQuotes = false;
      let quoteChar = null;
      
      for (let i = 0; i < line.length; i++) {
        const char = line[i];
        
        // Handle quote characters
        if ((char === '"' || char === "'") && !inQuotes) {
          inQuotes = true;
          quoteChar = char;
          continue;
        }
        
        if (char === quoteChar && inQuotes) {
          // Check for escaped quote
          if (i + 1 < line.length && line[i + 1] === quoteChar) {
            current += quoteChar;
            i++; // Skip next quote
          } else {
            inQuotes = false;
            quoteChar = null;
          }
          continue;
        }
        
        // Handle delimiter
        if (char === delimiter && !inQuotes) {
          result.push(current.trim());
          current = '';
          continue;
        }
        
        current += char;
      }
      
      // Add the last field
      result.push(current.trim());
      return result;
    };
    
    const detectedDelimiter = detectDelimiter(lines[0] || '');
    const headers = lines[0] ? parseCSVLine(lines[0], detectedDelimiter) : [];
    const data = lines.slice(1).map(line => parseCSVLine(line, detectedDelimiter));
    
    return {
      type: 'csv',
      headers,
      data,
      totalLines: content.split('\n').length,
      previewLines: lines.length,
      detectedDelimiter
    };
  },

  // Preview JSON content
  previewJSON: (content, maxLines) => {
    const parsed = JSON.parse(content);
    let preview;
    
    if (Array.isArray(parsed)) {
      preview = parsed.slice(0, maxLines);
    } else if (typeof parsed === 'object') {
      preview = Object.keys(parsed).slice(0, maxLines).reduce((obj, key) => {
        obj[key] = parsed[key];
        return obj;
      }, {});
    } else {
      preview = parsed;
    }
    
    return {
      type: 'json',
      data: preview,
      isArray: Array.isArray(parsed),
      totalItems: Array.isArray(parsed) ? parsed.length : Object.keys(parsed).length
    };
  },

  // Preview XML content
  previewXML: (content, maxLines) => {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(content, 'text/xml');
    
    // Get root element and first few child elements
    const root = xmlDoc.documentElement;
    const children = Array.from(root.children).slice(0, maxLines);
    
    return {
      type: 'xml',
      rootElement: root.tagName,
      children: children.map(child => ({
        tagName: child.tagName,
        attributes: Array.from(child.attributes).map(attr => ({
          name: attr.name,
          value: attr.value
        })),
        textContent: child.textContent?.substring(0, 100) + (child.textContent?.length > 100 ? '...' : '')
      })),
      totalChildren: root.children.length
    };
  },

  // Preview YAML content
  previewYAML: (content, maxLines) => {
    const lines = content.split('\n').slice(0, maxLines);
    return {
      type: 'yaml',
      lines,
      totalLines: content.split('\n').length,
      previewLines: lines.length
    };
  },

  // Preview text content
  previewText: (content, maxLines) => {
    const lines = content.split('\n').slice(0, maxLines);
    return {
      type: 'text',
      lines,
      totalLines: content.split('\n').length,
      previewLines: lines.length
    };
  },

  // Get file content as text for AI analysis
  getFileContent: async (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const content = e.target.result;
          resolve(content);
        } catch (error) {
          reject(new Error(`Failed to read file content: ${error.message}`));
        }
      };
      
      reader.onerror = (error) => {
        reject(new Error('Failed to read file'));
      };
      
      // Limit content size for AI analysis (first 100KB)
      const maxContentSize = 1024 * 100;
      if (file.size > maxContentSize) {
        const blob = file.slice(0, maxContentSize);
        reader.readAsText(blob);
      } else {
        reader.readAsText(file);
      }
    });
  },

  // Analyze GeoPackage file (basic detection)
  analyzeGeoPackage: async (file) => {
    // GeoPackage is a SQLite database, so we can't easily read it in the browser
    // We'll provide basic information and suggest backend processing
    return {
      type: 'geopackage',
      message: 'GeoPackage detected. This is a SQLite-based geospatial format.',
      layers: 'Layers and features will be detected during backend processing.',
      size: file.size,
      extension: 'gpkg',
      requiresBackendProcessing: true,
      supportedOperations: [
        'Layer detection',
        'Feature count analysis',
        'Geometry type identification',
        'Attribute field mapping',
        'Spatial index analysis'
      ]
    };
  },

  // Analyze Shapefile component
  analyzeShapefile: async (file) => {
    const extension = file.name.toLowerCase().split('.').pop();
    
    const componentInfo = {
      shp: 'Main shapefile geometry file',
      dbf: 'Attribute data file (dBase format)',
      shx: 'Shape index file',
      prj: 'Projection information file',
      cpg: 'Character encoding file',
      qix: 'Spatial index file'
    };
    
    return {
      type: 'shapefile',
      component: extension,
      description: componentInfo[extension] || 'Shapefile component',
      message: `Shapefile component detected: ${extension.toUpperCase()}`,
      requiresCompleteSet: true,
      missingComponents: ['shp', 'dbf', 'shx'].filter(comp => comp !== extension),
      size: file.size,
      extension: extension,
      requiresBackendProcessing: true,
      supportedOperations: [
        'Geometry analysis',
        'Attribute field mapping',
        'Projection detection',
        'Feature count analysis',
        'Spatial extent calculation'
      ]
    };
  }
};

export default function Upload() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [dragActive, setDragActive] = useState(false);
  const { user } = useUser();
  const [uploadHistory, setUploadHistory] = useState([]);
  const [historyFilters, setHistoryFilters] = useState({ table_name: '', filename: '', start_date: '', end_date: '' });
  const [historyLoading, setHistoryLoading] = useState(false);
  const [showAllHistory, setShowAllHistory] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [showConfigManager, setShowConfigManager] = useState(false);
  const { saveConfig, getConfig, getAllConfigs, deleteConfig } = useStagingConfig();

  useEffect(() => {
    fetchUploadHistory();
  }, []);

  const fetchUploadHistory = async () => {
    setHistoryLoading(true);
    try {
      let url, params;
      if (user && (user.role === 'admin' || user.role === 'power_user') && showAllHistory) {
        url = `${API_BASE_URL}/admin/staging/migration_history`;
        params = { status: 'upload', ...historyFilters };
      } else {
        url = `${API_BASE_URL}/ingestions/my_uploads`;
        params = { ...historyFilters };
      }
      console.log('Fetching upload history from:', url);
      console.log('With params:', params);
      const response = await api.get(url, { params });
      console.log('Upload history response:', response.data);
      setUploadHistory(response.data.history || []);
      console.log('Set upload history to:', response.data.history || []);
    } catch (err) {
      console.error('Error fetching upload history:', err);
      toast.error('Failed to fetch upload history');
    } finally {
      setHistoryLoading(false);
    }
  };

  const retryUpload = async (historyItem) => {
    try {
      // Find file in queue or prompt user to re-select
      toast('Please re-upload the file manually.');
    } catch (err) {
      toast.error('Retry failed');
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = async (fileList) => {
    console.log('handleFiles called with:', fileList.length, 'files');
    setAnalyzing(true);
    
    try {
      const newFiles = [];
      
      for (const file of Array.from(fileList)) {
        const fileId = Date.now() + Math.random();
        console.log('Processing file:', file.name, 'with ID:', fileId);
        
        // Create initial file object
        const fileObj = {
          id: fileId,
          file,
          name: file.name,
          size: file.size,
          type: file.type,
          status: 'pending',
          progress: 0,
          error: null,
          analysis: null
        };
        
        newFiles.push(fileObj);
        console.log('Added file to newFiles:', fileObj);
      }
      
      // First, add all files to state
      console.log('Setting files state with newFiles:', newFiles);
      setFiles(prev => {
        const combined = [...prev, ...newFiles];
        console.log('Combined files state:', combined);
        return combined;
      });
      
      // Then analyze each file
      for (const fileObj of newFiles) {
        try {
          console.log('Starting analysis for:', fileObj.name);
          const analysis = await FileAnalyzer.analyzeFile(fileObj.file);
          console.log('Analysis completed for:', fileObj.name, 'Result:', analysis);
          
          setFiles(prev => {
            console.log('Updating files state for ID:', fileObj.id);
            const updated = prev.map(f => 
              f.id === fileObj.id ? { ...f, analysis } : f
            );
            console.log('Updated files state:', updated);
            return updated;
          });
        } catch (error) {
          console.error('File analysis failed for:', fileObj.name, 'Error:', error);
          setFiles(prev => prev.map(f => 
            f.id === fileObj.id ? { ...f, analysis: { error: error.message } } : f
          ));
        }
      }
    } catch (error) {
      console.error('Error processing files:', error);
      toast.error('Failed to process files');
    } finally {
      console.log('Setting analyzing to false');
      setAnalyzing(false);
    }
  };

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const startIngestion = async (fileId) => {
    const file = files.find(f => f.id === fileId);
    if (!file) {
      toast.error('Please select a file');
      return;
    }

    try {
      setUploading(true);
      setUploadProgress(prev => ({ ...prev, [fileId]: 0 }));

      const formData = new FormData();
      formData.append('file', file.file);

      await api.post(`${API_BASE_URL}/ingestions/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(prev => ({ ...prev, [fileId]: progress }));
        }
      });

      toast.success(`Upload complete for ${file.name}`);
      setFiles(prev => prev.map(f => 
        f.id === fileId ? { ...f, status: 'uploaded' } : f
      ));
      
      fetchUploadHistory();
    } catch (err) {
      console.error('Error starting ingestion:', err);
      toast.error('Failed to upload');
      setFiles(prev => prev.map(f => 
        f.id === fileId ? { ...f, status: 'error', error: err.message } : f
      ));
    } finally {
      setUploading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'running':
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-gray-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50';
      case 'running':
        return 'text-blue-600 bg-blue-50';
      case 'failed':
        return 'text-red-600 bg-red-50';
      case 'pending':
        return 'text-gray-600 bg-gray-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours}h ${minutes}m ${secs}s`;
  };

  // Intelligent ZIP Analyzer Component
  const ZIPIntelligentAnalyzer = ({ zipContents, directoryStructure, file }) => {
    const [viewMode, setViewMode] = useState('structure'); // 'structure' or 'selection'
    const [selectedHeaderFile, setSelectedHeaderFile] = useState(null);
    const [selectedDataFiles, setSelectedDataFiles] = useState([]);
    const [suggestedFiles, setSuggestedFiles] = useState({ header: null, data: [] });

    // Analyze ZIP contents and suggest files intelligently
    useEffect(() => {
      if (zipContents && zipContents.files) {
        const suggestions = analyzeZIPContents(zipContents);
        setSuggestedFiles(suggestions);
        
        // Auto-select suggested files
        if (suggestions.header) {
          setSelectedHeaderFile(suggestions.header);
        }
        if (suggestions.data.length > 0) {
          setSelectedDataFiles(suggestions.data);
        }
      }
    }, [zipContents]);

    // Intelligent analysis of ZIP contents
    const analyzeZIPContents = (contents) => {
      const suggestions = { header: null, data: [] };
      
      // Find potential header files (small CSV files, README files, etc.)
      const potentialHeaders = contents.files.filter(file => {
        const name = file.name.toLowerCase();
        const size = file.size;
        
        // Look for header indicators
        return (
          name.includes('header') ||
          name.includes('schema') ||
          name.includes('readme') ||
          name.includes('metadata') ||
          name.includes('description') ||
          (name.endsWith('.csv') && size < 5000) || // Small CSV files
          (name.endsWith('.txt') && size < 2000)    // Small text files
        );
      });

      // Find potential data files
      const potentialData = contents.files.filter(file => {
        const name = file.name.toLowerCase();
        const size = file.size;
        
        // Look for data indicators
        return (
          (name.endsWith('.csv') && size > 1000) ||
          (name.endsWith('.json') && size > 1000) ||
          (name.endsWith('.xml') && size > 1000) ||
          (name.endsWith('.gml') && size > 1000) ||
          name.includes('data') ||
          name.includes('records') ||
          name.includes('values')
        );
      });

      // Suggest the best header file
      if (potentialHeaders.length > 0) {
        suggestions.header = potentialHeaders[0]; // Take the first one for now
      }

      // Suggest data files (limit to 5 for usability)
      suggestions.data = potentialData.slice(0, 5);

      return suggestions;
    };

    // Get file type icon
    const getFileIcon = (fileName) => {
      const ext = fileName.toLowerCase().split('.').pop();
      switch (ext) {
        case 'csv': return <FileSpreadsheet className="w-4 h-4 text-green-500" />;
        case 'json': return <FileCode className="w-4 h-4 text-yellow-500" />;
        case 'xml': return <FileCode className="w-4 h-4 text-blue-500" />;
        case 'gml': return <FileCode className="w-4 h-4 text-purple-500" />;
        case 'txt': return <FileText className="w-4 h-4 text-gray-500" />;
        default: return <FileText className="w-4 h-4 text-gray-400" />;
      }
    };

    // Toggle file selection
    const toggleFileSelection = (file, type) => {
      if (type === 'header') {
        setSelectedHeaderFile(selectedHeaderFile?.path === file.path ? null : file);
      } else {
        setSelectedDataFiles(prev => {
          const isSelected = prev.some(f => f.path === file.path);
          if (isSelected) {
            return prev.filter(f => f.path !== file.path);
          } else {
            return [...prev, file];
          }
        });
      }
    };

    return (
      <div className="text-xs">
        {/* Header with view toggle */}
        <div className="flex items-center justify-between mb-3">
          <div className="font-medium text-gray-700">
            ZIP Analysis ({zipContents.totalFiles} files, {formatFileSize(zipContents.totalSize)})
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setViewMode('structure')}
              className={`px-2 py-1 rounded text-xs ${
                viewMode === 'structure' 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              📁 Structure
            </button>
            <button
              onClick={() => setViewMode('selection')}
              className={`px-2 py-1 rounded text-xs ${
                viewMode === 'selection' 
                  ? 'bg-green-100 text-green-700' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              🎯 Select Files
            </button>
          </div>
        </div>

        {/* File Groups Summary */}
        {Object.keys(zipContents.fileGroups).length > 0 && (
          <div className="mb-3 p-2 bg-gray-50 rounded">
            <div className="font-medium text-gray-600 mb-1">📊 File Types Found:</div>
            <div className="flex flex-wrap gap-1">
              {Object.entries(zipContents.fileGroups).map(([type, files]) => (
                <span key={type} className="px-2 py-1 bg-white border rounded text-xs">
                  {type}: {files.length}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Directory Structure View */}
        {viewMode === 'structure' && directoryStructure && (
          <div className="mb-3 p-2 bg-blue-50 rounded border border-blue-200">
            <div className="font-medium text-blue-700 mb-2">📁 Directory Structure:</div>
            <div className="max-h-48 overflow-y-auto">
              <DirectoryTree node={directoryStructure} />
            </div>
            <div className="mt-2 text-xs text-blue-600">
              💡 Click "Select Files" to choose header and data files for processing
            </div>
          </div>
        )}

        {/* File Selection View */}
        {viewMode === 'selection' && (
          <div className="space-y-3">
            {/* Header File Selection */}
            <div className="p-3 bg-green-50 rounded border border-green-200">
              <div className="font-medium text-green-700 mb-2">
                📋 Header File Selection
                {suggestedFiles.header && (
                  <span className="ml-2 text-xs bg-green-200 px-2 py-1 rounded">💡 Suggested</span>
                )}
              </div>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {zipContents.files
                  .filter(file => 
                    file.name.toLowerCase().includes('header') ||
                    file.name.toLowerCase().includes('schema') ||
                    file.name.toLowerCase().includes('readme') ||
                    file.name.toLowerCase().endsWith('.csv') ||
                    file.name.toLowerCase().endsWith('.txt')
                  )
                  .map((file, idx) => (
                    <div
                      key={idx}
                      onClick={() => toggleFileSelection(file, 'header')}
                      className={`flex items-center space-x-2 p-2 rounded cursor-pointer border ${
                        selectedHeaderFile?.path === file.path
                          ? 'bg-green-100 border-green-300'
                          : 'bg-white border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      {getFileIcon(file.name)}
                      <span className="flex-1 truncate">{file.path}</span>
                      <span className="text-gray-400">({formatFileSize(file.size)})</span>
                      {suggestedFiles.header?.path === file.path && (
                        <span className="text-green-600 text-xs">💡</span>
                      )}
                    </div>
                  ))}
              </div>
            </div>

            {/* Data Files Selection */}
            <div className="p-3 bg-blue-50 rounded border border-blue-200">
              <div className="font-medium text-blue-700 mb-2">
                📊 Data Files Selection
                {suggestedFiles.data.length > 0 && (
                  <span className="ml-2 text-xs bg-blue-200 px-2 py-1 rounded">💡 Suggested</span>
                )}
              </div>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {zipContents.files
                  .filter(file => 
                    file.name.toLowerCase().includes('data') ||
                    file.name.toLowerCase().includes('records') ||
                    file.name.toLowerCase().endsWith('.csv') ||
                    file.name.toLowerCase().endsWith('.json') ||
                    file.name.toLowerCase().endsWith('.xml') ||
                    file.name.toLowerCase().endsWith('.gml')
                  )
                  .map((file, idx) => (
                    <div
                      key={idx}
                      onClick={() => toggleFileSelection(file, 'data')}
                      className={`flex items-center space-x-2 p-2 rounded cursor-pointer border ${
                        selectedDataFiles.some(f => f.path === file.path)
                          ? 'bg-blue-100 border-blue-300'
                          : 'bg-white border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      {getFileIcon(file.name)}
                      <span className="flex-1 truncate">{file.path}</span>
                      <span className="text-gray-400">({formatFileSize(file.size)})</span>
                      {suggestedFiles.data.some(f => f.path === file.path) && (
                        <span className="text-blue-600 text-xs">💡</span>
                      )}
                    </div>
                  ))}
              </div>
            </div>

            {/* Selection Summary */}
            <div className="p-2 bg-gray-50 rounded border">
              <div className="font-medium text-gray-700 mb-1">📋 Selection Summary:</div>
              <div className="space-y-1">
                <div className="text-gray-600">
                  <span className="font-medium">Header:</span> {selectedHeaderFile ? selectedHeaderFile.path : 'None selected'}
                </div>
                <div className="text-gray-600">
                  <span className="font-medium">Data Files:</span> {selectedDataFiles.length} selected
                  {selectedDataFiles.length > 0 && (
                    <div className="ml-4 text-xs text-gray-500">
                      {selectedDataFiles.map(f => f.path).join(', ')}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  // Process selected files
                  console.log('Processing ZIP with:', { selectedHeaderFile, selectedDataFiles });
                }}
                disabled={!selectedHeaderFile && selectedDataFiles.length === 0}
                className="px-3 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                🚀 Process Selected Files
              </button>
              <button
                onClick={() => setViewMode('structure')}
                className="px-3 py-1 bg-gray-600 text-white rounded text-xs hover:bg-gray-700"
              >
                ← Back to Structure
              </button>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Enhanced file preview component with mapping capabilities
  const FilePreview = ({ file, getAllConfigs }) => {
    const [stagingConfig, setStagingConfig] = useState(null);
    const [csvDelimiter, setCsvDelimiter] = useState(file.analysis?.preview?.detectedDelimiter || ',');
    const [csvPreview, setCsvPreview] = useState(null);
    const [showActionSuggestions, setShowActionSuggestions] = useState(false);
    const { saveConfig, getConfig } = useStagingConfig();
    
    console.log('FilePreview rendering for file:', file.name, 'analysis:', file.analysis);
    
    if (!file.analysis) {
      console.log('No analysis yet for:', file.name);
      return <div className="text-xs text-gray-500">Analyzing...</div>;
    }

    if (file.analysis.error) {
      console.log('Analysis error for:', file.name, 'error:', file.analysis.error);
      return <div className="text-xs text-red-500">Analysis failed: {file.analysis.error}</div>;
    }

    const { analysis } = file;
    console.log('Rendering analysis for:', file.name, 'type:', analysis.type);

    // CSV delimiter options
    const delimiterOptions = [
      { value: ',', label: 'Comma (,)' },
      { value: ';', label: 'Semicolon (;)' },
      { value: '\t', label: 'Tab' },
      { value: '|', label: 'Pipe (|)' },
      { value: ' ', label: 'Space' },
      { value: ':', label: 'Colon (:)' }
    ];

    // Function to parse CSV with custom delimiter
    const parseCSVWithDelimiter = (content, delimiter) => {
      const lines = content.split('\n');
      if (lines.length < 2) return { headers: [], data: [] };

      const parseLine = (line) => {
        const result = [];
        let current = '';
        let inQuotes = false;
        let quoteChar = null;
        
        for (let i = 0; i < line.length; i++) {
          const char = line[i];
          
          // Handle quote characters
          if ((char === '"' || char === "'") && !inQuotes) {
            inQuotes = true;
            quoteChar = char;
            continue;
          }
          
          if (char === quoteChar && inQuotes) {
            // Check for escaped quote
            if (i + 1 < line.length && line[i + 1] === quoteChar) {
              current += quoteChar;
              i++; // Skip next quote
            } else {
              inQuotes = false;
              quoteChar = null;
            }
            continue;
          }
          
          // Handle delimiter
          if (char === delimiter && !inQuotes) {
            result.push(current.trim());
            current = '';
            continue;
          }
          
          current += char;
        }
        
        // Add the last field
        result.push(current.trim());
        return result;
      };

      const headers = parseLine(lines[0]);
      const data = lines.slice(1, 11).map(line => parseLine(line)); // First 10 data rows
      
      return { headers, data, totalLines: lines.length };
    };

    // Update CSV preview when delimiter changes
    useEffect(() => {
      if (analysis.type === 'csv' && file.file) {
        try {
          const reader = new FileReader();
          reader.onload = (e) => {
            try {
              const content = e.target.result;
              const preview = parseCSVWithDelimiter(content, csvDelimiter);
              setCsvPreview(preview);
            } catch (error) {
              console.error('Error parsing CSV preview:', error);
              setCsvPreview({ headers: [], data: [], totalLines: 0, error: error.message });
            }
          };
          reader.onerror = (error) => {
            console.error('FileReader error in CSV preview:', error);
            setCsvPreview({ headers: [], data: [], totalLines: 0, error: 'Failed to read file' });
          };
          
          // Create a copy of the file to avoid conflicts
          const fileCopy = file.file.slice(0, Math.min(file.file.size, 1024 * 50)); // Read max 50KB
          reader.readAsText(fileCopy);
        } catch (error) {
          console.error('Error setting up CSV preview reader:', error);
          setCsvPreview({ headers: [], data: [], totalLines: 0, error: error.message });
        }
      }
    }, [csvDelimiter, analysis.type, file.file]);

    return (
      <div className="mt-3 p-3 bg-gray-50 rounded border">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            {FileAnalyzer.getFileIcon(analysis.type)}
            <span className="text-xs font-medium text-gray-700">
              {analysis.type.toUpperCase()} • {analysis.extension}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setSelectedFile(selectedFile?.id === file.id ? null : file)}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              {selectedFile?.id === file.id ? 'Hide' : 'Preview'}
            </button>
          </div>
        </div>

        {/* CSV Delimiter Selection */}
        {analysis.type === 'csv' && (
          <div className="mb-3 p-2 bg-white rounded border">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-xs font-medium text-gray-700">CSV Delimiter:</span>
              <select
                value={csvDelimiter}
                onChange={(e) => setCsvDelimiter(e.target.value)}
                className="text-xs border rounded px-2 py-1"
              >
                {delimiterOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <span className="text-xs text-gray-500">
                (Auto-detected: {analysis.preview?.detectedDelimiter || 'comma'})
              </span>
            </div>
            
            {/* Delimiter detection info */}
            <div className="text-xs text-gray-600">
              <div className="font-medium mb-1">Delimiter Detection:</div>
              <div className="space-y-1">
                <div>• Quoted fields are preserved regardless of delimiter</div>
                <div>• Spaces inside quotes are treated as part of the field</div>
                <div>• Common delimiters: comma, semicolon, tab, pipe</div>
              </div>
            </div>
          </div>
        )}

        {/* ZIP Contents - Enhanced Intelligent Analysis */}
        {analysis.type === 'zip' && analysis.zipContents && (
          <ZIPIntelligentAnalyzer 
            zipContents={analysis.zipContents} 
            directoryStructure={analysis.directoryStructure}
            file={file}
          />
        )}

        {/* GeoPackage Analysis */}
        {analysis.type === 'geopackage' && analysis.preview && (
          <div className="text-xs">
            <div className="font-medium text-gray-700 mb-1">GeoPackage Analysis:</div>
            <div className="space-y-1">
              <div className="text-gray-600">{analysis.preview.message}</div>
              <div className="text-gray-500">Size: {formatFileSize(analysis.preview.size)}</div>
              <div className="text-blue-600 font-medium">Requires backend processing for full analysis</div>
              <div className="text-gray-600">
                <div className="font-medium">Supported Operations:</div>
                <ul className="list-disc list-inside ml-2">
                  {analysis.preview.supportedOperations.map((op, idx) => (
                    <li key={idx}>{op}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Shapefile Analysis */}
        {analysis.type === 'shapefile' && analysis.preview && (
          <div className="text-xs">
            <div className="font-medium text-gray-700 mb-1">Shapefile Component:</div>
            <div className="space-y-1">
              <div className="text-gray-600">{analysis.preview.description}</div>
              <div className="text-gray-500">Component: {analysis.preview.component.toUpperCase()}</div>
              <div className="text-gray-500">Size: {formatFileSize(analysis.preview.size)}</div>
              {analysis.preview.requiresCompleteSet && (
                <div className="text-orange-600">
                  <div className="font-medium">Missing Components:</div>
                  <div className="ml-2">{analysis.preview.missingComponents.join(', ')}</div>
                </div>
              )}
              <div className="text-blue-600 font-medium">Requires backend processing for full analysis</div>
            </div>
          </div>
        )}

        {/* AI Analysis Results */}
        {analysis.aiAnalysis && !analysis.aiAnalysis.error && (
          <div className="mt-3 p-2 bg-blue-50 rounded border">
            <div className="flex items-center space-x-2 mb-2">
              <BarChart3 className="w-4 h-4 text-blue-600" />
              <span className="text-xs font-medium text-blue-700">AI Analysis</span>
              {analysis.aiAnalysis.confidence && (
                <span className="text-xs text-blue-600">
                  Confidence: {Math.round(analysis.aiAnalysis.confidence * 100)}%
                </span>
              )}
            </div>
            
            {/* Standards Compliance */}
            {analysis.aiAnalysis.standardsIdentification?.detectedStandards?.length > 0 && (
              <div className="mb-2">
                <div className="text-xs font-medium text-blue-600 mb-1">Detected Standards:</div>
                <div className="flex flex-wrap gap-1">
                  {analysis.aiAnalysis.standardsIdentification.detectedStandards.map((standard, idx) => (
                    <span key={idx} className="px-2 py-1 bg-blue-200 rounded text-xs text-blue-800">
                      {standard.name} ({Math.round(standard.score * 100)}%)
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {/* Data Patterns */}
            {analysis.aiAnalysis.contentAnalysis?.dataPatterns?.length > 0 && (
              <div className="mb-2">
                <div className="text-xs font-medium text-blue-600 mb-1">Detected Patterns:</div>
                <div className="space-y-1">
                  {analysis.aiAnalysis.contentAnalysis.dataPatterns.slice(0, 3).map((pattern, idx) => (
                    <div key={idx} className="text-xs text-blue-700">
                      <span className="font-medium">{pattern.header}:</span> {(pattern.detectedTypes || []).join(', ')}
                      {pattern.confidence > 0.8 && (
                        <span className="text-green-600 ml-1">✓ High confidence</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Recommendations */}
            {analysis.aiAnalysis.recommendations?.length > 0 && (
              <div className="mb-2">
                <div className="text-xs font-medium text-blue-600 mb-1">Recommendations:</div>
                <div className="space-y-1">
                  {analysis.aiAnalysis.recommendations.slice(0, 3).map((rec, idx) => (
                    <div key={idx} className="text-xs text-blue-700 flex items-start">
                      <span className="text-blue-500 mr-1">•</span>
                      {rec}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Mapping Suggestions */}
            {analysis.aiAnalysis.mappingSuggestions?.columnMappings?.length > 0 && (
              <div className="mb-2">
                <div className="text-xs font-medium text-blue-600 mb-1">Suggested Mappings:</div>
                <div className="space-y-1">
                  {analysis.aiAnalysis.mappingSuggestions.columnMappings.slice(0, 3).map((mapping, idx) => (
                    <div key={idx} className="text-xs text-blue-700">
                      <span className="font-medium">{mapping.sourceColumn}</span> → {mapping.targetColumn}
                      {mapping.dataType && (
                        <span className="text-gray-500 ml-1">({mapping.dataType})</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* AI Analysis Error */}
        {analysis.aiAnalysis?.error && (
          <div className="mt-3 p-2 bg-red-50 rounded border">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-red-600" />
              <span className="text-xs font-medium text-red-700">AI Analysis Failed</span>
            </div>
            <div className="text-xs text-red-600 mt-1">{analysis.aiAnalysis.error}</div>
          </div>
        )}

        {/* Action Suggestions */}
        {analysis.preview?.headers && analysis.preview.headers.length > 0 && (
          <div className="mt-3">
            {showActionSuggestions ? (
              <UploadActionSuggestions
                file={file.file}
                headers={analysis.preview.headers}
                onAction={(action) => {
                  console.log('Action selected:', action);
                  if (action === 'proceed_upload') {
                    // Proceed with upload
                    startIngestion(file.id);
                  }
                }}
                onClose={() => setShowActionSuggestions(false)}
                onUseExistingConfig={(configId) => {
                  // Load existing config
                  console.log('Loading config:', configId);
                  setShowActionSuggestions(false);
                }}
              />
            ) : (
              <button
                onClick={() => setShowActionSuggestions(true)}
                className="w-full p-3 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors text-left"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Info className="w-4 h-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-800">Get Action Suggestions</span>
                  </div>
                  <span className="text-xs text-blue-600">Click to see recommendations</span>
                </div>
                <p className="text-xs text-blue-600 mt-1">
                  Based on your file analysis, get suggestions for saving configs, using existing ones, or proceeding with upload
                </p>
              </button>
            )}
          </div>
        )}



        {/* File Preview */}
        {selectedFile?.id === file.id && (
          <div className="mt-3 p-2 bg-white rounded border text-xs">
            {analysis.preview?.type === 'csv' && csvPreview && (
              <CSVTablePreview preview={csvPreview} delimiter={csvDelimiter} />
            )}

            {analysis.preview?.type === 'json' && (
              <div>
                <div className="font-medium mb-1">
                  {analysis.preview.isArray ? 'Array' : 'Object'} ({analysis.preview.totalItems} items)
                </div>
                <pre className="max-h-32 overflow-y-auto text-gray-600 font-mono text-xs">
                  {JSON.stringify(analysis.preview.data, null, 2)}
                </pre>
              </div>
            )}

            {analysis.preview?.type === 'xml' && (
              <div>
                <div className="font-medium mb-1">Root: {analysis.preview.rootElement}</div>
                <div className="font-medium mb-1">Children ({analysis.preview.totalChildren}):</div>
                <div className="max-h-32 overflow-y-auto">
                  {analysis.preview.children.map((child, idx) => (
                    <div key={idx} className="text-gray-600">
                      <span className="font-medium">{child.tagName}</span>
                      {child.attributes.length > 0 && (
                        <span className="text-gray-400">
                          {' '}({(child.attributes || []).map(attr => `${attr.name}="${attr.value}"`).join(', ')})
                        </span>
                      )}
                      <span className="ml-2 text-gray-400">{child.textContent}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {analysis.preview?.type === 'yaml' && (
              <div>
                <div className="font-medium mb-1">Preview ({analysis.preview.previewLines}/{analysis.preview.totalLines} lines):</div>
                <pre className="max-h-32 overflow-y-auto text-gray-600 font-mono text-xs">
                  {(analysis.preview.lines || []).join('\n')}
                </pre>
              </div>
            )}

            {analysis.preview?.type === 'text' && (
              <div>
                <div className="font-medium mb-1">Preview ({analysis.preview.previewLines}/{analysis.preview.totalLines} lines):</div>
                <pre className="max-h-32 overflow-y-auto text-gray-600 font-mono text-xs">
                  {(analysis.preview.lines || []).join('\n')}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  // CSV Table Preview Component
  const CSVTablePreview = ({ preview, delimiter }) => {
    const getDelimiterDisplay = (delim) => {
      switch (delim) {
        case '\t': return 'Tab';
        case ' ': return 'Space';
        default: return delim;
      }
    };

    return (
      <div>
        <div className="font-medium mb-2">
          CSV Preview (Delimiter: {getDelimiterDisplay(delimiter)}) • {preview.data.length} rows
        </div>
        <div className="overflow-x-auto max-h-64">
          <table className="min-w-full text-xs border border-gray-300">
            <thead className="bg-gray-100">
              <tr>
                {preview.headers.map((header, idx) => (
                  <th key={idx} className="border border-gray-300 px-2 py-1 text-left font-medium">
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {preview.data.map((row, rowIdx) => (
                <tr key={rowIdx} className="hover:bg-gray-50">
                  {row.map((cell, cellIdx) => (
                    <td key={cellIdx} className="border border-gray-300 px-2 py-1 text-gray-700">
                      <div className="max-w-xs truncate" title={cell}>
                        {cell || ''}
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="text-xs text-gray-500 mt-1">
          Total lines: {preview.totalLines} • Showing first {preview.data.length} data rows
        </div>
      </div>
    );
  };



    // Calculate similarity score between current file and a saved config
    const calculateSimilarityScore = (currentHeaders, savedConfig) => {
      if (!savedConfig.mappings || !currentHeaders) return 0;
      
      const savedHeaders = savedConfig.mappings.map(m => m.sourceColumn);
      const currentSet = new Set(currentHeaders.map(h => h.toLowerCase()));
      const savedSet = new Set(savedHeaders.map(h => h.toLowerCase()));
      
      // Calculate intersection
      const intersection = new Set([...currentSet].filter(x => savedSet.has(x)));
      const union = new Set([...currentSet, ...savedSet]);
      
      // Jaccard similarity
      const jaccardSimilarity = intersection.size / union.size;
      
      // Additional scoring based on exact matches
      const exactMatches = currentHeaders.filter(h => 
        savedHeaders.some(sh => sh.toLowerCase() === h.toLowerCase())
      ).length;
      
      const exactMatchScore = exactMatches / Math.max(currentHeaders.length, savedHeaders.length);
      
      // Weighted score (favor exact matches)
      return (jaccardSimilarity * 0.4) + (exactMatchScore * 0.6);
    };

    

    

    

   







  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Data Upload</h1>
          <p className="mt-1 text-sm text-gray-500">
            Upload and ingest geospatial datasets
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowConfigManager(!showConfigManager)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <MapPin className="w-4 h-4 mr-2" />
            Config Manager
          </button>
          <button
            onClick={fetchUploadHistory}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
          <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </button>
        </div>
      </div>

      {/* Configuration Manager */}
      {showConfigManager && <StagingConfigManager />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <div className="space-y-6">
          {/* File Upload */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Upload Files</h2>
            
            {/* Drag & Drop Area */}
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive 
                  ? 'border-blue-400 bg-blue-50' 
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <UploadIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <div className="text-sm text-gray-600 mb-4">
                <label className="cursor-pointer">
                  <span className="font-medium text-blue-600 hover:text-blue-500">
                    Click to upload
                  </span>
                  <span className="text-gray-500"> or drag and drop</span>
                  <input
                    type="file"
                    multiple
                    onChange={handleFileSelect}
                    className="hidden"
                    accept=".csv,.txt,.gml,.xml,.zip,.gpkg,.shp,.dbf,.shx,.prj,.cpg,.qix,.sdmx,.kml,.geojson,.json,.yml,.yaml"
                  />
                </label>
              </div>
              <p className="text-xs text-gray-500">
                CSV, TXT, GML, XML, ZIP, GeoPackage, Shapefile, SDMX, KML, GeoJSON, JSON, YAML files up to 10GB
              </p>
            </div>
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Upload Queue
                {analyzing && <span className="ml-2 text-sm text-blue-600">(Analyzing files...)</span>}
              </h3>
              <div className="space-y-4">
                {files.map((file) => (
                  <div key={file.id} className="border border-gray-200 rounded-lg overflow-hidden">
                    <div className="flex items-center justify-between p-3 bg-gray-50">
                      <div className="flex items-center space-x-3 flex-1">
                        {file.analysis ? FileAnalyzer.getFileIcon(file.analysis.type) : <FileText className="w-5 h-5 text-gray-400" />}
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {file.name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {formatFileSize(file.size)}
                            {file.analysis && ` • ${file.analysis.type.toUpperCase()}`}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {file.status === 'pending' && (
                          <button
                            onClick={() => startIngestion(file.id)}
                            disabled={uploading || !file.file}
                            className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                          >
                            Start
                          </button>
                        )}
                        {file.status === 'uploading' && (
                          <div className="text-xs text-blue-600">
                            {uploadProgress[file.id] || 0}%
                          </div>
                        )}
                        <button
                          onClick={() => removeFile(file.id)}
                          className="p-1 text-gray-400 hover:text-red-600"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    
                    {/* File Analysis and Preview */}
                    <FilePreview file={file} getAllConfigs={getAllConfigs} />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Upload History */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mt-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
          Upload History
          {user && (user.role === 'admin' || user.role === 'power_user') && (
            <button
              className="ml-4 px-2 py-1 text-xs bg-gray-200 rounded"
              onClick={() => setShowAllHistory(v => !v)}
            >
              {showAllHistory ? 'Show My Uploads' : 'Show All Uploads'}
            </button>
          )}
        </h3>
        {/* Debug info */}
        <div className="text-xs text-gray-500 mb-2">
          Debug: {uploadHistory.length} uploads found, Loading: {historyLoading ? 'Yes' : 'No'}
        </div>
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            placeholder="Dataset/Table"
            value={historyFilters.table_name}
            onChange={e => setHistoryFilters(f => ({ ...f, table_name: e.target.value }))}
            className="border px-2 py-1 rounded text-xs"
          />
          <input
            type="text"
            placeholder="Filename"
            value={historyFilters.filename}
            onChange={e => setHistoryFilters(f => ({ ...f, filename: e.target.value }))}
            className="border px-2 py-1 rounded text-xs"
          />
          <input
            type="date"
            value={historyFilters.start_date}
            onChange={e => setHistoryFilters(f => ({ ...f, start_date: e.target.value }))}
            className="border px-2 py-1 rounded text-xs"
          />
          <input
            type="date"
            value={historyFilters.end_date}
            onChange={e => setHistoryFilters(f => ({ ...f, end_date: e.target.value }))}
            className="border px-2 py-1 rounded text-xs"
          />
          <button
            className="px-2 py-1 text-xs bg-blue-600 text-white rounded"
            onClick={fetchUploadHistory}
            disabled={historyLoading}
          >
            Filter
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="table-auto w-full text-xs">
            <thead>
              <tr>
                <th className="border px-2 py-1">Table</th>
                <th className="border px-2 py-1">Filename</th>
                <th className="border px-2 py-1">User</th>
                <th className="border px-2 py-1">Status</th>
                <th className="border px-2 py-1">Timestamp</th>
                <th className="border px-2 py-1">Actions</th>
              </tr>
            </thead>
            <tbody>
              {uploadHistory.map((item, idx) => (
                <tr key={idx}>
                  <td className="border px-2 py-1">{item.staging_table}</td>
                  <td className="border px-2 py-1">{item.filename || ''}</td>
                  <td className="border px-2 py-1">{item.uploaded_by}</td>
                  <td className="border px-2 py-1">{item.status}</td>
                  <td className="border px-2 py-1">{new Date(item.upload_timestamp).toLocaleString()}</td>
                  <td className="border px-2 py-1">
                    {item.status === 'error' && (
                      <button
                        className="px-2 py-1 text-xs bg-yellow-500 text-white rounded"
                        onClick={() => retryUpload(item)}
                      >
                        Retry
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {historyLoading && <div className="text-xs text-gray-500 mt-2">Loading...</div>}
          {!historyLoading && uploadHistory.length === 0 && (
            <div className="text-xs text-gray-500 mt-2">No upload history found</div>
          )}
        </div>
      </div>
    </div>
  );
}