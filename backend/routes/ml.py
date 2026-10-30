from flask import Blueprint, jsonify, request
from database import get_db_session
from models import ElectricalReading, Alert, SystemEvent
from services.anomaly_detector import AnomalyDetector
from routes.settings import load_all_settings

ml_bp = Blueprint("ml", __name__)

# Global anomaly detector instance
anomaly_detector = AnomalyDetector()

def get_anomaly_detector() -> AnomalyDetector:
    global anomaly_detector
    return anomaly_detector

@ml_bp.route("/ml/status", methods=["GET"])
def get_status():
    detector = get_anomaly_detector()
    status_info = detector.get_status()

    # Query current historical reading count for context
    with get_db_session() as session:
        available_readings = session.query(ElectricalReading).count()
        status_info["available_readings_in_db"] = available_readings

    return jsonify({"ml_status": status_info}), 200

@ml_bp.route("/ml/train", methods=["POST"])
def train_model():
    detector = get_anomaly_detector()
    with get_db_session() as session:
        settings = load_all_settings(session)
        contamination = float(settings.get("anomaly_contamination", 0.05))
        min_samples = int(settings.get("anomaly_min_samples", 30))

        detector.contamination = contamination
        detector.min_samples = min_samples

        readings = (
            session.query(ElectricalReading)
            .order_by(ElectricalReading.timestamp.asc())
            .all()
        )
        readings_data = [r.to_dict() for r in readings]

        result = detector.train(readings_data)

        if result.get("success"):
            session.add(SystemEvent(
                event_type="ML_MODEL_TRAINED",
                description=f"Isolation Forest model successfully trained on {result['sample_count']} historical readings (contamination={contamination})."
            ))

    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code

@ml_bp.route("/ml/anomalies", methods=["GET"])
def get_ml_anomalies():
    """Retrieve alerts flagged by the ML anomaly detector."""
    with get_db_session() as session:
        ml_alerts = (
            session.query(Alert)
            .filter(Alert.source == "ANOMALY_DETECTOR")
            .order_by(Alert.timestamp.desc())
            .limit(50)
            .all()
        )
        return jsonify({
            "anomalies": [a.to_dict() for a in ml_alerts],
            "count": len(ml_alerts),
        }), 200
