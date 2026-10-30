from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Tuple, Optional

class OverloadDetector:
    """Configurable rule-based electrical overload and threshold violation detector.
    
    Includes alert cooldown, deduplication, and persistence tracking.
    """

    def __init__(self):
        # Maps (category, severity) -> datetime of last emitted alert
        self.last_alert_times: Dict[Tuple[str, str], datetime] = {}
        # Maps violation_key -> start_time datetime
        self.violation_start_times: Dict[str, datetime] = {}

    def reset_state(self):
        """Reset cooldown and persistence caches."""
        self.last_alert_times.clear()
        self.violation_start_times.clear()

    def evaluate_reading(
        self,
        reading: Dict[str, Any],
        settings: Dict[str, Any],
        current_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Evaluate a reading against configured thresholds.
        
        Args:
            reading: Dictionary with keys 'voltage', 'current', 'active_power', 'power_factor'
            settings: Dictionary with threshold settings
            current_time: Evaluation timestamp (defaults to UTC now)
            
        Returns:
            Dictionary containing:
                - system_status: 'NORMAL', 'WARNING', or 'CRITICAL'
                - alerts_to_create: List of alert dictionaries to persist
                - active_violations: List of human-readable violation descriptions
        """
        now = current_time or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        v = float(reading.get("voltage", 230.0))
        i = float(reading.get("current", 0.0))
        p = float(reading.get("active_power", 0.0))
        pf = float(reading.get("power_factor", 1.0))

        max_current = float(settings.get("max_current", 16.0))
        max_power = float(settings.get("max_active_power", 3600.0))
        v_min = float(settings.get("voltage_min", 207.0))
        v_max = float(settings.get("voltage_max", 253.0))
        min_pf = float(settings.get("min_power_factor", 0.80))
        cooldown_sec = float(settings.get("alert_cooldown_seconds", 15.0))
        persist_sec = float(settings.get("persistence_duration_seconds", 3.0))

        potential_alerts = []
        overall_status = "NORMAL"

        # 1. Current Check
        if i >= max_current:
            overall_status = "CRITICAL"
            potential_alerts.append({
                "severity": "CRITICAL",
                "category": "CURRENT_OVERLOAD",
                "parameter": "current",
                "observed_value": i,
                "threshold_value": max_current,
                "message": f"Critical Current Overload: Observed {i:.2f} A exceeds limit of {max_current:.2f} A",
                "requires_persistence": True,
            })
        elif i >= (0.85 * max_current):
            if overall_status != "CRITICAL":
                overall_status = "WARNING"
            potential_alerts.append({
                "severity": "WARNING",
                "category": "CURRENT_WARNING",
                "parameter": "current",
                "observed_value": i,
                "threshold_value": round(0.85 * max_current, 2),
                "message": f"High Current Warning: Observed {i:.2f} A is near capacity ({max_current:.2f} A limit)",
                "requires_persistence": False,
            })

        # 2. Active Power Check
        if p >= max_power:
            overall_status = "CRITICAL"
            potential_alerts.append({
                "severity": "CRITICAL",
                "category": "POWER_OVERLOAD",
                "parameter": "active_power",
                "observed_value": p,
                "threshold_value": max_power,
                "message": f"Critical Power Overload: Observed {p:.1f} W exceeds limit of {max_power:.1f} W",
                "requires_persistence": True,
            })
        elif p >= (0.85 * max_power):
            if overall_status != "CRITICAL":
                overall_status = "WARNING"
            potential_alerts.append({
                "severity": "WARNING",
                "category": "POWER_WARNING",
                "parameter": "active_power",
                "observed_value": p,
                "threshold_value": round(0.85 * max_power, 2),
                "message": f"High Power Warning: Observed {p:.1f} W is near capacity ({max_power:.1f} W limit)",
                "requires_persistence": False,
            })

        # 3. Voltage Check
        # Severe voltage deviation (> 15% out of nominal 230V or severe breach)
        if v < (v_min * 0.9) or v > (v_max * 1.1):
            overall_status = "CRITICAL"
            potential_alerts.append({
                "severity": "CRITICAL",
                "category": "VOLTAGE_CRITICAL",
                "parameter": "voltage",
                "observed_value": v,
                "threshold_value": v_min if v < v_min else v_max,
                "message": f"Severe Voltage Out-of-Range: {v:.1f} V violates critical bounds",
                "requires_persistence": True,
            })
        elif v < v_min or v > v_max:
            if overall_status != "CRITICAL":
                overall_status = "WARNING"
            potential_alerts.append({
                "severity": "WARNING",
                "category": "VOLTAGE_OUT_OF_RANGE",
                "parameter": "voltage",
                "observed_value": v,
                "threshold_value": v_min if v < v_min else v_max,
                "message": f"Voltage Out-of-Range Warning: {v:.1f} V outside nominal window ({v_min:.0f}V - {v_max:.0f}V)",
                "requires_persistence": False,
            })

        # 4. Power Factor Check
        if pf < min_pf:
            if overall_status == "NORMAL":
                overall_status = "WARNING"
            potential_alerts.append({
                "severity": "WARNING",
                "category": "LOW_POWER_FACTOR",
                "parameter": "power_factor",
                "observed_value": pf,
                "threshold_value": min_pf,
                "message": f"Low Power Factor: Observed {pf:.3f} below minimum threshold of {min_pf:.2f}",
                "requires_persistence": False,
            })

        # Active violations list for UI/monitoring
        active_violations = [item["message"] for item in potential_alerts]

        # Apply persistence checks and cooldown filtering to avoid alert storms
        alerts_to_create = []
        for alert_cand in potential_alerts:
            cat = alert_cand["category"]
            sev = alert_cand["severity"]
            key = (cat, sev)
            violation_key = f"{cat}_{sev}"

            # Check persistence if required
            if alert_cand.get("requires_persistence") and persist_sec > 0:
                if violation_key not in self.violation_start_times:
                    self.violation_start_times[violation_key] = now
                    # Do not emit alert immediately if persistence duration not reached
                    continue
                else:
                    duration = (now - self.violation_start_times[violation_key]).total_seconds()
                    if duration < persist_sec:
                        continue
            else:
                self.violation_start_times.pop(violation_key, None)

            # Check cooldown
            last_emitted = self.last_alert_times.get(key)
            if last_emitted is not None:
                elapsed = (now - last_emitted).total_seconds()
                if elapsed < cooldown_sec:
                    # Within cooldown period; suppress duplicate alert
                    continue

            # Alert is valid and eligible to fire
            self.last_alert_times[key] = now
            alerts_to_create.append({
                "timestamp": now,
                "severity": sev,
                "category": cat,
                "parameter": alert_cand["parameter"],
                "observed_value": alert_cand["observed_value"],
                "threshold_value": alert_cand["threshold_value"],
                "message": alert_cand["message"],
                "source": "RULE_ENGINE",
                "acknowledged": False,
            })

        # Clean up stale violation start times if violation no longer active
        active_keys = {f"{a['category']}_{a['severity']}" for a in potential_alerts}
        for k in list(self.violation_start_times.keys()):
            if k not in active_keys:
                self.violation_start_times.pop(k, None)

        return {
            "system_status": overall_status,
            "alerts_to_create": alerts_to_create,
            "active_violations": active_violations,
        }
