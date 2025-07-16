import React from 'react';
import { FileText } from 'lucide-react';

export default function DataRequirements() {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-8">
      <div className="flex items-center mb-6">
        <FileText className="w-8 h-8 text-blue-600 mr-3" />
        <h1 className="text-3xl font-bold text-gray-900">Data Requirements & Guidelines</h1>
      </div>
      <div className="bg-white shadow rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-2">Required Datasets</h2>
        <ul className="list-disc pl-6 text-gray-700 space-y-1">
          <li><strong>NNDR Property List</strong> (CSV/Excel): Export from Civica/Idox or your business rates system.</li>
          <li><strong>UPRN Master List</strong> (CSV): Obtain from GeoPlace or Ordnance Survey AddressBase.</li>
          <li><strong>Historic Billing Data</strong> (CSV/Excel, optional): Export from your finance system for forecasting accuracy.</li>
          <li><strong>Council Tax Property List</strong> (optional): For cross-checking with NNDR and UPRN lists.</li>
        </ul>
        <div className="text-xs text-gray-500 mt-2">* Required for core functionality. All uploads are in-memory for demo purposes.</div>
      </div>
      <div className="bg-blue-50 border-l-4 border-blue-400 rounded p-6">
        <h2 className="text-lg font-semibold text-blue-900 mb-2">How to get started</h2>
        <ul className="list-disc pl-6 text-blue-900 text-sm space-y-1">
          <li>Gather the required datasets as listed above from your council systems or data providers.</li>
          <li>Use the Upload/Select features in the app to load each dataset (demo: in-memory only).</li>
          <li>Once all required data is loaded, the system will enable full forecasting and property identification features.</li>
          <li>Contact your IT/data team or the data provider if you need help sourcing any dataset.</li>
        </ul>
        <div className="mt-2 text-xs text-blue-800">This is a demonstration. In a production system, data would be securely stored and processed on council infrastructure.</div>
      </div>
    </div>
  );
} 