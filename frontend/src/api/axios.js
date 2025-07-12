import axios from "axios";

const api = axios.create();

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Add /api prefix only for admin endpoints if not already present
  if (config.url && config.url.startsWith('/admin') && !config.url.startsWith('/api')) {
    config.url = `/api${config.url}`;
  }
  
  return config;
});

export default api; 