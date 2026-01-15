# Fly Bot PRD / Technical Spec (Next-Hour Empties + Return-Probability Scoring)

## Context
Fly Bot is for **internal Alaska employees** to estimate the likelihood of **getting on a flight standby** from an airport, with awareness of **return constraints** and party factors (number of travelers, age buckets, region/area of world, and hardness of return time).

This spec implements the approach:
- Look at the **next hour** of outbound departures (“what’s empty?”) using near real-time load/open-seats data.
- Treat outbound as **near-known feasibility** (seat margin), not purely probabilistic.
- Score/rank options primarily by the **probability of meeting return criteria**.
- Be explicit: return a **score breakdown** explaining why top options were rated highly.

---

## Assumptions (explicit)
- **A1:** “Next hour” means departures within `lookahead_minutes` (default **60**).
- **A2:** We can access near real-time **empties/load snapshots** per flight (open seats by cabin if available).
- **A3:** Outbound in the next hour is treated as **constraint + high confidence** but still not guaranteed due to last-minute changes.
- **A4:** The key modeled uncertainty is the **return**: probability the party can meet return criteria (deadline/flex).
- **A5:** We can derive labels for return outcomes: for a given return flight and party, whether the party **cleared standby**.
- **A6:** Age is used only as **age bucket** for seat requirement/eligibility logic.
- **A7:** A baseline heuristic exists for safe fallback when ML is unavailable.

---

## Goals
- Provide fast, consistent, explainable rankings for outbound flights departing soon, prioritizing return feasibility.
- Make ranking transparent via a reproducible scoring formula and response-level score breakdown.
- Support safe rollout, kill switch, fallback, and minimal monitoring (ops + model).

## Non-goals
- Guarantee boarding.
- Replace official employee travel policies; Fly Bot is advisory.
- Optimize multi-day itineraries beyond “next-hour outbound + return constraints” (v1 scope).

---

## Success metrics

### ML metric(s)
**Primary:** **Brier Score** on return-flight clearance probability (calibration-sensitive).
- Target: **≥ 10% relative improvement** vs baseline heuristic on a held-out time-based test set.

**Secondary (recommended):** AUC or ECE (expected calibration error), tracked but not necessarily a hard gate for v1.

### Ops metric(s)
- **p95 end-to-end latency ≤ 800ms** for `/v1/flybot/recommend`
- **5xx error rate < 0.5%** over 5-minute windows
- Track `fallback_used` rate (alert on spikes)

---

## System behavior

### Stage A — Outbound candidate generation (“What’s empty”)
1. Fetch flights departing within `lookahead_minutes` for `(origin, destination)`.
2. For each flight, compute:
   - `open_seats_now` (from snapshot)
   - `seats_required` (from traveler age buckets)
   - `seat_margin = open_seats_now - seats_required`
3. Default feasibility:
   - If `seat_margin < 0`: exclude (configurable override)
   - Else include with outbound confidence proportional to margin and snapshot freshness.

### Stage B — Return feasibility scoring (probability)
For each feasible outbound option:
1. Fetch return schedule candidates within return window.
2. Apply return “hardness” buffer (see below) to determine eligible return flights.
3. For each eligible return flight:
   - Build features
   - Predict `p_i = P(clear_standby | context)`
4. Aggregate eligible return probabilities into a single:
   - `return_success_probability`

---

## Return hardness (explicit)
User provides `return_flex_minutes` (0 = hard). We convert it into a stricter buffered deadline:

- `return_deadline = return_window.latest`
- `buffer_max_minutes = 120` (configurable)
- `h = clamp(1 - return_flex_minutes / buffer_max_minutes, 0, 1)`
- `required_buffer = round(buffer_max_minutes * h)`

A return flight is **eligible** only if:
- `arrival_time <= return_deadline - required_buffer`

This is transparent and testable.

---

## Scoring and ranking (explicit)

### Per-return-flight model output
For each eligible return flight `r_i`, predict:
- `p_i` in [0, 1] (calibrated probability of clearing standby)

### Aggregate return success probability
Assuming approximate independence between attempts:

\[
P(\text{return success}) = 1 - \prod_{i=1}^{N} (1 - p_i)
\]

Expose as:
- `return_success_probability`

### Outbound “near-known” modifier
Outbound affects ranking modestly via seat margin:

- `seat_margin = open_seats_now - seats_required`
- `outbound_margin_bonus = sigmoid(seat_margin / 2)`
- `sigmoid(x) = 1 / (1 + exp(-x))`

### Final trip score
Return dominates; outbound modulates:

\[
trip\_score = return\_success\_probability \times (0.7 + 0.3 \times outbound\_margin\_bonus)
\]

Weights are configurable.

### Deterministic tie-breakers
If `trip_score` ties within epsilon (0.005), rank by:
1. higher `return_success_probability`
2. higher `seat_margin`
3. earlier outbound departure (or caller preference)

### Transparency requirement
Each recommendation MUST include:
- `score_breakdown` with all formula components and a formula string
- stable `reason_codes`
- user-facing `explanations`

---

## API Contract

### Endpoint
`POST /v1/flybot/recommend`

#### Request JSON schema (v1)
```json
{
  "request_id": "string",
  "origin": "SEA",
  "destination": "ANC",
  "lookahead_minutes": 60,
  "return_window": {
    "earliest": "2026-02-08T08:00:00",
    "latest": "2026-02-08T20:00:00",
    "return_flex_minutes": 0
  },
  "travelers": [
    {"age_bucket": "adult"},
    {"age_bucket": "adult"},
    {"age_bucket": "child"}
  ],
  "constraints": {
    "nonstop_only": false,
    "max_connections": 1,
    "cabin_preference": "any"
  }
}
```

#### Response JSON schema (v1)
```json
{
  "request_id": "string",
  "model_version": "string",
  "generated_at": "2026-01-15T12:34:56Z",
  "seats_required": 3,
  "required_return_buffer_minutes": 120,
  "recommendations": [
    {
      "trip_score": 0.41,
      "score_breakdown": {
        "return_success_probability": 0.55,
        "outbound_margin_bonus": 0.79,
        "multiplier": 0.7,
        "bonus_weight": 0.3,
        "formula": "trip_score = return_success_probability * (0.7 + 0.3*outbound_margin_bonus)"
      },
      "outbound": {
        "flight_id": "AS123_2026-02-06",
        "departure_time": "2026-02-06T10:15:00",
        "arrival_time": "2026-02-06T12:55:00",
        "open_seats_now": 5,
        "seat_margin": 2,
        "outbound_feasible": true,
        "outbound_confidence": "high"
      },
      "return_options": [
        {
          "flight_id": "AS456_2026-02-08",
          "departure_time": "2026-02-08T16:30:00",
          "arrival_time": "2026-02-08T19:05:00",
          "eligible": true,
          "clear_probability": 0.40
        }
      ],
      "reason_codes": [
        "RETURN_HARD_BUFFER_APPLIED",
        "OUTBOUND_POSITIVE_SEAT_MARGIN"
      ],
      "explanations": [
        "Return is hard (flex=0), so a 120-minute buffer was applied to the deadline",
        "Outbound has a positive seat margin (2 seats above requirement)"
      ]
    }
  ],
  "fallback_used": false,
  "timing_ms": {
    "empties_fetch": 120,
    "return_candidates_fetch": 110,
    "feature_build": 50,
    "inference": 30,
    "total": 380
  }
}
```

#### Errors
- **400** invalid IATA codes, invalid lookahead, empty travelers
- **422** time relationship invalid (latest < earliest)
- **503** dependencies unavailable and fallback cannot be computed

---

## Baseline + fallback
- Baseline estimates return `p_i` from route/time priors adjusted by party size and optional seasonality.
- If ML fails/disabled → baseline `p_i` and `fallback_used=true`.
- If empties fails → outbound confidence “low” + reason code `DATA_STALE_OR_MISSING_EMPTIES`, and either conservative scoring or (config) 503.

---

## Rollout
1. **Empties-only** (no ML) + logging
2. **Shadow ML** return scoring (not shown)
3. **Internal alpha** (flagged) with score breakdown
4. **Full internal rollout** with kill switch and monitoring

---

## Monitoring (minimal)
**Ops:** p95 latency, 5xx, dependency errors, fallback rate  
**ML:** distribution drift of return probabilities, # eligible return options, delayed Brier score on joined outcomes
