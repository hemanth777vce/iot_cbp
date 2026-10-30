from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, Text, Index
from database import Base

def utc_now():
    return datetime.now(timezone.utc)

class ElectricalReading(Base):
    __tablename__ = "electrical_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=utc_now, index=True, nullable=False)
    voltage = Column(Float, nullable=False)
    current = Column(Float, nullable=False)
    active_power = Column(Float, nullable=False)
    apparent_power = Column(Float, nullable=False)
    reactive_power = Column(Float, nullable=False)
    power_factor = Column(Float, nullable=False)
    energy_kwh = Column(Float, nullable=False)
    load_profile = Column(String(50), default="normal", index=True, nullable=False)
    simulated_elapsed_seconds = Column(Float, default=1.0, nullable=False)

    __table_args__ = (
        Index("idx_reading_time_profile", "timestamp", "load_profile"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "voltage": round(self.voltage, 2),
            "current": round(self.current, 2),
            "active_power": round(self.active_power, 2),
            "apparent_power": round(self.apparent_power, 2),
            "reactive_power": round(self.reactive_power, 2),
            "power_factor": round(self.power_factor, 3),
            "energy_kwh": round(self.energy_kwh, 5),
            "load_profile": self.load_profile,
            "simulated_elapsed_seconds": round(self.simulated_elapsed_seconds, 2),
        }

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=utc_now, index=True, nullable=False)
    severity = Column(String(20), index=True, nullable=False)  # "WARNING", "CRITICAL", "INFO"
    category = Column(String(50), nullable=False)             # "CURRENT_OVERLOAD", "POWER_OVERLOAD", etc.
    parameter = Column(String(50), nullable=False)            # "current", "active_power", "voltage", etc.
    observed_value = Column(Float, nullable=False)
    threshold_value = Column(Float, nullable=False)
    message = Column(Text, nullable=False)
    source = Column(String(50), default="RULE_ENGINE", nullable=False)  # "RULE_ENGINE" or "ANOMALY_DETECTOR"
    acknowledged = Column(Boolean, default=False, index=True, nullable=False)
    acknowledged_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_alert_severity_ack", "severity", "acknowledged"),
        Index("idx_alert_timestamp_ack", "timestamp", "acknowledged"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "severity": self.severity,
            "category": self.category,
            "parameter": self.parameter,
            "observed_value": round(self.observed_value, 2),
            "threshold_value": round(self.threshold_value, 2),
            "message": self.message,
            "source": self.source,
            "acknowledged": self.acknowledged,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
        }

class SystemEvent(Base):
    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=utc_now, index=True, nullable=False)
    event_type = Column(String(50), index=True, nullable=False)
    description = Column(Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "event_type": self.event_type,
            "description": self.description,
        }

class AppSetting(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(String(255), nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
