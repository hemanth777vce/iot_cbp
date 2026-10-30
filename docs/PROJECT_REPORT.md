# Academic Project Report: PowerGuard

## Intelligent Electrical Load Monitoring and Anomaly Detection Platform

---

### Abstract

Electrical energy management and real-time load analytics are vital for preventing electrical distribution failures, mitigating overload conditions, and optimizing industrial and commercial energy consumption. This project presents **PowerGuard**, a full-stack, software-based electrical load monitoring, analytics, and anomaly detection platform. PowerGuard couples a physics-consistent alternating current (AC) single-phase data simulator with an electrical calculation engine, a rule-based threshold violation detector, and an unsupervised Machine Learning (Isolation Forest) anomaly detector. The platform is backed by a Python Flask REST API, a persistent SQLite database managed via SQLAlchemy ORM, and a responsive React.js dashboard utilizing Recharts for data visualization. Automated test suites verify 32 distinct backend test cases encompassing parameter calculations, deterministic simulation, cooldown deduplication, and anomaly identification. The architecture maintains a decoupled hardware ingestion interface, allowing future seamless integration with physical microcontroller-based current and voltage sensors.

---

### 1. Introduction

Electrical power systems require continuous monitoring to ensure that operating parameters—such as RMS Voltage, Current draw, Active Power, and Power Factor—remain within safety and equipment rating thresholds. Sudden surges, sustained overloads, and harmonic phase shifts can degrade transformer lifespans, overheat cables, and lead to fire hazards or unplanned blackouts.

Traditionally, monitoring systems have relied on costly proprietary Supervisory Control and Data Acquisition (SCADA) platforms or basic multimeter readings. **PowerGuard** bridges the gap by providing an open, extensible, full-stack software platform that simulates complex electrical regimes, calculates derived engineering parameters in real time, and identifies statistical and threshold anomalies.

---

### 2. Problem Statement

Many educational and developmental power monitoring initiatives face significant hurdles:
1. **Safety and Hardware Overhead**: Prototyping on real 230V mains introduces severe physical shock hazards and requires expensive certified testbenches.
2. **Static Rule Limitations**: Simple threshold alarms fail to identify subtle multivariate anomalies such as severe power factor degradation, harmonic oscillations, or unexpected consumption patterns that remain below maximum breaker capacity.
3. **Coupled Codebases**: Existing demonstration applications tightly couple sensor reading loops to user interfaces, preventing clean migration between simulated testing and physical hardware deployment.

---

### 3. Objectives

The primary objectives of the PowerGuard project are:
1. To engineer a realistic, configurable software electrical simulator modeling single-phase AC parameters (230V, 50Hz) across six representative load profiles.
2. To implement a mathematically rigorous electrical calculation engine computing Apparent Power ($S$), Active Power ($P$), Reactive Power ($Q$), integrated Energy ($\text{kWh}$), and financial cost projections.
3. To build a rule-based overload engine featuring cooldown suppression and configurable persistence to prevent alert storms.
4. To integrate an unsupervised Machine Learning anomaly detector (Isolation Forest) capable of identifying multivariate patterns that deviate from normal baselines.
5. To design an intuitive, responsive React web dashboard with real-time telemetry graphs, event alarm management, and simulator controls.
6. To enforce software reliability through automated unit and integration tests.

---

### 4. Existing Approach vs. Proposed System

| Dimension | Existing / Traditional Approach | PowerGuard Proposed System |
|---|---|---|
| **Data Source** | Tied to physical hardware or crude random number generators | Realistic physics-consistent AC simulation with 6 distinct load regimes |
| **Detection Logic** | Static, hard-coded scalar threshold checks | Hybrid: Configurable rule-based detection + Isolation Forest ML |
| **Alert Management** | Repeated alert floods during sustained overloads | Cooldown deduplication and duration persistence tracking |
| **User Experience** | Basic text terminal logs or rudimentary desktop GUIs | Modern responsive React.js SPA with Recharts time-series graphs |
| **Hardware Migration** | Complete rewrite required to swap sensors | Clean ingestion contract decoupled from business logic |

---

### 5. Requirements Specification

#### 5.1 Functional Requirements
- **FR1: Telemetry Simulation**: Ability to start, pause, resume, and stop simulation; select from Normal, High, Fluctuating, Standby, Overload, and Anomalous profiles.
- **FR2: Electrical Parameter Derivation**: Automatic real-time computation of Apparent Power, Active Power, Reactive Power, and cumulative Energy.
- **FR3: Overload Alarms**: Immediate generation and database persistence of Warning and Critical alerts when current or power limits are exceeded.
- **FR4: Unsupervised Anomaly Detection**: Feature extraction and Isolation Forest prediction yielding outlier decision scores and natural-language explanations.
- **FR5: Alert Lifecycle**: Browsing, filtering, searching, and acknowledging alerts without mutating original readings.
- **FR6: Financial Analytics**: Configurable tariff calculation translating integrated energy consumption into monetary expenditure estimates.

#### 5.2 Non-Functional Requirements
- **NFR1: Reliability**: Thread-safe background execution preventing duplicate simulator processes.
- **NFR2: Performance**: API response latency under 50ms for local database queries.
- **NFR3: Security**: Default binding strictly to localhost (`127.0.0.1`), parameterized SQL queries to prevent injection.
- **NFR4: Usability**: Responsive design accommodating desktop (1440px), tablet (1024px), and mobile (768px) viewports.

---

### 6. Technology Stack

- **Frontend**:
  - React 18.3.1 (Component-based UI)
  - Vite 5.4.8 (Fast ES-module bundler)
  - Recharts 2.12.7 (SVG data visualization)
  - Lucide React 0.453.0 (Clean icon system)
  - Vanilla CSS3 (Custom design system with CSS custom properties)
- **Backend**:
  - Python 3.13.7
  - Flask 3.1.2 & Flask-CORS 6.0.1
  - SQLAlchemy 2.1.6 (ORM & connection pooling)
  - NumPy 2.3.3 & Pandas 2.3.2 (Feature engineering)
  - Scikit-Learn 1.9.1 (Isolation Forest model)
- **Database**:
  - SQLite 3 (Lightweight, local, persistent SQL database)
- **Testing**:
  - Pytest 9.2.0 (Automated backend test suite)

---

### 7. Algorithms & Mathematical Formulas

#### 7.1 Single-Phase AC Power Relations
For an instantaneous sinusoidal voltage and current with phase displacement angle $\phi$:
$$\text{Apparent Power } S = V_{\text{RMS}} \times I_{\text{RMS}} \quad [\text{VA}]$$
$$\text{Active Power } P = V_{\text{RMS}} \times I_{\text{RMS}} \times \cos(\phi) = S \times \text{PF} \quad [\text{W}]$$
$$\text{Reactive Power } Q = \sqrt{\max\left(0, S^2 - P^2\right)} \quad [\text{var}]$$

#### 7.2 Energy Integration
Energy consumption represents the time integral of real electrical power:
$$E = \int_{0}^{T} P(t) \, dt \approx \sum_{k=1}^{N} \frac{P_k \times \Delta t_k}{3,600,000} \quad [\text{kWh}]$$

#### 7.3 Tariff Cost Estimation
$$\text{Estimated Cost} = E_{\text{consumed}} \times \text{Tariff Rate } \left(\frac{\text{₹}}{\text{kWh}}\right)$$

#### 7.4 Isolation Forest Anomaly Detection
Isolation Forest isolates anomalies by randomly partitioning feature dimensions. The anomaly score $s(x, n)$ for an observation $x$ over a sample size $n$ is given by:
$$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$
Where $h(x)$ is the path length of observation $x$ in an isolation tree, $E(h(x))$ is the expected path length over an ensemble of 100 trees, and $c(n)$ is the average path length of unsuccessful searches in a Binary Search Tree (BST):
$$c(n) = 2 \ln(n - 1) + 0.5772156649 - \frac{2(n - 1)}{n}$$
When $s \to 1$, the observation is flagged as an anomaly; when $s < 0.5$, the observation is deemed normal.

---

### 8. Implementation Details

1. **Backend Modular Architecture**:
   - Organized into dedicated service singletons (`Simulator`, `OverloadDetector`, `AnomalyDetector`, `AnalyticsService`) and route blueprints (`dashboard`, `readings`, `alerts`, `analytics`, `simulation`, `settings`, `ml`).
2. **Alert Flood Throttling**:
   - Incorporates a cooldown dictionary mapping `(category, severity)` tuples to timestamp markers. Rapid identical violations within the 15-second window are suppressed.
3. **Database Concurrency**:
   - Utilizes SQLAlchemy `scoped_session` and context managers ensuring thread safety during background telemetry generation.
4. **Vite Frontend Bundling**:
   - Fully componentized into reusable modules (`MetricCard`, `LiveChart`, `AlertList`, `StatusBadge`). Built-in proxy configuration seamlessly routes `/api` requests to Flask port 5000.

---

### 9. Verification & Results

The system was verified using automated Pytest executions and production bundler builds:
- **Backend Tests**: 32 unit and integration tests covering calculation formulas, simulator states, overload conditions, cooldowns, and ML models.
  - **Result: 32 Passed, 0 Failed, 0 Skipped (100% pass rate in 6.09 seconds)**.
- **Frontend Build**: 2,388 modules compiled into minified HTML/CSS/JS bundles.
  - **Result: Production build succeeded in 10.89 seconds with 0 syntax or import errors**.
- **Demonstration Scenarios**:
  - *Overload Scenario*: Injected 21A current, successfully raised a `CURRENT_OVERLOAD (CRITICAL)` alarm.
  - *Anomaly Scenario*: Injected 0.40 PF distortion, successfully flagged by Isolation Forest with score `< 0` and persisted with source `ANOMALY_DETECTOR`.

*(Note: Long-term physical component thermal lifespans and hardware sensor noise remain unmeasured as this software prototype operates on synthetic data.)*

---

### 10. Limitations

1. **Simulation Scope**: Generates synthetic single-phase AC waveforms. Does not physically trip circuit breakers or disconnect electrical circuits.
2. **Three-Phase Support**: Current release models single-phase circuits only; three-phase line-to-line harmonic monitoring is not implemented.
3. **Academic Context**: The system is not certified for industrial safety instrumentation (SIL/IEC 61508).

---

### 11. Future Enhancements

1. **Hardware Telemetry Adapter**: Integrating MQTT / WebSocket ingestion for ESP32 microcontrollers with physical SCT-013 current transformers.
2. **Three-Phase Extension**: Calculating unbalanced neutral currents and polyphase reactive power vectors.
3. **Deep Learning Forecasting**: Implementing LSTM or Prophet models to forecast next-day peak demand.

---

### 12. Conclusion

The PowerGuard platform successfully demonstrates a full-stack, reliable software solution for electrical load monitoring, physical AC calculation, and hybrid anomaly detection. Combining rule-based overload protection with machine learning provides robust visibility into power utilization. Automated testing and modular architecture confirm its readiness for academic presentation, demonstration, and future hardware sensor integration.
