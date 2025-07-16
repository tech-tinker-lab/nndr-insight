// File removed after migration to ZIPIntelligentAnalyzer.tsx
import React, { useState, useEffect } from 'react';
import DirectoryTree from './DirectoryTree';
import { formatFileSize } from './uploadUtils';

// ZIPIntelligentAnalyzer: Intelligent analysis and selection of files in a ZIP archive
const ZIPIntelligentAnalyzer = ({ zipContents, directoryStructure, file, analysis, isLADFile }) => {
  const [viewMode, setViewMode] = useState('structure');
  const [selectedHeaderFile, setSelectedHeaderFile] = useState(null);
  const [selectedDataFiles, setSelectedDataFiles] = useState([]);
  const [suggestedFiles, setSuggestedFiles] = useState({ header: null, data: [] });

  useEffect(() => {
    if (zipContents && zipContents.files) {
      const suggestions = analyzeZIPContents(zipContents);
      setSuggestedFiles(suggestions);
      if (suggestions.header) setSelectedHeaderFile(suggestions.header);
      if (suggestions.data.length > 0) setSelectedDataFiles(suggestions.data);
    }
  }, [zipContents]);

  const analyzeZIPContents = (contents) => {
    const suggestions = { header: null, data: [] };
    const potentialHeaders = contents.files.filter(file => {
      const name = file.name.toLowerCase();
      const size = file.size;
      return (
        name.includes('header') ||
        name.includes('schema') ||
        name.includes('readme') ||
        name.includes('metadata') ||
        name.includes('description') ||
        (name.endsWith('.csv') && size < 5000) ||
        (name.endsWith('.txt') && size < 2000)
      );
    });
    const potentialData = contents.files.filter(file => {
      const name = file.name.toLowerCase();
      const size = file.size;
      return (
        (name.endsWith('.csv') && size > 1000) ||
        (name.endsWith('.json') && size > 1000) ||
        (name.endsWith('.xml') && size > 1000) ||
        (name.endsWith('.gml') && size > 1000) ||
        name.includes('data') ||
        name.includes('records') ||
        name.includes('values')
      );
    });
    if (potentialHeaders.length > 0) suggestions.header = potentialHeaders[0];
    suggestions.data = potentialData.slice(0, 5);
    return suggestions;
  };

  const getFileIcon = (fileName) => {
    const ext = fileName.toLowerCase().split('.').pop();
    switch (ext) {
      case 'csv': return <span role="img" aria-label="csv">🟩</span>;
      case 'json': return <span role="img" aria-label="json">🟨</span>;
      case 'xml': return <span role="img" aria-label="xml">🟦</span>;
      case 'gml': return <span role="img" aria-label="gml">🟪</span>;
      case 'txt': return <span role="img" aria-label="txt">⬜</span>;
      default: return <span role="img" aria-label="file">📄</span>;
    }
  };

  const toggleFileSelection = (file, type) => {
    if (type === 'header') {
      setSelectedHeaderFile(selectedHeaderFile?.path === file.path ? null : file);
    } else {
      setSelectedDataFiles(prev => {
        const isSelected = prev.some(f => f.path === file.path);
        if (isSelected) return prev.filter(f => f.path !== file.path);
        return [...prev, file];
      });
    }
  };

  if (isLADFile && isLADFile(file, analysis)) {
    return (
      <div className="p-3 bg-blue-50 rounded border border-blue-200 mt-2">
        <div className="font-medium text-blue-700 mb-2">LAD ZIP detected. Processing automatically.</div>
        {/* ...LAD file preview logic... */}
      </div>
    );
  }

  return (
    <div className="text-xs">
      {/* ...UI for structure/selection, file groups, directory tree, file selection... */}
    </div>
  );
};

export default ZIPIntelligentAnalyzer;
