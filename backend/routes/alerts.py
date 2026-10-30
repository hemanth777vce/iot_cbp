from flask import Blueprint, jsonify, request
from database import get_db_session
from models import Alert, SystemEvent
from services.alert_service import AlertService

alerts_bp = Blueprint("alerts", __name__)

@alerts_bp.route("/alerts", methods=["GET"])
def get_alerts():
    try:
        page = max(1, int(request.args.get("page", 1)))
        page_size = min(100, max(1, int(request.args.get("page_size", 20))))
    except ValueError:
        return jsonify({"error": "Page and page_size must be positive integers"}), 400

    severity = request.args.get("severity")
    source = request.args.get("source")
    search = request.args.get("search")
    ack_param = request.args.get("acknowledged")
    acknowledged = None
    if ack_param is not None:
        acknowledged = ack_param.lower() in ("true", "1", "yes")

    with get_db_session() as session:
        result = AlertService.get_alerts(
            session=session,
            page=page,
            page_size=page_size,
            severity=severity,
            source=source,
            acknowledged=acknowledged,
            search=search,
        )
        return jsonify(result), 200

@alerts_bp.route("/alerts/<int:alert_id>", methods=["GET"])
def get_alert_by_id(alert_id: int):
    with get_db_session() as session:
        alert = session.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return jsonify({"error": f"Alert with ID {alert_id} not found"}), 404
        return jsonify({"alert": alert.to_dict()}), 200

@alerts_bp.route("/alerts/<int:alert_id>/acknowledge", methods=["PATCH"])
def acknowledge_alert(alert_id: int):
    with get_db_session() as session:
        updated = AlertService.acknowledge_alert(session, alert_id)
        if not updated:
            return jsonify({"error": f"Alert with ID {alert_id} not found"}), 404

        session.add(SystemEvent(
            event_type="ALERT_ACKNOWLEDGED",
            description=f"Alert #{alert_id} ({updated['category']} - {updated['severity']}) acknowledged by user."
        ))

        return jsonify({
            "message": f"Alert #{alert_id} acknowledged successfully",
            "alert": updated,
        }), 200

@alerts_bp.route("/alerts/summary", methods=["GET"])
def get_alert_summary():
    with get_db_session() as session:
        summary = AlertService.get_alert_summary(session)
        return jsonify({"summary": summary}), 200
