import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
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
  Chip,
  IconButton,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Snackbar,
  CircularProgress,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Add as AddIcon,
  Upload as UploadIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  ExpandMore as ExpandMoreIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayArrowIcon,
  Pause as PauseIcon,
  Refresh as RefreshIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  Security as SecurityIcon
} from '@mui/icons-material';
import api from '../api/axios';
import { useUser } from '../context/UserContext';

const API_BASE_URL = 'http://localhost:8000/api';

const DatasetPipeline = () => {
  const { user } = useUser();
  const [datasets, setDatasets] = useState([]);
  const [uploads, setUploads] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Dialog states
  const [createDatasetDialog, setCreateDatasetDialog] = useState(false);
  const [uploadFileDialog, setUploadFileDialog] = useState(false);
  const [approvalDialog, setApprovalDialog] = useState(false);
  const [pipelineDialog, setPipelineDialog] = useState(false);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [selectedUpload, setSelectedUpload] = useState(null);
  
  // Form states
  const [newDataset, setNewDataset] = useState({
    dataset_name: '',
    description: '',
    source_type: 'file',
    business_owner: '',
    data_steward: ''
  });
  
  const [newUpload, setNewUpload] = useState({
    file_name: '',
    file_size: 0,
    file_type: '',
    file_path: ''
  });
  
  const [approvalData, setApprovalData] = useState({
    approval_notes: '',
    next_stage: ''
  });

  useEffect(() => {
    fetchDatasets();
    fetchUploads();
  }, []);

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      const response = await api.get(`${API_BASE_URL}/design/datasets`);
      setDatasets(response.data.datasets || []);
    } catch (err) {
      setError('Failed to fetch datasets');
      console.error('Error fetching datasets:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUploads = async () => {
    try {
      const response = await api.get(`${API_BASE_URL}/design/uploads`);
      setUploads(response.data.uploads || []);
    } catch (err) {
      setError('Failed to fetch uploads');
      console.error('Error fetching uploads:', err);
    }
  };

  const handleCreateDataset = async () => {
    try {
      setLoading(true);
      const response = await api.post(`${API_BASE_URL}/design/datasets`, newDataset);
      setSuccess('Dataset created successfully');
      setCreateDatasetDialog(false);
      setNewDataset({
        dataset_name: '',
        description: '',
        source_type: 'file',
        business_owner: '',
        data_steward: ''
      });
      fetchDatasets();
    } catch (err) {
      setError('Failed to create dataset');
      console.error('Error creating dataset:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadFile = async () => {
    try {
      setLoading(true);
      const response = await api.post(`${API_BASE_URL}/design/datasets/${selectedDataset.dataset_id}/upload`, newUpload);
      setSuccess('File uploaded successfully');
      setUploadFileDialog(false);
      setNewUpload({
        file_name: '',
        file_size: 0,
        file_type: '',
        file_path: ''
      });
      fetchUploads();
    } catch (err) {
      setError('Failed to upload file');
      console.error('Error uploading file:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveUpload = async () => {
    try {
      setLoading(true);
      const response = await api.post(`${API_BASE_URL}/design/uploads/${selectedUpload.upload_id}/approve`, approvalData);
      setSuccess('Upload approved successfully');
      setApprovalDialog(false);
      setApprovalData({
        approval_notes: '',
        next_stage: ''
      });
      fetchUploads();
    } catch (err) {
      setError('Failed to approve upload');
      console.error('Error approving upload:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'warning';
      case 'approved': return 'info';
      case 'rejected': return 'error';
      case 'uploaded': return 'default';
      default: return 'default';
    }
  };

  const getStageColor = (stage) => {
    switch (stage) {
      case 'upload': return 'primary';
      case 'staging': return 'secondary';
      case 'filtered': return 'warning';
      case 'final': return 'success';
      default: return 'default';
    }
  };

  const canApprove = (upload) => {
    if (!user) return false;
    if (user.role === 'admin') return true;
    if (user.role === 'power_user' && upload.status === 'uploaded') return true;
    return false;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dataset Pipeline Management
      </Typography>
      
      <Grid container spacing={3}>
        {/* Datasets Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Datasets</Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setCreateDatasetDialog(true)}
              >
                Create Dataset
              </Button>
            </Box>
            
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : (
              <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
                {datasets.map((dataset) => (
                  <Card key={dataset.dataset_id} sx={{ mb: 2 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Box>
                          <Typography variant="h6">{dataset.dataset_name}</Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                            {dataset.description}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                            <Chip 
                              label={dataset.source_type} 
                              size="small" 
                              color="primary" 
                              variant="outlined" 
                            />
                            <Chip 
                              label={dataset.status} 
                              size="small" 
                              color={dataset.status === 'active' ? 'success' : 'default'} 
                            />
                          </Box>
                          <Typography variant="caption" display="block">
                            Owner: {dataset.business_owner} | Steward: {dataset.data_steward}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedDataset(dataset);
                              setPipelineDialog(true);
                            }}
                          >
                            <TimelineIcon />
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedDataset(dataset);
                              setUploadFileDialog(true);
                            }}
                          >
                            <UploadIcon />
                          </IconButton>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Uploads Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Recent Uploads</Typography>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={fetchUploads}
              >
                Refresh
              </Button>
            </Box>
            
            <TableContainer sx={{ maxHeight: 400 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>File</TableCell>
                    <TableCell>Dataset</TableCell>
                    <TableCell>Stage</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {uploads.slice(0, 10).map((upload) => (
                    <TableRow key={upload.upload_id}>
                      <TableCell>
                        <Typography variant="body2" noWrap>
                          {upload.file_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(upload.uploaded_at).toLocaleDateString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {datasets.find(d => d.dataset_id === upload.dataset_id)?.dataset_name || 'Unknown'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={upload.current_stage} 
                          size="small" 
                          color={getStageColor(upload.current_stage)}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={upload.status} 
                          size="small" 
                          color={getStatusColor(upload.status)}
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          {canApprove(upload) && (
                            <IconButton
                              size="small"
                              color="success"
                              onClick={() => {
                                setSelectedUpload(upload);
                                setApprovalDialog(true);
                              }}
                            >
                              <CheckCircleIcon />
                            </IconButton>
                          )}
                          <IconButton size="small">
                            <VisibilityIcon />
                          </IconButton>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Pipeline Overview */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Pipeline Overview
            </Typography>
            <Stepper orientation="horizontal" sx={{ mt: 2 }}>
              <Step>
                <StepLabel>Upload</StepLabel>
              </Step>
              <Step>
                <StepLabel>Staging</StepLabel>
              </Step>
              <Step>
                <StepLabel>Filtered</StepLabel>
              </Step>
              <Step>
                <StepLabel>Final</StepLabel>
              </Step>
            </Stepper>
          </Paper>
        </Grid>
      </Grid>

      {/* Create Dataset Dialog */}
      <Dialog open={createDatasetDialog} onClose={() => setCreateDatasetDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Dataset</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Dataset Name"
                value={newDataset.dataset_name}
                onChange={(e) => setNewDataset({ ...newDataset, dataset_name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={newDataset.description}
                onChange={(e) => setNewDataset({ ...newDataset, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Source Type</InputLabel>
                <Select
                  value={newDataset.source_type}
                  onChange={(e) => setNewDataset({ ...newDataset, source_type: e.target.value })}
                >
                  <MenuItem value="file">File</MenuItem>
                  <MenuItem value="api">API</MenuItem>
                  <MenuItem value="database">Database</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Business Owner"
                value={newDataset.business_owner}
                onChange={(e) => setNewDataset({ ...newDataset, business_owner: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Data Steward"
                value={newDataset.data_steward}
                onChange={(e) => setNewDataset({ ...newDataset, data_steward: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDatasetDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateDataset} 
            variant="contained" 
            disabled={!newDataset.dataset_name || loading}
          >
            Create Dataset
          </Button>
        </DialogActions>
      </Dialog>

      {/* Upload File Dialog */}
      <Dialog open={uploadFileDialog} onClose={() => setUploadFileDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload File to Dataset</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Dataset: {selectedDataset?.dataset_name}
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="File Name"
                value={newUpload.file_name}
                onChange={(e) => setNewUpload({ ...newUpload, file_name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="File Size (bytes)"
                type="number"
                value={newUpload.file_size}
                onChange={(e) => setNewUpload({ ...newUpload, file_size: parseInt(e.target.value) })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="File Type"
                value={newUpload.file_type}
                onChange={(e) => setNewUpload({ ...newUpload, file_type: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="File Path"
                value={newUpload.file_path}
                onChange={(e) => setNewUpload({ ...newUpload, file_path: e.target.value })}
                required
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadFileDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleUploadFile} 
            variant="contained" 
            disabled={!newUpload.file_name || !newUpload.file_path || loading}
          >
            Upload File
          </Button>
        </DialogActions>
      </Dialog>

      {/* Approval Dialog */}
      <Dialog open={approvalDialog} onClose={() => setApprovalDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Approve Upload</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            File: {selectedUpload?.file_name}
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Next Stage</InputLabel>
                <Select
                  value={approvalData.next_stage}
                  onChange={(e) => setApprovalData({ ...approvalData, next_stage: e.target.value })}
                >
                  <MenuItem value="staging">Staging</MenuItem>
                  <MenuItem value="filtered">Filtered</MenuItem>
                  <MenuItem value="final">Final</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Approval Notes"
                multiline
                rows={3}
                value={approvalData.approval_notes}
                onChange={(e) => setApprovalData({ ...approvalData, approval_notes: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApprovalDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleApproveUpload} 
            variant="contained" 
            color="success"
            disabled={!approvalData.next_stage || loading}
          >
            Approve
          </Button>
        </DialogActions>
      </Dialog>

      {/* Pipeline Management Dialog */}
      <Dialog open={pipelineDialog} onClose={() => setPipelineDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Pipeline Management</DialogTitle>
        <DialogContent>
          <Typography variant="h6" gutterBottom>
            {selectedDataset?.dataset_name} Pipeline
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Configure pipeline stages and validation rules
          </Typography>
          {/* Pipeline configuration UI would go here */}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPipelineDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Notifications */}
      <Snackbar open={!!error} autoHideDuration={6000} onClose={() => setError(null)}>
        <Alert onClose={() => setError(null)} severity="error">
          {error}
        </Alert>
      </Snackbar>
      
      <Snackbar open={!!success} autoHideDuration={6000} onClose={() => setSuccess(null)}>
        <Alert onClose={() => setSuccess(null)} severity="success">
          {success}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DatasetPipeline; 