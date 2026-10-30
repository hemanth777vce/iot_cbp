import math
from typing import List, Dict, Any, Optional

class ElectricalCalculator:
    """Core electrical calculations for PowerGuard.
    
    Provides physics-based formulas for AC single-phase electrical systems,
    energy accumulation, and financial cost estimation.
    """

    @staticmethod
    def calculate_apparent_power(voltage: float, current: float) -> float:
        """Calculate Apparent Power in Volt-Amperes (VA).
        Formula: S = V * I
        """
        if voltage < 0 or current < 0:
            raise ValueError("Voltage and Current must be non-negative")
        return float(voltage * current)

    @staticmethod
    def calculate_active_power(voltage: float, current: float, power_factor: float) -> float:
        """Calculate Active (Real) Power in Watts (W).
        Formula: P = V * I * cos(phi) = S * PF
        """
        if voltage < 0 or current < 0:
            raise ValueError("Voltage and Current must be non-negative")
        if not (0.0 <= power_factor <= 1.0):
            raise ValueError("Power Factor must be between 0.0 and 1.0")
        return float(voltage * current * power_factor)

    @staticmethod
    def calculate_reactive_power(apparent_power: float, active_power: float) -> float:
        """Calculate Reactive Power in Volt-Amperes Reactive (var).
        Formula: Q = sqrt(max(0, S^2 - P^2))
        """
        if apparent_power < 0 or active_power < 0:
            raise ValueError("Apparent and Active power must be non-negative")
        diff = (apparent_power ** 2) - (active_power ** 2)
        return float(math.sqrt(max(0.0, diff)))

    @staticmethod
    def calculate_energy_kwh(power_watts: float, elapsed_seconds: float) -> float:
        """Calculate Energy Consumption in Kilowatt-Hours (kWh).
        Formula: Energy (kWh) = (Power (W) * elapsed_seconds) / 3,600,000
        """
        if power_watts < 0 or elapsed_seconds < 0:
            raise ValueError("Power and elapsed time must be non-negative")
        return float((power_watts * elapsed_seconds) / 3_600_000.0)

    @staticmethod
    def calculate_estimated_cost(energy_kwh: float, tariff_per_kwh: float) -> float:
        """Calculate Estimated Cost based on energy and configured tariff.
        Formula: Cost = Energy (kWh) * Tariff (currency / kWh)
        """
        if energy_kwh < 0 or tariff_per_kwh < 0:
            raise ValueError("Energy and tariff must be non-negative")
        return float(energy_kwh * tariff_per_kwh)

    @staticmethod
    def calculate_statistics(values: List[float]) -> Dict[str, Optional[float]]:
        """Calculate min, max, avg, and standard deviation for a list of values."""
        if not values:
            return {"min": None, "max": None, "avg": None, "std": None, "count": 0}
        
        n = len(values)
        avg = sum(values) / n
        variance = sum((x - avg) ** 2 for x in values) / n if n > 1 else 0.0
        
        return {
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "avg": round(avg, 2),
            "std": round(math.sqrt(variance), 2),
            "count": n,
        }

    @classmethod
    def compute_reading_parameters(cls, voltage: float, current: float, power_factor: float, elapsed_seconds: float) -> Dict[str, float]:
        """Compute full suite of electrical parameters for a set of raw observations."""
        s = cls.calculate_apparent_power(voltage, current)
        p = cls.calculate_active_power(voltage, current, power_factor)
        q = cls.calculate_reactive_power(s, p)
        e = cls.calculate_energy_kwh(p, elapsed_seconds)
        return {
            "apparent_power": round(s, 2),
            "active_power": round(p, 2),
            "reactive_power": round(q, 2),
            "energy_increment_kwh": e,
        }
