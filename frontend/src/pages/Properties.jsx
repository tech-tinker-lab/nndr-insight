import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  MapPin, 
  Building2, 
  Home, 
  Mail, 
  Phone,
  Globe,
  Calendar,
  Star,
  Eye,
  Heart,
  Share2,
  Download,
  RefreshCw,
  AlertCircle,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = 'http://localhost:8000/api';

export default function Properties() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    region: '',
    propertyType: '',
    minUprns: '',
    maxUprns: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [selectedProperty, setSelectedProperty] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // grid or list

  useEffect(() => {
    fetchProperties();
  }, []);

  const fetchProperties = async (query = '', filterParams = {}) => {
    try {
      setLoading(true);
      setError(null);
      
      // Use the properties endpoint from tables router
      const params = new URLSearchParams();
      if (query) params.append('search', query);
      params.append('limit', '50'); // Get more properties per page
      params.append('skip', '0');

      const response = await axios.get(`${API_BASE_URL}/properties?${params}`);
      setProperties(response.data.items || []);
    } catch (err) {
      console.error('Error fetching properties:', err);
      setError('Failed to load properties');
      toast.error('Failed to load properties');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchProperties(searchQuery, filters);
  };

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    fetchProperties(searchQuery, newFilters);
  };

  const clearFilters = () => {
    setFilters({
      region: '',
      propertyType: '',
      minUprns: '',
      maxUprns: ''
    });
    setSearchQuery('');
    fetchProperties();
  };

  const PropertyCard = ({ property }) => (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {property.property_description || property.ba_reference}
            </h3>
            <div className="flex items-center text-sm text-gray-500 mb-2">
              <MapPin className="w-4 h-4 mr-1" />
              {property.property_address || 'Address not available'}
            </div>
            {property.postcode && (
              <div className="flex items-center text-sm text-gray-500 mb-2">
                <Mail className="w-4 h-4 mr-1" />
                {property.postcode}
              </div>
            )}
            {property.administrative_area && (
              <div className="flex items-center text-sm text-gray-500 mb-3">
                <Globe className="w-4 h-4 mr-1" />
                {property.administrative_area}
              </div>
            )}
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setSelectedProperty(property)}
              className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
              title="View details"
            >
              <Eye className="w-4 h-4" />
            </button>
            <button
              className="p-2 text-gray-400 hover:text-red-600 transition-colors"
              title="Add to favorites"
            >
              <Heart className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {property.ba_reference}
            </div>
            <div className="text-xs text-gray-500">BA Reference</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              £{property.rateable_value ? property.rateable_value.toLocaleString() : '0'}
            </div>
            <div className="text-xs text-gray-500">Rateable Value</div>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center text-sm text-gray-500">
            <Calendar className="w-4 h-4 mr-1" />
            {property.effective_date ? new Date(property.effective_date).toLocaleDateString() : 'N/A'}
          </div>
          <button
            onClick={() => setSelectedProperty(property)}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            View Details →
          </button>
        </div>
      </div>
    </div>
  );

  const PropertyListItem = ({ property }) => (
    <div className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 p-6">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Building2 className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-semibold text-gray-900 truncate">
                {property.property_description || property.ba_reference}
              </h3>
              <div className="flex items-center text-sm text-gray-500 mt-1">
                <MapPin className="w-4 h-4 mr-1" />
                {property.property_address || 'Address not available'}
                {property.postcode && (
                  <>
                    <span className="mx-2">•</span>
                    <Mail className="w-4 h-4 mr-1" />
                    {property.postcode}
                  </>
                )}
                {property.administrative_area && (
                  <>
                    <span className="mx-2">•</span>
                    <Globe className="w-4 h-4 mr-1" />
                    {property.administrative_area}
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-6">
          <div className="text-center">
            <div className="text-lg font-semibold text-blue-600">
              {property.ba_reference}
            </div>
            <div className="text-xs text-gray-500">BA Reference</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-green-600">
              £{property.rateable_value ? property.rateable_value.toLocaleString() : '0'}
            </div>
            <div className="text-xs text-gray-500">Rateable Value</div>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setSelectedProperty(property)}
              className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
              title="View details"
            >
              <Eye className="w-4 h-4" />
            </button>
            <button
              className="p-2 text-gray-400 hover:text-red-600 transition-colors"
              title="Add to favorites"
            >
              <Heart className="w-4 h-4" />
            </button>
            <button
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              title="Share"
            >
              <Share2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const PropertyDetailModal = ({ property, onClose }) => {
    if (!property) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                {property.property_description || property.ba_reference}
              </h2>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <span className="sr-only">Close</span>
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-6">
              {/* Basic Information */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Property Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center">
                    <Building2 className="w-5 h-5 text-gray-400 mr-3" />
                    <div>
                      <div className="text-sm font-medium text-gray-900">BA Reference</div>
                      <div className="text-sm text-gray-500">{property.ba_reference || 'N/A'}</div>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <MapPin className="w-5 h-5 text-gray-400 mr-3" />
                    <div>
                      <div className="text-sm font-medium text-gray-900">Address</div>
                      <div className="text-sm text-gray-500">{property.property_address || 'N/A'}</div>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <Mail className="w-5 h-5 text-gray-400 mr-3" />
                    <div>
                      <div className="text-sm font-medium text-gray-900">Postcode</div>
                      <div className="text-sm text-gray-500">{property.postcode || 'N/A'}</div>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <Globe className="w-5 h-5 text-gray-400 mr-3" />
                    <div>
                      <div className="text-sm font-medium text-gray-900">Administrative Area</div>
                      <div className="text-sm text-gray-500">{property.administrative_area || 'N/A'}</div>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <Home className="w-5 h-5 text-gray-400 mr-3" />
                    <div>
                      <div className="text-sm font-medium text-gray-900">Locality</div>
                      <div className="text-sm text-gray-500">{property.locality || 'N/A'}</div>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <Calendar className="w-5 h-5 text-gray-400 mr-3" />
                    <div>
                      <div className="text-sm font-medium text-gray-900">Effective Date</div>
                      <div className="text-sm text-gray-500">
                        {property.effective_date ? new Date(property.effective_date).toLocaleDateString() : 'N/A'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Financial Information */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Financial Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      £{property.rateable_value ? property.rateable_value.toLocaleString() : '0'}
                    </div>
                    <div className="text-sm text-gray-600">Rateable Value</div>
                  </div>
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {property.property_category_code || 'N/A'}
                    </div>
                    <div className="text-sm text-gray-600">Category Code</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {property.scat_code || 'N/A'}
                    </div>
                    <div className="text-sm text-gray-600">SCAT Code</div>
                  </div>
                </div>
              </div>

              {/* Additional Details */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Additional Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm font-medium text-gray-900">Community Code</div>
                    <div className="text-sm text-gray-500">{property.community_code || 'N/A'}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-900">Street Descriptor</div>
                    <div className="text-sm text-gray-500">{property.street_descriptor || 'N/A'}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-900">Post Town</div>
                    <div className="text-sm text-gray-500">{property.post_town || 'N/A'}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-900">Partially Domestic Signal</div>
                    <div className="text-sm text-gray-500">{property.partially_domestic_signal || 'N/A'}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-900">Appeal Settlement Code</div>
                    <div className="text-sm text-gray-500">{property.appeal_settlement_code || 'N/A'}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-900">Unique Property Ref</div>
                    <div className="text-sm text-gray-500">{property.unique_property_ref || 'N/A'}</div>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex space-x-3 pt-4 border-t border-gray-200">
                <button className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
                  <Download className="w-4 h-4 mr-2" />
                  Export Data
                </button>
                <button className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                  <Share2 className="w-4 h-4 mr-2" />
                  Share
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Properties</h1>
          <p className="mt-1 text-sm text-gray-500">
            Search and explore property data across the UK
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
            className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            {viewMode === 'grid' ? 'List View' : 'Grid View'}
          </button>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <Filter className="w-4 h-4 mr-2" />
            Filters
            {showFilters ? <ChevronUp className="w-4 h-4 ml-2" /> : <ChevronDown className="w-4 h-4 ml-2" />}
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="flex space-x-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search properties by address, postcode, or description..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
        <button
          type="submit"
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Search
        </button>
      </form>

      {/* Filters */}
      {showFilters && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Region</label>
              <select
                value={filters.region}
                onChange={(e) => handleFilterChange('region', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Regions</option>
                <option value="England">England</option>
                <option value="Scotland">Scotland</option>
                <option value="Wales">Wales</option>
                <option value="Northern Ireland">Northern Ireland</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Property Type</label>
              <select
                value={filters.propertyType}
                onChange={(e) => handleFilterChange('propertyType', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Types</option>
                <option value="residential">Residential</option>
                <option value="commercial">Commercial</option>
                <option value="industrial">Industrial</option>
                <option value="mixed">Mixed</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Min UPRNs</label>
              <input
                type="number"
                value={filters.minUprns}
                onChange={(e) => handleFilterChange('minUprns', e.target.value)}
                placeholder="0"
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Max UPRNs</label>
              <input
                type="number"
                value={filters.maxUprns}
                onChange={(e) => handleFilterChange('maxUprns', e.target.value)}
                placeholder="1000"
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          <div className="mt-4 flex justify-end">
            <button
              type="button"
              onClick={clearFilters}
              className="text-sm text-gray-600 hover:text-gray-800"
            >
              Clear all filters
            </button>
          </div>
        </div>
      )}

      {/* Results */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <AlertCircle className="mx-auto h-12 w-12 text-red-500" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading properties</h3>
              <p className="mt-1 text-sm text-gray-500">{error}</p>
              <button
                onClick={() => fetchProperties()}
                className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                Try again
              </button>
            </div>
          </div>
        ) : properties.length === 0 ? (
          <div className="text-center py-12">
            <Building2 className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No properties found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your search criteria or filters.
            </p>
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-700">
                Showing {properties.length} properties
              </p>
              <button
                onClick={() => fetchProperties(searchQuery, filters)}
                className="inline-flex items-center text-sm text-gray-600 hover:text-gray-800"
              >
                <RefreshCw className="w-4 h-4 mr-1" />
                Refresh
              </button>
            </div>

            {viewMode === 'grid' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {properties.map((property, index) => (
                  <PropertyCard key={index} property={property} />
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {properties.map((property, index) => (
                  <PropertyListItem key={index} property={property} />
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* Property Detail Modal */}
      {selectedProperty && (
        <PropertyDetailModal
          property={selectedProperty}
          onClose={() => setSelectedProperty(null)}
        />
      )}
    </div>
  );
} 