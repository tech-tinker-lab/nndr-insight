import React from 'react';
import DataTable from './DataTable';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api';

const columns = [
  { key: 'id', label: 'ID' },
  { key: 'property_id', label: 'Property ID' },
  { key: 'row_id', label: 'Row ID' },
  { key: 'ba_reference', label: 'BA Ref' },
  { key: 'scat_code', label: 'SCAT' },
  { key: 'description', label: 'Description' },
  { key: 'herid', label: 'Herid' },
  { key: 'rateable_value', label: 'RV' },
  { key: 'effective_date', label: 'Effective Date' },
  { key: 'postcode', label: 'Postcode' },
  // Add more columns as needed
];

export default function ValuationsTable() {
  return <DataTable columns={columns} fetchUrl={`${API_BASE}/valuations`} />;
}
