import time
import pytest
from services.simulator import ElectricalSimulator

def test_simulator_output_validity():
    """Verify that generated readings contain all required fields and satisfy physical constraints."""
    sim = ElectricalSimulator(random_seed=123)
    reading = sim.generate_next_reading()

    required_fields = [
        "timestamp", "voltage", "current", "active_power",
        "apparent_power", "reactive_power", "power_factor",
        "energy_kwh", "load_profile", "simulated_elapsed_seconds"
    ]
    for field in required_fields:
        assert field in reading, f"Missing field {field}"

    assert reading["voltage"] > 0
    assert reading["current"] > 0
    assert 0.0 <= reading["power_factor"] <= 1.0
    # Physical invariant: Active power (W) cannot exceed Apparent power (VA)
    assert reading["active_power"] <= (reading["apparent_power"] + 1e-2)
    assert reading["reactive_power"] >= 0.0
    assert reading["energy_kwh"] > 0.0

def test_simulator_deterministic_behavior():
    """Verify that using identical seeds generates identical readings."""
    sim1 = ElectricalSimulator(random_seed=999)
    sim2 = ElectricalSimulator(random_seed=999)

    r1_a = sim1.generate_next_reading()
    r2_a = sim2.generate_next_reading()

    assert r1_a["voltage"] == r2_a["voltage"]
    assert r1_a["current"] == r2_a["current"]
    assert r1_a["active_power"] == r2_a["active_power"]

    r1_b = sim1.generate_next_reading()
    r2_b = sim2.generate_next_reading()

    assert r1_b["voltage"] == r2_b["voltage"]
    assert r1_b["current"] == r2_b["current"]

def test_energy_accumulation_monotonic():
    """Verify that cumulative energy never decreases over consecutive steps."""
    sim = ElectricalSimulator(random_seed=42)
    sim.reset_energy(0.0)

    last_energy = 0.0
    for _ in range(10):
        r = sim.generate_next_reading()
        assert r["energy_kwh"] >= last_energy
        last_energy = r["energy_kwh"]

def test_simulator_start_pause_resume_stop():
    """Verify full state machine: start -> pause -> resume -> stop."""
    sim = ElectricalSimulator()
    try:
        assert not sim.is_running
        assert not sim.is_paused

        # Start
        started = sim.start()
        assert started is True
        assert sim.is_running is True
        assert sim.is_paused is False

        # Duplicate start prevention
        dup_started = sim.start()
        assert dup_started is False

        # Pause
        paused = sim.pause()
        assert paused is True
        assert sim.is_paused is True

        # Resume
        resumed = sim.resume()
        assert resumed is True
        assert sim.is_paused is False

        # Stop
        stopped = sim.stop()
        assert stopped is True
        assert sim.is_running is False
    finally:
        sim.stop()

def test_simulator_speed_and_profile_controls():
    """Verify speed multiplier and profile validation."""
    sim = ElectricalSimulator()
    assert sim.set_speed(2.5) is True
    assert sim.speed == 2.5
    assert sim.set_speed(50.0) is False  # Out of range

    assert sim.set_profile("overload") is True
    assert sim.profile == "overload"
    assert sim.set_profile("invalid_profile_xyz") is False
    assert sim.profile == "overload"
