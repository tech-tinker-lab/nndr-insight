import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, Tabs, Tab, Box, Alert, Stepper, Step, StepLabel, CircularProgress, Table, TableHead, TableRow, TableCell, TableBody, Checkbox, IconButton, TableContainer, Paper, Select, MenuItem, Chip, Typography, Accordion, AccordionSummary, AccordionDetails
} from '@mui/material';
import { Upload as UploadIcon, Edit as EditIcon } from '@mui/icons-material';
import Papa from 'papaparse';

const DataStandardsRegistry = () => {
  const [standards, setStandards] = useState([]);
  const [categories, setCategories] = useState({});
  const [complianceLevels, setComplianceLevels] = useState({});
  const [statistics, setStatistics] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filters
  const [filters, setFilters] = useState({
    category: '',
    country: '',
    compliance_level: '',
    governing_body: ''
  });
  
  // Search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  
  // UI State
  const [selectedStandard, setSelectedStandard] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // grid, list, table

  // New Standard Handlers
  const [newStandardOpen, setNewStandardOpen] = useState(false);
  const [newStandardTab, setNewStandardTab] = useState(0);
  const [manualForm, setManualForm] = useState({
    name: '',
    description: '',
    governing_body: '',
    version: '1.0',
    fields: '', // JSON string or array
    compliance_level: '',
    category: '',
    country: ''
  });
  const [importFile, setImportFile] = useState(null);
  const [importError, setImportError] = useState('');
  const [submitError, setSubmitError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Edit/Fork Dialog State
  const [editMode, setEditMode] = useState(null); // 'edit' or 'fork'
  const [editStandard, setEditStandard] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [editError, setEditError] = useState('');
  const [editSubmitting, setEditSubmitting] = useState(false);

  // Wizard state for Import
  const [importWizardOpen, setImportWizardOpen] = useState(false);
  const [importStep, setImportStep] = useState(0);
  const [importFileObj, setImportFileObj] = useState(null);
  const [importFileType, setImportFileType] = useState('');
  const [importHeaderRow, setImportHeaderRow] = useState(true);
  const [importSampleData, setImportSampleData] = useState([]);
  const [importFields, setImportFields] = useState([]); // [{name, type, required, description, constraints}]
  const [importMeta, setImportMeta] = useState({ name: '', description: '', governing_body: '', version: '1.0', category: '', country: '', compliance_level: '', validation_rules: '' });
  const [importReviewing, setImportReviewing] = useState(false);
  const [importErrorMsg, setImportErrorMsg] = useState('');

  const SMALL_FILE_LIMIT = 10 * 1024 * 1024; // 10MB
  const MEDIUM_FILE_LIMIT = 2 * 1024 * 1024 * 1024; // 2GB
  const CSV_SAMPLE_ROWS = 10000;

  const [importAnalysisMode, setImportAnalysisMode] = useState('auto'); // 'auto', 'full', 'sample', 'server'
  const [importAnalysisStatus, setImportAnalysisStatus] = useState('');
  const [importAnalysisProgress, setImportAnalysisProgress] = useState(0);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load standards with current filters
      const standardsResponse = await api.get('/api/design-enhanced/data-standards', {
        params: filters
      });
      setStandards(Object.entries(standardsResponse.data.standards).map(([id, standard]) => ({
        id,
        ...standard
      })));
      
      // Load categories
      const categoriesResponse = await api.get('/api/design-enhanced/data-standards/categories');
      setCategories(categoriesResponse.data.categories);
      
      // Load compliance levels
      const complianceResponse = await api.get('/api/design-enhanced/data-standards/compliance-levels');
      setComplianceLevels(complianceResponse.data.compliance_levels);
      
      // Load statistics
      const statsResponse = await api.get('/api/design-enhanced/data-standards/statistics');
      setStatistics(statsResponse.data);
      
    } catch (err) {
      setError('Failed to load data standards');
      console.error('Error loading data standards:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    
    try {
      setSearching(true);
      const response = await api.get('/api/design-enhanced/data-standards/search', {
        params: {
          query: searchQuery,
          category: filters.category,
          country: filters.country
        }
      });
      setSearchResults(response.data.results);
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setSearching(false);
    }
  };

  const getComplianceLevelColor = (level) => {
    const colors = {
      mandatory: 'bg-red-100 text-red-800 border-red-200',
      recommended: 'bg-blue-100 text-blue-800 border-blue-200',
      industry: 'bg-green-100 text-green-800 border-green-200',
      de_facto: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      community: 'bg-purple-100 text-purple-800 border-purple-200'
    };
    return colors[level] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getCategoryColor = (category) => {
    const colors = {
      government: 'bg-blue-50 border-blue-200',
      international: 'bg-green-50 border-green-200',
      private: 'bg-purple-50 border-purple-200',
      financial: 'bg-yellow-50 border-yellow-200',
      healthcare: 'bg-red-50 border-red-200',
      transportation: 'bg-indigo-50 border-indigo-200',
      environmental: 'bg-emerald-50 border-emerald-200'
    };
    return colors[category] || 'bg-gray-50 border-gray-200';
  };

  // New Standard Handlers
  const handleManualChange = (e) => {
    setManualForm({ ...manualForm, [e.target.name]: e.target.value });
  };

  const handleImportFile = (e) => {
    setImportFile(e.target.files[0]);
    setImportError('');
  };

  const handleNewStandardSubmit = async () => {
    setSubmitting(true);
    setSubmitError('');
    try {
      if (newStandardTab === 0) {
        // Manual entry
        const payload = {
          ...manualForm,
          fields: manualForm.fields ? JSON.parse(manualForm.fields) : []
        };
        await api.post('/api/design-enhanced/data-standards', payload);
      } else {
        // Import
        if (!importFile) {
          setImportError('Please select a file to import.');
          setSubmitting(false);
          return;
        }
        const formData = new FormData();
        formData.append('file', importFile);
        await api.post('/api/design-enhanced/data-standards/import', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      }
      setNewStandardOpen(false);
      setManualForm({ name: '', description: '', governing_body: '', version: '1.0', fields: '', compliance_level: '', category: '', country: '' });
      setImportFile(null);
      loadData();
    } catch (err) {
      setSubmitError('Failed to create/import standard.');
    } finally {
      setSubmitting(false);
    }
  };

  const openEditDialog = (mode, standard) => {
    setEditMode(mode);
    setEditStandard(standard);
    setEditForm({
      ...standard,
      fields: JSON.stringify(standard.fields || [], null, 2),
      version: mode === 'fork' ? `${parseFloat(standard.version || '1.0') + 0.1}` : standard.version
    });
    setEditError('');
  };

  const handleEditChange = (e) => {
    setEditForm({ ...editForm, [e.target.name]: e.target.value });
  };

  const handleEditSubmit = async () => {
    setEditSubmitting(true);
    setEditError('');
    try {
      const payload = {
        ...editForm,
        fields: editForm.fields ? JSON.parse(editForm.fields) : []
      };
      if (editMode === 'edit') {
        await api.put(`/api/design-enhanced/data-standards/${editStandard.id}`, payload);
      } else {
        // Fork/version: POST to fork endpoint or create new with parent_id
        payload.parent_id = editStandard.id;
        await api.post('/api/design-enhanced/data-standards', payload);
      }
      setEditMode(null);
      setEditStandard(null);
      setEditForm({});
      loadData();
    } catch (err) {
      setEditError('Failed to save changes.');
    } finally {
      setEditSubmitting(false);
    }
  };

  // Enhanced Import Wizard Handlers
  const handleImportWizardFile = (e) => {
    const file = e.target.files[0];
    setImportFileObj(file);
    setImportFileType('');
    setImportHeaderRow(true);
    setImportSampleData([]);
    setImportFields([]);
    setImportStep(1);
    setImportErrorMsg('');
    setImportAnalysisMode('auto');
    setImportAnalysisStatus('');
    setImportAnalysisProgress(0);
    if (!file) return;
    // Detect file type
    const ext = file.name.split('.').pop().toLowerCase();
    if (["csv", "tsv"].includes(ext)) {
      setImportFileType('csv');
      Papa.parse(file, {
        header: true,
        preview: 10,
        skipEmptyLines: true,
        complete: (results) => {
          setImportSampleData(results.data);
          // AI: Guess field types from sample
          const fields = results.meta.fields.map(field => {
            const values = results.data.map(row => row[field]).filter(Boolean);
            let type = 'string';
            if (values.every(v => /^\d+$/.test(v))) type = 'integer';
            else if (values.every(v => /^\d+\.\d+$/.test(v))) type = 'float';
            else if (values.every(v => !isNaN(Date.parse(v)))) type = 'date';
            return { name: field, type, required: false, description: '', constraints: '', confidence: 0, sample_values: [] };
          });
          setImportFields(fields);
        },
        error: (err) => setImportErrorMsg('Failed to parse CSV: ' + err.message)
      });
    } else if (["json", "yaml", "yml"].includes(ext)) {
      setImportFileType(ext);
      // TODO: Parse and extract fields for JSON/YAML
      setImportErrorMsg('JSON/YAML import not yet implemented.');
    } else if (["zip", "gpkg", "gml", "shp"].includes(ext)) {
      setImportFileType('spatial');
      setImportErrorMsg('Spatial/ZIP import not yet implemented.');
    } else {
      setImportErrorMsg('Unsupported file type.');
    }
  };

  const analyzeCsvFile = (file, { full }) => {
    setImportFileType('csv');
    setImportAnalysisProgress(0);
    Papa.parse(file, {
      header: true,
      preview: full ? undefined : CSV_SAMPLE_ROWS,
      skipEmptyLines: true,
      step: (results, parser) => {
        // For large files, can update progress here
      },
      complete: (results) => {
        setImportSampleData(results.data);
        // AI: Guess field types from sample
        const fields = results.meta.fields.map(field => {
          const values = results.data.map(row => row[field]).filter(Boolean);
          let type = 'string';
          if (values.every(v => /^\d+$/.test(v))) type = 'integer';
          else if (values.every(v => /^\d+\.\d+$/.test(v))) type = 'float';
          else if (values.every(v => !isNaN(Date.parse(v)))) type = 'date';
          return { name: field, type, required: false, description: '', constraints: '', confidence: 0, sample_values: [] };
        });
        setImportFields(fields);
        setImportAnalysisStatus(full ? 'Full file analyzed.' : `Sampled first ${CSV_SAMPLE_ROWS} rows.`);
      },
      error: (err) => setImportErrorMsg('Failed to parse CSV: ' + err.message)
    });
  };

  const handleRequestFullAnalysis = () => {
    if (!importFileObj) return;
    setImportAnalysisStatus('Running full client-side analysis...');
    analyzeCsvFile(importFileObj, { full: true });
  };

  const handleRequestServerAnalysis = () => {
    setImportAnalysisStatus('Uploading file for server-side analysis...');
    setImportAnalysisMode('server');
    // TODO: Implement server-side upload/analysis logic
    setImportErrorMsg('Server-side analysis not yet implemented.');
  };

  const handleImportFieldEdit = (idx, key, value) => {
    setImportFields(fields => fields.map((f, i) => i === idx ? { ...f, [key]: value } : f));
  };

  const handleImportMetaChange = (e) => {
    setImportMeta({ ...importMeta, [e.target.name]: e.target.value });
  };

  const handleImportWizardNext = () => setImportStep(s => s + 1);
  const handleImportWizardBack = () => setImportStep(s => s - 1);

  const handleImportWizardSubmit = async () => {
    setImportReviewing(true);
    try {
      const payload = {
        ...importMeta,
        fields: importFields,
        validation_rules: importMeta.validation_rules ? JSON.parse(importMeta.validation_rules) : []
      };
      await api.post('/api/design-enhanced/data-standards', payload);
      setImportWizardOpen(false);
      setImportStep(0);
      setImportFileObj(null);
      setImportFields([]);
      setImportMeta({ name: '', description: '', governing_body: '', version: '1.0', category: '', country: '', compliance_level: '', validation_rules: '' });
      loadData();
    } catch (err) {
      setImportErrorMsg('Failed to create standard: ' + (err.response?.data?.detail || err.message));
    } finally {
      setImportReviewing(false);
    }
  };

  const handleImportWizardReset = () => {
    setImportStep(0);
    setImportFileObj(null);
    setImportFileType('');
    setImportHeaderRow(true);
    setImportSampleData([]);
    setImportFields([]);
    setImportMeta({ name: '', description: '', governing_body: '', version: '1.0', category: '', country: '', compliance_level: '', validation_rules: '' });
    setImportReviewing(false);
    setImportErrorMsg('');
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
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  const displayStandards = searchQuery ? searchResults : standards;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Data Standards Registry</h1>
            <p className="mt-1 text-sm text-gray-500">
              Comprehensive collection of data standards from government, private sector, and international organizations
            </p>
          </div>
          <div className="flex items-center space-x-4">
            {/* New Standard Button */}
            <Button variant="contained" color="primary" onClick={() => setNewStandardOpen(true)}>
              + New Standard
            </Button>
            {/* View Mode Buttons */}
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-2 rounded-md text-sm font-medium ${viewMode === 'grid' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}`}
            >
              Grid
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-2 rounded-md text-sm font-medium ${viewMode === 'list' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}`}
            >
              List
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`px-3 py-2 rounded-md text-sm font-medium ${viewMode === 'table' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'}`}
            >
              Table
            </button>
          </div>
        </div>
      </div>

      {/* New Standard Modal */}
      <Dialog open={newStandardOpen} onClose={() => setNewStandardOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Data Standard</DialogTitle>
        <DialogContent>
          <Tabs value={newStandardTab} onChange={(_, v) => setNewStandardTab(v)}>
            <Tab label="Manual Entry" />
            <Tab label="Import" />
          </Tabs>
          <Box mt={2} hidden={newStandardTab !== 0}>
            <TextField label="Name" name="name" value={manualForm.name} onChange={handleManualChange} fullWidth margin="normal" />
            <TextField label="Description" name="description" value={manualForm.description} onChange={handleManualChange} fullWidth margin="normal" />
            <TextField label="Governing Body" name="governing_body" value={manualForm.governing_body} onChange={handleManualChange} fullWidth margin="normal" />
            <TextField label="Version" name="version" value={manualForm.version} onChange={handleManualChange} fullWidth margin="normal" />
            <TextField label="Category" name="category" value={manualForm.category} onChange={handleManualChange} fullWidth margin="normal" />
            <TextField label="Country" name="country" value={manualForm.country} onChange={handleManualChange} fullWidth margin="normal" />
            <TextField label="Compliance Level" name="compliance_level" value={manualForm.compliance_level} onChange={handleManualChange} fullWidth margin="normal" />
            <TextField label="Fields (JSON array)" name="fields" value={manualForm.fields} onChange={handleManualChange} fullWidth margin="normal" multiline minRows={2} />
          </Box>
          <Box mt={2} hidden={newStandardTab !== 1}>
            <Button variant="outlined" startIcon={<UploadIcon />} onClick={() => setImportWizardOpen(true)}>
              Start Import Wizard
            </Button>
          </Box>
          {submitError && <Alert severity="error" sx={{ mt: 2 }}>{submitError}</Alert>}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewStandardOpen(false)} disabled={submitting}>Cancel</Button>
          <Button onClick={handleNewStandardSubmit} variant="contained" color="primary" disabled={submitting}>
            {submitting ? 'Submitting...' : 'Submit'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white shadow rounded-lg p-4">
          <div className="text-2xl font-bold text-gray-900">{statistics.total_standards}</div>
          <div className="text-sm text-gray-500">Total Standards</div>
        </div>
        <div className="bg-white shadow rounded-lg p-4">
          <div className="text-2xl font-bold text-blue-600">{Object.keys(statistics.by_category || {}).length}</div>
          <div className="text-sm text-gray-500">Categories</div>
        </div>
        <div className="bg-white shadow rounded-lg p-4">
          <div className="text-2xl font-bold text-green-600">{Object.keys(statistics.by_country || {}).length}</div>
          <div className="text-sm text-gray-500">Countries/Regions</div>
        </div>
        <div className="bg-white shadow rounded-lg p-4">
          <div className="text-2xl font-bold text-purple-600">{Object.keys(statistics.by_governing_body || {}).length}</div>
          <div className="text-sm text-gray-500">Governing Bodies</div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Category Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select
              value={filters.category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="">All Categories</option>
              {Object.entries(categories).map(([key, category]) => (
                <option key={key} value={key}>{category.name}</option>
              ))}
            </select>
          </div>

          {/* Country Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
            <select
              value={filters.country}
              onChange={(e) => handleFilterChange('country', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="">All Countries</option>
              <option value="UK">UK</option>
              <option value="EU">European Union</option>
              <option value="US">United States</option>
              <option value="International">International</option>
            </select>
          </div>

          {/* Compliance Level Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Compliance</label>
            <select
              value={filters.compliance_level}
              onChange={(e) => handleFilterChange('compliance_level', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="">All Levels</option>
              {Object.entries(complianceLevels).map(([key, level]) => (
                <option key={key} value={key}>{level.name}</option>
              ))}
            </select>
          </div>

          {/* Search */}
          <div className="lg:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Search Standards</label>
            <div className="flex">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by name, description, or governing body..."
                className="flex-1 border border-gray-300 rounded-l-md px-3 py-2 text-sm"
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <button
                onClick={handleSearch}
                disabled={searching}
                className="bg-blue-600 text-white px-4 py-2 rounded-r-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                {searching ? 'Searching...' : 'Search'}
              </button>
            </div>
          </div>
        </div>

        {/* Apply Filters Button */}
        <div className="mt-4 flex justify-end">
          <button
            onClick={loadData}
            className="bg-gray-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-700"
          >
            Apply Filters
          </button>
        </div>
      </div>

      {/* Standards Display */}
      <div className="space-y-4">
        {viewMode === 'grid' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {displayStandards.map((standard) => (
              <div
                key={standard.id}
                className={`bg-white shadow rounded-lg p-6 border ${getCategoryColor(standard.category)} hover:shadow-lg transition-shadow cursor-pointer`}
                onClick={() => setSelectedStandard(standard)}
              >
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">{standard.name}</h3>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getComplianceLevelColor(standard.compliance_level)}`}>
                    {complianceLevels[standard.compliance_level]?.name || standard.compliance_level}
                  </span>
                </div>
                
                <p className="text-sm text-gray-600 mb-4 line-clamp-3">{standard.description}</p>
                
                <div className="flex space-x-2 mt-2">
                  <Button size="small" variant="outlined" onClick={e => { e.stopPropagation(); openEditDialog('edit', standard); }}>Edit</Button>
                  <Button size="small" variant="outlined" color="secondary" onClick={e => { e.stopPropagation(); openEditDialog('fork', standard); }}>Fork/Version</Button>
                </div>
              </div>
            ))}
          </div>
        )}

        {viewMode === 'list' && (
          <div className="space-y-4">
            {displayStandards.map((standard) => (
              <div
                key={standard.id}
                className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => setSelectedStandard(standard)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900">{standard.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{standard.description}</p>
                  </div>
                  <span className={`px-3 py-1 text-sm font-medium rounded-full border ${getComplianceLevelColor(standard.compliance_level)}`}>
                    {complianceLevels[standard.compliance_level]?.name || standard.compliance_level}
                  </span>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Governing Body:</span>
                    <p className="text-gray-600">{standard.governing_body}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Country:</span>
                    <p className="text-gray-600">{standard.country}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Version:</span>
                    <p className="text-gray-600">{standard.version}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Required Fields:</span>
                    <p className="text-gray-600">{standard.required_fields?.length || 0}</p>
                  </div>
                </div>
                <div className="flex space-x-2 mt-2">
                  <Button size="small" variant="outlined" onClick={e => { e.stopPropagation(); openEditDialog('edit', standard); }}>Edit</Button>
                  <Button size="small" variant="outlined" color="secondary" onClick={e => { e.stopPropagation(); openEditDialog('fork', standard); }}>Fork/Version</Button>
                </div>
              </div>
            ))}
          </div>
        )}

        {viewMode === 'table' && (
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Standard</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Governing Body</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Country</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Compliance</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Version</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {displayStandards.map((standard) => (
                  <tr
                    key={standard.id}
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => setSelectedStandard(standard)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{standard.name}</div>
                        <div className="text-sm text-gray-500">{standard.description}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">{categories[standard.category]?.name || standard.category}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{standard.governing_body}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{standard.country}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getComplianceLevelColor(standard.compliance_level)}`}>
                        {complianceLevels[standard.compliance_level]?.name || standard.compliance_level}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{standard.version}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Standard Detail Modal */}
      {selectedStandard && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">{selectedStandard.name}</h3>
                <button
                  onClick={() => setSelectedStandard(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-700">Description</h4>
                  <p className="text-sm text-gray-600 mt-1">{selectedStandard.description}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Governing Body</h4>
                    <p className="text-sm text-gray-600 mt-1">{selectedStandard.governing_body}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Country</h4>
                    <p className="text-sm text-gray-600 mt-1">{selectedStandard.country}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Version</h4>
                    <p className="text-sm text-gray-600 mt-1">{selectedStandard.version}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Compliance Level</h4>
                    <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full border mt-1 ${getComplianceLevelColor(selectedStandard.compliance_level)}`}>
                      {complianceLevels[selectedStandard.compliance_level]?.name || selectedStandard.compliance_level}
                    </span>
                  </div>
                </div>
                
                <div>
                  <h4 className="text-sm font-medium text-gray-700">Required Fields</h4>
                  <div className="mt-1 flex flex-wrap gap-2">
                    {selectedStandard.required_fields?.map((field, index) => (
                      <span key={index} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                        {field}
                      </span>
                    ))}
                  </div>
                </div>
                
                {selectedStandard.url && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Documentation</h4>
                    <a
                      href={selectedStandard.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-800 mt-1 inline-block"
                    >
                      View Official Documentation →
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit/Fork Modal */}
      <Dialog open={!!editMode} onClose={() => setEditMode(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{editMode === 'edit' ? 'Edit Data Standard' : 'Fork/Version Data Standard'}</DialogTitle>
        <DialogContent>
          <TextField label="Name" name="name" value={editForm.name || ''} onChange={handleEditChange} fullWidth margin="normal" />
          <TextField label="Description" name="description" value={editForm.description || ''} onChange={handleEditChange} fullWidth margin="normal" />
          <TextField label="Governing Body" name="governing_body" value={editForm.governing_body || ''} onChange={handleEditChange} fullWidth margin="normal" />
          <TextField label="Version" name="version" value={editForm.version || ''} onChange={handleEditChange} fullWidth margin="normal" />
          <TextField label="Category" name="category" value={editForm.category || ''} onChange={handleEditChange} fullWidth margin="normal" />
          <TextField label="Country" name="country" value={editForm.country || ''} onChange={handleEditChange} fullWidth margin="normal" />
          <TextField label="Compliance Level" name="compliance_level" value={editForm.compliance_level || ''} onChange={handleEditChange} fullWidth margin="normal" />
          <TextField label="Fields (JSON array)" name="fields" value={editForm.fields || ''} onChange={handleEditChange} fullWidth margin="normal" multiline minRows={2} />
          {editError && <Alert severity="error" sx={{ mt: 2 }}>{editError}</Alert>}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditMode(null)} disabled={editSubmitting}>Cancel</Button>
          <Button onClick={handleEditSubmit} variant="contained" color="primary" disabled={editSubmitting}>
            {editSubmitting ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Import Wizard Modal */}
      <Dialog open={importWizardOpen} onClose={() => setImportWizardOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Import Data Standard (Wizard)</DialogTitle>
        <DialogContent>
          <Stepper activeStep={importStep} alternativeLabel>
            <Step><StepLabel>Upload File</StepLabel></Step>
            <Step><StepLabel>Analyze & AI Suggest</StepLabel></Step>
            <Step><StepLabel>Review Fields</StepLabel></Step>
            <Step><StepLabel>Validation & Metadata</StepLabel></Step>
            <Step><StepLabel>Review & Submit</StepLabel></Step>
          </Stepper>
          <Box mt={3}>
            {importStep === 0 && (
              <div>
                <input type="file" accept=".csv,.json,.yaml,.yml,.zip,.gpkg,.gml,.shp" onChange={handleImportWizardFile} />
                {importErrorMsg && <Alert severity="error" sx={{ mt: 2 }}>{importErrorMsg}</Alert>}
              </div>
            )}
            {importStep === 1 && importFileType === 'csv' && (
              <div>
                <Alert severity="info">{importAnalysisStatus}</Alert>
                {importAnalysisMode === 'auto' && importFileObj && importFileObj.size >= SMALL_FILE_LIMIT && importFileObj.size < MEDIUM_FILE_LIMIT && (
                  <Box mt={2}>
                    <Button onClick={handleRequestFullAnalysis} variant="outlined" sx={{ mr: 2 }}>Analyze Full File (Client)</Button>
                    <Button onClick={handleRequestServerAnalysis} variant="outlined">Analyze on Server</Button>
                  </Box>
                )}
                <Table size="small" sx={{ mt: 2 }}>
                  <TableHead>
                    <TableRow>
                      {importFields.map((f, idx) => <TableCell key={idx}>{f.name}</TableCell>)}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {importSampleData.slice(0, 5).map((row, i) => (
                      <TableRow key={i}>
                        {importFields.map((f, idx) => <TableCell key={idx}>{row[f.name]}</TableCell>)}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                <Box mt={2}>
                  <Button onClick={handleImportWizardNext} variant="contained">Next</Button>
                </Box>
              </div>
            )}
            {importStep === 2 && (
              <div>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Review and edit detected fields. AI has suggested types, confidence, and sample values. You can override any value below.
                </Alert>
                <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Field Name</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Confidence</TableCell>
                        <TableCell>Required</TableCell>
                        <TableCell>Description</TableCell>
                        <TableCell>Constraints</TableCell>
                        <TableCell>Sample Values</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {importFields.map((f, idx) => (
                        <TableRow key={idx} hover>
                          <TableCell>
                            <TextField value={f.name} onChange={e => handleImportFieldEdit(idx, 'name', e.target.value)} size="small" />
                          </TableCell>
                          <TableCell>
                            <FormControl size="small" fullWidth>
                              <Select
                                value={f.type}
                                onChange={e => handleImportFieldEdit(idx, 'type', e.target.value)}
                                displayEmpty
                              >
                                <MenuItem value="string"><Chip label="String" color="primary" size="small" /></MenuItem>
                                <MenuItem value="integer"><Chip label="Integer" color="success" size="small" /></MenuItem>
                                <MenuItem value="float"><Chip label="Float" color="info" size="small" /></MenuItem>
                                <MenuItem value="date"><Chip label="Date" color="warning" size="small" /></MenuItem>
                                <MenuItem value="boolean"><Chip label="Boolean" color="secondary" size="small" /></MenuItem>
                                <MenuItem value="geometry"><Chip label="Geometry" color="secondary" size="small" /></MenuItem>
                                <MenuItem value="other"><Chip label="Other" color="default" size="small" /></MenuItem>
                              </Select>
                            </FormControl>
                          </TableCell>
                          <TableCell>
                            {f.confidence !== undefined ? (
                              <Chip
                                label={f.confidence >= 0 ? `${Math.round((f.confidence || 0) * 100)}%` : 'N/A'}
                                color={f.confidence > 0.8 ? 'success' : f.confidence > 0.6 ? 'warning' : 'error'}
                                size="small"
                              />
                            ) : (
                              <Chip label="N/A" size="small" />
                            )}
                          </TableCell>
                          <TableCell>
                            <Checkbox checked={!!f.required} onChange={e => handleImportFieldEdit(idx, 'required', e.target.checked)} />
                          </TableCell>
                          <TableCell>
                            <TextField value={f.description} onChange={e => handleImportFieldEdit(idx, 'description', e.target.value)} size="small" />
                          </TableCell>
                          <TableCell>
                            <TextField value={f.constraints} onChange={e => handleImportFieldEdit(idx, 'constraints', e.target.value)} size="small" />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" noWrap>
                              {f.sample_values && f.sample_values.length > 0
                                ? f.sample_values.slice(0, 3).join(', ')
                                : '—'}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                <Box mt={2} display="flex" justifyContent="space-between" alignItems="center">
                  <Accordion sx={{ flex: 1, mr: 2 }}>
                    <AccordionSummary expandIcon={<IconButton size="small"><span>▼</span></IconButton>}>
                      <Typography variant="subtitle1">Field Analysis Summary</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Box display="flex" flexDirection="column" gap={1}>
                        <Typography variant="body2"><strong>Total Fields:</strong> {importFields.length}</Typography>
                        <Typography variant="body2"><strong>Required Fields:</strong> {importFields.filter(f => f.required).length}</Typography>
                        <Typography variant="body2"><strong>String Fields:</strong> {importFields.filter(f => f.type === 'string').length}</Typography>
                        <Typography variant="body2"><strong>Numeric Fields:</strong> {importFields.filter(f => f.type === 'integer' || f.type === 'float').length}</Typography>
                        <Typography variant="body2"><strong>Date Fields:</strong> {importFields.filter(f => f.type === 'date').length}</Typography>
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                  <Box>
                    <Button onClick={handleImportWizardBack} sx={{ mr: 2 }}>Back</Button>
                    <Button onClick={handleImportWizardNext} variant="contained">Next</Button>
                  </Box>
                </Box>
              </div>
            )}
            {importStep === 3 && (
              <div>
                <Alert severity="info">Add validation rules and enter standard metadata.</Alert>
                <TextField label="Validation Rules (JSON array)" name="validation_rules" value={importMeta.validation_rules} onChange={handleImportMetaChange} fullWidth margin="normal" multiline minRows={2} />
                <TextField label="Name" name="name" value={importMeta.name} onChange={handleImportMetaChange} fullWidth margin="normal" />
                <TextField label="Description" name="description" value={importMeta.description} onChange={handleImportMetaChange} fullWidth margin="normal" />
                <TextField label="Governing Body" name="governing_body" value={importMeta.governing_body} onChange={handleImportMetaChange} fullWidth margin="normal" />
                <TextField label="Version" name="version" value={importMeta.version} onChange={handleImportMetaChange} fullWidth margin="normal" />
                <TextField label="Category" name="category" value={importMeta.category} onChange={handleImportMetaChange} fullWidth margin="normal" />
                <TextField label="Country" name="country" value={importMeta.country} onChange={handleImportMetaChange} fullWidth margin="normal" />
                <TextField label="Compliance Level" name="compliance_level" value={importMeta.compliance_level} onChange={handleImportMetaChange} fullWidth margin="normal" />
                <Box mt={2}>
                  <Button onClick={handleImportWizardBack} sx={{ mr: 2 }}>Back</Button>
                  <Button onClick={handleImportWizardNext} variant="contained">Next</Button>
                </Box>
              </div>
            )}
            {importStep === 4 && (
              <div>
                <Alert severity="success">Review your new standard below. Click Submit to create it.</Alert>
                <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 4, maxHeight: 300, overflow: 'auto' }}>{JSON.stringify({ ...importMeta, fields: importFields }, null, 2)}</pre>
                {importErrorMsg && <Alert severity="error" sx={{ mt: 2 }}>{importErrorMsg}</Alert>}
                <Box mt={2}>
                  <Button onClick={handleImportWizardBack} sx={{ mr: 2 }}>Back</Button>
                  <Button onClick={handleImportWizardSubmit} variant="contained" disabled={importReviewing}>
                    {importReviewing ? <CircularProgress size={20} /> : 'Submit'}
                  </Button>
                </Box>
              </div>
            )}
          </Box>
        </DialogContent>
        <DialogActions sx={{ justifyContent: 'space-between' }}>
          <Button onClick={handleImportWizardReset} color="secondary" variant="outlined">
            Reset
          </Button>
          {/* Navigation/submit buttons are handled inside each step, so nothing else here for now */}
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default DataStandardsRegistry; 