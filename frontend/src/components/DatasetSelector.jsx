import React, { useEffect, useState } from "react";

export default function DatasetSelector({ selected, onSelect }) {
  const [datasets, setDatasets] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/datasets")
      .then((res) => res.json())
      .then((data) => setDatasets(data.datasets));
  }, []);

  return (
    <div className="mb-4">
      <label className="font-semibold mr-2">Select Dataset:</label>
      <select
        value={selected}
        onChange={(e) => onSelect(e.target.value)}
        className="border px-2 py-1"
      >
        <option value="">-- Choose --</option>
        {datasets.map((ds) => (
          <option key={ds} value={ds}>
            {ds}
          </option>
        ))}
      </select>
    </div>
  );
}