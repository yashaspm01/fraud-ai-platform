import joblib
import pandas as pd
from pathlib import Path

MODEL_DIR = Path("models/artifacts")


def load_latest_model():
    model_files = sorted(MODEL_DIR.glob("risk_model_v*.joblib"))
    if not model_files:
        raise FileNotFoundError("No trained model found. Run models/train_risk_model.py first.")
    latest = model_files[-1]
    bundle = joblib.load(latest)
    return bundle["model"], bundle["feature_columns"], latest.name


_model, _feature_columns, _model_version = load_latest_model()


def score_transaction(features: dict) -> dict:
    """Takes a dict of engineered features, returns a risk score + label."""
    row = pd.DataFrame([features])
    row = row.reindex(columns=_feature_columns, fill_value=0)

    probability = _model.predict_proba(row)[0][1]
    label = "HIGH_RISK" if probability >= 0.5 else "LOW_RISK"

    return {
        "risk_score": round(float(probability), 4),
        "label": label,
        "model_version": _model_version,
    }
