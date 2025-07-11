import React, { useState, useEffect, useCallback } from "react";
import api from "../api/axios";
import { Database } from "lucide-react";
import toast from "react-hot-toast";
import ReactFlow, { MiniMap, Controls, Background } from 'reactflow';
import 'reactflow/dist/style.css';
import Tooltip from '@mui/material/Tooltip';

function getTableNodes(masterTables, selectedTable) {
  return masterTables.map((table, idx) => ({
    id: table,
    data: { label: table },
    position: { x: 100 + 200 * (idx % 3), y: 100 + 120 * Math.floor(idx / 3) },
    style: {
      border: table === selectedTable ? '2px solid #059669' : '1px solid #ccc',
      background: table === selectedTable ? '#bbf7d0' : '#fff',
      cursor: 'pointer',
      minWidth: 120,
      textAlign: 'center',
      fontWeight: table === selectedTable ? 'bold' : 'normal',
    },
  }));
}

export default function MasterData() {
  const [selectedTable, setSelectedTable] = useState("");
  const [columns, setColumns] = useState([]);
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [selectedRow, setSelectedRow] = useState(null);
  const [error, setError] = useState(null);
  const [masterTables, setMasterTables] = useState([]);
  const [tableEdges, setTableEdges] = useState([]);

  // Fetch master tables and relationships on mount
  useEffect(() => {
    const fetchMasterTables = async () => {
      try {
        const res = await api.get('/api/admin/master/tables');
        setMasterTables(res.data.master_tables || []);
        setTableEdges(res.data.table_edges || []);
      } catch (err) {
        setMasterTables([]);
        setTableEdges([]);
        toast.error("Failed to fetch master tables/relationships");
      }
    };
    fetchMasterTables();
  }, []);

  useEffect(() => {
    if (selectedTable) {
      fetchData();
    }
    // eslint-disable-next-line
  }, [selectedTable, page, pageSize]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { page_size: pageSize, offset: (page - 1) * pageSize };
      const res = await api.get(`/api/admin/master/preview/${selectedTable}`, { params });
      setData(res.data.sample_data || []);
      setTotal(res.data.total_count || 0);
      if (res.data.sample_data && res.data.sample_data.length > 0) {
        setColumns(Object.keys(res.data.sample_data[0]));
      } else {
        setColumns([]);
      }
    } catch (err) {
      toast.error("Failed to fetch master data");
      setError("Failed to fetch master data.");
      setData([]);
      setColumns([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const handleTableChange = (e) => {
    setSelectedTable(e.target.value);
    setPage(1);
    setSelectedRow(null);
  };

  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  // ReactFlow handlers
  const nodes = getTableNodes(masterTables, selectedTable);
  const edges = tableEdges.map(e => ({ ...e, animated: true, style: { stroke: '#059669' }, labelStyle: { fill: '#059669', fontWeight: 600 } }));
  const onNodeClick = useCallback((event, node) => {
    setSelectedTable(node.id);
    setPage(1);
    setSelectedRow(null);
  }, []);

  return (
    <>
      <a href="#main-content" className="sr-only focus:not-sr-only absolute left-2 top-2 bg-green-700 text-white px-4 py-2 rounded z-50">Skip to main content</a>
      <div id="main-content" tabIndex={-1} className="max-w-7xl mx-auto p-6">
        <div className="flex items-center mb-6">
          <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center mr-3">
            <Database className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Master Data</h1>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="master-table-select">Select Master Table</label>
          <select
            id="master-table-select"
            aria-label="Select master table"
            value={selectedTable}
            onChange={handleTableChange}
            tabIndex={0}
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
          >
            <option value="">Select a table...</option>
            {masterTables.map((table) => (
              <option key={table} value={table}>{table}</option>
            ))}
          </select>
          <div className="text-xs text-gray-500 mt-1">Choose a table to preview and analyze its data.</div>
        </div>
        {/* Interactive Diagram */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Table Relationships</h2>
          <div className="h-96 w-full border-2 border-dashed border-gray-200 rounded-lg bg-gray-50">
            <ReactFlow
              nodes={nodes.map(node => ({
                ...node,
                data: {
                  ...node.data,
                  label: (
                    <Tooltip title={`Table: ${node.id}`} arrow>
                      <span
                        tabIndex={0}
                        role="button"
                        aria-label={`Select table ${node.id}`}
                        onKeyDown={e => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            setSelectedTable(node.id);
                            setPage(1);
                            setSelectedRow(null);
                          }
                        }}
                        style={{ outline: node.id === selectedTable ? '2px solid #059669' : undefined }}
                      >
                        {node.data.label}
                      </span>
                    </Tooltip>
                  )
                }
              }))}
              edges={edges}
              onNodeClick={onNodeClick}
              fitView
              style={{ width: '100%', height: '100%' }}
              aria-label="Master table relationships diagram"
            >
              <MiniMap />
              <Controls />
              <Background gap={16} />
            </ReactFlow>
          </div>
          <div className="text-xs text-gray-500 mt-2">Click a table node to select and preview its data below. Hover for table name.</div>
        </div>
        {/* Data Preview */}
        {selectedTable && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Data Preview</h2>
              <div className="text-sm text-gray-600">
                Showing {(page - 1) * pageSize + 1}-{Math.min(page * pageSize, total)} of {total} records
              </div>
            </div>
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
                <p className="mt-2 text-gray-600">Loading master data...</p>
              </div>
            ) : error ? (
              <div className="text-center py-8 text-red-600 font-semibold">
                {error}
              </div>
            ) : data.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200" aria-label="Master data preview table" role="table">
                  <thead className="bg-gray-50">
                    <tr>
                      {columns.map((col) => (
                        <Tooltip key={col} title={col} arrow>
                          <th
                            className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider focus:outline-green-600"
                            tabIndex={0}
                            aria-label={col}
                            scope="col"
                          >
                            {col}
                          </th>
                        </Tooltip>
                      ))}
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider" scope="col">Select</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {data.map((row, idx) => (
                      <tr
                        key={idx}
                        className={selectedRow === idx ? "bg-green-700 text-white border-l-4 border-green-700" : "hover:bg-green-100 focus:bg-green-200"}
                        tabIndex={0}
                        aria-selected={selectedRow === idx}
                        role="row"
                        onKeyDown={e => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            setSelectedRow(idx);
                          }
                        }}
                        style={selectedRow === idx ? { outline: '2px solid #059669' } : {}}
                      >
                        {columns.map((col) => (
                          <td key={col} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {row[col] === null ? 'NULL' : String(row[col]).substring(0, 100)}
                          </td>
                        ))}
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <button
                            className={`px-3 py-1 rounded focus:ring-2 focus:ring-green-500 ${selectedRow === idx ? "bg-green-900 text-white" : "bg-gray-200 text-gray-700 hover:bg-green-100"}`}
                            onClick={() => setSelectedRow(idx)}
                            aria-label={selectedRow === idx ? "Deselect row" : "Select row"}
                           tabIndex={0}
                          >
                            {selectedRow === idx ? "Selected" : "Select"}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                No data found
              </div>
            )}
            {/* Pagination and Page Size Selector */}
            <div className="flex items-center justify-between mt-4">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handlePageChange(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Previous page"
                >
                  Previous
                </button>
                <button
                  onClick={() => handlePageChange(page + 1)}
                  disabled={page * pageSize >= total}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Next page"
                >
                  Next
                </button>
                <label htmlFor="page-size-select" className="ml-4 text-sm text-gray-700">Rows per page:</label>
                <select
                  id="page-size-select"
                  value={pageSize}
                  onChange={e => { setPageSize(Number(e.target.value)); setPage(1); }}
                  className="p-1 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500"
                  aria-label="Rows per page"
                >
                  {[10, 25, 50, 100].map(size => (
                    <option key={size} value={size}>{size}</option>
                  ))}
                </select>
              </div>
              <div className="text-sm text-gray-600">
                Page {page} of {Math.ceil(total / pageSize)}
              </div>
            </div>
            {/* Row Details and Clear Selection */}
            {selectedRow !== null && data[selectedRow] && (
              <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold text-green-800">Selected Row Details</h3>
                  <button
                    className="ml-4 px-2 py-1 bg-gray-200 text-gray-700 rounded hover:bg-red-100 focus:ring-2 focus:ring-red-500"
                    onClick={() => setSelectedRow(null)}
                    aria-label="Clear row selection"
                  >
                    Clear selection
                  </button>
                </div>
                <pre className="text-xs text-gray-800 whitespace-pre-wrap">{JSON.stringify(data[selectedRow], null, 2)}</pre>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
} 