import React, { useEffect, useState } from "react";

export default function NonRatedProperties() {
  const [datasets, setDatasets] = useState([]);
  const [columnsA, setColumnsA] = useState([]);
  const [columnsB, setColumnsB] = useState([]);
  const [nndrDataset, setNndrDataset] = useState("");
  const [allPropsDataset, setAllPropsDataset] = useState("");
  const [nndrPostcodeCol, setNndrPostcodeCol] = useState("");
  const [allPostcodeCol, setAllPostcodeCol] = useState("");
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);

  // Fetch available datasets
  useEffect(() => {
    fetch("http://localhost:8000/api/datasets")
      .then(res => res.json())
      .then(data => setDatasets(data.datasets || []));
  }, []);

  // Fetch columns for NNDR dataset
  useEffect(() => {
    if (!nndrDataset) return setColumnsA([]);
    fetch(`http://localhost:8000/api/dataset-columns?dataset=${encodeURIComponent(nndrDataset)}`)
      .then(res => res.json())
      .then(data => setColumnsA(data.columns || []));
  }, [nndrDataset]);

  // Fetch columns for all properties dataset
  useEffect(() => {
    if (!allPropsDataset) return setColumnsB([]);
    fetch(`http://localhost:8000/api/dataset-columns?dataset=${encodeURIComponent(allPropsDataset)}`)
      .then(res => res.json())
      .then(data => setColumnsB(data.columns || []));
  }, [allPropsDataset]);

  const findMissing = async () => {
    if (!nndrDataset || !allPropsDataset || !nndrPostcodeCol || !allPostcodeCol) return;
    const params = new URLSearchParams({
      nndr_dataset: nndrDataset,
      all_props_dataset: allPropsDataset,
      nndr_postcode_col: nndrPostcodeCol,
      all_postcode_col: allPostcodeCol,
      limit: 100
    });
    const res = await fetch(`http://localhost:8000/api/non-rated-properties?${params.toString()}`);
    const json = await res.json();
    setResults(json.missing_properties || []);
    setTotal(json.total_missing || 0);
  };

  return (
    <div className="mb-8">
      <h2 className="font-semibold mb-2">Find Non-Rated Properties</h2>
      <div className="flex gap-4 mb-4">
        <div>
          <label>Rated (NNDR) dataset: </label>
          <select value={nndrDataset} onChange={e => setNndrDataset(e.target.value)}>
            <option value="">-- Choose --</option>
            {datasets.map(ds => <option key={ds} value={ds}>{ds}</option>)}
          </select>
          <br />
          <label>Postcode column: </label>
          <select value={nndrPostcodeCol} onChange={e => setNndrPostcodeCol(e.target.value)}>
            <option value="">-- Choose --</option>
            {columnsA.map(col => <option key={col} value={col}>{col}</option>)}
          </select>
        </div>
        <div>
          <label>All properties dataset: </label>
          <select value={allPropsDataset} onChange={e => setAllPropsDataset(e.target.value)}>
            <option value="">-- Choose --</option>
            {datasets.map(ds => <option key={ds} value={ds}>{ds}</option>)}
          </select>
          <br />
          <label>Postcode column: </label>
          <select value={allPostcodeCol} onChange={e => setAllPostcodeCol(e.target.value)}>
            <option value="">-- Choose --</option>
            {columnsB.map(col => <option key={col} value={col}>{col}</option>)}
          </select>
        </div>
      </div>
      <button
        className="bg-purple-600 text-white px-4 py-2 rounded mb-4"
        onClick={findMissing}
        disabled={!nndrDataset || !allPropsDataset || !nndrPostcodeCol || !allPostcodeCol}
      >
        Find Non-Rated Properties
      </button>
      {results.length > 0 && (
        <>
          <div className="mb-2">Showing {results.length} of {total} missing properties</div>
          <table className="table-auto w-full text-xs">
            <thead>
              <tr>
                {Object.keys(results[0]).map(key => (
                  <th key={key} className="border px-2 py-1">{key}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {results.map((row, idx) => (
                <tr key={idx}>
                  {Object.values(row).map((val, i) => (
                    <td key={i} className="border px-2 py-1">{val}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}