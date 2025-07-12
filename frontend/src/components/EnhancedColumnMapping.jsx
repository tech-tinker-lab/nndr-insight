import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  Sparkles, 
  Database,
  Info,
  Warning,
  ArrowRight,
  Settings,
  RefreshCw,
  X,
  Trash2
} from 'lucide-react';

const EnhancedColumnMapping = ({ 
  mappings = [], 
  onMappingsChange,
  matchStatus = null,
  suggestions = [],
  className = ""
}) => {
  const [localMappings, setLocalMappings] = useState(mappings);
  const [showDetails, setShowDetails] = useState({});

  useEffect(() => {
    setLocalMappings(mappings);
  }, [mappings]);

  const updateMapping = (id, updates) => {
    const newMappings = localMappings.map(m => 
      m.id === id ? { ...m, ...updates } : m
    );
    setLocalMappings(newMappings);
    if (onMappingsChange) {
      onMappingsChange(newMappings);
    }
  };

  const deleteMapping = (id) => {
    const mapping = localMappings.find(m => m.id === id);
    const mappingName = mapping?.sourceColumn || 'this mapping';
    
    if (window.confirm(`Are you sure you want to delete the mapping for "${mappingName}"?`)) {
      const newMappings = localMappings.filter(m => m.id !== id);
      setLocalMappings(newMappings);
      if (onMappingsChange) {
        onMappingsChange(newMappings);
      }
    }
  };

  const getMatchStatusIcon = (status) => {
    switch (status) {
      case 'exact':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'partial':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      case 'semantic':
        return <Clock className="w-4 h-4 text-blue-500" />;
      case 'suggested':
        return <Sparkles className="w-4 h-4 text-purple-500" />;
      case 'new_table':
        return <Database className="w-4 h-4 text-indigo-500" />;
      case 'unmatched':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Info className="w-4 h-4 text-gray-400" />;
    }
  };

  const getMatchStatusColor = (status) => {
    switch (status) {
      case 'exact':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'partial':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'semantic':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'suggested':
        return 'bg-purple-50 border-purple-200 text-purple-800';
      case 'new_table':
        return 'bg-indigo-50 border-indigo-200 text-indigo-800';
      case 'unmatched':
        return 'bg-red-50 border-red-200 text-red-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    if (confidence >= 0.4) return 'text-blue-600';
    return 'text-red-600';
  };

  const getMatchStatusText = (status) => {
    switch (status) {
      case 'exact':
        return 'Exact Match';
      case 'partial':
        return 'Partial Match';
      case 'semantic':
        return 'Semantic Match';
      case 'suggested':
        return 'AI Suggested';
      case 'new_table':
        return 'New Table';
      case 'unmatched':
        return 'Unmatched';
      default:
        return 'Unknown';
    }
  };

  const toggleDetails = (id) => {
    setShowDetails(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Overall Match Status */}
      {matchStatus && (
        <div className={`p-3 rounded-lg border ${getMatchStatusColor(matchStatus.status)}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {getMatchStatusIcon(matchStatus.status)}
              <span className="font-medium">{matchStatus.message}</span>
            </div>
            <div className={`text-sm font-medium ${getConfidenceColor(matchStatus.confidence)}`}>
              {Math.round(matchStatus.confidence * 100)}% confidence
            </div>
          </div>
        </div>
      )}

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <Info className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-800">AI Suggestions</span>
          </div>
          <div className="space-y-1">
            {suggestions.map((suggestion, index) => (
              <div key={index} className="text-xs text-blue-700">
                • {suggestion.message}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Column Mappings */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-medium text-gray-900">Column Mappings</h4>
          <div className="flex items-center space-x-3">
            <div className="text-xs text-gray-500">
              {localMappings.filter(m => m.matchStatus === 'exact').length} exact matches
            </div>
            {localMappings.length > 0 && (
              <button
                onClick={() => {
                  if (window.confirm(`Are you sure you want to remove all ${localMappings.length} mappings?`)) {
                    setLocalMappings([]);
                    if (onMappingsChange) {
                      onMappingsChange([]);
                    }
                  }
                }}
                className="text-xs text-red-600 hover:text-red-800 hover:bg-red-50 px-2 py-1 rounded transition-colors"
                title="Remove all mappings"
              >
                <Trash2 className="w-3 h-3 inline mr-1" />
                Remove All
              </button>
            )}
          </div>
        </div>
        
        {localMappings.map((mapping) => (
          <div
            key={mapping.id}
            className={`p-3 rounded-lg border transition-all duration-200 ${
              getMatchStatusColor(mapping.matchStatus)
            }`}
          >
            <div className="flex items-center space-x-3">
              {/* Status Icon */}
              <div className="flex-shrink-0">
                {getMatchStatusIcon(mapping.matchStatus)}
              </div>

              {/* Source Column */}
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-gray-900">
                  {mapping.sourceColumn}
                </div>
                <div className="text-xs text-gray-500">
                  Source column
                </div>
              </div>

              {/* Arrow */}
              <div className="flex-shrink-0">
                <ArrowRight className="w-4 h-4 text-gray-400" />
              </div>

              {/* Target Column */}
              <div className="flex-1 min-w-0">
                <input
                  type="text"
                  value={mapping.targetColumn}
                  onChange={(e) => updateMapping(mapping.id, { targetColumn: e.target.value })}
                  className={`w-full px-2 py-1 text-sm border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    mapping.matchStatus === 'exact' ? 'bg-green-50 border-green-300' :
                    mapping.matchStatus === 'partial' ? 'bg-yellow-50 border-yellow-300' :
                    mapping.matchStatus === 'semantic' ? 'bg-blue-50 border-blue-300' :
                    mapping.matchStatus === 'suggested' ? 'bg-purple-50 border-purple-300' :
                    mapping.matchStatus === 'new_table' ? 'bg-indigo-50 border-indigo-300' :
                    'bg-red-50 border-red-300'
                  }`}
                  placeholder="Target column name"
                />
                <div className="text-xs text-gray-500 mt-1">
                  Target column
                </div>
              </div>

              {/* Data Type */}
              <div className="flex-shrink-0 w-24">
                <select
                  value={mapping.dataType}
                  onChange={(e) => updateMapping(mapping.id, { dataType: e.target.value })}
                  className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="text">Text</option>
                  <option value="integer">Integer</option>
                  <option value="decimal">Decimal</option>
                  <option value="date">Date</option>
                  <option value="timestamp">Timestamp</option>
                  <option value="boolean">Boolean</option>
                  <option value="geometry">Geometry</option>
                </select>
              </div>

              {/* Confidence */}
              <div className="flex-shrink-0 w-16 text-center">
                <div className={`text-xs font-medium ${getConfidenceColor(mapping.confidence)}`}>
                  {Math.round(mapping.confidence * 100)}%
                </div>
                <div className="text-xs text-gray-500">Confidence</div>
              </div>

              {/* Details Toggle */}
              <div className="flex-shrink-0">
                <button
                  onClick={() => toggleDetails(mapping.id)}
                  className="text-gray-400 hover:text-gray-600 mr-1"
                  title="Settings"
                >
                  <Settings className="w-4 h-4" />
                </button>
              </div>

              {/* Delete Button */}
              <div className="flex-shrink-0">
                <button
                  onClick={() => deleteMapping(mapping.id)}
                  className="text-red-400 hover:text-red-600 hover:bg-red-50 p-1 rounded transition-colors"
                  title="Delete mapping"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Match Status Badge */}
            <div className="mt-2 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                  mapping.matchStatus === 'exact' ? 'bg-green-100 text-green-800' :
                  mapping.matchStatus === 'partial' ? 'bg-yellow-100 text-yellow-800' :
                  mapping.matchStatus === 'semantic' ? 'bg-blue-100 text-blue-800' :
                  mapping.matchStatus === 'suggested' ? 'bg-purple-100 text-purple-800' :
                  mapping.matchStatus === 'new_table' ? 'bg-indigo-100 text-indigo-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {getMatchStatusText(mapping.matchStatus)}
                </span>
                {mapping.isRequired && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    Required
                  </span>
                )}
              </div>
              {mapping.reason && (
                <div className="text-xs text-gray-500 max-w-xs truncate">
                  {mapping.reason}
                </div>
              )}
            </div>

            {/* Expanded Details */}
            {showDetails[mapping.id] && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <div className="grid grid-cols-2 gap-4">
                  {/* Required Field */}
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={mapping.isRequired}
                      onChange={(e) => updateMapping(mapping.id, { isRequired: e.target.checked })}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <label className="text-xs text-gray-700">Required field</label>
                  </div>

                  {/* Default Value */}
                  <div>
                    <label className="block text-xs text-gray-700 mb-1">Default Value</label>
                    <input
                      type="text"
                      value={mapping.defaultValue || ''}
                      onChange={(e) => updateMapping(mapping.id, { defaultValue: e.target.value })}
                      className="w-full px-2 py-1 text-xs border border-gray-300 rounded"
                      placeholder="Default value"
                    />
                  </div>

                  {/* Mapping Type */}
                  <div>
                    <label className="block text-xs text-gray-700 mb-1">Mapping Type</label>
                    <select
                      value={mapping.mappingType}
                      onChange={(e) => updateMapping(mapping.id, { mappingType: e.target.value })}
                      className="w-full px-2 py-1 text-xs border border-gray-300 rounded"
                    >
                      <option value="direct">Direct</option>
                      <option value="merge">Merge</option>
                      <option value="default">Default</option>
                      <option value="transform">Transform</option>
                      <option value="conditional">Conditional</option>
                    </select>
                  </div>

                  {/* Confidence Details */}
                  <div>
                    <label className="block text-xs text-gray-700 mb-1">Confidence</label>
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            mapping.confidence >= 0.8 ? 'bg-green-500' :
                            mapping.confidence >= 0.6 ? 'bg-yellow-500' :
                            mapping.confidence >= 0.4 ? 'bg-blue-500' :
                            'bg-red-500'
                          }`}
                          style={{ width: `${mapping.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-600">
                        {Math.round(mapping.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="p-3 bg-gray-50 rounded-lg">
        <div className="grid grid-cols-5 gap-4 text-center">
          <div>
            <div className="text-lg font-semibold text-green-600">
              {localMappings.filter(m => m.matchStatus === 'exact').length}
            </div>
            <div className="text-xs text-gray-600">Exact Matches</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-yellow-600">
              {localMappings.filter(m => m.matchStatus === 'partial').length}
            </div>
            <div className="text-xs text-gray-600">Partial Matches</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-blue-600">
              {localMappings.filter(m => m.matchStatus === 'semantic').length}
            </div>
            <div className="text-xs text-gray-600">Semantic Matches</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-purple-600">
              {localMappings.filter(m => m.matchStatus === 'suggested').length}
            </div>
            <div className="text-xs text-gray-600">AI Suggested</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-indigo-600">
              {localMappings.filter(m => m.matchStatus === 'new_table').length}
            </div>
            <div className="text-xs text-gray-600">New Table</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedColumnMapping; 