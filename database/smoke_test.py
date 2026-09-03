from database.connection import engine, SessionLocal
from database.models import Transaction, FraudCase

# 1. Can we even reach the database?
try:
    with engine.connect() as conn:
        print("✅ Connected to database successfully.")
except Exception as e:
    print("❌ Connection failed:", e)
    raise SystemExit(1)

# 2. Do the models correctly map to the real tables? (a read-only query)
db = SessionLocal()
try:
    tx_count = db.query(Transaction).count()
    case_count = db.query(FraudCase).count()
    print(f"✅ Transaction model OK — current row count: {tx_count}")
    print(f"✅ FraudCase model OK — current row count: {case_count}")
except Exception as e:
    print("❌ Query failed — model likely doesn't match the real table:", e)
    raise
finally:
    db.close()
