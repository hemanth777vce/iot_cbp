# PowerGuard — Intelligent Electrical Load Monitoring & Anomaly Detection Platform

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask 3.1+](https://img.shields.io/badge/Flask-3.1%2B-green.svg)](https://flask.palletsprojects.com/)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)
[![Vite 5](https://img.shields.io/badge/Vite-5-646cff.svg)](https://vitejs.dev/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Isolation%20Forest-orange.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **ACADEMIC SIMULATION NOTICE:** PowerGuard is an academic software simulation and energy analytics platform. It generates realistic, physically consistent AC waveforms for software demonstration and analysis. It does **not** physically measure live mains electricity, physically trip circuit breakers, or replace certified physical electrical safety protection devices.

---

## 1. Project Overview

**PowerGuard** is a full-stack, software-based electrical load monitoring, analytics, and anomaly detection platform. It couples a realistic AC single-phase data simulator with an electrical calculation engine, a rule-based overload evaluator, an unsupervised machine-learning anomaly detector (Scikit-learn Isolation Forest), and an interactive React web dashboard.

The architecture is strictly decoupled so that physical current transformers (e.g. SCT-013) and voltage sensors can be connected in the future via a clean ingestion contract without modifying core analytics.

---

## 2. Key Features

- **Realistic Electrical Simulator**: Simulates 230V AC parameters across 6 distinct load regimes: *Normal Household*, *High Consumption*, *Fluctuating / Inductive*, *Standby / Idle*, *Overload Scenario*, and *Anomalous Profile*.
- **Physical Electrical Engine**: Accurately computes Apparent Power ($S$), Active Power ($P$), Reactive Power ($Q$), discrete Energy integration ($\text{kWh}$), and tariff cost estimates.
- **Rule-Based Overload Protection**: Multi-tier detection (Normal, Warning, Critical) with cooldown deduplication and sustained violation persistence tracking to eliminate alert storms.
- **Machine Learning Anomaly Detection**: Unsupervised Isolation Forest trained on 7 engineered multivariate features, generating outlier scores and root-cause natural language explanations.
- **Modern Responsive Dashboard**: Built with React 18, Vite, Recharts, and Lucide React featuring live oscilloscope charts, dual-axis telemetry, financial estimators, and event logs.
- **Demo Data Generator**: Instantly produces hours of realistic, continuous telemetry with natural fluctuations, overload intervals, and ML anomalies for lab demonstrations.
- **Decoupled Ingestion Interface**: Ready for future microcontroller (ESP32 / Arduino / Raspberry Pi) hardware sensor integration.

---

## 3. Technology Stack

- **Frontend**: React 18, Vite 5, Recharts 2, Lucide React icons, Responsive CSS3 design system.
- **Backend**: Python 3 (3.10+), Flask 3.1, Flask-CORS, SQLAlchemy 2.1 ORM, NumPy, Pandas, Scikit-learn.
- **Database**: SQLite 3 with non-destructive auto-initialization and indexes.
- **Testing**: Pytest 9.2 with 32 automated unit and integration tests.

---

## 4. Project Folder Structure

```
PowerGuard/
├── backend/
│   ├── app.py                      # Application factory and route registration
│   ├── config.py                   # Default thresholds, tariffs, and validation rules
│   ├── database.py                 # SQLAlchemy session and schema management
│   ├── models.py                   # ElectricalReading, Alert, SystemEvent, AppSetting
│   ├── conftest.py                 # Pytest configuration and sys.path hook
│   ├── requirements.txt            # Python dependencies
│   ├── README.md                   # Backend architecture documentation
│   ├── instance/                   # Local SQLite database (powerguard.db)
│   ├── routes/
│   │   ├── dashboard.py            # Overview metrics, trends, and recent events
│   │   ├── readings.py             # Paginated readings, latest, and aggregates
│   │   ├── alerts.py               # Alert query, search, and acknowledgment
│   │   ├── analytics.py            # Energy bins, power trends, and cost estimates
│   │   ├── simulation.py           # Simulator controls, demo data generator, reset
│   │   ├── settings.py             # System parameters and threshold configuration
│   │   ├── ml.py                   # Isolation Forest training and predictions
│   │   └── health.py               # Health probe endpoint
│   ├── services/
│   │   ├── simulator.py            # Thread-safe AC load waveform generator
│   │   ├── electrical_calculator.py# S, P, Q, kWh, and cost formulations
│   │   ├── overload_detector.py    # Rule engine with cooldown and persistence
│   │   ├── anomaly_detector.py     # Isolation Forest model and explainability
│   │   ├── analytics_service.py    # Trend aggregation and DOD comparison
│   │   └── alert_service.py        # Alert persistence and summary metrics
│   └── tests/
│       ├── test_calculations.py    # Electrical formulas and invalid input tests
│       ├── test_simulator.py       # Simulator outputs, seeds, and state cycles
│       ├── test_overload.py        # Overload rules, cooldown, and persistence
│       ├── test_anomaly.py         # ML fallback, training, and outlier detection
│       └── test_api.py             # API endpoints, pagination, and error handling
├── frontend/
│   ├── index.html                  # HTML5 entry point
│   ├── package.json                # NPM configuration
│   ├── vite.config.js              # Vite server and /api proxy configuration
│   └── src/
│       ├── main.jsx                # React root mount
│       ├── App.jsx                 # Main navigation and state shell
│       ├── api/
│       │   └── client.js           # Centralized backend API client
│       ├── components/
│       │   ├── Sidebar.jsx         # Dark navy navigation sidebar
│       │   ├── Header.jsx          # Header with clock, simulation pill, and alerts
│       │   ├── MetricCard.jsx      # Rounded status KPI cards
│       │   ├── LiveChart.jsx       # Recharts responsive line & dual-axis chart
│       │   ├── AlertList.jsx       # Event list with acknowledgment controls
│       │   ├── StatusBadge.jsx     # Visual indicator badges
│       │   ├── LoadingState.jsx    # Spinner component
│       │   └── ErrorState.jsx      # Error card with retry trigger
│       ├── pages/
│       │   ├── Dashboard.jsx       # System overview, telemetry, and quick demo
│       │   ├── LiveMonitoring.jsx  # Oscilloscope view and streaming table
│       │   ├── Analytics.jsx       # Historical kWh trends and tariff calculator
│       │   ├── Alerts.jsx          # Alarms management and search filters
│       │   ├── DeviceSimulator.jsx # Simulator panel and one-click scenarios
│       │   ├── Settings.jsx        # Configurable limits, tariffs, and ML hyperparameters
│       │   └── About.jsx           # Electrical theory and architecture disclosures
│       └── styles/
│           ├── global.css          # Design tokens, variables, and typography
│           ├── dashboard.css       # Layout, sidebar, and header styles
│           ├── components.css      # Tables, charts, forms, and simulator pills
│           └── responsive.css      # Breakpoints for tablet and mobile
├── docs/
│   ├── ARCHITECTURE.md             # In-depth architectural design document
│   ├── TESTING.md                  # Test execution log and coverage matrix
│   └── PROJECT_REPORT.md           # Formal college project report
├── start.bat                       # One-click Windows launch batch script
├── start.ps1                       # One-click Windows PowerShell launch script
├── .gitignore
└── README.md
```

---

## 5. Prerequisites

Before running PowerGuard on Windows, verify you have installed:
1. **Python 3.10+** (tested on Python 3.13): Ensure *"Add Python to PATH"* is checked during installation.
2. **Node.js 18+ and npm** (tested on Node v24 and npm 11).

---

## 6. Installation & Startup Instructions (Windows)

### Option A: One-Click Startup (Recommended)
Simply double-click `start.bat` in the project root folder (or right-click `start.ps1` and select *Run with PowerShell*).

The script automatically:
1. Verifies Python and Node.js availability.
2. Checks and installs any missing backend Python packages.
3. Installs frontend npm dependencies if missing.
4. Initializes the SQLite database schema non-destructively.
5. Launches the Flask backend on `http://127.0.0.1:5000`.
6. Launches the Vite development server on `http://localhost:5173`.
7. Automatically opens the dashboard in your default web browser.

---

### Option B: Manual Step-by-Step Setup

#### Step 1: Backend Setup
Open a terminal in the project root:
```powershell
# Navigate to backend directory
cd backend

# Install Python dependencies
python -m pip install -r requirements.txt

# Start the Flask backend server (binds to localhost:5000)
python app.py
```

#### Step 2: Frontend Setup
Open a second terminal window in the project root:
```powershell
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the Vite development server (binds to localhost:5173)
npm run dev
```
Open your browser and navigate to: **`http://localhost:5173`**

---

## 7. How to Demonstrate Key Features

### A. Demonstrating Normal Operation
1. Navigate to the **Device Simulator** tab.
2. Click **Start Simulator**.
3. Select **Normal Household** profile (or click **Normal Operation** under One-Click Scenarios).
4. Navigate to **Dashboard** or **Live Monitoring**:
   - Voltage will hover steadily near 230V ($\pm 2$V).
   - Current draw will register 3A–5.5A.
   - System Status will read **NORMAL** with green indicators.

### B. Demonstrating Overload Detection
1. Open the **Device Simulator** tab.
2. Click the **Overload Scenario** button.
3. Observe the immediate behavior:
   - Current surges to **19A–23A** (exceeding the 16A limit).
   - Active Power jumps to **4200W–5000W** (exceeding the 3600W limit).
   - System status instantly transitions to <span style="color:red">**CRITICAL**</span>.
   - An alert appears in the **Alerts & Events** page: `Critical Current Overload: Observed 20.45 A exceeds limit of 16.00 A`.
   - Repeated alerts are throttled by the 15-second cooldown deduplication engine.

### C. Demonstrating Machine Learning Anomaly Detection
1. Open the **Device Simulator** tab.
2. Under One-Click Scenarios, click **Anomaly Scenario**.
3. The simulator injects an irregular electrical profile:
   - Power Factor drops severely to **0.38–0.45** (unusual lagging reactive load).
   - Instantaneous current oscillates abnormally.
4. Click **Train / Retrain Model** on the Isolation Forest card.
5. Once trained on the historical baseline, Isolation Forest detects the multi-dimensional outlier and registers an alert under **Alerts & Events** with source `ANOMALY_DETECTOR`.

### D. Generating a Multi-Hour Demonstration Dataset
On a fresh install or empty database:
1. On the **Dashboard**, click **Generate 6h Demo Data** (or use the button in **Energy Analytics**).
2. The generator synthesizes 120 chronological readings across multiple load profiles, fits the Isolation Forest model, and populates time-series consumption graphs, DOD comparisons, and alerts.

---

## 8. Running Automated Tests

Run the comprehensive Pytest suite from the repository root:

```powershell
python -m pytest backend/tests -v
```

**Verified Test Result:**
- `32 passed in 6.09s` (100% pass rate).

To verify the frontend production build:
```powershell
npm run build --prefix frontend
```
**Verified Build Result:**
- `✓ 2388 modules transformed. Built in 10.89s.`

---

## 9. API Endpoint Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | System health check and mode disclosure |
| `GET` | `/api/dashboard/summary` | Real-time electrical parameters, status, and alerts |
| `GET` | `/api/dashboard/recent-readings` | Recent time-series telemetry points |
| `GET` | `/api/dashboard/recent-events` | System activity audit log |
| `GET` | `/api/readings` | Paginated readings with profile and date filters |
| `GET` | `/api/readings/latest` | Most recent single electrical observation |
| `GET` | `/api/readings/aggregates` | Min, max, and average statistics across parameters |
| `GET` | `/api/alerts` | Paginated alerts with severity, source, and search filters |
| `GET` | `/api/alerts/<id>` | Detail view for a specific alert |
| `PATCH` | `/api/alerts/<id>/acknowledge`| Acknowledge an alert without mutating telemetry |
| `GET` | `/api/alerts/summary` | Aggregate counts (total, critical, warning, unacked) |
| `GET` | `/api/analytics/consumption` | Binned energy consumption trends (kWh) |
| `GET` | `/api/analytics/power-trends` | Real and apparent power trend points |
| `GET` | `/api/analytics/voltage-trends`| RMS Voltage history |
| `GET` | `/api/analytics/current-trends`| RMS Current history |
| `GET` | `/api/analytics/daily-summary` | Today vs yesterday comparison and cost |
| `GET` | `/api/analytics/cost-estimate` | Dynamic cost calculation for arbitrary kWh |
| `GET` | `/api/analytics/profiles` | Operational load profile distribution breakdown |
| `GET` | `/api/simulation/status` | Current simulator state, speed, and active violations |
| `POST`| `/api/simulation/start` | Start the background waveform simulator |
| `POST`| `/api/simulation/pause` | Pause active telemetry generation |
| `POST`| `/api/simulation/resume` | Resume paused simulation |
| `POST`| `/api/simulation/stop` | Terminate background worker cleanly |
| `POST`| `/api/simulation/profile` | Switch load regime (normal, high, overload, etc.) |
| `POST`| `/api/simulation/speed` | Adjust simulation speed multiplier (0.1x to 10.0x) |
| `POST`| `/api/simulation/generate-demo-data` | Ingest multi-hour synthetic dataset |
| `POST`| `/api/simulation/reset` | Clear database with explicit confirmation |
| `GET` | `/api/settings` | Retrieve active thresholds and validation rules |
| `PATCH`| `/api/settings` | Update thresholds, tariffs, and hyperparameters |
| `POST`| `/api/settings/reset` | Restore default system settings |
| `GET` | `/api/ml/status` | Current Isolation Forest model state and sample count |
| `POST`| `/api/ml/train` | Train or retrain Isolation Forest on historical data |
| `GET` | `/api/ml/anomalies` | Query outlier events flagged by machine learning |

---

## 10. Troubleshooting

- **Port 5000 in use**:
  If port 5000 is occupied by another process on Windows, run the backend on a different port:
  ```powershell
  $env:PORT="5001"; python backend/app.py
  ```
  And update `frontend/vite.config.js` proxy target accordingly.
- **Node.js dependencies not found**:
  Navigate to `frontend/` and run `npm install`.
- **Database lock**:
  If SQLite reports a database lock, ensure no background pytest instances are holding open connections, or delete `backend/instance/powerguard.db` to allow auto-reinitialization.

---

## 11. Known Limitations & Future Enhancements

- **Limitations**: Single-phase 230V AC model only; software simulation does not physically trip mechanical hardware; not certified for life-safety systems.
- **Future Enhancements**: MQTT ingestion adapter for physical ESP32 / Arduino microcontrollers, polyphase three-phase calculation engine, and LSTM time-series forecasting.
