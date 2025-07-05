import React, { useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { 
  Home, 
  Map, 
  BarChart3, 
  Building2, 
  Globe, 
  Upload, 
  Settings, 
  Menu, 
  X,
  Database,
  TrendingUp,
  Users,
  FileText
} from 'lucide-react';
import clsx from 'clsx';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Geospatial', href: '/geospatial', icon: Globe },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Properties', href: '/properties', icon: Building2 },
  { name: 'Maps', href: '/maps', icon: Map },
  { name: 'Upload', href: '/upload', icon: Upload },
  { name: 'Settings', href: '/settings', icon: Settings },
];

const dataNavigation = [
  { name: 'UPRN Data', href: '/data/uprn', icon: Database },
  { name: 'Postcodes', href: '/data/postcodes', icon: FileText },
  { name: 'Place Names', href: '/data/places', icon: Map },
  { name: 'Boundaries', href: '/data/boundaries', icon: Globe },
];

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gray-50 lg:flex">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

      {/* Main content */}
      <div className="flex-1 flex flex-col">
        <Topbar />
        <main className="py-6 flex-1">
          <div className="mx-auto px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
} 