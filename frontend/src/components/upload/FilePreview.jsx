import React, { useState } from 'react';
import CSVTablePreview from './CSVTablePreview';

const FilePreview = ({ analysis, getAllConfigs, tableName, setTableName, tableNameAvailable, setTableNameAvailable, showSQL, setShowSQL, generatedSQL, setGeneratedSQL }) => {
  const [showFieldAnalysis, setShowFieldAnalysis] = useState(false);
  if (!analysis) return <div className="text-xs text-gray-500">Analyzing...</div>;
  if (analysis.error) return <div className="text-xs text-red-500">Analysis failed: {analysis.error}</div>;
  const name = analysis.name || analysis.fileName || 'N/A';
  const type = analysis.type || analysis.format || 'N/A';
  const preview = analysis.preview || null;
  if (type === 'csv') {
    return (
      <div className="mt-3">
        <CSVTablePreview
          preview={preview}
          delimiter={preview?.detectedDelimiter || ','}
          file={{ name }}
          showSQL={showSQL}
          setShowSQL={setShowSQL}
          generatedSQL={generatedSQL}
          setGeneratedSQL={setGeneratedSQL}
          tableName={tableName}
          setTableName={setTableName}
          tableNameAvailable={tableNameAvailable}
          setTableNameAvailable={setTableNameAvailable}
        />
        {analysis.field_analysis && (
          <div className="mt-3">
            <button
              className="text-xs text-blue-600 underline hover:text-blue-800 mb-2"
              onClick={() => setShowFieldAnalysis(v => !v)}
              type="button"
            >
              {showFieldAnalysis ? 'Hide Field Analysis' : 'Show Field Analysis'}
            </button>
            {showFieldAnalysis && (
              <div className="mb-2">
                <div className="font-semibold text-gray-700 mb-2">Field Analysis</div>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-xs border border-gray-300 bg-white">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="border px-2 py-1">Field Name</th>
                        <th className="border px-2 py-1">Type</th>
                        <th className="border px-2 py-1">Confidence</th>
                        <th className="border px-2 py-1">Sample Values</th>
                        <th className="border px-2 py-1">Unique</th>
                        <th className="border px-2 py-1">Empty</th>
                        <th className="border px-2 py-1">Total</th>
                        <th className="border px-2 py-1">Reason</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analysis.field_analysis.map((field, idx) => (
                        <tr key={idx}>
                          <td className="border px-2 py-1">{field.field_name || '-'}</td>
                          <td className="border px-2 py-1">{field.type || '-'}</td>
                          <td className="border px-2 py-1">{field.confidence !== undefined ? `${Math.round(field.confidence * 100)}%` : '-'}</td>
                          <td className="border px-2 py-1">{Array.isArray(field.sample_values) ? field.sample_values.slice(0, 3).join(', ') : '-'}</td>
                          <td className="border px-2 py-1">{field.unique_count !== undefined ? field.unique_count : '-'}</td>
                          <td className="border px-2 py-1">{field.empty_count !== undefined ? field.empty_count : '-'}</td>
                          <td className="border px-2 py-1">{field.total_count !== undefined ? field.total_count : '-'}</td>
                          <td className="border px-2 py-1">{field.reason || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }
  // ...other file type previews...
  return <div className="text-xs text-gray-500">No preview available.</div>;
};

export default FilePreview;
// File removed after migration to FilePreview.tsx
import React, { useState } from 'react';
import CSVTablePreview from './CSVTablePreview';

const FilePreview = ({ analysis, getAllConfigs, tableName, setTableName, tableNameAvailable, setTableNameAvailable, showSQL, setShowSQL, generatedSQL, setGeneratedSQL }) => {
  const [showFieldAnalysis, setShowFieldAnalysis] = useState(false);
  if (!analysis) return <div className="text-xs text-gray-500">Analyzing...</div>;
  if (analysis.error) return <div className="text-xs text-red-500">Analysis failed: {analysis.error}</div>;
  const name = analysis.name || analysis.fileName || 'N/A';
  const type = analysis.type || analysis.format || 'N/A';
  const preview = analysis.preview || null;
  if (type === 'csv') {
    return (
      <div className="mt-3">
        <CSVTablePreview
          preview={preview}
          delimiter={preview?.detectedDelimiter || ','}
          file={{ name }}
          showSQL={showSQL}
          setShowSQL={setShowSQL}
          generatedSQL={generatedSQL}
          setGeneratedSQL={setGeneratedSQL}
          tableName={tableName}
          setTableName={setTableName}
          tableNameAvailable={tableNameAvailable}
          setTableNameAvailable={setTableNameAvailable}
        />
        {analysis.field_analysis && (
          <div className="mt-3">
            <button
              className="text-xs text-blue-600 underline hover:text-blue-800 mb-2"
              onClick={() => setShowFieldAnalysis(v => !v)}
              type="button"
            >
              {showFieldAnalysis ? 'Hide Field Analysis' : 'Show Field Analysis'}
            </button>
            {showFieldAnalysis && (
              <div className="mb-2">
                <div className="font-semibold text-gray-700 mb-2">Field Analysis</div>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-xs border border-gray-300 bg-white">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="border px-2 py-1">Field Name</th>
                        <th className="border px-2 py-1">Type</th>
                        <th className="border px-2 py-1">Confidence</th>
                        <th className="border px-2 py-1">Sample Values</th>
                        <th className="border px-2 py-1">Unique</th>
                        <th className="border px-2 py-1">Empty</th>
                        <th className="border px-2 py-1">Total</th>
                        <th className="border px-2 py-1">Reason</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analysis.field_analysis.map((field, idx) => (
                        <tr key={idx}>
                          <td className="border px-2 py-1">{field.field_name || '-'}</td>
                          <td className="border px-2 py-1">{field.type || '-'}</td>
                          <td className="border px-2 py-1">{field.confidence !== undefined ? `${Math.round(field.confidence * 100)}%` : '-'}</td>
                          <td className="border px-2 py-1">{Array.isArray(field.sample_values) ? field.sample_values.slice(0, 3).join(', ') : '-'}</td>
                          <td className="border px-2 py-1">{field.unique_count !== undefined ? field.unique_count : '-'}</td>
                          <td className="border px-2 py-1">{field.empty_count !== undefined ? field.empty_count : '-'}</td>
                          <td className="border px-2 py-1">{field.total_count !== undefined ? field.total_count : '-'}</td>
                          <td className="border px-2 py-1">{field.reason || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }
  // ...other file type previews...
  return <div className="text-xs text-gray-500">No preview available.</div>;
};

export default FilePreview;
