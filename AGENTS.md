# AGENTS.md — How to work in this repo (for humans and AI assistants)

This file defines **operating rules** for AI assistants and contributors in this repository.

## Prime directive
**Do not implement or change behavior unless it is traceable to the spec and acceptance criteria.**

## Required workflow
1. Start from a spec in `specs/` (create or update one).
2. Ensure acceptance criteria (AC-*) exist and are **testable**.
3. Write/modify tests in `tests/` first (or alongside) to enforce the ACs.
4. Implement the minimum code needed to pass tests.
5. Keep diffs small; prefer multiple small PRs over one large PR.
6. Update docs and monitoring/eval hooks as required by the spec.

## Hard constraints (non-negotiable)
- **No secrets** in code, logs, or prompts.
- **No sensitive data** in non-approved tools.
- **No silent interface changes**: if you change an input/output contract, update:
  - the spec
  - contract tests
  - versioning/migration notes (if applicable)
- **No “works on my machine”**: changes must be verifiable via tests and/or reproducible commands.

## When using an AI assistant
The assistant must:
- Ask clarifying questions when requirements, metrics, schemas, or rollout are ambiguous.
- Reference repository context (existing files, patterns) when suggesting changes.
- Prefer generating **tests and acceptance criteria** before implementation code.
- Provide a short plan before making multi-file edits.
- Explain assumptions and highlight risks.

### Output style requirements for AI-generated changes
- Include the **AC label** in test comments (e.g., `# AC-3`).
- Include clear error messages for validation failures.
- Prefer deterministic behavior by default (seeded randomness if used).

## Compounding engineering: how rules evolve
If you see recurring PR feedback, convert it into:
1. A new checklist item in `.github/PULL_REQUEST_TEMPLATE.md`
2. A new rule here (keep it one line if possible)
3. An automated gate (test, lint rule, CI check) when feasible

Track rule changes in `docs/compounding_engineering.md`.

## Common repo expectations (edit to your org)
- Log enough context to debug: request id, model version, config version (where applicable)
- Include a safe fallback behavior for low confidence / model unavailability
- Maintain a clear eval story (offline + monitoring)


Instructions for coding agents (human or AI) working in this repo.

---

## Project goals
Fly Bot is an internal recommender for standby travel:
- **Outbound (next hour):** find “what’s empty” using near-real-time open seats.
- **Return:** compute the probability of meeting return criteria (deadline + flexibility) using a calibrated ML model.
- **Ranking:** explicit, reproducible scoring formula with a returned `score_breakdown` and stable `reason_codes`.
- **Safety:** feature flags, fallback behavior, monitoring, and easy rollback.

---

## TDD policy (mandatory)
We use **Test-Driven Development**: tests are written early and often.

Rules:
1. **Red → Green → Refactor** for every new behavior.
2. **No new logic without a test.** Start by writing a failing unit/integration test that captures the intended behavior.
3. **Bug fixes require a regression test first** (fail before fix).
4. Keep scoring logic in **pure functions** so unit tests remain fast and deterministic.
5. Prefer small tests; add a **golden scenario** integration test to prevent scoring regressions.

---

## Tech stack
- Python **3.11+**
- Dependency management: **uv**
- API framework: **FastAPI** (recommended)
- Tests: **pytest**
- Lint: **ruff**
- Optional: typing via mypy/pyright

---

## Quickstart (local)
```bash
uv venv
uv sync
uv run pytest
uv run uvicorn flybot.api.app:app --host 0.0.0.0 --port 8000
```

---

## Repo conventions

### Core modules (suggested)
- `flybot/api/` — FastAPI app, routes, request/response schemas
- `flybot/clients/` — dependency adapters (`EmptiesClient`, `ScheduleClient`, etc.)
- `flybot/scoring/` — pure scoring functions (buffer, eligibility, aggregation, trip score)
- `flybot/model/` — model loading, prediction, calibration
- `flybot/baseline/` — heuristic fallback for return probabilities
- `pipelines/` — offline dataset build, training, calibration, evaluation
- `docs/` — PRD/spec, design doc, data schema, task list

### Determinism requirements
- Scoring functions must be **pure** and deterministic.
- `trip_score` MUST equal:
  `return_success_probability * (0.7 + 0.3*outbound_margin_bonus)`
- `return_success_probability` MUST equal:
  `1 - Π(1 - p_i)` over eligible return flights.
- Return buffer MUST follow the documented clamp/round logic.

### Explainability requirements
Every recommendation MUST include:
- `score_breakdown` fields sufficient to reproduce the score
- stable `reason_codes` (machine-readable, testable)
- user-facing `explanations` (strings; can evolve)

### Feature flags
Implement as config/env toggles:
- enable/disable ML return model
- enable/disable empties usage
- exclude negative seat margin
- scoring weights + buffer max minutes
- strict vs permissive behavior when dependencies are missing

---

## Testing expectations (what to write first)

### Unit tests (must-have)
- Seats required rules
- Return buffer math and eligibility filtering
- Aggregation function: `1 - Π(1 - p_i)`
- Outbound margin bonus monotonicity + known values
- Trip score formula exactness
- Tie-break determinism
- Reason code selection for known scenarios

### Integration tests (must-have)
- Mock empties and schedule dependencies
- Dependency failures trigger fallback with `fallback_used=true`
- Contract tests for request/response schemas

### Performance tests (should-have)
- Validate p95 ≤ 800ms under representative QPS
- Enforce dependency timeouts to protect p95

---

## Observability requirements
- Structured JSON logs (no PII; use age buckets, hashed IDs)
- Metrics for latency, errors, dependency latency, fallback rate, coverage (# eligible return options)
- Alerts on p95 latency, 5xx rate, dependency errors, fallback spikes

---

## Definition of Done (DoD)
A change is “done” when:
- A test exists for the behavior (unit or integration) and passes
- Unit + integration tests pass (`uv run pytest`)
- Lint passes (`uv run ruff check`)
- Scoring remains deterministic and matches the spec
- Response includes score breakdown + reason codes
- No PII is logged

---

## Where to start
1. Write unit tests for scoring math and determinism.
2. Add the golden scenario integration test with mocked dependencies.
3. Implement the API using baseline probabilities first.
4. Add ML pipeline and swap baseline for ML behind a flag.
