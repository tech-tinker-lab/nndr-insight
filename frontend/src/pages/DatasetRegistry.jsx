import React, { useEffect, useState } from 'react';
import api from '../api/axios';

const DatasetRegistry = () => {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDatasets = async () => {
      try {
        const response = await api.get('/api/design-enhanced/datasets');
        setDatasets(response.data);
      } catch (err) {
        setDatasets([]);
      } finally {
        setLoading(false);
      }
    };
    fetchDatasets();
  }, []);

  return (
    <div className="max-w-3xl mx-auto p-8">
      <h2 className="text-2xl font-bold mb-4">Dataset Registry</h2>
      {loading ? (
        <div>Loading...</div>
      ) : (
        <table className="w-full border">
          <thead>
            <tr>
              <th className="border px-2 py-1">Name</th>
              <th className="border px-2 py-1">Description</th>
              <th className="border px-2 py-1">Standard</th>
              <th className="border px-2 py-1">Version</th>
            </tr>
          </thead>
          <tbody>
            {datasets.map(ds => (
              <tr key={ds.id}>
                <td className="border px-2 py-1">{ds.name}</td>
                <td className="border px-2 py-1">{ds.description}</td>
                <td className="border px-2 py-1">{ds.standard_id}</td>
                <td className="border px-2 py-1">{ds.standard_version}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default DatasetRegistry; 