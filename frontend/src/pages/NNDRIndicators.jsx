import React, { useState } from 'react';
import { Tabs, Tab, Box, Typography, Paper, Grid, Select, MenuItem, FormControl, InputLabel, Card, CardContent, Button } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import {
  summaryCards,
  sectorBreakdown,
  topRatepayers,
  reliefDistribution,
  mapPoints,
  nndrTrends,
} from './dashboardMockData';

// Mock indicator data
const indicatorSummary = [
  { label: 'Total Rateable Value', value: '£2,350,000,000', change: '+2.5%' },
  { label: 'Properties', value: '1,250,000', change: '+0.8%' },
  { label: 'Vacancy Rate', value: '7.2%', change: '-0.3%' },
  { label: 'Business Openings', value: '12,500', change: '+4.1%' },
  { label: 'Business Closures', value: '9,800', change: '-1.2%' },
  { label: 'Economic Growth', value: '1.8%', change: '+0.2%' },
];
const indicatorTable = [
  { id: 1, name: 'Total Rateable Value', type: 'Financial', value: 2350000000, unit: '£', source: 'VOA', last_update: '2024-06-01' },
  { id: 2, name: 'Properties', type: 'Count', value: 1250000, unit: '', source: 'VOA', last_update: '2024-06-01' },
  { id: 3, name: 'Vacancy Rate', type: 'Percentage', value: 0.072, unit: '%', source: 'ONS', last_update: '2024-06-01' },
  { id: 4, name: 'Business Openings', type: 'Count', value: 12500, unit: '', source: 'ONS', last_update: '2024-06-01' },
  { id: 5, name: 'Business Closures', type: 'Count', value: 9800, unit: '', source: 'ONS', last_update: '2024-06-01' },
  { id: 6, name: 'Economic Growth', type: 'Percentage', value: 0.018, unit: '%', source: 'ONS', last_update: '2024-06-01' },
  { id: 7, name: 'Retail Properties', type: 'Count', value: 320000, unit: '', source: 'VOA', last_update: '2024-06-01' },
  { id: 8, name: 'Office Properties', type: 'Count', value: 210000, unit: '', source: 'VOA', last_update: '2024-06-01' },
  { id: 9, name: 'Industrial Properties', type: 'Count', value: 180000, unit: '', source: 'VOA', last_update: '2024-06-01' },
];
const indicatorTrends = [
  { year: 2020, rateable_value: 2100000000, vacancy: 0.08, growth: 0.012 },
  { year: 2021, rateable_value: 2150000000, vacancy: 0.077, growth: 0.013 },
  { year: 2022, rateable_value: 2250000000, vacancy: 0.075, growth: 0.015 },
  { year: 2023, rateable_value: 2300000000, vacancy: 0.073, growth: 0.017 },
  { year: 2024, rateable_value: 2350000000, vacancy: 0.072, growth: 0.018 },
];
const mockMapPoints = [
  { id: 1, name: 'LAD 1', lat: 51.51, lng: -0.12, value: 0.08 },
  { id: 2, name: 'LAD 2', lat: 51.52, lng: -0.13, value: 0.06 },
  { id: 3, name: 'LAD 3', lat: 51.5, lng: -0.15, value: 0.09 },
];
const chartColors = ['#1976d2', '#43a047', '#fbc02d', '#e53935'];

const factorDetails = {
  'Total Rateable Value': {
    description: 'The total value of all non-domestic properties assessed for business rates.',
    source: 'VOA',
    trend: indicatorTrends.map(d => ({ year: d.year, value: d.rateable_value })),
    unit: '£',
  },
  'Vacancy Rate': {
    description: 'Percentage of non-domestic properties currently vacant.',
    source: 'ONS',
    trend: indicatorTrends.map(d => ({ year: d.year, value: d.vacancy })),
    unit: '%',
  },
  'Economic Growth': {
    description: 'Annual economic growth rate for the region.',
    source: 'ONS',
    trend: indicatorTrends.map(d => ({ year: d.year, value: d.growth })),
    unit: '%',
  },
};

const NNDRIndicators = () => {
  const [tab, setTab] = useState(0);
  const [selectedFactor, setSelectedFactor] = useState(null);
  const [year, setYear] = useState(2024);
  const [type, setType] = useState('All');

  // Table columns
  const columns = [
    { field: 'name', headerName: 'Indicator', flex: 1 },
    { field: 'type', headerName: 'Type', flex: 1 },
    {
      field: 'value',
      headerName: 'Value',
      flex: 1,
      valueFormatter: (params) => {
        const row = params?.row || {};
        const value = params?.value;
        if (row.unit === '%') return `${(value * 100).toFixed(1)}%`;
        if (row.unit === '£') return `£${(value / 1e6).toFixed(1)}m`;
        return value;
      }
    },
    { field: 'unit', headerName: 'Unit', flex: 0.5 },
    { field: 'source', headerName: 'Source', flex: 1 },
    { field: 'last_update', headerName: 'Last Update', flex: 1 },
  ];

  return (
    <Box sx={{ p: { xs: 1, md: 3 } }}>
      {/* Header */}
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>NNDR Forecasting Indicators & Data Factors</Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Explore the key indicators and data factors that drive NNDR forecasting. Use the dashboard, table, charts, and map to understand trends and spatial patterns.
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
              <InputLabel>Type</InputLabel>
              <Select value={type} label="Type" onChange={e => setType(e.target.value)}>
                <MenuItem value="All">All</MenuItem>
                <MenuItem value="Financial">Financial</MenuItem>
                <MenuItem value="Count">Count</MenuItem>
                <MenuItem value="Percentage">Percentage</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Tabs */}
      <Paper elevation={1} sx={{ p: 2 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} variant="scrollable" scrollButtons="auto">
          <Tab label="Overview" />
          <Tab label="Tabular Data" />
          <Tab label="Charts" />
          <Tab label="Map" />
          <Tab label="Factor Details" />
        </Tabs>
        <Box sx={{ mt: 3 }}>
          {tab === 0 && (
            <Grid container spacing={2}>
              {summaryCards.map((card, idx) => (
                <Grid item xs={12} sm={6} md={4} key={idx}>
                  <Card sx={{ borderLeft: `6px solid ${chartColors[idx % chartColors.length]}` }}>
                    <CardContent>
                      <Typography variant="subtitle2" color="text.secondary">{card.label}</Typography>
                      <Typography variant="h5" fontWeight={700}>{card.value}</Typography>
                      {typeof card.change === 'string' ? (
                        <Typography variant="body2" color={card.change.startsWith('+') ? 'success.main' : 'error.main'}>{card.change}</Typography>
                      ) : null}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
          {tab === 1 && (
            <Box sx={{ height: 400, width: '100%' }}>
              <DataGrid
                rows={indicatorTable.filter(row => type === 'All' ? true : row.type === type)}
                columns={columns}
                pageSize={7}
                rowsPerPageOptions={[7, 14]}
                disableSelectionOnClick
                autoHeight
                onRowClick={({ row }) => { setSelectedFactor(row.name); setTab(4); }}
              />
            </Box>
          )}
          {tab === 2 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>Rateable Value Trend</Typography>
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={nndrTrends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="rateable_value" stroke="#1976d2" strokeWidth={3} name="Rateable Value" />
                  </LineChart>
                </ResponsiveContainer>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>Vacancy Rate Trend</Typography>
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={nndrTrends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="vacancy" stroke="#e53935" strokeWidth={3} name="Vacancy Rate" />
                  </LineChart>
                </ResponsiveContainer>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>Economic Growth Trend</Typography>
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={nndrTrends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="growth" stroke="#43a047" strokeWidth={3} name="Growth" />
                  </LineChart>
                </ResponsiveContainer>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>Indicator Mix (Pie)</Typography>
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={indicatorTable}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={70}
                      fill="#8884d8"
                      label
                    >
                      {indicatorTable.map((entry, idx) => (
                        <Cell key={`cell-${idx}`} fill={chartColors[idx % chartColors.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Grid>
            </Grid>
          )}
          {tab === 3 && (
            <Box sx={{ height: 400, width: '100%' }}>
              <MapContainer center={[51.51, -0.12]} zoom={11} style={{ height: '100%', width: '100%' }}>
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                {mapPoints.map(point => (
                  <CircleMarker
                    key={point.id}
                    center={[point.lat, point.lng]}
                    radius={20 * point.value}
                    color={point.value > 0.08 ? '#e53935' : '#43a047'}
                    fillOpacity={0.5}
                  >
                    <Popup>
                      <Typography variant="subtitle2">{point.name}</Typography>
                      <Typography variant="body2">Vacancy Rate: {(point.value * 100).toFixed(1)}%</Typography>
                    </Popup>
                  </CircleMarker>
                ))}
              </MapContainer>
            </Box>
          )}
          {tab === 4 && selectedFactor && (
            <Box>
              <Typography variant="h5" fontWeight={700} gutterBottom>{selectedFactor}</Typography>
              <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                {factorDetails[selectedFactor]?.description || 'No description available.'}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <strong>Source:</strong> {factorDetails[selectedFactor]?.source || 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <strong>Unit:</strong> {factorDetails[selectedFactor]?.unit || 'N/A'}
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6" gutterBottom>Historical Trend</Typography>
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={factorDetails[selectedFactor]?.trend || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="value" stroke="#1976d2" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
              <Button sx={{ mt: 2 }} variant="outlined" onClick={() => setTab(1)}>Back to Table</Button>
            </Box>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default NNDRIndicators; 