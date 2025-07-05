import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const SimpleMap = () => {
  const mapRef = useRef(null);

  useEffect(() => {
    if (mapRef.current) {
      console.log('Creating simple map...');
      
      // Create map
      const map = L.map(mapRef.current).setView([51.505, -0.09], 13);
      
      // Add tile layer
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(map);
      
      // Add a test marker
      L.marker([51.5, -0.09]).addTo(map)
        .bindPopup('<b>Hello!</b><br />I am a popup.').openPopup();
      
      console.log('Simple map created');
    }
  }, []);

  return (
    <div 
      ref={mapRef} 
      style={{ height: '400px', width: '100%' }}
      className="border border-gray-300 rounded"
    />
  );
};

export default SimpleMap; 