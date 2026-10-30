from datetime import datetime, timezone, timedelta
from services.overload_detector import OverloadDetector

DEFAULT_SETTINGS = {
    "max_current": 16.0,
    "max_active_power": 3600.0,
    "voltage_min": 207.0,
    "voltage_max": 253.0,
    "min_power_factor": 0.80,
    "alert_cooldown_seconds": 15.0,
    "persistence_duration_seconds": 0.0,  # 0 for immediate firing in direct rule tests
}

def test_normal_operating_conditions():
    """Verify NORMAL status when parameters are safely within limits."""
    detector = OverloadDetector()
    reading = {
        "voltage": 230.0,
        "current": 4.5,
        "active_power": 1000.0,
        "power_factor": 0.95,
    }
    result = detector.evaluate_reading(reading, DEFAULT_SETTINGS)
    assert result["system_status"] == "NORMAL"
    assert len(result["alerts_to_create"]) == 0
    assert len(result["active_violations"]) == 0

def test_current_overload_critical():
    """Verify CRITICAL alert is triggered when current exceeds threshold."""
    detector = OverloadDetector()
    reading = {
        "voltage": 228.0,
        "current": 19.5,  # Exceeds 16.0 A
        "active_power": 3200.0,
        "power_factor": 0.92,
    }
    result = detector.evaluate_reading(reading, DEFAULT_SETTINGS)
    assert result["system_status"] == "CRITICAL"
    assert len(result["alerts_to_create"]) >= 1
    alert = result["alerts_to_create"][0]
    assert alert["category"] == "CURRENT_OVERLOAD"
    assert alert["severity"] == "CRITICAL"
    assert alert["observed_value"] == 19.5

def test_power_overload_critical():
    """Verify CRITICAL alert is triggered when active power exceeds limit."""
    detector = OverloadDetector()
    reading = {
        "voltage": 230.0,
        "current": 15.0,
        "active_power": 4200.0,  # Exceeds 3600.0 W
        "power_factor": 0.95,
    }
    result = detector.evaluate_reading(reading, DEFAULT_SETTINGS)
    assert result["system_status"] == "CRITICAL"
    alert = next(a for a in result["alerts_to_create"] if a["category"] == "POWER_OVERLOAD")
    assert alert["severity"] == "CRITICAL"
    assert alert["observed_value"] == 4200.0

def test_voltage_out_of_range_warning():
    """Verify WARNING alert when voltage is outside nominal range."""
    detector = OverloadDetector()
    reading = {
        "voltage": 198.0,  # Below 207.0 V
        "current": 4.0,
        "active_power": 700.0,
        "power_factor": 0.92,
    }
    result = detector.evaluate_reading(reading, DEFAULT_SETTINGS)
    assert result["system_status"] == "WARNING"
    alert = next(a for a in result["alerts_to_create"] if "VOLTAGE" in a["category"])
    assert alert["severity"] == "WARNING"
    assert alert["parameter"] == "voltage"

def test_low_power_factor_warning():
    """Verify WARNING alert when power factor is below min threshold."""
    detector = OverloadDetector()
    reading = {
        "voltage": 230.0,
        "current": 5.0,
        "active_power": 600.0,
        "power_factor": 0.52,  # Below 0.80
    }
    result = detector.evaluate_reading(reading, DEFAULT_SETTINGS)
    assert result["system_status"] == "WARNING"
    alert = next(a for a in result["alerts_to_create"] if a["category"] == "LOW_POWER_FACTOR")
    assert alert["severity"] == "WARNING"
    assert alert["parameter"] == "power_factor"

def test_alert_cooldown_and_deduplication():
    """Verify that identical violations within the cooldown window do not spawn duplicate alerts."""
    detector = OverloadDetector()
    t0 = datetime.now(timezone.utc)
    reading = {
        "voltage": 225.0,
        "current": 20.0,
        "active_power": 4100.0,
        "power_factor": 0.91,
    }

    # First violation -> emits alerts
    res1 = detector.evaluate_reading(reading, DEFAULT_SETTINGS, current_time=t0)
    assert len(res1["alerts_to_create"]) > 0

    # Immediate second violation at t0 + 2 seconds (< 15s cooldown) -> suppressed
    t1 = t0 + timedelta(seconds=2)
    res2 = detector.evaluate_reading(reading, DEFAULT_SETTINGS, current_time=t1)
    assert len(res2["alerts_to_create"]) == 0

    # Third violation after cooldown expires at t0 + 20 seconds -> emits again
    t2 = t0 + timedelta(seconds=20)
    res3 = detector.evaluate_reading(reading, DEFAULT_SETTINGS, current_time=t2)
    assert len(res3["alerts_to_create"]) > 0

def test_violation_persistence_duration():
    """Verify that if persistence is enabled, critical alert requires sustained violation."""
    detector = OverloadDetector()
    settings_with_persist = dict(DEFAULT_SETTINGS)
    settings_with_persist["persistence_duration_seconds"] = 5.0

    t0 = datetime.now(timezone.utc)
    reading = {
        "voltage": 230.0,
        "current": 22.0,  # Critical overload
        "active_power": 4500.0,
        "power_factor": 0.92,
    }

    # At t0 (start of violation), duration is 0 < 5s -> alert not emitted yet
    res0 = detector.evaluate_reading(reading, settings_with_persist, current_time=t0)
    assert len(res0["alerts_to_create"]) == 0

    # At t0 + 2s, still under 5s -> not emitted
    res2 = detector.evaluate_reading(reading, settings_with_persist, current_time=t0 + timedelta(seconds=2))
    assert len(res2["alerts_to_create"]) == 0

    # At t0 + 6s, duration >= 5s -> alert emitted!
    res6 = detector.evaluate_reading(reading, settings_with_persist, current_time=t0 + timedelta(seconds=6))
    assert len(res6["alerts_to_create"]) > 0
