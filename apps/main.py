import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from services.risk_service import score_transaction
from rag.generate_answer import generate_answer
from agents.approval import approve_case_closure
from pipelines.feature_engineering import build_inference_features
from services.risk_service import get_feature_importance,model_version


app = FastAPI(title="Fraud Risk Scoring Service")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("fraud_ops")

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
    query: str
    top_k: int = 5


class AskRequest(BaseModel):
    question: str


class ApprovalRequest(BaseModel):
    approved: bool

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(5, ge=1, le=20)

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)

@app.get("/v1/health")
def health():
    return {"status": "ok"}


@app.post("/v1/risk")
def get_risk_score(request: RiskRequest):
    try:
        features = build_inference_features(request.model_dump())
        result = score_transaction(features)
        logger.info(f"risk_scored amount={request.amount} label={result['label']} score={result['risk_score']}")
        return result
    except Exception as e:
        logger.error(f"risk_scoring_failed error={e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/search")
def search_documents(request: SearchRequest):
    from rag.search import semantic_search
    results = semantic_search(request.query, top_k=request.top_k)
    logger.info(f"risk_scored amount={request.amount} label={result['label']} score={result['risk_score']}")
    return {
        "results": [
            {"source": r.source_document, "chunk_index": r.chunk_index, "content": r.content}
            for r in results
        ]
    }


@app.post("/v1/ask")
def ask_question(request: AskRequest):
    answer, sources = generate_answer(request.question)
    return {
        "answer": answer,
        "sources": [
            {"source": s.source_document, "chunk_index": s.chunk_index}
            for s in sources
        ],
    }


@app.post("/v1/approvals/{case_id}")
def approve_case(case_id: str, request: ApprovalRequest):
    result = approve_case_closure(case_id, request.approved)
    return result

@app.get("/v1/risk/explain")
def explain_model():
    return {"model_version": model_version, "feature_importances": get_feature_importance()}
