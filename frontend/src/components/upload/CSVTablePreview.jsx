import React, { useState, useEffect, useRef } from 'react';

const CSVTablePreview = ({ preview, delimiter, file, showSQL, setShowSQL, generatedSQL, setGeneratedSQL, tableName, setTableName, tableNameAvailable, setTableNameAvailable }) => {
  const [columnMappings, setColumnMappings] = useState({});
  const [aiSuggestions, setAiSuggestions] = useState({});
  const [showMappingOptions, setShowMappingOptions] = useState(false);
  const [creatingPipeline, setCreatingPipeline] = useState(false);
  const [checkingName, setCheckingName] = useState(false);
  const [showAIPrefInfo, setShowAIPrefInfo] = useState(false);
  const tableNameInputRef = useRef();

  // ...Field type options, detectFieldType, useEffect for AI suggestions, generateSQL, checkTableName, etc...

  return (
    <div>
      {/* CSV Data Preview Table */}
      {preview && preview.headers && preview.sampleRows && preview.headers.length > 0 && (
        <div className="mb-4">
          <div className="font-semibold text-gray-700 mb-2">CSV Data Preview</div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-xs border border-gray-300 bg-white">
              <thead className="bg-gray-100">
                <tr>
                  {preview.headers.map((header, idx) => (
                    <th key={idx} className="border px-2 py-1 text-left">{header}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.sampleRows.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-gray-50">
                    {row.map((cell, cIdx) => (
                      <td key={cIdx} className="border px-2 py-1">{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      {/* ...CSV preview table, column mapping, SQL generation, etc... */}
    </div>
  );
};

export default CSVTablePreview;
// File removed after migration to CSVTablePreview.tsx
import React, { useState, useEffect, useRef } from 'react';

const CSVTablePreview = ({ preview, delimiter, file, showSQL, setShowSQL, generatedSQL, setGeneratedSQL, tableName, setTableName, tableNameAvailable, setTableNameAvailable }) => {
  const [columnMappings, setColumnMappings] = useState({});
  const [aiSuggestions, setAiSuggestions] = useState({});
  const [showMappingOptions, setShowMappingOptions] = useState(false);
  const [creatingPipeline, setCreatingPipeline] = useState(false);
  const [checkingName, setCheckingName] = useState(false);
  const [showAIPrefInfo, setShowAIPrefInfo] = useState(false);
  const tableNameInputRef = useRef();

  // ...Field type options, detectFieldType, useEffect for AI suggestions, generateSQL, checkTableName, etc...

  return (
    <div>
      {/* CSV Data Preview Table */}
      {preview && preview.headers && preview.sampleRows && preview.headers.length > 0 && (
        <div className="mb-4">
          <div className="font-semibold text-gray-700 mb-2">CSV Data Preview</div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-xs border border-gray-300 bg-white">
              <thead className="bg-gray-100">
                <tr>
                  {preview.headers.map((header, idx) => (
                    <th key={idx} className="border px-2 py-1 text-left">{header}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.sampleRows.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-gray-50">
                    {row.map((cell, cIdx) => (
                      <td key={cIdx} className="border px-2 py-1">{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      {/* ...CSV preview table, column mapping, SQL generation, etc... */}
    </div>
  );
};

export default CSVTablePreview;
