/**
 * Centralized API Client for PowerGuard Backend
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const errorMessage = data.error || data.message || `Request failed with status ${response.status}`;
      const error = new Error(errorMessage);
      error.status = response.status;
      error.details = data.details || data;
      throw error;
    }

    return data;
  } catch (err) {
    if (err.name === 'TypeError' && err.message.includes('Failed to fetch')) {
      const networkError = new Error('Cannot connect to PowerGuard backend server. Please verify the Flask backend is running on port 5000.');
      networkError.status = 0;
      throw networkError;
    }
    throw err;
  }
}

export const api = {
  // Health
  getHealth: () => request('/health'),

  // Dashboard
  getDashboardSummary: () => request('/dashboard/summary'),
  getRecentReadings: () => request('/dashboard/recent-readings'),
  getRecentEvents: () => request('/dashboard/recent-events'),

  // Readings
  getReadings: (params = {}) => {
    const query = new URLSearchParams();
    if (params.page) query.set('page', params.page);
    if (params.page_size) query.set('page_size', params.page_size);
    if (params.load_profile) query.set('load_profile', params.load_profile);
    if (params.start_date) query.set('start_date', params.start_date);
    if (params.end_date) query.set('end_date', params.end_date);
    return request(`/readings?${query.toString()}`);
  },
  getLatestReading: () => request('/readings/latest'),
  getAggregates: (loadProfile) => {
    const query = loadProfile ? `?load_profile=${encodeURIComponent(loadProfile)}` : '';
    return request(`/readings/aggregates${query}`);
  },

  // Alerts
  getAlerts: (params = {}) => {
    const query = new URLSearchParams();
    if (params.page) query.set('page', params.page);
    if (params.page_size) query.set('page_size', params.page_size);
    if (params.severity) query.set('severity', params.severity);
    if (params.source) query.set('source', params.source);
    if (params.acknowledged !== undefined && params.acknowledged !== null && params.acknowledged !== '') {
      query.set('acknowledged', params.acknowledged);
    }
    if (params.search) query.set('search', params.search);
    return request(`/alerts?${query.toString()}`);
  },
  getAlertById: (id) => request(`/alerts/${id}`),
  acknowledgeAlert: (id) => request(`/alerts/${id}/acknowledge`, { method: 'PATCH' }),
  getAlertSummary: () => request('/alerts/summary'),

  // Analytics
  getConsumption: (params = {}) => {
    const query = new URLSearchParams();
    if (params.start_date) query.set('start_date', params.start_date);
    if (params.end_date) query.set('end_date', params.end_date);
    if (params.interval) query.set('interval', params.interval);
    return request(`/analytics/consumption?${query.toString()}`);
  },
  getPowerTrends: (limit = 100) => request(`/analytics/power-trends?limit=${limit}`),
  getVoltageTrends: (limit = 100) => request(`/analytics/voltage-trends?limit=${limit}`),
  getCurrentTrends: (limit = 100) => request(`/analytics/current-trends?limit=${limit}`),
  getDailySummary: () => request('/analytics/daily-summary'),
  getCostEstimate: (kwh) => request(`/analytics/cost-estimate?kwh=${encodeURIComponent(kwh)}`),
  getProfileDistribution: () => request('/analytics/profiles'),

  // Simulation
  getSimulationStatus: () => request('/simulation/status'),
  startSimulation: () => request('/simulation/start', { method: 'POST' }),
  pauseSimulation: () => request('/simulation/pause', { method: 'POST' }),
  resumeSimulation: () => request('/simulation/resume', { method: 'POST' }),
  stopSimulation: () => request('/simulation/stop', { method: 'POST' }),
  setProfile: (profile) => request('/simulation/profile', {
    method: 'POST',
    body: JSON.stringify({ profile }),
  }),
  setSpeed: (speed) => request('/simulation/speed', {
    method: 'POST',
    body: JSON.stringify({ speed }),
  }),
  generateDemoData: (hours = 6) => request('/simulation/generate-demo-data', {
    method: 'POST',
    body: JSON.stringify({ hours }),
  }),
  resetDemoData: () => request('/simulation/reset', {
    method: 'POST',
    body: JSON.stringify({ confirm: true }),
  }),

  // Settings
  getSettings: () => request('/settings'),
  updateSettings: (settingsObj) => request('/settings', {
    method: 'PATCH',
    body: JSON.stringify(settingsObj),
  }),
  resetSettings: () => request('/settings/reset', { method: 'POST' }),

  // ML
  getMlStatus: () => request('/ml/status'),
  trainMlModel: () => request('/ml/train', { method: 'POST' }),
  getMlAnomalies: () => request('/ml/anomalies'),
};
