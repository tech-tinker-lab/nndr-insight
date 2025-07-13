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
  Tooltip
} from '@mui/material';
import {
  Upload as UploadIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import api from '../api/axios';

const FileAnalysisSection = ({ onAnalysisComplete, onMappingsGenerated }) => {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [mappings, setMappings] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [severity, setSeverity] = useState('info');

  const showMessage = (msg, sev = 'info') => {
    setMessage(msg);
    setSeverity(sev);
    setTimeout(() => setMessage(''), 5000);
  };

  const handleFileUpload = useCallback(async (event) => {
    const uploadedFile = event.target.files[0];
    if (!uploadedFile) return;

    setFile(uploadedFile);
    setLoading(true);
    setAnalysis(null);
    setMappings(null);

    try {
      showMessage('Analyzing file... This should take just a few seconds.', 'info');

      const formData = new FormData();
      formData.append('file', uploadedFile);

      const analysisResponse = await Promise.race([
        api.post('/api/design-enhanced/ai/analyze-file', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
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
      
      let errorMessage = 'Analysis failed';
      if (error.response) {
        errorMessage = error.response.data?.detail || error.response.data?.message || error.response.statusText;
      } else if (error.request) {
        errorMessage = 'Network error - please check your connection';
      } else {
        errorMessage = error.message || 'Unknown error occurred';
      }
      
      setAnalysis({ error: errorMessage });
      showMessage('Analysis failed: ' + errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  }, [onAnalysisComplete]);

  const generateMappings = async (analysisData) => {
    try {
      setLoading(true);

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

      if (onMappingsGenerated) {
        onMappingsGenerated(mappingsData);
      }

    } catch (error) {
      console.error('Mapping generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const resetAnalysis = () => {
    setFile(null);
    setAnalysis(null);
    setMappings(null);
    setMessage('');
  };

  return (
    <Card variant="outlined" sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
          <Typography variant="h6">File Analysis</Typography>
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
            onClick={() => document.getElementById('file-upload').click()}
          >
            <input
              id="file-upload"
              type="file"
              accept=".csv,.json,.xml,.zip,.dbf,.shp"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
            <UploadIcon sx={{ fontSize: 48, color: '#666', mb: 1 }} />
            <Typography variant="h6" color="textSecondary" gutterBottom>
              Upload File for Analysis
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Supported formats: CSV, JSON, XML, ZIP, DBF, Shapefile
            </Typography>
          </Box>
        ) : (
          <Box>
            <Typography variant="body1" gutterBottom>
              <strong>File:</strong> {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
            </Typography>
            
            {loading && (
              <Box display="flex" alignItems="center" gap={2} sx={{ mt: 2 }}>
                <CircularProgress size={20} />
                <Typography variant="body2">Analyzing file...</Typography>
              </Box>
            )}

            {analysis && !analysis.error && (
              <Alert severity="success" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  File analyzed successfully! AI has detected {analysis.field_count || 0} fields and identified {analysis.identified_standards?.length || 0} data standards.
                  {analysis.primary_governing_body && ` Primary governing body: ${analysis.primary_governing_body}`}
                  {analysis.data_quality && ` Data quality: ${analysis.data_quality.overall_rating}`}
                </Typography>
              </Alert>
            )}

            {analysis?.error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                Analysis failed: {analysis.error}
              </Alert>
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

export default FileAnalysisSection; 