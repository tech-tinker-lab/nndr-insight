import React, { useEffect, useState } from 'react';

export default function DataTable({ columns, fetchUrl }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');

  useEffect(() => {
    setLoading(true);
    let url = `${fetchUrl}?page=${page}&page_size=${pageSize}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    fetch(url)
      .then((res) => res.json())
      .then((json) => {
        setData(json.items || json.results || []);
        setTotal(json.total || json.count || 0);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, [fetchUrl, page, pageSize, search]);

  return (
    <div className="p-4">
      <div className="flex mb-2 items-center">
        <input
          className="border px-2 py-1 rounded mr-2"
          placeholder="Search..."
          value={search}
          onChange={e => { setSearch(e.target.value); setPage(1); }}
        />
        <span className="text-sm text-gray-500">{total} records</span>
      </div>
      <div className="overflow-x-auto border rounded">
        <table className="min-w-full text-sm">
          <thead>
            <tr>
              {columns.map(col => (
                <th key={col.key} className="px-2 py-1 bg-gray-200 border-b text-left">{col.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={columns.length} className="text-center p-4">Loading...</td></tr>
            ) : error ? (
              <tr><td colSpan={columns.length} className="text-center text-red-500">{error}</td></tr>
            ) : data.length === 0 ? (
              <tr><td colSpan={columns.length} className="text-center p-4">No data</td></tr>
            ) : (
              data.map((row, i) => (
                <tr key={row.id || i} className="hover:bg-blue-50">
                  {columns.map(col => (
                    <td key={col.key} className="px-2 py-1 border-b">{row[col.key]}</td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <div className="flex justify-between items-center mt-2">
        <button
          className="px-2 py-1 border rounded disabled:opacity-50"
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
        >Prev</button>
        <span>Page {page}</span>
        <button
          className="px-2 py-1 border rounded disabled:opacity-50"
          onClick={() => setPage(p => p + 1)}
          disabled={page * pageSize >= total}
        >Next</button>
        <select
          className="ml-2 border rounded px-1"
          value={pageSize}
          onChange={e => { setPageSize(Number(e.target.value)); setPage(1); }}
        >
          {[10, 20, 50, 100].map(sz => <option key={sz} value={sz}>{sz}</option>)}
        </select>
      </div>
    </div>
  );
}
