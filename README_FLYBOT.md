# Fly Bot - Standby Travel Recommender

Internal Alaska Airlines standby travel recommender built with TDD and spec-driven development.

## Overview

Fly Bot helps employees estimate the likelihood of getting on a standby flight by:
- Finding "what's empty" in the next hour using near real-time seat availability
- Computing the probability of meeting return constraints using a calibrated ML model  
- Ranking options with explicit, reproducible scoring and transparent explanations

## Quick Start

### Setup

```bash
# Install dependencies
uv sync

# Run tests  
uv run pytest

# Start API server
uv run uvicorn flybot.api:app --host 0.0.0.0 --port 8000
```

### API Usage

```bash
# Health check
curl http://localhost:8000/healthz

# Get recommendations
curl -X POST http://localhost:8000/v1/flybot/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "test-123",
    "origin": "SEA",
    "destination": "ANC",
    "return_window": {
      "earliest": "2026-02-08T08:00:00",
      "latest": "2026-02-08T18:00:00",
      "return_flex_minutes": 60
    },
    "travelers": [
      {"age_bucket": "adult"},
      {"age_bucket": "child"}
    ]
  }'
```

## Project Status

✅ **Phase 0 Complete** - Testing harness & scaffolding  
✅ **Phase 1 Complete** - Core scoring engine (69 unit tests)  
✅ **Phase 2 Complete** - API contracts & integration (15 tests)

**Total: 84 tests passing**

## Architecture

- [src/flybot/scoring.py](src/flybot/scoring.py) - Pure scoring functions (deterministic, testable)
- [src/flybot/service.py](src/flybot/service.py) - Business logic orchestration
- [src/flybot/api.py](src/flybot/api.py) - FastAPI application
- [src/flybot/schemas.py](src/flybot/schemas.py) - Request/response contracts
- [src/flybot/clients.py](src/flybot/clients.py) - Dependency adapters
- [src/flybot/baseline.py](src/flybot/baseline.py) - Fallback heuristic model

## Key Features

### Deterministic Scoring
All scoring logic is pure and deterministic:
- `trip_score = return_success_probability * (0.7 + 0.3 * outbound_margin_bonus)`
- `return_success_probability = 1 - ∏(1 - p_i)` over eligible return flights  
- Tie-breaking: return probability → seat margin → departure time

### Explainability
Every recommendation includes:
- `score_breakdown` with formula and all components
- Stable `reason_codes` (machine-readable, testable)
- User-facing `explanations` (can evolve)

### Fallback Behavior
- ML unavailable → baseline heuristic model
- Empties missing → reduced outbound confidence  
- Schedule down → degraded service with `fallback_used=true`

## Testing

```bash
# Unit tests (69 tests - core scoring functions)
uv run pytest tests/unit/ -v

# Contract tests (10 tests - schema validation)
uv run pytest tests/contract/ -v

# Integration tests (5 tests - API endpoints)
uv run pytest tests/integration/ -v

# All tests
uv run pytest -v
```

## Documentation

- [PRD_SPEC.md](specs/PRD_SPEC.md) - Product requirements and success metrics
- [DESIGN_DOC.md](specs/DESIGN_DOC.md) - System architecture and design  
- [DATA_SCHEMA.md](specs/DATA_SCHEMA.md) - API and data contracts
- [TASK_LIST.md](specs/TASK_LIST.md) - Implementation task breakdown
- [AGENTS.md](AGENTS.md) - Development workflow rules for AI assistants

## Development Workflow

See [AGENTS.md](AGENTS.md) for complete workflow. Key principles:

1. **Spec-driven**: All changes trace to specs with acceptance criteria
2. **TDD**: Write tests first (Red → Green → Refactor)
3. **Deterministic**: Scoring functions are pure and reproducible
4. **Explicit**: Include score breakdown and reason codes
5. **Safe**: Fallback behavior for all dependencies

## Next Steps

See [TASK_LIST.md](specs/TASK_LIST.md) for remaining phases:

- **Phase 3**: Baseline heuristic + evaluation
- **Phase 4**: Observability (logging, metrics)
- **Phase 5**: ML pipeline (training, calibration)
- **Phase 6**: Rollout mechanics (shadow mode, kill switch)
- **Phase 7**: Performance & hardening
