import os
import tempfile
import pytest
from datetime import datetime, timezone, timedelta
from app import create_app
from database import init_db, get_db_session
from models import ElectricalReading, Alert, AppSetting, SystemEvent

@pytest.fixture(scope="module")
def test_client():
    """Create test client backed by an isolated temporary SQLite database."""
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(temp_db_fd)
    db_url = f"sqlite:///{temp_db_path}"

    app = create_app(db_url=db_url)
    app.config["TESTING"] = True
    app.config["DATABASE_URL"] = db_url

    with app.test_client() as client:
        yield client

    # Cleanup temp db
    try:
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
    except Exception:
        pass

def test_database_initialization_and_nondestructive(test_client):
    """Verify init_db initializes tables safely and idempotently without errors."""
    with test_client.application.app_context():
        # Running init_db multiple times must be non-destructive
        init_db(test_client.application.config["DATABASE_URL"])
        init_db(test_client.application.config["DATABASE_URL"])

        with get_db_session(test_client.application.config["DATABASE_URL"]) as session:
            settings_count = session.query(AppSetting).count()
            assert settings_count > 0

def test_health_endpoint(test_client):
    """Verify GET /api/health returns 200 OK with proper metadata."""
    res = test_client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert "Simulation Mode" in data["mode"]

def test_settings_get_and_patch_validation(test_client):
    """Verify settings retrieval, validation on PATCH, and rejection of invalid values."""
    # GET settings
    res = test_client.get("/api/settings")
    assert res.status_code == 200
    data = res.get_json()
    assert "settings" in data
    assert "max_current" in data["settings"]

    # Valid PATCH
    patch_res = test_client.patch("/api/settings", json={"max_current": 20.0, "electricity_tariff": 8.5})
    assert patch_res.status_code == 200
    updated = patch_res.get_json()["settings"]
    assert updated["max_current"] == 20.0
    assert updated["electricity_tariff"] == 8.5

    # Invalid PATCH (current out of bounds: -5.0)
    bad_res = test_client.patch("/api/settings", json={"max_current": -5.0})
    assert bad_res.status_code == 422
    assert "error" in bad_res.get_json()

    # Invalid PATCH (invalid profile enum)
    bad_enum_res = test_client.patch("/api/settings", json={"default_load_profile": "supernova"})
    assert bad_enum_res.status_code == 422

def test_demo_data_generation_and_readings_pagination(test_client):
    """Verify POST /api/simulation/generate-demo-data, reading pagination, and date filtering."""
    # Generate 2 hours of demo data
    gen_res = test_client.post("/api/simulation/generate-demo-data", json={"hours": 2})
    assert gen_res.status_code == 201
    gen_data = gen_res.get_json()
    assert gen_data["success"] is True
    assert gen_data["readings_count"] > 0

    # Test GET /api/readings with pagination
    readings_res = test_client.get("/api/readings?page=1&page_size=10")
    assert readings_res.status_code == 200
    r_data = readings_res.get_json()
    assert len(r_data["items"]) == 10
    assert r_data["total"] >= 40
    assert r_data["page"] == 1

    # Test filtering by load_profile
    profile_res = test_client.get("/api/readings?load_profile=normal")
    assert profile_res.status_code == 200
    for item in profile_res.get_json()["items"]:
        assert item["load_profile"] == "normal"

    # Test date filtering
    now = datetime.now(timezone.utc)
    one_hour_ago = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    now_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    date_res = test_client.get(f"/api/readings?start_date={one_hour_ago}&end_date={now_iso}")
    assert date_res.status_code == 200

def test_readings_latest_and_aggregates(test_client):
    """Verify /api/readings/latest and /api/readings/aggregates."""
    latest_res = test_client.get("/api/readings/latest")
    assert latest_res.status_code == 200
    assert latest_res.get_json()["reading"] is not None

    agg_res = test_client.get("/api/readings/aggregates")
    assert agg_res.status_code == 200
    agg = agg_res.get_json()
    assert agg["count"] > 0
    assert agg["voltage"]["avg"] is not None
    assert agg["current"]["avg"] is not None

def test_alert_query_and_acknowledgment(test_client):
    """Verify alert listing, summary, and acknowledgment persistence."""
    alerts_res = test_client.get("/api/alerts?page=1&page_size=10")
    assert alerts_res.status_code == 200
    alerts_data = alerts_res.get_json()

    if alerts_data["total"] > 0:
        first_alert = alerts_data["items"][0]
        alert_id = first_alert["id"]

        # Acknowledge
        ack_res = test_client.patch(f"/api/alerts/{alert_id}/acknowledge")
        assert ack_res.status_code == 200
        ack_data = ack_res.get_json()["alert"]
        assert ack_data["acknowledged"] is True
        assert ack_data["acknowledged_at"] is not None

    # Summary
    sum_res = test_client.get("/api/alerts/summary")
    assert sum_res.status_code == 200
    assert "total" in sum_res.get_json()["summary"]

def test_analytics_endpoints(test_client):
    """Verify analytics trends, daily summary, and cost estimate."""
    # Consumption
    c_res = test_client.get("/api/analytics/consumption")
    assert c_res.status_code == 200
    assert "consumption" in c_res.get_json()

    # Power trends
    p_res = test_client.get("/api/analytics/power-trends")
    assert p_res.status_code == 200
    assert "trends" in p_res.get_json()

    # Daily summary
    d_res = test_client.get("/api/analytics/daily-summary")
    assert d_res.status_code == 200
    d_data = d_res.get_json()["summary"]
    assert "today_energy_kwh" in d_data
    assert "estimated_daily_cost" in d_data

    # Cost estimate for 100 kWh
    cost_res = test_client.get("/api/analytics/cost-estimate?kwh=100")
    assert cost_res.status_code == 200
    cost_data = cost_res.get_json()
    assert cost_data["energy_kwh"] == 100.0
    assert cost_data["estimated_cost"] > 0

def test_dashboard_summary_and_events(test_client):
    """Verify /api/dashboard/summary and /api/dashboard/recent-events."""
    dash_res = test_client.get("/api/dashboard/summary")
    assert dash_res.status_code == 200
    dash_data = dash_res.get_json()
    assert "metrics" in dash_data
    assert "voltage" in dash_data["metrics"]
    assert "current" in dash_data["metrics"]
    assert "active_power" in dash_data["metrics"]
    assert "system_status" in dash_data

    events_res = test_client.get("/api/dashboard/recent-events")
    assert events_res.status_code == 200
    assert "events" in events_res.get_json()

def test_api_error_handling(test_client):
    """Verify clean JSON responses on 404, bad JSON, or invalid route."""
    res_404 = test_client.get("/api/nonexistent-route-xyz")
    assert res_404.status_code == 404
    assert res_404.is_json

    res_bad_page = test_client.get("/api/readings?page=invalid")
    assert res_bad_page.status_code == 400
    assert res_bad_page.is_json
