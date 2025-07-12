import React, { useState, useEffect } from 'react';
import { 
  Save, 
  Check, 
  Info, 
  Upload, 
  Brain, 
  Settings, 
  Clock,
  Star,
  AlertCircle,
  ChevronRight,
  X
} from 'lucide-react';
import api from '../api/axios';

const API_BASE_URL = 'http://localhost:8000/api';

const UploadActionSuggestions = ({ 
  file, 
  headers, 
  onAction, 
  onClose,
  onSaveConfig,
  onUseExistingConfig 
}) => {
  const [suggestions, setSuggestions] = useState([]);
  const [existingConfigs, setExistingConfigs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (file && headers.length > 0) {
      fetchSuggestions();
    }
  }, [file, headers]);

  const fetchSuggestions = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.post(`${API_BASE_URL}/admin/staging/suggest-actions`, {
        headers: headers,
        file_name: file.name,
        file_type: file.type || 'unknown',
        content_preview: '' // Could be enhanced with actual content preview
      });

      setSuggestions(response.data.suggestions || []);
      setExistingConfigs(response.data.existing_configs || []);
    } catch (err) {
      console.error('Error fetching suggestions:', err);
      setError('Failed to load suggestions');
      
      // Fallback suggestions
      setSuggestions([
        {
          action: "save_config",
          title: "Save Configuration",
          description: "Save current mapping configuration for future use",
          priority: "high",
          icon: "save"
        },
        {
          action: "proceed_upload",
          title: "Proceed with Upload",
          description: "Continue with current configuration",
          priority: "low",
          icon: "upload"
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = (action, configId = null) => {
    switch (action) {
      case 'save_config':
        onSaveConfig && onSaveConfig();
        break;
      case 'use_existing':
        onUseExistingConfig && onUseExistingConfig(configId);
        break;
      case 'ai_analysis':
        onAction && onAction('ai_analysis');
        break;
      case 'proceed_upload':
        onAction && onAction('proceed_upload');
        break;
      default:
        onAction && onAction(action);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-green-600 bg-green-50 border-green-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-gray-600 bg-gray-50 border-gray-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'high': return <Star className="w-4 h-4 text-green-600" />;
      case 'medium': return <Info className="w-4 h-4 text-yellow-600" />;
      case 'low': return <Clock className="w-4 h-4 text-gray-600" />;
      default: return <Info className="w-4 h-4 text-gray-600" />;
    }
  };

  const getActionIcon = (icon) => {
    switch (icon) {
      case 'save': return <Save className="w-5 h-5" />;
      case 'check': return <Check className="w-5 h-5" />;
      case 'info': return <Info className="w-5 h-5" />;
      case 'upload': return <Upload className="w-5 h-5" />;
      case 'brain': return <Brain className="w-5 h-5" />;
      case 'settings': return <Settings className="w-5 h-5" />;
      default: return <ChevronRight className="w-5 h-5" />;
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading suggestions...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
        <div className="flex items-center justify-center py-8">
          <AlertCircle className="w-8 h-8 text-red-500" />
          <span className="ml-3 text-red-600">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Suggested Actions</h3>
          <p className="text-sm text-gray-600 mt-1">
            Based on your file "{file.name}" with {headers.length} columns
          </p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Action Suggestions */}
      <div className="space-y-3 mb-6">
        {suggestions.map((suggestion, index) => (
          <div
            key={index}
            className={`p-4 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md ${getPriorityColor(suggestion.priority)}`}
            onClick={() => handleAction(suggestion.action, suggestion.config_id)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  {getPriorityIcon(suggestion.priority)}
                  {getActionIcon(suggestion.icon)}
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">{suggestion.title}</h4>
                  <p className="text-sm text-gray-600">{suggestion.description}</p>
                </div>
              </div>
              <ChevronRight className="w-5 h-5 text-gray-400" />
            </div>
          </div>
        ))}
      </div>

      {/* Existing Configurations */}
      {existingConfigs.length > 0 && (
        <div className="border-t border-gray-200 pt-6">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Similar Existing Configurations</h4>
          <div className="space-y-2">
            {existingConfigs.slice(0, 3).map((config, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => handleAction('use_existing', config.config_id)}
              >
                <div>
                  <div className="font-medium text-gray-900">{config.config_name}</div>
                  <div className="text-sm text-gray-600">
                    {new Date(config.created_at).toLocaleDateString()} • {config.similarity.toFixed(1)}% match
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                    config.similarity > 0.7 ? 'bg-green-100 text-green-800' :
                    config.similarity > 0.5 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {config.similarity.toFixed(0)}%
                  </div>
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="border-t border-gray-200 pt-6 mt-6">
        <div className="flex space-x-3">
          <button
            onClick={() => handleAction('proceed_upload')}
            className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center space-x-2"
          >
            <Upload className="w-4 h-4" />
            <span>Proceed</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadActionSuggestions; 