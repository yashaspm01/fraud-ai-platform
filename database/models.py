from sqlalchemy import Column, String, Numeric, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    transaction_type = Column(
        Enum(
            "CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER",
            name="transaction_type",
            create_type=False,  # enum already exists in Postgres (schema.sql created it)
        ),
        nullable=False,
    )

    amount = Column(Numeric(15, 2), nullable=False)

    sender_account_id = Column(String, nullable=False)
    sender_balance_before = Column(Numeric(15, 2), nullable=False)
    sender_balance_after = Column(Numeric(15, 2), nullable=False)

    receiver_account_id = Column(String, nullable=False)
    receiver_balance_before = Column(Numeric(15, 2), nullable=False)
    receiver_balance_after = Column(Numeric(15, 2), nullable=False)

    transaction_timestamp = Column(DateTime(timezone=True), nullable=False)
    is_fraud = Column(Boolean, nullable=False, default=False)

    created_on = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_on = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class FraudCase(Base):
    __tablename__ = "fraud_cases"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    transaction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transactions.id"),
        nullable=False,
    )

    status = Column(
        Enum(
            "OPEN", "INVESTIGATING", "ESCALATED", "CLOSED",
            name="case_status",
            create_type=False,  # already exists in Postgres (fraud_cases.sql created it)
        ),
        nullable=False,
        server_default="OPEN",
    )

    assigned_to = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    created_on = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_on = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
