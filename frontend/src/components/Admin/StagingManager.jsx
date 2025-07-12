import React, { useState, useEffect } from 'react';
import api from '../../api/axios';
import { useUser } from '../../context/UserContext';
import StagingTableAutocomplete from '../StagingTableAutocomplete';

const HISTORY_PAGE_SIZE = 25;

const EVENT_STATUS_LABELS = {
  success: 'Migration',
  error: 'Migration Error',
  upload: 'Upload',
  deleted: 'Delete',
  purged: 'Purge',
  purged_master: 'Master Purge',
};

const StagingManager = () => {
  const { token } = useUser();
  const [stagingTables, setStagingTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState('');
  const [tableSummary, setTableSummary] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [migrationLoading, setMigrationLoading] = useState(false);
  const [migrationResult, setMigrationResult] = useState(null);
  
  // Filter states
  const [filters, setFilters] = useState({
    batch_id: '',
    source_name: '',
    session_id: ''
  });
  const [filterOptions, setFilterOptions] = useState({});
  
  // Pagination
  const [pagination, setPagination] = useState({
    limit: 100,
    offset: 0
  });

  const [history, setHistory] = useState([]);
  const [historyTotal, setHistoryTotal] = useState(0);
  const [historyPage, setHistoryPage] = useState(1);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyFilters, setHistoryFilters] = useState({ staging_table: '', migrated_by: '', status: '' });

  const API_BASE = 'http://localhost:8000/api/admin';

  // Load staging tables on component mount
  useEffect(() => {
    loadStagingTables();
  }, []);

  // Load table summary when table is selected
  useEffect(() => {
    if (selectedTable) {
      loadTableSummary(selectedTable);
      loadPreviewData(selectedTable);
    }
  }, [selectedTable]);

  const loadStagingTables = async () => {
    try {
      setLoading(true);
      const response = await api.get(`${API_BASE}/staging/tables`);
      setStagingTables(response.data.staging_tables);
    } catch (error) {
      console.error('Error loading staging tables:', error);
      alert('Error loading staging tables');
    } finally {
      setLoading(false);
    }
  };

  const loadTableSummary = async (tableName) => {
    try {
      const response = await api.get(`${API_BASE}/staging/summary/${tableName}`);
      setTableSummary(response.data);
    } catch (error) {
      console.error('Error loading table summary:', error);
    }
  };

  const loadPreviewData = async (tableName, newFilters = filters, newPagination = pagination) => {
    try {
      setLoading(true);
      const params = {
        ...newFilters,
        ...newPagination
      };
      
      // Remove empty filters
      Object.keys(params).forEach(key => {
        if (params[key] === '') {
          delete params[key];
        }
      });

      const response = await api.get(`${API_BASE}/staging/preview/${tableName}`, { params });
      setPreviewData(response.data);
      setFilterOptions(response.data.filter_options);
    } catch (error) {
      console.error('Error loading preview data:', error);
      alert('Error loading preview data');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (filterName, value) => {
    const newFilters = { ...filters, [filterName]: value };
    setFilters(newFilters);
    setPagination({ ...pagination, offset: 0 }); // Reset to first page
    loadPreviewData(selectedTable, newFilters, { ...pagination, offset: 0 });
  };

  const handlePaginationChange = (newOffset) => {
    const newPagination = { ...pagination, offset: newOffset };
    setPagination(newPagination);
    loadPreviewData(selectedTable, filters, newPagination);
  };

  const handleMigration = async () => {
    if (!selectedTable) {
      alert('Please select a staging table first');
      return;
    }

    try {
      setMigrationLoading(true);
      setMigrationResult(null);
      
      const migrationRequest = {};
      Object.keys(filters).forEach(key => {
        if (filters[key]) {
          migrationRequest[key] = filters[key];
        }
      });

      const response = await api.post(
        `${API_BASE}/staging/migrate/${selectedTable}`,
        migrationRequest
      );
      setMigrationResult(response.data);
      alert(`Migration completed! ${response.data.records_migrated} records migrated.`);
      
      // Reload summary and preview
      loadTableSummary(selectedTable);
      loadPreviewData(selectedTable);
    } catch (error) {
      console.error('Error during migration:', error);
      alert('Error during migration: ' + (error.response?.data?.detail || error.message));
    } finally {
      setMigrationLoading(false);
    }
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat().format(num);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  // Fetch migration/upload/delete/purge history
  const fetchHistory = async () => {
    setHistoryLoading(true);
    try {
      const params = {
        limit: HISTORY_PAGE_SIZE,
        offset: (historyPage - 1) * HISTORY_PAGE_SIZE,
        ...Object.fromEntries(Object.entries(historyFilters).filter(([k, v]) => v))
      };
      const res = await api.get('/api/admin/staging/migration_history', { params });
      setHistory(res.data.history || []);
      setHistoryTotal(res.data.total || 0);
    } catch (err) {
      setHistory([]);
      setHistoryTotal(0);
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
    // eslint-disable-next-line
  }, [historyPage, historyFilters]);

  const handleHistoryFilterChange = (field, value) => {
    setHistoryFilters((prev) => ({ ...prev, [field]: value }));
    setHistoryPage(1);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Staging Data Manager</h1>
        <p className="text-gray-600">Preview and migrate data from staging tables to master tables</p>
      </div>

      {/* Table Selection */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Select Staging Table</h2>
        <StagingTableAutocomplete
          value={selectedTable}
          onChange={setSelectedTable}
          placeholder="Select a staging table..."
          className="p-3"
        />
      </div>

      {selectedTable && tableSummary && (
        <>
          {/* Table Summary */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Table Summary</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{formatNumber(tableSummary.total_records)}</div>
                <div className="text-sm text-gray-600">Total Records</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{tableSummary.unique_batches}</div>
                <div className="text-sm text-gray-600">Unique Batches</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{tableSummary.unique_sources}</div>
                <div className="text-sm text-gray-600">Unique Sources</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{tableSummary.unique_sessions}</div>
                <div className="text-sm text-gray-600">Unique Sessions</div>
              </div>
              <div className="text-center">
                <div className="text-sm font-semibold text-gray-800">{formatDate(tableSummary.earliest_upload)}</div>
                <div className="text-sm text-gray-600">Earliest Upload</div>
              </div>
              <div className="text-center">
                <div className="text-sm font-semibold text-gray-800">{formatDate(tableSummary.latest_upload)}</div>
                <div className="text-sm text-gray-600">Latest Upload</div>
              </div>
            </div>
          </div>

          {/* Filters */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Filters</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Batch ID</label>
                <select
                  value={filters.batch_id}
                  onChange={(e) => handleFilterChange('batch_id', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Batches</option>
                  {filterOptions.batch_id?.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Source Name</label>
                <select
                  value={filters.source_name}
                  onChange={(e) => handleFilterChange('source_name', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Sources</option>
                  {filterOptions.source_name?.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Session ID</label>
                <select
                  value={filters.session_id}
                  onChange={(e) => handleFilterChange('session_id', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Sessions</option>
                  {filterOptions.session_id?.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Migration Controls */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Migration Controls</h2>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">
                  Records to migrate: <span className="font-semibold">{previewData?.total_count || 0}</span>
                </p>
                <p className="text-sm text-gray-500">
                  {Object.keys(filters).filter(key => filters[key]).length > 0 
                    ? 'Filters applied' 
                    : 'No filters applied - will migrate all records'}
                </p>
              </div>
              <div className="flex gap-4">
                <button
                  onClick={handleMigration}
                  disabled={migrationLoading}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-md font-medium transition-colors"
                >
                  {migrationLoading ? 'Migrating...' : 'Migrate to Master'}
                </button>
                <button
                  className="bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-md font-medium transition-colors"
                  disabled={loading || !selectedTable || !Object.keys(filters).some(f => filters[f])}
                  title="Delete all data matching the current filters from this staging table"
                  onClick={async () => {
                    if (!selectedTable) return;
                    const filterPayload = {};
                    Object.keys(filters).forEach(f => {
                      if (filters[f]) filterPayload[f] = filters[f];
                    });
                    if (Object.keys(filterPayload).length === 0) {
                      alert("Please set at least one filter to delete data.");
                      return;
                    }
                    if (!window.confirm("Are you sure you want to delete all data matching these filters from this staging table? This cannot be undone.")) return;
                    try {
                      const res = await api.delete(`/api/admin/staging/delete/${selectedTable}`, { data: filterPayload });
                      alert(`Deleted ${res.data.rows_deleted} rows from ${selectedTable}`);
                      loadTableSummary(selectedTable);
                      loadPreviewData(selectedTable);
                      setFilters({ batch_id: '', source_name: '', session_id: '' });
                    } catch (err) {
                      alert(err.response?.data?.detail || "Failed to delete data");
                    }
                  }}
                >
                  Delete Filtered Data
                </button>
              </div>
            </div>
          </div>

          {/* Migration Result */}
          {migrationResult && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
              <h3 className="text-lg font-semibold text-green-800 mb-2">Migration Completed Successfully</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div className="text-sm text-green-600">Records Migrated</div>
                  <div className="text-lg font-bold text-green-800">{formatNumber(migrationResult.records_migrated)}</div>
                </div>
                <div>
                  <div className="text-sm text-green-600">Final Master Count</div>
                  <div className="text-lg font-bold text-green-800">{formatNumber(migrationResult.final_master_count)}</div>
                </div>
                <div>
                  <div className="text-sm text-green-600">Master Table</div>
                  <div className="text-lg font-bold text-green-800">{migrationResult.master_table}</div>
                </div>
                <div>
                  <div className="text-sm text-green-600">Migration Time</div>
                  <div className="text-lg font-bold text-green-800">{formatDate(migrationResult.migration_timestamp)}</div>
                </div>
              </div>
            </div>
          )}

          {/* Preview Data */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Data Preview</h2>
              <div className="text-sm text-gray-600">
                Showing {pagination.offset + 1}-{Math.min(pagination.offset + pagination.limit, previewData?.total_count || 0)} of {formatNumber(previewData?.total_count || 0)} records
              </div>
            </div>

            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-600">Loading preview data...</p>
              </div>
            ) : previewData?.sample_data?.length > 0 ? (
              <>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        {Object.keys(previewData.sample_data[0]).map(column => (
                          <th key={column} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            {column}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {previewData.sample_data.map((row, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          {Object.values(row).map((value, colIndex) => (
                            <td key={colIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {value === null ? 'NULL' : String(value).substring(0, 100)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                <div className="flex items-center justify-between mt-4">
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handlePaginationChange(Math.max(0, pagination.offset - pagination.limit))}
                      disabled={pagination.offset === 0}
                      className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>
                    <button
                      onClick={() => handlePaginationChange(pagination.offset + pagination.limit)}
                      disabled={pagination.offset + pagination.limit >= (previewData?.total_count || 0)}
                      className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next
                    </button>
                  </div>
                  <div className="text-sm text-gray-600">
                    Page {Math.floor(pagination.offset / pagination.limit) + 1} of {Math.ceil((previewData?.total_count || 0) / pagination.limit)}
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-8 text-gray-500">
                No data found with the current filters
              </div>
            )}
          </div>

          {/* Migration/Upload/Delete/Purge History */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">History (Upload, Migration, Delete, Purge)</h2>
            {/* Filters */}
            <div className="flex flex-wrap gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Staging Table</label>
                <select
                  value={historyFilters.staging_table}
                  onChange={e => handleHistoryFilterChange('staging_table', e.target.value)}
                  className="p-2 border border-gray-300 rounded-md"
                >
                  <option value="">All</option>
                  {stagingTables.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">User</label>
                <input
                  type="text"
                  value={historyFilters.migrated_by}
                  onChange={e => handleHistoryFilterChange('migrated_by', e.target.value)}
                  className="p-2 border border-gray-300 rounded-md"
                  placeholder="Username"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Event Type</label>
                <select
                  value={historyFilters.status}
                  onChange={e => handleHistoryFilterChange('status', e.target.value)}
                  className="p-2 border border-gray-300 rounded-md"
                >
                  <option value="">All</option>
                  <option value="upload">Upload</option>
                  <option value="success">Migration</option>
                  <option value="error">Migration Error</option>
                  <option value="deleted">Delete</option>
                  <option value="purged">Purge</option>
                  <option value="purged_master">Master Purge</option>
                </select>
              </div>
            </div>
            {/* Table */}
            {historyLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-600">Loading history...</p>
              </div>
            ) : history.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Event</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Staging Table</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Master Table</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Details</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Records</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Error</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {history.map((row, idx) => (
                      <tr key={row.id || idx} className={row.status === "error" ? "bg-red-50" : "hover:bg-gray-50"}>
                        <td className="px-4 py-2 text-sm font-semibold">{EVENT_STATUS_LABELS[row.status] || row.status}</td>
                        <td className="px-4 py-2 text-sm">{row.staging_table || '-'}</td>
                        <td className="px-4 py-2 text-sm">{row.master_table || '-'}</td>
                        <td className="px-4 py-2 text-sm">{row.migrated_by || '-'}</td>
                        <td className="px-4 py-2 text-xs max-w-xs truncate" title={row.filters ? JSON.stringify(row.filters) : ''}>
                          {row.status === 'upload' && row.filters?.filename ? (
                            <span>File: <span className="font-mono">{row.filters.filename}</span></span>
                          ) : row.status === 'deleted' && row.filters ? (
                            <span>Filters: {Object.entries(row.filters).map(([k, v]) => `${k}: ${v}`).join(', ')}</span>
                          ) : row.filters ? (
                            <span>{JSON.stringify(row.filters)}</span>
                          ) : '-'}
                        </td>
                        <td className="px-4 py-2 text-sm">{row.records_migrated ?? '-'}</td>
                        <td className="px-4 py-2 text-sm">{row.migration_timestamp ? new Date(row.migration_timestamp).toLocaleString() : ''}</td>
                        <td className={"px-4 py-2 text-sm font-semibold " + (row.status === "error" ? "text-red-600" : row.status === "success" ? "text-green-700" : "text-gray-700")}>{EVENT_STATUS_LABELS[row.status] || row.status}</td>
                        <td className="px-4 py-2 text-xs text-red-700 max-w-xs truncate" title={row.error_message}>{row.error_message}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">No history found</div>
            )}
            {/* Pagination */}
            <div className="flex items-center justify-between mt-4">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setHistoryPage(Math.max(1, historyPage - 1))}
                  disabled={historyPage === 1}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setHistoryPage(historyPage + 1)}
                  disabled={historyPage * HISTORY_PAGE_SIZE >= historyTotal}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
              <div className="text-sm text-gray-600">
                Page {historyPage} of {Math.ceil(historyTotal / HISTORY_PAGE_SIZE)}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default StagingManager; 