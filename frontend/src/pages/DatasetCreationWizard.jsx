import React, { useState } from 'react';
import DataStandardsRegistry from '../components/DataStandardsRegistry';
import FileUploadAndAIMatch from '../components/FileUploadAndAIMatch';
import { Link } from 'react-router-dom';
// import FileUploadAndAIMatch from '../components/FileUploadAndAIMatch'; // To be implemented

const DatasetCreationWizard = () => {
  const [workflow, setWorkflow] = useState(null); // 'standard' or 'file'

  if (!workflow) {
    return (
      <div className="max-w-xl mx-auto p-8">
        <h2 className="text-2xl font-bold mb-4">Create New Dataset</h2>
        <div className="space-y-4">
          <button
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700"
            onClick={() => setWorkflow('standard')}
          >
            Start with Standard
          </button>
          <button
            className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700"
            onClick={() => setWorkflow('file')}
          >
            Start with File (AI Suggestion)
          </button>
          <div className="pt-4 text-center">
            <Link to="/datasets" className="text-blue-600 hover:underline">View All Datasets</Link>
          </div>
        </div>
      </div>
    );
  }

  if (workflow === 'standard') {
    return (
      <div>
        <h2 className="text-xl font-bold mb-4">Select a Data Standard</h2>
        <DataStandardsRegistry />
        {/* TODO: Add file upload, field mapping, and ingestion steps */}
      </div>
    );
  }

  if (workflow === 'file') {
    return (
      <div>
        <h2 className="text-xl font-bold mb-4">Upload File & AI Suggestion</h2>
        <FileUploadAndAIMatch />
      </div>
    );
  }

  return null;
};

export default DatasetCreationWizard; 