import React, { useState, useEffect } from 'react';
import { Play, Pause, Square, Bell, Clock, Cpu } from 'lucide-react';
import { api } from '../api/client';

export default function Header({
  pageTitle,
  simulationState = {},
  unacknowledgedAlerts = 0,
  onNavigate,
  onStatusChange,
}) {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const isRunning = simulationState.is_running && !simulationState.is_paused;
  const isPaused = simulationState.is_running && simulationState.is_paused;
  const isStopped = !simulationState.is_running;

  const handleToggle = async () => {
    try {
      if (isRunning) {
        await api.pauseSimulation();
      } else if (isPaused) {
        await api.resumeSimulation();
      } else {
        await api.startSimulation();
      }
      if (onStatusChange) onStatusChange();
    } catch (err) {
      console.error('Failed to toggle simulation state:', err);
    }
  };

  const formattedTime = currentTime.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
  const formattedDate = currentTime.toLocaleDateString([], {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });

  return (
    <header className="app-header">
      <div className="header-title-area">
        <h1 className="page-title">{pageTitle}</h1>
      </div>

      <div className="header-actions">
        {/* Simulation Status Pill */}
        <div
          className={`status-pill ${
            isRunning
              ? 'status-pill-running'
              : isPaused
              ? 'status-pill-paused'
              : 'status-pill-stopped'
          }`}
        >
          <span className={`pulse-dot ${isRunning ? 'animating' : ''}`} />
          <span>
            {isRunning
              ? `Running (${simulationState.profile || 'normal'})`
              : isPaused
              ? 'Simulation Paused'
              : 'Simulator Idle'}
          </span>
          <button
            onClick={handleToggle}
            className="btn btn-sm"
            style={{
              padding: '2px 6px',
              fontSize: '0.7rem',
              marginLeft: '4px',
              backgroundColor: isRunning ? '#ffffff' : 'var(--primary)',
              color: isRunning ? 'var(--text-main)' : '#ffffff',
              border: 'none',
              borderRadius: '4px',
            }}
            title={isRunning ? 'Pause simulation' : 'Start/Resume simulation'}
          >
            {isRunning ? <Pause size={12} /> : <Play size={12} />}
          </button>
        </div>

        {/* Real-time Clock */}
        <div className="header-time">
          <Clock size={15} />
          <span>{formattedTime}</span>
          <span style={{ color: 'var(--text-light)' }}>({formattedDate})</span>
        </div>

        {/* Alerts Notification Button */}
        <button
          className="notification-btn"
          onClick={() => onNavigate && onNavigate('alerts')}
          title="View Alerts & Events"
        >
          <Bell size={18} />
          {unacknowledgedAlerts > 0 && (
            <span className="alert-counter">{unacknowledgedAlerts}</span>
          )}
        </button>
      </div>
    </header>
  );
}
