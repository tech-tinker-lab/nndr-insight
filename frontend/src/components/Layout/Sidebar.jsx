import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Home, Globe, BarChart3, Building2, Map, Upload, Settings, Database, FileText, Shield, Palette
} from 'lucide-react';
import clsx from 'clsx';
import { useUser } from '../../context/UserContext';

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Geospatial', href: '/geospatial', icon: Globe },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Properties', href: '/properties', icon: Building2 },
  { name: 'Maps', href: '/maps', icon: Map },
  { name: 'Upload', href: '/upload', icon: Upload },
  { name: 'Design System', href: '/design-system', icon: Palette },
  { name: 'Settings', href: '/settings', icon: Settings },
  { name: 'Staged Data', href: '/admin', icon: Shield },
  { name: 'Master Data', href: '/master', icon: Database },
];

const dataNavigation = [
  { name: 'UPRN Data', href: '/data/uprn', icon: Database },
  { name: 'Postcodes', href: '/data/postcodes', icon: FileText },
  { name: 'Place Names', href: '/data/places', icon: Map },
  { name: 'Boundaries', href: '/data/boundaries', icon: Globe },
];

export default function Sidebar({ sidebarOpen, setSidebarOpen }) {
  const location = useLocation();
  const { user } = useUser();
  return (
    <div className={clsx(
      'fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
      sidebarOpen ? 'translate-x-0' : '-translate-x-full')
    }>
      <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
        <div className="flex items-center">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Building2 className="w-5 h-5 text-white" />
          </div>
          <h1 className="ml-3 text-xl font-bold text-gray-900">NNDR Insight</h1>
        </div>
        <button
          onClick={() => setSidebarOpen(false)}
          className="lg:hidden p-1 rounded-md text-gray-400 hover:text-gray-600"
        >
          <span className="sr-only">Close sidebar</span>
          <svg className="h-6 w-6" stroke="currentColor" fill="none" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      </div>
      <nav className="mt-6 px-3">
        <div className="space-y-1">
          {navigation
            .filter((item) => {
              if (item.name === 'Staged Data') {
                return user && ["admin", "power_user", "dataset_manager"].includes(user.role);
              }
              return true;
            })
            .map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={clsx(
                    'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                    isActive
                      ? 'bg-blue-100 text-blue-700 border-r-2 border-blue-700'
                      : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                  )}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className={clsx('mr-3 h-5 w-5', isActive ? 'text-blue-700' : 'text-gray-400 group-hover:text-gray-500')} />
                  {item.name}
                </Link>
              );
            })}
        </div>
        <div className="mt-8">
          <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            Data Sources
          </h3>
          <div className="mt-2 space-y-1">
            {dataNavigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={clsx(
                    'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                    isActive
                      ? 'bg-green-100 text-green-700 border-r-2 border-green-700'
                      : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                  )}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className={clsx('mr-3 h-4 w-4', isActive ? 'text-green-700' : 'text-gray-400 group-hover:text-gray-500')} />
                  {item.name}
                </Link>
              );
            })}
          </div>
        </div>
      </nav>
    </div>
  );
} 