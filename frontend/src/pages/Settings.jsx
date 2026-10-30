import React, { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon,
  Save,
  RotateCcw,
  CheckCircle,
  AlertCircle,
  Sliders,
  DollarSign,
  Shield,
  Brain,
  Zap,
} from 'lucide-react';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import { api } from '../api/client';

export default function Settings() {
  const [settings, setSettings] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [showResetModal, setShowResetModal] = useState(false);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const res = await api.getSettings();
      setSettings(res.settings || {});
      setFormData(res.settings || {});
      setErrorMsg(null);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to load system settings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleChange = (key, value) => {
    setFormData((prev) => ({
      ...prev,
      [key]: value,
    }));
    setSuccessMsg(null);
    setErrorMsg(null);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg(null);
    setErrorMsg(null);

    try {
      // Convert numbers appropriately
      const payload = {
        electricity_tariff: Number(formData.electricity_tariff),
        max_current: Number(formData.max_current),
        max_active_power: Number(formData.max_active_power),
        voltage_min: Number(formData.voltage_min),
        voltage_max: Number(formData.voltage_max),
        min_power_factor: Number(formData.min_power_factor),
        alert_cooldown_seconds: Number(formData.alert_cooldown_seconds),
        persistence_duration_seconds: Number(formData.persistence_duration_seconds),
        anomaly_contamination: Number(formData.anomaly_contamination),
        anomaly_min_samples: Number(formData.anomaly_min_samples),
        default_load_profile: formData.default_load_profile,
      };

      const res = await api.updateSettings(payload);
      setSettings(res.settings);
      setFormData(res.settings);
      setSuccessMsg('Settings updated and persisted successfully!');
    } catch (err) {
      setErrorMsg(err.details?.error || err.message || 'Failed to update settings');
    } finally {
      setSaving(false);
    }
  };

  const handleResetDefaults = async () => {
    try {
      const res = await api.resetSettings();
      setSettings(res.settings);
      setFormData(res.settings);
      setShowResetModal(false);
      setSuccessMsg('System settings restored to original defaults.');
    } catch (err) {
      alert('Failed to reset settings: ' + err.message);
    }
  };

  if (loading && !settings) {
    return <LoadingState message="Loading configuration parameters..." />;
  }

  return (
    <div className="page-container">
      {successMsg && (
        <div className="card" style={{ backgroundColor: 'var(--success-bg)', borderColor: 'var(--success-border)', padding: '14px 18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#065f46', fontSize: '0.875rem', fontWeight: 500 }}>
            <CheckCircle size={18} />
            <span>{successMsg}</span>
          </div>
        </div>
      )}

      {errorMsg && (
        <div className="card" style={{ backgroundColor: 'var(--danger-bg)', borderColor: 'var(--danger-border)', padding: '14px 18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#991b1b', fontSize: '0.875rem', fontWeight: 500 }}>
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
        </div>
      )}

      <form onSubmit={handleSave}>
        {/* Electrical Safety Limits */}
        <div className="card" style={{ marginBottom: '20px' }}>
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <Shield size={18} color="var(--primary)" />
                <span>Overload Detection & Safety Thresholds</span>
              </h3>
              <p className="card-subtitle">Configurable limits governing rule-based overload and warning alerts</p>
            </div>
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Maximum Current Limit (A):</label>
              <input
                type="number"
                step="0.5"
                min="1.0"
                max="100.0"
                className="form-input mono"
                value={formData.max_current ?? 16.0}
                onChange={(e) => handleChange('max_current', e.target.value)}
              />
              <span className="form-help">Currents equal or exceeding this threshold trigger CRITICAL overload alarms.</span>
            </div>

            <div className="form-group">
              <label className="form-label">Maximum Active Power (W):</label>
              <input
                type="number"
                step="50"
                min="100"
                max="50000"
                className="form-input mono"
                value={formData.max_active_power ?? 3600.0}
                onChange={(e) => handleChange('max_active_power', e.target.value)}
              />
              <span className="form-help">Circuit power rating. Exceeding triggers power overload alert.</span>
            </div>

            <div className="form-group">
              <label className="form-label">Minimum RMS Voltage (V):</label>
              <input
                type="number"
                step="1"
                min="150"
                max="240"
                className="form-input mono"
                value={formData.voltage_min ?? 207.0}
                onChange={(e) => handleChange('voltage_min', e.target.value)}
              />
              <span className="form-help">Lower voltage boundary (typically -10% of 230V nominal).</span>
            </div>

            <div className="form-group">
              <label className="form-label">Maximum RMS Voltage (V):</label>
              <input
                type="number"
                step="1"
                min="220"
                max="300"
                className="form-input mono"
                value={formData.voltage_max ?? 253.0}
                onChange={(e) => handleChange('voltage_max', e.target.value)}
              />
              <span className="form-help">Upper voltage boundary (typically +10% of 230V nominal).</span>
            </div>

            <div className="form-group">
              <label className="form-label">Minimum Acceptable Power Factor:</label>
              <input
                type="number"
                step="0.05"
                min="0.10"
                max="1.00"
                className="form-input mono"
                value={formData.min_power_factor ?? 0.80}
                onChange={(e) => handleChange('min_power_factor', e.target.value)}
              />
              <span className="form-help">Power factor below this flags inefficient inductive/capacitive distortion.</span>
            </div>

            <div className="form-group">
              <label className="form-label">Alert Cooldown Window (seconds):</label>
              <input
                type="number"
                step="1"
                min="1"
                max="300"
                className="form-input mono"
                value={formData.alert_cooldown_seconds ?? 15.0}
                onChange={(e) => handleChange('alert_cooldown_seconds', e.target.value)}
              />
              <span className="form-help">Prevents alert flood during persistent violations by throttling repeated alarms.</span>
            </div>

            <div className="form-group">
              <label className="form-label">Persistence Duration (seconds):</label>
              <input
                type="number"
                step="0.5"
                min="0.0"
                max="60.0"
                className="form-input mono"
                value={formData.persistence_duration_seconds ?? 3.0}
                onChange={(e) => handleChange('persistence_duration_seconds', e.target.value)}
              />
              <span className="form-help">Duration condition must hold before critical alert is raised.</span>
            </div>
          </div>
        </div>

        {/* Electricity Tariff & Financial Parameters */}
        <div className="card" style={{ marginBottom: '20px' }}>
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <DollarSign size={18} color="var(--success)" />
                <span>Financial & Tariff Configuration</span>
              </h3>
              <p className="card-subtitle">Defines the unit price used for daily electricity bill estimations</p>
            </div>
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Electricity Tariff Rate (₹ per kWh):</label>
              <input
                type="number"
                step="0.25"
                min="0.5"
                max="100.0"
                className="form-input mono"
                value={formData.electricity_tariff ?? 7.50}
                onChange={(e) => handleChange('electricity_tariff', e.target.value)}
              />
              <span className="form-help">Configured energy price per kilowatt-hour consumed.</span>
            </div>

            <div className="form-group">
              <label className="form-label">Default Simulation Profile:</label>
              <select
                className="form-select"
                value={formData.default_load_profile || 'normal'}
                onChange={(e) => handleChange('default_load_profile', e.target.value)}
              >
                <option value="normal">Normal Household</option>
                <option value="high">High Consumption</option>
                <option value="fluctuating">Fluctuating / Inductive</option>
                <option value="standby">Standby / Low Power</option>
                <option value="overload">Overload Scenario</option>
                <option value="anomalous">Anomalous Profile</option>
              </select>
              <span className="form-help">Initial load profile loaded upon simulator startup.</span>
            </div>
          </div>
        </div>

        {/* Machine Learning Isolation Forest Hyperparameters */}
        <div className="card" style={{ marginBottom: '20px' }}>
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <Brain size={18} color="var(--purple)" />
                <span>Machine Learning Anomaly Parameters</span>
              </h3>
              <p className="card-subtitle">Hyperparameters tuning Scikit-learn's Isolation Forest anomaly detector</p>
            </div>
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Contamination Factor (0.01 - 0.25):</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                max="0.25"
                className="form-input mono"
                value={formData.anomaly_contamination ?? 0.05}
                onChange={(e) => handleChange('anomaly_contamination', e.target.value)}
              />
              <span className="form-help">Expected proportion of outliers in the training population (0.05 = 5%).</span>
            </div>

            <div className="form-group">
              <label className="form-label">Minimum Training Samples:</label>
              <input
                type="number"
                step="5"
                min="10"
                max="500"
                className="form-input mono"
                value={formData.anomaly_min_samples ?? 30}
                onChange={(e) => handleChange('anomaly_min_samples', e.target.value)}
              />
              <span className="form-help">Minimum required historical readings required before model fitting is permitted.</span>
            </div>
          </div>
        </div>

        {/* Form Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <button
            type="button"
            className="btn btn-outline-danger"
            onClick={() => setShowResetModal(true)}
          >
            <RotateCcw size={16} />
            <span>Restore Default Settings</span>
          </button>

          <button type="submit" className="btn btn-primary" disabled={saving}>
            <Save size={16} />
            <span>{saving ? 'Saving...' : 'Save Configuration'}</span>
          </button>
        </div>
      </form>

      {/* Confirmation Modal for Resetting Settings */}
      {showResetModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3 style={{ fontSize: '1.125rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '8px' }}>
              Restore Default Settings?
            </h3>
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
              Are you sure you want to revert all electrical thresholds, tariffs, and anomaly detection parameters
              to factory demo defaults?
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button className="btn btn-secondary" onClick={() => setShowResetModal(false)}>
                Cancel
              </button>
              <button className="btn btn-danger" onClick={handleResetDefaults}>
                Yes, Restore Defaults
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
