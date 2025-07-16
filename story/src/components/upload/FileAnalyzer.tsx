import React from 'react';
import { FileText, FileArchive, FileCode, FileSpreadsheet, MapPin } from 'lucide-react';

const FileAnalyzer = {
  /**
   * Analyze CSV text and return headers, sampleRows, and a simple structure.
   * Keeps logic short and easy to maintain.
   * @param {string} text - The CSV file content as string
   * @param {string} fileName - The file name (for metadata)
   * @returns {object} { headers, sampleRows, structure, filename, format }
   */
  analyzeCSV: (text: string, fileName = '') => {
    // Split lines, handle CRLF and skip empty lines
    const lines = text.split(/\r?\n/).filter(line => line.trim().length > 0);
    if (lines.length === 0) return { headers: [], sampleRows: [], structure: {}, filename: fileName, format: 'csv' };
    // Simple CSV split (does not handle quoted commas)
    const parseLine = (line: string) => line.split(',').map(cell => cell.trim());
    const headers = parseLine(lines[0]);
    const sampleRows = lines.slice(1, 11).map(parseLine); // up to 10 sample rows
    // Infer structure: guess type by sampling values
    const inferType = (values: string[]) => {
      if (values.every(v => /^-?\d+$/.test(v))) return 'integer';
      if (values.every(v => /^-?\d*\.\d+$/.test(v))) return 'float';
      if (values.every(v => v === 'true' || v === 'false')) return 'boolean';
      return 'string';
    };
    const structure: Record<string, { type: string; sample: string[] }> = {};
    headers.forEach((header, i) => {
      const colVals = sampleRows.map(row => row[i] || '');
      structure[header] = { type: inferType(colVals), sample: colVals };
    });
    return {
      headers,
      sampleRows,
      structure,
      filename: fileName,
      format: 'csv',
    };
  },
  detectFileType: (file: File) => {
    const extension = file.name.toLowerCase().split('.').pop();
    const mimeType = file.type;
    if (extension === 'zip' || mimeType === 'application/zip') return 'zip';
    if (extension === 'csv' || mimeType === 'text/csv') return 'csv';
    if (extension === 'json' || mimeType === 'application/json') return 'json';
    if (extension === 'xml' || mimeType === 'application/xml' || mimeType === 'text/xml') return 'xml';
    if (extension === 'yml' || extension === 'yaml' || mimeType === 'text/yaml') return 'yaml';
    if (extension === 'gml' || mimeType === 'application/gml+xml') return 'gml';
    if (extension === 'gpkg' || mimeType === 'application/geopackage+sqlite3') return 'geopackage';
    if ([ 'shp', 'dbf', 'shx', 'prj', 'cpg', 'qix' ].includes(extension || '')) return 'shapefile';
    if (extension === 'sdmx' || mimeType === 'application/vnd.sdmx.structure+xml') return 'sdmx';
    if (extension === 'kml' || mimeType === 'application/vnd.google-earth.kml+xml') return 'kml';
    if (extension === 'geojson' || mimeType === 'application/geo+json') return 'geojson';
    if (extension === 'txt' || mimeType.startsWith('text/')) return 'text';
    return 'text';
  },
  getFileIcon: (fileType: string) => {
    switch (fileType) {
      case 'zip': return <FileArchive className="w-5 h-5 text-orange-500" />;
      case 'csv': return <FileSpreadsheet className="w-5 h-5 text-green-500" />;
      case 'json':
      case 'geojson': return <FileCode className="w-5 h-5 text-yellow-500" />;
      case 'xml':
      case 'gml':
      case 'sdmx':
      case 'kml': return <FileCode className="w-5 h-5 text-blue-500" />;
      case 'yaml': return <FileCode className="w-5 h-5 text-purple-500" />;
      case 'geopackage': return <MapPin className="w-5 h-5 text-red-500" />;
      case 'shapefile': return <MapPin className="w-5 h-5 text-indigo-500" />;
      case 'text': return <FileText className="w-5 h-5 text-gray-500" />;
      default: return <FileText className="w-5 h-5 text-gray-400" />;
    }
  },
};

export default FileAnalyzer;
