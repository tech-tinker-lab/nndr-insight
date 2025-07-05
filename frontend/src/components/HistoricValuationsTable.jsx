import React from 'react';
import DataTable from './DataTable';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api';

const columns = [
  { key: 'id', label: 'ID' },
  { key: 'property_id', label: 'Property ID' },
  { key: 'ba_reference', label: 'BA Ref' },
  { key: 'scat_code', label: 'SCAT' },
  { key: 'description', label: 'Description' },
  { key: 'herid', label: 'Herid' },
  { key: 'rateable_value', label: 'RV' },
  { key: 'effective_date', label: 'Effective Date' },
  { key: 'change_date', label: 'Change Date' },
  { key: 'removal_date', label: 'Removal Date' },
  // Add more columns as needed
];

export default function HistoricValuationsTable() {
  return <DataTable columns={columns} fetchUrl={`${API_BASE}/historic_valuations`} />;
}
