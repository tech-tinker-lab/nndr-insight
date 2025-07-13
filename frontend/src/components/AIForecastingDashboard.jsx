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
  Tabs,
  Tab,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  ExpandMore as ExpandMoreIcon,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import api from '../api/axios';

const AIForecastingDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [anomalyData, setAnomalyData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [severity, setSeverity] = useState('info');
  const [showTrainingDialog, setShowTrainingDialog] = useState(false);
  const [showForecastDialog, setShowForecastDialog] = useState(false);
  const [showExplainDialog, setShowExplainDialog] = useState(false);
  const [performanceMetrics, setPerformanceMetrics] = useState(null);

  // Training form state
  const [trainingForm, setTrainingForm] = useState({
    dataSource: '',
    targetColumn: 'rateable_value',
    modelType: 'prophet',
    forecastPeriods: 12,
    parameters: {}
  });

  // Forecast form state
  const [forecastForm, setForecastForm] = useState({
    modelId: '',
    periods: 12,
    confidenceLevel: 'medium'
  });

  useEffect(() => {
    loadModels();
    loadPerformanceMetrics();
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/ai-enhanced/models');
      setModels(response.data.models || []);
    } catch (error) {
      console.error('Error loading models:', error);
      showMessage('Failed to load models', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadPerformanceMetrics = async () => {
    try {
      const response = await api.get('/api/ai-enhanced/performance/metrics');
      setPerformanceMetrics(response.data.overall_metrics);
    } catch (error) {
      console.error('Error loading performance metrics:', error);
    }
  };

  const showMessage = (msg, sev = 'info') => {
    setMessage(msg);
    setSeverity(sev);
    setTimeout(() => setMessage(''), 5000);
  };

  const handleTrainModel = async () => {
    try {
      setLoading(true);
      const response = await api.post('/api/ai-enhanced/forecast/train', trainingForm);
      
      if (response.data.success) {
        showMessage('Model trained successfully!', 'success');
        setShowTrainingDialog(false);
        loadModels();
        loadPerformanceMetrics();
      }
    } catch (error) {
      console.error('Error training model:', error);
      showMessage('Failed to train model: ' + (error.response?.data?.detail || error.message), 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateForecast = async () => {
    try {
      setLoading(true);
      const response = await api.post('/api/ai-enhanced/forecast/generate', forecastForm);
      
      if (response.data.success) {
        setForecastData(response.data.forecast);
        setShowForecastDialog(false);
        showMessage('Forecast generated successfully!', 'success');
      }
    } catch (error) {
      console.error('Error generating forecast:', error);
      showMessage('Failed to generate forecast: ' + (error.response?.data?.detail || error.message), 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDetectAnomalies = async (dataSource) => {
    try {
      setLoading(true);
      const response = await api.post('/api/ai-enhanced/anomaly/detect', {
        dataSource,
        targetColumn: 'rateable_value',
        method: 'statistical',
        threshold: 2.0
      });
      
      if (response.data.success) {
        setAnomalyData(response.data.anomalies);
        showMessage('Anomalies detected successfully!', 'success');
      }
    } catch (error) {
      console.error('Error detecting anomalies:', error);
      showMessage('Failed to detect anomalies: ' + (error.response?.data?.detail || error.message), 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleExplainModel = async (modelId) => {
    try {
      setLoading(true);
      const response = await api.post(`/api/ai-enhanced/models/${modelId}/explain`, {
        dataSource: 'properties',
        method: 'shap'
      });
      
      if (response.data.success) {
        // Handle explanation data
        showMessage('Model explanation generated!', 'success');
      }
    } catch (error) {
      console.error('Error explaining model:', error);
      showMessage('Failed to explain model: ' + (error.response?.data?.detail || error.message), 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeployModel = async (modelId, status) => {
    try {
      setLoading(true);
      const response = await api.post(`/api/ai-enhanced/models/${modelId}/deploy`, {
        deployment_status: status
      });
      
      if (response.data.success) {
        showMessage(`Model deployed to ${status}!`, 'success');
        loadModels();
      }
    } catch (error) {
      console.error('Error deploying model:', error);
      showMessage('Failed to deploy model: ' + (error.response?.data?.detail || error.message), 'error');
    } finally {
      setLoading(false);
    }
  };

  const renderModelCard = (model) => (
    <Card key={model.model_id} sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">{model.model_type}</Typography>
          <Chip 
            label={model.deployment_status} 
            color={model.deployment_status === 'production' ? 'success' : 'default'}
            size="small"
          />
        </Box>
        
        <Typography variant="body2" color="text.secondary" mb={2}>
          {model.description || `Model for ${model.target_column}`}
        </Typography>
        
        <Grid container spacing={2} mb={2}>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary">R² Score</Typography>
            <Typography variant="h6">
              {model.performance_metrics?.r2_score?.toFixed(3) || 'N/A'}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary">MAE</Typography>
            <Typography variant="h6">
              {model.performance_metrics?.mae?.toFixed(2) || 'N/A'}
            </Typography>
          </Grid>
        </Grid>
        
        <Box display="flex" gap={1}>
          <Button
            size="small"
            variant="outlined"
            startIcon={<TimelineIcon />}
            onClick={() => {
              setForecastForm({ ...forecastForm, modelId: model.model_id });
              setShowForecastDialog(true);
            }}
          >
            Forecast
          </Button>
          <Button
            size="small"
            variant="outlined"
            startIcon={<VisibilityIcon />}
            onClick={() => handleExplainModel(model.model_id)}
          >
            Explain
          </Button>
          <Button
            size="small"
            variant="outlined"
            startIcon={<AssessmentIcon />}
            onClick={() => setSelectedModel(model)}
          >
            Details
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  const renderForecastChart = () => {
    if (!forecastData) return null;

    const chartData = forecastData.forecast_dates.map((date, index) => ({
      date,
      forecast: forecastData.forecast_values[index],
      lower: forecastData.confidence_lower[index],
      upper: forecastData.confidence_upper[index]
    }));

    return (
      <Card>
        <CardContent>
          <Typography variant="h6" mb={2}>Forecast Results</Typography>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <RechartsTooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="forecast" 
                stroke="#8884d8" 
                strokeWidth={2}
                name="Forecast"
              />
              <Line 
                type="monotone" 
                dataKey="lower" 
                stroke="#82ca9d" 
                strokeDasharray="5 5"
                name="Lower Bound"
              />
              <Line 
                type="monotone" 
                dataKey="upper" 
                stroke="#ffc658" 
                strokeDasharray="5 5"
                name="Upper Bound"
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    );
  };

  const renderAnomalyChart = () => {
    if (!anomalyData) return null;

    const chartData = [
      { name: 'Normal', value: anomalyData.total_records - anomalyData.anomaly_count, fill: '#82ca9d' },
      { name: 'Anomalies', value: anomalyData.anomaly_count, fill: '#ff6b6b' }
    ];

    return (
      <Card>
        <CardContent>
          <Typography variant="h6" mb={2}>Anomaly Detection Results</Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  />
                </PieChart>
              </ResponsiveContainer>
            </Grid>
            <Grid item xs={6}>
              <Box>
                <Typography variant="h4" color="error">
                  {anomalyData.anomaly_count}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Anomalies Detected
                </Typography>
                <Typography variant="h6" mt={2}>
                  {anomalyData.anomaly_percentage.toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  of total records
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" mb={3}>
        AI Forecasting Dashboard
      </Typography>

      {message && (
        <Alert severity={severity} sx={{ mb: 2 }}>
          {message}
        </Alert>
      )}

      <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="Models" icon={<AssessmentIcon />} />
        <Tab label="Forecasting" icon={<TrendingUpIcon />} />
        <Tab label="Anomaly Detection" icon={<WarningIcon />} />
        <Tab label="Performance" icon={<BarChartIcon />} />
      </Tabs>

      {activeTab === 0 && (
        <Box>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h5">AI Models</Typography>
            <Button
              variant="contained"
              startIcon={<PlayIcon />}
              onClick={() => setShowTrainingDialog(true)}
            >
              Train New Model
            </Button>
          </Box>

          {loading ? (
            <Box display="flex" justifyContent="center" p={3}>
              <CircularProgress />
            </Box>
          ) : (
            <Grid container spacing={2}>
              {models.map(renderModelCard)}
            </Grid>
          )}
        </Box>
      )}

      {activeTab === 1 && (
        <Box>
          <Typography variant="h5" mb={3}>Forecasting</Typography>
          {forecastData ? (
            renderForecastChart()
          ) : (
            <Card>
              <CardContent>
                <Typography variant="body1" color="text.secondary">
                  Generate a forecast to see results here
                </Typography>
              </CardContent>
            </Card>
          )}
        </Box>
      )}

      {activeTab === 2 && (
        <Box>
          <Typography variant="h5" mb={3}>Anomaly Detection</Typography>
          {anomalyData ? (
            renderAnomalyChart()
          ) : (
            <Card>
              <CardContent>
                <Typography variant="body1" color="text.secondary" mb={2}>
                  Run anomaly detection to see results here
                </Typography>
                <Button
                  variant="contained"
                  onClick={() => handleDetectAnomalies('properties')}
                  disabled={loading}
                >
                  Detect Anomalies
                </Button>
              </CardContent>
            </Card>
          )}
        </Box>
      )}

      {activeTab === 3 && (
        <Box>
          <Typography variant="h5" mb={3}>Performance Metrics</Typography>
          {performanceMetrics && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" mb={2}>Model Overview</Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="h4">{performanceMetrics.total_models}</Typography>
                        <Typography variant="body2" color="text.secondary">Total Models</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="h4">{performanceMetrics.active_models}</Typography>
                        <Typography variant="body2" color="text.secondary">Active Models</Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" mb={2}>Average Performance</Typography>
                    <Typography variant="h4">
                      {(performanceMetrics.average_r2_score * 100).toFixed(1)}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">Average R² Score</Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </Box>
      )}

      {/* Training Dialog */}
      <Dialog open={showTrainingDialog} onClose={() => setShowTrainingDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Train New Model</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Data Source"
                value={trainingForm.dataSource}
                onChange={(e) => setTrainingForm({ ...trainingForm, dataSource: e.target.value })}
                placeholder="table_name or file path"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Target Column"
                value={trainingForm.targetColumn}
                onChange={(e) => setTrainingForm({ ...trainingForm, targetColumn: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Model Type</InputLabel>
                <Select
                  value={trainingForm.modelType}
                  onChange={(e) => setTrainingForm({ ...trainingForm, modelType: e.target.value })}
                >
                  <MenuItem value="prophet">Prophet</MenuItem>
                  <MenuItem value="random_forest">Random Forest</MenuItem>
                  <MenuItem value="gradient_boosting">Gradient Boosting</MenuItem>
                  <MenuItem value="linear">Linear Regression</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Forecast Periods"
                value={trainingForm.forecastPeriods}
                onChange={(e) => setTrainingForm({ ...trainingForm, forecastPeriods: parseInt(e.target.value) })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowTrainingDialog(false)}>Cancel</Button>
          <Button onClick={handleTrainModel} variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Train Model'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Forecast Dialog */}
      <Dialog open={showForecastDialog} onClose={() => setShowForecastDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Generate Forecast</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Model</InputLabel>
                <Select
                  value={forecastForm.modelId}
                  onChange={(e) => setForecastForm({ ...forecastForm, modelId: e.target.value })}
                >
                  {models.map(model => (
                    <MenuItem key={model.model_id} value={model.model_id}>
                      {model.model_type} - {model.target_column}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Forecast Periods"
                value={forecastForm.periods}
                onChange={(e) => setForecastForm({ ...forecastForm, periods: parseInt(e.target.value) })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Confidence Level</InputLabel>
                <Select
                  value={forecastForm.confidenceLevel}
                  onChange={(e) => setForecastForm({ ...forecastForm, confidenceLevel: e.target.value })}
                >
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowForecastDialog(false)}>Cancel</Button>
          <Button onClick={handleGenerateForecast} variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Generate Forecast'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AIForecastingDashboard; 