# FRAUD OPERATIONS PLATFORM
## Master PRD + 4-Week AI Engineer Build Program

*Source material: the previously-approved 4-project progression (Fraud & Risk Scoring Service → Compliance & Case Knowledge Assistant → Fraud Investigation Agent → Production Fraud Operations Platform). Where a detail below extends beyond what we explicitly agreed, it's engineering judgment applied to make the plan buildable — not something invented and attributed to a source.*

---

# A. FINAL 4-WEEK PROJECT PROGRESSION

```
FRAUD OPERATIONS PLATFORM
│
↓
┌─────────────┐
│   WEEK 1    │  Data → ML → API → Database
│ FOUNDATION  │
└──────┬──────┘
       ↓
┌─────────────┐
│   WEEK 2    │  + Documents → Embeddings → Vector Search → RAG
│  KNOWLEDGE  │
└──────┬──────┘
       ↓
┌─────────────┐
│   WEEK 3    │  + Tool Calling → Agent Loop → Memory → Human Approval
│   ACTION    │
└──────┬──────┘
       ↓
┌─────────────┐
│   WEEK 4    │  + Security → Observability → Reliability → Deploy
│    TRUST    │
└──────┬──────┘
       ↓
PRODUCTION AI SYSTEM
```

One system, four milestones. Nothing is rebuilt — each week extends what exists.

---

# B. EXECUTIVE SUMMARY

**What we're building:** A Fraud Operations Platform for a fintech company — a system that scores transaction risk, answers analyst questions grounded in compliance/case knowledge, autonomously investigates flagged cases using tools (with mandatory human approval), and runs as an observable, secured, deployed production service.

**Why it exists:** Fraud/risk teams spend disproportionate time on manual work — running scores, searching policy docs, gathering case context — before a human ever makes the actual judgment call. The platform automates the *gathering*, not the *decision*.

**Who uses it:** Fraud analysts, risk analysts, compliance analysts, and investigators at a mid-size fintech; secondarily, engineers/admins maintaining the platform.

**What problem it solves:** Slow, manual, inconsistent triage of suspicious transactions, and knowledge scattered across policy documents and case history that analysts must search by hand.

**Why the system evolves across four weeks:** Each capability depends on the one before it — you cannot ground an assistant in knowledge it can't retrieve, cannot safely let an agent act without something to act on, and shouldn't harden a system that doesn't exist yet. The four weeks mirror how a real team would actually sequence this build.

---

# C. PRODUCT VISION

Long-term, this platform becomes the system of record for how the fraud/risk team triages and investigates cases: every flagged transaction gets an automatic risk score, every analyst question about policy or case history gets a grounded answer with citations, every investigation gets an AI-assembled first draft that a human reviews and approves, and every action taken by the system is logged, evaluated, and auditable. The platform should eventually reduce average investigation time significantly while *increasing* — not decreasing — analyst confidence in decisions, because every AI output is traceable back to its source data or reasoning.

---

# D. PROBLEM STATEMENT

- **Fraud detection:** Suspicious transactions must be identified quickly, before settlement, without drowning analysts in false positives.
- **Risk scoring:** Not every flagged transaction deserves equal urgency; scores must be ranked and explainable.
- **Compliance knowledge retrieval:** Policies live in scattered documents; analysts currently search manually.
- **Investigation:** Building a case file (score + policy + history) is repetitive, manual work.
- **Analyst productivity:** Time-to-decision per case is the core business metric this platform should improve.
- **Decision support, not decision replacement:** The system must *assist* judgment, never silently replace it on high-impact actions.

---

# E. TARGET USERS

**Fraud Analyst**
- Goals: quickly triage a queue of flagged transactions.
- Pain points: manually re-deriving context (score, similar past cases) for every case.
- Needs: a risk score, a case summary, relevant policy — in one place.

**Risk Analyst**
- Goals: understand aggregate risk trends, not just single cases.
- Pain points: no easy way to query "why is this scored the way it is."
- Needs: explainable scores, access to model reasoning/features.

**Compliance Analyst**
- Goals: ensure decisions follow policy correctly.
- Pain points: policy documents are long, versioned, hard to search precisely.
- Needs: grounded, citation-backed answers to policy questions.

**Investigator**
- Goals: build a complete, defensible case file efficiently.
- Pain points: assembling score + knowledge + case history manually.
- Needs: an assistant that gathers evidence but never finalizes a decision alone.

**Engineering/Admin user**
- Goals: keep the system reliable, secure, cost-effective.
- Pain points: no visibility into AI failures, cost, or latency without tooling.
- Needs: observability, audit logs, evaluation dashboards.

---

# F. USER STORIES (representative, not exhaustive)

> As a fraud analyst, I want to submit a transaction and receive a risk score, so I can prioritize suspicious transactions.
Acceptance criteria: score returned within Development Target latency; score includes a confidence/probability value; request and result are logged.

> As a compliance analyst, I want to ask a natural-language question about policy and get a grounded, cited answer, so I don't have to search documents manually.
Acceptance criteria: answer includes at least one document citation; answer is refused (not hallucinated) if no relevant document is retrieved.

> As an investigator, I want an agent to gather a case's score, relevant policy, and history into a draft summary, so I can review instead of assembling it myself.
Acceptance criteria: draft is generated only from tool outputs (no unsupported claims); the case cannot be closed without explicit human approval.

> As an engineering/admin user, I want to see logs and traces of every AI/tool call, so I can debug failures and monitor cost.
Acceptance criteria: every model call, tool call, and retrieval is traced with latency, token/cost, and outcome.

> As a fraud analyst, I want the agent to never take an irreversible action without my approval, so I retain control over case outcomes.
Acceptance criteria: any state-changing action (closing a case, flagging a customer) requires an explicit approval step.

---

# G. PRODUCT SCOPE

### MVP (by end of Week 4)
Risk-scoring API on real transaction data; PostgreSQL-backed case/transaction store; RAG assistant over policy documents + case data (pgvector); a tool-using investigation agent with a human-approval gate; Dockerized deployment; basic CI/CD; basic observability (logs, traces, cost/latency); a golden-dataset evaluation suite for ML, RAG, and agent layers; core security (auth, input validation, prompt-injection isolation, tool permissions).

### Post-4-Week
Multi-tenant support, advanced agent frameworks (LangGraph in full), fine-tuning, model routing across multiple LLMs, advanced caching strategies, A/B testing infrastructure, feature-flagged rollouts, a proper frontend, drift monitoring, alerting/paging.

### Enterprise (what a real company would eventually need)
Kubernetes-based scaling, multi-region deployment, full RBAC with SSO, event-driven architecture with queues, a feature store, dedicated MLOps pipelines with automated retraining, SOC2/compliance-grade audit infrastructure, dedicated model-serving infrastructure, disaster recovery, 24/7 on-call.

---

# H. FUNCTIONAL REQUIREMENTS

- **Data ingestion:** accept transaction records (batch or single); accept documents (policy PDFs/text) for indexing.
- **Data validation:** reject malformed transaction records and documents at the API boundary (Pydantic schemas).
- **Data processing:** clean, normalize transaction fields; parse and clean document text.
- **Feature engineering:** derive model features from raw transaction fields (amounts, velocity, categorical encodings).
- **Fraud prediction / risk scoring:** return a probability/score + label for a given transaction.
- **Document ingestion:** parse, chunk, and embed policy/case documents.
- **Embeddings:** generate and store vector representations for all indexed chunks.
- **Retrieval:** return top-K relevant chunks for a query.
- **Reranking:** reorder retrieved chunks by relevance before passing to the LLM.
- **RAG responses:** generate grounded answers with citations; refuse when ungrounded.
- **Tool calling:** expose the risk model, RAG system, and case database as callable tools with strict schemas.
- **Agent investigation:** given a case ID, gather score + knowledge + history and produce a draft summary.
- **Human approval:** block any state-changing action until explicitly approved by a user.
- **Audit trail:** log every prediction, retrieval, tool call, and approval decision with timestamps and actor.
- **Authentication:** verify user identity on every request.
- **Authorization:** restrict actions by role (analyst vs. admin).
- **Monitoring:** expose logs, metrics, and traces for all AI and system operations.
- **Evaluation:** run golden-dataset evaluation for ML, RAG, and agent components on demand and in CI.
- **Deployment:** containerized, deployable via a documented pipeline to a single cloud target.

---

# I. NON-FUNCTIONAL REQUIREMENTS

*Development Target = what you'll hit as a solo builder in 4 weeks. Production Target = what a real company would eventually require. These are intentionally different — do not chase Production Targets during the program.*

| Dimension | Development Target | Production Target |
|---|---|---|
| Performance (risk scoring) | < 1s p95 | < 200ms p95 |
| Performance (RAG answer) | < 5s p95 | < 2s p95 |
| Performance (agent investigation) | < 30s p95 | < 10s p95 |
| Reliability | best-effort, manual restart OK | automated failover, 99.9% uptime |
| Availability | single instance, business-hours use | multi-instance, 24/7 |
| Security | auth + input validation + tool permissions | full RBAC, SSO, pen-tested |
| Scalability | single user / low concurrency | horizontal scaling, load-tested |
| Maintainability | tested, documented, typed | full CI/CD gates, code owners |
| Observability | logs + basic traces | full APM, alerting, on-call |
| Cost | tracked manually per request | automated budget alerts, cost dashboards |
| Data integrity | DB constraints + transactions | plus backups, point-in-time recovery |
| Explainability | feature importances on request | built-in explanation UI for every score |

---

# J. SYSTEM ARCHITECTURE (target end-state, Week 4)

```
User
 ↓
Frontend / API Client
 ↓
Authentication
 ↓
API Layer (FastAPI)
 ↓
AI Orchestration
 ├── Risk Service      (Project 1's model, wrapped as a tool)
 ├── RAG Service        (Project 2's retrieval + generation pipeline)
 ├── Agent              (Project 3's investigation loop)
 └── Data Services      (transaction/case CRUD)
 ↓
PostgreSQL
 ├── Transaction Data
 ├── Case Data
 ├── Audit Data
 └── pgvector (embeddings)
 ↓
Observability (logs, metrics, traces)
```

**Component explanations:**
- **API Layer:** the single entry point; owns auth, validation, routing. Never bypassed.
- **Risk Service:** wraps the trained model behind a stable interface; the agent and API both call this same service (no duplicated logic).
- **RAG Service:** owns chunking, retrieval, reranking, and grounded generation; used directly by analysts and as a tool by the agent.
- **Agent:** orchestrates Risk Service + RAG Service + Data Services to produce investigation drafts; never writes to the database directly without passing through the approval gate.
- **PostgreSQL + pgvector:** single database for structured data *and* vectors — deliberately avoids standing up separate infrastructure.
- **Observability:** cross-cutting; every layer emits logs/traces into it.

---

# K. ARCHITECTURE EVOLUTION

**Week 1 architecture**
```
Client → FastAPI → ML Model
                 → PostgreSQL (transactions, cases)
```

**Week 2 architecture** — adds retrieval; reuses DB + API
```
Client → FastAPI → ML Model
                 → PostgreSQL (+ pgvector)
                 → RAG Pipeline → Vector Store → LLM
```

**Week 3 architecture** — adds the agent; reuses everything as tools
```
Client → FastAPI → Agent
                     ├── Tool: ML Model (reused)
                     ├── Tool: RAG Pipeline (reused)
                     ├── Tool: PostgreSQL lookup (reused)
                     └── Human Approval Gate (new)
```

**Week 4 architecture** — adds trust; wraps everything
```
Client → Auth/Gateway → FastAPI → Agent Orchestrator (cached, retried, traced)
                                    ├── Risk Service
                                    ├── RAG Service (guarded vs. prompt injection)
                                    └── Human Approval Gate
                                  → PostgreSQL (+ pgvector)
                                  → Observability (logs/metrics/traces)
                                  → CI/CD → Docker → Cloud
```

---

# L. DATA ARCHITECTURE

- **Transaction data** → risk model input; source of truth for scoring.
- **Customer data** → linked to transactions; used for context, never used to make the model or agent overconfident about identity-based judgments.
- **Case data** → created when a transaction is flagged; the central object investigations revolve around.
- **Document data** → raw policy/compliance text, source for RAG.
- **Embeddings** → derived from document chunks (and optionally case notes); stored in pgvector, always traceable back to source document + chunk.
- **Risk scores** → derived from transactions; versioned by model version.
- **Investigation results** → derived from agent runs; always linked to the case and to the tool calls that produced them.
- **Audit logs** → derived from every action across the system; append-only.
- **Evaluation data** → golden datasets + evaluation run results; independent of production data.

Relationships: `transactions → risk_predictions → fraud_cases → investigations → tool_calls / approvals`; `documents → document_chunks → embeddings`, referenced by both RAG queries and investigations.

---

# M. DATABASE DESIGN (major entities — not full schemas yet)

```
users
customers
transactions
risk_predictions
fraud_cases
documents
document_chunks
embeddings
investigations
investigation_steps
tool_calls
approvals
audit_logs
evaluation_runs
```

Full column-level schemas are deferred to each week's implementation phase, per your instruction — this level is sufficient for the master architecture.

---

# N. AI/ML ARCHITECTURE

```
Transaction Data
      ↓
Feature Engineering
      ↓
Model (classification)
      ↓
Prediction (probability)
      ↓
Risk Score + Label
      ↓
Decision (human, assisted by score)
```

- **Training:** offline, on historical/labeled transaction data (e.g. a public fraud dataset).
- **Validation:** held-out split, stratified for class imbalance.
- **Testing:** final held-out evaluation before "release" of a model version.
- **Model evaluation:** precision, recall, F1, ROC-AUC — precision/recall matter more than raw accuracy given fraud's severe class imbalance.
- **Inference:** synchronous, via the Risk Service.
- **Model versioning:** every prediction stores which model version produced it.
- **Drift monitoring:** Development Target = manual periodic check of score distribution; Production Target = automated drift alerts. (Full drift infrastructure is POST-4-WEEK.)

---

# O. RAG ARCHITECTURE

```
Document
   ↓
Parser
   ↓
Chunking
   ↓
Embedding
   ↓
Vector DB (pgvector)
   ↓
Retriever
   ↓
Reranker
   ↓
Context Builder
   ↓
LLM
   ↓
Grounded Answer (with citations)
```

- **Chunking strategy:** fixed-size with overlap to start; revisit if retrieval quality is poor.
- **Metadata:** document source, section, version, date — attached to every chunk for citation and filtering.
- **Retrieval strategy:** vector similarity first; hybrid (keyword + vector) if time allows in Week 2.
- **Top-K:** start conservative (e.g. 5), tune based on evaluation results.
- **Reranking:** cross-encoder or LLM-based rerank of the top-K before generation.
- **Grounding:** the LLM must cite retrieved chunks; if nothing relevant is retrieved, it must refuse rather than answer from parametric knowledge.
- **Citations:** every answer references the source document/chunk.
- **Evaluation:** retrieval metrics (Recall@K, Precision@K) + generation metrics (faithfulness, answer correctness).

---

# P. AGENT ARCHITECTURE

```
User Request (case ID)
      ↓
Agent
      ↓
Reason / Plan
      ↓
Tool Selection
      ↓
Tool Execution
      ↓
Observation
      ↓
Next Action (loop, bounded)
      ↓
Final Result (draft investigation)
      ↓
Human Approval
```

- **Tool contracts:** each tool (risk model, RAG, case lookup) has a name, description, typed parameters, and a validated response shape.
- **State:** case ID, goal, tool call history, current step, retry count — explicit, not implicit in conversation text.
- **Memory:** short-term/task-scoped only for the MVP (no long-term cross-session memory — that's POST-4-WEEK).
- **Permissions:** the agent can *read* transactions, cases, and documents, and can *call* the risk model; it cannot write to `fraud_cases` (close/resolve) without passing through Approval.
- **Human approval:** required before any state-changing action.
- **Guardrails:** treat all document/case content as untrusted data, never as instructions; validate tool outputs before use.
- **Failure handling:** bounded retries per tool call; on repeated failure, surface a partial result rather than looping indefinitely.
- **Agent evaluation:** task completion rate, tool selection accuracy, invalid tool call rate, steps-to-completion, human intervention rate.

---

# Q. API ARCHITECTURE (boundaries only)

```
/v1/transactions
/v1/risk
/v1/documents
/v1/search
/v1/cases
/v1/investigations
/v1/agent
/v1/approvals
/v1/evaluation
/v1/health
```

Detailed contracts (request/response schemas) are designed just before each is implemented, not now.

---

# R. SECURITY ARCHITECTURE

- **Authentication:** required on every endpoint except `/health`.
- **Authorization / RBAC:** at minimum, `analyst` (read + request investigations) vs. `admin` (manage users, view all audit logs) roles.
- **Secrets:** environment variables locally; a secrets manager in cloud deployment (never committed to Git).
- **Input validation:** Pydantic schemas at every API boundary.
- **SQL injection protection:** parameterized queries via SQLAlchemy; no raw string interpolation.
- **Prompt injection protection:** retrieved document/case content is passed to the LLM as clearly delimited *data*, never as instructions; the agent's system instructions take precedence and are never overridable by tool output content.
- **Tool permissions:** enforced in application code (the model is never the final authority on what it's allowed to do — per the source PDF's own principle).
- **Data isolation:** not multi-tenant in the MVP, but the schema is designed so a `tenant_id` column could be added without a rewrite (POST-4-WEEK for actual multi-tenancy).
- **Audit logging:** every prediction, retrieval, tool call, and approval is logged with actor, timestamp, and outcome.
- **Human approval:** the primary security control on agent actions.
- **Sensitive information handling:** no card numbers, SSNs, or similar are stored beyond what's needed for scoring; logs are checked for accidental sensitive-data leakage.

**Evolution:** Week 1 = basic auth + input validation. Week 2 = + prompt injection isolation. Week 3 = + tool permissions + human approval. Week 4 = + full audit logging + RBAC hardening + secrets management.

---

# S. OBSERVABILITY ARCHITECTURE

- **Logs:** structured (JSON) logs for every request, prediction, retrieval, tool call, and approval decision.
- **Metrics:** request rate, error rate, latency percentiles per endpoint; model score distribution; RAG retrieval hit rate; agent task completion rate.
- **Traces:** end-to-end trace per request, spanning API → tool calls → model calls → DB queries.
- **AI telemetry:** model calls (which model, tokens in/out, latency, cost), tool calls (which tool, args, duration, success/failure), retrieval results (chunks returned, scores), agent failures (which step, why), evaluation scores (per run).

---

# T. RELIABILITY ARCHITECTURE

- **Retries:** exponential backoff on transient LLM/API/network errors only — not on validation errors.
- **Timeouts:** every external call (LLM, DB, tool) has an explicit timeout.
- **Idempotency:** state-changing operations (e.g. approving a case) use an operation ID to prevent duplicate execution on retry.
- **Circuit breakers:** POST-4-WEEK for full implementation; Week 4 MVP uses simple max-retry + fail-fast instead.
- **Graceful degradation:** if the RAG/LLM layer fails, the risk-scoring API must still function independently.
- **Database transactions:** case creation + audit log write happen atomically.
- **Failure recovery:** failed agent runs are logged with enough state to resume or retry manually.
- **LLM failure handling:** on provider error/timeout, return a clear error rather than a silent wrong answer; no automatic fallback model in the MVP (POST-4-WEEK).
- **Tool failure handling:** a failed tool call is surfaced to the agent as an observation, not a silent crash — the agent must be able to reason about failure.

---

# U. EVALUATION STRATEGY

**ML:** Precision, Recall, F1, ROC-AUC — tracked per model version.

**RAG:** Recall@K, Precision@K, context relevance, faithfulness, answer correctness — against a golden Q&A dataset built from real policy documents.

**Agents:** tool selection accuracy, task completion rate, invalid tool call rate, failure rate, human intervention rate — against a golden set of investigation scenarios (easy/normal/adversarial).

**Production:** latency (p50/p95), cost per request, error rate, throughput — tracked continuously, not just at build time.

---

# V. TESTING STRATEGY

- **Unit tests:** individual functions (feature engineering, chunking logic, schema validation).
- **Integration tests:** API endpoint → service → DB round-trips.
- **API tests:** contract tests against the OpenAPI spec.
- **ML tests:** model loads correctly, predicts within expected value ranges, doesn't crash on edge-case inputs.
- **RAG tests:** retrieval returns expected documents for known queries; citations are present.
- **Agent tests:** given a scripted scenario, the agent calls the expected tools in a reasonable order and respects the approval gate.
- **Security tests:** injection attempts (SQL + prompt) are rejected/isolated as expected.
- **End-to-end tests:** a full "submit transaction → get score → ask a policy question → run an investigation → approve" flow.
- **Load tests:** basic — confirm the API doesn't fall over under light concurrent load (full load testing is POST-4-WEEK).
- **Regression tests:** golden datasets re-run on every significant change to catch quality regressions.

---

# W. TECHNOLOGY STACK

| Technology | Purpose | Why selected | Alternative | Introduced | Mandatory? |
|---|---|---|---|---|---|
| Python | Primary language | Ecosystem fit for ML + AI + backend | — | Wk1 | Mandatory |
| FastAPI | API framework | Fast, typed, async, great docs generation | Flask/Django | Wk1 | Mandatory |
| PostgreSQL | Primary database | Relational + supports pgvector, one DB for everything | MySQL | Wk1 | Mandatory |
| pgvector | Vector search | Avoids standing up a separate vector DB | Chroma/Qdrant/Pinecone | Wk2 | Mandatory |
| Pandas/NumPy | Data processing | Standard, required for feature engineering | — | Wk1 | Mandatory |
| scikit-learn | Classical ML | Fast to train/evaluate a fraud classifier | XGBoost/LightGBM | Wk1 | Mandatory |
| Pydantic | Validation/schemas | Enforces data contracts at every boundary | — | Wk1 | Mandatory |
| SQLAlchemy | ORM | Prevents raw SQL injection risk, testable | Raw SQL + psycopg | Wk1 | Mandatory |
| pytest | Testing | Standard Python testing framework | — | Wk1 | Mandatory |
| An LLM API | Generation + tool calling | Needed for RAG and agent layers | Open-source local model | Wk2 | Mandatory |
| Docker | Containerization | Standard deployment unit | — | Wk4 | Mandatory |
| GitHub Actions | CI/CD | Free, integrates directly with GitHub | GitLab CI/Jenkins | Wk4 | Mandatory |
| A cloud host (single provider, e.g. Render/Railway/AWS) | Deployment | Needed to prove real deployment | — | Wk4 | Mandatory |
| A basic tracing tool (e.g. Langfuse/OpenTelemetry) | Observability | Needed to see model/tool call traces | Custom logging only | Wk4 | Optional (custom logging is an acceptable minimum) |

---

# X. FRAMEWORK STRATEGY

- **LangChain:** not introduced by default. If Week 2 is going slowly, LangChain's retriever abstractions may be adopted *after* you've built raw retrieval by hand once — never before.
- **LangGraph:** not mandatory for Week 3. Build the agent loop directly first (per the explicit instruction not to introduce a framework before the underlying loop is understood). LangGraph may be adopted afterward, only if you want to formalize the loop as a state graph, and only after the hand-rolled version works.
- **LlamaIndex:** not planned — its RAG abstractions overlap heavily with what you'll build directly in Week 2; introducing it would replace learning with framework-following.
- **Other frameworks (CrewAI, AutoGen):** POST-4-WEEK. Single-agent, hand-rolled tool calling is sufficient for this system's actual requirements; multi-framework comparison is explicitly out of scope per the earlier "what not to learn" decision.

---

# Y. REPOSITORY ARCHITECTURE

```
fraud-ai-platform/
│
├── apps/                # FastAPI app entrypoint(s)
├── services/            # risk service, RAG service, agent service (business logic)
├── pipelines/           # data ingestion, feature engineering, document processing
├── models/              # trained ML model artifacts + training scripts
├── agents/              # agent loop, tool definitions, state management
├── rag/                 # chunking, embedding, retrieval, reranking
├── database/            # SQLAlchemy models, migrations
├── tests/                # unit, integration, API, ML, RAG, agent, security, e2e
├── evaluation/           # golden datasets, evaluation scripts, run results
├── infrastructure/       # Dockerfiles, docker-compose, CI/CD configs
├── docs/                 # PRD, architecture docs, ADRs
├── scripts/              # one-off/dev utility scripts
└── configs/               # environment/config files
```

One repo, structured by *capability* (services/pipelines/agents/rag) rather than by week — because the system is one product, not four separate deliverables. Kept flat and shallow deliberately; no premature `libs/`, `packages/`, or monorepo tooling (Nx, Turborepo) — that's over-engineering for a solo 4-week build.

---

# Z. DEVELOPMENT ENVIRONMENT

- **Python version:** 3.11+ (stable, broad library support).
- **Package management:** `venv` + `pip` with a `requirements.txt` (or `pyproject.toml` if you prefer `uv`/`poetry` — either is fine, pick one and stay consistent).
- **Environment variables:** `.env` file locally (never committed), loaded via `pydantic-settings` or `python-dotenv`.
- **Local database:** PostgreSQL via Docker Compose (with the pgvector extension enabled) so local matches deployment.
- **Docker:** used for local Postgres from Week 1 onward, even before the app itself is containerized in Week 4.
- **Development commands:** a `Makefile` or simple shell scripts for `run`, `test`, `lint`, `migrate`.
- **Testing commands:** `pytest` with coverage reporting.
- **Linting/formatting:** `ruff` (fast, covers both) or `black` + `flake8`.
- **Type checking:** `mypy`, run at least on `services/`, `agents/`, `rag/`.

---

# AA. GIT STRATEGY

- **Branching:** trunk-based with short-lived feature branches (`feature/risk-scoring-api`, `feature/rag-pipeline`), merged via PR.
- **Commit conventions:** Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`) — makes the eventual CI/CD and changelog trivial.
- **Pull requests:** even solo, open a PR per feature and self-review against the Senior Engineer Review checklist (Part Z below) before merging — this is a habit, not bureaucracy.
- **Release tags:** tag `v0.1.0` at the end of Week 1, `v0.2.0` end of Week 2, `v0.3.0` end of Week 3, `v1.0.0` at the end of Week 4 (production release).
- **Versioning:** Semantic Versioning for the platform; model versions tracked separately (`risk-model-v1`, `v2`, ...).

---

# BB. CI/CD

```
Git Push
   ↓
Lint
   ↓
Type Check
   ↓
Unit Tests
   ↓
Integration Tests
   ↓
Build Docker Image
   ↓
Security Checks (dependency scan, basic secret scan)
   ↓
Deploy (staging or prod, per branch)
   ↓
Smoke Test
```

This pipeline is *designed* now, in the PRD; it's *implemented* in Week 4, once there's a full application to run it against.

---

# CC. CLOUD ARCHITECTURE

**Single provider recommendation: pick one of Render, Railway, or AWS** (any is fine — Render/Railway are simpler for a solo 4-week build; AWS is more "enterprise-realistic" but costs more setup time). Do not learn AWS + Azure + GCP simultaneously — that dilutes the four weeks for no benefit.

- **Compute:** a single managed container service (e.g. Render Web Service / AWS ECS Fargate).
- **Database:** managed PostgreSQL with pgvector support.
- **Storage:** object storage only if needed for raw document files (e.g. S3-compatible); otherwise documents live as text in Postgres.
- **Secrets:** the provider's built-in secrets/environment variable manager.
- **Networking:** HTTPS-only, provider-managed TLS.
- **Logging:** provider's built-in log aggregation to start; a dedicated tool only if time allows.
- **Deployment:** triggered by CI/CD on merge to `main`.

**Local vs. Development vs. Production:**
- **Local:** Docker Compose (Postgres + app), `.env.local`.
- **Development:** a deployed staging instance, seeded with synthetic data.
- **Production:** the "real" deployed instance — for this program, this can be the same as staging with a different flag, since there's no real user base yet; the *practice* of separating them is what matters.

---

# DD. COST ARCHITECTURE

**Major cost sources:** LLM inference calls (generation + tool calling), embedding generation, database hosting, compute (API + agent execution), storage, network egress.

**Cost reduction strategies:** cache repeated embeddings and frequent RAG queries; keep context windows small (retrieve only what's needed, don't over-stuff prompts); use a smaller/cheaper model for simple classification-style calls and reserve a stronger model for the agent's reasoning steps (full model routing is POST-4-WEEK, but the *principle* — don't use your biggest model for everything — applies from Week 2 onward); set hard token/step budgets on the agent to prevent runaway cost from loops.

---

# EE. PERFORMANCE ARCHITECTURE

- **Latency budget:** see Non-Functional Requirements table (Section I) for per-component Development Targets.
- **Database optimization:** index `transaction_id`, `case_id`, foreign keys; index the vector column appropriately for pgvector similarity search.
- **Caching:** cache embedding results for identical/frequent queries; consider a simple in-process cache before reaching for Redis (Redis is a reasonable Week 4 addition if time allows, not mandatory).
- **Model inference:** the risk model should be lightweight enough for synchronous, sub-second inference — this rules out anything requiring GPU inference for Week 1.
- **Retrieval latency:** keep Top-K modest (5–10) to bound reranking + context-building time.
- **LLM latency:** the dominant cost in RAG/agent response time; mitigate with streaming where the UI/UX benefits from it (POST-4-WEEK for actual streaming implementation, but design endpoints so streaming can be added without a rewrite).
- **Agent latency:** bound by `max_steps`; measure and report steps-to-completion as a first-class metric.
- **Measurement:** all of the above surfaced through the observability layer (Section S), not just eyeballed during development.

---

# FF. RISKS

| Risk | Mitigation |
|---|---|
| Bad/unrepresentative training data | Use a known public fraud dataset; document its limitations explicitly rather than pretending it's production-grade |
| Class imbalance | Use precision/recall/F1/ROC-AUC, not accuracy; consider resampling or class weighting |
| False positives (fraud model) | Tune threshold deliberately; expose the score, not just a binary label, so analysts can judge |
| Hallucination (RAG) | Enforce grounding — refuse to answer when retrieval returns nothing relevant; require citations |
| Poor retrieval quality | Build an evaluation set early (Week 2) so retrieval quality is measured, not assumed |
| Tool misuse by the agent | Strict tool schemas, validated arguments, permission boundaries enforced in code, not by the model |
| Prompt injection | Treat all retrieved/tool content as untrusted data; never let it override system instructions |
| LLM provider downtime | Clear error handling and graceful degradation (risk scoring keeps working even if the LLM is down) |
| Cost explosion (agent loops) | Hard step/token/cost budgets with fail-safe stop |
| Latency | Budgets per component (Section EE), measured continuously |
| Unauthorized data access | Auth + RBAC + audit logging from Week 1 onward, not bolted on at the end |

---

# GG. ACCEPTANCE CRITERIA (for the complete 4-week system)

The system is considered successful when: a transaction can be submitted and scored end-to-end; a policy/case question returns a grounded, cited answer or a clear refusal; a flagged case can be investigated by the agent using real tool calls, producing a draft that requires explicit human approval before any state change; the entire system runs in a Docker container, deployed via CI/CD, to a real cloud host; golden-dataset evaluations exist and pass for the ML, RAG, and agent layers; logs/traces exist for every AI and tool call; and the four weeks' work reads as one coherent system in the repository history, not four disconnected demos.

---

# HH. DEFINITION OF DONE

A feature is not done until it is:
```
Implemented
+ Tested (unit/integration as appropriate)
+ Documented (README/docstrings updated)
+ Logged (structured logging in place)
+ Evaluated where applicable (ML/RAG/agent metrics)
+ Reviewed (self-review against the Senior Engineer checklist)
+ Committed (Conventional Commit, merged via PR)
```

---

# II. FUTURE ARCHITECTURE (POST-4-WEEK / ADVANCED)

Event-driven architecture with message queues (e.g. moving investigation triggers off the synchronous request path); distributed processing for large-scale document ingestion; Kubernetes for horizontal scaling; dedicated model-serving infrastructure (e.g. a model server rather than in-process inference); a feature store for consistent ML features across training/serving; advanced observability (full APM, alerting, on-call rotations); multi-region deployment for availability and data residency. None of this belongs in the MVP — it's listed so the architecture doesn't accidentally block these paths later (e.g. why `tenant_id` is left as an easy future addition rather than retrofitted).

---

# PART 2 — FOUR-WEEK IMPLEMENTATION ROADMAP

## WEEK 1 — Foundation
**Objective:** Ship a tested, real risk-scoring service backed by a real database.
**Concepts:** Python, data processing, SQL/PostgreSQL, classical ML, FastAPI, testing.
**Architecture:** Section K, "Week 1."
**Features:** transaction ingestion + validation, feature engineering, trained fraud classifier, `/v1/transactions` and `/v1/risk` endpoints, PostgreSQL schema for transactions/cases.
**Deliverables:** a running FastAPI service; a trained, evaluated model; a seeded PostgreSQL database; a test suite.
**Tests:** unit (feature engineering, schema validation), integration (API → DB), ML (model sanity checks).
**Evaluation:** precision/recall/F1/ROC-AUC on a held-out test set.
**Git milestones:** `v0.1.0` tag at week's end.
**Production practices introduced:** basic input validation, structured logging, Conventional Commits, PR self-review.

## WEEK 2 — Knowledge
**Objective:** Ground the platform in real policy/case knowledge via RAG.
**Concepts:** embeddings, vector search (pgvector), RAG, reranking, RAG evaluation.
**Architecture:** Section K, "Week 2."
**Features:** document ingestion + chunking + embedding, `/v1/documents` and `/v1/search` endpoints, grounded Q&A with citations, reranking.
**Deliverables:** a working RAG pipeline over real policy documents; a golden Q&A evaluation set.
**Tests:** RAG tests (retrieval correctness, citation presence), integration tests.
**Evaluation:** Recall@K, Precision@K, faithfulness, answer correctness.
**Git milestones:** `v0.2.0` tag at week's end.
**Production practices introduced:** prompt-injection isolation for retrieved content.

## WEEK 3 — Action
**Objective:** Give the platform the ability to investigate cases using tools, safely.
**Concepts:** tool calling, agent loop, state, memory, human approval, guardrails.
**Architecture:** Section K, "Week 3."
**Features:** tool wrappers for the risk model and RAG service, `/v1/cases`, `/v1/investigations`, `/v1/agent`, `/v1/approvals` endpoints, a bounded agent loop, an approval gate before any state change.
**Deliverables:** a working investigation agent with logged tool calls and a mandatory approval step.
**Tests:** agent tests (tool selection, approval gate enforcement), security tests (injection resistance).
**Evaluation:** task completion rate, tool selection accuracy, invalid tool call rate, human intervention rate.
**Git milestones:** `v0.3.0` tag at week's end.
**Production practices introduced:** explicit agent state, tool permission enforcement, audit logging of every agent action.

## WEEK 4 — Trust
**Objective:** Turn the working system into a deployed, observable, secure production platform.
**Concepts:** security hardening, observability, reliability, Docker, CI/CD, cloud, cost/latency optimization.
**Architecture:** Section K, "Week 4" (final target architecture).
**Features:** full RBAC, secrets management, tracing/metrics, retries/timeouts, Dockerized deployment, CI/CD pipeline, deployed cloud instance.
**Deliverables:** a live, deployed system with a CI/CD pipeline and observability dashboards/logs.
**Tests:** security tests, end-to-end tests, basic load test, full regression run of all golden datasets.
**Evaluation:** production metrics (latency, cost, error rate) layered on top of the ML/RAG/agent evaluations from Weeks 1–3.
**Git milestones:** `v1.0.0` tag — the production release.
**Production practices introduced:** the full CI/CD gate sequence (Section BB), cost tracking, latency budgets enforced.

---

# PART 4 SUMMARY — HOW WE'LL WORK DAY TO DAY

Once you say **START WEEK 1 DAY 1**, each feature follows: problem → concept → engineering reasoning → alternatives/trade-offs → a small example → an implementation task *for you* → my review → your revision → integration → tests → commit. I won't hand you finished code up front — you'll get requirements and hints, write the implementation, and I'll review it like a senior engineer would (code quality, architecture, security, testing, performance, maintainability, AI correctness, production readiness), then push you to improve it before it's integrated. I'll also keep challenging you with the "why" questions (why Postgres, why this metric, why this chunk size, what happens when the LLM fails, how would you scale this) throughout — that's where the actual engineering judgment gets built, not just the code.

---

# POST-4-WEEK TOPICS (full list)

Fine-tuning (LoRA/QLoRA/SFT/DPO/PEFT) · training models from scratch · Kubernetes and multi-node scaling · full LangGraph/CrewAI/AutoGen framework adoption · multimodal AI · multi-vendor vector database comparison · advanced distributed system design (sharding, CAP theorem, replication) · multi-tenancy · event-driven architecture with queues · a feature store · dedicated model-serving infrastructure · drift monitoring automation · A/B testing and feature-flagged rollouts · full circuit-breaker implementation · streaming responses · Redis caching layer (optional stretch, not required) · multi-model routing · SSO/full RBAC · disaster recovery / multi-region deployment · 24/7 observability with alerting and on-call.

---

*This is the complete Master PRD and 4-week program. No implementation, code, database creation, or Day 1 content has been started, per your instruction. Say **START WEEK 1 DAY 1** when you're ready to begin.*
