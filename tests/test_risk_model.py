import joblib
import pandas as pd
from pathlib import Path
from pipelines.feature_engineering import build_inference_features

def test_model_loads_and_predicts_in_range():
    model_files = sorted(Path("models/artifacts").glob("risk_model_v*.joblib"))
    assert model_files, "No trained model found — run models/train_risk_model.py first"

    bundle = joblib.load(model_files[-1])
    model, feature_columns = bundle["model"], bundle["feature_columns"]

    raw = {
        "amount": 5000, "sender_balance_before": 5000, "sender_balance_after": 0,
        "receiver_balance_before": 0, "receiver_balance_after": 5000,
        "hour_of_day": 3, "day_of_week": 6, "transaction_type": "TRANSFER",
    }
    row = pd.DataFrame([build_inference_features(raw)]).reindex(columns=feature_columns, fill_value=0)
    proba = model.predict_proba(row)[0][1]
    assert 0.0 <= proba <= 1.0
