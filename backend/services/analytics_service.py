from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from models import ElectricalReading, Alert
from services.electrical_calculator import ElectricalCalculator

class AnalyticsService:
    """Service for processing, aggregating, and analyzing electrical monitoring data."""

    @staticmethod
    def get_consumption_trends(
        session: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = "hourly"
    ) -> List[Dict[str, Any]]:
        """Aggregate energy consumption trends over time."""
        query = session.query(ElectricalReading)
        if start_date:
            query = query.filter(ElectricalReading.timestamp >= start_date)
        if end_date:
            query = query.filter(ElectricalReading.timestamp <= end_date)

        readings = query.order_by(ElectricalReading.timestamp.asc()).all()
        if not readings:
            return []

        # Group by hour or day
        grouped: Dict[str, Dict[str, Any]] = {}
        for r in readings:
            ts_str = r.timestamp.strftime("%Y-%m-%d %H:00" if interval == "hourly" else "%Y-%m-%d")
            if ts_str not in grouped:
                grouped[ts_str] = {
                    "period": ts_str,
                    "powers": [],
                    "min_energy": r.energy_kwh,
                    "max_energy": r.energy_kwh,
                    "count": 0,
                }
            g = grouped[ts_str]
            g["powers"].append(r.active_power)
            g["max_energy"] = max(g["max_energy"], r.energy_kwh)
            g["min_energy"] = min(g["min_energy"], r.energy_kwh)
            g["count"] += 1

        results = []
        for period, data in grouped.items():
            powers = data["powers"]
            avg_p = sum(powers) / len(powers) if powers else 0.0
            peak_p = max(powers) if powers else 0.0
            # Energy consumed during this block is the delta or estimated from average power
            energy_consumed = max(0.0, data["max_energy"] - data["min_energy"])
            results.append({
                "period": period,
                "avg_power_w": round(avg_p, 2),
                "peak_power_w": round(peak_p, 2),
                "energy_kwh": round(energy_consumed, 4),
                "reading_count": data["count"],
            })
        return results

    @staticmethod
    def get_power_trends(session: Session, limit: int = 100) -> List[Dict[str, Any]]:
        """Return recent power readings for time-series charts."""
        readings = (
            session.query(ElectricalReading)
            .order_by(desc(ElectricalReading.timestamp))
            .limit(limit)
            .all()
        )
        readings.reverse()
        return [
            {
                "timestamp": r.timestamp.isoformat(),
                "time_label": r.timestamp.strftime("%H:%M:%S"),
                "active_power": round(r.active_power, 2),
                "apparent_power": round(r.apparent_power, 2),
                "reactive_power": round(r.reactive_power, 2),
                "power_factor": round(r.power_factor, 3),
            }
            for r in readings
        ]

    @staticmethod
    def get_voltage_and_current_trends(session: Session, limit: int = 100) -> List[Dict[str, Any]]:
        """Return voltage and current trend points on distinct scales."""
        readings = (
            session.query(ElectricalReading)
            .order_by(desc(ElectricalReading.timestamp))
            .limit(limit)
            .all()
        )
        readings.reverse()
        return [
            {
                "timestamp": r.timestamp.isoformat(),
                "time_label": r.timestamp.strftime("%H:%M:%S"),
                "voltage": round(r.voltage, 2),
                "current": round(r.current, 2),
            }
            for r in readings
        ]

    @staticmethod
    def get_daily_summary(session: Session, tariff: float = 7.50) -> Dict[str, Any]:
        """Generate high-level daily energy summary and day-over-day comparison."""
        now = datetime.now(timezone.utc)
        today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
        yesterday_start = today_start - timedelta(days=1)

        # Today's readings
        today_readings = (
            session.query(ElectricalReading)
            .filter(ElectricalReading.timestamp >= today_start)
            .order_by(ElectricalReading.timestamp.asc())
            .all()
        )

        # Yesterday's readings
        yesterday_readings = (
            session.query(ElectricalReading)
            .filter(ElectricalReading.timestamp >= yesterday_start, ElectricalReading.timestamp < today_start)
            .order_by(ElectricalReading.timestamp.asc())
            .all()
        )

        today_energy = 0.0
        peak_power = 0.0
        avg_pf = 0.0
        if today_readings:
            powers = [r.active_power for r in today_readings]
            pfs = [r.power_factor for r in today_readings]
            peak_power = max(powers)
            avg_pf = sum(pfs) / len(pfs)
            today_energy = max(0.0, today_readings[-1].energy_kwh - today_readings[0].energy_kwh)
            if today_energy == 0.0 and len(today_readings) > 1:
                # Fallback integration if baseline reset
                today_energy = sum(
                    ElectricalCalculator.calculate_energy_kwh(r.active_power, r.simulated_elapsed_seconds)
                    for r in today_readings
                )

        yesterday_energy = 0.0
        if yesterday_readings:
            yesterday_energy = max(0.0, yesterday_readings[-1].energy_kwh - yesterday_readings[0].energy_kwh)
            if yesterday_energy == 0.0 and len(yesterday_readings) > 1:
                yesterday_energy = sum(
                    ElectricalCalculator.calculate_energy_kwh(r.active_power, r.simulated_elapsed_seconds)
                    for r in yesterday_readings
                )

        # Day over day percentage comparison
        dod_change_pct = None
        if yesterday_energy > 0:
            dod_change_pct = round(((today_energy - yesterday_energy) / yesterday_energy) * 100.0, 1)

        estimated_cost = ElectricalCalculator.calculate_estimated_cost(today_energy, tariff)

        # Count alerts generated today
        alert_count_today = (
            session.query(Alert)
            .filter(Alert.timestamp >= today_start)
            .count()
        )

        return {
            "today_energy_kwh": round(today_energy, 4),
            "yesterday_energy_kwh": round(yesterday_energy, 4),
            "change_vs_yesterday_pct": dod_change_pct,
            "estimated_daily_cost": round(estimated_cost, 2),
            "tariff_rate": tariff,
            "peak_power_w": round(peak_power, 2),
            "avg_power_factor": round(avg_pf, 3),
            "alerts_today": alert_count_today,
            "today_readings_count": len(today_readings),
        }

    @staticmethod
    def get_load_profile_distribution(session: Session) -> List[Dict[str, Any]]:
        """Return distribution of readings across load profiles."""
        total = session.query(ElectricalReading).count()
        if total == 0:
            return []

        rows = (
            session.query(
                ElectricalReading.load_profile,
                func.count(ElectricalReading.id).label("count"),
                func.avg(ElectricalReading.active_power).label("avg_power"),
                func.max(ElectricalReading.active_power).label("peak_power"),
            )
            .group_by(ElectricalReading.load_profile)
            .all()
        )

        return [
            {
                "profile": row.load_profile,
                "count": row.count,
                "percentage": round((row.count / total) * 100.0, 1),
                "avg_power_w": round(float(row.avg_power or 0.0), 2),
                "peak_power_w": round(float(row.peak_power or 0.0), 2),
            }
            for row in rows
        ]
