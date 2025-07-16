import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert,
  Chip,
  Divider,
} from '@mui/material';
import type { SelectChangeEvent } from '@mui/material';

const DEFAULT_SCHEMAS = ['public', 'staging', 'archive'];

// Utility to map analyzer type to SQL type
const analyzerTypeToSQLType = (analyzerType: string): string => {
  switch (analyzerType) {
    case 'integer': return 'INTEGER';
    case 'float': return 'FLOAT';
    case 'boolean': return 'BOOLEAN';
    case 'date': return 'DATE';
    case 'geometry': return 'GEOMETRY';
    default: return 'TEXT';
  }
};

interface TableSQLGeneratorProps {
  mapping: Record<string, string>;
  structure: Record<string, { type: string }>;
  uniqueKey?: string;
  generatedSQL: string;
  setGeneratedSQL: (sql: string) => void;
}

const TableSQLGenerator: React.FC<TableSQLGeneratorProps> = ({ mapping, structure, uniqueKey, generatedSQL, setGeneratedSQL }) => {
  const [sqlTableName, setSqlTableName] = useState<string>('');
  const [sqlSchema, setSqlSchema] = useState<string>(DEFAULT_SCHEMAS[0]);
  const [tableExists, setTableExists] = useState<boolean | null>(null);
  const [sqlCheckLoading, setSqlCheckLoading] = useState<boolean>(false);
  const [sqlGenLoading, setSqlGenLoading] = useState<boolean>(false);
  const [availableSchemas, setAvailableSchemas] = useState<string[]>(DEFAULT_SCHEMAS);

  const checkTableExists = async () => {
    setSqlCheckLoading(true);
    try {
      // Mock API call for Storybook
      setTimeout(() => {
        setTableExists(Math.random() > 0.5);
        setSqlCheckLoading(false);
      }, 1000);
    } catch (e) {
      setTableExists(false);
      setSqlCheckLoading(false);
    }
  };

  const handleGenerateSQL = () => {
    setSqlGenLoading(true);
    let columns: string[] = [];
    if (structure && typeof structure === 'object' && Object.keys(structure).length > 0) {
      columns = Object.entries(structure).map(
        ([col, info]) => `  "${col}" ${analyzerTypeToSQLType(info.type)}`
      );
    } else if (mapping && typeof mapping === 'object' && Object.keys(mapping).length > 0) {
      columns = Object.entries(mapping).map(
        ([col, type]) => `  "${col}" ${type}`
      );
    }
    const sql = `CREATE TABLE "${sqlSchema}"."${sqlTableName}" (\n${columns.join(',\n')}\n);`;
    setGeneratedSQL(sql);
    setSqlGenLoading(false);
  };

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" sx={{ mb: 2, fontSize: '1rem' }}>
        SQL Table Generator
      </Typography>
      
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2, alignItems: 'center' }}>
        <TextField
          label="Table Name"
          size="small"
          value={sqlTableName}
          onChange={e => setSqlTableName(e.target.value)}
          placeholder="Enter table name"
          sx={{ minWidth: 200 }}
        />
        
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Schema</InputLabel>
          <Select
            value={sqlSchema}
            label="Schema"
            onChange={(e: SelectChangeEvent) => setSqlSchema(e.target.value)}
          >
            {DEFAULT_SCHEMAS.map(s => (
              <MenuItem key={s} value={s}>{s}</MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <Button
          variant="outlined"
          size="small"
          onClick={checkTableExists}
          disabled={sqlCheckLoading || !sqlTableName}
          startIcon={sqlCheckLoading ? <CircularProgress size={16} /> : null}
        >
          {sqlCheckLoading ? 'Checking...' : 'Check Table'}
        </Button>
        
        {tableExists !== null && (
          <Chip 
            label={tableExists ? 'Table exists' : 'Table available'}
            color={tableExists ? 'error' : 'success'}
            size="small"
            variant="outlined"
          />
        )}
      </Box>
      
      <Box sx={{ mb: 2 }}>
        <Button
          variant="contained"
          size="small"
          onClick={handleGenerateSQL}
          disabled={sqlGenLoading || !sqlTableName}
          startIcon={sqlGenLoading ? <CircularProgress size={16} /> : null}
          sx={{ mr: 1 }}
        >
          {sqlGenLoading ? 'Generating...' : 'Generate SQL'}
        </Button>
      </Box>
      
      <Divider sx={{ my: 2 }} />
      
      <Box>
        <Typography variant="subtitle2" sx={{ mb: 1, fontSize: '0.875rem' }}>
          Generated SQL:
        </Typography>
        <Paper 
          variant="outlined" 
          sx={{ 
            p: 2, 
            backgroundColor: 'grey.50',
            fontFamily: 'monospace',
            fontSize: '0.75rem',
            overflow: 'auto',
            maxHeight: 200,
            whiteSpace: 'pre-wrap'
          }}
        >
          {generatedSQL || 'SQL will appear here after generating the table structure.'}
        </Paper>
      </Box>
    </Paper>
  );
};

export default TableSQLGenerator;
