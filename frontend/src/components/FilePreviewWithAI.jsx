import React, { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Switch,
  FormControlLabel,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Upload as UploadIcon,
  Visibility as ViewIcon,
  Settings as SettingsIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon
} from '@mui/icons-material';
import api from '../api/axios';

const FilePreviewWithAI = ({ onAnalysisComplete, onMappingsGenerated }) => {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [mappings, setMappings] = useState(null);
  const [loading, setLoading] = useState(false);
  const [previewRows, setPreviewRows] = useState(10);
  const [showAllFields, setShowAllFields] = useState(false);
  const [selectedFields, setSelectedFields] = useState([]);
  const [message, setMessage] = useState('');
  const [severity, setSeverity] = useState('info');

  const showMessage = (msg, sev = 'info') => {
    setMessage(msg);
    setSeverity(sev);
    // Auto-clear messages after 5 seconds
    setTimeout(() => setMessage(''), 5000);
  };

  // Handle file upload and immediate analysis
  const handleFileUpload = useCallback(async (event) => {
    const uploadedFile = event.target.files[0];
    if (!uploadedFile) return;

    setFile(uploadedFile);
    setLoading(true);
    setAnalysis(null);
    setMappings(null);

    try {
      // Show progress message
      showMessage('Analyzing file... This should take just a few seconds.', 'info');

      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', uploadedFile);

      // Get AI analysis with timeout
      const analysisResponse = await Promise.race([
        api.post('/api/design-enhanced/ai/analyze-file', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Analysis timeout - file may be too large')), 30000)
        )
      ]);

      const analysisData = analysisResponse.data.analysis;
      setAnalysis(analysisData);

      // Auto-generate mappings if we have field analysis
      if (analysisData.field_analysis && analysisData.field_analysis.length > 0) {
        await generateMappings(analysisData);
      }

      if (onAnalysisComplete) {
        onAnalysisComplete(analysisData);
      }

      showMessage('File analyzed successfully!', 'success');

    } catch (error) {
      console.error('File analysis failed:', error);
      
      // Extract more detailed error information
      let errorMessage = 'Analysis failed';
      if (error.response) {
        // Server responded with error
        errorMessage = error.response.data?.detail || error.response.data?.message || error.response.statusText;
      } else if (error.request) {
        // Network error
        errorMessage = 'Network error - please check your connection';
      } else {
        // Other error
        errorMessage = error.message || 'Unknown error occurred';
      }
      
      setAnalysis({ error: errorMessage });
      showMessage('Analysis failed: ' + errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  }, [onAnalysisComplete]);

  // Generate field mappings
  const generateMappings = async (analysisData) => {
    try {
      setLoading(true);

      // For single file analysis, create a simplified mapping request
      const mappingRequest = {
        header_file: file.name,
        data_files: [file.name],
        analysis_data: {
          ...analysisData,
          file_previews: {
            [file.name]: {
              format: analysisData.format,
              headers: analysisData.field_analysis?.map(field => field.field_name) || [],
              sample_rows: analysisData.sample_rows || [],
              has_header: analysisData.has_header || false
            }
          }
        }
      };

      const mappingResponse = await api.post('/api/design-enhanced/ai/generate-mappings', mappingRequest);
      const mappingsData = mappingResponse.data.mappings;
      setMappings(mappingsData);

      // Auto-select all fields for 1-to-1 mapping
      const allFields = mappingsData.field_mappings.map(mapping => mapping.source_field);
      setSelectedFields(allFields);

      if (onMappingsGenerated) {
        onMappingsGenerated(mappingsData);
      }

    } catch (error) {
      console.error('Mapping generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle field selection for 1-to-1 mapping
  const handleFieldSelection = (fieldName, checked) => {
    if (checked) {
      setSelectedFields([...selectedFields, fieldName]);
    } else {
      setSelectedFields(selectedFields.filter(field => field !== fieldName));
    }
  };

  // Handle select all fields
  const handleSelectAllFields = () => {
    if (mappings?.field_mappings) {
      const allFields = mappings.field_mappings.map(mapping => mapping.source_field);
      setSelectedFields(allFields);
    }
  };

  // Handle deselect all fields
  const handleDeselectAllFields = () => {
    setSelectedFields([]);
  };

  // Render file analysis results
  const renderAnalysisResults = () => {
    if (!analysis) return null;

    if (analysis.error) {
      return (
        <Alert severity="error" sx={{ mb: 2 }}>
          Analysis failed: {analysis.error}
        </Alert>
      );
    }

    return (
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            AI Analysis Results
          </Typography>

          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle2">Format</Typography>
              <Chip label={analysis.format} color="primary" size="small" />
            </Grid>
            {analysis.encoding && (
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="subtitle2">Encoding</Typography>
                <Typography variant="body2">{analysis.encoding}</Typography>
              </Grid>
            )}
            {analysis.delimiter && (
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="subtitle2">Delimiter</Typography>
                <Typography variant="body2">'{analysis.delimiter}'</Typography>
              </Grid>
            )}
            {analysis.field_count && (
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="subtitle2">Fields</Typography>
                <Typography variant="body2">{analysis.field_count}</Typography>
              </Grid>
            )}
          </Grid>

          {/* Data Standards */}
          {analysis.identified_standards && analysis.identified_standards.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>Identified Data Standards</Typography>
              {analysis.identified_standards.map((standard, index) => (
                <Chip
                  key={index}
                  label={`${standard.name} (${(standard.confidence * 100).toFixed(0)}%)`}
                  color={standard.confidence > 0.7 ? "success" : "warning"}
                  size="small"
                  sx={{ mr: 1, mb: 1 }}
                />
              ))}
            </Box>
          )}

          {/* Government Body Analysis */}
          {analysis.primary_governing_body && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>Primary Governing Body</Typography>
              <Chip
                label={analysis.primary_governing_body}
                color="primary"
                size="medium"
                sx={{ mr: 1 }}
              />
            </Box>
          )}

          {/* Compliance Analysis */}
          {analysis.compliance_analysis && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>Compliance Analysis</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2">
                    Overall Compliance: {(analysis.compliance_analysis.overall_compliance * 100).toFixed(0)}%
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2">
                    Standards Identified: {analysis.compliance_analysis.standards_count}
                  </Typography>
                </Grid>
              </Grid>
              {analysis.compliance_analysis.recommended_actions && analysis.compliance_analysis.recommended_actions.length > 0 && (
                <Alert severity="info" sx={{ mt: 1 }}>
                  <Typography variant="body2" gutterBottom>Recommended Actions:</Typography>
                  <ul style={{ margin: 0, paddingLeft: '20px' }}>
                    {analysis.compliance_analysis.recommended_actions.map((action, index) => (
                      <li key={index}>
                        <Typography variant="body2">{action}</Typography>
                      </li>
                    ))}
                  </ul>
                </Alert>
              )}
            </Box>
          )}

          {/* Data Quality Assessment */}
          {analysis.data_quality && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>Data Quality Assessment</Typography>
              <Grid container spacing={2} sx={{ mb: 1 }}>
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2">
                    Overall Rating: 
                    <Chip 
                      label={analysis.data_quality.overall_rating} 
                      color={analysis.data_quality.overall_rating === 'Excellent' ? 'success' : 
                             analysis.data_quality.overall_rating === 'Good' ? 'primary' :
                             analysis.data_quality.overall_rating === 'Fair' ? 'warning' : 'error'}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2">
                    Quality Score: {(analysis.data_quality.score * 100).toFixed(0)}%
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2">
                    Fields: {analysis.data_quality.field_count}
                  </Typography>
                </Grid>
              </Grid>
              
              {analysis.data_quality.strengths && analysis.data_quality.strengths.length > 0 && (
                <Alert severity="success" sx={{ mb: 1 }}>
                  <Typography variant="body2" gutterBottom>Strengths:</Typography>
                  <ul style={{ margin: 0, paddingLeft: '20px' }}>
                    {analysis.data_quality.strengths.map((strength, index) => (
                      <li key={index}>
                        <Typography variant="body2">{strength}</Typography>
                      </li>
                    ))}
                  </ul>
                </Alert>
              )}
              
              {analysis.data_quality.issues && analysis.data_quality.issues.length > 0 && (
                <Alert severity="warning" sx={{ mb: 1 }}>
                  <Typography variant="body2" gutterBottom>Issues:</Typography>
                  <ul style={{ margin: 0, paddingLeft: '20px' }}>
                    {analysis.data_quality.issues.map((issue, index) => (
                      <li key={index}>
                        <Typography variant="body2">{issue}</Typography>
                      </li>
                    ))}
                  </ul>
                </Alert>
              )}
            </Box>
          )}

          {/* Field Analysis */}
          {analysis.field_analysis && analysis.field_analysis.length > 0 && (
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>Field Analysis ({analysis.field_analysis.length} fields)</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <TableContainer component={Paper} sx={{ maxHeight: 300 }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Field Name</TableCell>
                        <TableCell>Detected Type</TableCell>
                        <TableCell>Sample Values</TableCell>
                        <TableCell>Confidence</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {analysis.field_analysis.map((field, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              {field.field_name || `Field ${index + 1}`}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={field.type || field.detected_type || 'unknown'} 
                              color={field.confidence > 0.8 ? "success" : "warning"}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="caption">
                              {field.sample_values?.slice(0, 3).join(', ')}
                              {field.sample_values?.length > 3 && '...'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="caption">
                              {((field.confidence || 0) * 100).toFixed(0)}%
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </AccordionDetails>
            </Accordion>
          )}
        </CardContent>
      </Card>
    );
  };

  // Render data preview
  const renderDataPreview = () => {
    if (!analysis) return null;

    // Handle different data structures from backend
    let sampleRows = [];
    let headers = [];
    
    if (analysis.sample_rows && Array.isArray(analysis.sample_rows)) {
      sampleRows = analysis.sample_rows;
      // If we have field analysis, use those field names as headers
      if (analysis.field_analysis && Array.isArray(analysis.field_analysis)) {
        headers = analysis.field_analysis.map(field => field.field_name || `Field ${field.sequence_order || 0}`);
      } else {
        // Fallback: use first row as headers if it looks like headers
        headers = sampleRows[0] || [];
      }
    } else if (analysis.field_analysis && Array.isArray(analysis.field_analysis)) {
      headers = analysis.field_analysis.map(field => field.field_name || `Field ${field.sequence_order || 0}`);
      
      // Create sample rows from field analysis, ensuring empty fields are included
      const maxSampleValues = Math.max(...analysis.field_analysis.map(field => 
        field.sample_values ? field.sample_values.length : 0
      ), 1);
      
      sampleRows = [];
      for (let i = 0; i < maxSampleValues; i++) {
        const row = [];
        for (const field of analysis.field_analysis) {
          if (field.sample_values && i < field.sample_values.length) {
            row.push(field.sample_values[i]);
          } else {
            // For empty fields or missing sample values, show "empty"
            row.push(field.type === 'empty' ? 'empty' : '');
          }
        }
        sampleRows.push(row);
      }
    }
    
    if (sampleRows.length === 0) return null;

    // For CSV data, skip the first row if it's a header
    const dataRows = analysis.has_header && sampleRows.length > 1 ? sampleRows.slice(1) : sampleRows;
    const displayRows = dataRows.slice(0, previewRows);
    const displayHeaders = showAllFields ? headers : headers.slice(0, 10);

    // Ensure all rows have the same number of columns as headers
    const normalizedRows = displayRows.map(row => {
      const normalizedRow = [...row];
      // Fill missing columns with empty values to match header count
      while (normalizedRow.length < displayHeaders.length) {
        normalizedRow.push('');
      }
      return normalizedRow;
    });

    return (
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">Data Preview</Typography>
            <Box>
              <FormControl size="small" sx={{ mr: 2, minWidth: 120 }}>
                <InputLabel>Preview Rows</InputLabel>
                <Select
                  value={previewRows}
                  onChange={(e) => setPreviewRows(e.target.value)}
                  label="Preview Rows"
                >
                  <MenuItem value={5}>5 rows</MenuItem>
                  <MenuItem value={10}>10 rows</MenuItem>
                  <MenuItem value={20}>20 rows</MenuItem>
                  <MenuItem value={50}>50 rows</MenuItem>
                </Select>
              </FormControl>
              <FormControlLabel
                control={
                  <Switch
                    checked={showAllFields}
                    onChange={(e) => setShowAllFields(e.target.checked)}
                  />
                }
                label="Show all fields"
              />
            </Box>
          </Box>

          <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
            <Table size="small" stickyHeader>
              <TableHead>
                <TableRow>
                  {displayHeaders.map((header, index) => (
                    <TableCell key={index} sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>
                      {header}
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {normalizedRows.map((row, rowIndex) => (
                  <TableRow key={rowIndex} hover>
                    {displayHeaders.map((header, colIndex) => (
                      <TableCell key={colIndex}>
                        {row[colIndex] || ''}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {!showAllFields && headers.length > 10 && (
            <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
              Showing first 10 of {headers.length} fields. Enable "Show all fields" to see all columns.
            </Typography>
          )}
        </CardContent>
      </Card>
    );
  };

  // Render field mappings
  const renderFieldMappings = () => {
    if (!mappings || !mappings.field_mappings) return null;

    return (
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">1-to-1 Field Mappings</Typography>
            <Box>
              <Button
                size="small"
                onClick={handleSelectAllFields}
                sx={{ mr: 1 }}
              >
                Select All
              </Button>
              <Button
                size="small"
                onClick={handleDeselectAllFields}
                sx={{ mr: 1 }}
              >
                Deselect All
              </Button>
              <Typography variant="caption" color="textSecondary">
                {selectedFields.length} of {mappings.field_mappings.length} fields selected
              </Typography>
            </Box>
          </Box>

          <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Select</TableCell>
                  <TableCell>Source Field</TableCell>
                  <TableCell>Staging Field</TableCell>
                  <TableCell>Data Type</TableCell>
                  <TableCell>PostGIS Type</TableCell>
                  <TableCell>Required</TableCell>
                  <TableCell>Primary Key</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {mappings.field_mappings.map((mapping, index) => (
                  <TableRow key={index} hover>
                    <TableCell>
                      <Switch
                        checked={selectedFields.includes(mapping.source_field)}
                        onChange={(e) => handleFieldSelection(mapping.source_field, e.target.checked)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {mapping.source_field}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="textSecondary">
                        {mapping.staging_field}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={mapping.data_type} 
                        color="primary" 
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {mapping.postgis_type ? (
                        <Chip 
                          label={mapping.postgis_type} 
                          color="secondary" 
                          size="small"
                        />
                      ) : (
                        <Typography variant="caption" color="textSecondary">
                          N/A
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Switch
                        checked={mapping.is_required}
                        size="small"
                        disabled
                      />
                    </TableCell>
                    <TableCell>
                      <Switch
                        checked={mapping.is_primary_key}
                        size="small"
                        disabled
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Recommendations */}
          {mappings.recommendations && mappings.recommendations.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>AI Recommendations</Typography>
              {mappings.recommendations.map((recommendation, index) => (
                <Alert key={index} severity="info" sx={{ mb: 1 }}>
                  {recommendation}
                </Alert>
              ))}
            </Box>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <Box>
      {/* Message Display */}
      {message && (
        <Alert severity={severity} sx={{ mb: 2 }}>
          {message}
        </Alert>
      )}

      {/* File Upload */}
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Upload File for AI Analysis
          </Typography>
          
          <input
            accept=".csv,.json,.xml,.txt,.gpkg,.shp,.zip,.yaml,.yml"
            style={{ display: 'none' }}
            id="file-upload"
            type="file"
            onChange={handleFileUpload}
          />
          <label htmlFor="file-upload">
            <Button
              variant="contained"
              component="span"
              startIcon={loading ? <CircularProgress size={20} /> : <UploadIcon />}
              disabled={loading}
            >
              {loading ? 'Analyzing...' : 'Choose File'}
            </Button>
          </label>

          {file && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="textSecondary">
                Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Loading State */}
      {loading && (
        <Box display="flex" justifyContent="center" sx={{ my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Analysis Results */}
      {analysis && !loading && renderAnalysisResults()}

      {/* Data Preview */}
      {analysis && !loading && renderDataPreview()}

      {/* Field Mappings */}
      {mappings && !loading && renderFieldMappings()}
    </Box>
  );
};

export default FilePreviewWithAI; 