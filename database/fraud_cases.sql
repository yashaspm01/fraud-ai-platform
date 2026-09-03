CREATE TYPE case_status AS ENUM ('OPEN', 'INVESTIGATING', 'ESCALATED', 'CLOSED');

CREATE TABLE fraud_cases (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id    UUID NOT NULL REFERENCES transactions(id),
    status            case_status NOT NULL DEFAULT 'OPEN',
    assigned_to        TEXT,
    notes             TEXT,
    created_on        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_on        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_fraud_cases_transaction ON fraud_cases (transaction_id);

