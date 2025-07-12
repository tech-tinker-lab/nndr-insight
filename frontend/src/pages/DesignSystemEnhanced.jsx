import React, { useState, useEffect } from 'react';
import api from '../api/axios';
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

const DesignSystemEnhanced = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [severity, setSeverity] = useState('info');
  
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
  
  // Stepper and AI Analysis
  const [activeStep, setActiveStep] = useState(0);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [selectedHeaderFile, setSelectedHeaderFile] = useState(null);
  const [selectedDataFiles, setSelectedDataFiles] = useState([]);
  const [generatedMappings, setGeneratedMappings] = useState(null);
  
  // Form States
  const [newStructure, setNewStructure] = useState({
    name: '',
    description: '',
    source_type: '',
    category: '',
    version: '1.0'
  });
  
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
        structuresResponse,
        templatesResponse
      ] = await Promise.all([
        api.get('/api/design-enhanced/structures'),
        api.get('/api/design-enhanced/templates')
      ]);

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

  const handleCreateStructure = async () => {
    try {
      setLoading(true);
      const structureData = {
        dataset_name: newStructure.name,
        description: newStructure.description,
        source_type: newStructure.source_type,
        file_formats: [newStructure.source_type],
        governing_body: newStructure.category,
        data_standards: aiAnalysis?.identified_standards?.map(s => s.standard_id) || [],
        tags: [newStructure.category]
      };
      
      const response = await api.post('/api/design-enhanced/structures', structureData);
      
      // Reload structures to get the updated list
      const structuresResponse = await api.get('/api/design-enhanced/structures');
      setDatasetStructures(structuresResponse.data.structures || []);
      
      setStructureDialog(false);
      setActiveStep(0);
      setAiAnalysis(null);
      setNewStructure({ name: '', description: '', source_type: '', category: '', version: '1.0' });
      showMessage('Dataset structure created successfully', 'success');
    } catch (error) {
      showMessage('Error creating structure: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateField = async () => {
    try {
      setLoading(true);
      const fieldData = {
        field_name: newField.name,
        display_name: newField.display_name,
        data_type: newField.data_type,
        postgis_type: newField.postgis_type,
        is_required: newField.is_required,
        is_primary_key: newField.is_primary_key,
        default_value: newField.default_value,
        constraints: newField.constraints,
        description: newField.description,
        sequence_order: 1
      };
      
      const response = await api.post(`/api/design-enhanced/structures/${selectedStructure.structure_id}/fields`, fieldData);
      setFieldDialog(false);
      setNewField({ name: '', display_name: '', data_type: '', postgis_type: '', is_required: false, is_primary_key: false, default_value: '', constraints: '', description: '' });
      showMessage('Field created successfully', 'success');
    } catch (error) {
      showMessage('Error creating field: ' + error.message, 'error');
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
        template_sql: newTemplate.template_sql
      };
      
      const response = await api.post('/api/design-enhanced/templates', templateData);
      
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
      const response = await api.post(`/api/design-enhanced/templates/${templateId}/generate`, {
        table_name: `generated_table_${Date.now()}`,
        schema_name: 'public'
      });
      showMessage('Table generated successfully', 'success');
    } catch (error) {
      showMessage('Error generating table: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleStructureFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post('/api/design-enhanced/ai/analyze-file', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setAiAnalysis(response.data.analysis);
      setSelectedHeaderFile(null);
      setSelectedDataFiles([]);
      setGeneratedMappings(null);
      showMessage('File analyzed successfully', 'success');
    } catch (error) {
      showMessage('Error analyzing file: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Auto-generate mappings when CSV file is selected
  const handleHeaderFileSelection = (filename) => {
    setSelectedHeaderFile(filename);
    
    // Auto-generate mappings for CSV files
    if (aiAnalysis?.content_analysis?.file_previews?.[filename]?.format === 'csv') {
      // Set this file as the only data file for CSV processing
      setSelectedDataFiles([filename]);
      
      // Auto-generate mappings after a short delay
      setTimeout(() => {
        handleGenerateMappings();
      }, 500);
    }
  };

  const handleGenerateMappings = async () => {
    if (!selectedHeaderFile || selectedDataFiles.length === 0) {
      showMessage('Please select a header file and at least one data file', 'warning');
      return;
    }

    try {
      setLoading(true);
      const response = await api.post('/api/design-enhanced/ai/generate-mappings', {
        header_file: selectedHeaderFile,
        data_files: selectedDataFiles,
        analysis_data: aiAnalysis
      });
      
      setGeneratedMappings(response.data.mappings);
      showMessage('Field mappings generated successfully', 'success');
    } catch (error) {
      showMessage('Error generating mappings: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
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
                <Box mt={2}>
                  <Button
                    size="small"
                    startIcon={<FieldIcon />}
                    onClick={() => {
                      setSelectedStructure(structure);
                      setFieldDialog(true);
                    }}
                  >
                    Add Field
                  </Button>
                  <Button
                    size="small"
                    startIcon={<ViewIcon />}
                    onClick={() => setSelectedStructure(structure)}
                  >
                    View Fields
                  </Button>
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
                  <Button
                    size="small"
                    startIcon={<ViewIcon />}
                    onClick={() => setSelectedTemplate(template)}
                  >
                    View SQL
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
        <Button
          variant="contained"
          startIcon={<UploadIcon />}
          onClick={() => setUploadDialog(true)}
        >
          Upload Dataset
        </Button>
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
          <Tab label="Dataset Structures" icon={<StorageIcon />} />
          <Tab label="Table Templates" icon={<SchemaIcon />} />
          <Tab label="Recent Uploads" icon={<CloudUploadIcon />} />
        </Tabs>
      </Box>

      {activeTab === 0 && renderDatasetStructures()}
      {activeTab === 1 && renderTableTemplates()}
      {activeTab === 2 && renderRecentUploads()}

      {/* Create Structure Dialog */}
      <Dialog open={structureDialog} onClose={() => setStructureDialog(false)} maxWidth="lg" fullWidth>
        <DialogTitle>Create Dataset Structure</DialogTitle>
        <DialogContent>
          <Stepper activeStep={activeStep} orientation="vertical" sx={{ mt: 2 }}>
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
                    <TextField
                      fullWidth
                      label="Category"
                      value={newStructure.category}
                      onChange={(e) => setNewStructure({...newStructure, category: e.target.value})}
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
                    variant="contained"
                    onClick={() => setActiveStep(1)}
                    disabled={!newStructure.name || !newStructure.source_type}
                  >
                    Next: AI Analysis
                  </Button>
                </Box>
              </StepContent>
            </Step>
            
            <Step>
              <StepLabel>AI File Analysis (Optional)</StepLabel>
              <StepContent>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Upload a sample file to automatically detect format, structure, and data standards
                </Typography>
                
                <input
                  accept=".csv,.json,.xml,.txt,.gpkg,.shp,.zip,.yaml,.yml"
                  style={{ display: 'none' }}
                  id="structure-file-upload"
                  type="file"
                  onChange={handleStructureFileUpload}
                />
                <label htmlFor="structure-file-upload">
                  <Button
                    variant="outlined"
                    component="span"
                    startIcon={<UploadIcon />}
                    disabled={loading}
                    sx={{ mb: 2 }}
                  >
                    Upload Sample File
                  </Button>
                </label>
                
                {aiAnalysis && (
                  <Card variant="outlined" sx={{ mt: 2 }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        AI Analysis Results
                      </Typography>
                      
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                          <Typography variant="subtitle2">Format</Typography>
                          <Chip label={aiAnalysis.format} color="primary" size="small" />
                        </Grid>
                        {aiAnalysis.encoding && (
                          <Grid item xs={12} sm={6}>
                            <Typography variant="subtitle2">Encoding</Typography>
                            <Typography variant="body2">{aiAnalysis.encoding}</Typography>
                          </Grid>
                        )}
                        {aiAnalysis.delimiter && (
                          <Grid item xs={12} sm={6}>
                            <Typography variant="subtitle2">Delimiter</Typography>
                            <Typography variant="body2">'{aiAnalysis.delimiter}'</Typography>
                          </Grid>
                        )}
                        {aiAnalysis.field_count && (
                          <Grid item xs={12} sm={6}>
                            <Typography variant="subtitle2">Fields</Typography>
                            <Typography variant="body2">{aiAnalysis.field_count}</Typography>
                          </Grid>
                        )}
                      </Grid>
                      
                      {aiAnalysis.identified_standards && aiAnalysis.identified_standards.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>Identified Data Standards</Typography>
                          {aiAnalysis.identified_standards.map((standard, index) => (
                            <Chip
                              key={index}
                              label={`${standard.name} (${(standard.confidence * 100).toFixed(0)}%)`}
                              color={standard.confidence > 0.7 ? "success" : "warning"}
                              size="small"
                              sx={{ mr: 1, mb: 1 }}
                            />
                          ))}
                        </Box>
                      )}
                      
                      {/* Enhanced ZIP Analysis Results */}
                      {aiAnalysis.format === 'zip' && aiAnalysis.content_analysis && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>ZIP Structure Analysis</Typography>
                          
                          {aiAnalysis.content_analysis.has_header_data_structure && (
                            <Alert severity="info" sx={{ mb: 2 }}>
                              <Typography variant="body2">
                                <strong>Header/Data Structure Detected:</strong> This ZIP file contains separate directories for header files and data files.
                              </Typography>
                            </Alert>
                          )}
                          
                          {/* Directory Structure */}
                          {aiAnalysis.content_analysis.directory_structure && Object.keys(aiAnalysis.content_analysis.directory_structure).length > 0 && (
                            <Accordion>
                              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                <Typography>Directory Structure ({Object.keys(aiAnalysis.content_analysis.directory_structure).length} directories)</Typography>
                              </AccordionSummary>
                              <AccordionDetails>
                                {Object.entries(aiAnalysis.content_analysis.directory_structure).map(([dir, info]) => (
                                  <Box key={dir} sx={{ mb: 2, p: 1, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                                    <Typography variant="subtitle2" color="primary">
                                      📁 {dir}
                                    </Typography>
                                    <Typography variant="caption" display="block">
                                      Files: {info.files.length} | Size: {(info.total_size / 1024).toFixed(1)} KB | Types: {info.file_types.join(', ')}
                                    </Typography>
                                    <Box sx={{ mt: 1 }}>
                                      {info.files.slice(0, 3).map((file, idx) => (
                                        <Chip
                                          key={idx}
                                          label={`${file.name.split('/').pop()} (${(file.size / 1024).toFixed(1)} KB)`}
                                          size="small"
                                          variant="outlined"
                                          sx={{ mr: 0.5, mb: 0.5 }}
                                        />
                                      ))}
                                      {info.files.length > 3 && (
                                        <Typography variant="caption" color="textSecondary">
                                          +{info.files.length - 3} more files
                                        </Typography>
                                      )}
                                    </Box>
                                  </Box>
                                ))}
                              </AccordionDetails>
                            </Accordion>
                          )}
                          
                          {/* Suggested Header Files */}
                          {aiAnalysis.content_analysis.suggested_header_files && aiAnalysis.content_analysis.suggested_header_files.length > 0 && (
                            <Accordion defaultExpanded>
                              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                <Typography>Suggested Header Files ({aiAnalysis.content_analysis.suggested_header_files.length})</Typography>
                              </AccordionSummary>
                              <AccordionDetails>
                                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                                  Select a header file to define the data structure:
                                </Typography>
                                {aiAnalysis.content_analysis.suggested_header_files.map((file, index) => (
                                  <Card key={index} sx={{ mb: 2, border: selectedHeaderFile === file.filename ? '2px solid #1976d2' : '1px solid #e0e0e0' }}>
                                    <CardContent>
                                      <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                                        <Typography variant="subtitle2">
                                          📄 {file.filename.split('/').pop()}
                                        </Typography>
                                        <Chip 
                                          label={file.confidence} 
                                          color={file.confidence === 'high' ? 'success' : 'warning'}
                                          size="small"
                                        />
                                      </Box>
                                      
                                      {file.headers && (
                                        <Box sx={{ mb: 1 }}>
                                          <Typography variant="caption" color="textSecondary">Headers ({file.headers.length}):</Typography>
                                          <Box sx={{ mt: 0.5 }}>
                                            {file.headers.slice(0, 5).map((header, idx) => (
                                              <Chip
                                                key={idx}
                                                label={header}
                                                size="small"
                                                variant="outlined"
                                                sx={{ mr: 0.5, mb: 0.5 }}
                                              />
                                            ))}
                                            {file.headers.length > 5 && (
                                              <Typography variant="caption" color="textSecondary">
                                                +{file.headers.length - 5} more headers
                                              </Typography>
                                            )}
                                          </Box>
                                        </Box>
                                      )}
                                      
                                      {file.sample_rows && file.sample_rows.length > 0 && (
                                        <Box sx={{ mb: 1 }}>
                                          <Typography variant="caption" color="textSecondary">Sample Data:</Typography>
                                          <TableContainer component={Paper} sx={{ mt: 0.5, maxHeight: 200 }}>
                                            <Table size="small">
                                              <TableHead>
                                                <TableRow>
                                                  {file.headers && file.headers.slice(0, 5).map((header, idx) => (
                                                    <TableCell key={idx} size="small">{header}</TableCell>
                                                  ))}
                                                </TableRow>
                                              </TableHead>
                                              <TableBody>
                                                {file.sample_rows.slice(0, 3).map((row, rowIdx) => (
                                                  <TableRow key={rowIdx}>
                                                    {row.slice(0, 5).map((cell, cellIdx) => (
                                                      <TableCell key={cellIdx} size="small">{cell}</TableCell>
                                                    ))}
                                                  </TableRow>
                                                ))}
                                              </TableBody>
                                            </Table>
                                          </TableContainer>
                                        </Box>
                                      )}
                                      
                                      <Button
                                        variant={selectedHeaderFile === file.filename ? "contained" : "outlined"}
                                        size="small"
                                        onClick={() => handleHeaderFileSelection(file.filename)}
                                        sx={{ mt: 1 }}
                                      >
                                        {selectedHeaderFile === file.filename ? "Selected" : "Select as Header"}
                                      </Button>
                                    </CardContent>
                                  </Card>
                                ))}
                              </AccordionDetails>
                            </Accordion>
                          )}
                          
                          {/* Suggested Data Files */}
                          {aiAnalysis.content_analysis.suggested_data_files && aiAnalysis.content_analysis.suggested_data_files.length > 0 && (
                            <Accordion defaultExpanded>
                              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                <Typography>Suggested Data Files ({aiAnalysis.content_analysis.suggested_data_files.length})</Typography>
                              </AccordionSummary>
                              <AccordionDetails>
                                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                                  Select data files to process:
                                </Typography>
                                {aiAnalysis.content_analysis.suggested_data_files.map((file, index) => (
                                  <Card key={index} sx={{ mb: 2, border: selectedDataFiles.includes(file.filename) ? '2px solid #1976d2' : '1px solid #e0e0e0' }}>
                                    <CardContent>
                                      <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                                        <Typography variant="subtitle2">
                                          📊 {file.filename.split('/').pop()}
                                        </Typography>
                                        <Chip label={file.type.toUpperCase()} color="primary" size="small" />
                                      </Box>
                                      
                                      <Typography variant="caption" display="block">
                                        Fields: {file.field_count} | Estimated Rows: {file.row_count_estimate.toLocaleString()}
                                      </Typography>
                                      
                                      {file.headers && (
                                        <Box sx={{ mb: 1 }}>
                                          <Typography variant="caption" color="textSecondary">Fields:</Typography>
                                          <Box sx={{ mt: 0.5 }}>
                                            {file.headers.slice(0, 5).map((header, idx) => (
                                              <Chip
                                                key={idx}
                                                label={header}
                                                size="small"
                                                variant="outlined"
                                                sx={{ mr: 0.5, mb: 0.5 }}
                                              />
                                            ))}
                                            {file.headers.length > 5 && (
                                              <Typography variant="caption" color="textSecondary">
                                                +{file.headers.length - 5} more fields
                                              </Typography>
                                            )}
                                          </Box>
                                        </Box>
                                      )}
                                      
                                      <FormControlLabel
                                        control={
                                          <Switch
                                            checked={selectedDataFiles.includes(file.filename)}
                                            onChange={(e) => {
                                              if (e.target.checked) {
                                                setSelectedDataFiles([...selectedDataFiles, file.filename]);
                                              } else {
                                                setSelectedDataFiles(selectedDataFiles.filter(f => f !== file.filename));
                                              }
                                            }}
                                          />
                                        }
                                        label="Include in processing"
                                      />
                                    </CardContent>
                                  </Card>
                                ))}
                              </AccordionDetails>
                            </Accordion>
                          )}
                          
                          {/* Generate Mappings Button */}
                          {selectedHeaderFile && selectedDataFiles.length > 0 && (
                            <Box sx={{ mt: 2 }}>
                              <Button
                                variant="contained"
                                color="primary"
                                onClick={handleGenerateMappings}
                                disabled={loading}
                                startIcon={<BuildIcon />}
                                fullWidth
                              >
                                Generate Source-to-Staging Mappings
                              </Button>
                            </Box>
                          )}
                          
                          {/* Generated Mappings Display */}
                          {generatedMappings && (
                            <Accordion defaultExpanded sx={{ mt: 2 }}>
                              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                <Typography>Generated Field Mappings ({generatedMappings.field_mappings.length} fields)</Typography>
                              </AccordionSummary>
                              <AccordionDetails>
                                <TableContainer component={Paper}>
                                  <Table size="small">
                                    <TableHead>
                                      <TableRow>
                                        <TableCell>Source Field</TableCell>
                                        <TableCell>Staging Field</TableCell>
                                        <TableCell>Data Type</TableCell>
                                        <TableCell>PostGIS Type</TableCell>
                                        <TableCell>Constraints</TableCell>
                                        <TableCell>Transformations</TableCell>
                                      </TableRow>
                                    </TableHead>
                                    <TableBody>
                                      {generatedMappings.field_mappings.map((mapping, index) => (
                                        <TableRow key={index}>
                                          <TableCell>{mapping.source_field}</TableCell>
                                          <TableCell>{mapping.staging_field}</TableCell>
                                          <TableCell>
                                            <Chip label={mapping.data_type} size="small" color="primary" />
                                          </TableCell>
                                          <TableCell>{mapping.postgis_type}</TableCell>
                                          <TableCell>
                                            {mapping.constraints.length > 0 ? (
                                              <Chip label={`${mapping.constraints.length} constraints`} size="small" />
                                            ) : (
                                              <Typography variant="caption" color="textSecondary">None</Typography>
                                            )}
                                          </TableCell>
                                          <TableCell>
                                            {mapping.transformation_rules.length > 0 ? (
                                              <Chip label={`${mapping.transformation_rules.length} rules`} size="small" />
                                            ) : (
                                              <Typography variant="caption" color="textSecondary">None</Typography>
                                            )}
                                          </TableCell>
                                        </TableRow>
                                      ))}
                                    </TableBody>
                                  </Table>
                                </TableContainer>
                                
                                {generatedMappings.recommendations && generatedMappings.recommendations.length > 0 && (
                                  <Box sx={{ mt: 2 }}>
                                    <Typography variant="subtitle2" gutterBottom>Recommendations:</Typography>
                                    <List dense>
                                      {generatedMappings.recommendations.map((rec, index) => (
                                        <ListItem key={index}>
                                          <ListItemIcon>
                                            <CheckIcon color="primary" />
                                          </ListItemIcon>
                                          <ListItemText primary={rec} />
                                        </ListItem>
                                      ))}
                                    </List>
                                  </Box>
                                )}
                              </AccordionDetails>
                            </Accordion>
                          )}
                          
                          {/* Documentation Files */}
                          {aiAnalysis.content_analysis.documentation && aiAnalysis.content_analysis.documentation.length > 0 && (
                            <Accordion>
                              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                <Typography>Documentation ({aiAnalysis.content_analysis.documentation.length})</Typography>
                              </AccordionSummary>
                              <AccordionDetails>
                                <List dense>
                                  {aiAnalysis.content_analysis.documentation.map((file, index) => (
                                    <ListItem key={index}>
                                      <ListItemText
                                        primary={file.name.split('/').pop()}
                                        secondary={`${(file.size / 1024).toFixed(1)} KB | ${file.type}`}
                                      />
                                    </ListItem>
                                  ))}
                                </List>
                              </AccordionDetails>
                            </Accordion>
                          )}
                          
                          {/* Metadata Files */}
                          {aiAnalysis.content_analysis.metadata && aiAnalysis.content_analysis.metadata.length > 0 && (
                            <Accordion>
                              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                <Typography>Metadata ({aiAnalysis.content_analysis.metadata.length})</Typography>
                              </AccordionSummary>
                              <AccordionDetails>
                                <List dense>
                                  {aiAnalysis.content_analysis.metadata.map((file, index) => (
                                    <ListItem key={index}>
                                      <ListItemText
                                        primary={file.name.split('/').pop()}
                                        secondary={`${(file.size / 1024).toFixed(1)} KB | ${file.type}`}
                                      />
                                    </ListItem>
                                  ))}
                                </List>
                              </AccordionDetails>
                            </Accordion>
                          )}
                          
                          {/* All Files with Previews */}
                          {aiAnalysis.content_analysis.file_previews && Object.keys(aiAnalysis.content_analysis.file_previews).length > 0 && (
                            <Accordion defaultExpanded>
                              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                <Typography>All Files with Previews ({Object.keys(aiAnalysis.content_analysis.file_previews).length})</Typography>
                              </AccordionSummary>
                              <AccordionDetails>
                                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                                  Debug information for all files in the ZIP:
                                </Typography>
                                {Object.entries(aiAnalysis.content_analysis.file_previews).map(([filename, preview], index) => (
                                  <Card key={index} sx={{ mb: 2, border: '1px solid #e0e0e0' }}>
                                    <CardContent>
                                      <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                                        <Typography variant="subtitle2">
                                          📄 {filename.split('/').pop()}
                                        </Typography>
                                        <Chip 
                                          label={preview.extension || 'unknown'} 
                                          size="small"
                                          color={preview.preview_attempted ? 'success' : 'warning'}
                                        />
                                      </Box>
                                      
                                      <Typography variant="caption" display="block">
                                        Size: {(preview.size / 1024).toFixed(1)} KB | 
                                        Preview: {preview.preview_attempted ? 'Yes' : 'No'}
                                      </Typography>
                                      
                                      {preview.note && (
                                        <Typography variant="caption" color="textSecondary" display="block">
                                          Note: {preview.note}
                                        </Typography>
                                      )}
                                      
                                      {preview.preview_error && (
                                        <Typography variant="caption" color="error" display="block">
                                          Error: {preview.preview_error}
                                        </Typography>
                                      )}
                                      
                                      {preview.has_header && preview.headers && (
                                        <Box sx={{ mt: 1 }}>
                                          <Typography variant="caption" color="textSecondary">Headers:</Typography>
                                          <Box sx={{ mt: 0.5 }}>
                                            {preview.headers.slice(0, 3).map((header, idx) => (
                                              <Chip
                                                key={idx}
                                                label={header}
                                                size="small"
                                                variant="outlined"
                                                sx={{ mr: 0.5, mb: 0.5 }}
                                              />
                                            ))}
                                            {preview.headers.length > 3 && (
                                              <Typography variant="caption" color="textSecondary">
                                                +{preview.headers.length - 3} more
                                              </Typography>
                                            )}
                                          </Box>
                                        </Box>
                                      )}
                                    </CardContent>
                                  </Card>
                                ))}
                              </AccordionDetails>
                            </Accordion>
                          )}
                        </Box>
                      )}
                      
                      {aiAnalysis.recommendations && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>Recommendations</Typography>
                          <Accordion>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                              <Typography>Data Structure</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                              <List dense>
                                {aiAnalysis.recommendations.data_structure.map((rec, index) => (
                                  <ListItem key={index}>
                                    <ListItemText primary={rec} />
                                  </ListItem>
                                ))}
                              </List>
                            </AccordionDetails>
                          </Accordion>
                          
                          {aiAnalysis.recommendations.postgis_types.length > 0 && (
                            <Accordion>
                              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                <Typography>PostGIS Types</Typography>
                              </AccordionSummary>
                              <AccordionDetails>
                                <List dense>
                                  {aiAnalysis.recommendations.postgis_types.map((rec, index) => (
                                    <ListItem key={index}>
                                      <ListItemText primary={rec} />
                                    </ListItem>
                                  ))}
                                </List>
                              </AccordionDetails>
                            </Accordion>
                          )}
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                )}
                
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
                  >
                    Next: Review
                  </Button>
                </Box>
              </StepContent>
            </Step>
            
            <Step>
              <StepLabel>Review & Create</StepLabel>
              <StepContent>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Structure Summary</Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2">Name</Typography>
                        <Typography variant="body2">{newStructure.name}</Typography>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2">Version</Typography>
                        <Typography variant="body2">{newStructure.version}</Typography>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2">Source Type</Typography>
                        <Typography variant="body2">{newStructure.source_type}</Typography>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2">Category</Typography>
                        <Typography variant="body2">{newStructure.category}</Typography>
                      </Grid>
                      <Grid item xs={12}>
                        <Typography variant="subtitle2">Description</Typography>
                        <Typography variant="body2">{newStructure.description}</Typography>
                      </Grid>
                    </Grid>
                    
                    {aiAnalysis && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>AI Analysis Applied</Typography>
                        <Chip label={`${aiAnalysis.format.toUpperCase()} format detected`} color="info" size="small" />
                        {aiAnalysis.field_count && (
                          <Chip label={`${aiAnalysis.field_count} fields`} color="info" size="small" sx={{ ml: 1 }} />
                        )}
                      </Box>
                    )}
                  </CardContent>
                </Card>
                
                {/* Field Mappings Display */}
                {generatedMappings && (
                  <Card variant="outlined" sx={{ mt: 2 }}>
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                        <Typography variant="h6">Field Mappings</Typography>
                        <Chip 
                          label={generatedMappings.mapping_type} 
                          color="primary" 
                          size="small"
                        />
                      </Box>
                      
                      <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                        {generatedMappings.mapping_type === 'csv_with_headers' 
                          ? '1-to-1 mapping from CSV headers to staging fields:'
                          : 'Generated field names based on data standards:'
                        }
                      </Typography>
                      
                      <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
                        <Table size="small" stickyHeader>
                          <TableHead>
                            <TableRow>
                              <TableCell>Source Field</TableCell>
                              <TableCell>Staging Field</TableCell>
                              <TableCell>Data Type</TableCell>
                              <TableCell>PostGIS Type</TableCell>
                              <TableCell>Sample Value</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {generatedMappings.field_mappings.map((mapping, index) => (
                              <TableRow key={index} hover>
                                <TableCell>
                                  <Typography variant="body2" fontWeight="medium">
                                    {mapping.source_field}
                                  </Typography>
                                  <Typography variant="caption" color="textSecondary">
                                    Column {mapping.source_column_index + 1}
                                  </Typography>
                                </TableCell>
                                <TableCell>
                                  <Typography variant="body2" fontFamily="monospace">
                                    {mapping.staging_field}
                                  </Typography>
                                </TableCell>
                                <TableCell>
                                  <Chip 
                                    label={mapping.data_type} 
                                    size="small" 
                                    color="primary"
                                    variant="outlined"
                                  />
                                </TableCell>
                                <TableCell>
                                  <Typography variant="body2" fontFamily="monospace">
                                    {mapping.postgis_type}
                                  </Typography>
                                </TableCell>
                                <TableCell>
                                  {aiAnalysis?.content_analysis?.file_previews?.[selectedHeaderFile]?.sample_rows?.[0]?.[mapping.source_column_index] ? (
                                    <Typography variant="body2" noWrap sx={{ maxWidth: 150 }}>
                                      {aiAnalysis.content_analysis.file_previews[selectedHeaderFile].sample_rows[0][mapping.source_column_index]}
                                    </Typography>
                                  ) : (
                                    <Typography variant="caption" color="textSecondary">
                                      No sample
                                    </Typography>
                                  )}
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                      
                      {/* Mapping Type Information */}
                      <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Mapping Information
                        </Typography>
                        {generatedMappings.mapping_type === 'csv_with_headers' ? (
                          <Typography variant="body2" color="textSecondary">
                            ✓ CSV file contains header row - using actual column names for mapping
                          </Typography>
                        ) : generatedMappings.mapping_type === 'csv_without_headers' ? (
                          <Typography variant="body2" color="textSecondary">
                            ✓ CSV file has no headers - generated field names based on data content analysis
                          </Typography>
                        ) : (
                          <Typography variant="body2" color="textSecondary">
                            ✓ Field mappings generated based on file structure analysis
                          </Typography>
                        )}
                      </Box>
                      
                      {/* Recommendations */}
                      {generatedMappings.recommendations && generatedMappings.recommendations.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>Recommendations</Typography>
                          <List dense>
                            {generatedMappings.recommendations.map((rec, index) => (
                              <ListItem key={index}>
                                <ListItemIcon>
                                  <CheckIcon color="primary" />
                                </ListItemIcon>
                                <ListItemText primary={rec} />
                              </ListItem>
                            ))}
                          </List>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                )}
                
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
                    disabled={loading}
                  >
                    Create Structure
                  </Button>
                </Box>
              </StepContent>
            </Step>
          </Stepper>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setStructureDialog(false);
            setActiveStep(0);
            setAiAnalysis(null);
          }}>
            Cancel
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Field Dialog */}
      <Dialog open={fieldDialog} onClose={() => setFieldDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add Field to {selectedStructure?.name}</DialogTitle>
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

export default DesignSystemEnhanced; 