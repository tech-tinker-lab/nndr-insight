import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  Upload as UploadIcon,
  Transform as TransformIcon,
  Storage as StorageIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  ExpandMore as ExpandMoreIcon,
  DataObject as DataObjectIcon,
  TableChart as TableChartIcon,
  Settings as SettingsIcon,
  Download as DownloadIcon
} from '@mui/icons-material';
import api from '../api/axios';

const SimpleETLManager = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [severity, setSeverity] = useState('info');

  // ETL State
  const [sourceFile, setSourceFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);
  const [columnMapping, setColumnMapping] = useState({});
  const [targetTable, setTargetTable] = useState('');
  const [transformationRules, setTransformationRules] = useState([]);
  const [etlStatus, setEtlStatus] = useState('idle'); // idle, running, completed, failed
  const [etlResults, setEtlResults] = useState(null);

  // Available tables and transformations
  const [availableTables, setAvailableTables] = useState([]);
  const [availableTransformations, setAvailableTransformations] = useState([
    { id: 'uppercase', name: 'Convert to Uppercase', description: 'Convert text to uppercase' },
    { id: 'lowercase', name: 'Convert to Lowercase', description: 'Convert text to lowercase' },
    { id: 'trim', name: 'Trim Whitespace', description: 'Remove leading and trailing spaces' },
    { id: 'number_format', name: 'Format Number', description: 'Format numeric values' },
    { id: 'date_format', name: 'Format Date', description: 'Convert date formats' },
    { id: 'postcode_clean', name: 'Clean Postcode', description: 'Standardize UK postcode format' },
    { id: 'coordinate_validate', name: 'Validate Coordinates', description: 'Validate and convert coordinates' }
  ]);

  const steps = [
    {
      label: 'Upload Data',
      description: 'Select and upload your data file',
      icon: <UploadIcon />
    },
    {
      label: 'Preview & Map',
      description: 'Preview data and map columns',
      icon: <TableChartIcon />
    },
    {
      label: 'Transform',
      description: 'Apply data transformations',
      icon: <TransformIcon />
    },
    {
      label: 'Load',
      description: 'Load data into target table',
      icon: <StorageIcon />
    }
  ];

  useEffect(() => {
    loadAvailableTables();
  }, []);

  const loadAvailableTables = async () => {
    try {
      const response = await api.get('/api/tables');
      setAvailableTables(response.data.tables || []);
    } catch (error) {
      console.error('Error loading tables:', error);
    }
  };

  const showMessage = (msg, sev = 'info') => {
    setMessage(msg);
    setSeverity(sev);
    setTimeout(() => setMessage(''), 5000);
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setSourceFile(file);
    setLoading(true);

    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', file);

      // Upload file for preview
      const response = await api.post('/api/upload/preview', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.success) {
        setFilePreview(response.data.preview);
        setActiveStep(1);
        showMessage('File uploaded successfully!', 'success');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      showMessage('Failed to upload file: ' + (error.response?.data?.detail || error.message), 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleColumnMapping = (sourceColumn, targetColumn) => {
    setColumnMapping(prev => ({
      ...prev,
      [sourceColumn]: targetColumn
    }));
  };

  const addTransformationRule = () => {
    const newRule = {
      id: Date.now(),
      column: '',
      transformation: '',
      parameters: {}
    };
    setTransformationRules(prev => [...prev, newRule]);
  };

  const updateTransformationRule = (id, field, value) => {
    setTransformationRules(prev => 
      prev.map(rule => 
        rule.id === id ? { ...rule, [field]: value } : rule
      )
    );
  };

  const removeTransformationRule = (id) => {
    setTransformationRules(prev => prev.filter(rule => rule.id !== id));
  };

  const handleRunETL = async () => {
    if (!sourceFile || !targetTable) {
      showMessage('Please select a file and target table', 'warning');
      return;
    }

    setLoading(true);
    setEtlStatus('running');

    try {
      const etlConfig = {
        source_file: sourceFile.name,
        target_table: targetTable,
        column_mapping: columnMapping,
        transformations: transformationRules,
        parameters: {
          batch_size: 10000,
          skip_duplicates: true,
          validate_data: true
        }
      };

      const response = await api.post('/api/etl/run', etlConfig);

      if (response.data.success) {
        setEtlResults(response.data.results);
        setEtlStatus('completed');
        setActiveStep(3);
        showMessage('ETL process completed successfully!', 'success');
      }
    } catch (error) {
      console.error('Error running ETL:', error);
      setEtlStatus('failed');
      showMessage('ETL process failed: ' + (error.response?.data?.detail || error.message), 'error');
    } finally {
      setLoading(false);
    }
  };

  const renderFileUpload = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>
          Step 1: Upload Your Data File
        </Typography>
        
        <Box display="flex" flexDirection="column" alignItems="center" p={3}>
          <input
            accept=".csv,.xlsx,.json,.xml"
            style={{ display: 'none' }}
            id="file-upload"
            type="file"
            onChange={handleFileUpload}
          />
          <label htmlFor="file-upload">
            <Button
              variant="contained"
              component="span"
              startIcon={<UploadIcon />}
              size="large"
              disabled={loading}
            >
              {loading ? <CircularProgress size={20} /> : 'Choose File'}
            </Button>
          </label>
          
          <Typography variant="body2" color="text.secondary" mt={2}>
            Supported formats: CSV, Excel, JSON, XML
          </Typography>
          
          {sourceFile && (
            <Box mt={2}>
              <Chip 
                label={sourceFile.name} 
                color="primary" 
                onDelete={() => setSourceFile(null)}
              />
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );

  const renderColumnMapping = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>
          Step 2: Map Columns to Target Table
        </Typography>
        
        {filePreview && (
          <Box mb={3}>
            <Typography variant="subtitle1" mb={1}>File Preview (first 5 rows):</Typography>
            <TableContainer component={Paper} sx={{ maxHeight: 300 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    {filePreview.columns.map(column => (
                      <TableCell key={column}>{column}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filePreview.data.slice(0, 5).map((row, index) => (
                    <TableRow key={index}>
                      {filePreview.columns.map(column => (
                        <TableCell key={column}>{row[column]}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}
        
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Target Table</InputLabel>
              <Select
                value={targetTable}
                onChange={(e) => setTargetTable(e.target.value)}
              >
                {availableTables.map(table => (
                  <MenuItem key={table} value={table}>{table}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
        
        {filePreview && (
          <Box mt={3}>
            <Typography variant="subtitle1" mb={2}>Column Mapping:</Typography>
            <Grid container spacing={2}>
              {filePreview.columns.map(sourceColumn => (
                <Grid item xs={12} md={6} key={sourceColumn}>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Typography variant="body2" sx={{ minWidth: 120 }}>
                      {sourceColumn} →
                    </Typography>
                    <FormControl fullWidth size="small">
                      <Select
                        value={columnMapping[sourceColumn] || ''}
                        onChange={(e) => handleColumnMapping(sourceColumn, e.target.value)}
                      >
                        <MenuItem value="">Skip this column</MenuItem>
                        {availableTables.length > 0 && availableTables.map(table => (
                          <MenuItem key={table} value={table}>{table}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
        
        <Box mt={3} display="flex" justifyContent="space-between">
          <Button onClick={() => setActiveStep(0)}>Back</Button>
          <Button 
            variant="contained" 
            onClick={() => setActiveStep(2)}
            disabled={!targetTable}
          >
            Next: Transform
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  const renderTransformations = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>
          Step 3: Apply Data Transformations
        </Typography>
        
        <Box mb={3}>
          <Button
            variant="outlined"
            startIcon={<TransformIcon />}
            onClick={addTransformationRule}
          >
            Add Transformation Rule
          </Button>
        </Box>
        
        {transformationRules.length === 0 ? (
          <Alert severity="info">
            No transformation rules added. Your data will be loaded as-is.
          </Alert>
        ) : (
          <List>
            {transformationRules.map((rule, index) => (
              <ListItem key={rule.id} divider>
                <ListItemIcon>
                  <TransformIcon />
                </ListItemIcon>
                <ListItemText
                  primary={`Rule ${index + 1}`}
                  secondary={
                    <Grid container spacing={2} alignItems="center">
                      <Grid item xs={12} md={3}>
                        <FormControl fullWidth size="small">
                          <InputLabel>Column</InputLabel>
                          <Select
                            value={rule.column}
                            onChange={(e) => updateTransformationRule(rule.id, 'column', e.target.value)}
                          >
                            {filePreview?.columns.map(col => (
                              <MenuItem key={col} value={col}>{col}</MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <FormControl fullWidth size="small">
                          <InputLabel>Transformation</InputLabel>
                          <Select
                            value={rule.transformation}
                            onChange={(e) => updateTransformationRule(rule.id, 'transformation', e.target.value)}
                          >
                            {availableTransformations.map(trans => (
                              <MenuItem key={trans.id} value={trans.id}>
                                {trans.name}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <IconButton
                          color="error"
                          onClick={() => removeTransformationRule(rule.id)}
                        >
                          <ErrorIcon />
                        </IconButton>
                      </Grid>
                    </Grid>
                  }
                />
              </ListItem>
            ))}
          </List>
        )}
        
        <Box mt={3} display="flex" justifyContent="space-between">
          <Button onClick={() => setActiveStep(1)}>Back</Button>
          <Button 
            variant="contained" 
            onClick={() => setActiveStep(3)}
          >
            Next: Load Data
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  const renderDataLoad = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>
          Step 4: Load Data into Database
        </Typography>
        
        <Box mb={3}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary">
                    Source File
                  </Typography>
                  <Typography variant="h6">{sourceFile?.name}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary">
                    Target Table
                  </Typography>
                  <Typography variant="h6">{targetTable}</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
        
        <Box mb={3}>
          <Typography variant="subtitle1" mb={1}>ETL Configuration Summary:</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon>
                <TableChartIcon />
              </ListItemIcon>
              <ListItemText 
                primary="Column Mappings" 
                secondary={`${Object.keys(columnMapping).length} columns mapped`}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <TransformIcon />
              </ListItemIcon>
              <ListItemText 
                primary="Transformations" 
                secondary={`${transformationRules.length} rules applied`}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <StorageIcon />
              </ListItemIcon>
              <ListItemText 
                primary="Target" 
                secondary={`Loading into ${targetTable} table`}
              />
            </ListItem>
          </List>
        </Box>
        
        {etlStatus === 'completed' && etlResults && (
          <Alert severity="success" sx={{ mb: 2 }}>
            <Typography variant="h6">ETL Completed Successfully!</Typography>
            <Typography variant="body2">
              Records processed: {etlResults.records_processed}<br/>
              Records loaded: {etlResults.records_loaded}<br/>
              Errors: {etlResults.errors}<br/>
              Processing time: {etlResults.processing_time}s
            </Typography>
          </Alert>
        )}
        
        {etlStatus === 'failed' && (
          <Alert severity="error" sx={{ mb: 2 }}>
            ETL process failed. Please check the configuration and try again.
          </Alert>
        )}
        
        <Box display="flex" justifyContent="space-between">
          <Button onClick={() => setActiveStep(2)}>Back</Button>
          <Button 
            variant="contained" 
            startIcon={loading ? <CircularProgress size={20} /> : <PlayIcon />}
            onClick={handleRunETL}
            disabled={loading || etlStatus === 'running'}
          >
            {etlStatus === 'running' ? 'Running ETL...' : 'Run ETL Process'}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" mb={3}>
        Simple ETL Manager
      </Typography>

      {message && (
        <Alert severity={severity} sx={{ mb: 2 }}>
          {message}
        </Alert>
      )}

      <Stepper activeStep={activeStep} orientation="vertical" sx={{ mb: 3 }}>
        {steps.map((step, index) => (
          <Step key={step.label}>
            <StepLabel icon={step.icon}>
              {step.label}
            </StepLabel>
            <StepContent>
              <Typography variant="body2" color="text.secondary">
                {step.description}
              </Typography>
            </StepContent>
          </Step>
        ))}
      </Stepper>

      <Box>
        {activeStep === 0 && renderFileUpload()}
        {activeStep === 1 && renderColumnMapping()}
        {activeStep === 2 && renderTransformations()}
        {activeStep === 3 && renderDataLoad()}
      </Box>
    </Box>
  );
};

export default SimpleETLManager; 