from flask import Blueprint, jsonify, request
from datetime import datetime, timezone, timedelta
from database import get_db_session
from models import ElectricalReading, Alert, SystemEvent
from services.simulator import ElectricalSimulator
from services.overload_detector import OverloadDetector
from routes.ml import get_anomaly_detector
from routes.settings import load_all_settings

simulation_bp = Blueprint("simulation", __name__)

# Global singleton simulator and overload detector instances
simulator = ElectricalSimulator()
overload_detector = OverloadDetector()

def get_simulator() -> ElectricalSimulator:
    return simulator

def get_overload_detector() -> OverloadDetector:
    return overload_detector

def _on_reading_generated(reading_data: dict):
    """Callback triggered whenever simulator emits a new reading in background."""
    try:
        with get_db_session() as session:
            # 1. Save ElectricalReading
            reading = ElectricalReading(
                timestamp=reading_data["timestamp"],
                voltage=reading_data["voltage"],
                current=reading_data["current"],
                active_power=reading_data["active_power"],
                apparent_power=reading_data["apparent_power"],
                reactive_power=reading_data["reactive_power"],
                power_factor=reading_data["power_factor"],
                energy_kwh=reading_data["energy_kwh"],
                load_profile=reading_data["load_profile"],
                simulated_elapsed_seconds=reading_data["simulated_elapsed_seconds"],
            )
            session.add(reading)

            # 2. Evaluate Overload Rules
            settings = load_all_settings(session)
            eval_result = overload_detector.evaluate_reading(
                reading_data,
                settings,
                current_time=reading_data["timestamp"]
            )
            for alert_data in eval_result["alerts_to_create"]:
                alert = Alert(
                    timestamp=alert_data["timestamp"],
                    severity=alert_data["severity"],
                    category=alert_data["category"],
                    parameter=alert_data["parameter"],
                    observed_value=alert_data["observed_value"],
                    threshold_value=alert_data["threshold_value"],
                    message=alert_data["message"],
                    source="RULE_ENGINE",
                    acknowledged=False,
                )
                session.add(alert)

            # 3. Evaluate ML Anomaly Detection if trained
            detector = get_anomaly_detector()
            if detector.status in ("TRAINED", "PREDICTION_AVAILABLE"):
                ml_pred = detector.predict(reading_data)
                if ml_pred.get("is_anomaly"):
                    ml_alert = Alert(
                        timestamp=reading_data["timestamp"],
                        severity="WARNING",
                        category="ML_ANOMALY",
                        parameter="multivariate_pattern",
                        observed_value=reading_data["active_power"],
                        threshold_value=float(ml_pred.get("anomaly_score", 0.0)),
                        message=ml_pred.get("explanation") or "ML Isolation Forest flagged unusual energy pattern.",
                        source="ANOMALY_DETECTOR",
                        acknowledged=False,
                    )
                    session.add(ml_alert)

    except Exception as e:
        # Prevent callback exception from terminating background thread
        pass

# Attach callback to simulator
simulator.on_reading_generated = _on_reading_generated

@simulation_bp.route("/simulation/status", methods=["GET"])
def get_simulation_status():
    status = simulator.get_status()
    with get_db_session() as session:
        latest = session.query(ElectricalReading).order_by(ElectricalReading.timestamp.desc()).first()
        status["latest_reading"] = latest.to_dict() if latest else None
        
        # System health/warning status
        settings = load_all_settings(session)
        latest_dict = latest.to_dict() if latest else {"voltage": 230.0, "current": 0.0, "active_power": 0.0, "power_factor": 1.0}
        eval_res = overload_detector.evaluate_reading(latest_dict, settings)
        status["system_status"] = eval_res["system_status"]
        status["active_violations"] = eval_res["active_violations"]

    return jsonify({"simulation": status}), 200

@simulation_bp.route("/simulation/start", methods=["POST"])
def start_simulation():
    started = simulator.start()
    with get_db_session() as session:
        session.add(SystemEvent(
            event_type="SIMULATION_START",
            description=f"Simulation started in '{simulator.profile}' profile at {simulator.speed}x speed."
        ))
    return jsonify({
        "success": started,
        "message": "Simulation started successfully" if started else "Simulation already running",
        "status": simulator.get_status(),
    }), 200

@simulation_bp.route("/simulation/pause", methods=["POST"])
def pause_simulation():
    paused = simulator.pause()
    with get_db_session() as session:
        session.add(SystemEvent(
            event_type="SIMULATION_PAUSE",
            description="Simulation paused by user."
        ))
    return jsonify({
        "success": paused,
        "message": "Simulation paused" if paused else "Simulation not active or already paused",
        "status": simulator.get_status(),
    }), 200

@simulation_bp.route("/simulation/resume", methods=["POST"])
def resume_simulation():
    resumed = simulator.resume()
    with get_db_session() as session:
        session.add(SystemEvent(
            event_type="SIMULATION_RESUME",
            description="Simulation resumed by user."
        ))
    return jsonify({
        "success": resumed,
        "message": "Simulation resumed" if resumed else "Simulation not paused or not running",
        "status": simulator.get_status(),
    }), 200

@simulation_bp.route("/simulation/stop", methods=["POST"])
def stop_simulation():
    stopped = simulator.stop()
    with get_db_session() as session:
        session.add(SystemEvent(
            event_type="SIMULATION_STOP",
            description="Simulation stopped by user."
        ))
    return jsonify({
        "success": stopped,
        "message": "Simulation stopped" if stopped else "Simulation was not running",
        "status": simulator.get_status(),
    }), 200

@simulation_bp.route("/simulation/profile", methods=["POST"])
def change_profile():
    payload = request.get_json(silent=True) or {}
    profile = payload.get("profile", "").lower()
    if profile not in ElectricalSimulator.PROFILES:
        return jsonify({
            "error": f"Invalid profile '{profile}'. Must be one of {ElectricalSimulator.PROFILES}"
        }), 400

    old_profile = simulator.profile
    simulator.set_profile(profile)
    with get_db_session() as session:
        session.add(SystemEvent(
            event_type="PROFILE_CHANGED",
            description=f"Load profile changed from '{old_profile}' to '{profile}'."
        ))

    return jsonify({
        "message": f"Profile set to '{profile}'",
        "profile": profile,
        "status": simulator.get_status(),
    }), 200

@simulation_bp.route("/simulation/speed", methods=["POST"])
def change_speed():
    payload = request.get_json(silent=True) or {}
    try:
        speed = float(payload.get("speed", 1.0))
    except (ValueError, TypeError):
        return jsonify({"error": "Speed must be a valid float"}), 400

    if not simulator.set_speed(speed):
        return jsonify({"error": "Speed must be between 0.1 and 10.0"}), 400

    return jsonify({
        "message": f"Simulation speed adjusted to {speed}x",
        "speed": speed,
        "status": simulator.get_status(),
    }), 200

@simulation_bp.route("/simulation/generate-demo-data", methods=["POST"])
def generate_demo_data():
    """Generates several hours of realistic demonstration data."""
    payload = request.get_json(silent=True) or {}
    hours = max(1, min(24, int(payload.get("hours", 6))))
    points_per_hour = 20  # 1 reading every 3 simulated minutes
    total_points = hours * points_per_hour

    temp_sim = ElectricalSimulator(random_seed=42)
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=hours)
    step_duration_seconds = (hours * 3600) / total_points

    with get_db_session() as session:
        settings = load_all_settings(session)
        overload_detector.reset_state()
        
        # Determine existing cumulative energy baseline
        last_r = session.query(ElectricalReading).order_by(ElectricalReading.timestamp.desc()).first()
        base_energy = last_r.energy_kwh if last_r else 12.45
        temp_sim.reset_energy(base_energy)

        demo_readings = []
        created_alerts = []

        for i in range(total_points):
            current_ts = start_time + timedelta(seconds=i * step_duration_seconds)
            progress = i / total_points

            # Sequence of realistic intervals:
            # 0% - 40%: Normal household load
            # 40% - 60%: High consumption load (AC/heater active)
            # 60% - 75%: Fluctuating dynamic load
            # 75% - 85%: Controlled Overload scenario (causes genuine rule violations)
            # 85% - 95%: Anomalous profile (severe PF distortion)
            # 95% - 100%: Normal return to baseline
            if progress < 0.40:
                temp_sim.set_profile("normal")
            elif progress < 0.60:
                temp_sim.set_profile("high")
            elif progress < 0.75:
                temp_sim.set_profile("fluctuating")
            elif progress < 0.85:
                temp_sim.set_profile("overload")
            elif progress < 0.95:
                temp_sim.set_profile("anomalous")
            else:
                temp_sim.set_profile("normal")

            temp_sim.interval = step_duration_seconds
            reading_dict = temp_sim.generate_next_reading(custom_time=current_ts)
            
            db_reading = ElectricalReading(
                timestamp=reading_dict["timestamp"],
                voltage=reading_dict["voltage"],
                current=reading_dict["current"],
                active_power=reading_dict["active_power"],
                apparent_power=reading_dict["apparent_power"],
                reactive_power=reading_dict["reactive_power"],
                power_factor=reading_dict["power_factor"],
                energy_kwh=reading_dict["energy_kwh"],
                load_profile=reading_dict["load_profile"],
                simulated_elapsed_seconds=step_duration_seconds,
            )
            session.add(db_reading)
            demo_readings.append(reading_dict)

            # Evaluate overload rules
            eval_res = overload_detector.evaluate_reading(reading_dict, settings, current_time=current_ts)
            for alert_info in eval_res["alerts_to_create"]:
                alert = Alert(
                    timestamp=alert_info["timestamp"],
                    severity=alert_info["severity"],
                    category=alert_info["category"],
                    parameter=alert_info["parameter"],
                    observed_value=alert_info["observed_value"],
                    threshold_value=alert_info["threshold_value"],
                    message=alert_info["message"],
                    source="RULE_ENGINE",
                    acknowledged=False,
                )
                session.add(alert)
                created_alerts.append(alert)

        # Train ML Anomaly Detector on the generated normal baseline and predict anomalous section
        detector = get_anomaly_detector()
        normal_readings = [r for r in demo_readings if r["load_profile"] in ("normal", "standby")]
        if len(normal_readings) >= 30:
            detector.train(normal_readings)
            # Run ML detector on the anomalous portion to flag ML alerts
            for r in demo_readings:
                if r["load_profile"] == "anomalous":
                    pred = detector.predict(r)
                    if pred.get("is_anomaly"):
                        ml_alert = Alert(
                            timestamp=r["timestamp"],
                            severity="WARNING",
                            category="ML_ANOMALY",
                            parameter="multivariate_pattern",
                            observed_value=r["active_power"],
                            threshold_value=float(pred.get("anomaly_score", 0.0)),
                            message=pred.get("explanation") or "ML Isolation Forest flagged anomalous energy pattern.",
                            source="ANOMALY_DETECTOR",
                            acknowledged=False,
                        )
                        session.add(ml_alert)
                        created_alerts.append(ml_alert)

        session.add(SystemEvent(
            event_type="DEMO_DATA_GENERATED",
            description=f"Generated {total_points} synthetic demo readings spanning {hours} hours with {len(created_alerts)} alerts across multiple load profiles."
        ))

        # Sync simulator energy baseline
        simulator.reset_energy(temp_sim.cumulative_energy_kwh)

    return jsonify({
        "success": True,
        "message": f"Successfully generated {total_points} demo readings across {hours} hours.",
        "readings_count": total_points,
        "alerts_generated": len(created_alerts),
        "profiles_simulated": ["normal", "high", "fluctuating", "overload", "anomalous"],
    }), 201

@simulation_bp.route("/simulation/reset", methods=["POST"])
def reset_simulation_data():
    """User-confirmed reset of simulation readings, alerts, and events."""
    payload = request.get_json(silent=True) or {}
    if not payload.get("confirm", False):
        return jsonify({"error": "Explicit confirmation required (confirm: true)"}), 400

    simulator.stop()
    simulator.reset_energy(0.0)
    overload_detector.reset_state()

    with get_db_session() as session:
        session.query(ElectricalReading).delete()
        session.query(Alert).delete()
        session.query(SystemEvent).delete()
        session.add(SystemEvent(
            event_type="SYSTEM_RESET",
            description="Database reset executed by user. All readings, alerts, and events cleared."
        ))

    return jsonify({
        "success": True,
        "message": "Demo data successfully reset. Fresh database state established.",
    }), 200
