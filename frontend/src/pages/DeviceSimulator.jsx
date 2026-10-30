import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Play,
  Pause,
  Square,
  FastForward,
  RotateCcw,
  Sparkles,
  AlertTriangle,
  Brain,
  CheckCircle,
  HelpCircle,
  Activity,
  Flame,
  Zap,
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import { api } from '../api/client';

export default function DeviceSimulator() {
  const [status, setStatus] = useState(null);
  const [mlStatus, setMlStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [speedVal, setSpeedVal] = useState(1.0);
  const [showResetModal, setShowResetModal] = useState(false);
  const [actionMsg, setActionMsg] = useState(null);
  const [mlLoading, setMlLoading] = useState(false);

  const fetchStatus = async () => {
    try {
      const [simRes, mlRes] = await Promise.all([
        api.getSimulationStatus(),
        api.getMlStatus(),
      ]);

      setStatus(simRes.simulation);
      setSpeedVal(simRes.simulation?.speed || 1.0);
      setMlStatus(mlRes.ml_status);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to connect to simulator daemon');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleStart = async () => {
    try {
      await api.startSimulation();
      setActionMsg('Simulation started');
      fetchStatus();
    } catch (e) {
      setError(e.message);
    }
  };

  const handlePause = async () => {
    try {
      await api.pauseSimulation();
      setActionMsg('Simulation paused');
      fetchStatus();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleResume = async () => {
    try {
      await api.resumeSimulation();
      setActionMsg('Simulation resumed');
      fetchStatus();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleStop = async () => {
    try {
      await api.stopSimulation();
      setActionMsg('Simulation stopped');
      fetchStatus();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleProfileSwitch = async (profileName) => {
    try {
      await api.setProfile(profileName);
      setActionMsg(`Profile set to ${profileName}`);
      fetchStatus();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleSpeedChange = async (newSpeed) => {
    setSpeedVal(newSpeed);
    try {
      await api.setSpeed(newSpeed);
      fetchStatus();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleScenarioTrigger = async (profileName) => {
    try {
      await api.setProfile(profileName);
      if (!status?.is_running) {
        await api.startSimulation();
      } else if (status?.is_paused) {
        await api.resumeSimulation();
      }
      setActionMsg(`Triggered '${profileName}' active scenario!`);
      fetchStatus();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleTrainMl = async () => {
    setMlLoading(true);
    try {
      const res = await api.trainMlModel();
      setActionMsg(res.message);
      await fetchStatus();
    } catch (e) {
      alert(e.message);
    } finally {
      setMlLoading(false);
    }
  };

  const handleConfirmedReset = async () => {
    try {
      await api.resetDemoData();
      setShowResetModal(false);
      setActionMsg('Database successfully reset to clean state.');
      await fetchStatus();
    } catch (e) {
      alert('Reset failed: ' + e.message);
    }
  };

  if (loading && !status) {
    return <LoadingState message="Accessing Simulator Control Plane..." />;
  }

  const isRunning = status?.is_running && !status?.is_paused;
  const isPaused = status?.is_running && status?.is_paused;
  const isStopped = !status?.is_running;

  const profilesList = [
    {
      id: 'normal',
      name: 'Normal Household',
      desc: '230V nominal, 2.5A to 5.5A base load, 0.94 PF. Healthy residential condition.',
      icon: Activity,
    },
    {
      id: 'high',
      name: 'High Consumption',
      desc: '12A to 15.5A load (water heaters, oven, EV charger). High active power draw.',
      icon: Flame,
    },
    {
      id: 'fluctuating',
      name: 'Fluctuating / Inductive',
      desc: 'Cycles between 2A and 14A with lower power factors (0.78). Simulates compressor starts.',
      icon: Zap,
    },
    {
      id: 'standby',
      name: 'Standby / Low Power',
      desc: '0.3A to 0.7A idle load with capacitive/inductive standby distortion (0.70 PF).',
      icon: Activity,
    },
    {
      id: 'overload',
      name: 'Overload Scenario',
      desc: '18A to 24A, 4200W+ load. Exceeds limits and triggers immediate CRITICAL rule alerts!',
      icon: AlertTriangle,
    },
    {
      id: 'anomalous',
      name: 'Anomalous Consumption',
      desc: 'Distorted power factor (0.40) & irregular harmonic spikes. Triggers ML Isolation Forest!',
      icon: Brain,
    },
  ];

  return (
    <div className="page-container">
      {/* Prominent Required Simulation Banner */}
      <div
        className="sim-banner"
        style={{
          backgroundColor: '#eff6ff',
          border: '2px solid #3b82f6',
          padding: '14px 20px',
          fontWeight: 600,
        }}
      >
        <Zap size={22} color="#2563eb" />
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '0.9375rem', letterSpacing: '0.02em', color: '#1d4ed8' }}>
            SIMULATION MODE — NO PHYSICAL SENSORS CONNECTED
          </div>
          <p style={{ fontWeight: 400, fontSize: '0.75rem', color: '#1e40af', marginTop: '2px' }}>
            This application generates realistic synthetic single-phase AC waveforms. It does not measure physical
            current or physically trip circuit breakers.
          </p>
        </div>
        {actionMsg && (
          <span className="badge badge-normal" style={{ fontSize: '0.75rem' }}>
            {actionMsg}
          </span>
        )}
      </div>

      {error && <ErrorState message={error} onRetry={fetchStatus} />}

      {/* Simulator Primary Controls */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <Cpu size={18} color="var(--primary)" />
              <span>Simulation Execution Engine</span>
            </h3>
            <p className="card-subtitle">
              Manage thread-safe background waveform generation and simulation speed
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {isStopped && (
              <button className="btn btn-success" onClick={handleStart}>
                <Play size={16} />
                <span>Start Simulator</span>
              </button>
            )}

            {isRunning && (
              <button className="btn btn-warning" onClick={handlePause}>
                <Pause size={16} />
                <span>Pause</span>
              </button>
            )}

            {isPaused && (
              <button className="btn btn-primary" onClick={handleResume}>
                <Play size={16} />
                <span>Resume</span>
              </button>
            )}

            {!isStopped && (
              <button className="btn btn-danger" onClick={handleStop}>
                <Square size={16} />
                <span>Stop</span>
              </button>
            )}

            <button
              className="btn btn-outline-danger btn-sm"
              onClick={() => setShowResetModal(true)}
              title="Reset all database records"
            >
              <RotateCcw size={14} />
              <span>Reset Database</span>
            </button>
          </div>
        </div>

        {/* Speed Multiplier Slider */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px', padding: '12px 0', borderTop: '1px solid var(--border-light)' }}>
          <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-main)', minWidth: '130px' }}>
            Simulation Speed: <span className="mono">{speedVal}x</span>
          </span>
          <input
            type="range"
            min="0.5"
            max="5.0"
            step="0.5"
            value={speedVal}
            onChange={(e) => handleSpeedChange(Number(e.target.value))}
            style={{ flex: 1, maxWidth: '300px' }}
          />
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            (1 reading every {(1.0 / speedVal).toFixed(2)} real seconds)
          </span>
        </div>
      </div>

      {/* Demonstration Scenario Shortcuts */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <Sparkles size={18} color="#8b5cf6" />
              <span>One-Click Demonstration Scenarios</span>
            </h3>
            <p className="card-subtitle">
              Instantly inject characteristic operating conditions for lab evaluation and demonstration
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
          <button
            className="btn btn-secondary"
            style={{ flexDirection: 'column', alignItems: 'flex-start', padding: '14px', height: 'auto' }}
            onClick={() => handleScenarioTrigger('normal')}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600, color: 'var(--primary)' }}>
              <Activity size={16} />
              <span>Normal Operation</span>
            </div>
            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '4px', textAlign: 'left' }}>
              Nominal 230V, ~4A draw. All parameters within safe limits. System status: NORMAL.
            </p>
          </button>

          <button
            className="btn btn-secondary"
            style={{ flexDirection: 'column', alignItems: 'flex-start', padding: '14px', height: 'auto' }}
            onClick={() => handleScenarioTrigger('high')}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600, color: '#f59e0b' }}>
              <Flame size={16} />
              <span>High Consumption</span>
            </div>
            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '4px', textAlign: 'left' }}>
              High current (14A), ~3100W power draw. Nearing warning limits.
            </p>
          </button>

          <button
            className="btn btn-secondary"
            style={{ flexDirection: 'column', alignItems: 'flex-start', padding: '14px', height: 'auto', borderColor: 'var(--danger-border)', backgroundColor: '#fffafb' }}
            onClick={() => handleScenarioTrigger('overload')}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600, color: 'var(--danger)' }}>
              <AlertTriangle size={16} />
              <span>Overload Scenario</span>
            </div>
            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '4px', textAlign: 'left' }}>
              Surges to 21A and 4500W. Breaches 16A/3600W threshold, fires CRITICAL rule alert!
            </p>
          </button>

          <button
            className="btn btn-secondary"
            style={{ flexDirection: 'column', alignItems: 'flex-start', padding: '14px', height: 'auto', borderColor: 'var(--purple-border)', backgroundColor: '#faf5ff' }}
            onClick={() => handleScenarioTrigger('anomalous')}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600, color: 'var(--purple)' }}>
              <Brain size={16} />
              <span>Anomaly Scenario</span>
            </div>
            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '4px', textAlign: 'left' }}>
              Degrades power factor to 0.40 with irregular oscillations. Triggers ML Isolation Forest!
            </p>
          </button>
        </div>
      </div>

      {/* Machine Learning Model Diagnostics Card */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <Brain size={18} color="var(--purple)" />
              <span>Isolation Forest ML Anomaly Engine</span>
            </h3>
            <p className="card-subtitle">
              Multivariate unsupervised outlier detection across Voltage, Current, Power Factor & Rolling Deviations
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button
              className="btn btn-primary btn-sm"
              onClick={handleTrainMl}
              disabled={mlLoading}
            >
              <Brain size={14} />
              <span>{mlLoading ? 'Training Model...' : 'Train / Retrain Model'}</span>
            </button>
          </div>
        </div>

        <div className="metrics-grid">
          <div style={{ padding: '8px 0' }}>
            <span className="metric-label">MODEL STATUS</span>
            <div style={{ marginTop: '4px' }}>
              <StatusBadge status={mlStatus?.status || 'NOT_TRAINED'} text={mlStatus?.status || 'NOT_TRAINED'} />
            </div>
          </div>

          <div style={{ padding: '8px 0' }}>
            <span className="metric-label">TRAINING SAMPLES</span>
            <div className="metric-value-wrap">
              <span className="metric-value mono">{mlStatus?.samples_trained_on || 0}</span>
              <span className="metric-unit">readings</span>
            </div>
            <div className="metric-sub">Min required: {mlStatus?.min_samples_required || 30}</div>
          </div>

          <div style={{ padding: '8px 0' }}>
            <span className="metric-label">CONTAMINATION FACTOR</span>
            <div className="metric-value-wrap">
              <span className="metric-value mono">{mlStatus?.contamination || 0.05}</span>
            </div>
            <div className="metric-sub">Expected outlier proportion (5%)</div>
          </div>

          <div style={{ padding: '8px 0' }}>
            <span className="metric-label">AVAILABLE DB READINGS</span>
            <div className="metric-value-wrap">
              <span className="metric-value mono">{mlStatus?.available_readings_in_db || 0}</span>
            </div>
            <div className="metric-sub">Eligible for model fitting</div>
          </div>
        </div>
      </div>

      {/* Confirmation Modal for Resetting Demo Data */}
      {showResetModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3 style={{ fontSize: '1.125rem', fontWeight: 700, color: 'var(--danger)', marginBottom: '8px' }}>
              Confirm Database Reset
            </h3>
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
              Are you sure you want to clear all electrical readings, alert logs, and system events?
              This will restore PowerGuard to a fresh, clean database state.
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button className="btn btn-secondary" onClick={() => setShowResetModal(false)}>
                Cancel
              </button>
              <button className="btn btn-danger" onClick={handleConfirmedReset}>
                Yes, Reset Everything
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
