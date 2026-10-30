import React from 'react';
import {
  Info,
  Zap,
  Activity,
  Shield,
  Brain,
  Cpu,
  Layers,
  ArrowRight,
  Code2,
  AlertTriangle,
} from 'lucide-react';

export default function About() {
  return (
    <div className="page-container">
      {/* Prominent Mandatory Academic Disclosure */}
      <div
        className="card"
        style={{
          borderLeft: '4px solid var(--warning)',
          backgroundColor: '#fffdfa',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
          <AlertTriangle size={24} color="var(--warning)" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#92400e', marginBottom: '4px' }}>
              Academic Prototype Simulation Disclosure
            </h3>
            <p style={{ fontSize: '0.8125rem', color: '#78350f', lineHeight: 1.5 }}>
              <strong>PowerGuard is an academic software simulation.</strong> It does not connect to physical electrical
              sensors and is not a certified electrical safety or protection system. It generates synthetic telemetry
              for computer science research, analytics visualization, and machine learning evaluation. Never use this software
              as a substitute for physical circuit breakers, ground fault interrupters (GFCI), or certified electrical monitoring hardware.
            </p>
          </div>
        </div>
      </div>

      {/* Project Overview */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            <Zap size={18} color="var(--primary)" />
            <span>Project Overview & Motivation</span>
          </h3>
        </div>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-main)', lineHeight: 1.6 }}>
          <strong>PowerGuard</strong> is an intelligent electrical load monitoring and anomaly detection platform
          designed to simulate, monitor, and analyze electrical power consumption patterns. In modern power systems,
          continuous monitoring helps identify energy waste, unbalanced inductive loads, harmonic distortions, and
          overload conditions before they cause equipment damage or power failure.
        </p>
      </div>

      {/* Mathematical Formulas & Electrical Theory */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            <Code2 size={18} color="var(--primary)" />
            <span>Electrical Calculation Engine Formulations</span>
          </h3>
        </div>

        <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginBottom: '14px' }}>
          PowerGuard models a single-phase Alternating Current (AC) electrical system with nominal RMS voltage of 230V, 50Hz:
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
          <div className="formula-box">
            <div className="formula-title">1. Apparent Power (S):</div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Total power supplied to the circuit in Volt-Amperes (VA):</p>
            <div className="formula-code">S = Voltage (V) × Current (A)</div>
          </div>

          <div className="formula-box">
            <div className="formula-title">2. Active Real Power (P):</div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Useful work dissipated as heat or mechanical energy in Watts (W):</p>
            <div className="formula-code">P = V × I × cos(φ) = S × PF</div>
          </div>

          <div className="formula-box">
            <div className="formula-title">3. Reactive Power (Q):</div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Power oscillating between magnetic/electric fields in var:</p>
            <div className="formula-code">Q = √( max(0, S² - P²) )</div>
          </div>

          <div className="formula-box">
            <div className="formula-title">4. Energy Accumulation (kWh):</div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Discrete integration of active power over simulated elapsed time:</p>
            <div className="formula-code">Energy (kWh) = (Power (W) × dt (s)) / 3,600,000</div>
          </div>

          <div className="formula-box">
            <div className="formula-title">5. Estimated Financial Cost:</div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Projected billing based on configurable tariff rate:</p>
            <div className="formula-code">Cost = Energy (kWh) × Configured Tariff (₹/kWh)</div>
          </div>
        </div>
      </div>

      {/* Overload Detection & Rule Engine */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            <Shield size={18} color="var(--primary)" />
            <span>Rule-Based Overload Detection Architecture</span>
          </h3>
        </div>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-main)', lineHeight: 1.6, marginBottom: '12px' }}>
          The rule engine operates instantaneously on every ingested reading, checking parameter boundaries:
        </p>
        <ul style={{ paddingLeft: '20px', fontSize: '0.8125rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <li>
            <strong>Overcurrent Protection:</strong> Current exceeding configured threshold (default 16A) generates a <span className="badge badge-critical">CRITICAL</span> alert. Currents exceeding 85% of capacity generate a <span className="badge badge-warning">WARNING</span>.
          </li>
          <li>
            <strong>Power Capacity Protection:</strong> Active power dissipation exceeding max threshold (default 3600W) triggers critical alarm.
          </li>
          <li>
            <strong>Voltage Boundary Evaluation:</strong> Monitored RMS voltage must remain within nominal range (207V - 253V, ±10% nominal).
          </li>
          <li>
            <strong>Power Factor Degradation:</strong> Identifies poor phase alignment (&lt; 0.80) characteristic of inefficient inductive loads.
          </li>
          <li>
            <strong>Alert Cooldown & Deduplication:</strong> Prevents database flooding during continuous overload conditions by enforcing configurable cooldown intervals.
          </li>
        </ul>
      </div>

      {/* Machine Learning Isolation Forest */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            <Brain size={18} color="var(--purple)" />
            <span>Unsupervised Anomaly Detection via Isolation Forest</span>
          </h3>
        </div>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-main)', lineHeight: 1.6, marginBottom: '12px' }}>
          Unlike static rule thresholds, complex electrical faults (such as harmonic distortion, insulation breakdown, or subtle power theft)
          do not always exceed gross current limits. PowerGuard employs Scikit-learn's <strong>Isolation Forest</strong> algorithm:
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '14px', fontSize: '0.8125rem' }}>
          <div style={{ backgroundColor: '#f8fafc', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
            <strong>Feature Engineering:</strong>
            <p style={{ color: 'var(--text-muted)', marginTop: '4px' }}>
              Vector includes Voltage, Current, Active Power, Apparent Power, Power Factor, Rolling Mean Power, and Power Deviation.
            </p>
          </div>
          <div style={{ backgroundColor: '#f8fafc', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
            <strong>Isolation Trees:</strong>
            <p style={{ color: 'var(--text-muted)', marginTop: '4px' }}>
              Isolates observations by randomly selecting a feature and splitting value. Anomalies require fewer partitions to isolate.
            </p>
          </div>
          <div style={{ backgroundColor: '#f8fafc', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
            <strong>Anomaly Explainability:</strong>
            <p style={{ color: 'var(--text-muted)', marginTop: '4px' }}>
              Identifies which specific electrical dimensions contributed most significantly to the outlier score.
            </p>
          </div>
        </div>
      </div>

      {/* Future Hardware Compatibility Architecture */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            <Layers size={18} color="var(--primary)" />
            <span>Future Hardware Adapter Architecture</span>
          </h3>
        </div>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-main)', lineHeight: 1.6, marginBottom: '12px' }}>
          Although this implementation is entirely software-based, PowerGuard was intentionally architected with a decoupled
          data ingestion interface. A future developer can connect physical microcontrollers (e.g. ESP32, Arduino, Raspberry Pi)
          with current sensors (ACS712, SCT-013) and voltage transformers (ZMPT101B) by providing an ingestion adapter:
        </p>
        <div className="formula-box">
          <div className="formula-title">Data Ingestion Schema:</div>
          <div className="formula-code">
            {`{ "timestamp": ISO8601, "voltage": float, "current": float, "power_factor": float, "simulated_elapsed_seconds": float }`}
          </div>
        </div>
        <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '8px' }}>
          The backend REST API or a future MQTT subscriber can route physical readings directly into the existing
          calculation engine, overload evaluator, database models, and ML detector without altering business logic.
        </p>
      </div>
    </div>
  );
}
