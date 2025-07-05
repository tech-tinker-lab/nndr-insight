import React from 'react';
import DataTable from './DataTable';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api';

const columns = [
  { key: 'id', label: 'ID' },
  { key: 'list_altered', label: 'List Altered' },
  { key: 'community_code', label: 'Community Code' },
  { key: 'ba_reference', label: 'BA Ref' },
  { key: 'property_category_code', label: 'Category' },
  { key: 'property_description', label: 'Description' },
  { key: 'property_address', label: 'Address' },
  { key: 'postcode', label: 'Postcode' },
  { key: 'rateable_value', label: 'RV' },
  // Add more columns as needed
];

export default function PropertiesTable() {
  return <DataTable columns={columns} fetchUrl={`${API_BASE}/properties`} />;
}
