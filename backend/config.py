import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DB_PATH = INSTANCE_DIR / "powerguard.db"
DATABASE_URL = os.environ.get("POWERGUARD_DB_URL", f"sqlite:///{DEFAULT_DB_PATH}")

DEFAULT_SETTINGS = {
    "electricity_tariff": 7.50,         # ₹ per kWh
    "currency_symbol": "₹",
    "max_current": 16.0,                # Amperes
    "max_active_power": 3600.0,         # Watts
    "voltage_min": 207.0,               # Volts (-10% of 230V)
    "voltage_max": 253.0,               # Volts (+10% of 230V)
    "min_power_factor": 0.80,           # Dimensionless
    "alert_cooldown_seconds": 15.0,     # Seconds between similar alerts
    "persistence_duration_seconds": 3.0,# Seconds condition must hold for critical
    "simulation_speed": 1.0,            # Multiplier
    "simulation_interval": 1.0,         # Seconds per simulated step
    "default_load_profile": "normal",   # Initial load profile
    "anomaly_contamination": 0.05,      # Isolation forest contamination parameter
    "anomaly_min_samples": 30,          # Minimum readings required to train ML model
}

VALIDATION_RULES = {
    "electricity_tariff": {"min": 0.1, "max": 100.0, "type": float},
    "max_current": {"min": 1.0, "max": 100.0, "type": float},
    "max_active_power": {"min": 100.0, "max": 50000.0, "type": float},
    "voltage_min": {"min": 150.0, "max": 240.0, "type": float},
    "voltage_max": {"min": 220.0, "max": 300.0, "type": float},
    "min_power_factor": {"min": 0.1, "max": 1.0, "type": float},
    "alert_cooldown_seconds": {"min": 1.0, "max": 300.0, "type": float},
    "persistence_duration_seconds": {"min": 0.0, "max": 60.0, "type": float},
    "simulation_speed": {"min": 0.1, "max": 10.0, "type": float},
    "simulation_interval": {"min": 0.2, "max": 10.0, "type": float},
    "default_load_profile": {"enum": ["normal", "high", "fluctuating", "standby", "overload", "anomalous"], "type": str},
    "anomaly_contamination": {"min": 0.01, "max": 0.25, "type": float},
    "anomaly_min_samples": {"min": 10, "max": 1000, "type": int},
}
