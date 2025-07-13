import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  Search as SearchIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  AutoFixHigh as AutoFixIcon,
  Dataset as DatasetIcon,
  Storage as StorageIcon,
  Create as CreateIcon
} from '@mui/icons-material';
import api from '../api/axios';

const AIDatasetMatcher = ({ 
  file, 
  analysis, 
  onDatasetSelected, 
  onRequestNewDataset,
  onSkipMatching 
}) => {
  const [matching, setMatching] = useState(false);
  const [matches, setMatches] = useState([]);
  const [bestMatch, setBestMatch] = useState(null);
  const [showRequestDialog, setShowRequestDialog] = useState(false);
  const [newDatasetRequest, setNewDatasetRequest] = useState({
    name: '',
    description: '',
    category: '',
    source_type: 'file',
    reason: ''
  });

  useEffect(() => {
    if (file && analysis) {
      performAIMatching();
    }
  }, [file, analysis]);

  const performAIMatching = async () => {
    if (!file || !analysis) return;

    setMatching(true);
    try {
      // Step 1: Match with existing dataset structures
      const structureMatches = await matchWithDatasetStructures();
      
      // Step 2: Match with staging configurations
      const configMatches = await matchWithStagingConfigs();
      
      // Step 3: Match with dataset templates
      const templateMatches = await matchWithDesignTemplates();
      
      // Combine and rank all matches
      const allMatches = [...structureMatches, ...configMatches, ...templateMatches];
      const rankedMatches = rankMatches(allMatches);
      
      setMatches(rankedMatches);
      
      // Set best match if confidence is high enough
      if (rankedMatches.length > 0 && rankedMatches[0].confidence >= 0.75) {
        setBestMatch(rankedMatches[0]);
      }
      
    } catch (error) {
      console.error('AI matching failed:', error);
    } finally {
      setMatching(false);
    }
  };

  const matchWithDatasetStructures = async () => {
    try {
      // Get headers from either field_analysis or preview
      const headers = analysis.field_analysis?.map(f => f.field_name) || 
                     analysis.preview?.headers || [];
      
      const response = await api.post('/api/design-enhanced/match', {
        headers: headers,
        file_name: file.name,
        file_type: analysis.format || 'unknown',
        content_preview: analysis.preview || ''
      });
      
      return (response.data.matches || []).map(match => ({
        ...match,
        type: 'dataset_structure',
        source: 'Dataset Structures'
      }));
    } catch (error) {
      console.error('Dataset structure matching failed:', error);
      return [];
    }
  };

  const matchWithStagingConfigs = async () => {
    try {
      // Get headers from either field_analysis or preview
      const headers = analysis.field_analysis?.map(f => f.field_name) || 
                     analysis.preview?.headers || [];
      
      const response = await api.post('/api/admin/staging/configs/match', {
        headers: headers,
        file_name: file.name,
        file_type: analysis.format || 'unknown'
      });
      
      return (response.data.configs || []).map(config => ({
        id: config.config_id,
        name: config.config_name,
        description: config.description,
        confidence: config.similarity,
        type: 'staging_config',
        source: 'Staging Config',
        table_name: config.staging_table_name,
        category: 'Staging'
      }));
    } catch (error) {
      console.error('Staging config matching failed:', error);
      return [];
    }
  };

  const matchWithDesignTemplates = async () => {
    try {
      const response = await api.get('/api/design-enhanced/templates');
      const templates = response.data.templates || [];
      
      const matches = templates.map(template => {
        const confidence = calculateTemplateMatch(template);
        return {
          id: template.template_id,
          name: template.template_name,
          description: template.description || `Template for ${template.template_type}`,
          confidence: confidence,
          type: 'template',
          source: 'Design Templates',
          table_name: template.table_name_pattern || template.template_name,
          category: template.template_type || 'Unknown'
        };
      }).filter(match => match.confidence > 0.3);
      
      return matches;
    } catch (error) {
      console.error('Template matching failed:', error);
      return [];
    }
  };

  const calculateTemplateMatch = (template) => {
    // Get field names from either field_analysis or preview headers
    const fieldNames = analysis.field_analysis?.map(f => f.field_name.toLowerCase()) || 
                      analysis.preview?.headers?.map(h => h.toLowerCase()) || [];
    
    if (fieldNames.length === 0) return 0;
    
    const templateName = template.template_name.toLowerCase();
    const templateDesc = template.description?.toLowerCase() || '';
    
    let score = 0;
    
    // Check filename patterns
    const filename = file.name.toLowerCase();
    if (templateName.includes('postcode') && filename.includes('postcode')) score += 0.4;
    if (templateName.includes('uprn') && filename.includes('uprn')) score += 0.4;
    if (templateName.includes('nndr') && filename.includes('nndr')) score += 0.4;
    if (templateName.includes('boundary') && filename.includes('boundary')) score += 0.4;
    
    // Check field patterns
    const hasPostcode = fieldNames.some(f => f.includes('postcode') || f.includes('pcd'));
    const hasUprn = fieldNames.some(f => f.includes('uprn'));
    const hasGeometry = fieldNames.some(f => f.includes('geometry') || f.includes('geom'));
    
    if (templateName.includes('postcode') && hasPostcode) score += 0.3;
    if (templateName.includes('uprn') && hasUprn) score += 0.3;
    if (templateName.includes('geometry') && hasGeometry) score += 0.3;
    
    return Math.min(score, 1.0);
  };

  const rankMatches = (matches) => {
    // Remove duplicates and combine scores
    const uniqueMatches = new Map();
    
    matches.forEach(match => {
      const key = `${match.type}_${match.id}`;
      if (uniqueMatches.has(key)) {
        const existing = uniqueMatches.get(key);
        existing.confidence = Math.max(existing.confidence, match.confidence);
        existing.sources = [...(existing.sources || [existing.source]), match.source];
      } else {
        uniqueMatches.set(key, { ...match, sources: [match.source] });
      }
    });
    
    const ranked = Array.from(uniqueMatches.values());
    ranked.sort((a, b) => b.confidence - a.confidence);
    
    return ranked;
  };

  const handleSelectDataset = (match) => {
    onDatasetSelected(match);
  };

  const handleRequestNewDataset = () => {
    setNewDatasetRequest({
      name: file.name.replace(/\.[^/.]+$/, ""),
      description: `Dataset for ${file.name} - ${analysis.identified_standards?.map(s => s.name).join(', ') || 'AI detected'}`,
      category: analysis.primary_governing_body || 'Unknown',
      source_type: 'file',
      reason: `No suitable dataset found. AI detected: ${analysis.field_analysis?.length || 0} fields, ${analysis.identified_standards?.length || 0} standards`
    });
    setShowRequestDialog(true);
  };

  const submitNewDatasetRequest = async () => {
    try {
      await onRequestNewDataset(newDatasetRequest);
      setShowRequestDialog(false);
    } catch (error) {
      console.error('Failed to submit new dataset request:', error);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const getConfidenceLabel = (confidence) => {
    if (confidence >= 0.8) return 'Excellent Match';
    if (confidence >= 0.6) return 'Good Match';
    if (confidence >= 0.4) return 'Fair Match';
    return 'Poor Match';
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'dataset_structure':
        return <DatasetIcon />;
      case 'staging_config':
        return <StorageIcon />;
      case 'template':
        return <CreateIcon />;
      default:
        return <InfoIcon />;
    }
  };

  if (matching) {
    return (
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2}>
            <CircularProgress size={24} />
            <Typography variant="h6">AI-Powered Dataset Matching</Typography>
          </Box>
          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
            Analyzing your file and finding the best dataset matches...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">
              <AutoFixIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              AI Dataset Matching Results
            </Typography>
            <Button
              size="small"
              startIcon={<RefreshIcon />}
              onClick={performAIMatching}
            >
              Re-analyze
            </Button>
          </Box>

          {bestMatch && (
            <Alert severity="success" sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                🎯 Perfect Match Found!
              </Typography>
              <Typography variant="body2">
                <strong>{bestMatch.name}</strong> ({Math.round(bestMatch.confidence * 100)}% match)
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {bestMatch.description}
              </Typography>
              <Button
                variant="contained"
                size="small"
                startIcon={<CheckIcon />}
                onClick={() => handleSelectDataset(bestMatch)}
                sx={{ mt: 1 }}
              >
                Use This Dataset
              </Button>
            </Alert>
          )}

          {matches.length > 0 && (
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1">
                  All Matches ({matches.length})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <List>
                  {matches.map((match, index) => (
                    <React.Fragment key={`${match.type}_${match.id}`}>
                      <ListItem>
                        <ListItemIcon>
                          {getTypeIcon(match.type)}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box display="flex" alignItems="center" gap={1}>
                              <Typography variant="subtitle2">
                                {match.name}
                              </Typography>
                              <Chip
                                label={`${Math.round(match.confidence * 100)}%`}
                                color={getConfidenceColor(match.confidence)}
                                size="small"
                              />
                              <Chip
                                label={getConfidenceLabel(match.confidence)}
                                variant="outlined"
                                size="small"
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" color="textSecondary">
                                {match.description}
                              </Typography>
                              <Typography variant="caption" color="textSecondary">
                                Source: {match.sources?.join(', ') || match.source} • 
                                Category: {match.category || 'Unknown'}
                              </Typography>
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          <Button
                            variant="outlined"
                            size="small"
                            onClick={() => handleSelectDataset(match)}
                            disabled={match.confidence < 0.4}
                          >
                            Select
                          </Button>
                        </ListItemSecondaryAction>
                      </ListItem>
                      {index < matches.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          )}

          {matches.length === 0 && (
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                No suitable datasets found. The AI couldn't find a good match for your file.
              </Typography>
            </Alert>
          )}

          <Box display="flex" gap={2} sx={{ mt: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleRequestNewDataset}
            >
              Request New Dataset
            </Button>
            <Button
              variant="outlined"
              onClick={onSkipMatching}
            >
              Skip Matching
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* New Dataset Request Dialog */}
      <Dialog open={showRequestDialog} onClose={() => setShowRequestDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Request New Dataset Structure</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
            Request a new dataset structure for your file. Our team will review and create the appropriate structure.
          </Typography>
          
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Dataset Name"
              value={newDatasetRequest.name}
              onChange={(e) => setNewDatasetRequest({...newDatasetRequest, name: e.target.value})}
              sx={{ mb: 2 }}
            />
            
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Description"
              value={newDatasetRequest.description}
              onChange={(e) => setNewDatasetRequest({...newDatasetRequest, description: e.target.value})}
              sx={{ mb: 2 }}
            />
            
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Category</InputLabel>
              <Select
                value={newDatasetRequest.category}
                onChange={(e) => setNewDatasetRequest({...newDatasetRequest, category: e.target.value})}
                label="Category"
              >
                <MenuItem value="Ordnance Survey">Ordnance Survey</MenuItem>
                <MenuItem value="VOA">Valuation Office Agency</MenuItem>
                <MenuItem value="ONS">Office for National Statistics</MenuItem>
                <MenuItem value="Local Authority">Local Authority</MenuItem>
                <MenuItem value="Other">Other</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Reason for Request"
              value={newDatasetRequest.reason}
              onChange={(e) => setNewDatasetRequest({...newDatasetRequest, reason: e.target.value})}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowRequestDialog(false)}>Cancel</Button>
          <Button 
            onClick={submitNewDatasetRequest} 
            variant="contained"
            disabled={!newDatasetRequest.name || !newDatasetRequest.description}
          >
            Submit Request
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default AIDatasetMatcher; 