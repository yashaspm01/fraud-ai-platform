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
