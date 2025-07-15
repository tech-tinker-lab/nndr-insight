import React, { useRef, useEffect, useState } from 'react';
import ForecastChart from '../components/ForecastChart';
import DataTable from '../components/DataTable';
import { Button, Tooltip as MuiTooltip } from '@mui/material';
import { FileDown, BarChart2, ArrowLeft, Image as ImageIcon } from 'lucide-react';
import { exportToCSV, exportToPDF, exportChartAsImage } from '../services/exportUtils';
import axios from 'axios';

const IndicatorAnalysis = () => {
  const chartRef = useRef();
  const [indicator, setIndicator] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    axios.get('/api/indicator/1')
      .then(res => {
        setIndicator(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load indicator data');
        setLoading(false);
      });
  }, []);

  function handleExportCSV() {
    if (indicator) {
      exportToCSV(indicator.values, `indicator_${indicator.name.replace(/\s+/g,'_')}.csv`);
    }
  }

  async function handleExportPDF() {
    if (indicator) {
      const chartDataUrl = await exportChartAsImage(chartRef);
      await exportToPDF(
        indicator.values,
        `indicator_${indicator.name.replace(/\s+/g,'_')}.pdf`,
        `Indicator: ${indicator.name}`,
        chartDataUrl,
        'South Cambrishire NNDR Insights & Forecast'
      );
    }
  }

  async function handleExportChartPNG() {
    const chartDataUrl = await exportChartAsImage(chartRef);
    if (chartDataUrl && indicator) {
      const a = document.createElement('a');
      a.href = chartDataUrl;
      a.download = `indicator_chart_${indicator.name.replace(/\s+/g,'_')}.png`;
      a.click();
    }
  }

  if (loading) return <div className="p-6">Loading indicator...</div>;
  if (error) return <div className="p-6 text-red-600">{error}</div>;
  if (!indicator) return <div className="p-6">No indicator data available.</div>;

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between mb-2">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <BarChart2 className="w-7 h-7 text-purple-600" />
          Indicator Analysis: {indicator.name}
        </h1>
        <div className="flex gap-2">
          <MuiTooltip title="Export as CSV" arrow>
            <Button variant="outlined" color="primary" startIcon={<FileDown />} onClick={handleExportCSV}>CSV</Button>
          </MuiTooltip>
          <MuiTooltip title="Export as PDF (with chart)" arrow>
            <Button variant="outlined" color="secondary" startIcon={<FileDown />} onClick={handleExportPDF}>PDF</Button>
          </MuiTooltip>
          <MuiTooltip title="Export chart as PNG image" arrow>
            <Button variant="outlined" color="info" startIcon={<ImageIcon />} onClick={handleExportChartPNG}>Chart PNG</Button>
          </MuiTooltip>
        </div>
      </div>
      <div className="mb-6" ref={chartRef} style={{ background: 'white', borderRadius: 8, padding: 8 }}>
        <ForecastChart data={indicator.trend.map(t => ({ sector: t.year, value: t.value }))} />
      </div>
      <div className="mb-6">
        <MuiTooltip title="Indicator values by year and area" arrow>
          <div>
            <DataTable data={indicator.values} columns={[{Header:'Year',accessor:'year'},{Header:'Area',accessor:'area'},{Header:'Value',accessor:'value'}]} />
          </div>
        </MuiTooltip>
      </div>
      <MuiTooltip title="Back to Dashboard" arrow>
        <Button variant="text" startIcon={<ArrowLeft />} onClick={()=>window.history.back()}>
          Back
        </Button>
      </MuiTooltip>
    </div>
  );
};

export default IndicatorAnalysis; 