import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  FormControl,
  Select,
  MenuItem,
} from '@mui/material';
import type { SelectChangeEvent } from '@mui/material';

export type FieldType = 'TEXT' | 'INTEGER' | 'FLOAT' | 'DATE' | 'BOOLEAN' | 'GEOMETRY';
export type Mapping = { [header: string]: FieldType };

interface ColumnMappingOptionsProps {
  structure: { [field: string]: { type: string; sample: string[] } };
  mapping: Mapping;
  setMapping: React.Dispatch<React.SetStateAction<Mapping>>;
}

const typeOptions: { value: FieldType; label: string }[] = [
  { value: 'TEXT', label: 'Text' },
  { value: 'INTEGER', label: 'Integer' },
  { value: 'FLOAT', label: 'Float' },
  { value: 'DATE', label: 'Date' },
  { value: 'BOOLEAN', label: 'Boolean' },
  { value: 'GEOMETRY', label: 'Geometry' },
];

const ColumnMappingOptions: React.FC<ColumnMappingOptionsProps> = ({ structure, mapping, setMapping }) => {
  const headers = structure ? Object.keys(structure) : [];
  console.log('ColumnMappingOptions props:', { structure, mapping });
  
  if (!headers || !Array.isArray(headers) || headers.length === 0) {
    return (
      <Typography variant="body2" color="error" sx={{ fontSize: '0.75rem' }}>
        No columns detected, cannot map columns.
      </Typography>
    );
  }

  const handleAIMapping = () => {
    const aiMapping: Mapping = {};
    headers.forEach(header => {
      const h = header.toLowerCase();
      // Use analyzer type if available
      const analyzerType = structure[header]?.type;
      if (analyzerType) {
        switch (analyzerType) {
          case 'integer': aiMapping[header] = 'INTEGER'; break;
          case 'float': aiMapping[header] = 'FLOAT'; break;
          case 'boolean': aiMapping[header] = 'BOOLEAN'; break;
          case 'date': aiMapping[header] = 'DATE'; break;
          case 'geometry': aiMapping[header] = 'GEOMETRY'; break;
          default: aiMapping[header] = 'TEXT';
        }
        return;
      }
      // ...existing code...
      if (/(geom|geometry|shape|wkt|wkb|spatial|location|point|polygon|linestring)/.test(h)) {
        aiMapping[header] = 'GEOMETRY';
      } else if (/^(lat|latitude)$/.test(h) || h.includes('lat_')) {
        aiMapping[header] = 'FLOAT';
      } else if (/^(lon|lng|long|longitude)$/.test(h) || h.includes('lon_') || h.includes('lng_')) {
        aiMapping[header] = 'FLOAT';
      } else if (/^(is_|has_|flag|active|enabled|valid|deleted|visible)/.test(h) || h.endsWith('_flag')) {
        aiMapping[header] = 'BOOLEAN';
      } else if (/(date|time|timestamp|created|updated|modified|dob|birth)/.test(h)) {
        aiMapping[header] = 'DATE';
      } else if (/(id$|_id$|count|number|index|rank|order|seq|step)/.test(h)) {
        aiMapping[header] = 'INTEGER';
      } else if (/(amount|price|value|score|percent|ratio|weight|height|depth|width|distance|area|volume|size|measure|rate)/.test(h)) {
        aiMapping[header] = 'FLOAT';
      } else {
        aiMapping[header] = 'TEXT';
      }
    });
    setMapping(aiMapping);
  };

  const handleFieldChange = (header: string) => (event: SelectChangeEvent) => {
    setMapping(prev => ({ ...prev, [header]: event.target.value as FieldType }));
  };

  return (
    <Paper 
      elevation={1} 
      sx={{ 
        p: 2, 
        mb: 2, 
        backgroundColor: 'primary.50',
        border: '1px solid',
        borderColor: 'primary.200'
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="subtitle2" color="primary.800" sx={{ fontSize: '0.75rem', fontWeight: 600 }}>
          Column Field Type Mapping
        </Typography>
        <Button
          size="small"
          variant="text"
          onClick={handleAIMapping}
          sx={{ 
            fontSize: '0.75rem',
            fontWeight: 600,
            color: 'primary.600',
            '&:hover': {
              color: 'primary.800',
            }
          }}
        >
          ⚡ AI powered
        </Button>
      </Box>
      
      <Box 
        sx={{ 
          display: 'grid', 
          gridTemplateColumns: { 
            xs: 'repeat(2, 1fr)', 
            sm: 'repeat(3, 1fr)', 
            md: 'repeat(4, 1fr)' 
          }, 
          gap: 1 
        }}
      >
        {headers.map((header, idx) => (
          <Box key={idx} sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
            <Typography 
              variant="caption" 
              sx={{ 
                fontSize: '0.75rem', 
                fontWeight: 500,
                color: 'text.primary'
              }}
            >
              {header}
            </Typography>
            
            <FormControl size="small" fullWidth>
              <Select
                value={mapping[header] || 'TEXT'}
                onChange={handleFieldChange(header)}
                sx={{ 
                  fontSize: '0.75rem',
                  '& .MuiSelect-select': {
                    fontSize: '0.75rem',
                    py: 0.5,
                  }
                }}
              >
                {typeOptions.map(option => (
                  <MenuItem 
                    key={option.value} 
                    value={option.value}
                    sx={{ fontSize: '0.75rem' }}
                  >
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Typography 
              variant="caption" 
              sx={{ 
                fontSize: '0.625rem', 
                color: 'text.secondary',
                fontStyle: 'italic'
              }}
            >
              {structure[header]?.type || ''}
            </Typography>
          </Box>
        ))}
      </Box>
    </Paper>
  );
};

export default ColumnMappingOptions;
