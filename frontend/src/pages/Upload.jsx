import React, { useState, useEffect } from 'react';
import { 
  Upload as UploadIcon, 
  FileText, 
  Database, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  X,
  Download,
  RefreshCw,
  Play,
  Pause,
  Square,
  Settings,
  Info,
  Trash2,
  Eye,
  BarChart3
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = 'http://localhost:8000/api';

export default function Upload() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [ingestions, setIngestions] = useState([]);
  const [activeIngestions, setActiveIngestions] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState('');
  const [uploadProgress, setUploadProgress] = useState({});
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    fetchIngestions();
    const interval = setInterval(fetchIngestions, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchIngestions = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/ingestions`);
      setIngestions(response.data.ingestions || []);
      setActiveIngestions(response.data.ingestions?.filter(i => i.status === 'running') || []);
    } catch (err) {
      console.error('Error fetching ingestions:', err);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (fileList) => {
    const newFiles = Array.from(fileList).map(file => ({
      id: Date.now() + Math.random(),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'pending',
      progress: 0,
      error: null
    }));
    setFiles(prev => [...prev, ...newFiles]);
  };

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const startIngestion = async (fileId) => {
    const file = files.find(f => f.id === fileId);
    if (!file || !selectedDataset) {
      toast.error('Please select a dataset type');
      return;
    }

    try {
      setUploading(true);
      setUploadProgress(prev => ({ ...prev, [fileId]: 0 }));

      const formData = new FormData();
      formData.append('file', file.file);
      formData.append('dataset_type', selectedDataset);

      const response = await axios.post(`${API_BASE_URL}/ingestions/start`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(prev => ({ ...prev, [fileId]: progress }));
        }
      });

      toast.success(`Ingestion started for ${file.name}`);
      setFiles(prev => prev.map(f => 
        f.id === fileId ? { ...f, status: 'uploading', ingestion_id: response.data.ingestion_id } : f
      ));
      
      fetchIngestions();
    } catch (err) {
      console.error('Error starting ingestion:', err);
      toast.error('Failed to start ingestion');
      setFiles(prev => prev.map(f => 
        f.id === fileId ? { ...f, status: 'error', error: err.message } : f
      ));
    } finally {
      setUploading(false);
    }
  };

  const stopIngestion = async (ingestionId) => {
    try {
      await axios.post(`${API_BASE_URL}/ingestions/${ingestionId}/stop`);
      toast.success('Ingestion stopped');
      fetchIngestions();
    } catch (err) {
      console.error('Error stopping ingestion:', err);
      toast.error('Failed to stop ingestion');
    }
  };

  const deleteIngestion = async (ingestionId) => {
    try {
      await axios.delete(`${API_BASE_URL}/ingestions/${ingestionId}`);
      toast.success('Ingestion deleted');
      fetchIngestions();
    } catch (err) {
      console.error('Error deleting ingestion:', err);
      toast.error('Failed to delete ingestion');
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'running':
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-gray-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50';
      case 'running':
        return 'text-blue-600 bg-blue-50';
      case 'failed':
        return 'text-red-600 bg-red-50';
      case 'pending':
        return 'text-gray-600 bg-gray-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours}h ${minutes}m ${secs}s`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Data Upload</h1>
          <p className="mt-1 text-sm text-gray-500">
            Upload and ingest geospatial datasets
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={fetchIngestions}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
          <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <div className="space-y-6">
          {/* File Upload */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Upload Files</h2>
            
            {/* Dataset Type Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Dataset Type
              </label>
              <select
                value={selectedDataset}
                onChange={(e) => setSelectedDataset(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select dataset type</option>
                <option value="os_open_uprn">OS Open UPRN</option>
                <option value="onspd">ONSPD</option>
                <option value="os_open_names">OS Open Names</option>
                <option value="os_open_map_local">OS Open Map Local</option>
                <option value="code_point_open">Code Point Open</option>
              </select>
            </div>

            {/* Drag & Drop Area */}
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive 
                  ? 'border-blue-400 bg-blue-50' 
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <UploadIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <div className="text-sm text-gray-600 mb-4">
                <label className="cursor-pointer">
                  <span className="font-medium text-blue-600 hover:text-blue-500">
                    Click to upload
                  </span>
                  <span className="text-gray-500"> or drag and drop</span>
                  <input
                    type="file"
                    multiple
                    onChange={handleFileSelect}
                    className="hidden"
                    accept=".csv,.txt,.gml,.xml,.zip"
                  />
                </label>
              </div>
              <p className="text-xs text-gray-500">
                CSV, TXT, GML, XML, ZIP files up to 10GB
              </p>
            </div>
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Queue</h3>
              <div className="space-y-3">
                {files.map((file) => (
                  <div key={file.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3 flex-1">
                      <FileText className="w-5 h-5 text-gray-400" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatFileSize(file.size)}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {file.status === 'pending' && (
                        <button
                          onClick={() => startIngestion(file.id)}
                          disabled={uploading || !selectedDataset}
                          className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                        >
                          Start
                        </button>
                      )}
                      {file.status === 'uploading' && (
                        <div className="text-xs text-blue-600">
                          {uploadProgress[file.id] || 0}%
                        </div>
                      )}
                      <button
                        onClick={() => removeFile(file.id)}
                        className="p-1 text-gray-400 hover:text-red-600"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Active Ingestions */}
        <div className="space-y-6">
          {/* Active Ingestions */}
          {activeIngestions.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Active Ingestions</h3>
              <div className="space-y-3">
                {activeIngestions.map((ingestion) => (
                  <div key={ingestion.id} className="p-3 bg-blue-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <Clock className="w-4 h-4 text-blue-600 animate-spin" />
                        <span className="text-sm font-medium text-gray-900">
                          {ingestion.dataset_type}
                        </span>
                      </div>
                                             <button
                         onClick={() => stopIngestion(ingestion.id)}
                         className="p-1 text-gray-400 hover:text-red-600"
                       >
                         <Square className="w-4 h-4" />
                       </button>
                    </div>
                    <div className="text-xs text-gray-600">
                      Started: {new Date(ingestion.started_at).toLocaleString()}
                    </div>
                    {ingestion.progress && (
                      <div className="mt-2">
                        <div className="flex justify-between text-xs text-gray-600 mb-1">
                          <span>Progress</span>
                          <span>{ingestion.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${ingestion.progress}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Ingestions */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Ingestions</h3>
            <div className="space-y-3">
              {ingestions.slice(0, 5).map((ingestion) => (
                <div key={ingestion.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(ingestion.status)}
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {ingestion.dataset_type}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(ingestion.started_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(ingestion.status)}`}>
                      {ingestion.status}
                    </span>
                    <div className="flex space-x-1">
                      <button
                        className="p-1 text-gray-400 hover:text-blue-600"
                        title="View details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => deleteIngestion(ingestion.id)}
                        className="p-1 text-gray-400 hover:text-red-600"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Database className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-900">
                {ingestions.length}
              </p>
              <p className="text-sm text-gray-500">Total Ingestions</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-900">
                {ingestions.filter(i => i.status === 'completed').length}
              </p>
              <p className="text-sm text-gray-500">Completed</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Clock className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-900">
                {activeIngestions.length}
              </p>
              <p className="text-sm text-gray-500">Running</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <AlertCircle className="h-8 w-8 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-900">
                {ingestions.filter(i => i.status === 'failed').length}
              </p>
              <p className="text-sm text-gray-500">Failed</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 