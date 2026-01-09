# Feature Spec: Example — Delay Risk Score (Toy)

- **Status:** Draft
- **Owner(s):** ML Platform
- **Reviewer(s):** App Eng / Ops
- **Last updated:** 2026-01-09

---

## 1) Problem and context (why)
We need a simple risk score that estimates the likelihood of a delay given basic flight metadata. This is a toy example for workflow practice.

Constraints:
- Must be deterministic
- Must fail safely on invalid inputs

## 2) Goals and non-goals
Goals:
- Provide a numeric risk score 0..1
- Provide reason codes for the top contributing factors (toy)

Non-goals:
- Train a real model
- Optimize accuracy (this is workflow scaffolding)

Success metrics:
- Operational: p95 latency < 20ms (toy)
- Product: API returns stable schema with clear errors

## 4) Inputs / outputs
Inputs (required):
- flight_id: str
- dep_delay_min: int (>= 0)
- distance_mi: int (> 0)

Outputs:
- prediction: float in [0, 1]
- confidence: float in [0, 1]
- reason_codes: list[str]

Error behavior:
- On invalid inputs, raise ValueError with a clear message.

## 5) Acceptance criteria
- AC-1: Given valid inputs, `predict(payload)` returns keys {prediction, confidence, reason_codes}.
- AC-2: Given dep_delay_min < 0, validation fails with an error message mentioning dep_delay_min.
- AC-3: Given the same payload twice, outputs are identical (deterministic).
- AC-4: prediction and confidence are clamped to [0, 1].
