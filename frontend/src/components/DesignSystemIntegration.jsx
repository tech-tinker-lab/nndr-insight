import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Chip,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Palette,
  ArrowForward,
  CheckCircle,
  Info,
  Edit,
  Save,
  Cancel,
  Add,
  Delete,
  ExpandMore,
  AutoAwesome,
  TableChart,
  Settings
} from '@mui/icons-material';
import api from '../api/axios';

const DesignSystemIntegration = ({ 
  file, 
  analysis, 
  onDesignSelected, 
  onMappingGenerated,
  csvDelimiter = ',' 
}) => {
  const [designs, setDesigns] = useState([]);
  const [configs, setConfigs] = useState([]);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedDesign, setSelectedDesign] = useState(null);
  const [selectedConfig, setSelectedConfig] = useState(null);
  const [mappingDialogOpen, setMappingDialogOpen] = useState(false);
  const [visualMapping, setVisualMapping] = useState([]);
  const [designDialogOpen, setDesignDialogOpen] = useState(false);
  const [newDesignForm, setNewDesignForm] = useState({
    design_name: '',
    table_name: '',
    description: '',
    table_type: 'custom',
    category: 'general',
    columns: []
  });

  useEffect(() => {
    loadDesignSystem();
  }, []);

  useEffect(() => {
    if (file && analysis?.headers) {
      matchFileToDesigns();
    }
  }, [file, analysis]);

  const loadDesignSystem = async () => {
    setLoading(true);
    try {
      const [designsRes, configsRes] = await Promise.all([
        api.get('/api/design/tables'),
        api.get('/api/design/configs')
      ]);
      setDesigns(designsRes.data.designs || []);
      setConfigs(configsRes.data.configs || []);
    } catch (error) {
      console.error('Error loading design system:', error);
    } finally {
      setLoading(false);
    }
  };

  const matchFileToDesigns = async () => {
    if (!file || !analysis?.headers) return;

    setLoading(true);
    try {
      const response = await api.post('/api/design/match', {
        headers: analysis.headers,
        file_name: file.name,
        file_type: analysis.fileType,
        content_preview: analysis.preview || ''
      });
      setMatches(response.data.matches || []);
    } catch (error) {
      console.error('Error matching file to designs:', error);
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  const selectDesign = (design, config = null) => {
    setSelectedDesign(design);
    setSelectedConfig(config);
    
    // Generate initial mapping
    const initialMapping = generateInitialMapping(analysis.headers, design, config);
    setVisualMapping(initialMapping);
    
    onDesignSelected?.(design, config);
  };

  const generateInitialMapping = (headers, design, config) => {
    const mapping = [];
    const designColumns = design?.columns || [];
    const configRules = config?.mapping_rules || [];

    headers.forEach((header, index) => {
      const mappingItem = {
        id: `mapping_${index}`,
        sourceColumn: header,
        targetColumn: '',
        mappingType: 'direct',
        dataType: 'text',
        isRequired: false,
        confidence: 0,
        matchStatus: 'unmatched'
      };

      // Try to match using config rules first
      const configMatch = configRules.find(rule => 
        rule.source_column?.toLowerCase() === header.toLowerCase()
      );
      
      if (configMatch) {
        mappingItem.targetColumn = configMatch.target_column;
        mappingItem.mappingType = configMatch.mapping_type || 'direct';
        mappingItem.confidence = 0.9;
        mappingItem.matchStatus = 'exact';
      } else {
        // Try to match using design columns
        const designMatch = designColumns.find(col => 
          col.name?.toLowerCase() === header.toLowerCase() ||
          col.description?.toLowerCase().includes(header.toLowerCase())
        );
        
        if (designMatch) {
          mappingItem.targetColumn = designMatch.name;
          mappingItem.dataType = designMatch.type;
          mappingItem.isRequired = designMatch.is_required;
          mappingItem.confidence = 0.7;
          mappingItem.matchStatus = 'partial';
        } else {
          // Generate default mapping
          mappingItem.targetColumn = generateDefaultColumnName(header);
          mappingItem.dataType = inferDataType(header);
          mappingItem.confidence = 0.3;
          mappingItem.matchStatus = 'suggested';
        }
      }

      mapping.push(mappingItem);
    });

    return mapping;
  };

  const generateDefaultColumnName = (header) => {
    return header
      .toLowerCase()
      .replace(/[^a-z0-9]/g, '_')
      .replace(/_+/g, '_')
      .replace(/^_|_$/g, '');
  };

  const inferDataType = (header) => {
    const headerLower = header.toLowerCase();
    
    if (headerLower.includes('date') || headerLower.includes('time')) {
      return 'date';
    }
    if (headerLower.includes('id') || headerLower.includes('code')) {
      return 'text';
    }
    if (headerLower.includes('amount') || headerLower.includes('value') || headerLower.includes('price')) {
      return 'numeric';
    }
    if (headerLower.includes('count') || headerLower.includes('number')) {
      return 'integer';
    }
    if (headerLower.includes('active') || headerLower.includes('enabled') || headerLower.includes('flag')) {
      return 'boolean';
    }
    
    return 'text';
  };

  const updateMapping = (id, updates) => {
    setVisualMapping(prev => 
      prev.map(mapping => 
        mapping.id === id ? { ...mapping, ...updates } : mapping
      )
    );
  };

  const saveMapping = () => {
    onMappingGenerated?.(visualMapping, selectedDesign, selectedConfig);
    setMappingDialogOpen(false);
  };

  const createNewDesign = async () => {
    try {
      const response = await api.post('/api/design/tables', newDesignForm);
      const newDesign = response.data;
      
      setDesigns(prev => [...prev, newDesign]);
      setDesignDialogOpen(false);
      
      // Auto-select the new design
      selectDesign(newDesign);
      
      return newDesign;
    } catch (error) {
      console.error('Error creating new design:', error);
      throw error;
    }
  };

  const getMatchScoreColor = (score) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  };

  const getMatchScoreLabel = (score) => {
    if (score >= 0.8) return 'Excellent';
    if (score >= 0.6) return 'Good';
    if (score >= 0.4) return 'Fair';
    return 'Poor';
  };

  return (
    <Box>
      {/* Design System Header */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Palette sx={{ mr: 1 }} />
            <Typography variant="h6">Design System Integration</Typography>
            <Chip 
              label="AI-Powered" 
              color="primary" 
              size="small" 
              sx={{ ml: 1 }}
              icon={<AutoAwesome />}
            />
          </Box>
          
          <Typography variant="body2" color="text.secondary">
            Automatically match your file to existing table designs and generate intelligent column mappings
          </Typography>
        </CardContent>
      </Card>

      {/* Design Matches */}
      {matches.length > 0 && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Recommended Designs ({matches.length})
            </Typography>
            
            <Grid container spacing={2}>
              {matches.slice(0, 3).map((match, index) => (
                <Grid item xs={12} md={4} key={match.config_id}>
                  <Card 
                    variant="outlined" 
                    sx={{ 
                      cursor: 'pointer',
                      border: selectedDesign?.design_id === match.design_id ? 2 : 1,
                      borderColor: selectedDesign?.design_id === match.design_id ? 'primary.main' : 'divider'
                    }}
                    onClick={() => selectDesign(match, match)}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {match.design_name}
                        </Typography>
                        <Chip 
                          label={`${(match.match_score * 100).toFixed(0)}%`}
                          color={getMatchScoreColor(match.match_score)}
                          size="small"
                        />
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {match.table_name}
                      </Typography>
                      
                      <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                        <Chip label={match.table_type} size="small" color="primary" />
                        <Chip label={match.category} size="small" color="secondary" />
                      </Box>
                      
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        {match.columns?.length || 0} columns
                      </Typography>
                      
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<ArrowForward />}
                        onClick={(e) => {
                          e.stopPropagation();
                          selectDesign(match, match);
                        }}
                      >
                        Use This Design
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Selected Design Details */}
      {selectedDesign && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Selected Design: {selectedDesign.design_name}
              </Typography>
              <Button
                size="small"
                variant="outlined"
                startIcon={<Edit />}
                onClick={() => setMappingDialogOpen(true)}
              >
                Configure Mapping
              </Button>
            </Box>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">Table Name</Typography>
                <Typography variant="body1">{selectedDesign.table_name}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">Type</Typography>
                <Chip label={selectedDesign.table_type} size="small" color="primary" />
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary">Description</Typography>
                <Typography variant="body1">{selectedDesign.description}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Visual Mapping Dialog */}
      <Dialog 
        open={mappingDialogOpen} 
        onClose={() => setMappingDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <TableChart sx={{ mr: 1 }} />
            Column Mapping Configuration
          </Box>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Typography variant="subtitle1" sx={{ mb: 2 }}>
                Map source columns to target columns
              </Typography>
              
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Source Column</TableCell>
                      <TableCell>Target Column</TableCell>
                      <TableCell>Data Type</TableCell>
                      <TableCell>Required</TableCell>
                      <TableCell>Match Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {visualMapping.map((mapping) => (
                      <TableRow key={mapping.id}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {mapping.sourceColumn}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            value={mapping.targetColumn}
                            onChange={(e) => updateMapping(mapping.id, { targetColumn: e.target.value })}
                            fullWidth
                          />
                        </TableCell>
                        <TableCell>
                          <FormControl size="small" fullWidth>
                            <Select
                              value={mapping.dataType}
                              onChange={(e) => updateMapping(mapping.id, { dataType: e.target.value })}
                            >
                              <MenuItem value="text">Text</MenuItem>
                              <MenuItem value="integer">Integer</MenuItem>
                              <MenuItem value="numeric">Numeric</MenuItem>
                              <MenuItem value="boolean">Boolean</MenuItem>
                              <MenuItem value="date">Date</MenuItem>
                            </Select>
                          </FormControl>
                        </TableCell>
                        <TableCell>
                          <Switch
                            checked={mapping.isRequired}
                            onChange={(e) => updateMapping(mapping.id, { isRequired: e.target.checked })}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={mapping.matchStatus}
                            size="small"
                            color={
                              mapping.matchStatus === 'exact' ? 'success' :
                              mapping.matchStatus === 'partial' ? 'warning' :
                              mapping.matchStatus === 'suggested' ? 'info' : 'default'
                            }
                          />
                        </TableCell>
                        <TableCell>
                          <Tooltip title="Remove mapping">
                            <IconButton 
                              size="small"
                              onClick={() => {
                                setVisualMapping(prev => prev.filter(m => m.id !== mapping.id));
                              }}
                            >
                              <Delete />
                            </IconButton>
                          </Tooltip>
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
          <Button onClick={() => setMappingDialogOpen(false)}>Cancel</Button>
          <Button onClick={saveMapping} variant="contained" startIcon={<Save />}>
            Save Mapping
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create New Design Dialog */}
      <Dialog 
        open={designDialogOpen} 
        onClose={() => setDesignDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create New Table Design</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Design Name"
                value={newDesignForm.design_name}
                onChange={(e) => setNewDesignForm({ ...newDesignForm, design_name: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Table Name"
                value={newDesignForm.table_name}
                onChange={(e) => setNewDesignForm({ ...newDesignForm, table_name: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={newDesignForm.description}
                onChange={(e) => setNewDesignForm({ ...newDesignForm, description: e.target.value })}
                margin="normal"
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Table Type</InputLabel>
                <Select
                  value={newDesignForm.table_type}
                  onChange={(e) => setNewDesignForm({ ...newDesignForm, table_type: e.target.value })}
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
                  value={newDesignForm.category}
                  onChange={(e) => setNewDesignForm({ ...newDesignForm, category: e.target.value })}
                >
                  <MenuItem value="general">General</MenuItem>
                  <MenuItem value="business">Business</MenuItem>
                  <MenuItem value="government">Government</MenuItem>
                  <MenuItem value="address">Address</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDesignDialogOpen(false)}>Cancel</Button>
          <Button onClick={createNewDesign} variant="contained" startIcon={<Save />}>
            Create Design
          </Button>
        </DialogActions>
      </Dialog>

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
        <Button
          variant="outlined"
          startIcon={<Add />}
          onClick={() => setDesignDialogOpen(true)}
        >
          Create New Design
        </Button>
        
        {selectedDesign && (
          <Button
            variant="contained"
            startIcon={<Settings />}
            onClick={() => setMappingDialogOpen(true)}
          >
            Configure Mapping
          </Button>
        )}
      </Box>
    </Box>
  );
};

export default DesignSystemIntegration; 