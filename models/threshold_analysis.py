import numpy as np
from sklearn.metrics import precision_score, recall_score

from models.train_risk_model import prepare_dataset
from sklearn.model_selection import train_test_split
import joblib
from pathlib import Path

MODEL_DIR = Path("models/artifacts")
latest_model_path = sorted(MODEL_DIR.glob("risk_model_v*.joblib"))[-1]
bundle = joblib.load(latest_model_path)
model, feature_columns = bundle["model"], bundle["feature_columns"]

X, y = prepare_dataset()
_, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

probabilities = model.predict_proba(X_test)[:, 1]

print(f"{'Threshold':<10} {'Precision':<10} {'Recall':<10}")
for threshold in np.arange(0.1, 0.6, 0.05):
    preds = (probabilities >= threshold).astype(int)
    p = precision_score(y_test, preds, zero_division=0)
    r = recall_score(y_test, preds, zero_division=0)
    print(f"{threshold:<10.2f} {p:<10.4f} {r:<10.4f}")
