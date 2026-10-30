# PowerGuard — Backend Service

The PowerGuard backend is a Python Flask REST API designed for real-time electrical load monitoring, physical calculation modeling, rule-based overload protection, and machine learning anomaly detection.

## Key Modules

- `app.py`: Flask application factory, error handling, CORS configuration, and route registration.
- `config.py`: Default electrical limits, tariff rates, simulation timings, and validation rules.
- `database.py`: SQLAlchemy connection pooling, thread-safe session handling, and schema setup.
- `models.py`: Database models for `ElectricalReading`, `Alert`, `SystemEvent`, and `AppSetting`.
- `services/electrical_calculator.py`: Formulations for Apparent Power, Active Power, Reactive Power, Energy integration (kWh), and Cost estimation.
- `services/simulator.py`: Physically consistent AC single-phase waveform and load profile generator.
- `services/overload_detector.py`: Rule-based evaluation with cooldown deduplication and persistence logic.
- `services/anomaly_detector.py`: Scikit-learn Isolation Forest model with feature engineering and interpretability.
- `services/analytics_service.py`: Aggregation algorithms for power trends, consumption breakdowns, and day-over-day statistics.
- `services/alert_service.py`: Alert lifecycle management and acknowledgment persistence.

## Running Tests

```bash
cd backend
python -m pytest tests -v
```

## Running the Backend Server

```bash
python app.py
```
Default bind: `http://127.0.0.1:5000`
