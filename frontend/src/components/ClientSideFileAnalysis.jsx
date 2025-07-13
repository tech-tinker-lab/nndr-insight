import React, { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import {
  Upload as UploadIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Info as InfoIcon
} from '@mui/icons-material';

const ClientSideFileAnalysis = ({ onAnalysisComplete, onMappingsGenerated, onSwitchToServer }) => {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [mappings, setMappings] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [severity, setSeverity] = useState('info');
  const [progress, setProgress] = useState(0);

  const showMessage = (msg, sev = 'info') => {
    setMessage(msg);
    setSeverity(sev);
    setTimeout(() => setMessage(''), 5000);
  };

  // Client-side CSV analysis with dynamic row limits
  const analyzeCSV = async (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      // Dynamic row limits based on file size
      const fileSizeMB = file.size / (1024 * 1024);
      let maxRows = 1000; // Default for small files
      
      if (fileSizeMB > 100) {
        maxRows = 500; // Reduce for very large files
      } else if (fileSizeMB > 50) {
        maxRows = 750; // Medium files
      } else if (fileSizeMB < 1) {
        maxRows = 2000; // Very small files, analyze more rows
      }
      
      console.log(`CSV analysis: File size ${fileSizeMB.toFixed(1)}MB, analyzing up to ${maxRows} rows`);
      
      let rows = [];
      let headers = [];
      let fieldAnalysis = [];

      reader.onload = (e) => {
        try {
          console.log('CSV analysis: File loaded successfully');
          const content = e.target.result;
          console.log('CSV analysis: Content length:', content.length);
          
          if (!content || content.trim().length === 0) {
            throw new Error('File is empty or contains no readable content');
          }
          
          const lines = content.split('\n');
          console.log('CSV analysis: Number of lines:', lines.length);
          
          if (lines.length === 0) {
            throw new Error('No lines found in file');
          }
          
          // Detect delimiter
          const firstLine = lines[0];
          console.log('CSV analysis: First line:', firstLine.substring(0, 100) + '...');
          
          const delimiters = [',', ';', '\t', '|'];
          let delimiter = ',';
          let maxFields = 0;
          
          for (const delim of delimiters) {
            const fieldCount = firstLine.split(delim).length;
            if (fieldCount > maxFields) {
              maxFields = fieldCount;
              delimiter = delim;
            }
          }
          
          console.log('CSV analysis: Detected delimiter:', delimiter, 'with', maxFields, 'fields');

          // Parse headers
          headers = lines[0].split(delimiter).map(h => h.trim().replace(/"/g, ''));
          console.log('CSV analysis: Headers:', headers);
          
          if (headers.length === 0) {
            throw new Error('No headers found in file');
          }
          
          // Parse sample rows
          const sampleLines = lines.slice(1, Math.min(maxRows + 1, lines.length));
          rows = sampleLines
            .filter(line => line.trim())
            .map(line => line.split(delimiter).map(cell => cell.trim().replace(/"/g, '')));
          
          console.log('CSV analysis: Parsed', rows.length, 'rows');

          // Analyze each field
          fieldAnalysis = headers.map((header, index) => {
            const values = rows.map(row => row[index]).filter(val => val !== undefined && val !== '');
            const uniqueValues = [...new Set(values)];
            
            // Determine data type
            let dataType = 'text';
            let sampleValues = values.slice(0, 5);
            
            if (values.length > 0) {
              const firstValue = values[0];
              
              // Check for numeric
              if (values.every(val => !isNaN(val) && val !== '')) {
                if (values.every(val => Number.isInteger(parseFloat(val)))) {
                  dataType = 'integer';
                } else {
                  dataType = 'decimal';
                }
              }
              // Check for date
              else if (values.every(val => {
                const date = new Date(val);
                return !isNaN(date.getTime());
              })) {
                dataType = 'date';
              }
              // Check for boolean
              else if (values.every(val => ['true', 'false', 'yes', 'no', '1', '0'].includes(val.toLowerCase()))) {
                dataType = 'boolean';
              }
              // Check for coordinates
              else if (header.toLowerCase().includes('lat') || header.toLowerCase().includes('long') || 
                       header.toLowerCase().includes('x') || header.toLowerCase().includes('y')) {
                dataType = 'coordinate';
              }
              // Check for postcodes
              else if (header.toLowerCase().includes('postcode') || header.toLowerCase().includes('zip')) {
                dataType = 'postcode';
              }
            }

            return {
              field_name: header,
              display_name: header.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
              data_type: dataType,
              postgis_type: dataType === 'coordinate' ? 'POINT' : null,
              is_required: values.length === rows.length, // Field is required if it has values in all rows
              is_primary_key: index === 0, // First field as primary key
              default_value: '',
              constraints: '',
              description: `Auto-detected ${dataType} field`,
              sample_values: sampleValues,
              unique_count: uniqueValues.length,
              null_count: rows.length - values.length
            };
          });

          console.log('CSV analysis: Field analysis complete,', fieldAnalysis.length, 'fields');

          resolve({
            format: 'csv',
            has_header: true,
            delimiter: delimiter,
            field_count: headers.length,
            row_count: rows.length,
            field_analysis: fieldAnalysis,
            sample_rows: rows.slice(0, 5),
            headers: headers,
            file_size: file.size,
            filename: file.name
          });

        } catch (error) {
          console.error('CSV analysis error:', error);
          reject(new Error(`CSV parsing error: ${error.message}`));
        }
      };

      reader.onerror = (error) => {
        console.error('FileReader error:', error);
        reject(new Error(`File reading failed: ${error.target?.error?.message || 'Unknown error'}`));
      };
      
      reader.onabort = () => {
        console.error('FileReader aborted');
        reject(new Error('File reading was aborted'));
      };
      
      console.log('CSV analysis: Starting file read for', file.name, 'size:', file.size);
      reader.readAsText(file);
    });
  };

  // Client-side JSON analysis
  const analyzeJSON = async (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          console.log('JSON analysis: File loaded successfully');
          const content = e.target.result;
          console.log('JSON analysis: Content length:', content.length);
          
          if (!content || content.trim().length === 0) {
            throw new Error('File is empty or contains no readable content');
          }
          
          const data = JSON.parse(content);
          console.log('JSON analysis: Parsed JSON successfully');
          
          let fieldAnalysis = [];
          let sampleRows = [];
          
          if (Array.isArray(data)) {
            console.log('JSON analysis: Array of objects, length:', data.length);
            // Array of objects
            const firstItem = data[0] || {};
            const keys = Object.keys(firstItem);
            console.log('JSON analysis: Object keys:', keys);
            
            fieldAnalysis = keys.map((key, index) => {
              const values = data.slice(0, 100).map(item => item[key]).filter(val => val !== undefined && val !== null);
              const uniqueValues = [...new Set(values)];
              
              let dataType = 'text';
              if (values.length > 0) {
                const firstValue = values[0];
                if (typeof firstValue === 'number') {
                  dataType = Number.isInteger(firstValue) ? 'integer' : 'decimal';
                } else if (typeof firstValue === 'boolean') {
                  dataType = 'boolean';
                } else if (firstValue instanceof Date || !isNaN(new Date(firstValue).getTime())) {
                  dataType = 'date';
                }
              }

              return {
                field_name: key,
                display_name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                data_type: dataType,
                postgis_type: null,
                is_required: true,
                is_primary_key: index === 0,
                default_value: '',
                constraints: '',
                description: `Auto-detected ${dataType} field`,
                sample_values: values.slice(0, 5),
                unique_count: uniqueValues.length,
                null_count: 0
              };
            });
            
            sampleRows = data.slice(0, 5);
          } else {
            console.log('JSON analysis: Single object');
            // Single object
            const keys = Object.keys(data);
            fieldAnalysis = keys.map((key, index) => ({
              field_name: key,
              display_name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
              data_type: typeof data[key],
              postgis_type: null,
              is_required: true,
              is_primary_key: index === 0,
              default_value: '',
              constraints: '',
              description: `Auto-detected field`,
              sample_values: [data[key]],
              unique_count: 1,
              null_count: 0
            }));
            
            sampleRows = [data];
          }

          console.log('JSON analysis: Field analysis complete,', fieldAnalysis.length, 'fields');

          resolve({
            format: 'json',
            has_header: false,
            field_count: fieldAnalysis.length,
            row_count: Array.isArray(data) ? data.length : 1,
            field_analysis: fieldAnalysis,
            sample_rows: sampleRows,
            headers: fieldAnalysis.map(f => f.field_name),
            file_size: file.size,
            filename: file.name
          });

        } catch (error) {
          console.error('JSON analysis error:', error);
          reject(new Error(`JSON parsing error: ${error.message}`));
        }
      };

      reader.onerror = (error) => {
        console.error('FileReader error:', error);
        reject(new Error(`File reading failed: ${error.target?.error?.message || 'Unknown error'}`));
      };
      
      reader.onabort = () => {
        console.error('FileReader aborted');
        reject(new Error('File reading was aborted'));
      };
      
      console.log('JSON analysis: Starting file read for', file.name, 'size:', file.size);
      reader.readAsText(file);
    });
  };

  const handleFileUpload = useCallback(async (event) => {
    const uploadedFile = event.target.files[0];
    if (!uploadedFile) return;

    console.log('File upload started:', uploadedFile.name, 'size:', uploadedFile.size, 'type:', uploadedFile.type);

    // Dynamic file size handling for wide range (KB to GB)
    const fileSizeMB = uploadedFile.size / (1024 * 1024);
    const maxClientSize = 2 * 1024; // 2GB limit for client-side processing
    const warningSize = 500; // 500MB warning threshold
    
    if (uploadedFile.size > maxClientSize * 1024 * 1024) {
      showMessage(`File size (${fileSizeMB.toFixed(1)}MB) is very large. Consider using server-side analysis for better performance with files over 2GB.`, 'warning');
      // Don't block, just warn and continue
    } else if (uploadedFile.size > warningSize * 1024 * 1024) {
      showMessage(`Large file detected (${fileSizeMB.toFixed(1)}MB). Client-side processing may take longer.`, 'info');
    } else if (uploadedFile.size < 1024) {
      showMessage(`Small file detected (${uploadedFile.size} bytes). Processing should be very fast.`, 'info');
    }

    // Validate file type
    const fileExtension = uploadedFile.name.split('.').pop().toLowerCase();
    if (!['csv', 'json'].includes(fileExtension)) {
      showMessage('Please upload a CSV or JSON file.', 'error');
      return;
    }

    setFile(uploadedFile);
    setLoading(true);
    setAnalysis(null);
    setMappings(null);
    setProgress(0);

    try {
      showMessage('Analyzing file locally... This should be fast!', 'info');

      let analysisData;
      const fileExtension = uploadedFile.name.split('.').pop().toLowerCase();

      console.log('File extension detected:', fileExtension);

      setProgress(25);

      if (fileExtension === 'csv') {
        console.log('Starting CSV analysis...');
        analysisData = await analyzeCSV(uploadedFile);
      } else if (fileExtension === 'json') {
        console.log('Starting JSON analysis...');
        analysisData = await analyzeJSON(uploadedFile);
      } else {
        throw new Error(`Unsupported file format: ${fileExtension}. Please upload a CSV or JSON file.`);
      }

      console.log('Analysis completed successfully:', analysisData);

      setProgress(75);

      // Generate mappings
      const mappingsData = {
        field_mappings: analysisData.field_analysis.map(field => ({
          source_field: field.field_name,
          target_field: field.field_name.toLowerCase().replace(/[^a-z0-9]/g, '_'),
          data_type: field.data_type,
          postgis_type: field.postgis_type,
          is_required: field.is_required,
          is_primary_key: field.is_primary_key,
          default_value: field.default_value,
          constraints: field.constraints,
          description: field.description
        })),
        table_name: uploadedFile.name.split('.')[0].toLowerCase().replace(/[^a-z0-9]/g, '_'),
        schema_type: 'staging'
      };

      console.log('Mappings generated:', mappingsData);

      setProgress(100);

      setAnalysis(analysisData);
      setMappings(mappingsData);

      if (onAnalysisComplete) {
        onAnalysisComplete(analysisData);
      }

      if (onMappingsGenerated) {
        onMappingsGenerated(mappingsData);
      }

      showMessage('File analyzed successfully!', 'success');

    } catch (error) {
      console.error('File analysis failed:', error);
      let errorMessage = error.message;
      
      // Provide more helpful error messages
      if (errorMessage.includes('File reading failed')) {
        errorMessage = 'Unable to read the file. Please ensure the file is not corrupted and try again.';
      } else if (errorMessage.includes('JSON parsing error')) {
        errorMessage = 'Invalid JSON format. Please check your JSON file and try again.';
      } else if (errorMessage.includes('CSV parsing error')) {
        errorMessage = 'Invalid CSV format. Please check your CSV file and try again.';
      } else if (errorMessage.includes('Unsupported file format')) {
        errorMessage = 'Please upload a CSV or JSON file.';
      }
      
      setAnalysis({ error: errorMessage });
      showMessage('Analysis failed: ' + errorMessage, 'error');
    } finally {
      setLoading(false);
      setProgress(0);
    }
  }, [onAnalysisComplete, onMappingsGenerated]);

  const resetAnalysis = () => {
    setFile(null);
    setAnalysis(null);
    setMappings(null);
    setMessage('');
    setProgress(0);
  };

  const getDataTypeColor = (dataType) => {
    switch (dataType) {
      case 'integer': return 'primary';
      case 'decimal': return 'secondary';
      case 'date': return 'success';
      case 'boolean': return 'warning';
      case 'coordinate': return 'info';
      case 'postcode': return 'default';
      default: return 'default';
    }
  };

  return (
    <Card variant="outlined" sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
          <Typography variant="h6">Client-Side File Analysis</Typography>
          {file && (
            <Tooltip title="Reset analysis">
              <IconButton onClick={resetAnalysis} size="small">
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>

        {!file ? (
          <Box
            sx={{
              border: '2px dashed #ccc',
              borderRadius: 2,
              p: 3,
              textAlign: 'center',
              cursor: 'pointer',
              '&:hover': { borderColor: '#999' }
            }}
            onClick={() => document.getElementById('client-file-upload').click()}
          >
            <input
              id="client-file-upload"
              type="file"
              accept=".csv,.json"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
            <UploadIcon sx={{ fontSize: 48, color: '#666', mb: 1 }} />
            <Typography variant="h6" color="textSecondary" gutterBottom>
              Upload File for Local Analysis
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Supported formats: CSV, JSON (processed locally - no server timeout!)
            </Typography>
            <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
              Handles files from KB to GB | Large files may take longer to process
            </Typography>
          </Box>
        ) : (
          <Box>
            <Typography variant="body1" gutterBottom>
              <strong>File:</strong> {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
            </Typography>
            
            {loading && (
              <Box sx={{ mt: 2 }}>
                <Box display="flex" alignItems="center" gap={2} sx={{ mb: 1 }}>
                  <CircularProgress size={20} />
                  <Typography variant="body2">
                    Analyzing file locally... {progress}%
                    {file && file.size > 50 * 1024 * 1024 && (
                      <span style={{ color: 'orange' }}> (Large file - this may take a moment)</span>
                    )}
                  </Typography>
                </Box>
                <Box sx={{ width: '100%', bgcolor: '#f0f0f0', borderRadius: 1 }}>
                  <Box sx={{ width: `${progress}%`, height: 8, bgcolor: 'primary.main', borderRadius: 1, transition: 'width 0.3s' }} />
                </Box>
                {file && file.size > 100 * 1024 * 1024 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mb: 1 }}>
                      💡 Tip: For very large files, consider using server-side analysis for faster processing
                    </Typography>
                    {onSwitchToServer && (
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => onSwitchToServer(file)}
                        sx={{ fontSize: '0.75rem' }}
                      >
                        Switch to Server Analysis
                      </Button>
                    )}
                  </Box>
                )}
              </Box>
            )}

            {analysis && !analysis.error && (
              <Alert severity="success" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  File analyzed successfully! Detected {analysis.field_count || 0} fields from {analysis.row_count || 0} rows.
                </Typography>
              </Alert>
            )}

            {analysis?.error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Analysis failed: {analysis.error}
                </Typography>
                <Box sx={{ mt: 1 }}>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => {
                      setAnalysis(null);
                      setMappings(null);
                      setProgress(0);
                      // Retry the analysis
                      const event = { target: { files: [file] } };
                      handleFileUpload(event);
                    }}
                  >
                    Retry Analysis
                  </Button>
                  <Button
                    size="small"
                    variant="text"
                    onClick={() => {
                      console.log('File analysis debug info:', {
                        fileName: file?.name,
                        fileSize: file?.size,
                        fileType: file?.type,
                        lastModified: file?.lastModified
                      });
                    }}
                    sx={{ ml: 1 }}
                  >
                    Debug Info
                  </Button>
                </Box>
              </Alert>
            )}

            {analysis && !analysis.error && analysis.field_analysis && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>Field Analysis</Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Field Name</TableCell>
                        <TableCell>Data Type</TableCell>
                        <TableCell>Required</TableCell>
                        <TableCell>Primary Key</TableCell>
                        <TableCell>Sample Values</TableCell>
                        <TableCell>Unique Count</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {analysis.field_analysis.map((field, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                              {field.field_name}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={field.data_type} 
                              size="small" 
                              color={getDataTypeColor(field.data_type)}
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>
                            {field.is_required ? (
                              <CheckIcon color="success" fontSize="small" />
                            ) : (
                              <WarningIcon color="warning" fontSize="small" />
                            )}
                          </TableCell>
                          <TableCell>
                            {field.is_primary_key ? (
                              <CheckIcon color="primary" fontSize="small" />
                            ) : (
                              <InfoIcon color="disabled" fontSize="small" />
                            )}
                          </TableCell>
                          <TableCell>
                            <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                              {field.sample_values?.slice(0, 3).join(', ')}
                              {field.sample_values?.length > 3 && '...'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {field.unique_count}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
          </Box>
        )}

        {message && (
          <Alert severity={severity} sx={{ mt: 2 }}>
            {message}
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default ClientSideFileAnalysis; 