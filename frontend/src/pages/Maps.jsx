import React, { useState, useEffect, useRef } from 'react';
import { 
  MapPin, 
  Search, 
  Layers, 
  Filter, 
  Download, 
  Share2, 
  ZoomIn, 
  ZoomOut,
  Navigation,
  Globe,
  Building2,
  Home,
  AlertCircle,
  RefreshCw,
  Settings,
  Info,
  Crosshair
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = 'http://localhost:8000/api';

export default function Maps() {
  const [mapData, setMapData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [spatialQuery, setSpatialQuery] = useState({
    latitude: '',
    longitude: '',
    radius: '1000'
  });
  const [mapLayers, setMapLayers] = useState({
    boundaries: true,
    properties: true,
    postcodes: false,
    places: false
  });
  const [mapView, setMapView] = useState('default');
  const mapRef = useRef(null);

  useEffect(() => {
    initializeMap();
    fetchMapData();
  }, []);

  const initializeMap = () => {
    // Initialize map container
    if (mapRef.current) {
      // This would typically initialize a mapping library like Leaflet, Mapbox, or Google Maps
      // For now, we'll create a placeholder map interface
      console.log('Map initialized');
    }
  };

  const fetchMapData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch initial map data
      const response = await axios.get(`${API_BASE_URL}/geospatial/boundaries`);
      setMapData(response.data);
    } catch (err) {
      console.error('Error fetching map data:', err);
      setError('Failed to load map data');
      toast.error('Failed to load map data');
    } finally {
      setLoading(false);
    }
  };

  const handleLocationSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/geospatial/geocode?q=${encodeURIComponent(searchQuery)}`);
      
      if (response.data.results && response.data.results.length > 0) {
        const location = response.data.results[0];
        setSelectedLocation(location);
        // Here you would typically pan/zoom the map to the location
        toast.success(`Found: ${location.name}`);
      } else {
        toast.error('Location not found');
      }
    } catch (err) {
      console.error('Error searching location:', err);
      toast.error('Failed to search location');
    } finally {
      setLoading(false);
    }
  };

  const handleSpatialQuery = async (e) => {
    e.preventDefault();
    if (!spatialQuery.latitude || !spatialQuery.longitude) {
      toast.error('Please enter latitude and longitude');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/geospatial/spatial-query`, {
        params: {
          lat: spatialQuery.latitude,
          lon: spatialQuery.longitude,
          radius: spatialQuery.radius
        }
      });
      
      // Handle spatial query results
      console.log('Spatial query results:', response.data);
      toast.success(`Found ${response.data.features?.length || 0} features`);
    } catch (err) {
      console.error('Error performing spatial query:', err);
      toast.error('Failed to perform spatial query');
    } finally {
      setLoading(false);
    }
  };

  const toggleLayer = (layer) => {
    setMapLayers(prev => ({
      ...prev,
      [layer]: !prev[layer]
    }));
  };

  const MapControls = () => (
    <div className="absolute top-4 left-4 z-10 space-y-2">
      <div className="bg-white rounded-lg shadow-lg p-2">
        <button
          onClick={() => {/* Zoom in */}}
          className="w-8 h-8 flex items-center justify-center text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => {/* Zoom out */}}
          className="w-8 h-8 flex items-center justify-center text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
      </div>
      
      <div className="bg-white rounded-lg shadow-lg p-2">
        <button
          onClick={() => {/* Get current location */}}
          className="w-8 h-8 flex items-center justify-center text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
          title="My Location"
        >
          <Crosshair className="w-4 h-4" />
        </button>
      </div>
    </div>
  );

  const LayerPanel = () => (
    <div className="absolute top-4 right-4 z-10 bg-white rounded-lg shadow-lg p-4 w-64">
      <h3 className="text-sm font-medium text-gray-900 mb-3">Map Layers</h3>
      <div className="space-y-2">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={mapLayers.boundaries}
            onChange={() => toggleLayer('boundaries')}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700">Boundaries</span>
        </label>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={mapLayers.properties}
            onChange={() => toggleLayer('properties')}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700">Properties</span>
        </label>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={mapLayers.postcodes}
            onChange={() => toggleLayer('postcodes')}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700">Postcodes</span>
        </label>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={mapLayers.places}
            onChange={() => toggleLayer('places')}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700">Places</span>
        </label>
      </div>
    </div>
  );

  const SearchPanel = () => (
    <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10 bg-white rounded-lg shadow-lg p-4 w-96">
      <form onSubmit={handleLocationSearch} className="space-y-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search for a location..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>
    </div>
  );

  const SpatialQueryPanel = () => (
    <div className="absolute bottom-4 left-4 z-10 bg-white rounded-lg shadow-lg p-4 w-80">
      <h3 className="text-sm font-medium text-gray-900 mb-3">Spatial Query</h3>
      <form onSubmit={handleSpatialQuery} className="space-y-3">
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Latitude</label>
            <input
              type="number"
              step="any"
              value={spatialQuery.latitude}
              onChange={(e) => setSpatialQuery(prev => ({ ...prev, latitude: e.target.value }))}
              placeholder="51.5074"
              className="w-full px-3 py-1 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Longitude</label>
            <input
              type="number"
              step="any"
              value={spatialQuery.longitude}
              onChange={(e) => setSpatialQuery(prev => ({ ...prev, longitude: e.target.value }))}
              placeholder="-0.1278"
              className="w-full px-3 py-1 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Radius (meters)</label>
          <select
            value={spatialQuery.radius}
            onChange={(e) => setSpatialQuery(prev => ({ ...prev, radius: e.target.value }))}
            className="w-full px-3 py-1 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="100">100m</option>
            <option value="500">500m</option>
            <option value="1000">1km</option>
            <option value="5000">5km</option>
            <option value="10000">10km</option>
          </select>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full px-3 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {loading ? 'Querying...' : 'Query Area'}
        </button>
      </form>
    </div>
  );

  const MapInfoPanel = () => (
    <div className="absolute bottom-4 right-4 z-10 bg-white rounded-lg shadow-lg p-4 w-64">
      <h3 className="text-sm font-medium text-gray-900 mb-3">Map Information</h3>
      <div className="space-y-2 text-xs text-gray-600">
        <div className="flex justify-between">
          <span>Zoom Level:</span>
          <span>12</span>
        </div>
        <div className="flex justify-between">
          <span>Center:</span>
          <span>51.5074, -0.1278</span>
        </div>
        <div className="flex justify-between">
          <span>Active Layers:</span>
          <span>{Object.values(mapLayers).filter(Boolean).length}</span>
        </div>
        {selectedLocation && (
          <div className="pt-2 border-t border-gray-200">
            <div className="font-medium text-gray-900">Selected Location</div>
            <div className="text-gray-600">{selectedLocation.name}</div>
            <div className="text-gray-500">{selectedLocation.postcode}</div>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Interactive Maps</h1>
          <p className="mt-1 text-sm text-gray-500">
            Explore geospatial data with interactive mapping tools
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
            <Share2 className="w-4 h-4 mr-2" />
            Share
          </button>
          <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </button>
        </div>
      </div>

      {/* Map Container */}
      <div className="relative bg-gray-100 rounded-lg overflow-hidden" style={{ height: '70vh' }}>
        {/* Placeholder Map */}
        <div 
          ref={mapRef}
          className="w-full h-full bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center"
        >
          {loading ? (
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading map data...</p>
            </div>
          ) : error ? (
            <div className="text-center">
              <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
              <h3 className="text-sm font-medium text-gray-900 mb-2">Error loading map</h3>
              <p className="text-sm text-gray-500 mb-4">{error}</p>
              <button
                onClick={fetchMapData}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Try again
              </button>
            </div>
          ) : (
            <div className="text-center">
              <Globe className="mx-auto h-16 w-16 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Interactive Map</h3>
              <p className="text-gray-600 mb-4">
                This would display an interactive map with geospatial data
              </p>
              <div className="flex items-center justify-center space-x-4 text-sm text-gray-500">
                <div className="flex items-center">
                  <Building2 className="w-4 h-4 mr-1" />
                  Properties
                </div>
                <div className="flex items-center">
                  <MapPin className="w-4 h-4 mr-1" />
                  Boundaries
                </div>
                <div className="flex items-center">
                  <Home className="w-4 h-4 mr-1" />
                  Postcodes
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Map Controls */}
        <MapControls />
        
        {/* Layer Panel */}
        <LayerPanel />
        
        {/* Search Panel */}
        <SearchPanel />
        
        {/* Spatial Query Panel */}
        <SpatialQueryPanel />
        
        {/* Map Info Panel */}
        <MapInfoPanel />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Search className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Location Search</h3>
              <p className="text-sm text-gray-500">Find specific locations and addresses</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Navigation className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Spatial Queries</h3>
              <p className="text-sm text-gray-500">Query data within specific areas</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Layers className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Layer Management</h3>
              <p className="text-sm text-gray-500">Control map layers and data visibility</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 