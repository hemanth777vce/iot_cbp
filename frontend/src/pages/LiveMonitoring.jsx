import React, { useState, useEffect } from 'react';
import {
  Activity,
  Play,
  Pause,
  Square,
  Zap,
  Flame,
  Gauge,
  TrendingUp,
  Cpu,
  RefreshCw,
  Sliders,
} from 'lucide-react';
import MetricCard from '../components/MetricCard';
import LiveChart from '../components/LiveChart';
import StatusBadge from '../components/StatusBadge';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import { api } from '../api/client';

export default function LiveMonitoring() {
  const [latestReading, setLatestReading] = useState(null);
  const [recentReadings, setRecentReadings] = useState([]);
  const [simulationStatus, setSimulationStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProfile, setSelectedProfile] = useState('normal');

  const fetchLiveTelemetry = async () => {
    try {
      const [statusRes, latestRes, readingsRes] = await Promise.all([
        api.getSimulationStatus(),
        api.getLatestReading(),
        api.getReadings({ page: 1, page_size: 25 }),
      ]);

      setSimulationStatus(statusRes.simulation);
      if (statusRes.simulation?.load_profile) {
        setSelectedProfile(statusRes.simulation.load_profile);
      }
      setLatestReading(latestRes.reading);
      setRecentReadings(readingsRes.items || []);
      setError(null);
    } catch (err) {
      setError(err.message || 'Telemetry connection failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLiveTelemetry();
    const interval = setInterval(fetchLiveTelemetry, 1500); // 1.5s refresh for live monitoring
    return () => clearInterval(interval);
  }, []);

  const handleStart = async () => {
    try {
      await api.startSimulation();
      fetchLiveTelemetry();
    } catch (e) {
      alert(e.message);
    }
  };

  const handlePause = async () => {
    try {
      await api.pauseSimulation();
      fetchLiveTelemetry();
    } catch (e) {
      alert(e.message);
    }
  };

  const handleResume = async () => {
    try {
      await api.resumeSimulation();
      fetchLiveTelemetry();
    } catch (e) {
      alert(e.message);
    }
  };

  const handleStop = async () => {
    try {
      await api.stopSimulation();
      fetchLiveTelemetry();
    } catch (e) {
      alert(e.message);
    }
  };

  const handleProfileChange = async (profile) => {
    try {
      setSelectedProfile(profile);
      await api.setProfile(profile);
      fetchLiveTelemetry();
    } catch (e) {
      alert(e.message);
    }
  };

  if (loading && !latestReading) {
    return <LoadingState message="Connecting to live electrical stream..." />;
  }

  const isRunning = simulationStatus?.is_running && !simulationStatus?.is_paused;
  const isPaused = simulationStatus?.is_running && simulationStatus?.is_paused;
  const isStopped = !simulationStatus?.is_running;

  // Chart data formatted from recent readings (reversed to chronological)
  const chartData = [...recentReadings].reverse().map((r) => ({
    timestamp: r.timestamp,
    time_label: r.timestamp ? new Date(r.timestamp).toLocaleTimeString() : '',
    active_power: r.active_power,
    voltage: r.voltage,
    current: r.current,
  }));

  const profiles = [
    { id: 'normal', name: 'Normal Household', desc: 'Standard residential base load (3-6A)' },
    { id: 'high', name: 'High Consumption', desc: 'Heavy appliances, heating/cooling (12-15A)' },
    { id: 'fluctuating', name: 'Dynamic / Inductive', desc: 'Compressor cycles & motor starts' },
    { id: 'standby', name: 'Standby / Low Power', desc: 'Idle night load (<1A, low PF)' },
    { id: 'overload', name: 'Overload Scenario', desc: 'Intentional limit breach (>16A, >3600W)' },
    { id: 'anomalous', name: 'Anomalous Profile', desc: 'Severe PF lag & irregular harmonic surges' },
  ];

  return (
    <div className="page-container">
      {error && <ErrorState message={error} onRetry={fetchLiveTelemetry} />}

      {/* Live Controls Card */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <Sliders size={18} color="var(--primary)" />
              <span>Real-Time Generator Controls</span>
            </h3>
            <p className="card-subtitle">
              Interactive telemetry switchboard: manage simulated waveforms and load regimes
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {isStopped && (
              <button className="btn btn-success btn-sm" onClick={handleStart}>
                <Play size={14} />
                <span>Start Stream</span>
              </button>
            )}

            {isRunning && (
              <button className="btn btn-warning btn-sm" onClick={handlePause}>
                <Pause size={14} />
                <span>Pause</span>
              </button>
            )}

            {isPaused && (
              <button className="btn btn-primary btn-sm" onClick={handleResume}>
                <Play size={14} />
                <span>Resume</span>
              </button>
            )}

            {!isStopped && (
              <button className="btn btn-danger btn-sm" onClick={handleStop}>
                <Square size={14} />
                <span>Stop</span>
              </button>
            )}

            <button className="btn btn-secondary btn-sm" onClick={fetchLiveTelemetry}>
              <RefreshCw size={14} />
            </button>
          </div>
        </div>

        {/* Load Profile Selector Grid */}
        <div>
          <label className="form-label" style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
            Active Load Profile:
          </label>
          <div className="profile-pill-grid">
            {profiles.map((p) => {
              const active = selectedProfile === p.id;
              return (
                <div
                  key={p.id}
                  className={`profile-pill ${active ? 'active' : ''}`}
                  onClick={() => handleProfileChange(p.id)}
                >
                  <div className="profile-pill-name">
                    <span>{p.name}</span>
                    {active && <span className="badge badge-primary" style={{ fontSize: '0.65rem' }}>Active</span>}
                  </div>
                  <div className="profile-pill-desc">{p.desc}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Live Gauges & Cards */}
      <div className="metrics-grid">
        <MetricCard
          label="RMS VOLTAGE"
          value={latestReading?.voltage}
          unit="V"
          icon={Zap}
          status={latestReading?.voltage >= 207 && latestReading?.voltage <= 253 ? 'normal' : 'warning'}
          subText="Single Phase 50Hz AC"
        />

        <MetricCard
          label="CURRENT DRAW"
          value={latestReading?.current}
          unit="A"
          icon={Activity}
          status={latestReading?.current >= 16.0 ? 'critical' : latestReading?.current >= 13.6 ? 'warning' : 'normal'}
          subText={`Threshold: 16.0 A`}
        />

        <MetricCard
          label="ACTIVE POWER (P)"
          value={latestReading?.active_power}
          unit="W"
          icon={Flame}
          status={latestReading?.active_power >= 3600 ? 'critical' : latestReading?.active_power >= 3060 ? 'warning' : 'normal'}
          subText="P = V · I · cos(φ)"
        />

        <MetricCard
          label="APPARENT POWER (S)"
          value={latestReading?.apparent_power}
          unit="VA"
          icon={Zap}
          status="info"
          subText="S = V · I"
        />

        <MetricCard
          label="REACTIVE POWER (Q)"
          value={latestReading?.reactive_power}
          unit="var"
          icon={Activity}
          status="info"
          subText="Q = √(S² - P²)"
        />

        <MetricCard
          label="POWER FACTOR"
          value={latestReading?.power_factor}
          unit=""
          icon={Gauge}
          status={latestReading?.power_factor >= 0.80 ? 'normal' : 'warning'}
          subText="cos(φ) lagging"
        />
      </div>

      {/* Real-time Oscillating Chart */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <Activity size={18} color="var(--primary)" />
              <span>Real-Time Waveform & Load Trajectory</span>
            </h3>
            <p className="card-subtitle">
              Continuous live stream from simulated smart meter. Updates dynamically while simulation runs.
            </p>
          </div>
          <div>
            <span className={`badge ${isRunning ? 'badge-normal' : 'badge-warning'}`}>
              {isRunning ? 'Receiving Live Data' : isPaused ? 'Stream Paused' : 'Generator Stopped'}
            </span>
          </div>
        </div>
        <LiveChart
          data={chartData}
          lines={[
            { dataKey: 'active_power', name: 'Active Power (W)', color: '#2563eb', unit: 'W' },
            { dataKey: 'voltage', name: 'Voltage (V)', color: '#10b981', unit: 'V' },
          ]}
          height={300}
        />
      </div>

      {/* Telemetry Stream Log Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <TrendingUp size={18} color="#64748b" />
              <span>Latest Ingested Telemetry Packets</span>
            </h3>
            <p className="card-subtitle">Most recent high-resolution readings processed by the calculation pipeline</p>
          </div>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Voltage (V)</th>
                <th>Current (A)</th>
                <th>Active (W)</th>
                <th>Apparent (VA)</th>
                <th>Reactive (var)</th>
                <th>Power Factor</th>
                <th>Energy (kWh)</th>
                <th>Profile</th>
              </tr>
            </thead>
            <tbody>
              {recentReadings.length === 0 ? (
                <tr>
                  <td colSpan="9" style={{ textAlign: 'center', padding: '24px' }}>
                    No readings ingested yet. Start the simulator above to stream readings.
                  </td>
                </tr>
              ) : (
                recentReadings.map((r) => (
                  <tr key={r.id}>
                    <td className="mono">{r.timestamp ? new Date(r.timestamp).toLocaleTimeString() : '--'}</td>
                    <td className="mono">{r.voltage}</td>
                    <td className="mono" style={{ color: r.current >= 16.0 ? 'var(--danger)' : 'inherit', fontWeight: r.current >= 16.0 ? 700 : 400 }}>
                      {r.current}
                    </td>
                    <td className="mono" style={{ color: r.active_power >= 3600 ? 'var(--danger)' : 'inherit', fontWeight: r.active_power >= 3600 ? 700 : 400 }}>
                      {r.active_power}
                    </td>
                    <td className="mono">{r.apparent_power}</td>
                    <td className="mono">{r.reactive_power}</td>
                    <td className="mono" style={{ color: r.power_factor < 0.8 ? 'var(--warning)' : 'inherit' }}>
                      {r.power_factor}
                    </td>
                    <td className="mono">{r.energy_kwh}</td>
                    <td>
                      <StatusBadge status={r.load_profile} text={r.load_profile} />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
