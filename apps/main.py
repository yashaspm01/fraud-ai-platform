import logging
import os
from fastapi import FastAPI, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from database.connection import SessionLocal
from database.models import FraudCase

from services.risk_service import score_transaction, get_feature_importance, model_version
from rag.generate_answer import generate_answer
from rag.search import semantic_search
from agents.approval import approve_case_closure
from pipelines.feature_engineering import build_inference_features

app = FastAPI(title="Fraud Risk Scoring Service")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("fraud_ops")

API_KEY = os.getenv("API_KEY")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for local demo; would be locked to a real domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)


class RiskRequest(BaseModel):
    amount: float = Field(..., gt=0)
    sender_balance_before: float
    sender_balance_after: float
    receiver_balance_before: float
    receiver_balance_after: float
    hour_of_day: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)
    transaction_type: str


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(5, ge=1, le=20)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class ApprovalRequest(BaseModel):
    approved: bool


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/v1/health")
def health():
    return {"status": "ok"}


@app.post("/v1/risk", dependencies=[Depends(verify_api_key)])
@limiter.limit("10/minute")
def get_risk_score(request: Request, request_body: RiskRequest):
    try:
        features = build_inference_features(request_body.model_dump())
        result = score_transaction(features)
        logger.info(f"risk_scored amount={request_body.amount} label={result['label']} score={result['risk_score']}")
        return result
    except Exception as e:
        logger.error(f"risk_scoring_failed error={e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/search", dependencies=[Depends(verify_api_key)])
@limiter.limit("10/minute")
def search_documents(request: Request, request_body: SearchRequest):
    try:
        results = semantic_search(request_body.query, top_k=request_body.top_k)
        logger.info(f"search_executed query='{request_body.query}' results={len(results)}")
        return {
            "results": [
                {"source": r.source_document, "chunk_index": r.chunk_index, "content": r.content}
                for r in results
            ]
        }
    except Exception as e:
        logger.error(f"search_failed error={e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/ask", dependencies=[Depends(verify_api_key)])
@limiter.limit("10/minute")
def ask_question(request: Request, request_body: AskRequest):
    try:
        answer, sources = generate_answer(request_body.question)
        logger.info(f"question_answered question='{request_body.question}' sources={len(sources)}")
        return {
            "answer": answer,
            "sources": [{"source": s.source_document, "chunk_index": s.chunk_index} for s in sources],
        }
    except Exception as e:
        logger.error(f"ask_failed error={e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/approvals/{case_id}", dependencies=[Depends(verify_api_key)])
def approve_case(case_id: str, request_body: ApprovalRequest):
    try:
        result = approve_case_closure(case_id, request_body.approved)
        logger.info(f"approval_processed case_id={case_id} approved={request_body.approved} result={result}")
        return result
    except Exception as e:
        logger.error(f"approval_failed case_id={case_id} error={e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/risk/explain", dependencies=[Depends(verify_api_key)])
def explain_model():
    return {"model_version": model_version, "feature_importances": get_feature_importance()}

@app.get("/v1/cases/pending", dependencies=[Depends(verify_api_key)])
def list_pending_cases():
    db = SessionLocal()
    try:
        cases = db.query(FraudCase).filter(FraudCase.status.in_(["OPEN", "INVESTIGATING"])).all()
        return [{"id": str(c.id), "status": c.status, "notes": c.notes} for c in cases]
    finally:
        db.close()
