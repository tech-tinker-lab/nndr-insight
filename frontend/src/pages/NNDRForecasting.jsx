import React, { useState } from 'react';
import { Tabs, Tab, Box, Typography, Paper, Grid, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { DataGrid } from '@mui/x-data-grid';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import {
  summaryCards,
  sectorBreakdown,
  topRatepayers,
  reliefDistribution,
  mapPoints,
  nndrTrends,
} from './dashboardMockData';

// Mock data
const mockForecastData = [
  { id: 1, area: 'LAD 1', year: 2024, forecast: 1200000, growth: 0.03 },
  { id: 2, area: 'LAD 2', year: 2024, forecast: 950000, growth: 0.025 },
  { id: 3, area: 'LAD 3', year: 2024, forecast: 780000, growth: 0.02 },
  { id: 4, area: 'LAD 4', year: 2024, forecast: 670000, growth: 0.018 },
];
const mockTimeSeries = [
  { year: 2020, value: 900000 },
  { year: 2021, value: 950000 },
  { year: 2022, value: 1000000 },
  { year: 2023, value: 1100000 },
  { year: 2024, value: 1200000 },
];
const mockGeoJson = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": { "name": "LAD 1", "forecast": 1200000 },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [-0.1, 51.5],
            [-0.12, 51.5],
            [-0.12, 51.52],
            [-0.1, 51.52],
            [-0.1, 51.5]
          ]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": { "name": "LAD 2", "forecast": 950000 },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [-0.13, 51.5],
            [-0.15, 51.5],
            [-0.15, 51.52],
            [-0.13, 51.52],
            [-0.13, 51.5]
          ]
        ]
      }
    }
  ]
};
const chartColors = ['#1976d2', '#43a047', '#fbc02d', '#e53935'];

const NNDRForecasting = () => {
  const [tab, setTab] = useState(0);
  const [year, setYear] = useState(2024);
  const [scenario, setScenario] = useState('baseline');

  // Table columns
  const columns = [
    { field: 'area', headerName: 'Area', flex: 1 },
    { field: 'year', headerName: 'Year', flex: 1 },
    { field: 'forecast', headerName: 'Forecast (£)', flex: 1, type: 'number' },
    { field: 'growth', headerName: 'Growth Rate', flex: 1, type: 'number', valueFormatter: ({ value }) => `${(value * 100).toFixed(1)}%` },
  ];

  return (
    <Box sx={{ p: { xs: 1, md: 3 } }}>
      {/* Header */}
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>NNDR Forecasting Dashboard</Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Visualise, analyse, and compare National Non-Domestic Rates (NNDR) forecasts by area, year, and scenario. Use the map, table, and charts to explore trends and spatial patterns.
        </Typography>
        <Grid container spacing={2} alignItems="center" sx={{ mt: 1 }}>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Year</InputLabel>
              <Select value={year} label="Year" onChange={e => setYear(e.target.value)}>
                {[2020, 2021, 2022, 2023, 2024].map(y => <MenuItem key={y} value={y}>{y}</MenuItem>)}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Scenario</InputLabel>
              <Select value={scenario} label="Scenario" onChange={e => setScenario(e.target.value)}>
                <MenuItem value="baseline">Baseline</MenuItem>
                <MenuItem value="optimistic">Optimistic</MenuItem>
                <MenuItem value="pessimistic">Pessimistic</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Tabs */}
      <Paper elevation={1} sx={{ p: 2 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} variant="scrollable" scrollButtons="auto">
          <Tab label="Spatial Map" />
          <Tab label="Tabular Data" />
          <Tab label="Charts & Trends" />
        </Tabs>
        <Box sx={{ mt: 3 }}>
          {tab === 0 && (
            <Box sx={{ height: 400, width: '100%' }}>
              <MapContainer center={[51.51, -0.12]} zoom={12} style={{ height: '100%', width: '100%' }}>
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                <GeoJSON data={mockGeoJson} style={feature => ({
                  color: '#1976d2',
                  weight: 2,
                  fillOpacity: 0.3,
                  fillColor: feature?.properties?.forecast > 1000000 ? '#43a047' : '#fbc02d',
                })} />
              </MapContainer>
            </Box>
          )}
          {tab === 1 && (
            <Box sx={{ height: 400, width: '100%' }}>
              <DataGrid
                rows={mockForecastData}
                columns={columns}
                pageSize={5}
                rowsPerPageOptions={[5, 10]}
                disableSelectionOnClick
                autoHeight
              />
            </Box>
          )}
          {tab === 2 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={7}>
                <Typography variant="h6" gutterBottom>Forecast Trend (Line Chart)</Typography>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={mockTimeSeries}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="value" stroke="#1976d2" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              </Grid>
              <Grid item xs={12} md={5}>
                <Typography variant="h6" gutterBottom>Forecast by Area (Bar Chart)</Typography>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={mockForecastData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="area" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="forecast" fill="#43a047" />
                  </BarChart>
                </ResponsiveContainer>
                <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>Growth Rate (Pie Chart)</Typography>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={mockForecastData}
                      dataKey="growth"
                      nameKey="area"
                      cx="50%"
                      cy="50%"
                      outerRadius={60}
                      fill="#8884d8"
                      label
                    >
                      {mockForecastData.map((entry, idx) => (
                        <Cell key={`cell-${idx}`} fill={chartColors[idx % chartColors.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Grid>
            </Grid>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default NNDRForecasting; 