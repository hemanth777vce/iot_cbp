from flask import Blueprint, jsonify
from datetime import datetime, timezone

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    """System health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "PowerGuard Backend API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "mode": "Simulation Mode (No physical sensors connected)",
    }), 200
