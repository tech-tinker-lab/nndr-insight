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
import Admin from './pages/Admin';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './context/UserContext';
import StagedData from './pages/StagedData';
import MasterData from './pages/MasterData';
import DatasetStructures from './pages/DesignSystemEnhanced';
import DataStandardsRegistry from './components/DataStandardsRegistry';
import DatasetCreationWizard from './pages/DatasetCreationWizard';
import DatasetRegistry from './pages/DatasetRegistry';
import NNDRForecasting from './pages/NNDRForecasting';
import NNDRIndicators from './pages/NNDRIndicators';
import ForecastDetail from './pages/ForecastDetail';
import AreaDrilldown from './pages/AreaDrilldown';
import IndicatorAnalysis from './pages/IndicatorAnalysis';
import ReportBuilder from './pages/ReportBuilder';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/geospatial" element={<Geospatial />} />
                      <Route path="/analytics" element={<Analytics />} />
                      <Route path="/properties" element={<Properties />} />
                      <Route path="/maps" element={<Maps />} />
                      <Route path="/upload" element={<Upload />} />
                      <Route path="/settings" element={<Settings />} />
                      <Route
                        path="/admin"
                        element={
                          <ProtectedRoute allowedRoles={["admin", "power_user", "dataset_manager"]}>
                            <Admin />
                          </ProtectedRoute>
                        }
                      />
                      <Route path="/staged-data" element={<StagedData />} />
                      <Route path="/master" element={<MasterData />} />
                      <Route path="/dataset-structures" element={<DatasetStructures />} />
                      <Route path="/data-standards" element={<DataStandardsRegistry />} />
                      <Route path="/datasets/new" element={<DatasetCreationWizard />} />
                      <Route path="/datasets" element={<DatasetRegistry />} />
                      <Route path="/nndr-forecasting" element={<NNDRForecasting />} />
                      <Route path="/nndr-indicators" element={<NNDRIndicators />} />
                      <Route path="/forecast/:id" element={<ForecastDetail />} />
                      <Route path="/area/:id" element={<AreaDrilldown />} />
                      <Route path="/indicator/:id" element={<IndicatorAnalysis />} />
                      <Route path="/report-builder" element={<ReportBuilder />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
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
    </AuthProvider>
  );
}

export default App;
