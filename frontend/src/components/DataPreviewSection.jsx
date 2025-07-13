import React, { useState } from 'react';
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
  FormControlLabel
} from '@mui/material';

const DataPreviewSection = ({ analysis }) => {
  const [previewRows, setPreviewRows] = useState(10);
  const [showAllFields, setShowAllFields] = useState(false);

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

export default DataPreviewSection; 