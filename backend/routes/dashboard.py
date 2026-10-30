from flask import Blueprint, jsonify
from datetime import datetime, timezone
from sqlalchemy import desc
from database import get_db_session
from models import ElectricalReading, Alert, SystemEvent
from services.analytics_service import AnalyticsService
from routes.settings import load_all_settings
from routes.simulation import get_simulator, get_overload_detector

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard/summary", methods=["GET"])
def get_dashboard_summary():
    with get_db_session() as session:
        settings = load_all_settings(session)
        tariff = float(settings.get("electricity_tariff", 7.50))
        currency = settings.get("currency_symbol", "₹")

        latest = session.query(ElectricalReading).order_by(desc(ElectricalReading.timestamp)).first()
        
        sim = get_simulator()
        detector = get_overload_detector()

        if latest:
            reading_dict = latest.to_dict()
        else:
            reading_dict = {
                "voltage": 230.0,
                "current": 0.0,
                "active_power": 0.0,
                "apparent_power": 0.0,
                "reactive_power": 0.0,
                "power_factor": 1.0,
                "energy_kwh": 0.0,
                "load_profile": sim.profile,
                "timestamp": None,
            }

        eval_res = detector.evaluate_reading(reading_dict, settings)
        daily_summary = AnalyticsService.get_daily_summary(session, tariff=tariff)

        # Recent alerts
        recent_alerts = (
            session.query(Alert)
            .order_by(desc(Alert.timestamp))
            .limit(5)
            .all()
        )

        unacknowledged_alerts = session.query(Alert).filter(Alert.acknowledged == False).count()

        summary_payload = {
            "metrics": {
                "voltage": {
                    "value": reading_dict["voltage"],
                    "unit": "V",
                    "min_limit": settings.get("voltage_min", 207.0),
                    "max_limit": settings.get("voltage_max", 253.0),
                    "status": "normal" if settings.get("voltage_min", 207.0) <= reading_dict["voltage"] <= settings.get("voltage_max", 253.0) else "warning",
                },
                "current": {
                    "value": reading_dict["current"],
                    "unit": "A",
                    "max_threshold": settings.get("max_current", 16.0),
                    "status": "critical" if reading_dict["current"] >= settings.get("max_current", 16.0) else ("warning" if reading_dict["current"] >= 0.85 * settings.get("max_current", 16.0) else "normal"),
                },
                "active_power": {
                    "value": reading_dict["active_power"],
                    "unit": "W",
                    "max_threshold": settings.get("max_active_power", 3600.0),
                    "status": "critical" if reading_dict["active_power"] >= settings.get("max_active_power", 3600.0) else ("warning" if reading_dict["active_power"] >= 0.85 * settings.get("max_active_power", 3600.0) else "normal"),
                },
                "apparent_power": {
                    "value": reading_dict.get("apparent_power", 0.0),
                    "unit": "VA",
                },
                "reactive_power": {
                    "value": reading_dict.get("reactive_power", 0.0),
                    "unit": "var",
                },
                "power_factor": {
                    "value": reading_dict["power_factor"],
                    "min_threshold": settings.get("min_power_factor", 0.80),
                    "status": "normal" if reading_dict["power_factor"] >= settings.get("min_power_factor", 0.80) else "warning",
                },
                "cumulative_energy": {
                    "value": reading_dict["energy_kwh"],
                    "unit": "kWh",
                },
            },
            "system_status": eval_res["system_status"],
            "active_violations": eval_res["active_violations"],
            "simulation": {
                "is_running": sim.is_running,
                "is_paused": sim.is_paused,
                "profile": sim.profile,
                "speed": sim.speed,
            },
            "consumption_summary": {
                "today_energy_kwh": daily_summary["today_energy_kwh"],
                "estimated_daily_cost": daily_summary["estimated_daily_cost"],
                "currency_symbol": currency,
                "tariff": tariff,
                "change_vs_yesterday_pct": daily_summary["change_vs_yesterday_pct"],
                "peak_power_w": daily_summary["peak_power_w"],
                "alerts_today": daily_summary["alerts_today"],
                "unacknowledged_alerts": unacknowledged_alerts,
            },
            "recent_alerts": [a.to_dict() for a in recent_alerts],
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        return jsonify(summary_payload), 200

@dashboard_bp.route("/dashboard/recent-readings", methods=["GET"])
def get_recent_readings():
    with get_db_session() as session:
        readings = (
            session.query(ElectricalReading)
            .order_by(desc(ElectricalReading.timestamp))
            .limit(30)
            .all()
        )
        readings.reverse()
        return jsonify({
            "readings": [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "time_label": r.timestamp.strftime("%H:%M:%S"),
                    "voltage": r.voltage,
                    "current": r.current,
                    "active_power": r.active_power,
                    "power_factor": r.power_factor,
                    "energy_kwh": r.energy_kwh,
                }
                for r in readings
            ]
        }), 200

@dashboard_bp.route("/dashboard/recent-events", methods=["GET"])
def get_recent_events():
    with get_db_session() as session:
        events = (
            session.query(SystemEvent)
            .order_by(desc(SystemEvent.timestamp))
            .limit(15)
            .all()
        )
        return jsonify({"events": [e.to_dict() for e in events]}), 200
