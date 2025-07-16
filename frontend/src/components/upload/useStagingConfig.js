import { useState, useEffect } from 'react';
import api from '../../api/axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Staging table configuration store with persistence
export default function useStagingConfig() {
  const [configs, setConfigs] = useState({});
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    try {
      const stored = localStorage.getItem('staging_configs');
      if (stored) {
        const parsed = JSON.parse(stored);
        setConfigs(parsed);
        console.log('Loaded staging configs from localStorage:', parsed);
      }
    } catch (error) {
      console.error('Failed to load staging configs from localStorage:', error);
    }
    setLoaded(true);
  }, []);

  useEffect(() => {
    if (loaded) {
      try {
        localStorage.setItem('staging_configs', JSON.stringify(configs));
        console.log('Saved staging configs to localStorage:', configs);
      } catch (error) {
        console.error('Failed to save staging configs to localStorage:', error);
      }
    }
  }, [configs, loaded]);

  const saveConfig = async (datasetId, config) => {
    setConfigs(prev => ({
      ...prev,
      [datasetId]: config
    }));
    try {
      await api.post(`${API_BASE_URL}/admin/staging/configs`, {
        dataset_id: datasetId,
        config: config
      });
      console.log('Saved config to backend for dataset:', datasetId);
    } catch (error) {
      console.warn('Failed to save config to backend, using localStorage only:', error);
    }
  };

  const getConfig = (datasetId) => configs[datasetId] || null;
  const getAllConfigs = () => configs;
  const deleteConfig = (datasetId) => {
    setConfigs(prev => {
      const newConfigs = { ...prev };
      delete newConfigs[datasetId];
      return newConfigs;
    });
  };

  return { saveConfig, getConfig, getAllConfigs, deleteConfig };
}
