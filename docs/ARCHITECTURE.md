# PowerGuard System Architecture Documentation

## 1. Architectural Overview

PowerGuard is structured as a decoupled, multi-tier software system designed for high-resolution electrical telemetry processing, physical AC parameter simulation, rule-based overload detection, and machine-learning-driven anomaly identification.

```
+-------------------------------------------------------------------------------+
|                             Client Layer (Frontend)                          |
|  React 18 + Vite + Recharts + Lucide Icons (Single Page Application, SPA)    |
|  - Dashboard: Real-time telemetry, active power trends, VI dual-axis charts   |
|  - Live Monitoring: Waveform oscilloscope, live streaming meters, status      |
|  - Energy Analytics: Discrete kWh integration, Day-over-Day DOD, Tariff tool  |
|  - Alerts & Events: Multi-tier alarms, ML anomaly flags, persistent ack      |
|  - Simulator Control Plane: Profile regimes, speed multiplier, scenario test  |
+-------------------------------------------------------------------------------+
                                    |
                            HTTP REST / JSON
                                    v
+-------------------------------------------------------------------------------+
|                           Application Layer (Backend)                         |
|  Python 3.13 + Flask 3.1 + Flask-CORS (Localhost REST API on Port 5000)      |
|                                                                               |
|  [REST API Blueprints]                                                        |
|   /api/health       /api/dashboard     /api/readings     /api/alerts         |
|   /api/analytics    /api/simulation    /api/settings     /api/ml             |
|                                                                               |
|  [Core Domain Services]                                                       |
|   +-----------------------+     +-----------------------+                    |
|   |  Simulator Engine     | --> | Electrical Calculator |                    |
|   |  - 6 Load Profiles    |     | - Apparent (S = V·I)  |                    |
|   |  - Thread-safe Runner |     | - Active (P = S·PF)   |                    |
|   |  - Deterministic RNG  |     | - Reactive (Q)        |                    |
|   +-----------------------+     | - Energy (kWh = ∫Pdt) |                    |
|               |                 +-----------------------+                    |
|               v                             |                                |
|   +-----------------------+                 v                                |
|   |  Overload Detector    |     +-----------------------+                    |
|   |  - Rule Verification  |     |   Anomaly Detector    |                    |
|   |  - Alert Cooldown     |     | - Isolation Forest    |                    |
|   |  - Sustained Violations     | - Feature Engineering |                    |
|   +-----------------------+     | - Root-Cause Reasoner |                    |
|                                 +-----------------------+                    |
+-------------------------------------------------------------------------------+
                                    |
                              SQLAlchemy ORM
                                    v
+-------------------------------------------------------------------------------+
|                              Persistence Layer                                |
|  SQLite 3 Database (instance/powerguard.db)                                   |
|  - electrical_readings: High-resolution time-series electrical measurements   |
|  - alerts: Rule overload warnings, critical breaches, and ML anomalies      |
|  - system_events: Audited simulation state transitions and operations        |
|  - app_settings: Persisted operational limits, tariffs, and hyperparameters  |
+-------------------------------------------------------------------------------+
```

---

## 2. Component Descriptions

### 2.1 Electrical Simulator (`services/simulator.py`)
- Employs a thread-safe singleton background worker with `threading.Event` controls (`start`, `pause`, `resume`, `stop`).
- Generates physically consistent AC waveforms across six operational profiles:
  1. **Normal Household**: Nominal 230V RMS, 2.5A–5.5A, 0.94 PF.
  2. **High Consumption**: 12.0A–15.5A heavy appliance loading (~3200W).
  3. **Fluctuating / Inductive**: Dynamic switching load with motor inrush and lower PF (0.78).
  4. **Standby / Idle**: Residual night load (< 1A) with power factor distortion.
  5. **Overload Scenario**: Intentional threshold breach (18A–24A, 4200W+) triggering critical alarms.
  6. **Anomalous Profile**: Harmonic distortion and severe power factor degradation (0.35–0.50).
- Guarantees physical invariants: $S \ge P$, $Q = \sqrt{S^2 - P^2}$, and monotonically non-decreasing energy accumulation.

### 2.2 Electrical Calculation Engine (`services/electrical_calculator.py`)
- Pure, independently testable mathematical module.
- Calculations:
  - $\text{Apparent Power } (S) = V \times I$ [Volt-Amperes, VA]
  - $\text{Active Power } (P) = V \times I \times \cos(\phi) = S \times \text{PF}$ [Watts, W]
  - $\text{Reactive Power } (Q) = \sqrt{\max(0, S^2 - P^2)}$ [Volt-Amperes Reactive, var]
  - $\text{Discrete Energy Integration } (\text{kWh}) = \frac{P \times \Delta t}{3,600,000}$
  - $\text{Estimated Electricity Cost } = \text{Energy (kWh)} \times \text{Tariff Rate (₹/kWh)}$

### 2.3 Overload Detection Engine (`services/overload_detector.py`)
- Continuous rule evaluation per ingested reading against user-configured settings:
  - `max_current` (default 16A limit)
  - `max_active_power` (default 3600W limit)
  - `voltage_min` (207V) and `voltage_max` (253V)
  - `min_power_factor` (0.80)
- **Cooldown & Deduplication**: Throttles alert generation for repeated identical violations using `(category, severity)` keyed timestamps.
- **Persistence Duration**: Ensures temporary transients do not prematurely trigger critical alarms when persistence duration is configured.

### 2.4 Unsupervised Anomaly Detection (`services/anomaly_detector.py`)
- Implements Scikit-learn's **Isolation Forest** unsupervised algorithm.
- Operates on a 7-dimensional engineered feature space:
  1. Voltage ($V$)
  2. Current ($I$)
  3. Active Power ($P$)
  4. Apparent Power ($S$)
  5. Power Factor ($\text{PF}$)
  6. Rolling Mean Power (5-reading moving baseline)
  7. Power Deviation ($|P - \bar{P}_{\text{rolling}}|$)
- Computes decision function outlier scores. Anomaly threshold is governed by `anomaly_contamination` (default 5%).
- Generates natural language root-cause explanations (e.g. "power factor (0.42) deviated significantly from normal mean").

---

## 3. Database Schema

### `electrical_readings`
| Column | Type | Index | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Autoincrement reading ID |
| `timestamp` | DATETIME | YES | UTC observation timestamp |
| `voltage` | FLOAT | NO | RMS Voltage (V) |
| `current` | FLOAT | NO | RMS Current (A) |
| `active_power` | FLOAT | NO | Real dissipated power (W) |
| `apparent_power`| FLOAT | NO | Total supplied power (VA) |
| `reactive_power`| FLOAT | NO | Quadrature reactive power (var) |
| `power_factor` | FLOAT | NO | $\cos(\phi)$ dimension in [0.0, 1.0] |
| `energy_kwh` | FLOAT | NO | Cumulative simulated meter reading |
| `load_profile` | VARCHAR(50)| YES | Active operational regime |
| `simulated_elapsed_seconds` | FLOAT | NO | Time delta for step integration |

### `alerts`
| Column | Type | Index | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Alert ID |
| `timestamp` | DATETIME | YES | Occurrence timestamp |
| `severity` | VARCHAR(20)| YES | `WARNING`, `CRITICAL`, `INFO` |
| `category` | VARCHAR(50)| NO | `CURRENT_OVERLOAD`, `ML_ANOMALY`, etc. |
| `parameter` | VARCHAR(50)| NO | Parameter violated |
| `observed_value`| FLOAT | NO | Telemetry value recorded |
| `threshold_value`| FLOAT | NO | Threshold breached |
| `message` | TEXT | NO | Human-readable alert summary |
| `source` | VARCHAR(50)| NO | `RULE_ENGINE` or `ANOMALY_DETECTOR` |
| `acknowledged` | BOOLEAN | YES | Whether user has acknowledged |
| `acknowledged_at`| DATETIME| NO | Timestamp of acknowledgment |

### `app_settings`
| Column | Type | Index | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Setting ID |
| `key` | VARCHAR(100)| UNIQUE | Parameter key (e.g., `max_current`) |
| `value` | VARCHAR(255)| NO | Value serialized as string |
| `updated_at` | DATETIME | NO | Last modified timestamp |

### `system_events`
| Column | Type | Index | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Event ID |
| `timestamp` | DATETIME | YES | Event timestamp |
| `event_type` | VARCHAR(50)| YES | Event classification |
| `description` | TEXT | NO | Descriptive audit log |

---

## 4. Hardware Decoupling & Future Integration Interface

PowerGuard strictly isolates telemetry generation from domain analytics. To connect physical IoT microcontrollers (ESP32, Arduino, Raspberry Pi) with hardware current transformers (SCT-013) and voltage sensors (ZMPT101B), implement the following adapter interface:

```
[Physical Sensors] -> [ADC / ESP32] -> [HTTP POST /api/readings/ingest] -> [PowerGuard Engine]
```

### Ingestion Contract:
```json
{
  "voltage": 231.4,
  "current": 4.82,
  "power_factor": 0.94,
  "timestamp": "2026-10-30T15:00:00Z",
  "simulated_elapsed_seconds": 1.0
}
```
The backend automatically computes derived Apparent Power, Active Power, Reactive Power, integrates Energy (kWh), and streams the observation through both the Rule Overload Evaluator and Isolation Forest Anomaly Detector without requiring architectural modifications.
