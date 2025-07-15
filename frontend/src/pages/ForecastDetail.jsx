import React, { useRef, useEffect, useState } from 'react';
import ForecastChart from '../components/ForecastChart';
import DataTable from '../components/DataTable';
import PropertyMap from '../components/PropertyMap';
import { Button, Tooltip as MuiTooltip } from '@mui/material';
import { FileDown, FileText, ArrowLeft, Image as ImageIcon } from 'lucide-react';
import { exportToCSV, exportToPDF, exportChartAsImage } from '../services/exportUtils';
import axios from 'axios';

const ForecastDetail = () => {
  const chartRef = useRef();
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    axios.get('/api/forecast')
      .then(res => {
        setForecast(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load forecast data');
        setLoading(false);
      });
  }, []);

  function handleExportCSV() {
    if (forecast) {
      exportToCSV(forecast.properties, `forecast_properties_${forecast.area.replace(/\s+/g,'_')}_${forecast.year}.csv`);
    }
  }

  async function handleExportPDF() {
    if (forecast) {
      const chartDataUrl = await exportChartAsImage(chartRef);
      await exportToPDF(
        forecast.properties,
        `forecast_properties_${forecast.area.replace(/\s+/g,'_')}_${forecast.year}.pdf`,
        `Forecast Properties: ${forecast.area} (${forecast.year})`,
        chartDataUrl,
        'South Cambrishire NNDR Insights & Forecast'
      );
    }
  }

  async function handleExportChartPNG() {
    const chartDataUrl = await exportChartAsImage(chartRef);
    if (chartDataUrl) {
      const a = document.createElement('a');
      a.href = chartDataUrl;
      a.download = forecast ? `forecast_chart_${forecast.area.replace(/\s+/g,'_')}_${forecast.year}.png` : 'forecast_chart.png';
      a.click();
    }
  }

  if (loading) return <div className="p-6">Loading forecast...</div>;
  if (error) return <div className="p-6 text-red-600">{error}</div>;
  if (!forecast) return <div className="p-6">No forecast data available.</div>;

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between mb-2">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <FileText className="w-7 h-7 text-blue-600" />
          Forecast Detail: {forecast.area} ({forecast.year})
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
        <ForecastChart data={forecast.breakdown} />
      </div>
      <div className="mb-6">
        <MuiTooltip title="Click a row for property details" arrow>
          <div>
            <DataTable data={forecast.properties} columns={[{Header:'Address',accessor:'address'},{Header:'Rateable Value',accessor:'rateableValue'},{Header:'Sector',accessor:'sector'}]} />
          </div>
        </MuiTooltip>
      </div>
      <div className="mb-6">
        <PropertyMap properties={forecast.properties} />
      </div>
      <MuiTooltip title="Back to Dashboard" arrow>
        <Button variant="text" startIcon={<ArrowLeft />} onClick={()=>window.history.back()}>
          Back
        </Button>
      </MuiTooltip>
    </div>
  );
};

export default ForecastDetail; 