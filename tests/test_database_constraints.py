import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from database.connection import SessionLocal
from database.models import Transaction

def test_negative_amount_rejected():
    db = SessionLocal()
    try:
        bad_tx = Transaction(
            transaction_type="TRANSFER", amount=-100,
            sender_account_id="TEST_A", sender_balance_before=100, sender_balance_after=200,
            receiver_account_id="TEST_B", receiver_balance_before=0, receiver_balance_after=100,
            transaction_timestamp=datetime.now(timezone.utc),
        )
        db.add(bad_tx)
        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        db.rollback()
        db.close()
