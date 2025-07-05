import React from 'react';

const tables = [
  { key: 'properties', label: 'Properties' },
  { key: 'ratepayers', label: 'Ratepayers' },
  { key: 'valuations', label: 'Valuations' },
  { key: 'historic_valuations', label: 'Historic Valuations' },
  { key: 'non_rated_properties', label: 'Non-Rated Properties' },
  // Add more tables as needed
];

export default function Sidebar({ selected, onSelect }) {
  return (
    <aside className="w-64 bg-gray-100 h-full p-4 border-r">
      <h2 className="text-lg font-bold mb-4">NNDR Data Tables</h2>
      <ul>
        {tables.map((t) => (
          <li key={t.key}>
            <button
              className={`w-full text-left px-2 py-1 rounded hover:bg-blue-100 ${selected === t.key ? 'bg-blue-200 font-semibold' : ''}`}
              onClick={() => onSelect(t.key)}
            >
              {t.label}
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}
