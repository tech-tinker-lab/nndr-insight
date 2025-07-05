import React, { useState } from 'react';
import DataTable from './DataTable';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api';

const columns = [
  { key: 'PropertyID', label: 'Property ID' },
  { key: 'Address', label: 'Address' },
  { key: 'Postcode', label: 'Postcode' },
  { key: 'Latitude', label: 'Latitude' },
  { key: 'Longitude', label: 'Longitude' },
];

export default function NonRatedPropertiesTable() {
  const [postcodeFilter, setPostcodeFilter] = useState('');
  const [district, setDistrict] = useState('South Cambridgeshire');
  const [fetchUrl, setFetchUrl] = useState(`${API_BASE}/non-rated-properties-map?district=South%20Cambridgeshire`);

  const handleFilter = () => {
    let url = `${API_BASE}/non-rated-properties-map?district=${encodeURIComponent(district)}`;
    setFetchUrl(url);
  };

  return (
    <div>
      <div className="mb-2 flex gap-2 items-center">
        <input
          className="border px-2 py-1 rounded"
          placeholder="District (default: South Cambridgeshire)"
          value={district}
          onChange={e => setDistrict(e.target.value)}
        />
        <button className="px-2 py-1 border rounded bg-blue-100" onClick={handleFilter}>
          Apply Filter
        </button>
      </div>
      <DataTable columns={columns} fetchUrl={fetchUrl} />
    </div>
  );
}
