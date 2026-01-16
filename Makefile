SHELL := /bin/bash

.PHONY: install sync test lint format run run-demo run-demo-bg stop-demo demo-health demo-request

install:
	uv sync --group dev

sync:
	uv sync --group dev

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

# Run API (non-demo)
run:
	uv run uvicorn flybot.api:app --reload --log-level info

# Run API with deterministic demo data (override with `make run-demo DEMO_SEED=1 DEMO_OUTBOUND=500 ...`)
DEMO_SEED ?= 42
DEMO_OUTBOUND ?= 500
DEMO_RETURN ?= 1200
DEMO_NOW_ISO ?= 2026-01-15T10:00:00

run-demo:
	@echo "Starting Fly Bot demo server on http://127.0.0.1:8000 (leave this running; use a second terminal for requests)"
	FLYBOT_DEMO_DATA=1 \
	FLYBOT_DEMO_SEED=$(DEMO_SEED) \
	FLYBOT_DEMO_OUTBOUND_COUNT=$(DEMO_OUTBOUND) \
	FLYBOT_DEMO_RETURN_COUNT=$(DEMO_RETURN) \
	FLYBOT_DEMO_NOW_ISO='$(DEMO_NOW_ISO)' \
	uv run uvicorn flybot.api:app --reload --log-level info

# Start demo server in the background and write a pid file + log
run-demo-bg:
	@echo "Starting Fly Bot demo server in background..."
	@rm -f .demo_server.pid .demo_server.log
	@bash -lc "FLYBOT_DEMO_DATA=1 FLYBOT_DEMO_SEED=$(DEMO_SEED) FLYBOT_DEMO_OUTBOUND_COUNT=$(DEMO_OUTBOUND) FLYBOT_DEMO_RETURN_COUNT=$(DEMO_RETURN) FLYBOT_DEMO_NOW_ISO='$(DEMO_NOW_ISO)' nohup uv run uvicorn flybot.api:app --log-level info --port 8000 > .demo_server.log 2>&1 & echo \$$! > .demo_server.pid"
	@echo "PID: $$(cat .demo_server.pid)"
	@echo "Logs: tail -f .demo_server.log"

stop-demo:
	@if [ -f .demo_server.pid ]; then \
		kill "$$(cat .demo_server.pid)" && rm -f .demo_server.pid && echo "Stopped demo server"; \
	else \
		echo "No .demo_server.pid found"; \
	fi

demo-health:
	@curl -sS -f http://127.0.0.1:8000/healthz && echo

# Convenience request against a locally running server (requires jq)
demo-request:
	@bash -lc "set -euo pipefail; curl -sS -f -X POST http://127.0.0.1:8000/v1/flybot/recommend \
		-H 'content-type: application/json' \
		-d '{\"request_id\":\"play-pdx-sfo-001\",\"origin\":\"PDX\",\"destination\":\"SFO\",\"lookahead_minutes\":90,\"return_window\":{\"earliest\":\"2026-01-15T18:00:00\",\"latest\":\"2026-01-15T23:00:00\",\"return_flex_minutes\":60},\"travelers\":[{\"age_bucket\":\"adult\"}]}' \
	| jq '.recommendations[0]'"
