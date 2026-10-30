import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  DollarSign,
  Calendar,
  Filter,
  PieChart as PieIcon,
  Zap,
  Activity,
  Flame,
  Gauge,
  Sparkles,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import MetricCard from '../components/MetricCard';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import { api } from '../api/client';

const PROFILE_COLORS = {
  normal: '#2563eb',
  high: '#f59e0b',
  fluctuating: '#8b5cf6',
  standby: '#64748b',
  overload: '#ef4444',
  anomalous: '#ec4899',
};

export default function Analytics() {
  const [consumptionData, setConsumptionData] = useState([]);
  const [profileDist, setProfileDist] = useState([]);
  const [dailySummary, setDailySummary] = useState(null);
  const [aggregates, setAggregates] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [genLoading, setGenLoading] = useState(false);

  // Cost calculator interactive state
  const [customKwh, setCustomKwh] = useState(150);
  const [customCost, setCustomCost] = useState(null);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const [consRes, profRes, dailyRes, aggRes] = await Promise.all([
        api.getConsumption({ interval: 'hourly' }),
        api.getProfileDistribution(),
        api.getDailySummary(),
        api.getAggregates(),
      ]);

      setConsumptionData(consRes.consumption || []);
      setProfileDist(profRes.distribution || []);
      setDailySummary(dailyRes.summary || null);
      setAggregates(aggRes || null);

      // Fetch cost estimate for calculator
      const costRes = await api.getCostEstimate(customKwh);
      setCustomCost(costRes.estimated_cost);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to load historical analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const handleKwhChange = async (val) => {
    setCustomKwh(val);
    try {
      const res = await api.getCostEstimate(val);
      setCustomCost(res.estimated_cost);
    } catch (e) {
      console.error(e);
    }
  };

  const handleGenerateData = async () => {
    setGenLoading(true);
    try {
      await api.generateDemoData(8);
      await fetchAnalytics();
    } catch (err) {
      alert('Error generating demo records: ' + err.message);
    } finally {
      setGenLoading(false);
    }
  };

  if (loading && !dailySummary) {
    return <LoadingState message="Computing energy aggregations and statistics..." />;
  }

  const hasData = (aggregates?.count || 0) > 0;
  const currency = dailySummary?.currency_symbol || '₹';
  const tariff = dailySummary?.tariff_rate || 7.50;

  return (
    <div className="page-container">
      {error && <ErrorState message={error} onRetry={fetchAnalytics} />}

      {/* Analytics Summary Banner / Empty Check */}
      {!hasData && (
        <div className="card" style={{ textAlign: 'center', padding: '36px 20px' }}>
          <BarChart3 className="empty-icon" style={{ margin: '0 auto 12px' }} />
          <h3 className="empty-title">No Historical Energy Data Ingested</h3>
          <p className="empty-desc" style={{ margin: '0 auto 16px' }}>
            PowerGuard maintains full data integrity and does not fabricate fake database records.
            You can generate a multi-hour realistic synthetic dataset to demonstrate energy consumption analysis.
          </p>
          <button
            className="btn btn-primary"
            onClick={handleGenerateData}
            disabled={genLoading}
            style={{ margin: '0 auto' }}
          >
            <Sparkles size={16} />
            <span>{genLoading ? 'Simulating Historical Data...' : 'Generate 8-Hour Demo Dataset'}</span>
          </button>
        </div>
      )}

      {/* High-Level Historical Metrics */}
      <div className="metrics-grid">
        <MetricCard
          label="TOTAL READINGS"
          value={aggregates?.count || 0}
          unit="samples"
          icon={Activity}
          status="info"
          subText="Recorded historical database rows"
        />

        <MetricCard
          label="PEAK POWER RECORDED"
          value={aggregates?.active_power?.max ?? '--'}
          unit="W"
          icon={Flame}
          status="warning"
          subText="Maximum peak load spike observed"
        />

        <MetricCard
          label="AVERAGE ACTIVE POWER"
          value={aggregates?.active_power?.avg ?? '--'}
          unit="W"
          icon={Flame}
          status="normal"
          subText="Mean electrical load baseline"
        />

        <MetricCard
          label="MAX CURRENT DRAW"
          value={aggregates?.current?.max ?? '--'}
          unit="A"
          icon={Activity}
          status={aggregates?.current?.max >= 16.0 ? 'critical' : 'normal'}
          subText="Highest instantaneous current recorded"
        />

        <MetricCard
          label="AVG POWER FACTOR"
          value={aggregates?.power_factor?.avg ?? '--'}
          unit=""
          icon={Gauge}
          status={aggregates?.power_factor?.avg >= 0.85 ? 'normal' : 'warning'}
          subText="Network phase efficiency factor"
        />

        <MetricCard
          label="ESTIMATED COST (TODAY)"
          value={`${currency}${dailySummary?.estimated_daily_cost ?? '0.00'}`}
          unit=""
          icon={DollarSign}
          status="normal"
          subText={`Based on ${tariff} ${currency}/kWh tariff`}
        />
      </div>

      {/* Consumption Breakdown Bar Chart */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <BarChart3 size={18} color="var(--primary)" />
              <span>Energy Consumption Trends Over Time (kWh)</span>
            </h3>
            <p className="card-subtitle">
              Calculated by integrating active power over elapsed simulated seconds per observation window
            </p>
          </div>
        </div>

        {consumptionData.length === 0 ? (
          <div className="empty-state" style={{ minHeight: 280 }}>
            <p className="empty-title">No Periodic Consumption Segments</p>
            <p className="empty-desc">Generate demo data to populate time-series energy consumption bins.</p>
          </div>
        ) : (
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={consumptionData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="period" stroke="#94a3b8" fontSize={11} tickLine={false} dy={8} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} dx={-4} />
                <Tooltip
                  formatter={(val, name) => [
                    `${val} ${name === 'energy_kwh' ? 'kWh' : 'W'}`,
                    name === 'energy_kwh' ? 'Energy (kWh)' : 'Avg Power (W)',
                  ]}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', borderRadius: '6px' }}
                />
                <Legend verticalAlign="top" align="right" wrapperStyle={{ paddingBottom: '12px', fontSize: '12px' }} />
                <Bar dataKey="energy_kwh" name="Energy Consumed (kWh)" fill="#2563eb" radius={[4, 4, 0, 0]} />
                <Bar dataKey="avg_power_w" name="Average Power (W)" fill="#93c5fd" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Load Profile Distribution & Electricity Tariff Calculator */}
      <div className="charts-grid">
        {/* Profile Distribution */}
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <PieIcon size={18} color="#8b5cf6" />
                <span>Load Profile Distribution</span>
              </h3>
              <p className="card-subtitle">Proportion of time spent in each distinct operational load profile</p>
            </div>
          </div>

          {profileDist.length === 0 ? (
            <div className="empty-state">
              <p className="empty-title">No Profile Statistics</p>
              <p className="empty-desc">No readings categorized yet.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ width: '100%', height: 220 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={profileDist}
                      dataKey="count"
                      nameKey="profile"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      innerRadius={45}
                      paddingAngle={3}
                    >
                      {profileDist.map((entry) => (
                        <Cell
                          key={entry.profile}
                          fill={PROFILE_COLORS[entry.profile] || '#3b82f6'}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(val, name, props) => [`${val} samples (${props.payload.percentage}%)`, name]}
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', borderRadius: '6px' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Legend List */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '0.75rem' }}>
                {profileDist.map((item) => (
                  <div key={item.profile} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span
                      style={{
                        width: '10px',
                        height: '10px',
                        borderRadius: '2px',
                        backgroundColor: PROFILE_COLORS[item.profile] || '#3b82f6',
                        display: 'inline-block',
                      }}
                    />
                    <span style={{ textTransform: 'capitalize', fontWeight: 500 }}>{item.profile}:</span>
                    <span className="mono" style={{ color: 'var(--text-muted)' }}>{item.percentage}% ({item.count})</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Interactive Tariff Cost Estimator */}
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <DollarSign size={18} color="var(--success)" />
                <span>Electricity Tariff & Cost Estimator</span>
              </h3>
              <p className="card-subtitle">
                Model bill projections using the formula: Cost = Energy (kWh) × Tariff Rate
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div className="formula-box">
              <div className="formula-title">Mathematical Formula:</div>
              <div className="formula-code">Estimated Cost = Energy (kWh) × Configured Tariff ({currency}/kWh)</div>
            </div>

            <div className="form-group">
              <label className="form-label">Simulate Target Consumption (kWh):</label>
              <input
                type="number"
                className="form-input mono"
                value={customKwh}
                min="1"
                max="10000"
                step="5"
                onChange={(e) => handleKwhChange(Number(e.target.value))}
              />
              <span className="form-help">Adjust target energy value to simulate estimated electricity charges.</span>
            </div>

            <div
              style={{
                backgroundColor: 'var(--success-bg)',
                border: '1px solid var(--success-border)',
                borderRadius: 'var(--radius-sm)',
                padding: '16px',
                textAlign: 'center',
              }}
            >
              <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#065f46' }}>
                PROJECTED ESTIMATED COST:
              </span>
              <div className="mono" style={{ fontSize: '2rem', fontWeight: 700, color: '#065f46', marginTop: '4px' }}>
                {currency}{customCost !== null ? customCost : (customKwh * tariff).toFixed(2)}
              </div>
              <p style={{ fontSize: '0.7rem', color: '#047857', marginTop: '4px' }}>
                At {currency}{tariff}/kWh tariff rate. Academic software simulation.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
