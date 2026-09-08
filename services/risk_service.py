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


# Loaded once at module import time — reused across every request, never
# reloaded per-call (same reasoning as the DB engine being created once).
model, feature_columns, model_version = load_latest_model()

DECISION_THRESHOLD = 0.30  # Chosen over the default 0.5 to prioritize recall —
# a missed fraud case is typically costlier than a false alarm an analyst
# clears in seconds. See NOTES.md, Week 1 threshold analysis.


def score_transaction(features: dict) -> dict:
    """Takes a dict of engineered features, returns a risk score + label."""
    row = pd.DataFrame([features])
    row = row.reindex(columns=feature_columns, fill_value=0)

    probability = model.predict_proba(row)[0][1]
    label = "HIGH_RISK" if probability >= DECISION_THRESHOLD else "LOW_RISK"

    return {
        "risk_score": round(float(probability), 4),
        "label": label,
        "model_version": model_version,
    }


def get_feature_importance() -> list[dict]:
    """
    Returns global feature importances from the trained model — which
    features the model relies on most, across all predictions it makes.
    Not a per-transaction explanation (that would need SHAP); this answers
    'what does this model actually pay attention to' at the model level.
    """
    importances = model.feature_importances_
    ranked = sorted(
        zip(feature_columns, importances),
        key=lambda x: x[1],
        reverse=True,
    )
    return [{"feature": name, "importance": round(float(score), 4)} for name, score in ranked]
