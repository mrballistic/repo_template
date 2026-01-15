"""Pydantic schemas for Fly Bot API.

Based on DATA_SCHEMA.md specification.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class AgeBucket(str, Enum):
    """Age bucket for travelers."""

    INFANT = "infant"
    CHILD = "child"
    ADULT = "adult"


class TravelerInput(BaseModel):
    """Traveler in request."""

    age_bucket: AgeBucket


class ReturnWindow(BaseModel):
    """Return window constraints."""

    earliest: datetime
    latest: datetime
    return_flex_minutes: int = Field(ge=0, description="0 = hard deadline")

    @field_validator("latest")
    @classmethod
    def validate_window(cls, latest: datetime, info) -> datetime:
        """Ensure latest >= earliest."""
        if "earliest" in info.data:
            earliest = info.data["earliest"]
            if latest < earliest:
                raise ValueError("latest must be >= earliest")
        return latest


class Constraints(BaseModel):
    """Optional flight constraints."""

    nonstop_only: bool = False
    max_connections: int = 1
    cabin_preference: str | None = None


class FlybotRecommendRequest(BaseModel):
    """Request schema for /v1/flybot/recommend."""

    request_id: str
    origin: str = Field(min_length=3, max_length=3, description="IATA code")
    destination: str = Field(min_length=3, max_length=3, description="IATA code")
    lookahead_minutes: int = Field(default=60, ge=1, le=180)
    return_window: ReturnWindow
    travelers: list[TravelerInput] = Field(min_length=1)
    constraints: Constraints = Field(default_factory=Constraints)


class OutboundFlight(BaseModel):
    """Outbound flight details in response."""

    flight_number: str
    departure: datetime
    arrival: datetime
    open_seats_now: int | None = None
    seat_margin: int


class ReturnFlightOption(BaseModel):
    """Return flight option with probability."""

    flight_number: str
    departure: datetime
    arrival: datetime
    clearance_probability: float = Field(ge=0.0, le=1.0)


class ScoreBreakdown(BaseModel):
    """Explicit score breakdown for transparency."""

    formula: str
    return_success_probability: float
    outbound_margin_bonus: float
    return_weight: float = 0.7
    outbound_weight: float = 0.3
    trip_score: float


class Recommendation(BaseModel):
    """Single trip recommendation."""

    trip_score: float = Field(ge=0.0, le=1.0)
    score_breakdown: ScoreBreakdown
    outbound: OutboundFlight
    return_options: list[ReturnFlightOption]
    explanations: list[str]
    reason_codes: list[str]


class TimingMs(BaseModel):
    """Step-by-step timing breakdown."""

    total: int
    validation: int | None = None
    fetch_outbound: int | None = None
    fetch_return: int | None = None
    scoring: int | None = None


class FlybotRecommendResponse(BaseModel):
    """Response schema for /v1/flybot/recommend."""

    request_id: str
    model_version: str
    generated_at: datetime
    seats_required: int
    required_return_buffer_minutes: int
    recommendations: list[Recommendation]
    fallback_used: bool
    timing_ms: TimingMs
