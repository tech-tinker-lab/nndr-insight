import React, { useState, useRef, useEffect } from 'react';
import { Button, Tooltip as MuiTooltip } from '@mui/material';
import { FileDown, FileBarChart2, ArrowLeft, Filter, Image as ImageIcon } from 'lucide-react';
import { exportToCSV, exportToPDF, exportChartAsImage } from '../services/exportUtils';
import axios from 'axios';

const mockOptions = {
  years: [2020, 2021, 2022, 2023, 2024],
  areas: ['South Cambs', 'Cambridge North', 'Ely'],
  indicators: ['Retail Rateable Value Index', 'Office Occupancy Rate', 'Industrial Growth Factor'],
};

const ReportBuilder = () => {
  const [selectedYears, setSelectedYears] = useState([2024]);
  const [selectedAreas, setSelectedAreas] = useState(['South Cambs']);
  const [selectedIndicators, setSelectedIndicators] = useState(['Retail Rateable Value Index']);
  const [previewData, setPreviewData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const previewRef = useRef();

  useEffect(() => {
    setLoading(true);
    axios.get('/api/indicators')
      .then(res => {
        // For demo, use the first indicator's values as the preview
        setPreviewData(res.data[0]?.values || []);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load report data');
        setLoading(false);
      });
  }, []);

  function handleExportCSV() {
    exportToCSV(previewData, 'custom_report.csv');
  }

  async function handleExportPDF() {
    const previewDataUrl = await exportChartAsImage(previewRef);
    await exportToPDF(
      previewData,
      'custom_report.pdf',
      'Custom Report',
      previewDataUrl,
      'South Cambrishire NNDR Insights & Forecast'
    );
  }

  async function handleExportPreviewPNG() {
    const previewDataUrl = await exportChartAsImage(previewRef);
    if (previewDataUrl) {
      const a = document.createElement('a');
      a.href = previewDataUrl;
      a.download = 'custom_report_preview.png';
      a.click();
    }
  }

  if (loading) return <div className="p-6">Loading report preview...</div>;
  if (error) return <div className="p-6 text-red-600">{error}</div>;

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between mb-2">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <FileBarChart2 className="w-7 h-7 text-blue-600" />
          Custom Report Builder
        </h1>
        <div className="flex gap-2">
          <MuiTooltip title="Export as CSV" arrow>
            <Button variant="outlined" color="primary" startIcon={<FileDown />} onClick={handleExportCSV}>CSV</Button>
          </MuiTooltip>
          <MuiTooltip title="Export as PDF (with preview)" arrow>
            <Button variant="outlined" color="secondary" startIcon={<FileDown />} onClick={handleExportPDF}>PDF</Button>
          </MuiTooltip>
          <MuiTooltip title="Export preview as PNG image" arrow>
            <Button variant="outlined" color="info" startIcon={<ImageIcon />} onClick={handleExportPreviewPNG}>Preview PNG</Button>
          </MuiTooltip>
        </div>
      </div>
      <div className="mb-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="font-semibold flex items-center gap-1"><Filter className="w-4 h-4 text-blue-400" />Years</label>
          <select multiple className="w-full border p-2 rounded" value={selectedYears} onChange={e => setSelectedYears(Array.from(e.target.selectedOptions, o => o.value))}>
            {mockOptions.years.map(y => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>
        <div>
          <label className="font-semibold flex items-center gap-1"><Filter className="w-4 h-4 text-green-400" />Areas</label>
          <select multiple className="w-full border p-2 rounded" value={selectedAreas} onChange={e => setSelectedAreas(Array.from(e.target.selectedOptions, o => o.value))}>
            {mockOptions.areas.map(a => <option key={a} value={a}>{a}</option>)}
          </select>
        </div>
        <div>
          <label className="font-semibold flex items-center gap-1"><Filter className="w-4 h-4 text-purple-400" />Indicators</label>
          <select multiple className="w-full border p-2 rounded" value={selectedIndicators} onChange={e => setSelectedIndicators(Array.from(e.target.selectedOptions, o => o.value))}>
            {mockOptions.indicators.map(i => <option key={i} value={i}>{i}</option>)}
          </select>
        </div>
      </div>
      <div className="mb-6 p-4 border rounded bg-gray-50" ref={previewRef} style={{ background: 'white' }}>
        <h2 className="text-lg font-semibold mb-2 flex items-center gap-2"><FileBarChart2 className="w-5 h-5 text-blue-500" />Report Preview</h2>
        {previewData.length === 0 ? (
          <div className="text-gray-500">No data available for preview.</div>
        ) : (
          <table className="min-w-full text-xs">
            <thead>
              <tr>
                {Object.keys(previewData[0]).map((col) => (
                  <th key={col} className="px-2 py-1 text-left font-semibold text-gray-700">{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {previewData.map((row, idx) => (
                <tr key={idx} className="border-b last:border-0">
                  {Object.values(row).map((val, i) => (
                    <td key={i} className="px-2 py-1">{val}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      <MuiTooltip title="Back to Dashboard" arrow>
        <Button variant="text" startIcon={<ArrowLeft />} onClick={()=>window.history.back()}>
          Back
        </Button>
      </MuiTooltip>
    </div>
  );
};

export default ReportBuilder; 