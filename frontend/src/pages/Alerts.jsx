import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  AlertCircle,
  CheckCircle,
  Search,
  Filter,
  Check,
  RefreshCw,
  Bell,
  Cpu,
} from 'lucide-react';
import AlertList from '../components/AlertList';
import StatusBadge from '../components/StatusBadge';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import { api } from '../api/client';

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters & Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [severityFilter, setSeverityFilter] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');
  const [ackFilter, setAckFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchAlertsData = async () => {
    try {
      setLoading(true);
      const params = {
        page,
        page_size: 15,
      };
      if (severityFilter) params.severity = severityFilter;
      if (sourceFilter) params.source = sourceFilter;
      if (ackFilter !== '') params.acknowledged = ackFilter;
      if (searchQuery) params.search = searchQuery;

      const [alertsRes, sumRes] = await Promise.all([
        api.getAlerts(params),
        api.getAlertSummary(),
      ]);

      setAlerts(alertsRes.items || []);
      setTotalPages(alertsRes.total_pages || 1);
      setTotalCount(alertsRes.total || 0);
      setSummary(sumRes.summary || null);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to fetch alerts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlertsData();
  }, [page, severityFilter, sourceFilter, ackFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchAlertsData();
  };

  const handleAcknowledge = async (id) => {
    try {
      await api.acknowledgeAlert(id);
      fetchAlertsData();
    } catch (err) {
      alert('Failed to acknowledge alert: ' + err.message);
    }
  };

  return (
    <div className="page-container">
      {error && <ErrorState message={error} onRetry={fetchAlertsData} />}

      {/* Summary KPI Badges */}
      <div className="metrics-grid">
        <div className="card" style={{ padding: '16px 20px', borderLeft: '4px solid #64748b' }}>
          <span className="metric-label">TOTAL ALERTS</span>
          <div className="metric-value-wrap">
            <span className="metric-value mono">{summary?.total ?? 0}</span>
          </div>
          <div className="metric-sub">Recorded event violations</div>
        </div>

        <div className="card" style={{ padding: '16px 20px', borderLeft: '4px solid var(--danger)' }}>
          <span className="metric-label">CRITICAL OVERLOADS</span>
          <div className="metric-value-wrap">
            <span className="metric-value mono" style={{ color: 'var(--danger)' }}>{summary?.critical ?? 0}</span>
          </div>
          <div className="metric-sub">Severe threshold breaches</div>
        </div>

        <div className="card" style={{ padding: '16px 20px', borderLeft: '4px solid var(--warning)' }}>
          <span className="metric-label">WARNINGS</span>
          <div className="metric-value-wrap">
            <span className="metric-value mono" style={{ color: 'var(--warning)' }}>{summary?.warning ?? 0}</span>
          </div>
          <div className="metric-sub">Cautionary boundary alerts</div>
        </div>

        <div className="card" style={{ padding: '16px 20px', borderLeft: '4px solid var(--purple)' }}>
          <span className="metric-label">ML ANOMALIES</span>
          <div className="metric-value-wrap">
            <span className="metric-value mono" style={{ color: 'var(--purple)' }}>{summary?.ml_anomalies ?? 0}</span>
          </div>
          <div className="metric-sub">Isolation Forest detections</div>
        </div>

        <div className="card" style={{ padding: '16px 20px', borderLeft: '4px solid var(--primary)' }}>
          <span className="metric-label">UNACKNOWLEDGED</span>
          <div className="metric-value-wrap">
            <span className="metric-value mono" style={{ color: 'var(--primary)' }}>{summary?.unacknowledged ?? 0}</span>
          </div>
          <div className="metric-sub">Require user attention</div>
        </div>
      </div>

      {/* Filters & Search Toolbar */}
      <div className="card">
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
          {/* Search form */}
          <form onSubmit={handleSearchSubmit} style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: '1', minWidth: '240px', maxWidth: '400px' }}>
            <div style={{ position: 'relative', width: '100%' }}>
              <input
                type="text"
                className="form-input"
                style={{ width: '100%', paddingLeft: '34px' }}
                placeholder="Search parameter or message..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <Search size={16} color="var(--text-light)" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
            </div>
            <button type="submit" className="btn btn-secondary btn-sm">Search</button>
          </form>

          {/* Filter Dropdowns */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            {/* Severity */}
            <select
              className="form-select btn-sm"
              value={severityFilter}
              onChange={(e) => { setSeverityFilter(e.target.value); setPage(1); }}
            >
              <option value="">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="WARNING">Warning</option>
            </select>

            {/* Source */}
            <select
              className="form-select btn-sm"
              value={sourceFilter}
              onChange={(e) => { setSourceFilter(e.target.value); setPage(1); }}
            >
              <option value="">All Sources</option>
              <option value="RULE_ENGINE">Rule Engine</option>
              <option value="ANOMALY_DETECTOR">ML Anomaly Detector</option>
            </select>

            {/* Acknowledged */}
            <select
              className="form-select btn-sm"
              value={ackFilter}
              onChange={(e) => { setAckFilter(e.target.value); setPage(1); }}
            >
              <option value="">All Statuses</option>
              <option value="false">Unacknowledged Only</option>
              <option value="true">Acknowledged Only</option>
            </select>

            <button className="btn btn-secondary btn-sm" onClick={fetchAlertsData} title="Refresh alerts">
              <RefreshCw size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* Alerts Table / List */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <Bell size={18} color="var(--primary)" />
              <span>Event & Alarm Log</span>
            </h3>
            <p className="card-subtitle">
              Showing {alerts.length} of {totalCount} total alerts (Page {page} of {totalPages})
            </p>
          </div>
        </div>

        {loading ? (
          <LoadingState message="Loading alert records..." />
        ) : (
          <AlertList alerts={alerts} onAcknowledge={handleAcknowledge} />
        )}

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="pagination-bar">
            <span>Page {page} of {totalPages} ({totalCount} total events)</span>
            <div className="pagination-controls">
              <button
                className="btn btn-secondary btn-sm"
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
              >
                Previous
              </button>
              <button
                className="btn btn-secondary btn-sm"
                disabled={page >= totalPages}
                onClick={() => setPage(page + 1)}
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
