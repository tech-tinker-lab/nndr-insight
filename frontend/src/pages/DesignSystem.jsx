import React, { useState, useEffect } from 'react';
import axios from 'axios';
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
  Snackbar
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  ArrowForward as ArrowForwardIcon
} from '@mui/icons-material';

const DesignSystem = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [designs, setDesigns] = useState([]);
  const [configs, setConfigs] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [severity, setSeverity] = useState('info');

  // Design Dialog State
  const [designDialogOpen, setDesignDialogOpen] = useState(false);
  const [editingDesign, setEditingDesign] = useState(null);
  const [designForm, setDesignForm] = useState({
    design_name: '',
    table_name: '',
    description: '',
    table_type: 'custom',
    category: 'general',
    columns: []
  });

  // Config Dialog State
  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [editingConfig, setEditingConfig] = useState(null);
  const [configForm, setConfigForm] = useState({
    config_name: '',
    design_id: '',
    source_patterns: [],
    mapping_rules: [],
    priority: 1
  });

  // Column Editor State
  const [columnDialogOpen, setColumnDialogOpen] = useState(false);
  const [editingColumn, setEditingColumn] = useState(null);
  const [columnForm, setColumnForm] = useState({
    name: '',
    type: 'text',
    description: '',
    is_required: false
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [designsRes, configsRes, auditRes] = await Promise.all([
        axios.get('/api/design/tables'),
        axios.get('/api/design/configs'),
        axios.get('/api/design/audit')
      ]);

      setDesigns(designsRes.data.designs || []);
      setConfigs(configsRes.data.configs || []);
      setAuditLogs(auditRes.data.logs || []);
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

  // Design Management
  const openDesignDialog = (design = null) => {
    if (design) {
      setEditingDesign(design);
      setDesignForm({
        design_name: design.design_name,
        table_name: design.table_name,
        description: design.description,
        table_type: design.table_type,
        category: design.category,
        columns: design.columns || []
      });
    } else {
      setEditingDesign(null);
      setDesignForm({
        design_name: '',
        table_name: '',
        description: '',
        table_type: 'custom',
        category: 'general',
        columns: []
      });
    }
    setDesignDialogOpen(true);
  };

  const saveDesign = async () => {
    try {
      if (editingDesign) {
        await axios.put(`/api/design/tables/${editingDesign.design_id}`, designForm);
        showMessage('Design updated successfully', 'success');
      } else {
        await axios.post('/api/design/tables', designForm);
        showMessage('Design created successfully', 'success');
      }
      setDesignDialogOpen(false);
      loadData();
    } catch (error) {
      showMessage('Error saving design: ' + error.message, 'error');
    }
  };

  // Config Management
  const openConfigDialog = (config = null) => {
    if (config) {
      setEditingConfig(config);
      setConfigForm({
        config_name: config.config_name,
        design_id: config.design_id,
        source_patterns: config.source_patterns || [],
        mapping_rules: config.mapping_rules || [],
        priority: config.priority
      });
    } else {
      setEditingConfig(null);
      setConfigForm({
        config_name: '',
        design_id: '',
        source_patterns: [],
        mapping_rules: [],
        priority: 1
      });
    }
    setConfigDialogOpen(true);
  };

  const saveConfig = async () => {
    try {
      if (editingConfig) {
        await axios.put(`/api/design/configs/${editingConfig.config_id}`, configForm);
        showMessage('Configuration updated successfully', 'success');
      } else {
        await axios.post('/api/design/configs', configForm);
        showMessage('Configuration created successfully', 'success');
      }
      setConfigDialogOpen(false);
      loadData();
    } catch (error) {
      showMessage('Error saving configuration: ' + error.message, 'error');
    }
  };

  // Column Management
  const openColumnDialog = (column = null, index = -1) => {
    if (column) {
      setEditingColumn({ ...column, index });
      setColumnForm({
        name: column.name,
        type: column.type,
        description: column.description,
        is_required: column.is_required
      });
    } else {
      setEditingColumn(null);
      setColumnForm({
        name: '',
        type: 'text',
        description: '',
        is_required: false
      });
    }
    setColumnDialogOpen(true);
  };

  const saveColumn = () => {
    const newColumn = { ...columnForm };
    
    if (editingColumn && editingColumn.index >= 0) {
      // Update existing column
      const newColumns = [...designForm.columns];
      newColumns[editingColumn.index] = newColumn;
      setDesignForm({ ...designForm, columns: newColumns });
    } else {
      // Add new column
      setDesignForm({
        ...designForm,
        columns: [...designForm.columns, newColumn]
      });
    }
    
    setColumnDialogOpen(false);
  };

  const deleteColumn = (index) => {
    const newColumns = designForm.columns.filter((_, i) => i !== index);
    setDesignForm({ ...designForm, columns: newColumns });
  };

  const getDataTypeColor = (type) => {
    const colors = {
      text: 'primary',
      integer: 'secondary',
      numeric: 'success',
      boolean: 'warning',
      date: 'info'
    };
    return colors[type] || 'default';
  };

  const renderDesignDialog = () => (
    <Dialog open={designDialogOpen} onClose={() => setDesignDialogOpen(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        {editingDesign ? 'Edit Table Design' : 'Create New Table Design'}
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Design Name"
              value={designForm.design_name}
              onChange={(e) => setDesignForm({ ...designForm, design_name: e.target.value })}
              margin="normal"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Table Name"
              value={designForm.table_name}
              onChange={(e) => setDesignForm({ ...designForm, table_name: e.target.value })}
              margin="normal"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description"
              value={designForm.description}
              onChange={(e) => setDesignForm({ ...designForm, description: e.target.value })}
              margin="normal"
              multiline
              rows={3}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth margin="normal">
              <InputLabel>Table Type</InputLabel>
              <Select
                value={designForm.table_type}
                onChange={(e) => setDesignForm({ ...designForm, table_type: e.target.value })}
              >
                <MenuItem value="custom">Custom</MenuItem>
                <MenuItem value="address">Address</MenuItem>
                <MenuItem value="property">Property</MenuItem>
                <MenuItem value="postcode">Postcode</MenuItem>
                <MenuItem value="boundary">Boundary</MenuItem>
                <MenuItem value="business">Business</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth margin="normal">
              <InputLabel>Category</InputLabel>
              <Select
                value={designForm.category}
                onChange={(e) => setDesignForm({ ...designForm, category: e.target.value })}
              >
                <MenuItem value="general">General</MenuItem>
                <MenuItem value="business">Business</MenuItem>
                <MenuItem value="government">Government</MenuItem>
                <MenuItem value="address">Address</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          {/* Columns Section */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Columns</Typography>
              <Button
                startIcon={<AddIcon />}
                onClick={() => openColumnDialog()}
                variant="outlined"
                size="small"
              >
                Add Column
              </Button>
            </Box>
            
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Required</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {designForm.columns.map((column, index) => (
                    <TableRow key={index}>
                      <TableCell>{column.name}</TableCell>
                      <TableCell>
                        <Chip 
                          label={column.type} 
                          size="small" 
                          color={getDataTypeColor(column.type)}
                        />
                      </TableCell>
                      <TableCell>{column.description}</TableCell>
                      <TableCell>
                        <Chip 
                          label={column.is_required ? 'Yes' : 'No'} 
                          size="small" 
                          color={column.is_required ? 'error' : 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        <IconButton size="small" onClick={() => openColumnDialog(column, index)}>
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" onClick={() => deleteColumn(index)}>
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setDesignDialogOpen(false)}>Cancel</Button>
        <Button onClick={saveDesign} variant="contained" startIcon={<SaveIcon />}>
          Save Design
        </Button>
      </DialogActions>
    </Dialog>
  );

  const renderColumnDialog = () => (
    <Dialog open={columnDialogOpen} onClose={() => setColumnDialogOpen(false)}>
      <DialogTitle>
        {editingColumn ? 'Edit Column' : 'Add Column'}
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Column Name"
              value={columnForm.name}
              onChange={(e) => setColumnForm({ ...columnForm, name: e.target.value })}
              margin="normal"
            />
          </Grid>
          <Grid item xs={12}>
            <FormControl fullWidth margin="normal">
              <InputLabel>Data Type</InputLabel>
              <Select
                value={columnForm.type}
                onChange={(e) => setColumnForm({ ...columnForm, type: e.target.value })}
              >
                <MenuItem value="text">Text</MenuItem>
                <MenuItem value="integer">Integer</MenuItem>
                <MenuItem value="numeric">Numeric</MenuItem>
                <MenuItem value="boolean">Boolean</MenuItem>
                <MenuItem value="date">Date</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description"
              value={columnForm.description}
              onChange={(e) => setColumnForm({ ...columnForm, description: e.target.value })}
              margin="normal"
              multiline
              rows={2}
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={columnForm.is_required}
                  onChange={(e) => setColumnForm({ ...columnForm, is_required: e.target.checked })}
                />
              }
              label="Required Field"
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setColumnDialogOpen(false)}>Cancel</Button>
        <Button onClick={saveColumn} variant="contained">Save Column</Button>
      </DialogActions>
    </Dialog>
  );

  const renderConfigDialog = () => (
    <Dialog open={configDialogOpen} onClose={() => setConfigDialogOpen(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        {editingConfig ? 'Edit Mapping Configuration' : 'Create New Mapping Configuration'}
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Configuration Name"
              value={configForm.config_name}
              onChange={(e) => setConfigForm({ ...configForm, config_name: e.target.value })}
              margin="normal"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth margin="normal">
              <InputLabel>Table Design</InputLabel>
              <Select
                value={configForm.design_id}
                onChange={(e) => setConfigForm({ ...configForm, design_id: e.target.value })}
              >
                {designs.map(design => (
                  <MenuItem key={design.design_id} value={design.design_id}>
                    {design.design_name} ({design.table_name})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Priority"
              type="number"
              value={configForm.priority}
              onChange={(e) => setConfigForm({ ...configForm, priority: parseInt(e.target.value) })}
              margin="normal"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Source Patterns (comma-separated)"
              value={configForm.source_patterns.join(', ')}
              onChange={(e) => setConfigForm({ 
                ...configForm, 
                source_patterns: e.target.value.split(',').map(s => s.trim()).filter(s => s)
              })}
              margin="normal"
              helperText="Patterns to match in file names (e.g., 'address, property, postcode')"
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setConfigDialogOpen(false)}>Cancel</Button>
        <Button onClick={saveConfig} variant="contained" startIcon={<SaveIcon />}>
          Save Configuration
        </Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Design System
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Create and manage table designs and mapping configurations for data uploads
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Table Designs" />
          <Tab label="Mapping Configurations" />
          <Tab label="Audit Logs" />
        </Tabs>
      </Box>

      {/* Table Designs Tab */}
      {activeTab === 0 && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Table Designs</Typography>
              <Button
                startIcon={<AddIcon />}
                onClick={() => openDesignDialog()}
                variant="contained"
              >
                Create Design
              </Button>
            </Box>

            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Design Name</TableCell>
                    <TableCell>Table Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Columns</TableCell>
                    <TableCell>Version</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {designs.map((design) => (
                    <TableRow key={design.design_id}>
                      <TableCell>{design.design_name}</TableCell>
                      <TableCell>{design.table_name}</TableCell>
                      <TableCell>
                        <Chip label={design.table_type} size="small" color="primary" />
                      </TableCell>
                      <TableCell>
                        <Chip label={design.category} size="small" color="secondary" />
                      </TableCell>
                      <TableCell>{design.columns?.length || 0}</TableCell>
                      <TableCell>v{design.version}</TableCell>
                      <TableCell>
                        <IconButton size="small" onClick={() => openDesignDialog(design)}>
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small">
                          <ViewIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Mapping Configurations Tab */}
      {activeTab === 1 && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Mapping Configurations</Typography>
              <Button
                startIcon={<AddIcon />}
                onClick={() => openConfigDialog()}
                variant="contained"
              >
                Create Configuration
              </Button>
            </Box>

            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Configuration Name</TableCell>
                    <TableCell>Table Design</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Patterns</TableCell>
                    <TableCell>Version</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {configs.map((config) => (
                    <TableRow key={config.config_id}>
                      <TableCell>{config.config_name}</TableCell>
                      <TableCell>{config.design_name}</TableCell>
                      <TableCell>
                        <Chip label={config.priority} size="small" color="primary" />
                      </TableCell>
                      <TableCell>
                        {config.source_patterns?.map((pattern, i) => (
                          <Chip key={i} label={pattern} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                        ))}
                      </TableCell>
                      <TableCell>v{config.version}</TableCell>
                      <TableCell>
                        <IconButton size="small" onClick={() => openConfigDialog(config)}>
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small">
                          <ViewIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Audit Logs Tab */}
      {activeTab === 2 && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>Audit Logs</Typography>
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>User</TableCell>
                    <TableCell>Action</TableCell>
                    <TableCell>Resource Type</TableCell>
                    <TableCell>Resource ID</TableCell>
                    <TableCell>Details</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {auditLogs.map((log) => (
                    <TableRow key={log.audit_id}>
                      <TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell>
                      <TableCell>{log.user_id}</TableCell>
                      <TableCell>
                        <Chip label={log.action} size="small" color="primary" />
                      </TableCell>
                      <TableCell>{log.resource_type}</TableCell>
                      <TableCell>{log.resource_id}</TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap>
                          {JSON.stringify(log.details)}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Dialogs */}
      {renderDesignDialog()}
      {renderColumnDialog()}
      {renderConfigDialog()}

      {/* Snackbar for messages */}
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