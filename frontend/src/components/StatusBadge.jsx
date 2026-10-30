import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle, Info } from 'lucide-react';

export default function StatusBadge({ status, text, size = 'sm' }) {
  const normalized = (status || '').toUpperCase();
  
  let badgeClass = 'badge-normal';
  let Icon = CheckCircle;
  let label = text || status;

  if (normalized === 'CRITICAL' || normalized === 'DANGER' || normalized === 'OVERLOAD') {
    badgeClass = 'badge-critical';
    Icon = AlertCircle;
  } else if (normalized === 'WARNING') {
    badgeClass = 'badge-warning';
    Icon = AlertTriangle;
  } else if (normalized === 'INFO' || normalized === 'STANDBY') {
    badgeClass = 'badge-info';
    Icon = Info;
  } else if (normalized === 'ANOMALOUS' || normalized === 'ANOMALY_DETECTOR') {
    badgeClass = 'badge-purple';
    Icon = AlertTriangle;
  }

  return (
    <span className={`badge ${badgeClass} ${size === 'sm' ? 'btn-sm' : ''}`}>
      <Icon size={12} />
      <span>{label}</span>
    </span>
  );
}
