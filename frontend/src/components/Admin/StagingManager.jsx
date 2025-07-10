import React, { useState, useEffect } from 'react';
import axios from 'axios';

const StagingManager = () => {
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
      const response = await axios.get(`${API_BASE}/staging/tables`);
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
      const response = await axios.get(`${API_BASE}/staging/summary/${tableName}`);
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

      const response = await axios.get(`${API_BASE}/staging/preview/${tableName}`, { params });
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

      const response = await axios.post(`${API_BASE}/staging/migrate/${selectedTable}`, migrationRequest);
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

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Staging Data Manager</h1>
        <p className="text-gray-600">Preview and migrate data from staging tables to master tables</p>
      </div>

      {/* Table Selection */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Select Staging Table</h2>
        <select
          value={selectedTable}
          onChange={(e) => setSelectedTable(e.target.value)}
          className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Select a staging table...</option>
          {stagingTables.map(table => (
            <option key={table} value={table}>{table}</option>
          ))}
        </select>
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
              <button
                onClick={handleMigration}
                disabled={migrationLoading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-md font-medium transition-colors"
              >
                {migrationLoading ? 'Migrating...' : 'Migrate to Master'}
              </button>
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
        </>
      )}
    </div>
  );
};

export default StagingManager; 