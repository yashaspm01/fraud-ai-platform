import pandas as pd
from sqlalchemy import create_engine
from database.connection import DATABASE_URL


def load_raw_data() -> pd.DataFrame:
    engine = create_engine(DATABASE_URL)
    query = "SELECT * FROM transactions;"
    return pd.read_sql(query, engine)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Did this transaction drain the sender's balance? Fraud often empties accounts.
    df["sender_balance_delta"] = df["sender_balance_before"] - df["sender_balance_after"]
    #df["sender_emptied_account"] = (df["sender_balance_after"] == 0).astype(int)

    # Balance mismatches: legit systems update both sides consistently.
    # A mismatch (delta doesn't match amount) is itself a signal.
    #df["sender_balance_error"] = (
    #    df["sender_balance_before"] - df["amount"] - df["sender_balance_after"]
    #).abs()

    #df["receiver_balance_error"] = (
    #    df["receiver_balance_before"] + df["amount"] - df["receiver_balance_after"]
    #).abs()

    # Time-based features — this is exactly why we anchored to a fixed,
    # real start date earlier instead of "now": these features are only
    # meaningful with consistent real timestamps.
    df["hour_of_day"] = df["transaction_timestamp"].dt.hour
    df["is_night"] = df["hour_of_day"].apply(lambda h: 1 if h < 6 or h >= 22 else 0)
    df["day_of_week"] = df["transaction_timestamp"].dt.dayofweek

    # One-hot encode transaction_type — models need numbers, not category labels.
    df = pd.get_dummies(df, columns=["transaction_type"], prefix="type")

    return df


if __name__ == "__main__":
    raw = load_raw_data()
    features = engineer_features(raw)
    print(features.shape)
    print(features.columns.tolist())
