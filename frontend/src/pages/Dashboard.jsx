import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  MapPin, 
  BarChart3, 
  TrendingUp, 
  Database, 
  Globe,
  Users,
  FileText,
  Activity,
  AlertCircle,
  Upload
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, Legend } from 'recharts';
import api from '../api/axios';
import toast from 'react-hot-toast';
import {
  summaryCards,
  sectorBreakdown,
  topRatepayers,
  reliefDistribution,
  mapPoints,
  nndrTrends,
} from './dashboardMockData';
import { Slider, Input, Select, MenuItem } from '@mui/material';

// Add mockTimeSeries for forecast trend (now includes 2025–2027)
const mockTimeSeries = [
  { year: 2020, value: 900000 },
  { year: 2021, value: 950000 },
  { year: 2022, value: 1000000 },
  { year: 2023, value: 1100000 },
  { year: 2024, value: 1200000 },
  { year: 2025, value: 1300000 }, // forecast
  { year: 2026, value: 1350000 }, // forecast
  { year: 2027, value: 1400000 }, // forecast
];

// Add mock data for forecast by sector (2025)
const initialForecastBySector = [
  { sector: 'Retail', forecast: 320000 },
  { sector: 'Office', forecast: 280000 },
  { sector: 'Industrial', forecast: 350000 },
  { sector: 'Hospitality', forecast: 120000 },
  { sector: 'Other', forecast: 90000 },
];

const sectorIcons = {
  Retail: BarChart3,
  Office: Building2,
  Industrial: Database,
  Hospitality: Users,
  Other: Globe,
};

const API_BASE_URL = 'http://localhost:8000/api';

export default function Dashboard() {
  // Use 2025 values for the top row cards
  const [stats, setStats] = useState({
    total_properties: 1300000, // 2025 value
    total_postcodes: 1750000,  // mock 2025 value
    total_places: 52000,       // mock 2025 value
    total_lads: 20,            // mock 2025 value
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Forecast tuning state
  const [growthRate, setGrowthRate] = useState(4); // %
  const [sectorAdjustments, setSectorAdjustments] = useState({
    Retail: 0,
    Office: 0,
    Industrial: 0,
    Hospitality: 0,
    Other: 0,
  });

  // Calculate forecast by sector based on tuning
  const forecastBySector = initialForecastBySector.map(row => ({
    ...row,
    forecast: Math.round(row.forecast * (1 + growthRate / 100) * (1 + (sectorAdjustments[row.sector] || 0) / 100)),
  }));

  // Calculate total properties for top card
  const totalProperties = forecastBySector.reduce((sum, row) => sum + row.forecast, 0);

  // Top cards with icons, color, and trend
  const statCards = [
    {
      name: 'Total Properties',
      value: totalProperties.toLocaleString(),
      icon: Building2,
      color: 'bg-blue-500',
      change: `+${growthRate}%`,
      changeType: growthRate >= 0 ? 'positive' : 'negative',
    },
    {
      name: 'Total Postcodes',
      value: stats?.total_postcodes?.toLocaleString() || '0',
      icon: MapPin,
      color: 'bg-green-500',
      change: '+2%',
      changeType: 'positive',
    },
    {
      name: 'Total Places',
      value: stats?.total_places?.toLocaleString() || '0',
      icon: Globe,
      color: 'bg-purple-500',
      change: '+1%',
      changeType: 'positive',
    },
    {
      name: 'LAD Boundaries',
      value: stats?.total_lads?.toLocaleString() || '0',
      icon: MapPin,
      color: 'bg-orange-500',
      change: '+0%',
      changeType: 'neutral',
    },
  ];

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsResponse, coverageResponse] = await Promise.all([
        api.get(`${API_BASE_URL}/geospatial/statistics`),
        api.get(`${API_BASE_URL}/analytics/coverage`)
      ]);

      setStats({
        ...statsResponse.data,
        coverage: coverageResponse.data
      });
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data');
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-red-500" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading dashboard</h3>
          <p className="mt-1 text-sm text-gray-500">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your NNDR Insight geospatial data and analytics
        </p>
      </div>

      {/* Stats Cards - Quality UI */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <div key={stat.name} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5 flex items-center">
              <div className={`flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-md ${stat.color}`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">{stat.name}</dt>
                  <dd className="text-lg font-bold text-gray-900">{stat.value}</dd>
                </dl>
              </div>
            </div>
            <div className="bg-gray-50 px-5 py-3">
              <div className="text-sm flex items-center">
                <span className={`font-medium ${
                  stat.changeType === 'positive' ? 'text-green-600' : stat.changeType === 'negative' ? 'text-red-600' : 'text-gray-500'
                }`}>
                  {stat.change}
                  {stat.changeType === 'positive' && <span className="ml-1">▲</span>}
                  {stat.changeType === 'negative' && <span className="ml-1">▼</span>}
                </span>
                <span className="text-gray-500 ml-1">from last year</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Forecast Tuning Controls */}
      <div className="bg-white shadow rounded-lg p-6 mb-2">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Forecast Tuning</h3>
        <div className="flex flex-col lg:flex-row gap-6 items-center">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">Overall Growth Rate (%)</label>
            <Slider
              value={growthRate}
              min={-5}
              max={10}
              step={0.1}
              onChange={(_, v) => setGrowthRate(v)}
              valueLabelDisplay="auto"
              sx={{ maxWidth: 300 }}
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">Sector Adjustments (%)</label>
            <div className="grid grid-cols-2 gap-2">
              {Object.keys(sectorAdjustments).map(sector => (
                <div key={sector} className="flex items-center gap-2">
                  <span className="w-20 text-gray-700">{sector}</span>
                  <Slider
                    value={sectorAdjustments[sector]}
                    min={-10}
                    max={10}
                    step={0.1}
                    onChange={(_, v) => setSectorAdjustments(a => ({ ...a, [sector]: v }))}
                    valueLabelDisplay="auto"
                    sx={{ maxWidth: 120 }}
                  />
                  <Input
                    value={sectorAdjustments[sector]}
                    onChange={e => setSectorAdjustments(a => ({ ...a, [sector]: Number(e.target.value) }))}
                    type="number"
                    className="w-12 border rounded px-1 py-0.5 text-sm"
                    inputProps={{ min: -10, max: 10, step: 0.1 }}
                  />
                  <span className="text-gray-500 text-xs">%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* NNDR Forecast Trend Chart */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">NNDR Forecast Trend</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mockTimeSeries.map((d, i) => ({ ...d, value: d.value * (1 + growthRate / 100) }))}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#1976d2" strokeWidth={3} name="Forecast" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Grid - By Sector */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sector Breakdown Pie Chart */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Properties by Sector</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sectorBreakdown}
                  dataKey="properties"
                  nameKey="sector"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ sector, percent }) => `${sector} ${(percent * 100).toFixed(0)}%`}
                  fill="#8884d8"
                >
                  {sectorBreakdown.map((entry, idx) => (
                    <Cell key={`cell-${idx}`} fill={["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EF4444"][idx % 5]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        {/* Forecast by Sector Bar Chart */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Forecast by Sector (2025)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={forecastBySector}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="sector" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="forecast" fill="#43a047" name="Forecast" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Comprehensive Data Tables Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sector Breakdown Table */}
        <div className="bg-white shadow rounded-lg p-6 overflow-x-auto">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Sector Breakdown</h3>
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2 pr-4">Sector</th>
                <th className="py-2 pr-4">Properties</th>
                <th className="py-2 pr-4">Median RV</th>
                <th className="py-2 pr-4">Total RV</th>
                <th className="py-2 pr-4">% with Relief</th>
                <th className="py-2 pr-4">Notes</th>
              </tr>
            </thead>
            <tbody>
              {sectorBreakdown.map((row, idx) => (
                <tr key={row.sector} className="border-b last:border-0">
                  <td className="py-2 pr-4 font-semibold">{row.sector}</td>
                  <td className="py-2 pr-4">{row.properties.toLocaleString()}</td>
                  <td className="py-2 pr-4">£{row.medianRV.toLocaleString()}</td>
                  <td className="py-2 pr-4">£{row.totalRV.toLocaleString()}</td>
                  <td className="py-2 pr-4 flex items-center gap-1">
                    {row.percentWithRelief}%
                    {/* +/- indicator: green up for >40, red down for <40 */}
                    {row.percentWithRelief >= 40 ? (
                      <span className="text-green-600 ml-1">+<svg className="inline h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" /></svg></span>
                    ) : (
                      <span className="text-red-600 ml-1">-<svg className="inline h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19 14l-7 7m0 0l-7-7m7 7V3" /></svg></span>
                    )}
                  </td>
                  <td className="py-2 pr-4">{row.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {/* Top Ratepayers Table */}
        <div className="bg-white shadow rounded-lg p-6 overflow-x-auto">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Ratepayers</h3>
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2 pr-4">Name</th>
                <th className="py-2 pr-4">Sector</th>
                <th className="py-2 pr-4">Rateable Value</th>
                <th className="py-2 pr-4">Address</th>
                <th className="py-2 pr-4">Reliefs</th>
              </tr>
            </thead>
            <tbody>
              {topRatepayers.slice(0, 8).map((row, idx) => (
                <tr key={row.name} className="border-b last:border-0">
                  <td className="py-2 pr-4 font-semibold">{row.name}</td>
                  <td className="py-2 pr-4">{row.sector}</td>
                  <td className="py-2 pr-4">£{row.rv.toLocaleString()}</td>
                  <td className="py-2 pr-4">{row.address}</td>
                  <td className="py-2 pr-4">{row.reliefs}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Activity & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-2 bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <Database className="w-4 h-4 text-green-600" />
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">Data ingestion completed</p>
                <p className="text-sm text-gray-500">All geospatial datasets loaded successfully</p>
              </div>
              <div className="text-sm text-gray-500">2 hours ago</div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <Activity className="w-4 h-4 text-blue-600" />
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">API health check</p>
                <p className="text-sm text-gray-500">All services running normally</p>
              </div>
              <div className="text-sm text-gray-500">1 hour ago</div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                  <BarChart3 className="w-4 h-4 text-purple-600" />
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">Analytics updated</p>
                <p className="text-sm text-gray-500">Regional coverage analysis completed</p>
              </div>
              <div className="text-sm text-gray-500">30 minutes ago</div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors">
              <Globe className="w-4 h-4 mr-3" />
              Geocode Address
            </button>
            <button className="w-full flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors">
              <MapPin className="w-4 h-4 mr-3" />
              Search Properties
            </button>
            <button className="w-full flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors">
              <BarChart3 className="w-4 h-4 mr-3" />
              View Analytics
            </button>
            <button className="w-full flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors">
              <Upload className="w-4 h-4 mr-3" />
              Upload Data
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 