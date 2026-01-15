"""Contract tests for API request/response schemas.

AC-Contract-1: Valid requests parse successfully.
AC-Contract-2: Invalid requests fail with expected error messages.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from flybot.schemas import (
    AgeBucket,
    Constraints,
    FlybotRecommendRequest,
    ReturnWindow,
    TravelerInput,
)


def test_valid_request_minimal():
    """AC-Contract-1: Minimal valid request parses successfully."""
    data = {
        "request_id": "req123",
        "origin": "SEA",
        "destination": "ANC",
        "return_window": {
            "earliest": "2026-02-08T08:00:00",
            "latest": "2026-02-08T18:00:00",
            "return_flex_minutes": 0,
        },
        "travelers": [{"age_bucket": "adult"}],
    }
    req = FlybotRecommendRequest.model_validate(data)
    assert req.request_id == "req123"
    assert req.origin == "SEA"
    assert req.destination == "ANC"
    assert req.lookahead_minutes == 60  # default
    assert len(req.travelers) == 1
    assert req.travelers[0].age_bucket == AgeBucket.ADULT


def test_valid_request_full():
    """AC-Contract-1: Full valid request with all optional fields."""
    data = {
        "request_id": "req456",
        "origin": "PDX",
        "destination": "LAX",
        "lookahead_minutes": 90,
        "return_window": {
            "earliest": "2026-02-10T10:00:00",
            "latest": "2026-02-10T20:00:00",
            "return_flex_minutes": 120,
        },
        "travelers": [
            {"age_bucket": "adult"},
            {"age_bucket": "child"},
            {"age_bucket": "infant"},
        ],
        "constraints": {
            "nonstop_only": True,
            "max_connections": 0,
            "cabin_preference": "economy",
        },
    }
    req = FlybotRecommendRequest.model_validate(data)
    assert req.lookahead_minutes == 90
    assert len(req.travelers) == 3
    assert req.constraints.nonstop_only is True


def test_invalid_request_missing_required_field():
    """AC-Contract-2: Missing required field fails validation."""
    data = {
        "request_id": "req789",
        "origin": "SEA",
        # Missing destination
        "return_window": {
            "earliest": "2026-02-08T08:00:00",
            "latest": "2026-02-08T18:00:00",
            "return_flex_minutes": 0,
        },
        "travelers": [{"age_bucket": "adult"}],
    }
    with pytest.raises(ValidationError) as exc_info:
        FlybotRecommendRequest.model_validate(data)
    
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("destination",) for e in errors)


def test_invalid_request_wrong_iata_code_length():
    """AC-Contract-2: IATA code must be 3 characters."""
    data = {
        "request_id": "req101",
        "origin": "SEATTLE",  # Too long
        "destination": "ANC",
        "return_window": {
            "earliest": "2026-02-08T08:00:00",
            "latest": "2026-02-08T18:00:00",
            "return_flex_minutes": 0,
        },
        "travelers": [{"age_bucket": "adult"}],
    }
    with pytest.raises(ValidationError) as exc_info:
        FlybotRecommendRequest.model_validate(data)
    
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("origin",) for e in errors)


def test_invalid_request_negative_lookahead():
    """AC-Contract-2: lookahead_minutes must be positive."""
    data = {
        "request_id": "req102",
        "origin": "SEA",
        "destination": "ANC",
        "lookahead_minutes": -10,
        "return_window": {
            "earliest": "2026-02-08T08:00:00",
            "latest": "2026-02-08T18:00:00",
            "return_flex_minutes": 0,
        },
        "travelers": [{"age_bucket": "adult"}],
    }
    with pytest.raises(ValidationError) as exc_info:
        FlybotRecommendRequest.model_validate(data)
    
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("lookahead_minutes",) for e in errors)


def test_invalid_request_return_window_inverted():
    """AC-Contract-2: Return window earliest must be before latest."""
    data = {
        "request_id": "req103",
        "origin": "SEA",
        "destination": "ANC",
        "return_window": {
            "earliest": "2026-02-08T18:00:00",
            "latest": "2026-02-08T08:00:00",  # Before earliest
            "return_flex_minutes": 0,
        },
        "travelers": [{"age_bucket": "adult"}],
    }
    with pytest.raises(ValidationError) as exc_info:
        FlybotRecommendRequest.model_validate(data)
    
    errors = exc_info.value.errors()
    assert any("latest" in str(e["loc"]) for e in errors)


def test_invalid_request_negative_flex():
    """AC-Contract-2: return_flex_minutes cannot be negative."""
    data = {
        "request_id": "req104",
        "origin": "SEA",
        "destination": "ANC",
        "return_window": {
            "earliest": "2026-02-08T08:00:00",
            "latest": "2026-02-08T18:00:00",
            "return_flex_minutes": -30,
        },
        "travelers": [{"age_bucket": "adult"}],
    }
    with pytest.raises(ValidationError) as exc_info:
        FlybotRecommendRequest.model_validate(data)
    
    errors = exc_info.value.errors()
    assert any("return_flex_minutes" in str(e["loc"]) for e in errors)


def test_invalid_request_empty_travelers():
    """AC-Contract-2: travelers list cannot be empty."""
    data = {
        "request_id": "req105",
        "origin": "SEA",
        "destination": "ANC",
        "return_window": {
            "earliest": "2026-02-08T08:00:00",
            "latest": "2026-02-08T18:00:00",
            "return_flex_minutes": 0,
        },
        "travelers": [],  # Empty
    }
    with pytest.raises(ValidationError) as exc_info:
        FlybotRecommendRequest.model_validate(data)
    
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("travelers",) for e in errors)


def test_invalid_request_bad_age_bucket():
    """AC-Contract-2: age_bucket must be valid enum value."""
    data = {
        "request_id": "req106",
        "origin": "SEA",
        "destination": "ANC",
        "return_window": {
            "earliest": "2026-02-08T08:00:00",
            "latest": "2026-02-08T18:00:00",
            "return_flex_minutes": 0,
        },
        "travelers": [{"age_bucket": "teenager"}],  # Invalid
    }
    with pytest.raises(ValidationError) as exc_info:
        FlybotRecommendRequest.model_validate(data)
    
    errors = exc_info.value.errors()
    assert any("age_bucket" in str(e["loc"]) for e in errors)


def test_valid_constraints_defaults():
    """AC-Contract-1: Constraints have sensible defaults."""
    c = Constraints()
    assert c.nonstop_only is False
    assert c.max_connections == 1
    assert c.cabin_preference is None
