import React, { useState, useEffect, useRef } from 'react';
import { Search, Database, Plus, Check } from 'lucide-react';
import api from '../api/axios';
import toast from 'react-hot-toast';

const StagingTableAutocomplete = ({ 
  value, 
  onChange, 
  onTableSelect,
  realTimeSearch = true,
  placeholder = "Search or type table name...",
  className = ""
}) => {
  const [suggestions, setSuggestions] = useState([]);
  const [searching, setSearching] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const searchTimeoutRef = useRef(null);
  const inputRef = useRef(null);
  
  // Real-time search as user types
  const handleInputChange = async (inputValue) => {
    onChange(inputValue);
    
    if (realTimeSearch && inputValue.length >= 2) {
      // Clear previous timeout
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
      
      // Debounce search to avoid too many API calls
      searchTimeoutRef.current = setTimeout(async () => {
        setSearching(true);
        try {
          console.log('Searching for tables with query:', inputValue);
          
          // Try the simple endpoint first for testing
          const response = await api.post('/admin/staging/search-tables-simple', {
            query: inputValue,
            limit: 10
          });
          
          console.log('Search response:', response.data);
          setSuggestions(response.data.suggestions || []);
          setShowSuggestions(true);
          setSelectedIndex(-1);
        } catch (error) {
          console.error('Table search failed:', error);
          console.error('Error details:', error.response?.data);
          
          // Show user-friendly error message
          if (error.response?.status === 404) {
            toast.error('Search endpoint not found. Please restart the backend server.');
          } else {
            toast.error('Failed to search tables: ' + (error.response?.data?.detail || error.message));
          }
          
          // Set empty suggestions to show "no results" state
          setSuggestions([]);
          setShowSuggestions(false);
        } finally {
          setSearching(false);
        }
      }, 300); // 300ms debounce
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };
  
  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (!showSuggestions || suggestions.length === 0) return;
    
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev > 0 ? prev - 1 : suggestions.length - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          handleSuggestionSelect(suggestions[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setSelectedIndex(-1);
        inputRef.current?.blur();
        break;
    }
  };
  
  // Handle suggestion selection
  const handleSuggestionSelect = (suggestion) => {
    onChange(suggestion.name);
    onTableSelect(suggestion);
    setShowSuggestions(false);
    setSelectedIndex(-1);
    setSuggestions([]);
  };
  
  // Handle input focus/blur
  const handleFocus = () => {
    if (suggestions.length > 0) {
      setShowSuggestions(true);
    }
  };
  
  const handleBlur = () => {
    // Delay hiding suggestions to allow for clicks
    setTimeout(() => {
      setShowSuggestions(false);
      setSelectedIndex(-1);
    }, 200);
  };
  
  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, []);
  
  const getSuggestionIcon = (type) => {
    switch (type) {
      case 'existing':
        return <Database className="w-4 h-4 text-blue-500" />;
      case 'ai_suggested':
        return <Plus className="w-4 h-4 text-green-500" />;
      default:
        return <Database className="w-4 h-4 text-gray-400" />;
    }
  };
  
  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-gray-500';
  };
  
  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <input
          ref={inputRef}
          value={value}
          onChange={(e) => handleInputChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={placeholder}
          className="w-full px-3 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
        <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
        {searching && (
          <div className="absolute right-3 top-2.5">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
          </div>
        )}
      </div>
      
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {suggestions.map((suggestion, index) => (
            <div
              key={index}
              onClick={() => handleSuggestionSelect(suggestion)}
              className={`px-3 py-2 cursor-pointer flex items-center justify-between ${
                index === selectedIndex 
                  ? 'bg-blue-50 border-l-4 border-blue-500' 
                  : 'hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center space-x-3 flex-1">
                {getSuggestionIcon(suggestion.type)}
                <div className="flex-1">
                  <div className="font-medium text-gray-900">
                    {suggestion.name}
                  </div>
                  <div className="text-sm text-gray-600">
                    {suggestion.description}
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`text-xs font-medium ${getConfidenceColor(suggestion.confidence)}`}>
                  {Math.round(suggestion.confidence * 100)}%
                </span>
                {suggestion.type === 'existing' && (
                  <Check className="w-4 h-4 text-green-500" />
                )}
              </div>
            </div>
          ))}
        </div>
      )}
      
      {showSuggestions && suggestions.length === 0 && !searching && value.length >= 2 && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg p-3">
          <div className="text-sm text-gray-500 text-center">
            No tables found. Type to create a new table name.
          </div>
        </div>
      )}
    </div>
  );
};

export default StagingTableAutocomplete; 