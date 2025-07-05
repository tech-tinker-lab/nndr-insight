import React from 'react';
import DataTable from './DataTable';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api';

const columns = [
  { key: 'id', label: 'ID' },
  { key: 'property_id', label: 'Property ID' },
  { key: 'name', label: 'Name' },
  { key: 'address', label: 'Address' },
  { key: 'liability_start_date', label: 'Start Date' },
  { key: 'liability_end_date', label: 'End Date' },
  { key: 'annual_charge', label: 'Annual Charge' },
  { key: 'exemption_code', label: 'Exemption' },
  // Add more columns as needed
];

export default function RatepayersTable() {
  return <DataTable columns={columns} fetchUrl={`${API_BASE}/ratepayers`} />;
}
