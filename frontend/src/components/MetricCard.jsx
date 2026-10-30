import React from 'react';

export default function MetricCard({
  label,
  value,
  unit,
  icon: Icon,
  status = 'normal',
  subText,
  badgeText,
}) {
  return (
    <div className={`metric-card status-${status}`}>
      <div className="metric-top">
        <span className="metric-label">{label}</span>
        {Icon && (
          <div
            className="metric-icon-wrap"
            style={{
              backgroundColor:
                status === 'critical'
                  ? 'var(--danger-bg)'
                  : status === 'warning'
                  ? 'var(--warning-bg)'
                  : 'var(--primary-light)',
              color:
                status === 'critical'
                  ? 'var(--danger)'
                  : status === 'warning'
                  ? 'var(--warning)'
                  : 'var(--primary)',
            }}
          >
            <Icon size={18} />
          </div>
        )}
      </div>

      <div className="metric-value-wrap">
        <span className="metric-value mono">
          {value !== undefined && value !== null ? value : '--'}
        </span>
        {unit && <span className="metric-unit">{unit}</span>}
      </div>

      {(subText || badgeText) && (
        <div className="metric-sub">
          {subText && <span>{subText}</span>}
        </div>
      )}
    </div>
  );
}
