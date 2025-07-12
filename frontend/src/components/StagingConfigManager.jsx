import React, { useState, useEffect } from 'react';
import { 
  Settings, 
  Save, 
  Loader, 
  CheckCircle, 
  AlertCircle, 
  Database, 
  FileText,
  Sparkles,
  Clock,
  Trash2,
  Edit3,
  Eye
} from 'lucide-react';
import api from '../api/axios';
import toast from 'react-hot-toast';

const StagingConfigManager = ({ 
  headers = [], 
  fileName = '', 
  fileType = 'csv',
  onConfigSelect,
  onConfigSave,
  className = ""
}) => {
  const [configs, setConfigs] = useState([]);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedConfig, setSelectedConfig] = useState(null);
  const [showConfigs, setShowConfigs] = useState(false);
  const [bestMatch, setBestMatch] = useState(null);

  useEffect(() => {
    if (headers.length > 0) {
      loadConfigs();
      findMatches();
    }
  }, [headers, fileName, fileType]);

  const loadConfigs = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/admin/staging/configs');
      setConfigs(response.data.configs || []);
    } catch (error) {
      console.error('Error loading configs:', error);
      toast.error('Failed to load configurations');
    } finally {
      setLoading(false);
    }
  };

  const findMatches = async () => {
    if (headers.length === 0) return;

    try {
      const response = await api.post('/api/admin/staging/configs/match', {
        headers,
        file_name: fileName,
        file_type: fileType
      });
      
      setMatches(response.data.matches || []);
      setBestMatch(response.data.best_match);
    } catch (error) {
      console.error('Error finding matches:', error);
    }
  };

  const handleConfigSelect = async (configId) => {
    try {
      const response = await api.get(`/api/admin/staging/configs/${configId}`);
      const config = response.data;
      
      setSelectedConfig(config);
      if (onConfigSelect) {
        onConfigSelect(config);
      }
      
      toast.success(`Loaded configuration: ${config.name}`);
    } catch (error) {
      console.error('Error loading config:', error);
      toast.error('Failed to load configuration');
    }
  };

  const handleConfigSave = async (configData) => {
    try {
      const response = await api.post('/api/admin/staging/configs', configData);
      
      toast.success('Configuration saved successfully');
      
      // Reload configs
      await loadConfigs();
      await findMatches();
      
      if (onConfigSave) {
        onConfigSave(response.data);
      }
      
      return response.data;
    } catch (error) {
      console.error('Error saving config:', error);
      toast.error('Failed to save configuration');
      throw error;
    }
  };

  const getMatchIcon = (score) => {
    if (score >= 0.8) return <CheckCircle className="w-4 h-4 text-green-500" />;
    if (score >= 0.6) return <AlertCircle className="w-4 h-4 text-yellow-500" />;
    return <AlertCircle className="w-4 h-4 text-red-500" />;
  };

  const getMatchColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className={`${className}`}>
      {/* Configuration Management Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Settings className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-medium text-gray-900">Staging Configurations</h3>
        </div>
        <button
          onClick={() => setShowConfigs(!showConfigs)}
          className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
        >
          {showConfigs ? 'Hide' : 'Show'} Configs
        </button>
      </div>

      {/* Best Match Display */}
      {bestMatch && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-green-800">Best Match Found</span>
            </div>
            <div className={`text-sm font-medium ${getMatchColor(bestMatch.similarity_score)}`}>
              {Math.round(bestMatch.similarity_score * 100)}% match
            </div>
          </div>
          <div className="mt-2">
            <div className="text-sm text-green-700 font-medium">{bestMatch.name}</div>
            <div className="text-xs text-green-600">{bestMatch.description}</div>
            <div className="text-xs text-green-600 mt-1">{bestMatch.match_reason}</div>
          </div>
          <button
            onClick={() => handleConfigSelect(bestMatch.id)}
            className="mt-2 text-xs bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700"
          >
            Use This Configuration
          </button>
        </div>
      )}

      {/* Configuration List */}
      {showConfigs && (
        <div className="space-y-3">
          {/* Matches Section */}
          {matches.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                <Database className="w-4 h-4 mr-1" />
                Matching Configurations ({matches.length})
              </h4>
              <div className="space-y-2">
                {matches.map((match) => (
                  <div
                    key={match.id}
                    className="p-3 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 cursor-pointer"
                    onClick={() => handleConfigSelect(match.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getMatchIcon(match.similarity_score)}
                        <div>
                          <div className="text-sm font-medium text-blue-900">{match.name}</div>
                          <div className="text-xs text-blue-700">{match.staging_table_name}</div>
                        </div>
                      </div>
                      <div className={`text-sm font-medium ${getMatchColor(match.similarity_score)}`}>
                        {Math.round(match.similarity_score * 100)}%
                      </div>
                    </div>
                    <div className="mt-1 text-xs text-blue-600">{match.match_reason}</div>
                    <div className="mt-1 text-xs text-blue-500">
                      {match.mapping_count} mappings • Created by {match.created_by}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* All Configurations */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
              <FileText className="w-4 h-4 mr-1" />
              All Configurations ({configs.length})
            </h4>
            {loading ? (
              <div className="flex items-center justify-center py-4">
                <Loader className="w-4 h-4 animate-spin mr-2" />
                <span className="text-sm text-gray-500">Loading configurations...</span>
              </div>
            ) : (
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {configs.map((config) => (
                  <div
                    key={config.id}
                    className="p-3 bg-gray-50 border border-gray-200 rounded-md hover:bg-gray-100 cursor-pointer"
                    onClick={() => handleConfigSelect(config.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{config.name}</div>
                        <div className="text-xs text-gray-600">{config.staging_table_name}</div>
                      </div>
                      <div className="text-xs text-gray-500">
                        {config.mapping_count} mappings
                      </div>
                    </div>
                    {config.description && (
                      <div className="mt-1 text-xs text-gray-500">{config.description}</div>
                    )}
                    <div className="mt-1 text-xs text-gray-400">
                      Created by {config.created_by} • {new Date(config.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Selected Configuration Details */}
      {selectedConfig && (
        <div className="mt-4 p-3 bg-purple-50 border border-purple-200 rounded-md">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium text-purple-900">Selected Configuration</h4>
            <button
              onClick={() => setSelectedConfig(null)}
              className="text-xs text-purple-600 hover:text-purple-800"
            >
              Clear
            </button>
          </div>
          <div className="text-sm text-purple-800">
            <div className="font-medium">{selectedConfig.name}</div>
            <div className="text-xs text-purple-600">{selectedConfig.staging_table_name}</div>
            {selectedConfig.description && (
              <div className="text-xs text-purple-600 mt-1">{selectedConfig.description}</div>
            )}
            <div className="text-xs text-purple-500 mt-1">
              {selectedConfig.column_mappings?.length || 0} column mappings
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StagingConfigManager; 