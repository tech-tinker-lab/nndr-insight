import React, { useState } from 'react';
import api from '../api/axios';

const FileUploadAndAIMatch = () => {
  const [file, setFile] = useState(null);
  const [fields, setFields] = useState([]); // Placeholder for extracted fields
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    // TODO: Extract fields from file (CSV/JSON/XLS/etc.)
    // For now, use placeholder fields
    setFields([
      { name: 'uprn', type: 'bigint' },
      { name: 'postcode', type: 'varchar' },
      { name: 'address', type: 'text' }
    ]);
  };

  const handleAIMatch = async () => {
    setLoading(true);
    try {
      const response = await api.post('/api/design-enhanced/data-standards/match', fields);
      setMatches(response.data.matches);
    } catch (err) {
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto p-8">
      <h2 className="text-xl font-bold mb-4">Upload File & AI Standards Suggestion</h2>
      <input type="file" onChange={handleFileChange} className="mb-4" />
      <button
        className="bg-blue-600 text-white px-4 py-2 rounded"
        onClick={handleAIMatch}
        disabled={!fields.length || loading}
      >
        {loading ? 'Matching...' : 'Find Matching Standards'}
      </button>
      {matches.length > 0 && (
        <div className="mt-6">
          <h3 className="font-semibold mb-2">AI Suggested Standards:</h3>
          <ul>
            {matches.map((m, idx) => (
              <li key={idx} className="mb-2 p-2 border rounded">
                <strong>{m.name}</strong> (Confidence: {(m.confidence * 100).toFixed(1)}%)<br />
                <span className="text-xs">Missing fields: {m.missing_fields.join(', ') || 'None'}</span><br />
                <span className="text-xs">Extra fields: {m.extra_fields.join(', ') || 'None'}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default FileUploadAndAIMatch; 