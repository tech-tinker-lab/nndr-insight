// File removed after migration to TableSQLGenerator.tsx
import React, { useState } from 'react';
import api from '../../api/axios';

const DEFAULT_SCHEMAS = ['public', 'staging', 'archive']; // Replace with real schemas if needed


// Utility to map analyzer type to SQL type
const analyzerTypeToSQLType = (analyzerType) => {
  switch (analyzerType) {
    case 'integer': return 'INTEGER';
    case 'float': return 'FLOAT';
    case 'boolean': return 'BOOLEAN';
    case 'date': return 'DATE';
    case 'geometry': return 'GEOMETRY';
    default: return 'TEXT';
  }
};

const TableSQLGenerator = ({ mapping, structure, uniqueKey, generatedSQL, setGeneratedSQL }) => {
  const [sqlTableName, setSqlTableName] = useState('');
  const [sqlSchema, setSqlSchema] = useState(DEFAULT_SCHEMAS[0]);
  const [tableExists, setTableExists] = useState(null);
  const [sqlCheckLoading, setSqlCheckLoading] = useState(false);
  const [sqlGenLoading, setSqlGenLoading] = useState(false);
  const [availableSchemas, setAvailableSchemas] = useState(DEFAULT_SCHEMAS);

  // Function to check if table exists (replace with real API call)
  const checkTableExists = async () => {
    setSqlCheckLoading(true);
    try {
      const res = await api.get(`/db/check-table?schema=${sqlSchema}&table=${sqlTableName}`);
      setTableExists(res.data.exists);
    } catch (e) {
      setTableExists(false);
    }
    setSqlCheckLoading(false);
  };

  // Function to generate SQL from structure (or mapping fallback)
  const handleGenerateSQL = () => {
    setSqlGenLoading(true);
    let columns = [];
    if (structure && typeof structure === 'object' && Object.keys(structure).length > 0) {
      columns = Object.entries(structure).map(
        ([col, info]) => `  "${col}" ${analyzerTypeToSQLType(info.type)}`
      );
    } else if (mapping && typeof mapping === 'object' && Object.keys(mapping).length > 0) {
      columns = Object.entries(mapping).map(
        ([col, type]) => `  "${col}" ${type}`
      );
    }
    const sql = `CREATE TABLE "${sqlSchema}"."${sqlTableName}" (\n${columns.join(',\n')}\n);`;
    setGeneratedSQL(sql);
    setSqlGenLoading(false);
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center space-x-2 flex-wrap">
        <label className="text-xs font-medium">Table Name:</label>
        <input
          className="border px-2 py-1 rounded text-xs"
          value={sqlTableName}
          onChange={e => setSqlTableName(e.target.value)}
          placeholder="Enter table name"
        />
        <label className="text-xs font-medium">Schema:</label>
        <select
          className="border px-2 py-1 rounded text-xs"
          value={sqlSchema}
          onChange={e => setSqlSchema(e.target.value)}
        >
          {availableSchemas.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <button
          className="text-xs px-2 py-1 bg-blue-600 text-white rounded"
          onClick={checkTableExists}
          disabled={sqlCheckLoading || !sqlTableName}
        >
          {sqlCheckLoading ? 'Checking...' : 'Check'}
        </button>
        {tableExists !== null && (
          <span className={`text-xs ml-2 ${tableExists ? 'text-red-600' : 'text-green-600'}`}>
            {tableExists ? 'Table exists' : 'Table available'}
          </span>
        )}
        <button
          className="text-xs px-2 py-1 bg-green-600 text-white rounded ml-2"
          onClick={handleGenerateSQL}
          disabled={sqlGenLoading || !sqlTableName}
        >
          {sqlGenLoading ? 'Generating...' : 'Generate Table'}
        </button>
      </div>
      <div className="bg-gray-100 rounded p-2 text-xs overflow-x-auto mt-2">
        {generatedSQL || 'SQL will appear here after mapping.'}
      </div>
    </div>
  );
};

export default TableSQLGenerator;
import React, { useState } from 'react';
import api from '../../api/axios';

const DEFAULT_SCHEMAS = ['public', 'staging', 'archive']; // Replace with real schemas if needed


// Utility to map analyzer type to SQL type
const analyzerTypeToSQLType = (analyzerType) => {
  switch (analyzerType) {
    case 'integer': return 'INTEGER';
    case 'float': return 'FLOAT';
    case 'boolean': return 'BOOLEAN';
    case 'date': return 'DATE';
    case 'geometry': return 'GEOMETRY';
    default: return 'TEXT';
  }
};

const TableSQLGenerator = ({ mapping, structure, uniqueKey, generatedSQL, setGeneratedSQL }) => {
  const [sqlTableName, setSqlTableName] = useState('');
  const [sqlSchema, setSqlSchema] = useState(DEFAULT_SCHEMAS[0]);
  const [tableExists, setTableExists] = useState(null);
  const [sqlCheckLoading, setSqlCheckLoading] = useState(false);
  const [sqlGenLoading, setSqlGenLoading] = useState(false);
  const [availableSchemas, setAvailableSchemas] = useState(DEFAULT_SCHEMAS);

  // Function to check if table exists (replace with real API call)
  const checkTableExists = async () => {
    setSqlCheckLoading(true);
    try {
      const res = await api.get(`/db/check-table?schema=${sqlSchema}&table=${sqlTableName}`);
      setTableExists(res.data.exists);
    } catch (e) {
      setTableExists(false);
    }
    setSqlCheckLoading(false);
  };

  // Function to generate SQL from structure (or mapping fallback)
  const handleGenerateSQL = () => {
    setSqlGenLoading(true);
    let columns = [];
    if (structure && typeof structure === 'object' && Object.keys(structure).length > 0) {
      columns = Object.entries(structure).map(
        ([col, info]) => `  "${col}" ${analyzerTypeToSQLType(info.type)}`
      );
    } else if (mapping && typeof mapping === 'object' && Object.keys(mapping).length > 0) {
      columns = Object.entries(mapping).map(
        ([col, type]) => `  "${col}" ${type}`
      );
    }
    const sql = `CREATE TABLE "${sqlSchema}"."${sqlTableName}" (\n${columns.join(',\n')}\n);`;
    setGeneratedSQL(sql);
    setSqlGenLoading(false);
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center space-x-2 flex-wrap">
        <label className="text-xs font-medium">Table Name:</label>
        <input
          className="border px-2 py-1 rounded text-xs"
          value={sqlTableName}
          onChange={e => setSqlTableName(e.target.value)}
          placeholder="Enter table name"
        />
        <label className="text-xs font-medium">Schema:</label>
        <select
          className="border px-2 py-1 rounded text-xs"
          value={sqlSchema}
          onChange={e => setSqlSchema(e.target.value)}
        >
          {availableSchemas.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <button
          className="text-xs px-2 py-1 bg-blue-600 text-white rounded"
          onClick={checkTableExists}
          disabled={sqlCheckLoading || !sqlTableName}
        >
          {sqlCheckLoading ? 'Checking...' : 'Check'}
        </button>
        {tableExists !== null && (
          <span className={`text-xs ml-2 ${tableExists ? 'text-red-600' : 'text-green-600'}`}>
            {tableExists ? 'Table exists' : 'Table available'}
          </span>
        )}
        <button
          className="text-xs px-2 py-1 bg-green-600 text-white rounded ml-2"
          onClick={handleGenerateSQL}
          disabled={sqlGenLoading || !sqlTableName}
        >
          {sqlGenLoading ? 'Generating...' : 'Generate Table'}
        </button>
      </div>
      <div className="bg-gray-100 rounded p-2 text-xs overflow-x-auto mt-2">
        {generatedSQL || 'SQL will appear here after mapping.'}
      </div>
    </div>
  );
};

export default TableSQLGenerator;
