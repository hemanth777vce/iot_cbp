import os
import sys
from pathlib import Path
from flask import Flask, jsonify
from flask_cors import CORS

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from database import init_db
from routes.health import health_bp
from routes.dashboard import dashboard_bp
from routes.readings import readings_bp
from routes.alerts import alerts_bp
from routes.analytics import analytics_bp
from routes.simulation import simulation_bp
from routes.settings import settings_bp
from routes.ml import ml_bp

def create_app(db_url=None):
    """Application factory for PowerGuard Flask backend."""
    app = Flask(__name__)
    
    # Enable CORS for local Vite development server
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173", "*"]}})

    # Register blueprints under /api prefix
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(readings_bp, url_prefix="/api")
    app.register_blueprint(alerts_bp, url_prefix="/api")
    app.register_blueprint(analytics_bp, url_prefix="/api")
    app.register_blueprint(simulation_bp, url_prefix="/api")
    app.register_blueprint(settings_bp, url_prefix="/api")
    app.register_blueprint(ml_bp, url_prefix="/api")

    # Safe error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found", "status_code": 404}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed", "status_code": 405}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "An internal server error occurred", "status_code": 500}), 500

    # Initialize database tables and default configuration
    with app.app_context():
        init_db(db_url)

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Host localhost strictly by default as per security specification
    app.run(host="127.0.0.1", port=port, debug=False)
