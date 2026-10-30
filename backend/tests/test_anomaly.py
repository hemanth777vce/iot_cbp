import pytest
from services.anomaly_detector import AnomalyDetector
from services.simulator import ElectricalSimulator

def test_anomaly_detector_insufficient_data():
    """Verify detector refuses training and returns clean status with insufficient data."""
    detector = AnomalyDetector(min_samples=30)
    assert detector.status == "NOT_TRAINED"

    # Try training with only 5 readings
    sim = ElectricalSimulator(random_seed=1)
    few_readings = [sim.generate_next_reading() for _ in range(5)]
    res = detector.train(few_readings)

    assert res["success"] is False
    assert detector.status == "INSUFFICIENT_DATA"
    assert "Insufficient data" in res["message"]

    # Predict returns fallback safely
    pred = detector.predict(sim.generate_next_reading())
    assert pred["is_anomaly"] is False
    assert pred["status"] == "INSUFFICIENT_DATA"

def test_anomaly_detector_training_and_prediction():
    """Verify successful training on normal cluster and detection of injected anomalies."""
    detector = AnomalyDetector(contamination=0.08, min_samples=30, random_state=42)
    sim = ElectricalSimulator(random_seed=42)

    # Generate 60 normal readings for training
    sim.set_profile("normal")
    normal_training_readings = [sim.generate_next_reading() for _ in range(60)]

    train_res = detector.train(normal_training_readings)
    assert train_res["success"] is True
    assert detector.status == "TRAINED"
    assert train_res["sample_count"] == 60

    # Test normal reading prediction
    normal_test_reading = sim.generate_next_reading()
    pred_normal = detector.predict(normal_test_reading)
    assert pred_normal["status"] == "PREDICTION_AVAILABLE"

    # Test anomalous reading (severely distorted power factor 0.35 with strange active power)
    anomalous_reading = {
        "voltage": 248.0,
        "current": 18.0,
        "active_power": 1200.0,
        "apparent_power": 4464.0,
        "power_factor": 0.27,  # Very anomalous compared to 0.94 baseline
        "energy_kwh": 5.0,
        "load_profile": "anomalous",
        "simulated_elapsed_seconds": 1.0,
    }
    pred_anom = detector.predict(anomalous_reading, recent_history=normal_training_readings[-5:])
    assert pred_anom["is_anomaly"] is True
    assert pred_anom["anomaly_score"] < 0  # Isolation forest scores anomalies negatively
    assert pred_anom["explanation"] is not None
    assert "ML Anomaly" in pred_anom["explanation"]

def test_anomaly_detector_status_metadata():
    """Verify metadata returned by get_status."""
    detector = AnomalyDetector(contamination=0.05, min_samples=30)
    status = detector.get_status()
    assert status["status"] == "NOT_TRAINED"
    assert status["contamination"] == 0.05
    assert status["min_samples_required"] == 30
    assert "voltage" in status["features"]
