import React, { useState, useEffect } from 'react';
import { api } from '../api/axios';

const DataStandardsAnalytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filters
  const [timePeriod, setTimePeriod] = useState('30d');
  const [category, setCategory] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    loadAnalytics();
  }, [timePeriod, category]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      
      // Load analytics data
      const analyticsResponse = await api.get('/api/design-enhanced/data-standards/analytics', {
        params: { time_period: timePeriod, category }
      });
      setAnalytics(analyticsResponse.data);
      
      // Load performance metrics
      const performanceResponse = await api.get('/api/design-enhanced/data-standards/performance-metrics', {
        params: { start_date: startDate, end_date: endDate }
      });
      setPerformance(performanceResponse.data);
      
      // Load recommendations
      const recommendationsResponse = await api.get('/api/design-enhanced/data-standards/recommendations');
      setRecommendations(recommendationsResponse.data);
      
    } catch (err) {
      setError('Failed to load analytics data');
      console.error('Error loading analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getTrendColor = (trend) => {
    const colors = {
      increasing: 'text-green-600',
      decreasing: 'text-red-600',
      stable: 'text-blue-600'
    };
    return colors[trend] || 'text-gray-600';
  };

  const getPerformanceColor = (value) => {
    if (value >= 0.9) return 'text-green-600';
    if (value >= 0.8) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Data Standards Analytics</h1>
            <p className="mt-1 text-sm text-gray-500">
              Data-driven insights into standards usage, performance, and effectiveness
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={timePeriod}
              onChange={(e) => setTimePeriod(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
              <option value="all">All time</option>
            </select>
            <button
              onClick={loadAnalytics}
              className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white shadow rounded-lg p-4">
            <div className="text-2xl font-bold text-gray-900">{analytics.summary.total_standards_analyzed}</div>
            <div className="text-sm text-gray-500">Standards Analyzed</div>
          </div>
          <div className="bg-white shadow rounded-lg p-4">
            <div className={`text-2xl font-bold ${getPerformanceColor(analytics.summary.avg_confidence_score)}`}>
              {formatPercentage(analytics.summary.avg_confidence_score)}
            </div>
            <div className="text-sm text-gray-500">Avg Confidence Score</div>
          </div>
          <div className="bg-white shadow rounded-lg p-4">
            <div className={`text-2xl font-bold ${getPerformanceColor(analytics.summary.detection_accuracy)}`}>
              {formatPercentage(analytics.summary.detection_accuracy)}
            </div>
            <div className="text-sm text-gray-500">Detection Accuracy</div>
          </div>
          <div className="bg-white shadow rounded-lg p-4">
            <div className="text-2xl font-bold text-blue-600">{analytics.summary.countries_represented}</div>
            <div className="text-sm text-gray-500">Countries Represented</div>
          </div>
        </div>
      )}

      {/* Performance Metrics */}
      {performance && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Detection Performance */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Detection Performance</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Detections:</span>
                  <span className="text-sm font-medium">{performance.performance_metrics.detection_performance.total_detections}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Success Rate:</span>
                  <span className={`text-sm font-medium ${getPerformanceColor(performance.performance_metrics.detection_performance.success_rate)}`}>
                    {formatPercentage(performance.performance_metrics.detection_performance.success_rate)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Avg Detection Time:</span>
                  <span className="text-sm font-medium">{performance.performance_metrics.detection_performance.avg_detection_time_ms}ms</span>
                </div>
              </div>
            </div>

            {/* Accuracy Metrics */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Accuracy Metrics</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Overall Accuracy:</span>
                  <span className={`text-sm font-medium ${getPerformanceColor(performance.performance_metrics.accuracy_metrics.overall_accuracy)}`}>
                    {formatPercentage(performance.performance_metrics.accuracy_metrics.overall_accuracy)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Precision:</span>
                  <span className={`text-sm font-medium ${getPerformanceColor(performance.performance_metrics.accuracy_metrics.precision)}`}>
                    {formatPercentage(performance.performance_metrics.accuracy_metrics.precision)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Recall:</span>
                  <span className={`text-sm font-medium ${getPerformanceColor(performance.performance_metrics.accuracy_metrics.recall)}`}>
                    {formatPercentage(performance.performance_metrics.accuracy_metrics.recall)}
                  </span>
                </div>
              </div>
            </div>

            {/* Summary */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Summary</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Overall Success Rate:</span>
                  <span className={`text-sm font-medium ${getPerformanceColor(performance.summary.overall_success_rate)}`}>
                    {formatPercentage(performance.summary.overall_success_rate)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Standards Tracked:</span>
                  <span className="text-sm font-medium">{performance.summary.total_standards_tracked}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Trend:</span>
                  <span className={`text-sm font-medium ${getTrendColor(performance.summary.improvement_trend)}`}>
                    {performance.summary.improvement_trend}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Category Performance */}
      {performance && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Category Performance</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(performance.performance_metrics.category_performance).map(([category, data]) => (
              <div key={category} className="border border-gray-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-900 mb-2">{data.category_name}</h3>
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-xs text-gray-600">Standards:</span>
                    <span className="text-xs font-medium">{data.standards_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-xs text-gray-600">Success Rate:</span>
                    <span className={`text-xs font-medium ${getPerformanceColor(data.avg_success_rate)}`}>
                      {formatPercentage(data.avg_success_rate)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-xs text-gray-600">Detections:</span>
                    <span className="text-xs font-medium">{data.total_detections}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Performing Standards */}
      {performance && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Performing Standards</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Standard</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Detections</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Success Rate</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Confidence</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trend</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Object.entries(performance.performance_metrics.standards_performance)
                  .sort((a, b) => b[1].success_rate - a[1].success_rate)
                  .slice(0, 10)
                  .map(([standardId, data]) => (
                    <tr key={standardId}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{data.name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{data.detection_count}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-sm font-medium ${getPerformanceColor(data.success_rate)}`}>
                          {formatPercentage(data.success_rate)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-sm font-medium ${getPerformanceColor(data.avg_confidence)}`}>
                          {formatPercentage(data.avg_confidence)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-sm font-medium ${getTrendColor(data.trend)}`}>
                          {data.trend}
                        </span>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Data-Driven Recommendations</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* System Recommendations */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-3">System Recommendations</h3>
              <div className="space-y-2">
                {performance?.summary?.recommendations?.map((recommendation, index) => (
                  <div key={index} className="flex items-start">
                    <div className="flex-shrink-0">
                      <svg className="h-4 w-4 text-blue-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-2 text-sm text-gray-600">{recommendation}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Industry Best Practices */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-3">Industry Best Practices</h3>
              <div className="space-y-2">
                {recommendations.recommendations?.industry_best_practices?.slice(0, 5).map((practice, index) => (
                  <div key={index} className="flex items-start">
                    <div className="flex-shrink-0">
                      <svg className="h-4 w-4 text-green-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-2">
                      <div className="text-sm font-medium text-gray-900">{practice.name}</div>
                      <div className="text-xs text-gray-500">{practice.reasoning}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Trends Chart */}
      {performance && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Detection Trends (Last 30 Days)</h2>
          <div className="h-64 flex items-end justify-between space-x-1">
            {performance.performance_metrics.trends.daily_detections.slice(-30).map((day, index) => (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div 
                  className="w-full bg-blue-500 rounded-t"
                  style={{ 
                    height: `${(day.detections / 50) * 100}%`,
                    minHeight: '4px'
                  }}
                ></div>
                <div className="text-xs text-gray-500 mt-1">
                  {new Date(day.date).getDate()}
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 text-center text-sm text-gray-600">
            Daily detection counts over the last 30 days
          </div>
        </div>
      )}
    </div>
  );
};

export default DataStandardsAnalytics; 