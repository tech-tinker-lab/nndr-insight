import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
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
  PieChart as PieChartIcon,
  Store as StoreIcon,
  Extension as ExtensionIcon,
  Psychology as PsychologyIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Pending as PendingIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import api from '../api/axios';

const AIEnhancedDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [severity, setSeverity] = useState('info');

  // AI Models state
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [anomalyData, setAnomalyData] = useState(null);
  const [performanceMetrics, setPerformanceMetrics] = useState(null);

  // Plugin Marketplace state
  const [plugins, setPlugins] = useState([]);
  const [pluginCategories, setPluginCategories] = useState([]);
  const [featuredPlugins, setFeaturedPlugins] = useState([]);
  const [marketplaceStats, setMarketplaceStats] = useState(null);
  const [executions, setExecutions] = useState([]);

  // Dialogs state
  const [showTrainingDialog, setShowTrainingDialog] = useState(false);
  const [showForecastDialog, setShowForecastDialog] = useState(false);
  const [showPluginDialog, setShowPluginDialog] = useState(false);
  const [showExplainDialog, setShowExplainDialog] = useState(false);

  // Forms state
  const [trainingForm, setTrainingForm] = useState({
    dataSource: '',
    targetColumn: 'rateable_value',
    modelType: 'prophet',
    forecastPeriods: 12,
    parameters: {}
  });

  const [forecastForm, setForecastForm] = useState({
    modelId: '',
    periods: 12,
    confidenceLevel: 'medium'
  });

  const [pluginForm, setPluginForm] = useState({
    pluginId: '',
    parameters: {},
    inputDatasets: {}
  });

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadModels(),
        loadPerformanceMetrics(),
        loadPlugins(),
        loadPluginCategories(),
        loadFeaturedPlugins(),
        loadMarketplaceStats(),
        loadExecutions()
      ]);
    } catch (error) {
      console.error('Error loading data:', error);
      showMessage('Failed to load dashboard data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadModels = async () => {
    try {
      const response = await api.get('/api/ai-enhanced/models');
      setModels(response.data.models || []);
    } catch (error) {
      console.error('Error loading models:', error);
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

  const loadPlugins = async () => {
    try {
      const response = await api.get('/api/plugin-marketplace/plugins');
      setPlugins(response.data.plugins || []);
    } catch (error) {
      console.error('Error loading plugins:', error);
    }
  };

  const loadPluginCategories = async () => {
    try {
      const response = await api.get('/api/plugin-marketplace/marketplace/categories');
      setPluginCategories(response.data.categories || []);
    } catch (error) {
      console.error('Error loading plugin categories:', error);
    }
  };

  const loadFeaturedPlugins = async () => {
    try {
      const response = await api.get('/api/plugin-marketplace/marketplace/featured');
      setFeaturedPlugins(response.data.featured_plugins || []);
    } catch (error) {
      console.error('Error loading featured plugins:', error);
    }
  };

  const loadMarketplaceStats = async () => {
    try {
      const response = await api.get('/api/plugin-marketplace/marketplace/statistics');
      setMarketplaceStats(response.data.statistics);
    } catch (error) {
      console.error('Error loading marketplace stats:', error);
    }
  };

  const loadExecutions = async () => {
    try {
      const response = await api.get('/api/plugin-marketplace/executions');
      setExecutions(response.data.executions || []);
    } catch (error) {
      console.error('Error loading executions:', error);
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

  const handleExecutePlugin = async () => {
    try {
      setLoading(true);
      const response = await api.post(`/api/plugin-marketplace/plugins/${pluginForm.pluginId}/execute`, {
        parameters: pluginForm.parameters,
        input_datasets: pluginForm.inputDatasets
      });
      
      if (response.data.success) {
        showMessage('Plugin execution started!', 'success');
        setShowPluginDialog(false);
        loadExecutions();
      }
    } catch (error) {
      console.error('Error executing plugin:', error);
      showMessage('Failed to execute plugin: ' + (error.response?.data?.detail || error.message), 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDetectAnomalies = async () => {
    try {
      setLoading(true);
      const response = await api.post('/api/ai-enhanced/anomaly/detect', {
        dataSource: 'properties',
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

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon color="success" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      case 'running':
        return <PendingIcon color="primary" />;
      default:
        return <PendingIcon color="disabled" />;
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
            onClick={() => setSelectedModel(model)}
          >
            Details
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  const renderPluginCard = (plugin) => (
    <Card key={plugin.plugin_id} sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">{plugin.name}</Typography>
          <Chip 
            label={plugin.category} 
            color="primary"
            size="small"
          />
        </Box>
        
        <Typography variant="body2" color="text.secondary" mb={2}>
          {plugin.description}
        </Typography>
        
        <Box display="flex" gap={1} mb={2}>
          {plugin.tags.map(tag => (
            <Chip key={tag} label={tag} size="small" variant="outlined" />
          ))}
        </Box>
        
        <Box display="flex" gap={1}>
          <Button
            size="small"
            variant="contained"
            startIcon={<PlayIcon />}
            onClick={() => {
              setPluginForm({ ...pluginForm, pluginId: plugin.plugin_id });
              setShowPluginDialog(true);
            }}
          >
            Execute
          </Button>
          <Button
            size="small"
            variant="outlined"
            startIcon={<VisibilityIcon />}
            onClick={() => setSelectedModel(plugin)}
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
        AI-Enhanced Dashboard
      </Typography>

      {message && (
        <Alert severity={severity} sx={{ mb: 2 }}>
          {message}
        </Alert>
      )}

      <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="AI Models" icon={<PsychologyIcon />} />
        <Tab label="Forecasting" icon={<TrendingUpIcon />} />
        <Tab label="Anomaly Detection" icon={<WarningIcon />} />
        <Tab label="Plugin Marketplace" icon={<StoreIcon />} />
        <Tab label="Executions" icon={<TimelineIcon />} />
        <Tab label="Performance" icon={<AnalyticsIcon />} />
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
                  onClick={handleDetectAnomalies}
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
          <Typography variant="h5" mb={3}>Plugin Marketplace</Typography>
          
          {marketplaceStats && (
            <Grid container spacing={3} mb={3}>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h4">{marketplaceStats.total_plugins}</Typography>
                    <Typography variant="body2" color="text.secondary">Total Plugins</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h4">{marketplaceStats.active_plugins}</Typography>
                    <Typography variant="body2" color="text.secondary">Active Plugins</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h4">{marketplaceStats.total_executions}</Typography>
                    <Typography variant="body2" color="text.secondary">Total Executions</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h4">{marketplaceStats.success_rate.toFixed(1)}%</Typography>
                    <Typography variant="body2" color="text.secondary">Success Rate</Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          <Typography variant="h6" mb={2}>Featured Plugins</Typography>
          <Grid container spacing={2}>
            {featuredPlugins.map(renderPluginCard)}
          </Grid>
        </Box>
      )}

      {activeTab === 4 && (
        <Box>
          <Typography variant="h5" mb={3}>Plugin Executions</Typography>
          
          <List>
            {executions.map(execution => (
              <React.Fragment key={execution.execution_id}>
                <ListItem>
                  <ListItemIcon>
                    {getStatusIcon(execution.status)}
                  </ListItemIcon>
                  <ListItemText
                    primary={`${execution.plugin_id} - ${execution.status}`}
                    secondary={`Started: ${new Date(execution.start_time).toLocaleString()}`}
                  />
                  <Chip 
                    label={execution.status} 
                    color={execution.status === 'completed' ? 'success' : 
                           execution.status === 'failed' ? 'error' : 'default'}
                    size="small"
                  />
                </ListItem>
                <Divider />
              </React.Fragment>
            ))}
          </List>
        </Box>
      )}

      {activeTab === 5 && (
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

      {/* Plugin Dialog */}
      <Dialog open={showPluginDialog} onClose={() => setShowPluginDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Execute Plugin</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Plugin</InputLabel>
                <Select
                  value={pluginForm.pluginId}
                  onChange={(e) => setPluginForm({ ...pluginForm, pluginId: e.target.value })}
                >
                  {plugins.map(plugin => (
                    <MenuItem key={plugin.plugin_id} value={plugin.plugin_id}>
                      {plugin.name} - {plugin.category}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Parameters (JSON)"
                value={JSON.stringify(pluginForm.parameters, null, 2)}
                onChange={(e) => {
                  try {
                    const params = JSON.parse(e.target.value);
                    setPluginForm({ ...pluginForm, parameters: params });
                  } catch (error) {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='{"param1": "value1", "param2": "value2"}'
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPluginDialog(false)}>Cancel</Button>
          <Button onClick={handleExecutePlugin} variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Execute Plugin'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AIEnhancedDashboard; 