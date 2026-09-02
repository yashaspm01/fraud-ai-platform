-- Enable UUID generation (not on by default)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Fixed, known set of transaction types (PaySim's categories) — ENUM chosen
-- over TEXT to reject typos/inconsistent values at write time.
CREATE TYPE transaction_type AS ENUM (
    'CASH_IN',
    'CASH_OUT',
    'DEBIT',
    'PAYMENT',
    'TRANSFER'
);

CREATE TABLE transactions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    transaction_type        transaction_type NOT NULL,
    amount                  NUMERIC(15, 2) NOT NULL CHECK (amount >= 0),

    sender_account_id       TEXT NOT NULL,
    sender_balance_before   NUMERIC(15, 2) NOT NULL,
    sender_balance_after    NUMERIC(15, 2) NOT NULL,

    receiver_account_id     TEXT NOT NULL,
    receiver_balance_before NUMERIC(15, 2) NOT NULL,
    receiver_balance_after  NUMERIC(15, 2) NOT NULL,

    transaction_timestamp   TIMESTAMPTZ NOT NULL,
    is_fraud                BOOLEAN NOT NULL DEFAULT FALSE,

    created_on              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_on              TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index on sender_account_id: analysts and the future agent will constantly
-- ask "show me this account's transaction history" — that's a WHERE clause
-- on this column, run often, so it earns an index. We are NOT indexing
-- transaction_type or is_fraud yet — low-cardinality columns (only 5 values,
-- only 2 values) benefit far less from a plain B-tree index than a
-- high-cardinality one like an account ID.
CREATE INDEX idx_transactions_sender_account ON transactions (sender_account_id);
