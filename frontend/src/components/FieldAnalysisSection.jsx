import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  Button,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Switch,
  TextField
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  AutoFixHigh as AutoFixIcon
} from '@mui/icons-material';
import api from '../api/axios';

const FieldAnalysisSection = ({ fieldAnalysis, onApplySuggestions, autoApply = false }) => {
  const [suggestions, setSuggestions] = useState([]);
  const [hasEmptyFields, setHasEmptyFields] = useState(false);
  const [dataTypes, setDataTypes] = useState([]);
  const [loadingDataTypes, setLoadingDataTypes] = useState(false);

  useEffect(() => {
    const fetchDataTypes = async () => {
      try {
        setLoadingDataTypes(true);
        const response = await api.get('/api/design-enhanced/data-types');
        setDataTypes(response.data.data_types || []);
      } catch (error) {
        console.error('Error fetching data types:', error);
        // Fallback to default data types
        setDataTypes([
          { value: 'text', label: 'Text', description: 'Variable-length character string' },
          { value: 'varchar', label: 'VARCHAR', description: 'Variable-length character string with max length' },
          { value: 'integer', label: 'Integer', description: 'Whole number' },
          { value: 'bigint', label: 'Big Integer', description: 'Large whole number' },
          { value: 'decimal', label: 'Decimal', description: 'Fixed-point decimal number' },
          { value: 'date', label: 'Date', description: 'Date without time' },
          { value: 'timestamp', label: 'Timestamp', description: 'Date and time' },
          { value: 'boolean', label: 'Boolean', description: 'True/false value' },
          { value: 'geometry', label: 'Geometry', description: 'PostGIS geometry type' },
          { value: 'geography', label: 'Geography', description: 'PostGIS geography type' }
        ]);
      } finally {
        setLoadingDataTypes(false);
      }
    };

    fetchDataTypes();
  }, []);

  useEffect(() => {
    if (fieldAnalysis && fieldAnalysis.length > 0) {
      const initialSuggestions = fieldAnalysis.map((field, index) => {
        // Determine the selected type based on AI detection
        let selectedType = 'text'; // default fallback
        
        if (field.type === 'empty') {
          selectedType = 'text';
        } else if (field.type) {
          // Check if the detected type is available in dataTypes
          const availableType = dataTypes.find(dt => dt.value === field.type);
          if (availableType) {
            selectedType = field.type;
          } else {
            // Map custom types to valid database types
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
        }

        return {
          id: index,
          sourceField: field.field_name || `field_${index + 1}`,
          displayName: field.field_name || `Field ${index + 1}`,
          aiDetectedType: field.type || 'text',
          selectedType: selectedType,
          confidence: field.confidence || 0,
          isEmpty: field.type === 'empty',
          sampleValues: field.sample_values || [],
          uniqueCount: field.unique_count || 0,
          emptyCount: field.empty_count || 0,
          totalCount: field.total_count || 0,
          reason: field.reason || '',
          sequenceOrder: field.sequence_order || index + 1,
          isRequired: false,
          isNullable: true,
          defaultValue: ''
        };
      });

      setSuggestions(initialSuggestions);
      setHasEmptyFields(initialSuggestions.some(s => s.isEmpty));
      
      // Auto-apply suggestions if enabled
      if (autoApply && initialSuggestions.length > 0) {
        onApplySuggestions(initialSuggestions);
      }
    }
  }, [fieldAnalysis, dataTypes, autoApply, onApplySuggestions]);

  const getTypeColor = (type) => {
    const colors = {
      text: 'default',
      integer: 'primary',
      decimal: 'secondary',
      date: 'success',
      boolean: 'warning',
      postcode: 'info',
      uprn: 'error',
      coordinate: 'success',
      empty: 'warning'
    };
    return colors[type] || 'default';
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const handleTypeChange = (fieldId, newType) => {
    setSuggestions(prev => 
      prev.map(suggestion => 
        suggestion.id === fieldId 
          ? { ...suggestion, selectedType: newType }
          : suggestion
      )
    );
  };

  const handleRequiredChange = (fieldId, isRequired) => {
    setSuggestions(prev => 
      prev.map(suggestion => 
        suggestion.id === fieldId 
          ? { ...suggestion, isRequired, isNullable: !isRequired }
          : suggestion
      )
    );
  };

  const handleNullableChange = (fieldId, isNullable) => {
    setSuggestions(prev => 
      prev.map(suggestion => 
        suggestion.id === fieldId 
          ? { ...suggestion, isNullable, isRequired: !isNullable }
          : suggestion
      )
    );
  };

  const handleDefaultValueChange = (fieldId, defaultValue) => {
    setSuggestions(prev => 
      prev.map(suggestion => 
        suggestion.id === fieldId 
          ? { ...suggestion, defaultValue }
          : suggestion
      )
    );
  };

  const handleApplySuggestions = () => {
    if (onApplySuggestions) {
      onApplySuggestions(suggestions);
    }
  };

  if (!fieldAnalysis || fieldAnalysis.length === 0) {
    return (
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>AI Field Analysis</Typography>
          <Alert severity="info">
            No field analysis available. Please complete file analysis first.
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card variant="outlined" sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
          <Typography variant="h6">AI Field Analysis & Suggestions</Typography>
          <Button
            variant="contained"
            startIcon={<AutoFixIcon />}
            onClick={handleApplySuggestions}
            size="small"
          >
            Apply AI Suggestions
          </Button>
        </Box>

        {hasEmptyFields && (
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              AI detected some fields with empty data. These fields are marked with warning indicators and can be manually configured.
            </Typography>
          </Alert>
        )}

        <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Field Name</TableCell>
                <TableCell>AI Detection</TableCell>
                <TableCell>Select Type</TableCell>
                <TableCell>Required</TableCell>
                <TableCell>Nullable</TableCell>
                <TableCell>Default Value</TableCell>
                <TableCell>Sample Values</TableCell>
                <TableCell>Statistics</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {suggestions.map((suggestion) => (
                <TableRow key={suggestion.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {suggestion.displayName}
                    </Typography>
                    {suggestion.isEmpty && (
                      <Chip 
                        label="Empty Data" 
                        size="small" 
                        color="warning" 
                        sx={{ mt: 0.5 }}
                      />
                    )}
                  </TableCell>
                  
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Chip 
                        label={suggestion.aiDetectedType} 
                        size="small" 
                        color={getTypeColor(suggestion.aiDetectedType)}
                      />
                      {suggestion.aiDetectedType === 'empty' && (
                        <WarningIcon color="warning" fontSize="small" />
                      )}
                    </Box>
                    {suggestion.confidence > 0 && (
                      <Typography variant="caption" color="textSecondary" sx={{ mt: 0.5, display: 'block' }}>
                        Confidence: {Math.round(suggestion.confidence * 100)}%
                      </Typography>
                    )}
                  </TableCell>
                  
                  <TableCell>
                    <FormControl size="small" fullWidth>
                      <Select
                        value={suggestion.selectedType}
                        onChange={(e) => handleTypeChange(suggestion.id, e.target.value)}
                        displayEmpty
                        disabled={loadingDataTypes}
                      >
                        {loadingDataTypes ? (
                          <MenuItem disabled>
                            <Box display="flex" alignItems="center" gap={1}>
                              <CircularProgress size={16} />
                              <Typography variant="body2">Loading...</Typography>
                            </Box>
                          </MenuItem>
                        ) : (
                          dataTypes.map((type) => (
                            <MenuItem key={type.value} value={type.value}>
                              <Box>
                                <Typography variant="body2">{type.label}</Typography>
                                <Typography variant="caption" color="textSecondary">
                                  {type.description}
                                </Typography>
                              </Box>
                            </MenuItem>
                          ))
                        )}
                      </Select>
                    </FormControl>
                  </TableCell>
                  
                  <TableCell>
                    <Switch
                      checked={suggestion.isRequired}
                      onChange={(e) => handleRequiredChange(suggestion.id, e.target.checked)}
                      size="small"
                    />
                  </TableCell>
                  
                  <TableCell>
                    <Switch
                      checked={suggestion.isNullable}
                      onChange={(e) => handleNullableChange(suggestion.id, e.target.checked)}
                      size="small"
                    />
                  </TableCell>
                  
                  <TableCell>
                    <TextField
                      size="small"
                      value={suggestion.defaultValue}
                      onChange={(e) => handleDefaultValueChange(suggestion.id, e.target.value)}
                      placeholder="Default value"
                      sx={{ minWidth: 120 }}
                    />
                  </TableCell>
                  
                  <TableCell>
                    <Typography variant="body2" noWrap>
                      {suggestion.sampleValues.length > 0 
                        ? suggestion.sampleValues.slice(0, 3).join(', ')
                        : suggestion.isEmpty 
                          ? 'Empty data detected'
                          : 'No sample data'
                      }
                    </Typography>
                  </TableCell>
                  
                  <TableCell>
                    <Box display="flex" flexDirection="column" gap={0.5}>
                      {suggestion.uniqueCount > 0 && (
                        <Typography variant="caption" color="textSecondary">
                          {suggestion.uniqueCount} unique values
                        </Typography>
                      )}
                      {suggestion.isEmpty && suggestion.totalCount > 0 && (
                        <Typography variant="caption" color="warning.main">
                          {suggestion.emptyCount}/{suggestion.totalCount} empty values
                        </Typography>
                      )}
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Analysis Summary */}
        <Accordion sx={{ mt: 2 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1">
              Analysis Summary
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box display="flex" flexDirection="column" gap={1}>
              <Typography variant="body2">
                <strong>Total Fields:</strong> {suggestions.length}
              </Typography>
              <Typography variant="body2">
                <strong>Empty Fields:</strong> {suggestions.filter(s => s.isEmpty).length}
              </Typography>
              <Typography variant="body2">
                <strong>High Confidence Detections:</strong> {suggestions.filter(s => s.confidence >= 0.8).length}
              </Typography>
              <Typography variant="body2">
                <strong>Low Confidence Detections:</strong> {suggestions.filter(s => s.confidence < 0.6).length}
              </Typography>
            </Box>
          </AccordionDetails>
        </Accordion>
      </CardContent>
    </Card>
  );
};

export default FieldAnalysisSection; 