import React, { useState, useEffect } from "react";
import api from "../api/axios";
import { Database } from "lucide-react";
import toast from "react-hot-toast";
import clsx from "clsx";
import StagingTableAutocomplete from "../components/StagingTableAutocomplete";

const API_BASE = "/api/admin/staging";

const STAGING_TABLES = [
  "onspd_staging",
  "code_point_open_staging",
  "os_open_names_staging",
  "os_open_map_local_staging",
  "os_open_usrn_staging",
  "os_open_uprn_staging",
  "nndr_properties_staging",
  "nndr_ratepayers_staging",
  "valuations_staging",
  "lad_boundaries_staging"
];

const METADATA_FILTERS = ["batch_id", "source_name", "session_id"];

const HISTORY_PAGE_SIZE = 25;

export default function StagedData() {
  const [selectedTable, setSelectedTable] = useState("");
  const [columns, setColumns] = useState([]);
  const [filters, setFilters] = useState({});
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(50);
  const [filterOptions, setFilterOptions] = useState({});
  const [tab, setTab] = useState("preview");
  const [history, setHistory] = useState([]);
  const [historyTotal, setHistoryTotal] = useState(0);
  const [historyPage, setHistoryPage] = useState(1);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyFilters, setHistoryFilters] = useState({ staging_table: "", migrated_by: "", status: "" });

  useEffect(() => {
    if (selectedTable) {
      fetchPreview();
    }
    // eslint-disable-next-line
  }, [selectedTable, page, limit]);

  useEffect(() => {
    if (tab === "history") {
      fetchHistory();
    }
    // eslint-disable-next-line
  }, [tab, historyPage, historyFilters]);

  const fetchPreview = async () => {
    setLoading(true);
    try {
      const params = { ...filters, limit, offset: (page - 1) * limit };
      const res = await api.get(`${API_BASE}/preview/${selectedTable}`, { params });
      setData(res.data.sample_data || []);
      setTotal(res.data.total_count || 0);
      setFilterOptions(res.data.filter_options || {});
      if (res.data.sample_data && res.data.sample_data.length > 0) {
        setColumns(Object.keys(res.data.sample_data[0]));
      } else {
        setColumns([]);
      }
    } catch (err) {
      toast.error("Failed to fetch preview data");
      setData([]);
      setColumns([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const handleTableChange = (e) => {
    setSelectedTable(e.target.value);
    setFilters({});
    setPage(1);
  };

  const handleFilterChange = (col, value) => {
    setFilters((prev) => ({ ...prev, [col]: value }));
    setPage(1);
  };

  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  const fetchHistory = async () => {
    setHistoryLoading(true);
    try {
      const params = {
        limit: HISTORY_PAGE_SIZE,
        offset: (historyPage - 1) * HISTORY_PAGE_SIZE,
        ...Object.fromEntries(Object.entries(historyFilters).filter(([k, v]) => v))
      };
      const res = await api.get("/api/admin/staging/migration_history", { params });
      setHistory(res.data.history || []);
      setHistoryTotal(res.data.total || 0);
    } catch (err) {
      toast.error("Failed to fetch migration history");
      setHistory([]);
      setHistoryTotal(0);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleHistoryFilterChange = (field, value) => {
    setHistoryFilters((prev) => ({ ...prev, [field]: value }));
    setHistoryPage(1);
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="flex items-center mb-6">
        <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
          <Database className="w-6 h-6 text-white" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900">Staged Data</h1>
      </div>
      {/* Tabs */}
      <div className="flex space-x-4 mb-6">
        <button
          className={clsx("px-4 py-2 rounded-t font-medium", tab === "preview" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700")}
          onClick={() => setTab("preview")}
        >
          Data Preview
        </button>
        <button
          className={clsx("px-4 py-2 rounded-t font-medium", tab === "history" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700")}
          onClick={() => setTab("history")}
        >
          Migration History
        </button>
      </div>

      {tab === "preview" && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Select Staging Table</label>
          <StagingTableAutocomplete
            value={selectedTable}
            onChange={setSelectedTable}
            placeholder="Select a staging table..."
            className="p-3"
          />
        </div>
      )}
      {tab === "preview" && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            {METADATA_FILTERS.map((col) => (
              <div key={col}>
                <label className="block text-sm font-medium text-gray-700 mb-2">{col.replace('_', ' ').toUpperCase()}</label>
                <select
                  value={filters[col] || ""}
                  onChange={(e) => handleFilterChange(col, e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="">All</option>
                  {(filterOptions[col] || []).map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              </div>
            ))}
            {/* Data column filters */}
            {columns.filter((col) => !METADATA_FILTERS.includes(col)).map((col) => (
              <div key={col}>
                <label className="block text-sm font-medium text-gray-700 mb-2">{col}</label>
                <input
                  type="text"
                  value={filters[col] || ""}
                  onChange={(e) => handleFilterChange(col, e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md"
                  placeholder={`Filter by ${col}`}
                />
              </div>
            ))}
          </div>
          <button
            className="bg-blue-600 text-white px-4 py-2 rounded-md font-medium"
            onClick={fetchPreview}
            disabled={loading}
          >
            Apply Filters
          </button>
          <button
            className="bg-red-600 text-white px-4 py-2 rounded-md font-medium ml-4"
            onClick={async () => {
              if (!selectedTable) return;
              // Only allow if at least one filter is set
              const filterPayload = {};
              ["batch_id", "source_name", "session_id"].forEach(f => {
                if (filters[f]) filterPayload[f] = filters[f];
              });
              if (Object.keys(filterPayload).length === 0) {
                toast.error("Please set at least one filter to delete data.");
                return;
              }
              if (!window.confirm("Are you sure you want to delete all data matching these filters from this staging table? This cannot be undone.")) return;
              try {
                const res = await api.delete(`/api/admin/staging/delete/${selectedTable}`, { data: filterPayload });
                toast.success(`Deleted ${res.data.rows_deleted} rows from ${selectedTable}`);
                fetchPreview();
              } catch (err) {
                toast.error(err.response?.data?.detail || "Failed to delete data");
              }
            }}
            disabled={loading || !selectedTable || !["batch_id", "source_name", "session_id"].some(f => filters[f])}
            title="Delete all data matching the current filters from this staging table"
          >
            Delete Filtered Data
          </button>
        </div>
      )}
      {tab === "preview" && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Data Preview</h2>
            <div className="text-sm text-gray-600">
              Showing {(page - 1) * limit + 1}-{Math.min(page * limit, total)} of {total} records
            </div>
          </div>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading preview data...</p>
            </div>
          ) : data.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {columns.map((col) => (
                      <th key={col} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data.map((row, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      {columns.map((col) => (
                        <td key={col} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {row[col] === null ? 'NULL' : String(row[col]).substring(0, 100)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No data found with the current filters
            </div>
          )}
          {/* Pagination */}
          <div className="flex items-center justify-between mt-4">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handlePageChange(Math.max(1, page - 1))}
                disabled={page === 1}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={() => handlePageChange(page + 1)}
                disabled={page * limit >= total}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
            <div className="text-sm text-gray-600">
              Page {page} of {Math.ceil(total / limit)}
            </div>
          </div>
        </div>
      )}

      {tab === "history" && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Migration History</h2>
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Staging Table</label>
              <select
                value={historyFilters.staging_table}
                onChange={e => handleHistoryFilterChange("staging_table", e.target.value)}
                className="p-2 border border-gray-300 rounded-md"
              >
                <option value="">All</option>
                {STAGING_TABLES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Migrated By</label>
              <input
                type="text"
                value={historyFilters.migrated_by}
                onChange={e => handleHistoryFilterChange("migrated_by", e.target.value)}
                className="p-2 border border-gray-300 rounded-md"
                placeholder="Username"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                value={historyFilters.status}
                onChange={e => handleHistoryFilterChange("status", e.target.value)}
                className="p-2 border border-gray-300 rounded-md"
              >
                <option value="">All</option>
                <option value="success">Success</option>
                <option value="error">Error</option>
              </select>
            </div>
          </div>
          {/* Table */}
          {historyLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading migration history...</p>
            </div>
          ) : history.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Staging Table</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Master Table</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Migrated By</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Records Migrated</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Final Master Count</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Error</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {history.map((row, idx) => (
                    <tr key={row.id || idx} className={row.status === "error" ? "bg-red-50" : "hover:bg-gray-50"}>
                      <td className="px-4 py-2 text-sm">{row.staging_table}</td>
                      <td className="px-4 py-2 text-sm">{row.master_table}</td>
                      <td className="px-4 py-2 text-sm">{row.migrated_by}</td>
                      <td className="px-4 py-2 text-sm">{row.records_migrated}</td>
                      <td className="px-4 py-2 text-sm">{row.final_master_count}</td>
                      <td className="px-4 py-2 text-sm">{row.migration_timestamp ? new Date(row.migration_timestamp).toLocaleString() : ""}</td>
                      <td className={clsx("px-4 py-2 text-sm font-semibold", row.status === "error" ? "text-red-600" : "text-green-700")}>{row.status}</td>
                      <td className="px-4 py-2 text-xs text-red-700 max-w-xs truncate" title={row.error_message}>{row.error_message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">No migration history found</div>
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
      )}
    </div>
  );
} 