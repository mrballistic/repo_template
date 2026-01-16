"""FastAPI application for Fly Bot."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from flybot.clients import MockEmptiesClient, MockScheduleClient
from flybot.devdata import make_demo_clients
from flybot.metrics import get_metrics_summary, record_error
from flybot.schemas import FlybotRecommendRequest, FlybotRecommendResponse
from flybot.service import recommend

# Global dependency clients (in production, these would be real clients)
empties_client = MockEmptiesClient()
schedule_client = MockScheduleClient()


def _maybe_enable_demo_mode() -> None:
    """Swap mock clients for generated demo clients when env-gated.

    Kept at module scope so it works even when ASGI lifespan hooks
    are not executed (e.g., some test transports).
    """
    global empties_client, schedule_client
    if os.getenv("FLYBOT_DEMO_DATA") in {"1", "true", "True", "yes", "YES"}:
        seed = int(os.getenv("FLYBOT_DEMO_SEED", "0"))
        outbound_count = int(os.getenv("FLYBOT_DEMO_OUTBOUND_COUNT", "200"))
        return_count = int(os.getenv("FLYBOT_DEMO_RETURN_COUNT", "400"))
        empties_client, schedule_client = make_demo_clients(
            seed=seed,
            outbound_count=outbound_count,
            return_count=return_count,
        )


_maybe_enable_demo_mode()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the app."""
    # Startup
    print("Fly Bot API starting up...")

    # Dev-only demo mode: swap mock clients for generated data.
    _maybe_enable_demo_mode()
    yield
    # Shutdown
    print("Fly Bot API shutting down...")


app = FastAPI(
    title="Fly Bot API",
    description="Internal Alaska standby travel recommender",
    version="0.1.0",
    lifespan=lifespan,
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def healthcheck():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/readyz")
async def readiness():
    """Readiness check endpoint."""
    # In production, check if ML model is loaded when required
    return {"status": "ready", "model_loaded": False}


@app.get("/metrics")
async def metrics():
    """Metrics endpoint for observability."""
    return get_metrics_summary()


@app.post("/v1/flybot/recommend", response_model=FlybotRecommendResponse)
async def recommend_endpoint(request: FlybotRecommendRequest):
    """Generate flight recommendations.

    Returns ranked trip options with explicit scoring breakdown.
    """
    try:
        response = await recommend(
            request=request,
            empties_client=empties_client,
            schedule_client=schedule_client,
            model_version="baseline-v1",
            use_ml=False,
        )
        return response
    except Exception as e:
        record_error("recommend_endpoint_error")
        raise HTTPException(status_code=500, detail=str(e)) from None


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    record_error("unhandled_exception")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )
