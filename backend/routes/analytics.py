from flask import Blueprint, jsonify, request
from database import get_db_session
from services.analytics_service import AnalyticsService
from services.electrical_calculator import ElectricalCalculator
from routes.settings import load_all_settings
from routes.readings import parse_iso_datetime

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/analytics/consumption", methods=["GET"])
def get_consumption():
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    interval = request.args.get("interval", "hourly")

    try:
        start_date = parse_iso_datetime(start_date_str)
        end_date = parse_iso_datetime(end_date_str)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    with get_db_session() as session:
        data = AnalyticsService.get_consumption_trends(
            session=session,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
        )
        return jsonify({"consumption": data, "interval": interval}), 200

@analytics_bp.route("/analytics/power-trends", methods=["GET"])
def get_power_trends():
    limit = min(500, max(10, int(request.args.get("limit", 100))))
    with get_db_session() as session:
        trends = AnalyticsService.get_power_trends(session, limit=limit)
        return jsonify({"trends": trends}), 200

@analytics_bp.route("/analytics/voltage-trends", methods=["GET"])
def get_voltage_trends():
    limit = min(500, max(10, int(request.args.get("limit", 100))))
    with get_db_session() as session:
        trends = AnalyticsService.get_voltage_and_current_trends(session, limit=limit)
        return jsonify({
            "trends": [{"timestamp": t["timestamp"], "time_label": t["time_label"], "voltage": t["voltage"]} for t in trends]
        }), 200

@analytics_bp.route("/analytics/current-trends", methods=["GET"])
def get_current_trends():
    limit = min(500, max(10, int(request.args.get("limit", 100))))
    with get_db_session() as session:
        trends = AnalyticsService.get_voltage_and_current_trends(session, limit=limit)
        return jsonify({
            "trends": [{"timestamp": t["timestamp"], "time_label": t["time_label"], "current": t["current"]} for t in trends]
        }), 200

@analytics_bp.route("/analytics/daily-summary", methods=["GET"])
def get_daily_summary():
    with get_db_session() as session:
        settings = load_all_settings(session)
        tariff = float(settings.get("electricity_tariff", 7.50))
        summary = AnalyticsService.get_daily_summary(session, tariff=tariff)
        summary["currency_symbol"] = settings.get("currency_symbol", "₹")
        return jsonify({"summary": summary}), 200

@analytics_bp.route("/analytics/cost-estimate", methods=["GET"])
def get_cost_estimate():
    try:
        kwh = float(request.args.get("kwh", 0.0))
    except ValueError:
        return jsonify({"error": "kwh must be a valid number"}), 400

    with get_db_session() as session:
        settings = load_all_settings(session)
        tariff = float(settings.get("electricity_tariff", 7.50))
        currency = settings.get("currency_symbol", "₹")
        cost = ElectricalCalculator.calculate_estimated_cost(kwh, tariff)

        return jsonify({
            "energy_kwh": round(kwh, 4),
            "tariff": tariff,
            "currency_symbol": currency,
            "estimated_cost": round(cost, 2),
            "disclaimer": "Estimated electricity cost based on simulated energy consumption and configured tariff rate.",
        }), 200

@analytics_bp.route("/analytics/profiles", methods=["GET"])
def get_profile_distribution():
    with get_db_session() as session:
        distribution = AnalyticsService.get_load_profile_distribution(session)
        return jsonify({"distribution": distribution}), 200
