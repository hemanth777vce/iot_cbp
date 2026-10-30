from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session
from models import Alert

class AlertService:
    """Service for managing, persisting, querying, and acknowledging alerts."""

    @staticmethod
    def create_alert(session: Session, alert_data: Dict[str, Any]) -> Alert:
        """Create and persist a new Alert."""
        alert = Alert(
            timestamp=alert_data.get("timestamp") or datetime.now(timezone.utc),
            severity=alert_data["severity"],
            category=alert_data["category"],
            parameter=alert_data["parameter"],
            observed_value=float(alert_data["observed_value"]),
            threshold_value=float(alert_data["threshold_value"]),
            message=alert_data["message"],
            source=alert_data.get("source", "RULE_ENGINE"),
            acknowledged=bool(alert_data.get("acknowledged", False)),
        )
        session.add(alert)
        session.flush()
        return alert

    @staticmethod
    def get_alerts(
        session: Session,
        page: int = 1,
        page_size: int = 20,
        severity: Optional[str] = None,
        source: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch paginated, filtered alerts."""
        query = session.query(Alert)

        if severity:
            query = query.filter(Alert.severity == severity.upper())
        if source:
            query = query.filter(Alert.source == source.upper())
        if acknowledged is not None:
            query = query.filter(Alert.acknowledged == acknowledged)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Alert.message.ilike(search_pattern),
                    Alert.parameter.ilike(search_pattern),
                    Alert.category.ilike(search_pattern),
                )
            )

        total_count = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(desc(Alert.timestamp)).offset(offset).limit(page_size).all()

        return {
            "items": [item.to_dict() for item in items],
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size if page_size > 0 else 0,
        }

    @staticmethod
    def acknowledge_alert(session: Session, alert_id: int) -> Optional[Dict[str, Any]]:
        """Mark an alert as acknowledged without altering observed reading values."""
        alert = session.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        
        alert.acknowledged = True
        alert.acknowledged_at = datetime.now(timezone.utc)
        session.flush()
        return alert.to_dict()

    @staticmethod
    def get_alert_summary(session: Session) -> Dict[str, int]:
        """Compute aggregated counts of alerts by severity and acknowledgment status."""
        total = session.query(Alert).count()
        critical = session.query(Alert).filter(Alert.severity == "CRITICAL").count()
        warning = session.query(Alert).filter(Alert.severity == "WARNING").count()
        unacknowledged = session.query(Alert).filter(Alert.acknowledged == False).count()
        acknowledged = session.query(Alert).filter(Alert.acknowledged == True).count()
        ml_anomalies = session.query(Alert).filter(Alert.source == "ANOMALY_DETECTOR").count()

        return {
            "total": total,
            "critical": critical,
            "warning": warning,
            "unacknowledged": unacknowledged,
            "acknowledged": acknowledged,
            "ml_anomalies": ml_anomalies,
        }
