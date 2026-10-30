import pytest
import math
from services.electrical_calculator import ElectricalCalculator

def test_apparent_power_formula():
    """Verify Apparent Power (VA) = Voltage (V) * Current (A)."""
    v = 230.0
    i = 10.0
    s = ElectricalCalculator.calculate_apparent_power(v, i)
    assert s == 2300.0

def test_active_power_formula():
    """Verify Active Power (W) = Voltage (V) * Current (A) * Power Factor."""
    v = 230.0
    i = 10.0
    pf = 0.95
    p = ElectricalCalculator.calculate_active_power(v, i, pf)
    assert pytest.approx(p, rel=1e-4) == 2185.0

def test_reactive_power_formula():
    """Verify Reactive Power (var) = sqrt(max(0, S^2 - P^2))."""
    s = 2300.0
    p = 2185.0
    q = ElectricalCalculator.calculate_reactive_power(s, p)
    expected_q = math.sqrt(s**2 - p**2)
    assert pytest.approx(q, rel=1e-4) == expected_q

def test_reactive_power_zero_when_unity_power_factor():
    """Verify Reactive Power is 0 when PF = 1.0."""
    s = 2300.0
    p = 2300.0
    q = ElectricalCalculator.calculate_reactive_power(s, p)
    assert q == 0.0

def test_energy_accumulation_formula():
    """Verify Energy (kWh) = Power (W) * Time (s) / 3,600,000."""
    p = 1000.0  # 1 kW
    t = 3600.0  # 1 hour in seconds
    kwh = ElectricalCalculator.calculate_energy_kwh(p, t)
    assert pytest.approx(kwh, rel=1e-5) == 1.0

def test_cost_estimation():
    """Verify Cost = Energy (kWh) * Tariff rate."""
    kwh = 2.5
    tariff = 7.50
    cost = ElectricalCalculator.calculate_estimated_cost(kwh, tariff)
    assert pytest.approx(cost, rel=1e-5) == 18.75

def test_invalid_calculation_inputs():
    """Verify invalid negative inputs or invalid power factors raise ValueError."""
    with pytest.raises(ValueError):
        ElectricalCalculator.calculate_apparent_power(-230.0, 5.0)

    with pytest.raises(ValueError):
        ElectricalCalculator.calculate_apparent_power(230.0, -5.0)

    with pytest.raises(ValueError):
        ElectricalCalculator.calculate_active_power(230.0, 5.0, 1.2)  # PF > 1.0

    with pytest.raises(ValueError):
        ElectricalCalculator.calculate_active_power(230.0, 5.0, -0.1)  # PF < 0.0

    with pytest.raises(ValueError):
        ElectricalCalculator.calculate_energy_kwh(-500.0, 10.0)

    with pytest.raises(ValueError):
        ElectricalCalculator.calculate_estimated_cost(-1.0, 7.5)

def test_statistics_calculation():
    """Verify min, max, avg, and standard deviation calculations."""
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    stats = ElectricalCalculator.calculate_statistics(values)
    assert stats["min"] == 10.0
    assert stats["max"] == 50.0
    assert stats["avg"] == 30.0
    assert stats["count"] == 5

    # Empty list
    empty_stats = ElectricalCalculator.calculate_statistics([])
    assert empty_stats["count"] == 0
    assert empty_stats["avg"] is None
