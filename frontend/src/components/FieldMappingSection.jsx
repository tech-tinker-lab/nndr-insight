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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import api from '../api/axios';

const FieldMappingSection = ({ fieldAnalysis, onMappingComplete, embedded = false }) => {
  const [mappings, setMappings] = useState([]);
  const [editingField, setEditingField] = useState(null);
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
      const initialMappings = fieldAnalysis.map((field, index) => ({
        id: index,
        sourceField: field.field_name || `field_${index + 1}`,
        displayName: field.field_name || `Field ${index + 1}`,
        aiDetectedType: field.type || 'text',
        selectedType: field.type === 'empty' ? 'text' : field.type || 'text',
        isRequired: false,
        isPrimaryKey: index === 0,
        defaultValue: '',
        constraints: '',
        description: field.description || `Field ${index + 1}`,
        confidence: field.confidence || 0,
        isEmpty: field.type === 'empty',
        sampleValues: field.sample_values || [],
        uniqueCount: field.unique_count || 0,
        emptyCount: field.empty_count || 0,
        totalCount: field.total_count || 0,
        reason: field.reason || ''
      }));

      setMappings(initialMappings);
    }
  }, [fieldAnalysis]);

  // Auto-save mappings when they change in embedded mode
  useEffect(() => {
    if (embedded && mappings.length > 0) {
      processMappings();
    }
  }, [mappings, embedded]);

  const handleTypeChange = (fieldId, newType) => {
    setMappings(prev => 
      prev.map(mapping => 
        mapping.id === fieldId 
          ? { ...mapping, selectedType: newType }
          : mapping
      )
    );
  };

  const handleFieldUpdate = (fieldId, updates) => {
    setMappings(prev => 
      prev.map(mapping => 
        mapping.id === fieldId 
          ? { ...mapping, ...updates }
          : mapping
      )
    );
  };

  const startEditing = (fieldId) => {
    setEditingField(fieldId);
  };

  const saveEdit = () => {
    setEditingField(null);
  };

  const cancelEdit = () => {
    setEditingField(null);
  };

  const processMappings = () => {
    const processedMappings = mappings.map(mapping => {
      let postgisType = null;
      let fieldType = mapping.selectedType;
      
      if (mapping.selectedType.startsWith('geometry_')) {
        const geomType = mapping.selectedType.replace('geometry_', '').toUpperCase();
        postgisType = geomType;
        fieldType = 'geometry';
      } else if (mapping.selectedType.startsWith('geography_')) {
        const geoType = mapping.selectedType.replace('geography_', '').toUpperCase();
        postgisType = geoType;
        fieldType = 'geography';
      } else if (mapping.selectedType === 'geometry') {
        postgisType = 'POINT';
        fieldType = 'geometry';
      } else if (mapping.selectedType === 'geography') {
        postgisType = 'POINT';
        fieldType = 'geography';
      }

      return {
        source_field: mapping.sourceField,
        staging_field: mapping.sourceField,
        data_type: fieldType,
        postgis_type: postgisType,
        is_required: mapping.isRequired,
        is_primary_key: mapping.isPrimaryKey,
        default_value: mapping.defaultValue,
        constraints: mapping.constraints,
        description: mapping.description
      };
    });

    if (onMappingComplete) {
      onMappingComplete(processedMappings);
    }
  };

  const getTypeColor = (type) => {
    const colors = {
      text: 'default',
      integer: 'primary',
      decimal: 'secondary',
      date: 'success',
      boolean: 'warning',
      geometry: 'info',
      geography: 'info',
      empty: 'warning'
    };
    return colors[type] || 'default';
  };

  if (!fieldAnalysis || fieldAnalysis.length === 0) {
    return (
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Field Configuration</Typography>
          <Alert severity="info">
            No field analysis available. Please complete AI field analysis first.
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card variant="outlined" sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>Field Configuration</Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
          Review and configure field mappings. You can modify data types, constraints, and field properties.
        </Typography>

        <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Field Name</TableCell>
                <TableCell>AI Detection</TableCell>
                <TableCell>Selected Type</TableCell>
                <TableCell>Required</TableCell>
                <TableCell>Primary Key</TableCell>
                <TableCell>Sample Values</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mappings.map((mapping) => (
                <TableRow key={mapping.id}>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {mapping.displayName}
                    </Typography>
                    {mapping.isEmpty && (
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
                        label={mapping.aiDetectedType} 
                        size="small" 
                        color={getTypeColor(mapping.aiDetectedType)}
                      />
                      {mapping.confidence > 0 && (
                        <Chip 
                          label={`${Math.round(mapping.confidence * 100)}%`}
                          size="small"
                          color={mapping.confidence >= 0.8 ? 'success' : mapping.confidence >= 0.6 ? 'warning' : 'error'}
                          variant="outlined"
                        />
                      )}
                    </Box>
                  </TableCell>
                  
                  <TableCell>
                    <FormControl size="small" fullWidth>
                      <Select
                        value={mapping.selectedType}
                        onChange={(e) => handleTypeChange(mapping.id, e.target.value)}
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
                      checked={mapping.isRequired}
                      onChange={(e) => handleFieldUpdate(mapping.id, { isRequired: e.target.checked })}
                      size="small"
                    />
                  </TableCell>
                  
                  <TableCell>
                    <Switch
                      checked={mapping.isPrimaryKey}
                      onChange={(e) => handleFieldUpdate(mapping.id, { isPrimaryKey: e.target.checked })}
                      size="small"
                    />
                  </TableCell>
                  
                  <TableCell>
                    <Typography variant="body2" noWrap>
                      {mapping.sampleValues.length > 0 
                        ? mapping.sampleValues.slice(0, 3).join(', ')
                        : mapping.isEmpty 
                          ? 'Empty data detected'
                          : 'No sample data'
                      }
                    </Typography>
                    {mapping.isEmpty && mapping.totalCount > 0 && (
                      <Typography variant="caption" color="warning.main">
                        {mapping.emptyCount}/{mapping.totalCount} empty values
                      </Typography>
                    )}
                  </TableCell>
                  
                  <TableCell>
                    <Tooltip title="Edit field details">
                      <IconButton 
                        size="small"
                        onClick={() => startEditing(mapping.id)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {!embedded && (
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              onClick={processMappings}
              startIcon={<SaveIcon />}
            >
              Save Field Mappings
            </Button>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default FieldMappingSection; 