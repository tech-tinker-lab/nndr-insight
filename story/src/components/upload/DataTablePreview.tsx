import React from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Chip,
} from '@mui/material';

interface DataTablePreviewProps {
  preview: {
    headers: string[];
    data: string[][];
  };
  showMappingOptions?: boolean;
  columnMappings?: Record<string, string>;
}

const DataTablePreview: React.FC<DataTablePreviewProps> = ({ preview, showMappingOptions, columnMappings = {} }) => (
  <TableContainer 
    component={Paper} 
    sx={{ 
      maxHeight: 256, 
      overflow: 'auto',
      border: '1px solid',
      borderColor: 'divider'
    }}
  >
    <Table size="small" stickyHeader>
      <TableHead>
        <TableRow>
          {preview.headers.map((header, idx) => (
            <TableCell 
              key={idx} 
              sx={{ 
                fontSize: '0.75rem',
                fontWeight: 600,
                backgroundColor: 'grey.100',
                position: 'sticky',
                top: 0,
                zIndex: 1
              }}
            >
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                <Typography variant="caption" sx={{ fontSize: '0.75rem', fontWeight: 600 }}>
                  {header}
                </Typography>
                {showMappingOptions && (
                  <Chip 
                    label={columnMappings[header] || 'TEXT'} 
                    size="small"
                    variant="outlined"
                    color="primary"
                    sx={{ 
                      fontSize: '0.625rem',
                      height: 20,
                      '& .MuiChip-label': {
                        px: 1,
                        fontSize: '0.625rem'
                      }
                    }}
                  />
                )}
              </Box>
            </TableCell>
          ))}
        </TableRow>
      </TableHead>
      <TableBody>
        {preview.data.map((row, rowIdx) => (
          <TableRow 
            key={rowIdx} 
            sx={{ 
              '&:nth-of-type(odd)': { backgroundColor: 'grey.50' },
              '&:hover': { backgroundColor: 'grey.100' }
            }}
          >
            {row.map((cell, cellIdx) => (
              <TableCell 
                key={cellIdx}
                sx={{ 
                  fontSize: '0.75rem',
                  py: 0.5,
                  px: 1,
                  color: 'text.primary'
                }}
              >
                <Box 
                  sx={{ 
                    maxWidth: '200px', 
                    overflow: 'hidden', 
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}
                  title={cell}
                >
                  {cell || ''}
                </Box>
              </TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  </TableContainer>
);

export default DataTablePreview;
