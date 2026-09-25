# Fraud & Risk Operations Platform

![CI](https://github.com/yashaspm01/fraud-ai-platform/actions/workflows/ci.yml/badge.svg)

A 4-week AI Engineer build: one evolving system spanning ML risk scoring,
RAG-grounded compliance knowledge, an agentic investigation workflow with a
human approval gate, and production hardening — not four separate demos.

## Live Demo
- Frontend: https://fraud-ai-platform-1.onrender.com
- API: https://fraud-ai-platform.onrender.com
- Note: free-tier hosting — the API sleeps after inactivity, so the first
  request after a while may take up to ~50s to wake up.
- Note: RAG/agent features require a local LLM (Ollama) and are not
  available on the deployed instance — the deployed API fully demonstrates
  real-time ML risk scoring and explainability; RAG/agent features are
  demoed by running the platform locally via Docker (see below).

## CI/CD
GitHub Actions runs the self-contained test suite (feature engineering,
agent tool contracts) on every push to main. Database/model/RAG-dependent
tests require live local services and run as part of the full local suite.

## Architecture
See `docs/PRD.md` for full architecture, requirements, and the week-by-week
decision log in `NOTES.md` — every real bug, incident, and design trade-off
this project hit is documented there as it happened, not cleaned up after
the fact.

## Stack
Python, FastAPI, PostgreSQL + pgvector, scikit-learn, Ollama (local LLM +
embeddings), Docker, GitHub Actions, Render.

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
- `GET /v1/cases/pending` — pending agent recommendations awaiting review

## Security
API key auth on all protected endpoints, per-IP rate limiting, prompt
injection isolation on retrieved content, a relevance gate that refuses
off-topic questions before invoking the LLM.

## Testing
`pytest tests/ -v` — 9 tests covering feature engineering, model sanity, RAG
regression guards, agent tool contracts, and database constraints.

## Known limitations (documented honestly, not hidden)
- llama3.2 (3B, local) shows inconsistent grounding behavior on
  scattered-vs-undefined-term questions; query rewriting was evaluated and
  deliberately disabled after causing real retrieval instability — see NOTES.md.
- Deployed API omits RAG/agent features (require a local LLM not available
  on the free hosting tier) — documented trade-off, not an oversight.
- Single shared API key, not full RBAC — appropriate for this project's
  single-operator scope.
