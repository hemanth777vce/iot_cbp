import React, { useState, useEffect } from 'react';
import {
  Zap,
  Activity,
  Flame,
  Gauge,
  DollarSign,
  AlertTriangle,
  History,
  TrendingUp,
  RefreshCw,
  ArrowRight,
  ShieldCheck,
  ShieldAlert,
} from 'lucide-react';
import MetricCard from '../components/MetricCard';
import LiveChart from '../components/LiveChart';
import AlertList from '../components/AlertList';
import StatusBadge from '../components/StatusBadge';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import { api } from '../api/client';

export default function Dashboard({ onNavigate }) {
  const [summary, setSummary] = useState(null);
  const [powerTrends, setPowerTrends] = useState([]);
  const [viTrends, setViTrends] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [genLoading, setGenLoading] = useState(false);

  const fetchDashboardData = async () => {
    try {
      const [sumRes, powerRes, viRes, eventsRes] = await Promise.all([
        api.getDashboardSummary(),
        api.getPowerTrends(30),
        api.getVoltageTrends(30),
        api.getRecentEvents(),
      ]);

      setSummary(sumRes);
      setPowerTrends(powerRes.trends || []);

      // Merge voltage and current trends for dual-axis display
      const currentRes = await api.getCurrentTrends(30);
      const mergedVI = (viRes.trends || []).map((vt, i) => ({
        timestamp: vt.timestamp,
        time_label: vt.time_label,
        voltage: vt.voltage,
        current: (currentRes.trends && currentRes.trends[i]) ? currentRes.trends[i].current : 0,
      }));
      setViTrends(mergedVI);
      setEvents(eventsRes.events || []);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    // Auto-refresh interval (2.5 seconds)
    const interval = setInterval(fetchDashboardData, 2500);
    return () => clearInterval(interval);
  }, []);

  const handleGenerateDemo = async () => {
    setGenLoading(true);
    try {
      await api.generateDemoData(6);
      await fetchDashboardData();
    } catch (err) {
      alert('Failed to generate demo data: ' + err.message);
    } finally {
      setGenLoading(false);
    }
  };

  const handleAcknowledge = async (id) => {
    try {
      await api.acknowledgeAlert(id);
      fetchDashboardData();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading && !summary) {
    return <LoadingState message="Initializing PowerGuard telemetry dashboard..." />;
  }

  if (error && !summary) {
    return <ErrorState message={error} onRetry={fetchDashboardData} />;
  }

  const metrics = summary?.metrics || {};
  const consumption = summary?.consumption_summary || {};
  const isNormal = summary?.system_status === 'NORMAL';
  const isCritical = summary?.system_status === 'CRITICAL';

  return (
    <div className="page-container">
      {/* Simulation Notice Banner */}
      <div className="sim-banner">
        <Zap size={18} />
        <div style={{ flex: 1 }}>
          <strong>SIMULATION MODE ACTIVE:</strong> Generating physically consistent single-phase synthetic AC signals.
          No physical electrical circuit or safety trip hardware connected.
        </div>
        {consumption.today_energy_kwh === 0 && (
          <button
            className="btn btn-primary btn-sm"
            onClick={handleGenerateDemo}
            disabled={genLoading}
          >
            {genLoading ? 'Simulating...' : 'Generate 6h Demo Data'}
          </button>
        )}
      </div>

      {/* Primary Telemetry Metric Cards */}
      <div className="metrics-grid">
        <MetricCard
          label="VOLTAGE"
          value={metrics.voltage?.value}
          unit="V"
          icon={Zap}
          status={metrics.voltage?.status || 'normal'}
          subText={`Nominal: ${metrics.voltage?.min_limit || 207}V - ${metrics.voltage?.max_limit || 253}V`}
        />

        <MetricCard
          label="CURRENT"
          value={metrics.current?.value}
          unit="A"
          icon={Activity}
          status={metrics.current?.status || 'normal'}
          subText={`Threshold: ${metrics.current?.max_threshold || 16.0} A limit`}
        />

        <MetricCard
          label="ACTIVE POWER"
          value={metrics.active_power?.value}
          unit="W"
          icon={Flame}
          status={metrics.active_power?.status || 'normal'}
          subText={`Capacity: ${metrics.active_power?.max_threshold || 3600} W limit`}
        />

        <MetricCard
          label="POWER FACTOR"
          value={metrics.power_factor?.value}
          unit=""
          icon={Gauge}
          status={metrics.power_factor?.status || 'normal'}
          subText={`Min Acceptable: ${metrics.power_factor?.min_threshold || 0.80}`}
        />

        <MetricCard
          label="ENERGY CONSUMED"
          value={metrics.cumulative_energy?.value}
          unit="kWh"
          icon={TrendingUp}
          status="info"
          subText="Cumulative simulated meter"
        />

        <MetricCard
          label="SYSTEM STATUS"
          value={summary?.system_status || 'NORMAL'}
          unit=""
          icon={isNormal ? ShieldCheck : ShieldAlert}
          status={isCritical ? 'critical' : isNormal ? 'normal' : 'warning'}
          subText={summary?.active_violations?.length > 0 ? summary.active_violations[0] : 'All circuits nominal'}
        />
      </div>

      {/* Live Charts Section */}
      <div className="charts-grid">
        {/* Active Power Trend */}
        <div className="card chart-card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <Flame size={18} color="var(--primary)" />
                <span>Live Active Power Trend</span>
              </h3>
              <p className="card-subtitle">Real-time real power dissipation (Watts) with continuous rolling baseline</p>
            </div>
            <div className="chart-header-actions">
              <span className="badge badge-normal">Live Auto-Update</span>
            </div>
          </div>
          <div className="chart-wrapper">
            <LiveChart
              data={powerTrends}
              lines={[
                { dataKey: 'active_power', name: 'Active Power', color: '#2563eb', unit: 'W' },
                { dataKey: 'apparent_power', name: 'Apparent Power', color: '#93c5fd', unit: 'VA' },
              ]}
              height={260}
            />
          </div>
        </div>

        {/* Dual Axis Voltage and Current Trends */}
        <div className="card chart-card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <Zap size={18} color="#10b981" />
                <span>Voltage & Current Telemetry</span>
              </h3>
              <p className="card-subtitle">Separate calibrated axes: Voltage (V) left axis, Current (A) right axis</p>
            </div>
            <div className="chart-header-actions">
              <span className="badge badge-info">Dual-Axis</span>
            </div>
          </div>
          <div className="chart-wrapper">
            <LiveChart
              data={viTrends}
              lines={[
                { dataKey: 'voltage', name: 'Voltage (V)', color: '#10b981', yAxisId: 'left', unit: 'V' },
                { dataKey: 'current', name: 'Current (A)', color: '#f59e0b', yAxisId: 'right', unit: 'A' },
              ]}
              dualAxis={true}
              height={260}
            />
          </div>
        </div>
      </div>

      {/* Consumption Summary & Financial Estimation */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <DollarSign size={18} color="var(--success)" />
              <span>Daily Consumption & Estimated Energy Cost</span>
            </h3>
            <p className="card-subtitle">
              Calculated from integrated active energy multiplied by configured tariff (
              {consumption.currency_symbol || '₹'}{consumption.tariff || '7.50'}/kWh)
            </p>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={() => onNavigate('analytics')}>
            <span>Deep Analytics</span>
            <ArrowRight size={14} />
          </button>
        </div>

        <div className="metrics-grid">
          <div style={{ padding: '10px 0' }}>
            <span className="metric-label">TODAY'S ENERGY</span>
            <div className="metric-value-wrap">
              <span className="metric-value mono">{consumption.today_energy_kwh ?? '0.000'}</span>
              <span className="metric-unit">kWh</span>
            </div>
            <div className="metric-sub">
              {consumption.change_vs_yesterday_pct !== null ? (
                <span>{consumption.change_vs_yesterday_pct > 0 ? `+${consumption.change_vs_yesterday_pct}%` : `${consumption.change_vs_yesterday_pct}%`} vs yesterday</span>
              ) : (
                <span>Baseline day</span>
              )}
            </div>
          </div>

          <div style={{ padding: '10px 0' }}>
            <span className="metric-label">ESTIMATED DAILY COST</span>
            <div className="metric-value-wrap">
              <span className="metric-value mono">
                {consumption.currency_symbol || '₹'}{consumption.estimated_daily_cost ?? '0.00'}
              </span>
            </div>
            <div className="metric-sub">Estimated at configured demo tariff</div>
          </div>

          <div style={{ padding: '10px 0' }}>
            <span className="metric-label">PEAK POWER OBSERVED</span>
            <div className="metric-value-wrap">
              <span className="metric-value mono">{consumption.peak_power_w ?? '0.0'}</span>
              <span className="metric-unit">W</span>
            </div>
            <div className="metric-sub">Maximum recorded load today</div>
          </div>

          <div style={{ padding: '10px 0' }}>
            <span className="metric-label">ALERTS RECORDED TODAY</span>
            <div className="metric-value-wrap">
              <span className="metric-value mono">{consumption.alerts_today ?? 0}</span>
            </div>
            <div className="metric-sub">
              {consumption.unacknowledged_alerts > 0 ? (
                <span style={{ color: 'var(--danger)', fontWeight: 600 }}>
                  {consumption.unacknowledged_alerts} unacknowledged
                </span>
              ) : (
                'All acknowledged'
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Row: Recent Alerts & System Activity Log */}
      <div className="charts-grid">
        {/* Recent Alerts */}
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <AlertTriangle size={18} color="var(--warning)" />
                <span>Recent Alerts & Violations</span>
              </h3>
              <p className="card-subtitle">Latest critical overload, threshold, and ML anomaly events</p>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={() => onNavigate('alerts')}>
              <span>View All</span>
              <ArrowRight size={14} />
            </button>
          </div>
          <AlertList alerts={summary?.recent_alerts || []} onAcknowledge={handleAcknowledge} isCompact={true} />
        </div>

        {/* System Activity */}
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <History size={18} color="#64748b" />
                <span>Recent System Activity</span>
              </h3>
              <p className="card-subtitle">Audited simulation state changes, rule evaluations, and model triggers</p>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={fetchDashboardData}>
              <RefreshCw size={14} />
            </button>
          </div>

          {events.length === 0 ? (
            <div className="empty-state" style={{ padding: '24px 0' }}>
              <p className="empty-title">No Events Logged</p>
              <p className="empty-desc">System events will appear here as simulation operates.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {events.map((ev) => (
                <div
                  key={ev.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '8px 12px',
                    backgroundColor: '#f8fafc',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.8125rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span className="badge badge-info" style={{ fontSize: '0.65rem' }}>
                      {ev.event_type}
                    </span>
                    <span style={{ color: 'var(--text-main)' }}>{ev.description}</span>
                  </div>
                  <span style={{ color: 'var(--text-light)', fontSize: '0.75rem', whiteSpace: 'nowrap' }}>
                    {ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : ''}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
