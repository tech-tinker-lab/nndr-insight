// uploadUtils.js: Utility functions for Upload page and related components

export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function getStatusIcon(status) {
  // Return a string or icon component based on status
  switch (status) {
    case 'completed': return '✔️';
    case 'running': return '⏳';
    case 'failed': return '❌';
    case 'pending': return '🕒';
    default: return '🕒';
  }
}

export function getStatusColor(status) {
  switch (status) {
    case 'completed': return 'text-green-600 bg-green-50';
    case 'running': return 'text-blue-600 bg-blue-50';
    case 'failed': return 'text-red-600 bg-red-50';
    case 'pending': return 'text-gray-600 bg-gray-50';
    default: return 'text-gray-600 bg-gray-50';
  }
}

export function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hours}h ${minutes}m ${secs}s`;
}
