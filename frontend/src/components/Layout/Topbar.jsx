import React from 'react';
import { useLocation } from 'react-router-dom';
import { User, CheckCircle } from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/' },
  { name: 'Geospatial', href: '/geospatial' },
  { name: 'Analytics', href: '/analytics' },
  { name: 'Properties', href: '/properties' },
  { name: 'Maps', href: '/maps' },
  { name: 'Upload', href: '/upload' },
  { name: 'Settings', href: '/settings' },
];

export default function Topbar() {
  const location = useLocation();
  const current = navigation.find(item => item.href === location.pathname)?.name || 'Dashboard';
  return (
    <div className="sticky top-0 z-10 bg-white shadow-sm border-b border-gray-200">
      <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
        <div className="flex items-center space-x-4">
          <h2 className="text-lg font-medium text-gray-900">{current}</h2>
        </div>
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span>API Connected</span>
          </div>
          <div className="flex items-center space-x-2">
            <User className="w-5 h-5 text-gray-400" />
            <span className="text-sm text-gray-700">User</span>
          </div>
        </div>
      </div>
    </div>
  );
} 