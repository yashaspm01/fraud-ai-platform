from datetime import datetime, timedelta, timezone
import pandas as pd
from sqlalchemy import create_engine

from database.connection import DATABASE_URL

# Fixed anchor: PaySim's `step` is "hours since simulation start" — not a
# real date. We anchor to a fixed, arbitrary Monday so time-of-day /
# day-of-week features are consistent across every re-run of this script.
SIMULATION_START = datetime(2026, 1, 5, 0, 0, 0, tzinfo=timezone.utc)

SAMPLE_SIZE = 200_000  # documented scope decision — see NOTES.md

RAW_CSV_PATH = "pipelines/data/raw/paysim.csv"


def extract() -> pd.DataFrame:
    """Read a sample of PaySim's raw CSV."""
    df = pd.read_csv(RAW_CSV_PATH, nrows=SAMPLE_SIZE)
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Translate PaySim's raw shape into our schema's shape."""

    df = df.rename(columns={
        "type": "transaction_type",
        "nameOrig": "sender_account_id",
        "oldbalanceOrg": "sender_balance_before",
        "newbalanceOrig": "sender_balance_after",
        "nameDest": "receiver_account_id",
        "oldbalanceDest": "receiver_balance_before",
        "newbalanceDest": "receiver_balance_after",
        "isFraud": "is_fraud",
    })

    # step (int hours) -> real TIMESTAMPTZ, anchored to a fixed start date
    df["transaction_timestamp"] = df["step"].apply(
        lambda step: SIMULATION_START + timedelta(hours=int(step))
    )

    # isFraud arrives as 0/1 -> proper boolean
    df["is_fraud"] = df["is_fraud"].astype(bool)

    # Keep only the columns our transactions table actually has —
    # drop PaySim's isFlaggedFraud and the raw step column, which we don't model.
    df = df[[
        "transaction_type",
        "amount",
        "sender_account_id",
        "sender_balance_before",
        "sender_balance_after",
        "receiver_account_id",
        "receiver_balance_before",
        "receiver_balance_after",
        "transaction_timestamp",
        "is_fraud",
    ]]

    return df


def load(df: pd.DataFrame) -> None:
    """Bulk-insert the cleaned data into Postgres."""
    engine = create_engine(DATABASE_URL)
    df.to_sql(
        "transactions",
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000,
    )


if __name__ == "__main__":
    print("Extracting...")
    raw_df = extract()
    print(f"  → {len(raw_df):,} rows read")

    print("Transforming...")
    clean_df = transform(raw_df)

    print("Loading into Postgres...")
    load(clean_df)

    print(f"✅ Done — {len(clean_df):,} transactions loaded.")
