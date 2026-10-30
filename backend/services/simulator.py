import time
import math
import random
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable, List
from services.electrical_calculator import ElectricalCalculator

class ElectricalSimulator:
    """Thread-safe, realistic software electrical data simulator.
    
    Generates physically consistent single-phase AC parameters across six distinct
    load profiles with deterministic seed support for testing.
    """

    PROFILES = ["normal", "high", "fluctuating", "standby", "overload", "anomalous"]

    def __init__(self, random_seed: Optional[int] = None):
        self.random_seed = random_seed
        self.rng = random.Random(random_seed)
        
        # State variables
        self.profile = "normal"
        self.is_running = False
        self.is_paused = False
        self.speed = 1.0  # Time multiplier
        self.interval = 1.0  # Base interval in seconds
        
        self.cumulative_energy_kwh = 0.0
        self.simulated_elapsed_seconds = 0.0
        self.step_count = 0
        
        # Background worker thread management
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # Not paused initially
        self._lock = threading.Lock()
        
        # Callback invoked for each new reading
        self.on_reading_generated: Optional[Callable[[Dict[str, Any]], None]] = None

    def set_seed(self, seed: Optional[int]):
        """Set or reset RNG seed for reproducible testing."""
        self.random_seed = seed
        self.rng = random.Random(seed)

    def set_profile(self, profile: str) -> bool:
        """Change the active load profile."""
        with self._lock:
            if profile in self.PROFILES:
                self.profile = profile
                return True
            return False

    def set_speed(self, speed: float) -> bool:
        """Adjust simulation speed multiplier (0.1x to 10.0x)."""
        with self._lock:
            if 0.1 <= speed <= 10.0:
                self.speed = float(speed)
                return True
            return False

    def reset_energy(self, initial_kwh: float = 0.0):
        """Reset cumulative energy and elapsed time."""
        with self._lock:
            self.cumulative_energy_kwh = float(initial_kwh)
            self.simulated_elapsed_seconds = 0.0
            self.step_count = 0

    def generate_next_reading(self, custom_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate a single physically consistent electrical reading for the current profile."""
        with self._lock:
            profile = self.profile
            elapsed_dt = self.interval * self.speed
            self.simulated_elapsed_seconds += elapsed_dt
            self.step_count += 1
            
            # Base voltage: 230V standard AC nominal
            if profile == "normal":
                voltage = 230.0 + self.rng.gauss(0, 1.8)
                current = 3.5 + self.rng.uniform(-0.8, 1.2) + 0.5 * math.sin(self.step_count * 0.1)
                power_factor = min(0.98, max(0.88, 0.94 + self.rng.gauss(0, 0.015)))
            
            elif profile == "high":
                # High consumption (HVAC + water heater + oven)
                voltage = 227.0 + self.rng.gauss(0, 2.0)
                current = 13.5 + self.rng.uniform(-1.0, 1.8) + 0.8 * math.sin(self.step_count * 0.08)
                power_factor = min(0.96, max(0.87, 0.92 + self.rng.gauss(0, 0.015)))

            elif profile == "fluctuating":
                # Dynamic loads switching on and off (e.g. induction motors, compressors)
                voltage = 229.0 + self.rng.gauss(0, 3.0)
                cycle = (self.step_count % 12)
                if cycle < 4:
                    current = 2.5 + self.rng.uniform(-0.5, 0.5)
                    power_factor = 0.92 + self.rng.gauss(0, 0.02)
                elif cycle < 8:
                    current = 12.0 + self.rng.uniform(-1.0, 1.5)
                    power_factor = 0.78 + self.rng.gauss(0, 0.03)  # Motor start has lower PF
                else:
                    current = 6.0 + self.rng.uniform(-0.8, 0.8)
                    power_factor = 0.85 + self.rng.gauss(0, 0.02)
                power_factor = min(0.98, max(0.70, power_factor))

            elif profile == "standby":
                # Very low power standby (electronics, chargers)
                voltage = 232.0 + self.rng.gauss(0, 1.2)
                current = 0.45 + self.rng.uniform(-0.15, 0.25)
                power_factor = min(0.82, max(0.60, 0.72 + self.rng.gauss(0, 0.03)))

            elif profile == "overload":
                # Intentional critical overload: exceeds 16A and 3600W
                voltage = 221.0 + self.rng.gauss(0, 2.5)  # Voltage sag under extreme load
                current = 19.5 + self.rng.uniform(0.5, 3.5)
                power_factor = min(0.96, max(0.89, 0.93 + self.rng.gauss(0, 0.01)))

            elif profile == "anomalous":
                # Anomalous: severely degraded power factor or high current surge
                sub_mode = self.step_count % 3
                if sub_mode == 0:
                    voltage = 228.0 + self.rng.gauss(0, 1.5)
                    current = 8.5 + self.rng.uniform(-0.5, 0.5)
                    power_factor = 0.42 + self.rng.uniform(-0.05, 0.06)  # Severely lagging PF anomaly
                elif sub_mode == 1:
                    voltage = 210.0 + self.rng.gauss(0, 4.0)  # Abnormal brownout dip
                    current = 14.5 + self.rng.uniform(-1.0, 1.0)
                    power_factor = 0.68 + self.rng.uniform(-0.04, 0.04)
                else:
                    voltage = 246.0 + self.rng.gauss(0, 3.0)  # Surge
                    current = 11.0 + self.rng.uniform(0.0, 3.0)
                    power_factor = 0.55 + self.rng.uniform(-0.05, 0.05)
                power_factor = min(0.98, max(0.35, power_factor))

            else:
                voltage = 230.0
                current = 3.0
                power_factor = 0.92

            # Guardrails
            voltage = max(50.0, float(voltage))
            current = max(0.01, float(current))
            power_factor = min(1.0, max(0.05, float(power_factor)))

            # Physically consistent calculations
            apparent_power = ElectricalCalculator.calculate_apparent_power(voltage, current)
            active_power = ElectricalCalculator.calculate_active_power(voltage, current, power_factor)
            reactive_power = ElectricalCalculator.calculate_reactive_power(apparent_power, active_power)
            energy_delta = ElectricalCalculator.calculate_energy_kwh(active_power, elapsed_dt)
            self.cumulative_energy_kwh += energy_delta

            ts = custom_time or datetime.now(timezone.utc)

            reading = {
                "timestamp": ts,
                "voltage": round(voltage, 2),
                "current": round(current, 2),
                "active_power": round(active_power, 2),
                "apparent_power": round(apparent_power, 2),
                "reactive_power": round(reactive_power, 2),
                "power_factor": round(power_factor, 3),
                "energy_kwh": round(self.cumulative_energy_kwh, 5),
                "load_profile": profile,
                "simulated_elapsed_seconds": round(elapsed_dt, 2),
            }
            return reading

    def start(self):
        """Start the background simulation thread."""
        with self._lock:
            if self.is_running:
                return False  # Avoid duplicate background loops
            self.is_running = True
            self.is_paused = False
            self._stop_event.clear()
            self._pause_event.set()
            self._thread = threading.Thread(target=self._run_loop, name="SimulatorThread", daemon=True)
            self._thread.start()
            return True

    def pause(self):
        """Pause the background simulation."""
        with self._lock:
            if not self.is_running or self.is_paused:
                return False
            self.is_paused = True
            self._pause_event.clear()
            return True

    def resume(self):
        """Resume a paused simulation."""
        with self._lock:
            if not self.is_running or not self.is_paused:
                return False
            self.is_paused = False
            self._pause_event.set()
            return True

    def stop(self):
        """Stop the background simulation cleanly."""
        with self._lock:
            if not self.is_running:
                return False
            self.is_running = False
            self.is_paused = False
            self._stop_event.set()
            self._pause_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None
        return True

    def _run_loop(self):
        """Continuous background simulation loop."""
        while not self._stop_event.is_set():
            # Wait if paused
            self._pause_event.wait()
            if self._stop_event.is_set():
                break

            try:
                reading = self.generate_next_reading()
                if self.on_reading_generated:
                    self.on_reading_generated(reading)
            except Exception as e:
                # Log or handle error without crashing loop
                pass

            # Sleep interval scaled by speed
            sleep_time = max(0.05, self.interval / max(0.1, self.speed))
            time.sleep(sleep_time)

    def get_status(self) -> Dict[str, Any]:
        """Return current status of the simulator."""
        with self._lock:
            return {
                "is_running": self.is_running,
                "is_paused": self.is_paused,
                "load_profile": self.profile,
                "speed": self.speed,
                "interval": self.interval,
                "cumulative_energy_kwh": round(self.cumulative_energy_kwh, 5),
                "simulated_elapsed_seconds": round(self.simulated_elapsed_seconds, 2),
                "step_count": self.step_count,
            }
