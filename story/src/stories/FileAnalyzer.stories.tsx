import type { Meta, StoryObj } from '@storybook/react';
import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import FileAnalyzer from '../components/upload/FileAnalyzer';

// Demo component to showcase FileAnalyzer functionality
const FileAnalyzerDemo: React.FC<{ sampleData?: string; fileName?: string }> = ({ 
  sampleData = '', 
  fileName = 'sample.csv' 
}) => {
  const [csvText, setCsvText] = useState(sampleData);
  const [analysis, setAnalysis] = useState<any>(null);

  const handleAnalyze = () => {
    if (csvText.trim()) {
      const result = FileAnalyzer.analyzeCSV(csvText, fileName);
      setAnalysis(result);
    }
  };

  const handleGetFileIcon = (filename: string) => {
    const IconComponent = FileAnalyzer.getFileIcon(filename);
    return <IconComponent className="w-6 h-6" />;
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          CSV File Analyzer Demo
        </Typography>
        <TextField
          label="CSV Content"
          multiline
          rows={6}
          fullWidth
          value={csvText}
          onChange={(e) => setCsvText(e.target.value)}
          placeholder="Paste your CSV content here..."
          variant="outlined"
          sx={{ mb: 2 }}
        />
        <Button
          variant="contained"
          onClick={handleAnalyze}
          disabled={!csvText.trim()}
        >
          Analyze CSV
        </Button>
      </Box>

      {analysis && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Analysis Results
          </Typography>
          
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2, mb: 3 }}>
            <Box>
              <Typography variant="subtitle2">Filename:</Typography>
              <Typography variant="body2">{analysis.filename}</Typography>
            </Box>
            <Box>
              <Typography variant="subtitle2">Format:</Typography>
              <Typography variant="body2">{analysis.format}</Typography>
            </Box>
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              File Icon:
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {handleGetFileIcon(analysis.filename)}
              <Typography variant="body2">{analysis.filename}</Typography>
            </Box>
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              Headers ({analysis.headers.length}):
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {analysis.headers.map((header: string, i: number) => (
                <Chip key={i} label={header} size="small" variant="outlined" />
              ))}
            </Box>
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              Data Structure:
            </Typography>
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Column</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Type</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Sample Values</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(analysis.structure).map(([column, info]: [string, any]) => (
                    <TableRow key={column}>
                      <TableCell sx={{ fontWeight: 500 }}>{column}</TableCell>
                      <TableCell>
                        <Chip 
                          label={info.type}
                          size="small"
                          color={
                            info.type === 'integer' ? 'primary' :
                            info.type === 'float' ? 'success' :
                            info.type === 'boolean' ? 'secondary' :
                            'default'
                          }
                        />
                      </TableCell>
                      <TableCell>
                        {info.sample.slice(0, 3).join(', ')}
                        {info.sample.length > 3 ? '...' : ''}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>

          <Box>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              Sample Rows ({analysis.sampleRows.length}):
            </Typography>
            <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 300 }}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    {analysis.headers.map((header: string, i: number) => (
                      <TableCell key={i} sx={{ fontWeight: 600, backgroundColor: 'grey.100' }}>
                        {header}
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {analysis.sampleRows.map((row: string[], i: number) => (
                    <TableRow key={i}>
                      {row.map((cell: string, j: number) => (
                        <TableCell key={j} sx={{ fontSize: '0.875rem' }}>
                          {cell}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        </Box>
      )}
    </Paper>
  );
};

const meta: Meta<typeof FileAnalyzerDemo> = {
  title: 'Upload/FileAnalyzer',
  component: FileAnalyzerDemo,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    sampleData: {
      description: 'Sample CSV content to analyze',
      control: { type: 'text' },
    },
    fileName: {
      description: 'Name of the file being analyzed',
      control: { type: 'text' },
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    sampleData: `customer_id,customer_name,email,phone,created_date,is_active
1,John Doe,john@example.com,+1-555-0101,2023-01-15,true
2,Jane Smith,jane@example.com,+1-555-0102,2023-02-20,false
3,Bob Johnson,bob@example.com,+1-555-0103,2023-03-10,true
4,Alice Brown,alice@example.com,+1-555-0104,2023-04-05,true
5,Charlie Wilson,charlie@example.com,+1-555-0105,2023-05-12,false`,
    fileName: 'customers.csv',
  },
};

export const GeospatialData: Story = {
  args: {
    sampleData: `property_id,address,latitude,longitude,lot_size_sqft,zoning_code,has_pool
1001,123 Main St,40.7128,-74.0060,5000.5,R1,false
1002,456 Oak Ave,34.0522,-118.2437,7500.0,R2,true
1003,789 Pine Rd,41.8781,-87.6298,6200.25,C1,false
1004,321 Elm St,29.7604,-95.3698,4800.75,R1,false
1005,654 Maple Dr,39.9526,-75.1652,8900.0,R3,true`,
    fileName: 'properties.geojson',
  },
};

export const FinancialData: Story = {
  args: {
    sampleData: `transaction_id,account_number,amount,currency,transaction_date,is_verified,transaction_type
10001,ACC-001,1250.50,USD,2023-12-01,true,debit
10002,ACC-002,2500.00,EUR,2023-12-02,true,credit
10003,ACC-003,750.25,GBP,2023-12-03,false,debit
10004,ACC-004,3200.75,USD,2023-12-04,true,credit
10005,ACC-005,900.00,CAD,2023-12-05,false,debit`,
    fileName: 'transactions.xlsx',
  },
};

export const EmptyCSV: Story = {
  args: {
    sampleData: '',
    fileName: 'empty.csv',
  },
};

export const SingleColumnCSV: Story = {
  args: {
    sampleData: `id
1
2
3
4
5`,
    fileName: 'single_column.csv',
  },
};

export const MixedDataTypes: Story = {
  args: {
    sampleData: `id,name,score,active,created_at,coordinates
1,Product A,95.5,true,2023-01-01,40.7128
2,Product B,87.2,false,2023-01-02,34.0522
3,Product C,92.8,true,2023-01-03,41.8781
4,Product D,88.1,true,2023-01-04,29.7604
5,Product E,91.3,false,2023-01-05,39.9526`,
    fileName: 'mixed_data.csv',
  },
};
