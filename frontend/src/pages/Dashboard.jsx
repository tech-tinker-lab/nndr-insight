import React, { useState } from 'react';
import { Upload, CheckCircle, AlertCircle, TrendingUp, Search, BarChart2, FileText } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

// --- In-memory demo data ---
const demoForecastData = [
  { month: 'Jan', income: 4200000 },
  { month: 'Feb', income: 4250000 },
  { month: 'Mar', income: 4300000 },
  { month: 'Apr', income: 4400000 },
  { month: 'May', income: 4450000 },
  { month: 'Jun', income: 4500000 },
  { month: 'Jul', income: 4550000 },
  { month: 'Aug', income: 4600000 },
  { month: 'Sep', income: 4650000 },
  { month: 'Oct', income: 4700000 },
  { month: 'Nov', income: 4750000 },
  { month: 'Dec', income: 4800000 },
];
const demoNonRated = [
  { uprn: '100010001', address: '1 High St, Cambourne', type: 'Retail', reason: 'Not in NNDR list' },
  { uprn: '100010002', address: '2 Market Rd, Sawston', type: 'Industrial', reason: 'Not in NNDR list' },
  { uprn: '100010003', address: '3 Main St, Bar Hill', type: 'Office', reason: 'Not in NNDR list' },
];
const demoDatasets = [
  {
    key: 'nndr',
    name: 'NNDR Property List',
    required: true,
    status: false,
    note: 'Export from Civica/Idox or your business rates system as CSV or Excel.'
  },
  {
    key: 'uprn',
    name: 'UPRN Master List',
    required: true,
    status: false,
    note: 'Obtain from GeoPlace or Ordnance Survey AddressBase. CSV recommended.'
  },
  {
    key: 'billing',
    name: 'Historic Billing Data',
    required: false,
    status: false,
    note: 'Export from your finance system for forecasting accuracy.'
  },
  {
    key: 'councilTax',
    name: 'Council Tax Property List',
    required: false,
    status: false,
    note: 'Optional: For cross-checking with NNDR and UPRN lists.'
  },
];

export default function Dashboard() {
  const [datasets, setDatasets] = useState(demoDatasets);

  // Simulate upload/select
  const handleUpload = (key) => {
    setDatasets(ds => ds.map(d => d.key === key ? { ...d, status: true } : d));
  };

  // Data status summary
  const allRequiredLoaded = datasets.filter(d => d.required).every(d => d.status);

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 space-y-8">
      {/* Welcome Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">South Cambridgeshire NNDR Intelligence Portal</h1>
        <p className="text-lg text-gray-600 max-w-2xl">
          Welcome! This platform provides accurate business rate income forecasting and helps identify currently non-rated properties for National Non Domestic Rates (NNDR). Please ensure all required datasets are loaded for full functionality. All data is processed securely and never leaves your council environment.
        </p>
      </div>

      {/* Data Status Indicator */}
      <div className="flex items-center space-x-4 mb-4">
        {allRequiredLoaded ? (
          <span className="flex items-center text-green-700 font-semibold"><CheckCircle className="w-5 h-5 mr-1 text-green-600" /> All required datasets loaded</span>
        ) : (
          <span className="flex items-center text-yellow-700 font-semibold"><AlertCircle className="w-5 h-5 mr-1 text-yellow-600" /> Awaiting required datasets</span>
        )}
      </div>

      {/* Data Requirements Panel */}
      <Card variant="outlined" className="mb-8">
        <CardHeader title="Data Requirements" />
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {datasets.map(ds => (
              <div key={ds.key} className="flex items-start space-x-3 p-3 rounded border border-gray-100 bg-gray-50">
                <FileText className="w-6 h-6 text-blue-500 mt-1" />
                <div className="flex-1">
                  <div className="font-semibold text-gray-900">{ds.name} {ds.required && <span className="text-red-500">*</span>}</div>
                  <div className="text-sm text-gray-600 mb-1">{ds.note}</div>
                  <div className="flex items-center space-x-2">
                    {ds.status ? (
                      <span className="flex items-center text-green-600"><CheckCircle className="w-4 h-4 mr-1" />Loaded</span>
                    ) : (
                      <button onClick={() => handleUpload(ds.key)} className="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 text-xs font-medium"><Upload className="w-4 h-4 mr-1" />Upload/Select</button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="text-xs text-gray-500 mt-2">* Required for core functionality. All uploads are in-memory for demo purposes.</div>
        </CardContent>
      </Card>

      {/* Main Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Business Rate Income Forecasting */}
        <Card variant="outlined">
          <CardHeader title={<span className="flex items-center"><TrendingUp className="w-5 h-5 mr-2 text-blue-600" />Business Rate Income Forecasting</span>} />
          <CardContent>
            <div className="mb-2 text-gray-700 text-sm">
              Upload your NNDR property list and historic billing data to generate accurate forecasts. The system uses advanced models to predict income trends and highlight risks.
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={demoForecastData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="income" stroke="#2563eb" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 text-xs text-gray-500">
              <strong>Required data:</strong> NNDR Property List (CSV/Excel), Historic Billing Data (CSV/Excel, optional for improved accuracy).<br />
              <strong>Source:</strong> Civica/Idox, council finance system.
            </div>
          </CardContent>
        </Card>

        {/* Non-Rated Properties Identification */}
        <Card variant="outlined">
          <CardHeader title={<span className="flex items-center"><Search className="w-5 h-5 mr-2 text-green-600" />Identification of Non-Rated Properties</span>} />
          <CardContent>
            <div className="mb-2 text-gray-700 text-sm">
              Upload your UPRN master list and NNDR property list to identify properties not currently rated for NNDR. Cross-check with council tax and other datasets for maximum coverage.
            </div>
            <div className="overflow-x-auto rounded border border-gray-100 bg-gray-50 mt-2">
              <table className="min-w-full text-xs">
                <thead>
                  <tr className="bg-gray-100 text-gray-700">
                    <th className="px-2 py-1 text-left">UPRN</th>
                    <th className="px-2 py-1 text-left">Address</th>
                    <th className="px-2 py-1 text-left">Type</th>
                    <th className="px-2 py-1 text-left">Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {demoNonRated.map((row, idx) => (
                    <tr key={idx} className="border-b last:border-0">
                      <td className="px-2 py-1 font-mono">{row.uprn}</td>
                      <td className="px-2 py-1">{row.address}</td>
                      <td className="px-2 py-1">{row.type}</td>
                      <td className="px-2 py-1 text-red-600">{row.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-4 text-xs text-gray-500">
              <strong>Required data:</strong> UPRN Master List (CSV), NNDR Property List (CSV/Excel).<br />
              <strong>Source:</strong> GeoPlace, Ordnance Survey, Civica/Idox.
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Guidance/Next Steps */}
      <div className="mt-10 p-6 bg-blue-50 border-l-4 border-blue-400 rounded">
        <h2 className="text-lg font-semibold text-blue-900 mb-2">How to get started</h2>
        <ul className="list-disc pl-6 text-blue-900 text-sm space-y-1">
          <li>Gather the required datasets as listed above from your council systems or data providers.</li>
          <li>Use the Upload/Select buttons to load each dataset (demo: in-memory only).</li>
          <li>Once all required data is loaded, the system will enable full forecasting and property identification features.</li>
          <li>Contact your IT/data team or the data provider if you need help sourcing any dataset.</li>
        </ul>
        <div className="mt-2 text-xs text-blue-800">This is a demonstration. In a production system, data would be securely stored and processed on council infrastructure.</div>
      </div>
    </div>
  );
} 