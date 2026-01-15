# Fly Bot Task List (TDD-first)

This list is organized to ship value early (empties-first), then add ML return scoring, then harden with monitoring + rollout controls — **using Test-Driven Development (TDD) throughout**.

**TDD rule:** For every new behavior or bug fix, write a failing test first (Red), implement the minimal code to pass (Green), then refactor safely (Refactor).

---

## Phase 0 — Testing harness + scaffolding (before “real code”)
1. Scaffold repo: `pyproject.toml`, `src/`, `tests/`, `pipelines/`, `docs/`
2. Add Ruff + Pytest (and optional mypy) configs
3. Add uv workflows:
   - `uv venv`, `uv sync`, `uv run pytest`, `uv run uvicorn ...`
4. Establish test structure:
   - `tests/unit/` (pure scoring functions)
   - `tests/integration/` (API + dependency mocks/fakes)
   - `tests/contract/` (schema/contract validation)
5. Create a **golden scenario fixture**:
   - input request JSON
   - mocked empties response
   - mocked return schedule response
   - expected ranked recommendations and score breakdown (deterministic)

---

## Phase 1 — Core scoring engine via unit tests (tests first, then code)
6. **Write tests** for `seats_required(travelers)`:
   - adult/child/infant bucket cases
   - deterministic output
7. **Write tests** for return buffer computation:
   - flex=0 → buffer=120
   - flex=120 → buffer=0
   - flex>120 clamps to 0
   - negative flex treated as 0 (or rejected—pick one and test it)
8. **Write tests** for return eligibility:
   - arrival <= latest-buffer → eligible
   - arrival > latest-buffer → not eligible
   - boundary equality case
9. **Write tests** for return aggregation:
   - `1 - Π(1 - p_i)` for known vectors
   - empty eligible list returns 0.0 (or documented alternative)
10. **Write tests** for outbound modifier:
   - `outbound_margin_bonus = sigmoid(seat_margin/2)`
   - monotonicity with seat_margin
11. **Write tests** for trip scoring formula:
   - `trip_score = return_success_probability * (0.7 + 0.3*outbound_margin_bonus)`
   - verify within numeric tolerance
12. **Write tests** for deterministic ranking + tie-breakers:
   - epsilon tie handling
   - order stability
13. **Write tests** for reason codes selection on known scenarios:
   - hard buffer applied
   - low return option coverage
   - missing/stale empties
   - fallback baseline used

*(Only after each test exists do we implement the corresponding function.)*

---

## Phase 2 — API contract + integration tests (tests first)
14. Define Pydantic schemas for request/response and internal models
15. **Write contract tests** verifying:
   - valid requests parse successfully
   - invalid requests fail with expected error code and fields
16. **Write integration test** for `/v1/flybot/recommend` using mocked clients:
   - returns expected sorted recommendations
   - includes `score_breakdown`, `reason_codes`, `timing_ms`
17. **Write integration test**: empties down or stale → fallback behavior (as configured) and `fallback_used=true`
18. **Write integration test**: schedule dependency down → fallback or 503 (as configured)
19. **Write integration test**: invalid time relationships → 422

Then implement:
20. Implement FastAPI app + endpoint wiring
21. Implement dependency client interfaces + default mocks for tests
22. Implement timing collection per step in response

---

## Phase 3 — Baseline heuristic (fallback + benchmark) (tests first)
23. **Write tests** for baseline return `p_i` properties:
   - bounded within [0, 1]
   - decreases as `seats_required` increases
   - deterministic for same inputs
24. Implement baseline heuristic:
   - route/time priors + party penalty + optional seasonality
25. Wire baseline fallback:
   - ML disabled/unavailable → baseline `p_i`, set `fallback_used=true` and reason code
26. Add a simple evaluation script that reports baseline metrics on a static dataset

---

## Phase 4 — Observability (testable where practical)
27. **Write tests** verifying structured logs include required keys and omit PII
28. Implement structured logging aligned to `flybot_predictions_log`
29. Implement metrics:
   - latency, error counts, dependency latency, fallback counters, coverage (# eligible returns)
30. Add a lightweight “metrics smoke test” in integration suite

---

## Phase 5 — ML pipeline (return model) (tests first)
31. **Write tests** for dataset builder outputs:
   - required columns present
   - required fields non-null
   - types within expected ranges
32. Implement dataset builder for `return_clearance_training_examples`
33. Implement labeling logic and document `label_source`
34. Implement shared feature builder (training + inference parity)
35. **Write tests** for evaluation outputs:
   - includes Brier score and baseline delta
36. Train v1 model (GBDT) + calibrate probabilities
37. Package model bundle (model + calibration + schema + model card)
38. Implement model loader in service:
   - pinned model_version via config
   - readiness fails if ML enabled and model missing

---

## Phase 6 — Rollout mechanics + reliability
39. Add shadow mode:
   - compute ML but do not show; log ML vs baseline for comparison
40. Add kill switch:
   - disable ML instantly, revert to baseline
41. Staging rollback drill:
   - previous model pin and service rollback

---

## Phase 7 — Performance & hardening
42. Enforce dependency timeouts to protect p95
43. Add load test to validate p95 ≤ 800ms and 5xx < 0.5%
44. Add chaos tests for slow/down dependencies ensuring correct fallback + reason codes
