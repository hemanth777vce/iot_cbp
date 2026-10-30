from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
from sqlalchemy import desc, func
from database import get_db_session
from models import ElectricalReading
from services.electrical_calculator import ElectricalCalculator

readings_bp = Blueprint("readings", __name__)

def parse_iso_datetime(date_str: str):
    """Safely parse ISO datetime string, handling URL decoded '+' signs."""
    if not date_str:
        return None
    try:
        # In URL query params, '+' can be decoded to a space. Fix space before timezone offset
        clean_str = date_str.strip().replace("Z", "+00:00")
        if " " in clean_str and ("+" not in clean_str):
            # Check if space is separating date/time or time/offset
            parts = clean_str.split(" ")
            if len(parts) == 2 and ":" in parts[1] and ("-" in parts[0] or ":" in parts[0]):
                if len(parts[1]) == 5: # e.g. 00:00 offset
                    clean_str = f"{parts[0]}+{parts[1]}"
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        raise ValueError(f"Invalid ISO datetime: {date_str}")

@readings_bp.route("/readings", methods=["GET"])
def get_readings():
    try:
        page = max(1, int(request.args.get("page", 1)))
        page_size = min(200, max(1, int(request.args.get("page_size", 50))))
    except ValueError:
        return jsonify({"error": "Page and page_size must be positive integers"}), 400

    profile = request.args.get("load_profile")
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    try:
        start_date = parse_iso_datetime(start_date_str)
        end_date = parse_iso_datetime(end_date_str)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if start_date and end_date and start_date > end_date:
        return jsonify({"error": "start_date cannot be after end_date"}), 400

    with get_db_session() as session:
        query = session.query(ElectricalReading)
        if profile:
            query = query.filter(ElectricalReading.load_profile == profile.lower())
        if start_date:
            query = query.filter(ElectricalReading.timestamp >= start_date)
        if end_date:
            query = query.filter(ElectricalReading.timestamp <= end_date)

        total_count = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(desc(ElectricalReading.timestamp)).offset(offset).limit(page_size).all()

        return jsonify({
            "items": [item.to_dict() for item in items],
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size if page_size > 0 else 0,
        }), 200

@readings_bp.route("/readings/latest", methods=["GET"])
def get_latest_reading():
    with get_db_session() as session:
        reading = session.query(ElectricalReading).order_by(desc(ElectricalReading.timestamp)).first()
        if not reading:
            return jsonify({"reading": None, "message": "No readings recorded yet"}), 200
        return jsonify({"reading": reading.to_dict()}), 200

@readings_bp.route("/readings/aggregates", methods=["GET"])
def get_aggregates():
    profile = request.args.get("load_profile")
    with get_db_session() as session:
        query = session.query(ElectricalReading)
        if profile:
            query = query.filter(ElectricalReading.load_profile == profile.lower())

        count = query.count()
        if count == 0:
            return jsonify({
                "count": 0,
                "voltage": {"min": None, "max": None, "avg": None},
                "current": {"min": None, "max": None, "avg": None},
                "active_power": {"min": None, "max": None, "avg": None},
                "power_factor": {"min": None, "max": None, "avg": None},
            }), 200

        res = query.with_entities(
            func.min(ElectricalReading.voltage), func.max(ElectricalReading.voltage), func.avg(ElectricalReading.voltage),
            func.min(ElectricalReading.current), func.max(ElectricalReading.current), func.avg(ElectricalReading.current),
            func.min(ElectricalReading.active_power), func.max(ElectricalReading.active_power), func.avg(ElectricalReading.active_power),
            func.min(ElectricalReading.power_factor), func.max(ElectricalReading.power_factor), func.avg(ElectricalReading.power_factor),
        ).first()

        return jsonify({
            "count": count,
            "voltage": {"min": round(float(res[0]), 2), "max": round(float(res[1]), 2), "avg": round(float(res[2]), 2)},
            "current": {"min": round(float(res[3]), 2), "max": round(float(res[4]), 2), "avg": round(float(res[5]), 2)},
            "active_power": {"min": round(float(res[6]), 2), "max": round(float(res[7]), 2), "avg": round(float(res[8]), 2)},
            "power_factor": {"min": round(float(res[9]), 3), "max": round(float(res[10]), 3), "avg": round(float(res[11]), 3)},
        }), 200
