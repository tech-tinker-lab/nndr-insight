import React, { useState, useEffect } from 'react';
import { 
  Search, 
  MapPin, 
  Globe, 
  Building2, 
  Navigation,
  Filter,
  Download,
  Eye,
  Map
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import InteractiveMap from '../components/Map/InteractiveMap';
import SimpleInteractiveMap from '../components/Map/SimpleInteractiveMap';

const API_BASE_URL = 'http://localhost:8000/api';

export default function Geospatial() {
  const [activeTab, setActiveTab] = useState('geocode');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [testMapRef, setTestMapRef] = useState(null);

  // Geocoding state
  const [geocodeQuery, setGeocodeQuery] = useState('');
  const [geocodeLimit, setGeocodeLimit] = useState(10);

  // Property search state
  const [searchType, setSearchType] = useState('postcode');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLimit, setSearchLimit] = useState(50);

  // Spatial query state
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [radius, setRadius] = useState(1000);
  const [selectedDatasets, setSelectedDatasets] = useState(['uprn', 'names']);

  // Test map initialization
  useEffect(() => {
    if (activeTab === 'map') {
      // Wait for DOM to be ready
      setTimeout(() => {
        const testMapElement = document.getElementById('test-map');
        if (testMapElement) {
          console.log('Initializing test map...');
          try {
            const L = require('leaflet');
            
            // Clear any existing map
            testMapElement.innerHTML = '';
            
            const map = L.map(testMapElement).setView([51.505, -0.09], 13);
            
            // Try CartoDB tiles
            L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
              attribution: '© CartoDB',
              maxZoom: 19,
              minZoom: 1,
              subdomains: ['a', 'b', 'c', 'd']
            }).addTo(map);
            
            // Add a test marker
            L.marker([51.5, -0.09]).addTo(map)
              .bindPopup('<b>Test!</b><br />Map is working.').openPopup();
            
            console.log('Test map created successfully');
          } catch (error) {
            console.error('Test map error:', error);
          }
        }
      }, 500);
    }
  }, [activeTab]);

  const handleGeocode = async () => {
    if (!geocodeQuery.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    setLoading(true);
    try {
      console.log('Starting geocoding search...');
      const response = await axios.post(`${API_BASE_URL}/geospatial/geocode`, {
        query: geocodeQuery,
        limit: geocodeLimit
      });
      console.log('Geocoding results:', response.data);
      setResults(response.data);
      toast.success(`Found ${response.data.total_found} results`);
    } catch (error) {
      console.error('Geocoding error:', error);
      toast.error('Failed to geocode address');
    } finally {
      setLoading(false);
    }
  };

  const handlePropertySearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    setLoading(true);
    try {
      console.log('Starting property search...');
      const searchData = {};
      if (searchType === 'postcode') {
        searchData.postcode = searchQuery;
      } else if (searchType === 'address') {
        searchData.address = searchQuery;
      } else if (searchType === 'uprn') {
        searchData.uprn = parseInt(searchQuery);
      }
      searchData.limit = searchLimit;

      const response = await axios.post(`${API_BASE_URL}/geospatial/search`, searchData);
      console.log('Property search results:', response.data);
      setResults(response.data);
      toast.success(`Found ${response.data.total_found} results`);
    } catch (error) {
      console.error('Search error:', error);
      toast.error('Failed to search properties');
    } finally {
      setLoading(false);
    }
  };

  const handleSpatialQuery = async () => {
    if (!latitude || !longitude) {
      toast.error('Please enter latitude and longitude');
      return;
    }

    setLoading(true);
    try {
      console.log('Starting spatial query...');
      const response = await axios.post(`${API_BASE_URL}/geospatial/spatial`, {
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
        radius_meters: radius,
        datasets: selectedDatasets
      });
      console.log('Spatial query results:', response.data);
      setResults(response.data);
      toast.success('Spatial query completed');
    } catch (error) {
      console.error('Spatial query error:', error);
      toast.error('Failed to perform spatial query');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'geocode', name: 'Geocoding', icon: Globe },
    { id: 'search', name: 'Property Search', icon: Search },
    { id: 'spatial', name: 'Spatial Query', icon: MapPin },
    { id: 'map', name: 'Interactive Map', icon: Map }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Geospatial Tools</h1>
        <p className="mt-1 text-sm text-gray-500">
          Geocode addresses, search properties, and perform spatial queries
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'map' ? (
        // Full-width map view
        <div className="space-y-4">
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Interactive Map</h3>
            <p className="text-sm text-gray-600 mb-4">
              Use the geocoding, property search, or spatial query tools above to see results on the map.
            </p>
            
            {/* Interactive Map Component */}
            <SimpleInteractiveMap 
              results={results}
              center={[51.505, -0.09]} // London center
              zoom={10}
              height="600px"
            />
            
            {/* Test Map */}
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Test Map (Debug)</h4>
              <div 
                id="test-map"
                style={{ height: '200px', width: '100%' }}
                className="border border-gray-300 rounded"
              />
            </div>
            
            {results && (
              <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-800">
                  Found {results.total_found || Object.keys(results.results || {}).length} results
                </p>
              </div>
            )}
          </div>
        </div>
      ) : (
        // Original layout for other tabs
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {activeTab === 'geocode' && 'Geocode Address'}
                {activeTab === 'search' && 'Search Properties'}
                {activeTab === 'spatial' && 'Spatial Query'}
              </h3>

              {activeTab === 'geocode' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Address or Postcode
                    </label>
                    <input
                      type="text"
                      value={geocodeQuery}
                      onChange={(e) => setGeocodeQuery(e.target.value)}
                      placeholder="Enter address or postcode..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Limit Results
                    </label>
                    <input
                      type="number"
                      value={geocodeLimit}
                      onChange={(e) => setGeocodeLimit(parseInt(e.target.value))}
                      min="1"
                      max="100"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <button
                    onClick={handleGeocode}
                    disabled={loading}
                    className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    {loading ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <>
                        <Globe className="w-4 h-4 mr-2" />
                        Geocode
                      </>
                    )}
                  </button>
                </div>
              )}

              {activeTab === 'search' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Search Type
                    </label>
                    <select
                      value={searchType}
                      onChange={(e) => setSearchType(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="postcode">Postcode</option>
                      <option value="address">Address</option>
                      <option value="uprn">UPRN</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Search Query
                    </label>
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder={`Enter ${searchType}...`}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Limit Results
                    </label>
                    <input
                      type="number"
                      value={searchLimit}
                      onChange={(e) => setSearchLimit(parseInt(e.target.value))}
                      min="1"
                      max="1000"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <button
                    onClick={handlePropertySearch}
                    disabled={loading}
                    className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    {loading ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <>
                        <Search className="w-4 h-4 mr-2" />
                        Search
                      </>
                    )}
                  </button>
                </div>
              )}

              {activeTab === 'spatial' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Latitude
                      </label>
                      <input
                        type="number"
                        step="any"
                        value={latitude}
                        onChange={(e) => setLatitude(e.target.value)}
                        placeholder="51.5074"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Longitude
                      </label>
                      <input
                        type="number"
                        step="any"
                        value={longitude}
                        onChange={(e) => setLongitude(e.target.value)}
                        placeholder="-0.1278"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Radius (meters)
                    </label>
                    <input
                      type="number"
                      value={radius}
                      onChange={(e) => setRadius(parseInt(e.target.value))}
                      min="100"
                      max="10000"
                      step="100"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Datasets
                    </label>
                    <div className="space-y-2">
                      {['uprn', 'names', 'map_local'].map((dataset) => (
                        <label key={dataset} className="flex items-center">
                          <input
                            type="checkbox"
                            checked={selectedDatasets.includes(dataset)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedDatasets([...selectedDatasets, dataset]);
                              } else {
                                setSelectedDatasets(selectedDatasets.filter(d => d !== dataset));
                              }
                            }}
                            className="mr-2"
                          />
                          <span className="text-sm text-gray-700 capitalize">{dataset.replace('_', ' ')}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                  <button
                    onClick={handleSpatialQuery}
                    disabled={loading}
                    className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    {loading ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <>
                        <MapPin className="w-4 h-4 mr-2" />
                        Query
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2">
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Results</h3>
                {results && (
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500">
                      {results.total_found || Object.keys(results.results || {}).length} results
                    </span>
                    <button 
                      className="text-blue-600 hover:text-blue-700 p-1 rounded"
                      title="View on map"
                      onClick={() => setActiveTab('map')}
                    >
                      <Map className="w-4 h-4" />
                    </button>
                    <button className="text-blue-600 hover:text-blue-700">
                      <Download className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>

              {!results && !loading && (
                <div className="text-center py-12">
                  <Globe className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No results</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Perform a search to see results here
                  </p>
                </div>
              )}

              {loading && (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              )}

              {results && !loading && (
                <div className="space-y-4">
                  {/* Map preview for results */}
                  <div className="bg-gray-50 rounded-lg p-4 mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-medium text-gray-900">Map Preview</h4>
                      <button 
                        onClick={() => setActiveTab('map')}
                        className="text-blue-600 hover:text-blue-700 text-sm"
                      >
                        View Full Map →
                      </button>
                    </div>
                    <SimpleInteractiveMap 
                      results={results}
                      center={[51.505, -0.09]}
                      zoom={10}
                      height="200px"
                    />
                  </div>

                  {activeTab === 'geocode' && results.results && (
                    <div className="space-y-3">
                      {results.results.map((result, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900">{result.name}</h4>
                              <p className="text-sm text-gray-500">{result.type} • {result.source}</p>
                              {result.longitude && result.latitude && (
                                <p className="text-sm text-gray-500">
                                  {result.longitude.toFixed(6)}, {result.latitude.toFixed(6)}
                                </p>
                              )}
                              {result.populated_place && (
                                <p className="text-sm text-gray-500">{result.populated_place}</p>
                              )}
                            </div>
                            <button className="text-blue-600 hover:text-blue-700">
                              <Eye className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {activeTab === 'search' && results.results && (
                    <div className="space-y-3">
                      {results.results.map((result, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900">
                                {result.uprn || result.postcode || result.os_id}
                              </h4>
                              <p className="text-sm text-gray-500">{result.source}</p>
                              {result.longitude && result.latitude && (
                                <p className="text-sm text-gray-500">
                                  {result.longitude.toFixed(6)}, {result.latitude.toFixed(6)}
                                </p>
                              )}
                              {result.local_authority && (
                                <p className="text-sm text-gray-500">{result.local_authority}</p>
                              )}
                            </div>
                            <button className="text-blue-600 hover:text-blue-700">
                              <Eye className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {activeTab === 'spatial' && results.results && (
                    <div className="space-y-4">
                      {Object.entries(results.results).map(([dataset, data]) => (
                        <div key={dataset} className="border border-gray-200 rounded-lg p-4">
                          <h4 className="font-medium text-gray-900 mb-3 capitalize">
                            {dataset.replace('_', ' ')} ({data.length})
                          </h4>
                          <div className="space-y-2">
                            {data.slice(0, 5).map((item, index) => (
                              <div key={index} className="text-sm text-gray-600">
                                {item.uprn || item.name1 || item.fid} 
                                {item.distance_meters && ` (${item.distance_meters.toFixed(0)}m)`}
                              </div>
                            ))}
                            {data.length > 5 && (
                              <p className="text-sm text-gray-500">
                                ... and {data.length - 5} more
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 