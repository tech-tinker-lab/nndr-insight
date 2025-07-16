import React from 'react';

const DataTablePreview = ({ preview, showMappingOptions, columnMappings }) => (
  <div className="overflow-x-auto max-h-64">
    <table className="min-w-full text-xs border border-gray-300">
      <thead className="bg-gray-100">
        <tr>
          {preview.headers.map((header, idx) => (
            <th key={idx} className="border border-gray-300 px-2 py-1 text-left font-medium">
              <div className="flex flex-col">
                <span>{header}</span>
                {showMappingOptions && (
                  <span className="text-xs text-blue-600 font-normal">
                    {columnMappings[header] || 'TEXT'}
                  </span>
                )}
              </div>
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {preview.data.map((row, rowIdx) => (
          <tr key={rowIdx} className="hover:bg-gray-50">
            {row.map((cell, cellIdx) => (
              <td key={cellIdx} className="border border-gray-300 px-2 py-1 text-gray-700">
                <div className="max-w-xs truncate" title={cell}>
                  {cell || ''}
                </div>
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

// File removed after migration to DataTablePreview.tsx
