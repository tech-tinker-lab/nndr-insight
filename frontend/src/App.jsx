import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard';
import Geospatial from './pages/Geospatial';
import Analytics from './pages/Analytics';
import Properties from './pages/Properties';
import Maps from './pages/Maps';
import Upload from './pages/Upload';
import Settings from './pages/Settings';

function App() {
  return (
    <Router>
      <div className="App">
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/geospatial" element={<Geospatial />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/properties" element={<Properties />} />
            <Route path="/maps" element={<Maps />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;
