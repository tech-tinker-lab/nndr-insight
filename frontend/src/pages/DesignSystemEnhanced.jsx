import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import FileAnalysisSection from '../components/FileAnalysisSection';
import ClientSideFileAnalysis from '../components/ClientSideFileAnalysis';
import DataPreviewSection from '../components/DataPreviewSection';
import FieldAnalysisSection from '../components/FieldAnalysisSection';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Box,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Snackbar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Tooltip,
  Fab,
  Zoom,
  Fade,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  DeleteOutline as DeleteOutlineIcon,
  Visibility as ViewIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  ArrowForward as ArrowForwardIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Code as CodeIcon,
  Schema as SchemaIcon,
  Storage as StorageIcon,
  DataObject as DataIcon,
  Security as SecurityIcon,
  IntegrationInstructions as IntegrationIcon,
  TableChart as TableIcon,
  ViewColumn as FieldIcon,
  CloudUpload as CloudUploadIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  ExpandMore as ExpandMoreIcon,
  List as ListIcon,
  ViewList as ViewListIcon,
  Create as CreateIcon,
  Build as BuildIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';

const DatasetStructures = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [severity, setSeverity] = useState('info');
  
  // Dataset Types
  const [datasetTypes, setDatasetTypes] = useState([]);
  const [selectedType, setSelectedType] = useState(null);
  
  // Dataset Structures
  const [datasetStructures, setDatasetStructures] = useState([]);
  const [selectedStructure, setSelectedStructure] = useState(null);
  
  // Table Templates
  const [tableTemplates, setTableTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  
  // Generated Tables
  const [generatedTables, setGeneratedTables] = useState([]);
  
  // Field Mappings
  const [fieldMappings, setFieldMappings] = useState([]);
  
  // Dataset Uploads
  const [datasetUploads, setDatasetUploads] = useState([]);
  
  // Reviews
  const [reviews, setReviews] = useState([]);
  
  // Dialogs
  const [structureDialog, setStructureDialog] = useState(false);
  const [fieldDialog, setFieldDialog] = useState(false);
  const [templateDialog, setTemplateDialog] = useState(false);
  const [tableDialog, setTableDialog] = useState(false);
  const [mappingDialog, setMappingDialog] = useState(false);
  const [uploadDialog, setUploadDialog] = useState(false);
  const [reviewDialog, setReviewDialog] = useState(false);
  const [tableStructureDialog, setTableStructureDialog] = useState(false);
  
  // Stepper and AI Analysis
  const [activeStep, setActiveStep] = useState(0);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [generatedMappings, setGeneratedMappings] = useState(null);
  const [useClientSideAnalysis, setUseClientSideAnalysis] = useState(true);
  
  // Table Structure View
  const [structureFields, setStructureFields] = useState([]);
  const [selectedStructureForView, setSelectedStructureForView] = useState(null);
  
  // Delete Confirmation
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [structureToDelete, setStructureToDelete] = useState(null);
  

  
  // Form States
  const [newStructure, setNewStructure] = useState({
    name: '',
    description: '',
    source_type: '',
    category: '',
    version: '1.0',
    data_type: 'file', // Add data type field
    target_schema_type: 'staging' // Add target schema type field
  });
  
  // Edit mode state
  const [isEditMode, setIsEditMode] = useState(false);
  const [editingStructure, setEditingStructure] = useState(null);
  
  const [newField, setNewField] = useState({
    name: '',
    display_name: '',
    data_type: '',
    postgis_type: '',
    is_required: false,
    is_primary_key: false,
    default_value: '',
    constraints: '',
    description: ''
  });
  
  const [newTemplate, setNewTemplate] = useState({
    name: '',
    description: '',
    template_type: '',
    structure_id: null,
    template_sql: ''
  });

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    try {
      setLoading(true);
      const [
        typesResponse,
        structuresResponse,
        templatesResponse
      ] = await Promise.all([
        api.get('/api/dataset-structures/types'),
        api.get('/api/dataset-structures/structures'),
        api.get('/api/dataset-structures/templates')
      ]);

      setDatasetTypes(typesResponse.data.types || []);
      setDatasetStructures(structuresResponse.data.structures || []);
      setTableTemplates(templatesResponse.data.templates || []);
      setGeneratedTables([]); // Not implemented yet
      setFieldMappings([]); // Not implemented yet
      setDatasetUploads([]); // Not implemented yet
      setReviews([]); // Not implemented yet
    } catch (error) {
      showMessage('Error loading data: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadStructureFields = async (structureId) => {
    try {
      setLoading(true);
      const response = await api.get(`/api/design-enhanced/structures/${structureId}/fields`);
      setStructureFields(response.data.fields || []);
    } catch (error) {
      showMessage('Error loading structure fields: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleViewTableStructure = async (structure) => {
    setSelectedStructureForView(structure);
    await loadStructureFields(structure.structure_id);
    setTableStructureDialog(true);
  };

  const autoPopulateFromAnalysis = (analysisData) => {
    if (!analysisData) return;
    
    const updatedStructure = { ...newStructure };
    
    // Auto-populate name from filename
    if (analysisData.filename && !updatedStructure.name) {
      const cleanName = analysisData.filename.replace(/\.[^/.]+$/, "").replace(/[^a-zA-Z0-9\s]/g, " ").trim();
      updatedStructure.name = cleanName;
    }
    
    // Auto-populate source type from detected format
    if (analysisData.format && !updatedStructure.source_type) {
      updatedStructure.source_type = analysisData.format.toLowerCase();
    }
    
    // Auto-populate category from governing body
    if (analysisData.primary_governing_body && !updatedStructure.category) {
      updatedStructure.category = analysisData.primary_governing_body;
    }
    
    // Auto-populate description from analysis
    if (analysisData.identified_standards && analysisData.identified_standards.length > 0 && !updatedStructure.description) {
      const standards = analysisData.identified_standards.map(s => s.name).join(", ");
      updatedStructure.description = `AI-detected standards: ${standards}. ${analysisData.field_count || 0} fields identified.`;
    }
    
    setNewStructure(updatedStructure);
  };

  const handleDeleteStructure = async (structure) => {
    setStructureToDelete(structure);
    setDeleteDialog(true);
  };

  const handleDeleteType = async (type) => {
    if (!type) return;
    
    try {
      setLoading(true);
      await api.delete(`/api/dataset-structures/types/${type.type_id}`);
      
      // Remove from local state
      setDatasetTypes(prev => 
        prev.filter(t => t.type_id !== type.type_id)
      );
      
      showMessage('Dataset type deleted successfully', 'success');
    } catch (error) {
      showMessage('Error deleting dataset type: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const confirmDeleteStructure = async () => {
    if (!structureToDelete) return;
    
    try {
      setLoading(true);
      await api.delete(`/api/design-enhanced/structures/${structureToDelete.structure_id}`);
      
      showMessage(`Dataset structure '${structureToDelete.dataset_name}' deleted successfully`, 'success');
      
      // Refresh the structures list
      await loadAllData();
      
      // Close dialogs
      setDeleteDialog(false);
      setStructureToDelete(null);
    } catch (error) {
      showMessage('Error deleting structure: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateStructure = async () => {
    try {
      setLoading(true);
      const structureData = {
        dataset_name: newStructure.name,
        description: newStructure.description,
        source_type: newStructure.data_type, // Use data_type instead of source_type for database
        file_formats: [newStructure.source_type],
        governing_body: newStructure.category,
        target_schema_type: newStructure.target_schema_type,
        data_standards: aiAnalysis?.identified_standards?.map(s => s.standard_id) || [],
        tags: [newStructure.category]
      };
      
      let response;
      let structureId;
      
      if (isEditMode && editingStructure) {
        // Update existing structure
        response = await api.put(`/api/design-enhanced/structures/${editingStructure.structure_id}`, structureData);
        structureId = editingStructure.structure_id;
        showMessage('Dataset structure updated successfully!', 'success');
      } else {
        // Create new structure
        response = await api.post('/api/dataset-structures/structures', structureData);
        structureId = response.data.structure_id;
        showMessage('Dataset structure created successfully!', 'success');
      }
      
      // Create field definitions from the mappings configured in Step 2
      if (structureId && generatedMappings?.field_mappings && generatedMappings.field_mappings.length > 0) {
        try {
          console.log('Debug: Creating fields from stepper mappings, count:', generatedMappings.field_mappings.length);
          await createFieldsFromMappings(structureId, generatedMappings);
          showMessage(`Created ${generatedMappings.field_mappings.length} field definitions!`, 'success');
        } catch (fieldError) {
          console.error('Error creating fields:', fieldError);
          showMessage('Structure created but field creation failed: ' + fieldError.message, 'warning');
        }
      } else if (structureId && aiAnalysis?.field_analysis && aiAnalysis.field_analysis.length > 0) {
        // Fallback: Create fields directly from analysis if no mappings
        try {
          console.log('Debug: Creating fields from analysis, count:', aiAnalysis.field_analysis.length);
          await processFieldMappings(structureId, aiAnalysis.field_analysis);
          showMessage(`Created ${aiAnalysis.field_analysis.length} field definitions from analysis!`, 'success');
        } catch (fieldError) {
          console.error('Error creating fields from analysis:', fieldError);
          showMessage('Structure created but field creation failed: ' + fieldError.message, 'warning');
        }
      }
      
      // Reload structures to get the updated list
      const structuresResponse = await api.get('/api/design-enhanced/structures');
      setDatasetStructures(structuresResponse.data.structures || []);
      
      // Reset form and close dialog
      setNewStructure({
        name: '',
        description: '',
        source_type: '',
        category: '',
        version: '1.0',
        data_type: 'file',
        target_schema_type: 'staging'
      });
      setIsEditMode(false);
      setEditingStructure(null);
      setActiveStep(0);
      setAiAnalysis(null);
      setGeneratedMappings(null);
      setStructureDialog(false);
    } catch (error) {
      showMessage('Error creating structure: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };



  const processFieldMappings = async (structureId, fieldAnalysis) => {
    for (let i = 0; i < fieldAnalysis.length; i++) {
      const field = fieldAnalysis[i];
      console.log(`Debug: Processing field ${i + 1}:`, field);
      
      // Determine field type and PostGIS type
      let fieldType = field.type || 'text';
      let postgisType = null; // Only set for actual geometry fields
      
      switch (fieldType.toLowerCase()) {
        case 'integer':
        case 'number':
          fieldType = 'integer';
          break;
        case 'decimal':
        case 'float':
          fieldType = 'numeric';
          break;
        case 'date':
          fieldType = 'date';
          break;
        case 'timestamp':
          fieldType = 'timestamp';
          break;
        case 'boolean':
          fieldType = 'boolean';
          break;
        case 'geometry':
          fieldType = 'geometry';
          postgisType = 'POINT'; // Only set PostGIS type for geometry fields
          break;
        default:
          fieldType = 'text';
      }
      
      const fieldData = {
        field_name: field.field_name || `field_${i + 1}`,
        display_name: field.field_name || `Field ${i + 1}`,
        field_type: fieldType,
        postgis_type: postgisType, // Will be null for non-geometry fields
        is_required: false,
        is_primary_key: i === 0, // First field as primary key
        default_value: '',
        constraints: '',
        description: field.description || `Auto-generated from AI analysis`,
        sequence_order: i + 1
      };
      
      console.log(`Debug: Creating field with data:`, fieldData);
      
      try {
        const response = await api.post(`/api/dataset-structures/structures/${structureId}/fields`, fieldData);
        console.log(`Debug: Field ${i + 1} created successfully:`, response.data);
      } catch (error) {
        console.error(`Debug: Error creating field ${i + 1}:`, error);
        throw error;
      }
    }
  };



  const createFieldsFromMappings = async (structureId, mappings) => {
    const fieldMappings = mappings.field_mappings || [];
    
    for (let i = 0; i < fieldMappings.length; i++) {
      const mapping = fieldMappings[i];
      
      // Map custom field types to valid database field types
      let fieldType = mapping.data_type || 'text';
      let postgisType = null;
      
      // Map custom field types to valid database types
      switch (fieldType) {
        case 'postcode':
        case 'uprn':
        case 'usrn':
        case 'coordinate':
        case 'longitude':
        case 'latitude':
          fieldType = 'text'; // Store as text to preserve formatting
          break;
        case 'geometry':
          fieldType = 'geometry';
          postgisType = mapping.postgis_type || 'POINT';
          break;
        case 'geography':
          fieldType = 'geography';
          postgisType = mapping.postgis_type || 'POINT';
          break;
        case 'integer':
        case 'number':
          fieldType = 'integer';
          break;
        case 'decimal':
        case 'float':
        case 'numeric':
          fieldType = 'numeric';
          break;
        case 'date':
          fieldType = 'date';
          break;
        case 'timestamp':
          fieldType = 'timestamp';
          break;
        case 'boolean':
          fieldType = 'boolean';
          break;
        case 'varchar':
          fieldType = 'varchar';
          break;
        case 'bigint':
          fieldType = 'bigint';
          break;
        case 'jsonb':
          fieldType = 'jsonb';
          break;
        case 'box2d':
        case 'box3d':
        case 'raster':
          // These are PostGIS types that don't need separate postgis_type
          fieldType = fieldType;
          break;
        default:
          fieldType = 'text'; // Default to text for unknown types
      }
      
      const fieldData = {
        field_name: mapping.source_field || mapping.staging_field,
        display_name: mapping.source_field || mapping.staging_field,
        field_type: fieldType,
        postgis_type: postgisType,
        is_required: mapping.is_required || false,
        is_primary_key: mapping.is_primary_key || false,
        default_value: mapping.default_value || '',
        constraints: mapping.constraints || '',
        description: mapping.description || `Auto-generated from AI mapping: ${mapping.source_field || mapping.staging_field}`,
        sequence_order: mapping.sequence_order || i + 1
      };
      
                await api.post(`/api/dataset-structures/structures/${structureId}/fields`, fieldData);
    }
  };

  const handleCreateField = async () => {
    try {
      setLoading(true);
      const fieldData = {
        field_name: newField.name,
        display_name: newField.display_name,
        field_type: newField.data_type,
        postgis_type: newField.postgis_type,
        is_required: newField.is_required,
        is_primary_key: newField.is_primary_key,
        default_value: newField.default_value,
        constraints: newField.constraints,
        description: newField.description
      };
      
              const response = await api.post(`/api/dataset-structures/structures/${selectedStructure.structure_id}/fields`, fieldData);
      
      setFieldDialog(false);
      setNewField({ name: '', display_name: '', data_type: '', postgis_type: '', is_required: false, is_primary_key: false, default_value: '', constraints: '', description: '' });
      showMessage('Field added successfully', 'success');
    } catch (error) {
      showMessage('Error adding field: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTemplate = async () => {
    try {
      setLoading(true);
      const templateData = {
        template_name: newTemplate.name,
        description: newTemplate.description,
        template_type: newTemplate.template_type,
        structure_id: newTemplate.structure_id,
        table_name_pattern: `{dataset_name}_${newTemplate.template_type}`,
        schema_name: 'public',
        include_audit_fields: true,
        include_source_tracking: true,
        include_processing_metadata: true,
        postgis_enabled: true
      };
      
      const response = await api.post('/api/dataset-structures/templates', templateData);
      
      // Reload templates to get the updated list
      const templatesResponse = await api.get('/api/design-enhanced/templates');
      setTableTemplates(templatesResponse.data.templates || []);
      
      setTemplateDialog(false);
      setNewTemplate({ name: '', description: '', template_type: '', structure_id: null, template_sql: '' });
      showMessage('Table template created successfully', 'success');
    } catch (error) {
      showMessage('Error creating template: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateTable = async (templateId) => {
    try {
      setLoading(true);
      const generationData = {
        table_name: `generated_table_${Date.now()}`,
        schema_name: 'public'
      };
      
              const response = await api.post(`/api/dataset-structures/templates/${templateId}/generate`, generationData);
      showMessage('Table generated successfully', 'success');
    } catch (error) {
      showMessage('Error generating table: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Generate SQL preview for the structure
  const generateSQLPreview = () => {
    if (!aiAnalysis || !newStructure.name) return '';

    const tableName = newStructure.name.toLowerCase().replace(/[^a-z0-9]/g, '_');
    const fields = aiAnalysis.field_analysis || [];
    const schemaType = newStructure.target_schema_type || 'staging';
    
    let sql = `-- Generated SQL for ${newStructure.name}\n`;
    sql += `-- Data Type: ${newStructure.data_type}\n`;
    sql += `-- Source Type: ${newStructure.source_type}\n`;
    sql += `-- Target Schema: ${schemaType}\n\n`;
    
    sql += `CREATE TABLE ${schemaType}.${tableName}_${schemaType} (\n`;
    
    // Add standard staging fields
    sql += `    id SERIAL PRIMARY KEY,\n`;
    sql += `    batch_id VARCHAR(50),\n`;
    sql += `    source_name VARCHAR(100),\n`;
    sql += `    session_id VARCHAR(50),\n`;
    sql += `    source_file TEXT,\n`;
    sql += `    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n`;
    
    // Add detected fields
    fields.forEach((field, index) => {
      const fieldName = field.field_name || `field_${index + 1}`;
      let postgresType = 'TEXT';
      
      switch (field.type) {
        case 'integer':
          postgresType = 'INTEGER';
          break;
        case 'decimal':
          postgresType = 'NUMERIC';
          break;
        case 'date':
          postgresType = 'DATE';
          break;
        case 'boolean':
          postgresType = 'BOOLEAN';
          break;
        case 'coordinate':
          postgresType = 'NUMERIC(10, 8)';
          break;
        default:
          postgresType = 'TEXT';
      }
      
      sql += `    ${fieldName} ${postgresType},\n`;
    });
    
    sql += `    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n`;
    sql += `);\n\n`;
    
    // Add indexes
    sql += `-- Indexes\n`;
    sql += `CREATE INDEX idx_${tableName}_${schemaType}_batch_id ON ${schemaType}.${tableName}_${schemaType}(batch_id);\n`;
    sql += `CREATE INDEX idx_${tableName}_${schemaType}_source_name ON ${schemaType}.${tableName}_${schemaType}(source_name);\n`;
    sql += `CREATE INDEX idx_${tableName}_${schemaType}_session_id ON ${schemaType}.${tableName}_${schemaType}(session_id);\n`;
    
    // Add spatial index if coordinates are present
    const hasCoordinates = fields.some(f => f.type === 'coordinate');
    if (hasCoordinates) {
      sql += `CREATE INDEX idx_${tableName}_${schemaType}_geom ON ${schemaType}.${tableName}_${schemaType} USING GIST(geometry);\n`;
    }
    
    return sql;
  };

  const showMessage = (msg, sev = 'info') => {
    setMessage(msg);
    setSeverity(sev);
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'draft': return 'warning';
      case 'inactive': return 'error';
      case 'pending': return 'info';
      case 'approved': return 'success';
      case 'rejected': return 'error';
      default: return 'default';
    }
  };

  const renderDatasetTypes = () => (
    <div>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">
          Dataset Types
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setStructureDialog(true)}
        >
          Create Dataset Type
        </Button>
      </Box>

      <Grid container spacing={3}>
        {datasetTypes.map((type) => (
          <Grid item xs={12} md={6} lg={4} key={type.type_id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                  <Typography variant="h6" gutterBottom>
                    {type.display_name}
                  </Typography>
                  <Chip 
                    label={type.category} 
                    color="primary"
                    size="small"
                  />
                </Box>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  {type.description}
                </Typography>
                <Typography variant="caption" display="block">
                  Type: {type.type_name} | Governing Body: {type.governing_body}
                </Typography>
                <Typography variant="caption" display="block">
                  Required Fields: {type.required_fields?.length || 0} | Optional Fields: {type.optional_fields?.length || 0}
                </Typography>
                <Typography variant="caption" display="block">
                  Created: {new Date(type.created_at).toLocaleDateString()}
                </Typography>
                <Box mt={2} display="flex" justifyContent="space-between" alignItems="center">
                  <Button
                    size="small"
                    startIcon={<ViewIcon />}
                    onClick={() => setSelectedType(type)}
                  >
                    View Details
                  </Button>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => handleDeleteType(type)}
                  >
                    <DeleteOutlineIcon />
                  </IconButton>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </div>
  );

  const renderDatasetStructures = () => (
    <div className="space-y-6">
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h4" gutterBottom>
          <StorageIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Dataset Structures
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setStructureDialog(true)}
        >
          Create Structure
        </Button>
      </Box>

      <Grid container spacing={3}>
        {datasetStructures.map((structure) => (
          <Grid item xs={12} md={6} lg={4} key={structure.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                  <Typography variant="h6" gutterBottom>
                    {structure.dataset_name}
                  </Typography>
                  <Chip 
                    label={structure.status || 'draft'} 
                    color={getStatusColor(structure.status || 'draft')}
                    size="small"
                  />
                </Box>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  {structure.description}
                </Typography>
                <Typography variant="caption" display="block">
                  Source: {structure.source_type} | Category: {structure.governing_body}
                </Typography>
                <Typography variant="caption" display="block">
                  Created: {new Date(structure.created_at).toLocaleDateString()}
                </Typography>
                <Box mt={2} display="flex" justifyContent="space-between" alignItems="center">
                  <Button
                    size="small"
                    startIcon={<TableIcon />}
                    onClick={() => handleViewTableStructure(structure)}
                  >
                    View Structure
                  </Button>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => handleDeleteStructure(structure)}
                  >
                    <DeleteOutlineIcon />
                  </IconButton>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </div>
  );

  const renderTableTemplates = () => (
    <div className="space-y-6">
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h4" gutterBottom>
          <SchemaIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Table Templates
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setTemplateDialog(true)}
        >
          Create Template
        </Button>
      </Box>

      <Grid container spacing={3}>
        {tableTemplates.map((template) => (
          <Grid item xs={12} md={6} lg={4} key={template.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                  <Typography variant="h6" gutterBottom>
                    {template.template_name}
                  </Typography>
                  <Chip 
                    label={template.template_type} 
                    color="primary"
                    size="small"
                  />
                </Box>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  {template.description}
                </Typography>
                <Typography variant="caption" display="block">
                  Structure: {template.structure_id || 'N/A'}
                </Typography>
                <Box mt={2}>
                  <Button
                    size="small"
                    startIcon={<BuildIcon />}
                    onClick={() => handleGenerateTable(template.id)}
                  >
                    Generate Table
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </div>
  );

  const renderRecentUploads = () => (
    <div className="space-y-6">
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h4" gutterBottom>
          <CloudUploadIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Recent Uploads
        </Typography>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>File Name</TableCell>
              <TableCell>Dataset Structure</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Records</TableCell>
              <TableCell>Uploaded</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {datasetUploads.map((upload) => (
              <TableRow key={upload.id}>
                <TableCell>{upload.file_name}</TableCell>
                <TableCell>{upload.structure_name}</TableCell>
                <TableCell>
                  <Chip 
                    label={upload.status} 
                    color={getStatusColor(upload.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{upload.record_count || 0}</TableCell>
                <TableCell>{new Date(upload.uploaded_at).toLocaleDateString()}</TableCell>
                <TableCell>
                  <IconButton size="small">
                    <ViewIcon />
                  </IconButton>
                  <IconButton size="small">
                    <AssessmentIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );

  return (
    <Container maxWidth="xl">
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Dataset Types" icon={<DataIcon />} />
          <Tab label="Dataset Structures" icon={<StorageIcon />} />
          <Tab label="Table Templates" icon={<SchemaIcon />} />
          <Tab label="Recent Uploads" icon={<CloudUploadIcon />} />
        </Tabs>
      </Box>

      {activeTab === 0 && renderDatasetTypes()}
      {activeTab === 1 && renderDatasetStructures()}
      {activeTab === 2 && renderTableTemplates()}
      {activeTab === 3 && renderRecentUploads()}

      {/* Create Structure Dialog */}
      <Dialog 
        open={structureDialog} 
        onClose={() => {
          setStructureDialog(false);
          // Reset form state
          setNewStructure({
            name: '',
            description: '',
            source_type: '',
            category: '',
            version: '1.0',
            data_type: 'file'
          });
          setIsEditMode(false);
          setEditingStructure(null);
          setActiveStep(0);
          setAiAnalysis(null);
          setGeneratedMappings(null);
        }} 
        maxWidth="lg" 
        fullWidth
      >
        <DialogTitle>
          {isEditMode ? 'Edit Dataset Structure' : 'Create Dataset Structure'}
        </DialogTitle>
        <DialogContent>
          <Stepper activeStep={activeStep} orientation="vertical" sx={{ mt: 2 }}>
            <Step>
              <StepLabel>AI File Analysis & Field Definition</StepLabel>
              <StepContent>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Upload a sample file to automatically detect format, structure, data standards, preview the data, and configure field mappings
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={useClientSideAnalysis}
                        onChange={(e) => setUseClientSideAnalysis(e.target.checked)}
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="body2">
                          {useClientSideAnalysis ? 'Client-Side Analysis' : 'Server-Side Analysis'}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {useClientSideAnalysis 
                            ? 'Fast local processing - no server timeout' 
                            : 'Advanced AI analysis with data standards detection'
                          }
                        </Typography>
                      </Box>
                    }
                  />
                </Box>
                
                {/* File Analysis Section */}
                {useClientSideAnalysis ? (
                  <ClientSideFileAnalysis
                    onAnalysisComplete={(analysisData) => {
                      setAiAnalysis(analysisData);
                      autoPopulateFromAnalysis(analysisData);
                      
                      // Automatically generate field mappings from analysis
                      if (analysisData.field_analysis && analysisData.field_analysis.length > 0) {
                        const processedMappings = analysisData.field_analysis.map((field, index) => {
                          // Map field types to valid database types
                          let selectedType = 'text';
                          if (field.data_type) {
                            switch (field.data_type) {
                              case 'postcode':
                              case 'uprn':
                              case 'usrn':
                              case 'coordinate':
                              case 'longitude':
                              case 'latitude':
                                selectedType = 'text';
                                break;
                              case 'integer':
                              case 'number':
                                selectedType = 'integer';
                                break;
                              case 'decimal':
                              case 'float':
                              case 'numeric':
                                selectedType = 'decimal';
                                break;
                              case 'date':
                                selectedType = 'date';
                                break;
                              case 'timestamp':
                                selectedType = 'timestamp';
                                break;
                              case 'boolean':
                                selectedType = 'boolean';
                                break;
                              case 'geometry':
                                selectedType = 'geometry';
                                break;
                              case 'geography':
                                selectedType = 'geography';
                                break;
                              default:
                                selectedType = 'text';
                            }
                          }

                          return {
                            source_field: field.field_name || `field_${index + 1}`,
                            staging_field: field.field_name || `field_${index + 1}`,
                            data_type: selectedType,
                            postgis_type: field.postgis_type || null,
                            is_required: field.is_required || false,
                            is_primary_key: field.is_primary_key || index === 0,
                            default_value: field.default_value || '',
                            constraints: field.constraints || '',
                            description: field.description || `Field ${index + 1}`
                          };
                        });
                        setGeneratedMappings({ field_mappings: processedMappings });
                      }
                    }}
                    onMappingsGenerated={(mappingsData) => {
                      setGeneratedMappings(mappingsData);
                    }}
                    onSwitchToServer={(file) => {
                      setUseClientSideAnalysis(false);
                      showMessage(`Switched to server-side analysis for large file (${(file.size / (1024 * 1024)).toFixed(1)}MB)`, 'info');
                    }}
                  />
                ) : (
                  <FileAnalysisSection
                    onAnalysisComplete={(analysisData) => {
                      setAiAnalysis(analysisData);
                      autoPopulateFromAnalysis(analysisData);
                      
                      // Automatically generate field mappings from AI analysis
                      if (analysisData.field_analysis && analysisData.field_analysis.length > 0) {
                        const processedMappings = analysisData.field_analysis.map((field, index) => {
                          // Map field types to valid database types (same logic as in FieldAnalysisSection)
                          let selectedType = 'text';
                          if (field.type === 'empty') {
                            selectedType = 'text';
                          } else if (field.type) {
                            switch (field.type) {
                              case 'postcode':
                              case 'uprn':
                              case 'usrn':
                              case 'coordinate':
                              case 'longitude':
                              case 'latitude':
                                selectedType = 'text';
                                break;
                              case 'integer':
                              case 'number':
                                selectedType = 'integer';
                                break;
                              case 'decimal':
                              case 'float':
                              case 'numeric':
                                selectedType = 'decimal';
                                break;
                              case 'date':
                                selectedType = 'date';
                                break;
                              case 'timestamp':
                                selectedType = 'timestamp';
                                break;
                              case 'boolean':
                                selectedType = 'boolean';
                                break;
                              case 'geometry':
                                selectedType = 'geometry';
                                break;
                              case 'geography':
                                selectedType = 'geography';
                                break;
                              default:
                                selectedType = 'text';
                            }
                          }

                          return {
                            source_field: field.field_name || `field_${index + 1}`,
                            staging_field: field.field_name || `field_${index + 1}`,
                            data_type: selectedType,
                            postgis_type: null,
                            is_required: false,
                            is_primary_key: index === 0,
                            default_value: '',
                            constraints: '',
                            description: field.field_name || `Field ${index + 1}`
                          };
                        });
                        setGeneratedMappings({ field_mappings: processedMappings });
                      }
                    }}
                    onMappingsGenerated={(mappingsData) => {
                      setGeneratedMappings(mappingsData);
                    }}
                  />
                )}
                
                {/* Data Preview Section */}
                {aiAnalysis && (
                  <DataPreviewSection analysis={aiAnalysis} />
                )}
                
                {/* Field Analysis Section */}
                {aiAnalysis && aiAnalysis.field_analysis && (
                  <FieldAnalysisSection
                    fieldAnalysis={aiAnalysis.field_analysis}
                    onApplySuggestions={(suggestions) => {
                      // Convert suggestions to field mappings format
                      const processedMappings = suggestions.map(suggestion => ({
                        source_field: suggestion.sourceField,
                        staging_field: suggestion.sourceField,
                        data_type: suggestion.selectedType,
                        postgis_type: null,
                        is_required: suggestion.isRequired,
                        is_primary_key: suggestion.sequenceOrder === 1,
                        default_value: suggestion.defaultValue,
                        constraints: '',
                        description: suggestion.displayName
                      }));
                      setGeneratedMappings({ field_mappings: processedMappings });
                    }}
                    autoApply={true}
                  />
                )}
                

                
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    onClick={() => setActiveStep(1)}
                    disabled={!aiAnalysis || !generatedMappings?.field_mappings}
                  >
                    Next: Basic Information
                  </Button>
                </Box>
              </StepContent>
            </Step>
            
            <Step>
              <StepLabel>Basic Information</StepLabel>
              <StepContent>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Structure Name"
                      value={newStructure.name}
                      onChange={(e) => setNewStructure({...newStructure, name: e.target.value})}
                      placeholder={aiAnalysis?.filename ? aiAnalysis.filename.replace(/\.[^/.]+$/, "") : ""}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Version"
                      value={newStructure.version}
                      onChange={(e) => setNewStructure({...newStructure, version: e.target.value})}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>Source Type</InputLabel>
                      <Select
                        value={newStructure.source_type}
                        onChange={(e) => setNewStructure({...newStructure, source_type: e.target.value})}
                      >
                        <MenuItem value="csv">CSV</MenuItem>
                        <MenuItem value="json">JSON</MenuItem>
                        <MenuItem value="xml">XML</MenuItem>
                        <MenuItem value="shapefile">Shapefile</MenuItem>
                        <MenuItem value="geopackage">GeoPackage</MenuItem>
                        <MenuItem value="database">Database</MenuItem>
                        <MenuItem value="zip">ZIP Archive</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>Data Type</InputLabel>
                      <Select
                        value={newStructure.data_type}
                        onChange={(e) => setNewStructure({...newStructure, data_type: e.target.value})}
                      >
                        <MenuItem value="file">File Upload</MenuItem>
                        <MenuItem value="api">API Integration</MenuItem>
                        <MenuItem value="database">Database Connection</MenuItem>
                        <MenuItem value="stream">Real-time Stream</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>Target Schema Type</InputLabel>
                      <Select
                        value={newStructure.target_schema_type}
                        onChange={(e) => setNewStructure({...newStructure, target_schema_type: e.target.value})}
                      >
                        <MenuItem value="staging">Staging</MenuItem>
                        <MenuItem value="production">Production</MenuItem>
                        <MenuItem value="archive">Archive</MenuItem>
                        <MenuItem value="temp">Temporary</MenuItem>
                        <MenuItem value="backup">Backup</MenuItem>
                        <MenuItem value="analytics">Analytics</MenuItem>
                        <MenuItem value="reporting">Reporting</MenuItem>
                        <MenuItem value="audit">Audit</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Category"
                      value={newStructure.category}
                      onChange={(e) => setNewStructure({...newStructure, category: e.target.value})}
                      placeholder={aiAnalysis?.primary_governing_body || "e.g., Ordnance Survey, VOA, ONS"}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      multiline
                      rows={3}
                      label="Description"
                      value={newStructure.description}
                      onChange={(e) => setNewStructure({...newStructure, description: e.target.value})}
                    />
                  </Grid>
                </Grid>
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="outlined"
                    onClick={() => setActiveStep(0)}
                    sx={{ mr: 1 }}
                  >
                    Back
                  </Button>
                  <Button
                    variant="contained"
                    onClick={() => setActiveStep(2)}
                    disabled={!newStructure.name || !newStructure.source_type}
                  >
                    Next: Review & Create
                  </Button>
                </Box>
              </StepContent>
            </Step>
            
            <Step>
              <StepLabel>Review & Create</StepLabel>
              <StepContent>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Review the AI analysis, field mappings, and generated SQL before creating the dataset structure
                </Typography>
                
                {generatedMappings && (
                  <Alert severity="info" sx={{ mb: 2 }}>
                    <Typography variant="body2">
                      {generatedMappings.field_mappings?.length || 0} fields have been configured and are ready for structure creation.
                    </Typography>
                  </Alert>
                )}
                
                {/* SQL Preview */}
                <Accordion defaultExpanded sx={{ mb: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="h6">
                      <CodeIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Generated SQL Preview
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <TextField
                      fullWidth
                      multiline
                      rows={15}
                      value={generateSQLPreview()}
                      InputProps={{
                        readOnly: true,
                        style: { fontFamily: 'monospace', fontSize: '0.875rem' }
                      }}
                      variant="outlined"
                    />
                  </AccordionDetails>
                </Accordion>
                
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="outlined"
                    onClick={() => setActiveStep(1)}
                    sx={{ mr: 1 }}
                  >
                    Back
                  </Button>
                  <Button
                    variant="contained"
                    onClick={handleCreateStructure}
                    disabled={!newStructure.name || !newStructure.source_type || !generatedMappings?.field_mappings}
                  >
                    {isEditMode ? 'Update Dataset Structure' : 'Create Dataset Structure'}
                  </Button>
                </Box>
              </StepContent>
            </Step>
          </Stepper>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStructureDialog(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>

      {/* Create Field Dialog */}
      <Dialog open={fieldDialog} onClose={() => setFieldDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add Field to {selectedStructure?.dataset_name}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Field Name"
                value={newField.name}
                onChange={(e) => setNewField({...newField, name: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Display Name"
                value={newField.display_name}
                onChange={(e) => setNewField({...newField, display_name: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Data Type</InputLabel>
                <Select
                  value={newField.data_type}
                  onChange={(e) => setNewField({...newField, data_type: e.target.value})}
                >
                  <MenuItem value="text">Text</MenuItem>
                  <MenuItem value="integer">Integer</MenuItem>
                  <MenuItem value="decimal">Decimal</MenuItem>
                  <MenuItem value="boolean">Boolean</MenuItem>
                  <MenuItem value="date">Date</MenuItem>
                  <MenuItem value="timestamp">Timestamp</MenuItem>
                  <MenuItem value="geometry">Geometry</MenuItem>
                  <MenuItem value="geography">Geography</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="PostGIS Type"
                value={newField.postgis_type}
                onChange={(e) => setNewField({...newField, postgis_type: e.target.value})}
                placeholder="e.g., VARCHAR(255), INTEGER, GEOMETRY(POINT,4326)"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Default Value"
                value={newField.default_value}
                onChange={(e) => setNewField({...newField, default_value: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Constraints"
                value={newField.constraints}
                onChange={(e) => setNewField({...newField, constraints: e.target.value})}
                placeholder="e.g., NOT NULL, UNIQUE"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Description"
                value={newField.description}
                onChange={(e) => setNewField({...newField, description: e.target.value})}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={newField.is_required}
                    onChange={(e) => setNewField({...newField, is_required: e.target.checked})}
                  />
                }
                label="Required Field"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={newField.is_primary_key}
                    onChange={(e) => setNewField({...newField, is_primary_key: e.target.checked})}
                  />
                }
                label="Primary Key"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFieldDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateField} variant="contained" disabled={loading}>
            Add Field
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Template Dialog */}
      <Dialog open={templateDialog} onClose={() => setTemplateDialog(false)} maxWidth="lg" fullWidth>
        <DialogTitle>Create Table Template</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Template Name"
                value={newTemplate.name}
                onChange={(e) => setNewTemplate({...newTemplate, name: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Template Type</InputLabel>
                <Select
                  value={newTemplate.template_type}
                  onChange={(e) => setNewTemplate({...newTemplate, template_type: e.target.value})}
                >
                  <MenuItem value="staging">Staging Table</MenuItem>
                  <MenuItem value="production">Production Table</MenuItem>
                  <MenuItem value="archive">Archive Table</MenuItem>
                  <MenuItem value="temporary">Temporary Table</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Dataset Structure</InputLabel>
                <Select
                  value={newTemplate.structure_id || ''}
                  onChange={(e) => setNewTemplate({...newTemplate, structure_id: e.target.value})}
                >
                  {datasetStructures.map((structure) => (
                    <MenuItem key={structure.structure_id} value={structure.structure_id}>
                      {structure.dataset_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={newTemplate.description}
                onChange={(e) => setNewTemplate({...newTemplate, description: e.target.value})}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={10}
                label="Template SQL"
                value={newTemplate.template_sql}
                onChange={(e) => setNewTemplate({...newTemplate, template_sql: e.target.value})}
                placeholder="CREATE TABLE {table_name} (...)"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTemplateDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateTemplate} variant="contained" disabled={loading}>
            Create Template
          </Button>
        </DialogActions>
      </Dialog>

             {/* Table Structure Dialog */}
       <Dialog open={tableStructureDialog} onClose={() => setTableStructureDialog(false)} maxWidth="xl" fullWidth>
         <DialogTitle>
           <Box display="flex" alignItems="center" justifyContent="space-between">
             <Typography variant="h6">
               <TableIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
               Table Structure: {selectedStructureForView?.dataset_name}
             </Typography>
             <Chip 
               label={selectedStructureForView?.status || 'draft'} 
               color={getStatusColor(selectedStructureForView?.status || 'draft')}
               size="small"
             />
           </Box>
         </DialogTitle>
         <DialogContent>
           <Box mb={2}>
             <Typography variant="body2" color="textSecondary">
               {selectedStructureForView?.description}
             </Typography>
             <Typography variant="caption" display="block" sx={{ mt: 1 }}>
               Source Type: {selectedStructureForView?.source_type} | 
               Category: {selectedStructureForView?.governing_body} | 
               Created: {selectedStructureForView?.created_at ? new Date(selectedStructureForView.created_at).toLocaleDateString() : 'N/A'}
             </Typography>
           </Box>
           
           <Typography variant="h6" gutterBottom>
             <FieldIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
             Field Definitions ({structureFields.length} fields)
           </Typography>
           
           <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
             <Table stickyHeader>
               <TableHead>
                 <TableRow>
                   <TableCell sx={{ fontWeight: 'bold' }}>Field Name</TableCell>
                   <TableCell sx={{ fontWeight: 'bold' }}>Display Name</TableCell>
                   <TableCell sx={{ fontWeight: 'bold' }}>Data Type</TableCell>
                   <TableCell sx={{ fontWeight: 'bold' }}>PostGIS Type</TableCell>
                   <TableCell sx={{ fontWeight: 'bold' }}>Required</TableCell>
                   <TableCell sx={{ fontWeight: 'bold' }}>Primary Key</TableCell>
                   <TableCell sx={{ fontWeight: 'bold' }}>Default Value</TableCell>
                   <TableCell sx={{ fontWeight: 'bold' }}>Constraints</TableCell>
                   <TableCell sx={{ fontWeight: 'bold' }}>Description</TableCell>
                 </TableRow>
               </TableHead>
               <TableBody>
                 {loading ? (
                   <TableRow>
                     <TableCell colSpan={9} align="center">
                       <Typography variant="body2" color="textSecondary">
                         Loading fields...
                       </Typography>
                     </TableCell>
                   </TableRow>
                 ) : structureFields.length === 0 ? (
                   <TableRow>
                     <TableCell colSpan={9} align="center">
                       <Typography variant="body2" color="textSecondary">
                         No fields defined for this structure yet.
                       </Typography>
                     </TableCell>
                   </TableRow>
                 ) : (
                   structureFields.map((field) => (
                     <TableRow key={field.id} hover>
                       <TableCell>
                         <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                           {field.field_name}
                         </Typography>
                       </TableCell>
                       <TableCell>{field.display_name || field.field_name}</TableCell>
                       <TableCell>
                         <Chip 
                           label={field.field_type} 
                           size="small" 
                           color="primary" 
                           variant="outlined"
                         />
                       </TableCell>
                       <TableCell>
                         <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                           {field.postgis_type}
                         </Typography>
                       </TableCell>
                       <TableCell>
                         {field.is_required ? (
                           <Chip label="Yes" size="small" color="error" />
                         ) : (
                           <Chip label="No" size="small" color="default" variant="outlined" />
                         )}
                       </TableCell>
                       <TableCell>
                         {field.is_primary_key ? (
                           <Chip label="Yes" size="small" color="success" />
                         ) : (
                           <Chip label="No" size="small" color="default" variant="outlined" />
                         )}
                       </TableCell>
                       <TableCell>
                         <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                           {field.default_value || '-'}
                         </Typography>
                       </TableCell>
                       <TableCell>
                         <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                           {field.constraints || '-'}
                         </Typography>
                       </TableCell>
                       <TableCell>
                         <Typography variant="body2" color="textSecondary">
                           {field.description || '-'}
                         </Typography>
                       </TableCell>
                     </TableRow>
                   ))
                 )}
               </TableBody>
             </Table>
           </TableContainer>
           
           {structureFields.length > 0 && (
             <Box mt={2}>
               <Accordion>
                 <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                   <Typography variant="h6">
                     <CodeIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                     Generated SQL Preview
                   </Typography>
                 </AccordionSummary>
                 <AccordionDetails>
                   <TextField
                     fullWidth
                     multiline
                     rows={10}
                     value={generateSQLPreview()}
                     InputProps={{
                       readOnly: true,
                       style: { fontFamily: 'monospace', fontSize: '0.875rem' }
                     }}
                     variant="outlined"
                   />
                 </AccordionDetails>
               </Accordion>
             </Box>
           )}
         </DialogContent>
         <DialogActions>
           <Button 
             startIcon={<RefreshIcon />}
             onClick={() => loadStructureFields(selectedStructureForView.structure_id)}
             disabled={loading}
           >
             Refresh
           </Button>
           <Button 
             startIcon={<EditIcon />}
             onClick={() => {
               setTableStructureDialog(false);
               // Open edit dialog for this structure
               setEditingStructure(selectedStructureForView);
               setNewStructure({
                 name: selectedStructureForView.dataset_name,
                 description: selectedStructureForView.description || '',
                 source_type: selectedStructureForView.source_type,
                 category: selectedStructureForView.governing_body || '',
                 version: '1.0',
                 data_type: selectedStructureForView.source_type === 'file' ? 'file' : selectedStructureForView.source_type
               });
               setIsEditMode(true);
               setStructureDialog(true);
             }}
           >
             Edit Structure
           </Button>
           <Button 
             startIcon={<FieldIcon />}
             onClick={() => {
               setTableStructureDialog(false);
               setSelectedStructure(selectedStructureForView);
               setFieldDialog(true);
             }}
           >
             Add Field
           </Button>
           <Button onClick={() => setTableStructureDialog(false)}>Close</Button>
         </DialogActions>
       </Dialog>

       {/* Dataset Type Details Dialog */}
       <Dialog open={!!selectedType} onClose={() => setSelectedType(null)} maxWidth="md" fullWidth>
         <DialogTitle>
           <Box display="flex" alignItems="center" justifyContent="space-between">
             <Typography variant="h6">
               <DataIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
               Dataset Type: {selectedType?.display_name}
             </Typography>
             <Chip 
               label={selectedType?.category || 'N/A'} 
               color="primary"
               size="small"
             />
           </Box>
         </DialogTitle>
         <DialogContent>
           <Grid container spacing={3}>
             <Grid item xs={12}>
               <Typography variant="body2" color="textSecondary" gutterBottom>
                 {selectedType?.description}
               </Typography>
             </Grid>
             
             <Grid item xs={12} md={6}>
               <Typography variant="subtitle2" gutterBottom>Type Information</Typography>
               <Typography variant="body2" gutterBottom>
                 <strong>Type Name:</strong> {selectedType?.type_name}
               </Typography>
               <Typography variant="body2" gutterBottom>
                 <strong>Category:</strong> {selectedType?.category}
               </Typography>
               <Typography variant="body2" gutterBottom>
                 <strong>Governing Body:</strong> {selectedType?.governing_body || 'N/A'}
               </Typography>
               <Typography variant="body2" gutterBottom>
                 <strong>Status:</strong> 
                 <Chip 
                   label={selectedType?.is_active ? 'Active' : 'Inactive'} 
                   size="small" 
                   color={selectedType?.is_active ? 'success' : 'default'}
                   sx={{ ml: 1 }}
                 />
               </Typography>
             </Grid>
             
             <Grid item xs={12} md={6}>
               <Typography variant="subtitle2" gutterBottom>Field Requirements</Typography>
               <Typography variant="body2" gutterBottom>
                 <strong>Required Fields:</strong> {selectedType?.required_fields?.length || 0}
               </Typography>
               <Typography variant="body2" gutterBottom>
                 <strong>Optional Fields:</strong> {selectedType?.optional_fields?.length || 0}
               </Typography>
               <Typography variant="body2" gutterBottom>
                 <strong>Validation Rules:</strong> {selectedType?.validation_rules?.length || 0}
               </Typography>
               <Typography variant="body2" gutterBottom>
                 <strong>Data Standards:</strong> {selectedType?.data_standards?.length || 0}
               </Typography>
             </Grid>
             
             {selectedType?.required_fields && selectedType.required_fields.length > 0 && (
               <Grid item xs={12}>
                 <Typography variant="subtitle2" gutterBottom>Required Fields</Typography>
                 <TableContainer component={Paper} variant="outlined">
                   <Table size="small">
                     <TableHead>
                       <TableRow>
                         <TableCell>Field Name</TableCell>
                         <TableCell>Data Type</TableCell>
                         <TableCell>Description</TableCell>
                       </TableRow>
                     </TableHead>
                     <TableBody>
                       {selectedType.required_fields.map((field, index) => (
                         <TableRow key={index}>
                           <TableCell>{field.name || field}</TableCell>
                           <TableCell>{field.data_type || 'text'}</TableCell>
                           <TableCell>{field.description || '-'}</TableCell>
                         </TableRow>
                       ))}
                     </TableBody>
                   </Table>
                 </TableContainer>
               </Grid>
             )}
             
             {selectedType?.optional_fields && selectedType.optional_fields.length > 0 && (
               <Grid item xs={12}>
                 <Typography variant="subtitle2" gutterBottom>Optional Fields</Typography>
                 <TableContainer component={Paper} variant="outlined">
                   <Table size="small">
                     <TableHead>
                       <TableRow>
                         <TableCell>Field Name</TableCell>
                         <TableCell>Data Type</TableCell>
                         <TableCell>Description</TableCell>
                       </TableRow>
                     </TableHead>
                     <TableBody>
                       {selectedType.optional_fields.map((field, index) => (
                         <TableRow key={index}>
                           <TableCell>{field.name || field}</TableCell>
                           <TableCell>{field.data_type || 'text'}</TableCell>
                           <TableCell>{field.description || '-'}</TableCell>
                         </TableRow>
                       ))}
                     </TableBody>
                   </Table>
                 </TableContainer>
               </Grid>
             )}
             
             {selectedType?.data_standards && selectedType.data_standards.length > 0 && (
               <Grid item xs={12}>
                 <Typography variant="subtitle2" gutterBottom>Data Standards</Typography>
                 <Box display="flex" flexWrap="wrap" gap={1}>
                   {selectedType.data_standards.map((standard, index) => (
                     <Chip 
                       key={index}
                       label={standard.name || standard} 
                       size="small" 
                       color="secondary" 
                       variant="outlined"
                     />
                   ))}
                 </Box>
               </Grid>
             )}
             
             <Grid item xs={12}>
               <Typography variant="caption" color="textSecondary">
                 Created by: {selectedType?.created_by} | 
                 Created: {selectedType?.created_at ? new Date(selectedType.created_at).toLocaleDateString() : 'N/A'} |
                 Updated: {selectedType?.updated_at ? new Date(selectedType.updated_at).toLocaleDateString() : 'N/A'}
               </Typography>
             </Grid>
           </Grid>
         </DialogContent>
         <DialogActions>
           <Button onClick={() => setSelectedType(null)}>Close</Button>
         </DialogActions>
       </Dialog>

       {/* Delete Confirmation Dialog */}
       <Dialog open={deleteDialog} onClose={() => setDeleteDialog(false)} maxWidth="sm" fullWidth>
         <DialogTitle>
           <Box display="flex" alignItems="center">
             <WarningIcon sx={{ mr: 1, color: 'error.main' }} />
             Confirm Delete
           </Box>
         </DialogTitle>
         <DialogContent>
           <Typography variant="body1" gutterBottom>
             Are you sure you want to delete the dataset structure:
           </Typography>
           <Typography variant="h6" color="error" gutterBottom>
             "{structureToDelete?.dataset_name}"
           </Typography>
           <Alert severity="warning" sx={{ mt: 2 }}>
             <Typography variant="body2">
               This action will permanently delete the structure and all its associated field definitions. 
               This action cannot be undone.
             </Typography>
           </Alert>
         </DialogContent>
         <DialogActions>
           <Button 
             onClick={() => setDeleteDialog(false)}
             disabled={loading}
           >
             Cancel
           </Button>
           <Button 
             onClick={confirmDeleteStructure}
             color="error"
             variant="contained"
             disabled={loading}
             startIcon={loading ? null : <DeleteOutlineIcon />}
           >
             {loading ? 'Deleting...' : 'Delete Structure'}
           </Button>
         </DialogActions>
       </Dialog>



      <Snackbar
        open={!!message}
        autoHideDuration={6000}
        onClose={() => setMessage('')}
      >
        <Alert onClose={() => setMessage('')} severity={severity}>
          {message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default DatasetStructures; 