# agents/approval.py
from database.connection import SessionLocal
from database.models import FraudCase, Transaction
import uuid


def request_case_closure(transaction_id: str, recommendation: str) -> dict:
    """
    Called by the agent. Does NOT close the case — only creates a
    PENDING record describing what the agent wants to do and why.
    Nothing in the database actually changes state here.
    """
    db = SessionLocal()
    try:
        tx_exists = db.query(Transaction).filter(Transaction.id == uuid.UUID(transaction_id)).first()
        if not tx_exists:
            return {"error": f"Transaction {transaction_id} does not exist. Cannot recommend closure."}

        case = FraudCase(
            transaction_id=uuid.UUID(transaction_id),
            status="OPEN",  # stays OPEN — NOT closed yet
            notes=f"AGENT RECOMMENDATION (pending approval): {recommendation}",
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        return {
            "case_id": str(case.id),
            "status": "PENDING_APPROVAL",
            "recommendation": recommendation,
        }
    finally:
        db.close()

def approve_case_closure(case_id: str, approved: bool) -> dict:
    """
    This is the ONLY function that can actually change a case's status.
    Called by a human, via the API — never by the agent itself.
    """
    db = SessionLocal()
    try:
        case = db.query(FraudCase).filter(FraudCase.id == uuid.UUID(case_id)).first()
        if not case:
            return {"error": "Case not found"}

        if approved:
            case.status = "CLOSED"
            case.notes += " | APPROVED by human reviewer."
        else:
            case.status = "INVESTIGATING"
            case.notes += " | REJECTED by human reviewer — remains open."

        db.commit()
        return {"case_id": case_id, "new_status": case.status}
    finally:
        db.close()
