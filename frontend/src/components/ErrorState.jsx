import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export default function ErrorState({ title = 'Error Loading Data', message, onRetry }) {
  return (
    <div className="card" style={{ borderColor: 'var(--danger-border)', backgroundColor: '#fffafb' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
        <AlertCircle size={22} color="var(--danger)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div style={{ flex: 1 }}>
          <h4 style={{ color: 'var(--danger)', fontSize: '0.9375rem', fontWeight: 600, marginBottom: '4px' }}>
            {title}
          </h4>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', marginBottom: onRetry ? '12px' : '0' }}>
            {message || 'An unexpected error occurred while communicating with the PowerGuard service.'}
          </p>
          {onRetry && (
            <button className="btn btn-secondary btn-sm" onClick={onRetry}>
              <RefreshCw size={14} />
              <span>Retry</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
