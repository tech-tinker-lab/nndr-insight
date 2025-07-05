import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const SimpleInteractiveMap = ({ 
  results, 
  center = [51.505, -0.09], 
  zoom = 13, 
  height = '400px'
}) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef([]);

  useEffect(() => {
    // Initialize map
    if (!mapInstanceRef.current && mapRef.current) {
      try {
        console.log('Initializing simple map...');
        mapInstanceRef.current = L.map(mapRef.current).setView(center, zoom);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors'
        }).addTo(mapInstanceRef.current);
        
        console.log('Simple map initialized successfully');
      } catch (error) {
        console.error('Error initializing simple map:', error);
      }
    }

    // Clear existing markers
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    // Add markers based on results
    if (results && mapInstanceRef.current) {
      let markers = [];
      let bounds = null;

      if (results.results && Array.isArray(results.results)) {
        // Handle geocoding and property search results
        results.results.forEach((result, index) => {
          if (result.latitude && result.longitude) {
            const marker = L.marker([result.latitude, result.longitude])
              .bindPopup(`
                <div class="p-2">
                  <h3 class="font-bold">${result.name || result.uprn || result.postcode || 'Location'}</h3>
                  <p class="text-sm">${result.type || result.source || ''}</p>
                  <p class="text-sm">${result.longitude.toFixed(6)}, ${result.latitude.toFixed(6)}</p>
                  ${result.populated_place ? `<p class="text-sm">${result.populated_place}</p>` : ''}
                  ${result.local_authority ? `<p class="text-sm">${result.local_authority}</p>` : ''}
                </div>
              `);
            
            marker.addTo(mapInstanceRef.current);
            markers.push(marker);
            
            if (!bounds) {
              bounds = L.latLngBounds([result.latitude, result.longitude]);
            } else {
              bounds.extend([result.latitude, result.longitude]);
            }
          }
        });
      } else if (results.results && typeof results.results === 'object') {
        // Handle spatial query results
        Object.entries(results.results).forEach(([dataset, data]) => {
          if (Array.isArray(data)) {
            data.forEach((item, index) => {
              if (item.latitude && item.longitude) {
                const marker = L.marker([item.latitude, item.longitude])
                  .bindPopup(`
                    <div class="p-2">
                      <h3 class="font-bold">${item.uprn || item.name1 || item.fid || 'Location'}</h3>
                      <p class="text-sm">${dataset.replace('_', ' ')}</p>
                      <p class="text-sm">${item.longitude.toFixed(6)}, ${item.latitude.toFixed(6)}</p>
                      ${item.distance_meters ? `<p class="text-sm">Distance: ${item.distance_meters.toFixed(0)}m</p>` : ''}
                    </div>
                  `);
                
                marker.addTo(mapInstanceRef.current);
                markers.push(marker);
                
                if (!bounds) {
                  bounds = L.latLngBounds([item.latitude, item.longitude]);
                } else {
                  bounds.extend([item.latitude, item.longitude]);
                }
              }
            });
          }
        });
      }

      markersRef.current = markers;

      // Fit map to show all markers if we have any
      if (bounds && markers.length > 0) {
        try {
          mapInstanceRef.current.fitBounds(bounds, { padding: [20, 20] });
        } catch (error) {
          console.error('Error fitting bounds:', error);
          // Fallback to center on first marker
          if (markers.length > 0) {
            const firstMarker = markers[0];
            const pos = firstMarker.getLatLng();
            mapInstanceRef.current.setView(pos, 15);
          }
        }
      }
    }

    return () => {
      // Cleanup markers
      markersRef.current.forEach(marker => marker.remove());
    };
  }, [results, center, zoom]);

  return (
    <div 
      ref={mapRef} 
      style={{ height, width: '100%' }}
      className="rounded-lg border border-gray-200"
    />
  );
};

export default SimpleInteractiveMap; 