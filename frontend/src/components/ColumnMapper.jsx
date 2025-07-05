import React, { useEffect, useState } from "react";

export default function ColumnMapper({ dataset, mapping, setMapping }) {
  const [columns, setColumns] = useState([]);

  useEffect(() => {
    if (!dataset) return;
    fetch(`http://localhost:8000/api/dataset-columns?dataset=${encodeURIComponent(dataset)}`)
      .then((res) => res.json())
      .then((data) => setColumns(data.columns || []));
  }, [dataset]);

  if (!dataset) return null;

  return (
    <div className="mb-4 flex gap-4">
      <div>
        <label>Date column: </label>
        <select
          value={mapping.date_col || ""}
          onChange={e => setMapping(m => ({ ...m, date_col: e.target.value }))}
        >
          <option value="">--</option>
          {columns.map(col => <option key={col} value={col}>{col}</option>)}
        </select>
      </div>
      <div>
        <label>Value column: </label>
        <select
          value={mapping.value_col || ""}
          onChange={e => setMapping(m => ({ ...m, value_col: e.target.value }))}
        >
          <option value="">--</option>
          {columns.map(col => <option key={col} value={col}>{col}</option>)}
        </select>
      </div>
      <div>
        <label>Postcode column: </label>
        <select
          value={mapping.postcode_col || ""}
          onChange={e => setMapping(m => ({ ...m, postcode_col: e.target.value }))}
        >
          <option value="">--</option>
          {columns.map(col => <option key={col} value={col}>{col}</option>)}
        </select>
      </div>
    </div>
  );
}