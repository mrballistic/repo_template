# Fly Bot - Standby Travel Recommender

Internal Alaska Airlines tool for recommending standby travel options based on real-time seat availability and return probability predictions.

## 🎯 What We've Built

**Full-stack standby travel recommender** with:
- ✅ **FastAPI backend** with demo data mode
- ✅ **React + TypeScript frontend** with dark mode UI
- ✅ **Baseline probability model** (heuristic, ready for ML upgrade)
- ✅ **Deterministic scoring engine** with explainability
- ✅ **Structured logging & metrics** for observability
- ✅ **131 passing backend tests** + 6 frontend tests
- ✅ **Spec-driven development** with acceptance criteria

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- uv package manager

### Run the Full Stack

```bash
# 1. Start the API server in demo mode
make run-demo-bg
make demo-health  # Verify it's running

# 2. Start the frontend (in a new terminal)
cd frontend
npm install
npm run dev
```

Visit:
- 🎨 **Frontend:** http://localhost:3001
- 🔧 **API Docs:** http://localhost:8000/docs
- 📊 **Metrics:** http://localhost:8000/metrics

### Example API Request

```bash
make demo-request  # Pre-configured PDX→SFO search
```

Or manually:
```bash
curl -X POST http://localhost:8000/v1/flybot/recommend \
  -H 'Content-Type: application/json' \
  -d '{
    "request_id": "test-001",
    "origin": "PDX",
    "destination": "SFO",
    "lookahead_minutes": 90,
    "return_window": {
      "earliest": "2026-01-15T18:00:00",
      "latest": "2026-01-15T23:00:00",
      "return_flex_minutes": 60
    },
    "travelers": [{"age_bucket": "adult"}]
  }'
```

## 📁 Repository Structure

```
├── specs/                    # Feature specs with acceptance criteria
│   ├── PRD_SPEC.md          # Product requirements
│   ├── DESIGN_DOC.md        # System design
│   ├── DATA_SCHEMA.md       # API contracts
│   └── 001-dev_demo_data_mode.md
├── src/flybot/              # Backend Python code
│   ├── api.py               # FastAPI app with CORS
│   ├── service.py           # Business logic
│   ├── scoring.py           # Deterministic scoring engine
│   ├── baseline.py          # Heuristic probability model
│   ├── logging.py           # Structured prediction logging
│   ├── metrics.py           # In-memory metrics collector
│   └── devdata.py           # Demo data generators
├── frontend/                # React + TypeScript UI
│   ├── src/
│   │   ├── components/      # SearchForm, ResultCard, etc.
│   │   ├── api/             # TanStack Query hooks
│   │   └── types/           # TypeScript types (from DATA_SCHEMA)
│   └── tests/               # Frontend component tests
├── tests/                   # Backend tests (131 passing)
│   ├── unit/                # Pure function tests
│   └── integration/         # API + service tests
├── eval/                    # Offline evaluation framework
└── pipelines/               # Dataset building & training (future)
```

## 🧪 Development Workflow

### Backend Development
```bash
# Install dependencies
uv sync

# Run tests (131 tests)
uv run pytest -v

# Lint
uv run ruff check .

# Run server locally
make run-demo
```

### Frontend Development
```bash
cd frontend

# Run tests (6 tests)
npm test

# Lint
npm run lint

# Build for production
npm run build
```

## 📊 Current Implementation Status

### ✅ Phase 0-4 Complete
- [x] Project scaffolding
- [x] Core scoring engine (deterministic, explainable)
- [x] API contracts + integration tests
- [x] Baseline evaluation framework
- [x] Observability (logging + metrics)
- [x] Demo data mode
- [x] React frontend with dark mode

### 🔄 In Progress
- [ ] ML pipeline (feature engineering, training, calibration)
- [ ] Rollout mechanics (shadow mode, kill switch)
- [ ] Performance testing (load tests, chaos tests)

## 🎨 Frontend Features

**Modern dark mode UI** with:
- Glass morphism cards with backdrop blur
- Gradient backgrounds and animations
- Responsive design (mobile-friendly)
- Real-time search with loading states
- Expandable details showing:
  - Score breakdown (return probability, margin bonus, trip score)
  - Reason codes (machine-readable)
  - Individual return flight probabilities
- Error handling with retry

**Tech Stack:**
- React 19 + TypeScript 5.9 (strict mode)
- Vite 7 (fast HMR)
- TanStack Query 5 (API state management)
- Tailwind CSS 4 (utility-first styling)
- Vitest 4 + Testing Library

## 📖 Key Documentation

- **[AGENTS.md](AGENTS.md)** — Rules for AI assistants and human developers
- **[specs/PRD_SPEC.md](specs/PRD_SPEC.md)** — Product requirements
- **[specs/DESIGN_DOC.md](specs/DESIGN_DOC.md)** — System architecture
- **[specs/DATA_SCHEMA.md](specs/DATA_SCHEMA.md)** — API contracts
- **[frontend/README.md](frontend/README.md)** — Frontend-specific docs

## 🔧 Makefile Targets

```bash
make run-demo         # Start API in foreground (demo mode)
make run-demo-bg      # Start API in background
make stop-demo        # Stop background API
make demo-health      # Check API health
make demo-request     # Test PDX→SFO search
```

## 🧠 AI Development Notes

This project follows **spec-driven TDD**:
1. Write specs with testable acceptance criteria (AC-*)
2. Write failing tests that enforce the ACs
3. Implement minimum code to pass tests
4. Refactor while keeping tests green

**AI Assistant Instructions:** See [AGENTS.md](AGENTS.md) for detailed rules on:
- When to write tests first
- How to handle secrets and PII
- Determinism requirements
- Explainability requirements

## 📈 Testing & Quality

- **131 backend tests** covering scoring, API, observability, demo mode
- **6 frontend tests** for API client (error handling, timeouts, types)
- **Zero lint errors** (ruff for Python, ESLint for TypeScript)
- **Strict TypeScript** with no `any` types
- **Contract tests** ensure API matches DATA_SCHEMA.md

## 🚢 Deployment (Future)

Backend:
- Package as container with FastAPI + uvicorn
- Deploy to Kubernetes/Cloud Run
- Enable real empties and schedule clients
- Configure structured logging to BigQuery/DataDog

Frontend:
- Build static assets: `npm run build`
- Deploy to Vercel/Netlify/CloudFront
- Point to production API URL via env vars

## 📝 License

MIT

---

**Built with spec-driven TDD + AI-assisted development**  
See [docs/compounding_engineering.md](docs/compounding_engineering.md) for how we turned PR feedback into automated gates.
