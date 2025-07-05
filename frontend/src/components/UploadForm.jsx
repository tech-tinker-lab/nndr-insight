// UploadForm.jsx
import React, { useState } from 'react';

export default function UploadForm() {
  const [nndrData, setNndrData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [skip, setSkip] = useState(0);
  const [limit, setLimit] = useState(100);

  const fetchData = async (newSkip = skip, newLimit = limit) => {
    setLoading(true);
    const url = `http://localhost:8000/api/nndr/properties?skip=${newSkip}&limit=${newLimit}`;
    const res = await fetch(url);
    const json = await res.json();
    setNndrData(json.data || []);
    setSkip(newSkip);
    setLimit(newLimit);
    setLoading(false);
  };

  const handlePrev = () => {
    if (skip - limit >= 0) fetchData(skip - limit, limit);
  };

  const handleNext = () => {
    if (nndrData.length === limit) fetchData(skip + limit, limit);
  };

  return (
    <div>
      <h2 className="font-semibold mb-2">NNDR Properties</h2>
      <button
        className="bg-blue-500 text-white px-4 py-2 rounded mb-4"
        onClick={() => fetchData(0, limit)}
      >
        Load Data
      </button>
      {loading && <div>Loading...</div>}
      {nndrData.length > 0 && (
        <>
          <div className="mb-2 flex gap-2">
            <button
              className="bg-gray-300 px-2 py-1 rounded"
              onClick={handlePrev}
              disabled={skip === 0}
            >
              Previous
            </button>
            <button
              className="bg-gray-300 px-2 py-1 rounded"
              onClick={handleNext}
              disabled={nndrData.length < limit}
            >
              Next
            </button>
            <span>Showing {skip + 1} - {skip + nndrData.length}</span>
          </div>
          <table className="table-auto w-full text-xs">
            <thead>
              <tr>
                {Object.keys(nndrData[0]).map((key) => (
                  <th key={key} className="border px-2 py-1">{key}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {nndrData.map((row, idx) => (
                <tr key={idx}>
                  {Object.values(row).map((val, i) => (
                    <td key={i} className="border px-2 py-1">{val}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
