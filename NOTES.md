# Project Notes & Decision Log

Append-only. One entry per feature or notable decision, in chronological order.
Never edit past entries to look smarter in hindsight — if a decision turned out to be
wrong, add a NEW entry explaining what changed and why. That history has value.

## How to write an entry
```
## [Week X, Day Y] Feature/Decision Title

**Context:** What problem were we solving? What was already in place?

**Decision:** What did we actually build/choose?

**Alternatives considered:** What else could we have done, and why didn't we?

**Trade-offs:** What are we giving up with this choice? What would make us revisit it?

**Status:** implemented / in progress / reverted / superseded by [link to later entry]
```

Keep each entry short — a few sentences per section is enough. The goal is
"future me (or an interviewer) can understand why this exists," not a full essay.

---

## [Setup] Project initialized

**Context:** Starting the 4-week Fraud Ops Platform build.

**Decision:** Repo structured by capability (services/pipelines/agents/rag/etc.),
not by week — the system is one product across four milestones. Full rationale
in `docs/PRD.md`, Section Y (Repository Architecture).

**Alternatives considered:** A folder-per-week structure — rejected because it
would encourage treating each week as a separate throwaway project instead of one
evolving system.

**Trade-offs:** None significant at this stage.

**Status:** implemented


## [Setup] Repo pushed to GitHub

**Context:** Local repo initialized with folder structure, CLAUDE.md, NOTES.md, PRD.

**Decision:** Created `fraud-ai-platform` on GitHub, connected via a fine-grained
Personal Access Token scoped to this repo only (Contents: Read/write), 90-day expiry.

**Alternatives considered:** Classic PAT with broader scope — rejected in favor of
least-privilege access, since a leaked broad-scope token risks every repo, not just this one.

**Trade-offs:** Token needs manual renewal every 90 days — acceptable for a personal project.

**Status:** implemented

## [Week 1, Day 1] Local PostgreSQL + pgvector setup

**Context:** Needed a local database with vector search support provisioned early
(Week 1) even though RAG isn't built until Week 2, to avoid a mid-project DB migration.

**Decision:** Postgres 16 + pgvector via Docker Compose (`pgvector/pgvector:pg16`),
credentials sourced from a root-level `.env`, data persisted via a named volume.
Runtime is actually Podman (aliased as `docker` on this machine) — noted in case
future errors are Podman-specific rather than Docker-specific.

**Incident:** First boot used `POSTGRES_USER=Yashas P M` (a personal name with
spaces) instead of a proper service-account name, causing role-not-found errors
on connection. Fixed by correcting `.env` to `fraud_admin` and running
`docker compose down -v` to wipe the already-initialized (and broken) volume,
since Postgres only runs first-time initialization on an empty data directory.

**Alternatives considered:** Restarting the container without wiping the volume —
doesn't work, since Postgres won't re-initialize an existing data directory.

**Trade-offs:** None — no real data existed yet, so the wipe was free.

**Status:** implemented

## [Week 1, Day 1] transactions table created

**Context:** Needed the core table PaySim data will load into, before writing any
ingestion or feature-engineering code.

**Decision:** UUID primary key (non-guessable, safer default for a fraud system)
over BIGSERIAL. ENUM for transaction_type (fixed, known PaySim category set) over
plain TEXT, trading migration friction for write-time data quality guarantees.
NUMERIC(15,2) for all money fields — never FLOAT. TIMESTAMPTZ throughout.
created_on/updated_on as explicit audit columns (updated_on auto-bump-on-UPDATE
trigger deliberately deferred — not needed until update logic exists).
Indexed sender_account_id only — high-cardinality, frequently filtered; did NOT
index transaction_type or is_fraud (low-cardinality, poor index selectivity).

**Alternatives considered:** BIGSERIAL PK (rejected — sequential IDs leak
information in a fraud context). TEXT for transaction_type (rejected — no
guardrail against inconsistent values like "Transfer" vs "TRANSFER").

**Trade-offs:** ENUM makes adding a genuinely new transaction type later a real
migration (ALTER TYPE), not just a config change — accepted deliberately, since
PaySim's category set is fixed and known upfront.

**Status:** implemented

## [Week 1, Day 2] transactions table created

**Context:** Needed the core table PaySim data will load into, before writing any
ingestion or feature-engineering code.

**Decision:** UUID primary key (non-guessable, safer default for a fraud system)
over BIGSERIAL. ENUM for transaction_type (fixed, known PaySim category set) over
plain TEXT, trading migration friction for write-time data quality guarantees.
NUMERIC(15,2) for all money fields — never FLOAT. TIMESTAMPTZ throughout.
created_on/updated_on as explicit audit columns (updated_on auto-bump-on-UPDATE
trigger deliberately deferred — not needed until update logic exists).
Indexed sender_account_id only — high-cardinality, frequently filtered; did NOT
index transaction_type or is_fraud (low-cardinality, poor index selectivity).

**Alternatives considered:** BIGSERIAL PK (rejected — sequential IDs leak
information in a fraud context). TEXT for transaction_type (rejected — no
guardrail against inconsistent values like "Transfer" vs "TRANSFER").

**Trade-offs:** ENUM makes adding a genuinely new transaction type later a real
migration (ALTER TYPE), not just a config change — accepted deliberately, since
PaySim's category set is fixed and known upfront.

**Status:** implemented

## [Week 1, Day 3] Database connection debugging — three real bugs, one session

**Context:** First attempt to connect Python (SQLAlchemy) to the Dockerized
Postgres instance for a smoke test of Transaction/FraudCase models.

**Bugs found and fixed, in order:**
1. `POSTGRES_HOST=localhost` caused psycopg2 to attempt a Unix socket connection
   instead of TCP — fixed by using `127.0.0.1` explicitly.
2. Password contained an `@` character, which collided with the `@` delimiter
   in the `user:password@host` connection string format, corrupting the parsed
   host. Fixed with `urllib.parse.quote_plus()` to percent-encode the password
   before building the URL.
3. `fraud_cases.sql` had been discussed/written in chat but never actually
   saved to disk or executed — `models.py` described a table that didn't exist.
   Created the file, ran it against the DB.

**Decision:** Each bug was isolated independently (connection layer vs. model
layer vs. file-existence) via a purpose-built smoke test, rather than
guessing/patching randomly.

**Status:** implemented — full connection + both models verified working.

## [Week 1, Day 4] Data leakage caught and fixed in risk model

**Context:** Initial model trained on engineered features hit Precision 1.0,
ROC-AUC 1.0 — an implausible result for real fraud detection.

**Root cause:** `sender_balance_error`, `receiver_balance_error`, and
`sender_emptied_account` were derived from PaySim's own balance-update logic,
which has a known artifact: fraudulent transactions in the simulator often
zero out balances in a way that near-perfectly encodes the label itself.
These weren't real behavioral signals — they were leaking the answer.

**Decision:** Removed the three leaking features, kept `sender_balance_delta`
(a legitimate derived feature). Retrained.

**Result:** Precision 0.90, Recall 0.6552, F1 0.76, ROC-AUC 0.9996 — believable
and defensible, though ~35% of real fraud is still missed at the default 0.5
probability threshold. Open question for Week 1 wrap-up: whether to tune the
decision threshold to trade some precision for higher recall, given that a
missed fraud case is typically costlier than a false alarm.

**Status:** implemented — model retrained and saved; threshold tuning pending.

## [Week 1, Day 5] Decision threshold finalized

**Context:** Default 0.5 threshold caught only 65% of real fraud (Recall 0.6552).
Threshold analysis swept 0.10–0.55 to see the full precision/recall trade-off.

**Decision:** Set DECISION_THRESHOLD = 0.30 (Precision 0.7857, Recall 0.7586).
Deliberately biased toward recall relative to the default, since a missed fraud
case is typically costlier than a false alarm an analyst dismisses quickly.
Noted but did not compute the F1-optimal threshold mathematically — chose to
reason from the business trade-off directly rather than pure statistical balance,
since F1 treats false positives/negatives as equally costly, which isn't true here.

**Status:** implemented — Week 1 (Foundation) complete.

## [Week 2, Day 1] Embeddings via Ollama (local, open-source)

**Context:** Needed an embedding model to convert text into comparable vectors
for RAG retrieval. Also wanted to avoid introducing a second local-model tool
alongside the Ollama LLM fallback already planned for Week 4.

**Decision:** Ollama + `nomic-embed-text` (local, free, ~274MB) — one local-model
runtime serving both embeddings (Week 2) and LLM fallback (Week 4), instead of
`sentence-transformers` as a separate dependency. Closes the "Open Source AI"
gap identified from the roadmap.sh comparison.

**Validation:** Cosine similarity test — related sentences ("balance dropped to
zero" vs "funds completely withdrawn") scored 0.6638; unrelated sentence
("weather was sunny") scored 0.4075. Correct relative ranking confirmed.
Noted: absolute similarity values sit in a "baseline positive" zone for any
coherent English text — retrieval must always compare candidates *relative*
to each other (top-K), never against a fixed absolute cutoff.

**Alternatives considered:** `sentence-transformers` (Hugging Face) — rejected
to avoid a second local-model runtime doing a conceptually similar job.

**Status:** implemented

## [Week 2, Day 2] Document ingestion — chunking, embedding, storage

**Context:** Needed real policy text in the system for RAG. Sourced the FFIEC
BSA/AML Examination Manual (public, U.S. government document) instead of an
invented sample, since real regulatory structure/language has more evaluation
and portfolio value.

**Incident:** First download attempt via plain `curl` silently saved an HTML
error page instead of the real PDF (`invalid pdf header: b'<!DOC'` on parse) —
government site blocked the request without a browser User-Agent. Fixed with
`curl -L -A "Mozilla/5.0..."`. Caught only because we verified the file with
`file` before trusting it — same discipline as the fraud_cases.sql incident.

**Decision:** Fixed-size chunking (800 chars, 100 char overlap) via pypdf text
extraction. Embeddings via Ollama (nomic-embed-text, 768 dimensions). Storage
via SQLAlchemy ORM + the `pgvector` SQLAlchemy extension (`Vector(768)` column
type) — corrected an earlier inconsistency where raw SQLAlchemy Core/text()
was used instead of the ORM pattern established in Week 1, to keep one
consistent data-access style across the project.

**Result:** 103,918 characters extracted, 149 chunks created, all embedded and
stored in `document_chunks`.

**Status:** implemented

## [Week 2, Day 3] First working end-to-end RAG pipeline

**Context:** Combined semantic search (Day 2) with local LLM generation
(Ollama, llama3.2) to produce grounded answers with citations.

**Decision:** Prompt explicitly instructs the model to answer ONLY from
provided context and to say so if context is insufficient — the mechanism
enforcing groundedness, per PRD's RAG grounding requirement. Sources returned
alongside the answer text, not just the answer, so citations are structurally
built in rather than bolted on later.

**Validation:** [FILL IN: did you manually verify each claim in the generated
answer against the actual retrieved chunk text? What did you find?]

**Status:** implemented — first full RAG loop working (retrieval → generation
→ citations).

## [Week 2, Day 4] Grounding vs. synthesis trade-off — known model limitation

**Context:** Iterated through three prompt strategies trying to get llama3.2
to correctly (a) synthesize answers across scattered relevant chunks and
(b) refuse when a term appears throughout the corpus but is never actually
defined. Tested against a 3-question regression set discovered through real
usage: "What is BSA/AML" (undefined term — should refuse), "What happens if a
bank fails to comply" (answer scattered across chunks — should synthesize),
"What is required of a BSA compliance officer" (clean single-chunk answer —
baseline case).

**Finding:** No single prompt version tested got all three right
simultaneously. Strict grounding language fixed the refusal case but broke
synthesis. Permissive/chain-of-thought prompting fixed synthesis but
reintroduced hallucination on the refusal case — the model treats an acronym
appearing frequently throughout retrieved chunks as license to define it from
its own training knowledge, even when no chunk actually contains a definition.

**Decision:** Kept the chain-of-thought prompt (rag/generate_answer.py),
since it correctly handles the majority of realistic multi-chunk synthesis
questions, which matter more for this platform's actual use case than acronym
lookups. Documenting the "term-present-but-undefined" hallucination as a known
limitation of llama3.2 at this prompt complexity, rather than continuing to
iterate against a project deadline.

**What would fix this properly (not implemented — time-boxed decision):**
(1) A larger/commercial LLM, which handles this distinction more reliably.
(2) A second verification pass: after generating an answer, ask the LLM
(or a separate check) "is this specific claim explicitly stated in the
source text, yes/no" before returning it to the user — real technique,
meaningfully more engineering complexity.
(3) A stricter glossary-style guardrail specifically for acronym/definition
questions, detected and handled as a special case.

**Status:** documented limitation — acceptable for portfolio/demo purposes,
would need addressing before genuine production use.

## [Week 3, Day 1] First working agent loop (ReAct pattern, hand-rolled)

**Context:** Built the agent loop by hand (per PRD Framework Strategy — raw
loop before any framework), wrapping Week 1's risk scoring and Week 2's RAG
as callable tools.

**Iterations and findings:**
1. First run: agent called get_risk_score 4 times with identical arguments,
   never used the actual score value in its reasoning, never reached "finish"
   before MAX_STEPS. Root cause: no duplicate-action detection, no explicit
   prompt instruction to use prior observations.
2. Added duplicate-action detection (tracked via a set of (action, args)
   signatures) and explicit "reference the most recent Observation" prompt
   instruction. Result: duplicates stopped, reasoning correctly referenced
   the real risk score — but agent got stuck rephrasing an unanswerable
   policy question 3 times, still hit MAX_STEPS.
3. Added forceful instruction injection ("your next Action MUST be finish")
   triggered after the first blocked duplicate. Final run: clean 2-step
   execution, correct risk-score usage, proper finish with valid summary.

**Known limitation (undertested):** the forceful "must finish" injection
was built and is logically sound, but the clean final run succeeded before
that mechanism was ever triggered — it has not been directly proven to work
under real failure conditions, only inferred from the plain duplicate-block
behavior observed in iteration 2. Acceptable gap given timeline; would want
a dedicated test forcing this path before calling it production-verified.

**Broader finding:** llama3.2 (3B, local) can articulate correct reasoning
("I should not repeat this action") without that reasoning reliably
constraining its next output — required explicit, forceful instruction
injection rather than persuasive/explanatory prompting alone. A larger or
commercial model would likely need less scaffolding here.

**Status:** implemented — basic agent loop working for the risk+policy
investigation use case.

## [Week 3, Day 2] Human approval gate — verified end-to-end

**Context:** PRD requires state-changing actions (closing a case) to be
blocked until explicit human approval. Needed to prove this structurally,
not just claim it works.

**Decision:** Split into two functions with different permissions:
`request_case_closure` (callable by the agent, never sets status to CLOSED)
and `approve_case_closure` (the only function anywhere that can set CLOSED,
wired only to a human-facing API endpoint, never to the agent's tool list).

**Bugs found along the way:**
1. Agent initially claimed "I will close the case" in its finish summary
   without ever calling recommend_case_closure — added a code-level check
   comparing claimed actions against actual tool-call history, forcing
   correction rather than trusting the model's self-report.
2. Agent's goal string didn't include a real transaction_id, so it had
   nothing valid to pass even when it did try to call the tool — fixed by
   explicitly including a verified real transaction ID in the goal.

**Verification:** Directly invoked request_case_closure (bypassing agent
judgment, since a security-critical path shouldn't rely on hoping the LLM
exercises it) → confirmed row created with status=OPEN → called
POST /v1/approvals/{case_id} → confirmed status flipped to CLOSED only after
that call, with notes correctly appended. Full chain verified with real
database queries at each stage, not assumed from code review alone.

**Status:** implemented and verified — the actual security control the PRD
requires (model is never the final authority on state-changing actions) is
now a structural fact about the codebase, not just a design intention.

## [Pre-Week-4] Production hardening pass on Weeks 1-3

**Context:** Before starting Week 4, audited Weeks 1-3 for gaps against the
PRD's own Reliability/Testing requirements rather than assuming "it works"
from manual testing alone.

**Fixes applied:**
1. Added explicit timeouts (30-60s) + graceful degradation on every Ollama
   HTTP call (embeddings, reranking, generation, agent loop) — previously
   any of these could hang indefinitely with no recovery.
2. Eliminated train/serve feature skew — build_inference_features() is now
   the single source of truth used by both training and the live API,
   replacing duplicated inline logic in apps/main.py that could have
   silently drifted (it still referenced a removed leaky feature).
3. Added input validation bounds (length, top_k range) on /v1/search and
   /v1/ask — previously unbounded.
4. Added basic structured logging (success/failure per endpoint) — replacing
   raw SQL echo noise as the only visibility into request handling.
5. Built first real test suite (9 tests): feature engineering shape +
   leakage-regression guard, model sanity check, RAG duplicate-regression
   guard, agent tool contract checks, DB constraint enforcement. Required
   pytest.ini with pythonpath=. — same root-import issue as every prior
   `-m module` fix this project has hit, now solved once, centrally.

**Status:** implemented — all 9 tests passing. Weeks 1-3 now have real
regression protection against every major bug found this week, not just
manual verification.

## [Pre-Week-4] Model explainability endpoint

**Context:** PRD lists "feature importances on request" as an Explainability
requirement (Development Target, NFR table).

**Decision:** GET /v1/risk/explain returns global feature importances from
the trained RandomForest (model.feature_importances_) — not a per-transaction
explanation (would require SHAP, deferred as Post-MVP given time/complexity).

**Validation:** Rankings pass a domain sanity check — sender_balance_delta,
amount, and balance fields dominate, consistent with legitimate fraud signal
post-leakage-fix. day_of_week scored exactly 0.0 — plausible, since PaySim's
30-day simulation likely has no real weekly pattern to learn; not treated as
a bug.

**Status:** implemented
