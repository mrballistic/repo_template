# Spec: Dev Demo Data Mode (Mock Flights)

## Goal
Make it easy to “play with” Fly Bot locally by generating a large amount of deterministic mock outbound/return flight data behind an env flag.

This is **dev-only** behavior and must be opt-in.

## Non-goals
- No production-grade persistence
- No real dependency integrations
- No PII

## Interface
Enable demo data mode via env vars:
- `FLYBOT_DEMO_DATA=1` enables demo clients
- `FLYBOT_DEMO_SEED` (int, default 0) controls determinism
- `FLYBOT_DEMO_OUTBOUND_COUNT` (int, default 200) number of outbound flights
- `FLYBOT_DEMO_RETURN_COUNT` (int, default 400) number of return flights
- `FLYBOT_DEMO_NOW_ISO` (optional ISO8601 datetime) freezes "now" for determinism

## Acceptance Criteria
- **AC-DEMOMODE-1:** When `FLYBOT_DEMO_DATA=1`, calling `POST /v1/flybot/recommend` with a valid request returns `recommendations` with length > 0.
- **AC-DEMOMODE-2:** With the same `FLYBOT_DEMO_SEED` and `FLYBOT_DEMO_NOW_ISO`, repeated calls return the same top recommendation `outbound.flight_number`.
- **AC-DEMOMODE-3:** When `FLYBOT_DEMO_DATA` is not enabled, behavior remains unchanged (default empty mock clients).
- **AC-DEMOMODE-4:** Demo data generation is deterministic and contains no PII fields.
