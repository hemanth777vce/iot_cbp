# PowerGuard Testing Documentation

This document records the automated verification methodology, test execution commands, and verified results for the PowerGuard platform.

## 1. Automated Test Execution Summary

| Suite | Runner | Test Files | Total Tests | Passed | Failed | Skipped | Execution Time |
|---|---|---|---|---|---|---|---|
| **Backend Test Suite** | `pytest 9.2.0` | 5 | 32 | **32** | 0 | 0 | **6.09 seconds** |
| **Frontend Production Build** | `vite build (v5.4.21)` | — | 2,388 modules | **SUCCESS** | 0 | 0 | **10.89 seconds** |

---

## 2. Backend Test Coverage Mapping

All 24 required technical criteria specified in Section 21 are implemented and verified:

| # | Requirement Area | Test Case | Status | Verified Module |
|---|---|---|---|---|
| 1 | Database Initialization | `test_database_initialization_and_nondestructive` | **PASSED** | `database.py` |
| 2 | Health Endpoint | `test_health_endpoint` | **PASSED** | `routes/health.py` |
| 3 | Electrical Calculation Formulas | `test_apparent_power_formula`, `test_active_power_formula`, `test_reactive_power_formula` | **PASSED** | `services/electrical_calculator.py` |
| 4 | Invalid Calculation Inputs | `test_invalid_calculation_inputs` | **PASSED** | `services/electrical_calculator.py` |
| 5 | Simulator Output Validity | `test_simulator_output_validity` | **PASSED** | `services/simulator.py` |
| 6 | Deterministic Simulator (Random Seed) | `test_simulator_deterministic_behavior` | **PASSED** | `services/simulator.py` |
| 7 | Energy Accumulation Monotonicity | `test_energy_accumulation_monotonic` | **PASSED** | `services/simulator.py` |
| 8 | Start, Pause, Resume, Stop Cycle | `test_simulator_start_pause_resume_stop` | **PASSED** | `services/simulator.py` |
| 9 | Duplicate Simulation Prevention | `test_simulator_start_pause_resume_stop` | **PASSED** | `services/simulator.py` |
| 10 | Normal Operating Conditions | `test_normal_operating_conditions` | **PASSED** | `services/overload_detector.py` |
| 11 | Overload Detection Rules | `test_current_overload_critical`, `test_power_overload_critical` | **PASSED** | `services/overload_detector.py` |
| 12 | Alert Cooldown & Deduplication | `test_alert_cooldown_and_deduplication` | **PASSED** | `services/overload_detector.py` |
| 13 | Alert Acknowledgment Persistence | `test_alert_query_and_acknowledgment` | **PASSED** | `services/alert_service.py` |
| 14 | Settings Validation & Rejection | `test_settings_get_and_patch_validation` | **PASSED** | `routes/settings.py` |
| 15 | Reading Pagination | `test_demo_data_generation_and_readings_pagination` | **PASSED** | `routes/readings.py` |
| 16 | Reading Date Filters | `test_demo_data_generation_and_readings_pagination` | **PASSED** | `routes/readings.py` |
| 17 | Analytics Calculations | `test_analytics_endpoints` | **PASSED** | `services/analytics_service.py` |
| 18 | Empty Analytics Dataset Safety | `test_statistics_calculation`, `test_readings_latest_and_aggregates` | **PASSED** | `services/analytics_service.py` |
| 19 | ML Model Insufficient Data Fallback | `test_anomaly_detector_insufficient_data` | **PASSED** | `services/anomaly_detector.py` |
| 20 | ML Training and Outlier Prediction | `test_anomaly_detector_training_and_prediction` | **PASSED** | `services/anomaly_detector.py` |
| 21 | Demo Data Generation | `test_demo_data_generation_and_readings_pagination` | **PASSED** | `routes/simulation.py` |
| 22 | API Error Handling (404, bad input) | `test_api_error_handling` | **PASSED** | `app.py` |
| 23 | Cost Estimation Logic | `test_cost_estimation` | **PASSED** | `services/electrical_calculator.py` |
| 24 | Non-Destructive Database Init | `test_database_initialization_and_nondestructive` | **PASSED** | `database.py` |

---

## 3. How to Run Backend Tests

Open PowerShell or Command Prompt in the repository root:

```powershell
python -m pytest backend/tests -v
```

Expected Output:
```
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\satya\OneDrive\Desktop\IOT-CBP
collected 32 items

backend/tests/test_anomaly.py::test_anomaly_detector_insufficient_data PASSED
backend/tests/test_anomaly.py::test_anomaly_detector_training_and_prediction PASSED
backend/tests/test_anomaly.py::test_anomaly_detector_status_metadata PASSED
backend/tests/test_api.py::test_database_initialization_and_nondestructive PASSED
backend/tests/test_api.py::test_health_endpoint PASSED
backend/tests/test_api.py::test_settings_get_and_patch_validation PASSED
backend/tests/test_api.py::test_demo_data_generation_and_readings_pagination PASSED
backend/tests/test_api.py::test_readings_latest_and_aggregates PASSED
backend/tests/test_api.py::test_alert_query_and_acknowledgment PASSED
backend/tests/test_api.py::test_analytics_endpoints PASSED
backend/tests/test_api.py::test_dashboard_summary_and_events PASSED
backend/tests/test_api.py::test_api_error_handling PASSED
backend/tests/test_calculations.py::test_apparent_power_formula PASSED
backend/tests/test_calculations.py::test_active_power_formula PASSED
backend/tests/test_calculations.py::test_reactive_power_formula PASSED
backend/tests/test_calculations.py::test_reactive_power_zero_when_unity_power_factor PASSED
backend/tests/test_calculations.py::test_energy_accumulation_formula PASSED
backend/tests/test_calculations.py::test_cost_estimation PASSED
backend/tests/test_calculations.py::test_invalid_calculation_inputs PASSED
backend/tests/test_calculations.py::test_statistics_calculation PASSED
backend/tests/test_overload.py::test_normal_operating_conditions PASSED
backend/tests/test_overload.py::test_current_overload_critical PASSED
backend/tests/test_overload.py::test_power_overload_critical PASSED
backend/tests/test_overload.py::test_voltage_out_of_range_warning PASSED
backend/tests/test_overload.py::test_low_power_factor_warning PASSED
backend/tests/test_overload.py::test_alert_cooldown_and_deduplication PASSED
backend/tests/test_overload.py::test_violation_persistence_duration PASSED
backend/tests/test_simulator.py::test_simulator_output_validity PASSED
backend/tests/test_simulator.py::test_simulator_deterministic_behavior PASSED
backend/tests/test_simulator.py::test_energy_accumulation_monotonic PASSED
backend/tests/test_simulator.py::test_simulator_start_pause_resume_stop PASSED
backend/tests/test_simulator.py::test_simulator_speed_and_profile_controls PASSED

============================= 32 passed in 6.09s ==============================
```

---

## 4. Frontend Production Build Verification

Execute the Vite production bundler from repository root:

```powershell
npm run build --prefix frontend
```

Expected Output:
```
> powerguard-frontend@1.0.0 build
> vite build

vite v5.4.21 building for production...
transforming...
✓ 2388 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   1.04 kB │ gzip:   0.59 kB
dist/assets/index-B_Q0dtCI.css   14.27 kB │ gzip:   3.42 kB
dist/assets/index-CEHY4FnO.js   645.02 kB │ gzip: 178.48 kB
✓ built in 10.89s
```

All 2,388 modules were transformed and compiled without compilation errors or broken imports.
