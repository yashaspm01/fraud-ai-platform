# Fraud & Risk Operations Platform

A 4-week AI Engineer build: one evolving system spanning ML risk scoring,
RAG-grounded compliance knowledge, an agentic investigation workflow with a
human approval gate, and production hardening — not four separate demos.

## Architecture
See `docs/PRD.md` for full architecture, requirements, and the week-by-week
decision log in `NOTES.md` — every real bug, incident, and design trade-off
this project hit is documented there as it happened.

## Stack
Python, FastAPI, PostgreSQL + pgvector, scikit-learn, Ollama (local LLM +
embeddings), Docker.

## Running locally
1. `cp .env.example .env` and fill in real values
2. `docker compose up -d --build`
3. Load data: `python3 -m pipelines.ingest_paysim` and `python3 -m rag.ingest_documents`
4. Train the model: `python3 -m models.train_risk_model`
5. API available at `http://127.0.0.1:8000` — all endpoints except `/v1/health`
   require an `X-API-Key` header.

## Endpoints
- `POST /v1/risk` — fraud risk scoring
- `GET /v1/risk/explain` — model feature importances
- `POST /v1/search`, `POST /v1/ask` — RAG retrieval + grounded Q&A
- `POST /v1/approvals/{case_id}` — human approval gate for agent recommendations

## Security
API key auth on all protected endpoints, per-IP rate limiting (10/min),
prompt injection isolation on retrieved content, a relevance gate that
refuses off-topic questions before invoking the LLM.

## Testing
`pytest tests/ -v` — 9 tests covering feature engineering, model sanity, RAG
regression guards, agent tool contracts, and DB constraints.

## Known limitations (documented honestly, not hidden)
- llama3.2 (3B, local) shows inconsistent grounding behavior on
  scattered-vs-undefined-term questions — see NOTES.md, Week 2 Day 4.
- No CI/CD pipeline or cloud deployment — designed in docs/PRD.md, not
  implemented, given the project timeline.
- Single shared API key, not full RBAC — appropriate for this project's
  single-operator scope.
- Relevance gate threshold calibrated against limited real examples, not a
  full labeled evaluation dataset.
