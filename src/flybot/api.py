"""FastAPI application for Fly Bot."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from flybot.clients import MockEmptiesClient, MockScheduleClient
from flybot.schemas import FlybotRecommendRequest, FlybotRecommendResponse
from flybot.service import recommend


# Global dependency clients (in production, these would be real clients)
empties_client = MockEmptiesClient()
schedule_client = MockScheduleClient()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the app."""
    # Startup
    print("Fly Bot API starting up...")
    yield
    # Shutdown
    print("Fly Bot API shutting down...")


app = FastAPI(
    title="Fly Bot API",
    description="Internal Alaska standby travel recommender",
    version="0.1.0",
    lifespan=lifespan,
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
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )
