from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from services.risk_service import score_transaction
from rag.generate_answer import generate_answer

app = FastAPI(title="Fraud Risk Scoring Service")


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


@app.get("/v1/health")
def health():
    return {"status": "ok"}


@app.post("/v1/risk")
def get_risk_score(request: RiskRequest):
    try:
        features = request.model_dump()
        tx_type = features.pop("transaction_type")

        features["sender_balance_delta"] = (
            features["sender_balance_before"] - features["sender_balance_after"]
        )
        features["sender_emptied_account"] = int(features["sender_balance_after"] == 0)
        features["is_night"] = int(features["hour_of_day"] < 6 or features["hour_of_day"] >= 22)
        features[f"type_{tx_type}"] = 1

        return score_transaction(features)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/search")
def search_documents(request: SearchRequest):
    from rag.search import semantic_search
    results = semantic_search(request.query, top_k=request.top_k)
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
