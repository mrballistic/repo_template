# Fly Bot Engineering Design Doc

## Assumptions
- Near real-time “empties/load snapshot” exists for flights departing within lookahead window.
- Return scoring uses a calibrated probabilistic model and explicit aggregation.
- Internal-only auth; logs avoid PII (use age buckets + hashed identifiers).

---

## 1) Architecture
### Components
1. **API Service**
   - Validates request, computes seats_required and buffer, fetches dependencies, predicts return probabilities, scores trips, returns explicit breakdown.
2. **Data Clients**
   - `EmptiesClient` for outbound next-hour open seats
   - `ScheduleClient` for return candidate flights
   - Optional: `DisruptionClient` for delay/cancel/weather signals
3. **ML Package**
   - Feature builder, model loader, calibrated predictor
4. **Observability**
   - Metrics, logs, tracing, dashboards, alerts
5. **Offline pipeline**
   - Dataset build, train, calibrate, evaluate, package, publish

### Request lifecycle
1. Validate schema
2. Derive `seats_required`
3. Fetch outbound flights in `lookahead_minutes` + empties snapshot
4. Filter by `seat_margin >= 0` (default)
5. Fetch return schedule in return window
6. Compute buffer, mark eligible returns (arrival <= latest-buffer)
7. Predict `p_i` for eligible returns (ML or baseline)
8. Aggregate return success: `1 - Π(1 - p_i)`
9. Compute outbound bonus: `sigmoid(seat_margin/2)`
10. Compute trip score: `return_success_probability * (0.7 + 0.3*outbound_bonus)`
11. Sort + tie-break + add reason codes and explanations
12. Respond + emit logs/metrics

---

## 2) Service design
### Endpoints
- `POST /v1/flybot/recommend`
- `GET /healthz`
- `GET /readyz` (fails if ML enabled and model not loaded)

### Determinism
Given the same:
- model_version
- config weights
- dependency snapshot inputs  
…results are reproducible (within numeric tolerance). Include timestamps and snapshot ids when possible.

---

## 3) Feature computation
### Seats required
- Single policy-driven function mapping age buckets to seat counts.
- Keep rules in config; unit test thoroughly.

### Return buffer
- `buffer_max_minutes` configurable (default 120)
- `required_buffer = round(buffer_max_minutes * clamp(1 - flex/buffer_max_minutes, 0, 1))`

### ML features (v1)
- route/region, day-of-week, hour-of-day
- capacity/load snapshot signals if available
- time-to-departure
- seats_required/party size
- seasonality; disruptions flags (optional)

Feature parity: one feature builder shared across training + inference.

---

## 4) ML design
### Target label
`label_cleared = 1` if the party cleared standby on the return flight; else 0.

### Model
- v1: Gradient boosted trees (fast inference) + calibration (isotonic or Platt).

### Artifact bundle
- model binary, calibration params, feature schema, model card, version.

---

## 5) Scoring engine
Implement as pure functions:
- buffer computation
- eligible return filtering
- return prediction
- aggregation `1 - Π(1 - p_i)`
- outbound bonus
- trip score
- deterministic tie-break
- explanation + reason codes

Return both:
- stable `reason_codes` (testable)
- user-facing explanations (can evolve)

---

## 6) Dependencies & failure handling
- Strict per-dependency timeouts to protect p95.
- If ML fails: fall back to baseline return probabilities.
- If empties missing/stale: reduce outbound confidence and optionally apply conservative logic.

---

## 7) Feature flags
- enable/disable ML
- enable/disable empties usage
- exclude negative seat margin
- scoring weights and buffer max minutes

---

## 8) Observability
### Metrics
- latency buckets, error counts, dependency latency, fallback counters, coverage (# eligible returns)

### Logging
Structured logs (no PII), include:
- request_id, model_version, seats_required, outbound seat margin, return p_i list (sampled), trip_score, reason codes, timing.

### Alerts
- p95 latency, 5xx rate, dependency errors, fallback spikes.

---

## 9) Deployment
- Containerized service (FastAPI recommended)
- readiness requires model loaded when ML enabled
- rollback via feature flag (baseline-only) and model version pin.

---

## 10) Testing
- Unit: buffer, aggregation, scoring formula, determinism, reason codes
- Integration: dependency mocks + failure injection
- Perf: load test to meet p95 ≤ 800ms
