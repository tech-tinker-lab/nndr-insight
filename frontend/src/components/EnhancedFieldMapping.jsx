import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
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
  TextField,
  Switch,
  FormControlLabel,
  Typography,
  Box,
  Chip,
  Alert,
  IconButton,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';

const EnhancedFieldMapping = ({ 
  open, 
  onClose, 
  fieldAnalysis, 
  onMappingComplete,
  structureName,
  embedded = false
}) => {
  const [mappings, setMappings] = useState([]);
  const [editingField, setEditingField] = useState(null);
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
        // Fallback to default data types if API fails
        setDataTypes([
          // Standard PostgreSQL types
          { value: 'text', label: 'Text', description: 'Variable-length character string' },
          { value: 'varchar', label: 'VARCHAR', description: 'Variable-length character string with max length' },
          { value: 'integer', label: 'Integer', description: 'Whole number' },
          { value: 'bigint', label: 'Big Integer', description: 'Large whole number (e.g., UPRN)' },
          { value: 'decimal', label: 'Decimal', description: 'Fixed-point decimal number' },
          { value: 'numeric', label: 'Numeric', description: 'Variable-precision decimal number' },
          { value: 'date', label: 'Date', description: 'Date without time' },
          { value: 'timestamp', label: 'Timestamp', description: 'Date and time' },
          { value: 'boolean', label: 'Boolean', description: 'True/false value' },
          { value: 'json', label: 'JSON', description: 'JSON data type' },
          { value: 'uuid', label: 'UUID', description: 'Universally unique identifier' },
          
          // PostGIS Geometry types
          { value: 'geometry', label: 'Geometry', description: 'Generic geometry type (PostGIS)' },
          { value: 'geometry_point', label: 'Geometry (Point)', description: 'Point geometry with SRID 4326' },
          { value: 'geometry_linestring', label: 'Geometry (LineString)', description: 'LineString geometry with SRID 4326' },
          { value: 'geometry_polygon', label: 'Geometry (Polygon)', description: 'Polygon geometry with SRID 4326' },
          { value: 'geometry_multipoint', label: 'Geometry (MultiPoint)', description: 'MultiPoint geometry with SRID 4326' },
          { value: 'geometry_multilinestring', label: 'Geometry (MultiLineString)', description: 'MultiLineString geometry with SRID 4326' },
          { value: 'geometry_multipolygon', label: 'Geometry (MultiPolygon)', description: 'MultiPolygon geometry with SRID 4326' },
          { value: 'geometry_collection', label: 'Geometry (GeometryCollection)', description: 'GeometryCollection with SRID 4326' },
          
          // PostGIS Geography types
          { value: 'geography', label: 'Geography', description: 'Generic geography type (PostGIS)' },
          { value: 'geography_point', label: 'Geography (Point)', description: 'Point geography with SRID 4326' },
          { value: 'geography_linestring', label: 'Geography (LineString)', description: 'LineString geography with SRID 4326' },
          { value: 'geography_polygon', label: 'Geography (Polygon)', description: 'Polygon geography with SRID 4326' },
          { value: 'geography_multipoint', label: 'Geography (MultiPoint)', description: 'MultiPoint geography with SRID 4326' },
          { value: 'geography_multilinestring', label: 'Geography (MultiLineString)', description: 'MultiLineString geography with SRID 4326' },
          { value: 'geography_multipolygon', label: 'Geography (MultiPolygon)', description: 'MultiPolygon geography with SRID 4326' },
          { value: 'geography_collection', label: 'Geography (GeometryCollection)', description: 'GeometryCollection geography with SRID 4326' },
          
          // Specialized PostGIS types
          { value: 'box2d', label: 'Box2D', description: '2D bounding box' },
          { value: 'box3d', label: 'Box3D', description: '3D bounding box' },
          { value: 'raster', label: 'Raster', description: 'Raster data type' }
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
      setHasEmptyFields(initialMappings.some(m => m.isEmpty));
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
      // Determine if this is a PostGIS type and extract the appropriate postgis_type
      let postgisType = null;
      let fieldType = mapping.selectedType;
      
      if (mapping.selectedType.startsWith('geometry_')) {
        // Extract the geometry type from the value (e.g., 'geometry_point' -> 'POINT')
        const geomType = mapping.selectedType.replace('geometry_', '').toUpperCase();
        postgisType = geomType;
        fieldType = 'geometry';
      } else if (mapping.selectedType.startsWith('geography_')) {
        // Extract the geography type from the value (e.g., 'geography_point' -> 'POINT')
        const geoType = mapping.selectedType.replace('geography_', '').toUpperCase();
        postgisType = geoType;
        fieldType = 'geography';
      } else if (mapping.selectedType === 'geometry') {
        postgisType = 'POINT'; // Default for generic geometry
        fieldType = 'geometry';
      } else if (mapping.selectedType === 'geography') {
        postgisType = 'POINT'; // Default for generic geography
        fieldType = 'geography';
      } else if (['box2d', 'box3d', 'raster'].includes(mapping.selectedType)) {
        fieldType = mapping.selectedType;
      }
      
      return {
        field_name: mapping.sourceField,
        display_name: mapping.displayName,
        field_type: fieldType,
        postgis_type: postgisType,
        is_required: mapping.isRequired,
        is_primary_key: mapping.isPrimaryKey,
        default_value: mapping.defaultValue,
        constraints: mapping.constraints,
        description: mapping.description,
        sequence_order: mapping.id + 1
      };
    });

    onMappingComplete(processedMappings);
  };

  const handleSaveMapping = () => {
    processMappings();
    onClose();
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'empty': return 'error';
      case 'text': case 'varchar': return 'default';
      case 'integer': case 'bigint': return 'primary';
      case 'decimal': case 'numeric': return 'secondary';
      case 'date': case 'timestamp': return 'info';
      case 'boolean': return 'warning';
      case 'geometry': case 'geography': 
      case 'geometry_point': case 'geometry_linestring': case 'geometry_polygon':
      case 'geometry_multipoint': case 'geometry_multilinestring': case 'geometry_multipolygon': case 'geometry_collection':
      case 'geography_point': case 'geography_linestring': case 'geography_polygon':
      case 'geography_multipoint': case 'geography_multilinestring': case 'geography_multipolygon': case 'geography_collection':
        return 'success';
      case 'box2d': case 'box3d': case 'raster': return 'success';
      case 'json': case 'uuid': return 'info';
      default: return 'default';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const renderContent = () => (
    <>
      {hasEmptyFields && (
        <Alert severity="info" sx={{ mb: 2 }}>
          <Typography variant="body2">
            AI detected some fields with empty data. You can manually select the appropriate data type for these fields.
          </Typography>
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
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
                        color={getConfidenceColor(mapping.confidence)}
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
                            <Typography variant="body2">Loading data types...</Typography>
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
                  <Box display="flex" flexDirection="column" gap={0.5}>
                    {mapping.uniqueCount > 0 && (
                      <Typography variant="caption" color="textSecondary">
                        {mapping.uniqueCount} unique values
                      </Typography>
                    )}
                    {mapping.isEmpty && mapping.totalCount > 0 && (
                      <Typography variant="caption" color="warning.main">
                        {mapping.emptyCount}/{mapping.totalCount} empty values
                      </Typography>
                    )}
                    {mapping.reason && (
                      <Typography variant="caption" color="info.main">
                        {mapping.reason}
                      </Typography>
                    )}
                  </Box>
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

      {/* Field Detail Edit Dialog */}
      {editingField !== null && (
        <Dialog 
          open={editingField !== null} 
          onClose={cancelEdit}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Edit Field Details</DialogTitle>
          <DialogContent>
            <Box display="flex" flexDirection="column" gap={2} sx={{ mt: 1 }}>
              <TextField
                label="Display Name"
                value={mappings.find(m => m.id === editingField)?.displayName || ''}
                onChange={(e) => handleFieldUpdate(editingField, { displayName: e.target.value })}
                fullWidth
              />
              
              <TextField
                label="Default Value"
                value={mappings.find(m => m.id === editingField)?.defaultValue || ''}
                onChange={(e) => handleFieldUpdate(editingField, { defaultValue: e.target.value })}
                fullWidth
              />
              
              <TextField
                label="Constraints"
                value={mappings.find(m => m.id === editingField)?.constraints || ''}
                onChange={(e) => handleFieldUpdate(editingField, { constraints: e.target.value })}
                fullWidth
                multiline
                rows={2}
              />
              
              <TextField
                label="Description"
                value={mappings.find(m => m.id === editingField)?.description || ''}
                onChange={(e) => handleFieldUpdate(editingField, { description: e.target.value })}
                fullWidth
                multiline
                rows={3}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={cancelEdit}>Cancel</Button>
            <Button onClick={saveEdit} variant="contained">Save</Button>
          </DialogActions>
        </Dialog>
      )}
    </>
  );

  if (embedded) {
    return renderContent();
  }

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="lg" 
      fullWidth
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <InfoIcon color="primary" />
          <Typography variant="h6">
            Enhanced Field Mapping - {structureName}
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        {renderContent()}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button 
          onClick={handleSaveMapping} 
          variant="contained" 
          startIcon={<SaveIcon />}
        >
          Save Field Mappings
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EnhancedFieldMapping; 