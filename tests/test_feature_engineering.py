from pipelines.feature_engineering import build_inference_features

def test_build_inference_features_shape():
    raw = {
        "amount": 5000, "sender_balance_before": 5000, "sender_balance_after": 0,
        "receiver_balance_before": 0, "receiver_balance_after": 5000,
        "hour_of_day": 3, "day_of_week": 6, "transaction_type": "TRANSFER",
    }
    features = build_inference_features(raw)
    assert features["sender_balance_delta"] == 5000
    assert features["is_night"] == 1
    assert features["type_TRANSFER"] == 1
    assert features["type_CASH_IN"] == 0
    # Regression guard — these must NEVER reappear (Week 1 leakage incident)
    assert "sender_balance_error" not in features
    assert "sender_emptied_account" not in features
    assert "receiver_balance_error" not in features

def test_is_night_boundary():
    raw = {
        "amount": 100, "sender_balance_before": 100, "sender_balance_after": 0,
        "receiver_balance_before": 0, "receiver_balance_after": 100,
        "hour_of_day": 12, "day_of_week": 2, "transaction_type": "PAYMENT",
    }
    assert build_inference_features(raw)["is_night"] == 0
