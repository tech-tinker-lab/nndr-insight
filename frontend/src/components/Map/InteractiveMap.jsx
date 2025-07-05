import React, { useEffect, useState, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in Leaflet
import L from 'leaflet';
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Component to handle map updates
function MapUpdater({ results, center, zoom }) {
  const map = useMap();

  const updateMapView = useCallback(() => {
    if (results && results.results) {
      let markers = [];

      if (Array.isArray(results.results)) {
        // Handle geocoding and property search results
        results.results.forEach((result) => {
          if (result.latitude && result.longitude) {
            markers.push([result.latitude, result.longitude]);
          }
        });
      } else if (typeof results.results === 'object') {
        // Handle spatial query results
        Object.entries(results.results).forEach(([dataset, data]) => {
          if (Array.isArray(data)) {
            data.forEach((item) => {
              if (item.latitude && item.longitude) {
                markers.push([item.latitude, item.longitude]);
              }
            });
          }
        });
      }

      // Fit map to show all markers if we have any
      if (markers.length > 0) {
        try {
          const bounds = L.latLngBounds(markers);
          map.fitBounds(bounds, { padding: [20, 20] });
        } catch (error) {
          console.error('Error fitting bounds:', error);
          // Fallback to center on first marker
          if (markers.length > 0) {
            map.setView(markers[0], 15);
          }
        }
      }
    }
  }, [results, map]);

  useEffect(() => {
    updateMapView();
  }, [updateMapView]);

  return null;
}

const InteractiveMap = ({ 
  results, 
  center = [51.505, -0.09], 
  zoom = 13, 
  height = '400px'
}) => {
  const [mapKey, setMapKey] = useState(0);

  // Force map re-render when results change significantly
  useEffect(() => {
    if (results && results.results) {
      setMapKey(prev => prev + 1);
    }
  }, [results]);

  const renderMarkers = () => {
    if (!results || !results.results) return null;

    if (Array.isArray(results.results)) {
      // Handle geocoding and property search results
      return results.results.map((result, index) => (
        result.latitude && result.longitude && (
          <Marker key={`result-${index}`} position={[result.latitude, result.longitude]}>
            <Popup>
              <div className="p-2">
                <h3 className="font-bold">{result.name || result.uprn || result.postcode || 'Location'}</h3>
                <p className="text-sm">{result.type || result.source || ''}</p>
                <p className="text-sm">{result.longitude.toFixed(6)}, {result.latitude.toFixed(6)}</p>
                {result.populated_place && <p className="text-sm">{result.populated_place}</p>}
                {result.local_authority && <p className="text-sm">{result.local_authority}</p>}
              </div>
            </Popup>
          </Marker>
        )
      ));
    } else if (typeof results.results === 'object') {
      // Handle spatial query results
      return Object.entries(results.results).map(([dataset, data]) => (
        Array.isArray(data) && data.map((item, index) => (
          item.latitude && item.longitude && (
            <Marker key={`${dataset}-${index}`} position={[item.latitude, item.longitude]}>
              <Popup>
                <div className="p-2">
                  <h3 className="font-bold">{item.uprn || item.name1 || item.fid || 'Location'}</h3>
                  <p className="text-sm">{dataset.replace('_', ' ')}</p>
                  <p className="text-sm">{item.longitude.toFixed(6)}, {item.latitude.toFixed(6)}</p>
                  {item.distance_meters && <p className="text-sm">Distance: {item.distance_meters.toFixed(0)}m</p>}
                </div>
              </Popup>
            </Marker>
          )
        ))
      ));
    }

    return null;
  };

  return (
    <div style={{ height, width: '100%' }} className="rounded-lg border border-gray-200">
      <MapContainer 
        key={mapKey}
        center={center} 
        zoom={zoom} 
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
        attributionControl={true}
        whenReady={() => console.log('Map is ready')}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapUpdater results={results} center={center} zoom={zoom} />
        
        {renderMarkers()}
      </MapContainer>
    </div>
  );
};

export default InteractiveMap; 