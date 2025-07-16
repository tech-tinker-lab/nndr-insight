import React from 'react';

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
    return <div className="text-xs text-red-600">No columns detected, cannot map columns.</div>;
  }

  // Enhanced AI-powered mapping (prototype logic)
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
      // Fallback to heuristics
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

  return (
    <div className="mb-3 p-3 bg-blue-50 rounded border">
      <div className="flex items-center justify-between mb-2">
        <div className="text-xs font-medium text-blue-800">Column Field Type Mapping</div>
        <button
          className="text-xs text-blue-600 underline hover:text-blue-800 font-semibold"
          style={{ cursor: 'pointer' }}
          onClick={handleAIMapping}
          type="button"
        >
          AI powered
        </button>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
        {headers.map((header, idx) => (
          <div key={idx} className="flex flex-col space-y-1">
            <label className="text-xs font-medium text-gray-700">{header}</label>
            <select
              value={mapping[header] || 'TEXT'}
              onChange={e => setMapping(prev => ({ ...prev, [header]: e.target.value as FieldType }))}
              className="text-xs border border-gray-300 rounded px-2 py-1 bg-white"
            >
              {typeOptions.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
            <span className="text-2xs text-gray-400">{structure[header]?.type || ''}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ColumnMappingOptions;
