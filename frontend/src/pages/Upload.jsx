
// ...existing code for all imports and helpers...

// Upload page recreated as a clean, modular React component
import React, { useState, useRef } from 'react';
import { Upload as UploadIcon, FileText, Clock, X, RefreshCw, Settings, MapPin } from 'lucide-react';
import api from '../api/axios';
import toast from 'react-hot-toast';
import { useUser } from '../context/UserContext.tsx';
import StagingConfigManager from '../components/StagingConfigManager';
import FileAnalyzer from '../components/upload/FileAnalyzer';
import FilePreview from '../components/upload/FilePreview.tsx';
import ColumnMappingOptions from '../components/upload/ColumnMappingOptions.tsx';
// ...existing code for all imports and helpers...
import { formatFileSize } from '../components/upload/uploadUtils';

const API_BASE_URL = 'http://localhost:8000/api';
const AI_ANALYZE_API_URL = 'http://localhost:8000/api/design-enhanced/ai/analyze-file';

const Upload = () => {
  const [dragActive, setDragActive] = useState(false);
  const [analysisResults, setAnalysisResults] = useState({});
  const [showConfigManager, setShowConfigManager] = useState(false);
  const [tableName, setTableName] = useState('');
  const [tableNameAvailable, setTableNameAvailable] = useState(true);
  const [showSQL, setShowSQL] = useState(false);
  const [generatedSQL, setGeneratedSQL] = useState('');
  // State for column mapping and active tab
  const [columnMapping, setColumnMapping] = useState({});
  const [activeSQLTab, setActiveSQLTab] = useState('mapping'); // 'mapping' or 'sql'
  const [showFieldAnalysis, setShowFieldAnalysis] = useState({});
  const fileInputRef = useRef();
  const user = useUser();

  // File drag handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect({ target: { files: e.dataTransfer.files } });
    }
  };

  // Client-side file analysis for CSV (and optionally other types)
  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    files.forEach(file => {
      // Only do client-side preview for CSV files
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        const reader = new FileReader();
        reader.onload = (event) => {
          const text = event.target.result;
          // Use FileAnalyzer to parse CSV headers and sample rows
          const preview = FileAnalyzer.analyzeCSV(text, file.name);
          setAnalysisResults(prev => ({
            ...prev,
            [file.name]: {
              status: 'client-preview',
              fileName: file.name,
              preview,
              file,
            }
          }));
        };
        reader.readAsText(file);
      } else {
        // For other files, just show as pending and send to server
        setAnalysisResults(prev => ({
          ...prev,
          [file.name]: {
            status: 'analyzing',
            fileName: file.name,
            progress: 0,
            file,
          }
        }));
        analyzeFile(file);
      }
    });
  };

  // Analyze file with AI (server-side)
  const analyzeFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    setAnalysisResults(prev => ({ ...prev, [file.name]: { ...prev[file.name], status: 'analyzing', fileName: file.name, progress: 0 } }));
    try {
      const response = await api.post(AI_ANALYZE_API_URL, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      setAnalysisResults(prev => ({ ...prev, [file.name]: { ...prev[file.name], status: 'completed', fileName: file.name, result: response.data } }));
    } catch (error) {
      setAnalysisResults(prev => ({ ...prev, [file.name]: { ...prev[file.name], status: 'failed', fileName: file.name, error: error.message } }));
      toast.error(`Analysis failed for ${file.name}`);
    }
  };

  // Remove file from queue
  const removeFile = (key) => {
    setAnalysisResults(prev => { const copy = { ...prev }; delete copy[key]; return copy; });
  };


  return (
    <div className="w-screen min-w-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="flex items-center justify-between p-6 bg-white shadow-md">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Data Upload</h1>
          <p className="mt-1 text-sm text-gray-500">Upload and ingest geospatial datasets</p>
        </div>
        <div className="flex items-center space-x-3">
          <button onClick={() => setShowConfigManager(v => !v)} className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
            <MapPin className="w-4 h-4 mr-2" />Config Manager
          </button>
          <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
            <Settings className="w-4 h-4 mr-2" />Settings
          </button>
        </div>
      </div>

      {/* Config Manager */}
      {showConfigManager && <StagingConfigManager />}

      <div className="flex flex-col items-center justify-start w-full">
        {/* File Upload */}
        <div className="w-full max-w-5xl flex flex-col items-center justify-start">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 w-full flex flex-col items-center justify-start">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Upload Files</h2>
            <div className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors w-full min-h-[10rem] flex flex-col items-center justify-center ${dragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}`}
              onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}>
              <UploadIcon className="mx-auto h-16 w-16 text-gray-400 mb-4" />
              <div className="text-sm text-gray-600 mb-4">
                <label className="cursor-pointer">
                  <span className="font-medium text-blue-600 hover:text-blue-500">Click to upload</span>
                  <span className="text-gray-500"> or drag and drop</span>
                  <input type="file" multiple onChange={handleFileSelect} className="hidden" accept=".csv,.txt,.gml,.xml,.zip,.gpkg,.shp,.dbf,.shx,.prj,.cpg,.qix,.sdmx,.kml,.geojson,.json,.yml,.yaml" ref={fileInputRef} />
                </label>
              </div>
              <p className="text-xs text-gray-500">CSV, TXT, GML, XML, ZIP, GeoPackage, Shapefile, SDMX, KML, GeoJSON, JSON, YAML files up to 10GB</p>
            </div>
          </div>

          {/* File List */}
          {Object.keys(analysisResults).length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 w-full mt-8 overflow-auto">
              <div className="space-y-4">
                {Object.entries(analysisResults).map(([uniqueKey, analysisResult]) => {
                  let previewAnalysis = analysisResult.result;
                  if (previewAnalysis && previewAnalysis.format === 'zip' && previewAnalysis.content_analysis) {
                    previewAnalysis = {
                      ...previewAnalysis,
                      zipContents: previewAnalysis.content_analysis,
                      directoryStructure: previewAnalysis.content_analysis.directory_structure,
                    };
                  }
                  // Show preview if client-side preview or server-side analysis is available
                  const hasClientPreview = analysisResult.status === 'client-preview' && analysisResult.preview && analysisResult.preview.headers && analysisResult.preview.headers.length > 0;
                  const hasServerPreview = analysisResult.status === 'completed' && previewAnalysis && previewAnalysis.headers && previewAnalysis.headers.length > 0;
                  return (
                    <div key={uniqueKey} className="border border-gray-200 rounded-lg overflow-hidden">
                      <div className="flex items-center justify-between p-3 bg-gray-50">
                        <div className="flex items-center space-x-3 flex-1">
                          {(hasClientPreview || hasServerPreview) ? FileAnalyzer.getFileIcon(previewAnalysis?.format || 'csv') : <FileText className="w-5 h-5 text-gray-400" />}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">{analysisResult.fileName}</p>
                            <p className="text-xs text-gray-500">{previewAnalysis?.filename || ''}{previewAnalysis?.format && ` • ${previewAnalysis.format.toUpperCase()}`}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {analysisResult.status !== 'completed' && analysisResult.status !== 'failed' && analysisResult.status !== 'client-preview' && (
                            <div className="flex items-center space-x-1">
                              <Clock className="w-4 h-4 text-blue-500 animate-spin" />
                              <span className="text-xs text-blue-600">Analyzing...</span>
                              <span className="text-xs text-gray-500">{analysisResult.progress}%</span>
                            </div>
                          )}
                          <button onClick={() => removeFile(uniqueKey)} className="p-1 text-gray-400 hover:text-red-600"><X className="w-4 h-4" /></button>
                        </div>
                      </div>
                      {/* File Analysis and Preview */}
                      {hasClientPreview ? (
                        <div className="p-3">
                          {/* CSV Data Table Preview always first for CSV files */}
                          {analysisResult.preview.format === 'csv' && analysisResult.preview.headers && analysisResult.preview.sampleRows && (
                            <div className="mb-4">
                              <div className="font-semibold text-gray-700 mb-2">CSV Data Preview</div>
                              <div className="overflow-x-auto">
                                <table className="min-w-full text-xs border border-gray-300 bg-white">
                                  <thead className="bg-gray-100">
                                    <tr>
                                      {analysisResult.preview.headers.map((header, idx) => (
                                        <th key={idx} className="border px-2 py-1 text-left">{header}</th>
                                      ))}
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {analysisResult.preview.sampleRows.map((row, rIdx) => (
                                      <tr key={rIdx} className="hover:bg-gray-50">
                                        {row.map((cell, cIdx) => (
                                          <td key={cIdx} className="border px-2 py-1">{cell}</td>
                                        ))}
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                              {/* Links below table */}
                              <div className="flex justify-between items-center mt-2">
                                <button
                                  className="text-xs text-blue-600 underline hover:text-blue-800"
                                  type="button"
                                  onClick={() => {
                                    setShowFieldAnalysis(prev => ({ ...prev, [uniqueKey]: !prev?.[uniqueKey] }));
                                  }}
                                >
                                  Analyze Fields
                                </button>
                                <button
                                  className="text-xs text-blue-600 underline hover:text-blue-800"
                                  type="button"
                                  onClick={() => setShowSQL(v => !v)}
                                >
                                  Show SQL / Mapping
                                </button>
                              </div>
                              {/* JSON structure toggle */}
                              {showFieldAnalysis?.[uniqueKey] && (
                                <div className="mt-2">
                                  <div className="font-semibold text-gray-700 mb-1">Field Structure (JSON)</div>
                                  <pre className="bg-gray-100 rounded p-2 text-xs overflow-x-auto">{JSON.stringify(analysisResult.preview.structure, null, 2)}</pre>
                                </div>
                              )}
                            </div>
                          )}
                          {/* The above handles JSON structure toggle inline with Analyze Fields link */}
                          <FilePreview
                            analysis={analysisResult.preview}
                            getAllConfigs={() => {}}
                            tableName={tableName}
                            setTableName={setTableName}
                            tableNameAvailable={tableNameAvailable}
                            setTableNameAvailable={setTableNameAvailable}
                            showSQL={showSQL}
                            setShowSQL={setShowSQL}
                            generatedSQL={generatedSQL}
                            setGeneratedSQL={setGeneratedSQL}
                          />
                          {/* Show SQL / Mapping Tabs */}
                          {showSQL && (
                            <div className="mt-4">
                              <div className="flex border-b border-gray-200 mb-2">
                                <button
                                  className={`px-4 py-2 text-sm font-medium focus:outline-none ${activeSQLTab === 'mapping' ? 'border-b-2 border-blue-600 text-blue-700' : 'text-gray-600'}`}
                                  onClick={() => setActiveSQLTab('mapping')}
                                >
                                  Column Mapping
                                </button>
                                <button
                                  className={`ml-2 px-4 py-2 text-sm font-medium focus:outline-none ${activeSQLTab === 'sql' ? 'border-b-2 border-blue-600 text-blue-700' : 'text-gray-600'}`}
                                  onClick={() => setActiveSQLTab('sql')}
                                >
                                  SQL
                                </button>
                              </div>
                              <div>
                                {activeSQLTab === 'mapping' && (
                                  <>
                                    {(() => {
                                      // Debug log for client preview
                                      console.log('Client preview structure:', analysisResult.preview);
                                      if (!analysisResult.preview || !Array.isArray(analysisResult.preview.headers) || analysisResult.preview.headers.length === 0) {
                                        return <div className="text-xs text-red-600">No columns detected in this file, mapping unavailable.</div>;
                                      }
                                      return (
                                        <ColumnMappingOptions
                                          structure={analysisResult.preview.structure}
                                          mapping={columnMapping[uniqueKey] || {}}
                                          setMapping={mapping => {
                                            setColumnMapping(prev => ({ ...prev, [uniqueKey]: mapping }));
                                            // Optionally, update SQL here if needed
                                          }}
                                        />
                                      );
                                    })()}
                                  </>
                                )}
                                {activeSQLTab === 'sql' && (
                                  <div className="bg-gray-100 rounded p-2 text-xs overflow-x-auto">
                                    {/* Show generated SQL, or a placeholder if not generated yet */}
                                    {generatedSQL || 'SQL will appear here after mapping.'}
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      ) : hasServerPreview ? (
                        <div className="p-3">
                          {previewAnalysis?.structure && (
                            <div className="mb-2">
                              <div className="font-semibold text-gray-700">Detected Table Structure</div>
                              <pre className="bg-gray-100 rounded p-2 text-xs overflow-x-auto">{JSON.stringify(previewAnalysis.structure, null, 2)}</pre>
                            </div>
                          )}
                          <FilePreview
                            analysis={previewAnalysis}
                            getAllConfigs={() => {}}
                            tableName={tableName}
                            setTableName={setTableName}
                            tableNameAvailable={tableNameAvailable}
                            setTableNameAvailable={setTableNameAvailable}
                            showSQL={showSQL}
                            setShowSQL={setShowSQL}
                            generatedSQL={generatedSQL}
                            setGeneratedSQL={setGeneratedSQL}
                          />
                          {/* Show SQL / Mapping Tabs for server preview */}
                          {showSQL && (
                            <div className="mt-4">
                              <div className="flex border-b border-gray-200 mb-2">
                                <button
                                  className={`px-4 py-2 text-sm font-medium focus:outline-none ${activeSQLTab === 'mapping' ? 'border-b-2 border-blue-600 text-blue-700' : 'text-gray-600'}`}
                                  onClick={() => setActiveSQLTab('mapping')}
                                >
                                  Column Mapping
                                </button>
                                <button
                                  className={`ml-2 px-4 py-2 text-sm font-medium focus:outline-none ${activeSQLTab === 'sql' ? 'border-b-2 border-blue-600 text-blue-700' : 'text-gray-600'}`}
                                  onClick={() => setActiveSQLTab('sql')}
                                >
                                  SQL
                                </button>
                              </div>
                              <div>
                                {activeSQLTab === 'mapping' && (
                                  <>
                                    {(() => {
                                      // Debug log for server preview
                                      console.log('Server preview structure:', previewAnalysis);
                                      if (!previewAnalysis || !Array.isArray(previewAnalysis.headers) || previewAnalysis.headers.length === 0) {
                                        return <div className="text-xs text-red-600">No columns detected in this file, mapping unavailable.</div>;
                                      }
                                      return (
                                        <ColumnMappingOptions
                                          structure={previewAnalysis.structure}
                                          mapping={columnMapping[uniqueKey] || {}}
                                          setMapping={mapping => {
                                            setColumnMapping(prev => ({ ...prev, [uniqueKey]: mapping }));
                                            // Optionally, update SQL here if needed
                                          }}
                                        />
                                      );
                                    })()}
                                  </>
                                )}
                                {activeSQLTab === 'sql' && (
                                  <div className="bg-gray-100 rounded p-2 text-xs overflow-x-auto">
                                    {generatedSQL || 'SQL will appear here after mapping.'}
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      ) : analysisResult.status === 'completed' ? (
                        <div className="p-3 text-gray-500 text-xs">No preview available.</div>
                      ) : null}
                      {analysisResult.status === 'failed' && (
                        <div className="p-3 text-red-600 text-xs">Analysis failed: {analysisResult.error}</div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
        {Object.keys(analysisResults).length === 0 && (<div className="text-center text-gray-500 mt-8">No files uploaded or no analysis results yet.</div>)}
      </div>
    </div>
  );
};

export default Upload;