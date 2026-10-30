from flask import Blueprint, jsonify, request
from database import get_db_session
from models import AppSetting, SystemEvent
from config import DEFAULT_SETTINGS, VALIDATION_RULES

settings_bp = Blueprint("settings", __name__)

def load_all_settings(session) -> dict:
    """Helper to return current settings dictionary with type conversions."""
    records = session.query(AppSetting).all()
    current = dict(DEFAULT_SETTINGS)
    for r in records:
        key = r.key
        val_str = r.value
        rule = VALIDATION_RULES.get(key, {})
        target_type = rule.get("type", str)
        try:
            if target_type == float:
                current[key] = float(val_str)
            elif target_type == int:
                current[key] = int(val_str)
            elif target_type == bool:
                current[key] = val_str.lower() in ("true", "1", "yes")
            else:
                current[key] = val_str
        except (ValueError, TypeError):
            current[key] = val_str
    return current

@settings_bp.route("/settings", methods=["GET"])
def get_settings():
    with get_db_session() as session:
        settings = load_all_settings(session)
        return jsonify({
            "settings": settings,
            "rules": {
                k: {sk: sv for sk, sv in v.items() if sk != "type"}
                for k, v in VALIDATION_RULES.items()
            }
        }), 200

@settings_bp.route("/settings", methods=["PATCH"])
def update_settings():
    payload = request.get_json(silent=True)
    if not payload or not isinstance(payload, dict):
        return jsonify({"error": "Invalid JSON payload"}), 400

    errors = {}
    validated_updates = {}

    for key, val in payload.items():
        if key not in VALIDATION_RULES:
            # Skip unknown settings safely
            continue

        rule = VALIDATION_RULES[key]
        target_type = rule.get("type", str)

        try:
            typed_val = target_type(val)
        except (ValueError, TypeError):
            errors[key] = f"Value must be of type {target_type.__name__}"
            continue

        if "min" in rule and typed_val < rule["min"]:
            errors[key] = f"Value must be at least {rule['min']}"
            continue
        if "max" in rule and typed_val > rule["max"]:
            errors[key] = f"Value must be at most {rule['max']}"
            continue
        if "enum" in rule and typed_val not in rule["enum"]:
            errors[key] = f"Value must be one of {rule['enum']}"
            continue

        validated_updates[key] = typed_val

    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 422

    if not validated_updates:
        return jsonify({"message": "No valid settings provided to update"}), 200

    with get_db_session() as session:
        for key, val in validated_updates.items():
            setting_obj = session.query(AppSetting).filter_by(key=key).first()
            if not setting_obj:
                setting_obj = AppSetting(key=key, value=str(val))
                session.add(setting_obj)
            else:
                setting_obj.value = str(val)

        # Log system event
        event_desc = f"Settings updated: {', '.join(f'{k}={v}' for k, v in validated_updates.items())}"
        session.add(SystemEvent(event_type="SETTINGS_CHANGED", description=event_desc))
        
        all_settings = load_all_settings(session)

    return jsonify({
        "message": "Settings updated successfully",
        "settings": all_settings,
    }), 200

@settings_bp.route("/settings/reset", methods=["POST"])
def reset_settings():
    with get_db_session() as session:
        for key, val in DEFAULT_SETTINGS.items():
            setting_obj = session.query(AppSetting).filter_by(key=key).first()
            if not setting_obj:
                session.add(AppSetting(key=key, value=str(val)))
            else:
                setting_obj.value = str(val)
        
        session.add(SystemEvent(event_type="SETTINGS_RESET", description="All application settings restored to system defaults."))
        current = load_all_settings(session)

    return jsonify({
        "message": "Settings reset to defaults successfully",
        "settings": current,
    }), 200
