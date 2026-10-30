import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Intelligent Machine Learning Anomaly Detection using Isolation Forest.
    
    Trained on multivariate electrical readings with feature engineering to detect
    abnormal energy profiles, phase balance issues, harmonic distortions, or irregular spikes.
    """

    FEATURE_NAMES = [
        "voltage",
        "current",
        "active_power",
        "apparent_power",
        "power_factor",
        "rolling_mean_power",
        "power_deviation",
    ]

    def __init__(self, contamination: float = 0.05, min_samples: int = 30, random_state: int = 42):
        self.contamination = contamination
        self.min_samples = min_samples
        self.random_state = random_state
        self.model: Optional[IsolationForest] = None
        self.training_feature_means: Dict[str, float] = {}
        self.training_feature_stds: Dict[str, float] = {}
        self.status = "NOT_TRAINED"
        self.last_trained_sample_count = 0
        self.training_timestamp = None

    def get_status(self) -> Dict[str, Any]:
        """Return the current model status and metadata."""
        return {
            "status": self.status,
            "min_samples_required": self.min_samples,
            "samples_trained_on": self.last_trained_sample_count,
            "contamination": self.contamination,
            "trained_at": self.training_timestamp.isoformat() if self.training_timestamp else None,
            "features": self.FEATURE_NAMES,
            "model_type": "Isolation Forest (scikit-learn)",
        }

    def _prepare_dataframe(self, readings: List[Dict[str, Any]]) -> pd.DataFrame:
        """Extract and engineer required ML features from reading dictionaries."""
        if not readings:
            return pd.DataFrame(columns=self.FEATURE_NAMES)

        df = pd.DataFrame(readings)

        # Ensure essential columns exist
        for col in ["voltage", "current", "active_power", "apparent_power", "power_factor"]:
            if col not in df.columns:
                df[col] = 0.0
            else:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        # Feature Engineering: Rolling mean power & power deviation
        # Use a rolling window of 5 readings (or smaller if fewer)
        window_size = min(5, len(df))
        df["rolling_mean_power"] = df["active_power"].rolling(window=window_size, min_periods=1).mean()
        df["power_deviation"] = (df["active_power"] - df["rolling_mean_power"]).abs()

        return df[self.FEATURE_NAMES].copy()

    def train(self, readings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train Isolation Forest model on historical readings."""
        if not readings or len(readings) < self.min_samples:
            self.status = "INSUFFICIENT_DATA"
            return {
                "success": False,
                "status": self.status,
                "message": f"Insufficient data: {len(readings) if readings else 0} readings available, minimum {self.min_samples} required.",
                "sample_count": len(readings) if readings else 0,
            }

        df = self._prepare_dataframe(readings)
        
        # Fit Isolation Forest
        model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100,
            max_samples="auto",
        )
        model.fit(df.values)

        self.model = model
        self.status = "TRAINED"
        self.last_trained_sample_count = len(df)
        from datetime import datetime, timezone
        self.training_timestamp = datetime.now(timezone.utc)

        # Cache baseline statistics for anomaly explanation
        for col in self.FEATURE_NAMES:
            self.training_feature_means[col] = float(df[col].mean())
            self.training_feature_stds[col] = float(df[col].std()) if df[col].std() > 0 else 1.0

        return {
            "success": True,
            "status": self.status,
            "message": f"Isolation Forest successfully trained on {len(df)} readings.",
            "sample_count": len(df),
            "contamination": self.contamination,
        }

    def predict(self, reading: Dict[str, Any], recent_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Predict whether a reading is an anomaly.
        
        Returns:
            Dictionary with is_anomaly, anomaly_score, explanation, and model status.
        """
        if self.model is None or self.status not in ("TRAINED", "PREDICTION_AVAILABLE"):
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "explanation": "Model not trained yet",
                "status": self.status,
            }

        # Build feature vector incorporating recent history for rolling metrics
        all_readings = (recent_history or []) + [reading]
        df = self._prepare_dataframe(all_readings)
        feature_vector = df.iloc[[-1]].values

        # Isolation forest: -1 indicates anomaly, 1 indicates normal
        prediction = self.model.predict(feature_vector)[0]
        # Decision function: lower values mean more anomalous
        score = float(self.model.decision_function(feature_vector)[0])
        is_anomaly = bool(prediction == -1)

        explanation = None
        if is_anomaly:
            explanation = self._generate_explanation(df.iloc[-1])

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(score, 4),
            "explanation": explanation,
            "status": "PREDICTION_AVAILABLE",
        }

    def _generate_explanation(self, row: pd.Series) -> str:
        """Determine which features deviated most from training normal baselines."""
        reasons = []
        for feat in self.FEATURE_NAMES:
            mean = self.training_feature_means.get(feat, 0.0)
            std = self.training_feature_stds.get(feat, 1.0)
            val = float(row[feat])
            z_score = abs(val - mean) / (std if std > 1e-4 else 1.0)

            if z_score >= 2.5:
                if feat == "power_factor":
                    reasons.append(f"power factor ({val:.2f}) deviated significantly from normal mean ({mean:.2f})")
                elif feat == "active_power":
                    reasons.append(f"active power ({val:.0f}W) unusual for observed load profile")
                elif feat == "power_deviation":
                    reasons.append(f"sharp rapid deviation ({val:.0f}W) from rolling baseline")
                elif feat == "current":
                    reasons.append(f"current draw ({val:.2f}A) outside typical distribution")
                elif feat == "voltage":
                    reasons.append(f"voltage fluctuations ({val:.1f}V)")

        if reasons:
            return f"ML Anomaly: {', '.join(reasons[:2])}."
        return "ML Anomaly: Multivariate pattern deviated from normal cluster."
