import joblib
from datetime import datetime
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report,
)

from pipelines.feature_engineering import load_raw_data, engineer_features

MODEL_DIR = Path("models/artifacts")
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def prepare_dataset():
    raw = load_raw_data()
    features = engineer_features(raw)

    # Drop columns the model shouldn't see: IDs are not predictive signal,
    # and leaving raw timestamps/IDs in risks the model "memorizing" noise
    # rather than learning generalizable fraud patterns.
    drop_cols = [
        "id", "sender_account_id", "receiver_account_id",
        "transaction_timestamp", "created_on", "updated_on", "is_fraud",
    ]
    X = features.drop(columns=[c for c in drop_cols if c in features.columns])
    y = features["is_fraud"]
    return X, y


def train_and_evaluate():
    X, y = prepare_dataset()

    # stratify=y: preserves the fraud/non-fraud ratio in both splits.
    # With severe class imbalance, a plain random split can accidentally
    # leave your test set with almost no fraud examples at all.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # class_weight="balanced": tells the model to penalize missing a fraud
    # case more heavily than misclassifying a normal one — without this,
    # a model can get 99.9% accuracy by just predicting "not fraud" always,
    # which is worthless. This is the direct fix for class imbalance.
    model = RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    print("=== Evaluation (NOT accuracy — imbalanced classes) ===")
    print(f"Precision: {precision_score(y_test, y_pred):.4f}")
    print(f"Recall:    {recall_score(y_test, y_pred):.4f}")
    print(f"F1:        {f1_score(y_test, y_pred):.4f}")
    print(f"ROC-AUC:   {roc_auc_score(y_test, y_proba):.4f}")
    print("\nConfusion matrix:\n", confusion_matrix(y_test, y_pred))
    print("\n", classification_report(y_test, y_pred))

    # Version the model file with a timestamp — per the PRD's AI/ML
    # Architecture section: every prediction should trace back to which
    # model version produced it.
    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = MODEL_DIR / f"risk_model_v{version}.joblib"
    joblib.dump({"model": model, "feature_columns": X.columns.tolist()}, model_path)
    print(f"\n✅ Model saved: {model_path}")


if __name__ == "__main__":
    train_and_evaluate()

