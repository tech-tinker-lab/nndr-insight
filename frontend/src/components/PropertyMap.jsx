// PropertyMap.jsx
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function PropertyMap() {
  const [properties, setProperties] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [dataset, setDataset] = useState('');
  const [latCol, setLatCol] = useState('Latitude');
  const [lonCol, setLonCol] = useState('Longitude');
  const [columns, setColumns] = useState([]);

  // Fetch available datasets
  useEffect(() => {
    fetch('http://localhost:8000/api/datasets')
      .then(res => res.json())
      .then(data => setDatasets(data.datasets || []));
  }, []);

  // Fetch columns for selected dataset
  useEffect(() => {
    if (!dataset) return setColumns([]);
    fetch(`http://localhost:8000/api/dataset-columns?dataset=${encodeURIComponent(dataset)}`)
      .then(res => res.json())
      .then(data => setColumns(data.columns || []));
  }, [dataset]);

  const fetchMap = async () => {
    const params = new URLSearchParams({
      dataset,
      lat_col: latCol,
      lon_col: lonCol
    });
    const res = await fetch(`http://localhost:8000/api/map?${params.toString()}`);
    const json = await res.json();
    setProperties(json.properties || []);
  };

  return (
    <div>
      <h2 className="font-semibold mb-2">Property Map</h2>
      <div className="flex gap-4 mb-2">
        <div>
          <label>Dataset: </label>
          <select value={dataset} onChange={e => setDataset(e.target.value)}>
            <option value="">-- Choose --</option>
            {datasets.map(ds => <option key={ds} value={ds}>{ds}</option>)}
          </select>
        </div>
        <div>
          <label>Latitude column: </label>
          <select value={latCol} onChange={e => setLatCol(e.target.value)}>
            {columns.map(col => <option key={col} value={col}>{col}</option>)}
          </select>
        </div>
        <div>
          <label>Longitude column: </label>
          <select value={lonCol} onChange={e => setLonCol(e.target.value)}>
            {columns.map(col => <option key={col} value={col}>{col}</option>)}
          </select>
        </div>
      </div>
      <button
        className="bg-purple-500 text-white px-4 py-2 rounded mb-4"
        onClick={fetchMap}
        disabled={!dataset || !latCol || !lonCol}
      >
        Load Map Data
      </button>
      {properties.length > 0 && (
        <MapContainer
          center={[properties[0].Latitude, properties[0].Longitude]}
          zoom={13}
          style={{ height: '400px', width: '100%' }}
        >
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          {properties.map((p, i) => (
            <Marker key={p.PropertyID || i} position={[p.Latitude, p.Longitude]}>
              <Popup>
                <strong>{p.Address}</strong>
                <br />
                {p.Postcode}
                <br />
                Status: {p.CurrentRatingStatus}
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      )}
    </div>
  );
}
