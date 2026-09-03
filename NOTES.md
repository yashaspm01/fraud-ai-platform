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

## [Week 1, Day 2] Database connection debugging — three real bugs, one session

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
