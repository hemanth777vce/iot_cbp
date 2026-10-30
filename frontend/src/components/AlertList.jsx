import React from 'react';
import { Check, BellOff, ShieldAlert } from 'lucide-react';
import StatusBadge from './StatusBadge';

export default function AlertList({ alerts = [], onAcknowledge, isCompact = false }) {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="empty-state">
        <BellOff className="empty-icon" />
        <p className="empty-title">All Clear</p>
        <p className="empty-desc">No electrical alerts or anomaly events recorded.</p>
      </div>
    );
  }

  const formatTimestamp = (ts) => {
    if (!ts) return '';
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) +
        ' (' + d.toLocaleDateString([], { month: 'short', day: 'numeric' }) + ')';
    } catch {
      return ts;
    }
  };

  return (
    <div className="alert-list">
      {alerts.map((alert) => (
        <div key={alert.id} className={`alert-item severity-${alert.severity}`}>
          <div className="alert-content">
            <div className="alert-headline">
              <StatusBadge status={alert.severity} />
              <span className="alert-msg">{alert.message}</span>
            </div>

            <div className="alert-details">
              <span>Param: <strong className="mono">{alert.parameter}</strong></span>
              <span>Observed: <strong className="mono">{alert.observed_value}</strong></span>
              <span>Limit: <strong className="mono">{alert.threshold_value}</strong></span>
              <span>Source: <strong>{alert.source === 'ANOMALY_DETECTOR' ? 'ML Isolation Forest' : 'Rule Engine'}</strong></span>
              <span>{formatTimestamp(alert.timestamp)}</span>
            </div>
          </div>

          <div className="alert-action">
            {alert.acknowledged ? (
              <span className="badge badge-normal" title={`Acknowledged at ${alert.acknowledged_at || ''}`}>
                <Check size={12} />
                <span>Acked</span>
              </span>
            ) : (
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => onAcknowledge && onAcknowledge(alert.id)}
                title="Acknowledge this event"
              >
                <Check size={14} />
                <span>Acknowledge</span>
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
