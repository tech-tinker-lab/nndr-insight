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
  Divider
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  ArrowForward as ArrowForwardIcon,
  ExpandMore as ExpandMoreIcon,
  LocationOn as LocationIcon,
  Code as CodeIcon,
  TableChart as TableIcon
} from '@mui/icons-material';

const DesignSystem = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [structures, setStructures] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [uploads, setUploads] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [severity, setSeverity] = useState('info');

  // Structure Dialog State
  const [structureDialogOpen, setStructureDialogOpen] = useState(false);
  const [editingStructure, setEditingStructure] = useState(null);
  const [structureForm, setStructureForm] = useState({
    dataset_name: '',
    description: '',
    source_type: 'file',
    file_formats: [],
    governing_body: '',
    data_standards: [],
    business_owner: '',
    data_steward: '',
    tags: []
  });

  // Field Dialog State
  const [fieldDialogOpen, setFieldDialogOpen] = useState(false);
  const [editingField, setEditingField] = useState(null);
  const [currentStructureId, setCurrentStructureId] = useState(null);
  const [fieldForm, setFieldForm] = useState({
    field_name: '',
    field_type: 'text',
    postgis_type: '',
    srid: 4326,
    field_length: null,
    field_precision: null,
    field_scale: null,
    is_required: false,
    is_primary_key: false,
    is_unique: false,
    has_index: false,
    default_value: '',
    description: '',
    sequence_order: 1
  });

  // Template Dialog State
  const [templateDialogOpen, setTemplateDialogOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [templateForm, setTemplateForm] = useState({
    template_name: '',
    template_type: 'staging',
    structure_id: '',
    table_name_pattern: '',
    schema_name: 'public',
    include_audit_fields: true,
    include_source_tracking: true,
    include_processing_metadata: true,
    postgis_enabled: false
  });

  // Table Generation State
  const [generationDialogOpen, setGenerationDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [generationForm, setGenerationForm] = useState({
    table_name: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [structuresRes, templatesRes, uploadsRes] = await Promise.all([
        api.get('/api/design-enhanced/structures'),
        api.get('/api/design-enhanced/templates'),
        api.get('/api/design-enhanced/dashboard/overview')
      ]);

      setStructures(structuresRes.data.structures || []);
      setTemplates(templatesRes.data.templates || []);
      setUploads(uploadsRes.data.recent_uploads || []);
    } catch (error) {
      showMessage('Error loading data: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (msg, sev = 'info') => {
    setMessage(msg);
    setSeverity(sev);
  };

  // Structure Management
  const openStructureDialog = (structure = null) => {
    if (structure) {
      setEditingStructure(structure);
      setStructureForm({
        dataset_name: structure.dataset_name,
        description: structure.description,
        source_type: structure.source_type,
        file_formats: structure.file_formats || [],
        governing_body: structure.governing_body,
        data_standards: structure.data_standards || [],
        business_owner: structure.business_owner,
        data_steward: structure.data_steward,
        tags: structure.tags || []
      });
    } else {
      setEditingStructure(null);
      setStructureForm({
        dataset_name: '',
        description: '',
        source_type: 'file',
        file_formats: [],
        governing_body: '',
        data_standards: [],
        business_owner: '',
        data_steward: '',
        tags: []
      });
    }
    setStructureDialogOpen(true);
  };

  const saveStructure = async () => {
    try {
      if (editingStructure) {
        await api.put(`/api/design-enhanced/structures/${editingStructure.structure_id}`, structureForm);
        showMessage('Dataset structure updated successfully', 'success');
      } else {
        await api.post('/api/design-enhanced/structures', structureForm);
        showMessage('Dataset structure created successfully', 'success');
      }
      setStructureDialogOpen(false);
      loadData();
    } catch (error) {
      showMessage('Error saving dataset structure: ' + error.message, 'error');
    }
  };

  // Field Management
  const openFieldDialog = (structureId, field = null) => {
    setCurrentStructureId(structureId);
    if (field) {
      setEditingField(field);
      setFieldForm({
        field_name: field.field_name,
        field_type: field.field_type,
        postgis_type: field.postgis_type || '',
        srid: field.srid || 4326,
        field_length: field.field_length,
        field_precision: field.field_precision,
        field_scale: field.field_scale,
        is_required: field.is_required,
        is_primary_key: field.is_primary_key,
        is_unique: field.is_unique,
        has_index: field.has_index,
        default_value: field.default_value || '',
        description: field.description || '',
        sequence_order: field.sequence_order
      });
    } else {
      setEditingField(null);
      setFieldForm({
        field_name: '',
        field_type: 'text',
        postgis_type: '',
        srid: 4326,
        field_length: null,
        field_precision: null,
        field_scale: null,
        is_required: false,
        is_primary_key: false,
        is_unique: false,
        has_index: false,
        default_value: '',
        description: '',
        sequence_order: 1
      });
    }
    setFieldDialogOpen(true);
  };

  const saveField = async () => {
    try {
      if (editingField) {
        await api.put(`/api/design-enhanced/structures/${currentStructureId}/fields/${editingField.field_id}`, fieldForm);
        showMessage('Field definition updated successfully', 'success');
      } else {
        await api.post(`/api/design-enhanced/structures/${currentStructureId}/fields`, fieldForm);
        showMessage('Field definition created successfully', 'success');
      }
      setFieldDialogOpen(false);
      loadData();
    } catch (error) {
      showMessage('Error saving field definition: ' + error.message, 'error');
    }
  };

  // Template Management
  const openTemplateDialog = (template = null) => {
    if (template) {
      setEditingTemplate(template);
      setTemplateForm({
        template_name: template.template_name,
        template_type: template.template_type,
        structure_id: template.structure_id,
        table_name_pattern: template.table_name_pattern,
        schema_name: template.schema_name,
        include_audit_fields: template.include_audit_fields,
        include_source_tracking: template.include_source_tracking,
        include_processing_metadata: template.include_processing_metadata,
        postgis_enabled: template.postgis_enabled
      });
    } else {
      setEditingTemplate(null);
      setTemplateForm({
        template_name: '',
        template_type: 'staging',
        structure_id: '',
        table_name_pattern: '',
        schema_name: 'public',
        include_audit_fields: true,
        include_source_tracking: true,
        include_processing_metadata: true,
        postgis_enabled: false
      });
    }
    setTemplateDialogOpen(true);
  };

  const saveTemplate = async () => {
    try {
      if (editingTemplate) {
        await api.put(`/api/design-enhanced/templates/${editingTemplate.template_id}`, templateForm);
        showMessage('Table template updated successfully', 'success');
      } else {
        await api.post('/api/design-enhanced/templates', templateForm);
        showMessage('Table template created successfully', 'success');
      }
      setTemplateDialogOpen(false);
      loadData();
    } catch (error) {
      showMessage('Error saving table template: ' + error.message, 'error');
    }
  };

  // Table Generation
  const openGenerationDialog = (template) => {
    setSelectedTemplate(template);
    setGenerationForm({
      table_name: template.table_name_pattern?.replace('{dataset_name}', template.dataset_name) || ''
    });
    setGenerationDialogOpen(true);
  };

  const generateTable = async () => {
    try {
      const response = await api.post(`/api/design-enhanced/templates/${selectedTemplate.template_id}/generate`, generationForm);
      showMessage('Table generated successfully', 'success');
      setGenerationDialogOpen(false);
      // You could show the DDL script in a dialog here
      console.log('Generated DDL:', response.data.ddl_script);
    } catch (error) {
      showMessage('Error generating table: ' + error.message, 'error');
    }
  };

  const getFieldTypeColor = (type) => {
    const colors = {
      'text': '#1976d2',
      'varchar': '#1976d2',
      'integer': '#2e7d32',
      'bigint': '#2e7d32',
      'numeric': '#ed6c02',
      'decimal': '#ed6c02',
      'boolean': '#9c27b0',
      'date': '#d32f2f',
      'timestamp': '#d32f2f',
      'geometry': '#7b1fa2',
      'geography': '#7b1fa2',
      'jsonb': '#f57c00'
    };
    return colors[type] || '#666';
  };

  const renderStructureDialog = () => (
    <Dialog open={structureDialogOpen} onClose={() => setStructureDialogOpen(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        {editingStructure ? 'Edit Dataset Structure' : 'Create Dataset Structure'}
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Dataset Name"
              value={structureForm.dataset_name}
              onChange={(e) => setStructureForm({...structureForm, dataset_name: e.target.value})}
              required
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Source Type</InputLabel>
              <Select
                value={structureForm.source_type}
                onChange={(e) => setStructureForm({...structureForm, source_type: e.target.value})}
                label="Source Type"
              >
                <MenuItem value="file">File</MenuItem>
                <MenuItem value="api">API</MenuItem>
                <MenuItem value="database">Database</MenuItem>
                <MenuItem value="stream">Stream</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Description"
              value={structureForm.description}
              onChange={(e) => setStructureForm({...structureForm, description: e.target.value})}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Governing Body"
              value={structureForm.governing_body}
              onChange={(e) => setStructureForm({...structureForm, governing_body: e.target.value})}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Business Owner"
              value={structureForm.business_owner}
              onChange={(e) => setStructureForm({...structureForm, business_owner: e.target.value})}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Data Steward"
              value={structureForm.data_steward}
              onChange={(e) => setStructureForm({...structureForm, data_steward: e.target.value})}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setStructureDialogOpen(false)}>Cancel</Button>
        <Button onClick={saveStructure} variant="contained" startIcon={<SaveIcon />}>
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );

  const renderFieldDialog = () => (
    <Dialog open={fieldDialogOpen} onClose={() => setFieldDialogOpen(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        {editingField ? 'Edit Field Definition' : 'Create Field Definition'}
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Field Name"
              value={fieldForm.field_name}
              onChange={(e) => setFieldForm({...fieldForm, field_name: e.target.value})}
              required
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Field Type</InputLabel>
              <Select
                value={fieldForm.field_type}
                onChange={(e) => setFieldForm({...fieldForm, field_type: e.target.value})}
                label="Field Type"
              >
                <MenuItem value="text">Text</MenuItem>
                <MenuItem value="varchar">VARCHAR</MenuItem>
                <MenuItem value="integer">Integer</MenuItem>
                <MenuItem value="bigint">BigInt</MenuItem>
                <MenuItem value="numeric">Numeric</MenuItem>
                <MenuItem value="decimal">Decimal</MenuItem>
                <MenuItem value="boolean">Boolean</MenuItem>
                <MenuItem value="date">Date</MenuItem>
                <MenuItem value="timestamp">Timestamp</MenuItem>
                <MenuItem value="geometry">Geometry</MenuItem>
                <MenuItem value="geography">Geography</MenuItem>
                <MenuItem value="jsonb">JSONB</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          {fieldForm.field_type === 'geometry' && (
            <>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>PostGIS Type</InputLabel>
                  <Select
                    value={fieldForm.postgis_type}
                    onChange={(e) => setFieldForm({...fieldForm, postgis_type: e.target.value})}
                    label="PostGIS Type"
                  >
                    <MenuItem value="POINT">POINT</MenuItem>
                    <MenuItem value="LINESTRING">LINESTRING</MenuItem>
                    <MenuItem value="POLYGON">POLYGON</MenuItem>
                    <MenuItem value="MULTIPOINT">MULTIPOINT</MenuItem>
                    <MenuItem value="MULTILINESTRING">MULTILINESTRING</MenuItem>
                    <MenuItem value="MULTIPOLYGON">MULTIPOLYGON</MenuItem>
                    <MenuItem value="GEOMETRYCOLLECTION">GEOMETRYCOLLECTION</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="SRID"
                  value={fieldForm.srid}
                  onChange={(e) => setFieldForm({...fieldForm, srid: parseInt(e.target.value)})}
                />
              </Grid>
            </>
          )}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Sequence Order"
              value={fieldForm.sequence_order}
              onChange={(e) => setFieldForm({...fieldForm, sequence_order: parseInt(e.target.value)})}
              required
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Description"
              value={fieldForm.description}
              onChange={(e) => setFieldForm({...fieldForm, description: e.target.value})}
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={fieldForm.is_required}
                  onChange={(e) => setFieldForm({...fieldForm, is_required: e.target.checked})}
                />
              }
              label="Required"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={fieldForm.is_primary_key}
                  onChange={(e) => setFieldForm({...fieldForm, is_primary_key: e.target.checked})}
                />
              }
              label="Primary Key"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={fieldForm.is_unique}
                  onChange={(e) => setFieldForm({...fieldForm, is_unique: e.target.checked})}
                />
              }
              label="Unique"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={fieldForm.has_index}
                  onChange={(e) => setFieldForm({...fieldForm, has_index: e.target.checked})}
                />
              }
              label="Has Index"
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setFieldDialogOpen(false)}>Cancel</Button>
        <Button onClick={saveField} variant="contained" startIcon={<SaveIcon />}>
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );

  const renderTemplateDialog = () => (
    <Dialog open={templateDialogOpen} onClose={() => setTemplateDialogOpen(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        {editingTemplate ? 'Edit Table Template' : 'Create Table Template'}
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Template Name"
              value={templateForm.template_name}
              onChange={(e) => setTemplateForm({...templateForm, template_name: e.target.value})}
              required
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Template Type</InputLabel>
              <Select
                value={templateForm.template_type}
                onChange={(e) => setTemplateForm({...templateForm, template_type: e.target.value})}
                label="Template Type"
              >
                <MenuItem value="staging">Staging</MenuItem>
                <MenuItem value="master">Master</MenuItem>
                <MenuItem value="intermediate">Intermediate</MenuItem>
                <MenuItem value="archive">Archive</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Dataset Structure</InputLabel>
              <Select
                value={templateForm.structure_id}
                onChange={(e) => setTemplateForm({...templateForm, structure_id: e.target.value})}
                label="Dataset Structure"
                required
              >
                {structures.map((structure) => (
                  <MenuItem key={structure.structure_id} value={structure.structure_id}>
                    {structure.dataset_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Table Name Pattern"
              value={templateForm.table_name_pattern}
              onChange={(e) => setTemplateForm({...templateForm, table_name_pattern: e.target.value})}
              placeholder="{dataset_name}_staging"
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={templateForm.include_audit_fields}
                  onChange={(e) => setTemplateForm({...templateForm, include_audit_fields: e.target.checked})}
                />
              }
              label="Include Audit Fields"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={templateForm.include_source_tracking}
                  onChange={(e) => setTemplateForm({...templateForm, include_source_tracking: e.target.checked})}
                />
              }
              label="Include Source Tracking"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={templateForm.include_processing_metadata}
                  onChange={(e) => setTemplateForm({...templateForm, include_processing_metadata: e.target.checked})}
                />
              }
              label="Include Processing Metadata"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={templateForm.postgis_enabled}
                  onChange={(e) => setTemplateForm({...templateForm, postgis_enabled: e.target.checked})}
                />
              }
              label="PostGIS Enabled"
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setTemplateDialogOpen(false)}>Cancel</Button>
        <Button onClick={saveTemplate} variant="contained" startIcon={<SaveIcon />}>
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );

  const renderGenerationDialog = () => (
    <Dialog open={generationDialogOpen} onClose={() => setGenerationDialogOpen(false)} maxWidth="sm" fullWidth>
      <DialogTitle>Generate Table from Template</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Table Name"
              value={generationForm.table_name}
              onChange={(e) => setGenerationForm({...generationForm, table_name: e.target.value})}
              required
            />
          </Grid>
          {selectedTemplate && (
            <Grid item xs={12}>
              <Typography variant="body2" color="textSecondary">
                Template: {selectedTemplate.template_name}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Type: {selectedTemplate.template_type}
              </Typography>
            </Grid>
          )}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setGenerationDialogOpen(false)}>Cancel</Button>
        <Button onClick={generateTable} variant="contained" startIcon={<TableIcon />}>
          Generate Table
        </Button>
      </DialogActions>
    </Dialog>
  );

  const renderStructuresTab = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Dataset Structures</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => openStructureDialog()}
        >
          Create Structure
        </Button>
      </Box>
      
      <Grid container spacing={2}>
        {structures.map((structure) => (
          <Grid item xs={12} md={6} key={structure.structure_id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="h6">{structure.dataset_name}</Typography>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      {structure.description}
                    </Typography>
                    <Chip 
                      label={structure.source_type} 
                      size="small" 
                      sx={{ mr: 1 }}
                    />
                    <Chip 
                      label={structure.status} 
                      size="small" 
                      color={structure.status === 'active' ? 'success' : 'default'}
                    />
                  </Box>
                  <Box>
                    <IconButton size="small" onClick={() => openStructureDialog(structure)}>
                      <EditIcon />
                    </IconButton>
                  </Box>
                </Box>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle2" gutterBottom>Details:</Typography>
                <Typography variant="body2" color="textSecondary">
                  Governing Body: {structure.governing_body || 'N/A'}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Business Owner: {structure.business_owner || 'N/A'}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Data Steward: {structure.data_steward || 'N/A'}
                </Typography>
                
                <Box sx={{ mt: 2 }}>
                  <Button
                    size="small"
                    startIcon={<AddIcon />}
                    onClick={() => openFieldDialog(structure.structure_id)}
                  >
                    Add Field
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  const renderTemplatesTab = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Table Templates</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => openTemplateDialog()}
        >
          Create Template
        </Button>
      </Box>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Template Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Dataset</TableCell>
              <TableCell>PostGIS</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {templates.map((template) => (
              <TableRow key={template.template_id}>
                <TableCell>{template.template_name}</TableCell>
                <TableCell>
                  <Chip label={template.template_type} size="small" />
                </TableCell>
                <TableCell>{template.dataset_name}</TableCell>
                <TableCell>
                  {template.postgis_enabled ? (
                    <Chip label="Enabled" size="small" color="success" />
                  ) : (
                    <Chip label="Disabled" size="small" />
                  )}
                </TableCell>
                <TableCell>
                  <IconButton size="small" onClick={() => openTemplateDialog(template)}>
                    <EditIcon />
                  </IconButton>
                  <IconButton size="small" onClick={() => openGenerationDialog(template)}>
                    <TableIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderUploadsTab = () => (
    <Box>
      <Typography variant="h6" gutterBottom>Recent Uploads</Typography>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>File Name</TableCell>
              <TableCell>Dataset</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Uploaded By</TableCell>
              <TableCell>Upload Date</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {uploads.map((upload) => (
              <TableRow key={upload.upload_id}>
                <TableCell>{upload.file_name}</TableCell>
                <TableCell>{upload.dataset_name}</TableCell>
                <TableCell>
                  <Chip 
                    label={upload.processing_status} 
                    size="small" 
                    color={upload.processing_status === 'completed' ? 'success' : 'default'}
                  />
                </TableCell>
                <TableCell>{upload.uploaded_by}</TableCell>
                <TableCell>{new Date(upload.uploaded_at).toLocaleDateString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Dataset Structure System
      </Typography>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Dataset Structures" />
          <Tab label="Table Templates" />
          <Tab label="Recent Uploads" />
        </Tabs>
      </Box>

      {activeTab === 0 && renderStructuresTab()}
      {activeTab === 1 && renderTemplatesTab()}
      {activeTab === 2 && renderUploadsTab()}

      {renderStructureDialog()}
      {renderFieldDialog()}
      {renderTemplateDialog()}
      {renderGenerationDialog()}

      <Snackbar
        open={!!message}
        autoHideDuration={6000}
        onClose={() => setMessage('')}
      >
        <Alert onClose={() => setMessage('')} severity={severity} sx={{ width: '100%' }}>
          {message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default DesignSystem; 