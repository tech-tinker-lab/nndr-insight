import React, { useState, useRef, useEffect } from 'react';
import DataTable from '../components/DataTable';
import PropertyMap from '../components/PropertyMap';
import { Button, Tooltip as MuiTooltip } from '@mui/material';
import { FileDown, FileText, ArrowLeft, Info, Image as ImageIcon } from 'lucide-react';
import { exportToCSV, exportToPDF, exportChartAsImage } from '../services/exportUtils';
import axios from 'axios';

const AreaDrilldown = () => {
  const [area, setArea] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(null);
  const mapRef = useRef();

  useEffect(() => {
    setLoading(true);
    axios.get('/api/area/1')
      .then(res => {
        setArea(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load area data');
        setLoading(false);
      });
  }, []);

  function handleExportCSV() {
    if (area) {
      exportToCSV(area.properties, `area_properties_${area.name.replace(/\s+/g,'_')}.csv`);
    }
  }

  async function handleExportPDF() {
    if (area) {
      const mapDataUrl = await exportChartAsImage(mapRef);
      await exportToPDF(
        area.properties,
        `area_properties_${area.name.replace(/\s+/g,'_')}.pdf`,
        `Area Properties: ${area.name}`,
        mapDataUrl,
        'South Cambrishire NNDR Insights & Forecast'
      );
    }
  }

  async function handleExportMapPNG() {
    const mapDataUrl = await exportChartAsImage(mapRef);
    if (mapDataUrl && area) {
      const a = document.createElement('a');
      a.href = mapDataUrl;
      a.download = `area_map_${area.name.replace(/\s+/g,'_')}.png`;
      a.click();
    }
  }

  if (loading) return <div className="p-6">Loading area...</div>;
  if (error) return <div className="p-6 text-red-600">{error}</div>;
  if (!area) return <div className="p-6">No area data available.</div>;

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between mb-2">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <FileText className="w-7 h-7 text-green-600" />
          Area Drill-Down: {area.name}
        </h1>
        <div className="flex gap-2">
          <MuiTooltip title="Export as CSV" arrow>
            <Button variant="outlined" color="primary" startIcon={<FileDown />} onClick={handleExportCSV}>CSV</Button>
          </MuiTooltip>
          <MuiTooltip title="Export as PDF (with map)" arrow>
            <Button variant="outlined" color="secondary" startIcon={<FileDown />} onClick={handleExportPDF}>PDF</Button>
          </MuiTooltip>
          <MuiTooltip title="Export map as PNG image" arrow>
            <Button variant="outlined" color="info" startIcon={<ImageIcon />} onClick={handleExportMapPNG}>Map PNG</Button>
          </MuiTooltip>
        </div>
      </div>
      <div className="mb-6" ref={mapRef} style={{ background: 'white', borderRadius: 8, padding: 8 }}>
        <PropertyMap properties={area.properties} onSelect={setSelected} />
      </div>
      <div className="mb-6">
        <MuiTooltip title="Click a row for property details" arrow>
          <div>
            <DataTable
              data={area.properties}
              columns={[
                { Header: 'Address', accessor: 'address' },
                { Header: 'Rateable Value', accessor: 'rateableValue' },
                { Header: 'Sector', accessor: 'sector' },
                { Header: 'Reliefs', accessor: 'reliefs' },
                { Header: 'History', accessor: 'history' },
              ]}
              onRowClick={row => setSelected(row)}
            />
          </div>
        </MuiTooltip>
      </div>
      {selected && (
        <div className="mb-6 p-4 border rounded bg-gray-50">
          <h2 className="text-xl font-semibold mb-2 flex items-center gap-2"><Info className="w-5 h-5 text-blue-500" />Property Detail</h2>
          <div>Address: {selected.address}</div>
          <div>Rateable Value: {selected.rateableValue}</div>
          <div>Sector: {selected.sector}</div>
          <div>Reliefs: {selected.reliefs}</div>
          <div>History: {selected.history}</div>
          <MuiTooltip title="Close property detail" arrow>
            <Button className="mt-2" variant="outlined" startIcon={<ArrowLeft />} onClick={() => setSelected(null)}>
              Close
            </Button>
          </MuiTooltip>
        </div>
      )}
      <MuiTooltip title="Back to Dashboard" arrow>
        <Button variant="text" startIcon={<ArrowLeft />} onClick={()=>window.history.back()}>
          Back
        </Button>
      </MuiTooltip>
    </div>
  );
};

export default AreaDrilldown; 