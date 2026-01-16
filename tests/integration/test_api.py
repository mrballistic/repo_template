"""Integration tests for /v1/flybot/recommend endpoint.

AC-Integration-1: Happy path with mocked dependencies returns sorted recommendations.
AC-Integration-2: Empties down/stale triggers fallback behavior.
AC-Integration-3: Schedule dependency down triggers appropriate response.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from flybot.api import app
from flybot.clients import EmptiesSnapshot, Flight, MockEmptiesClient, MockScheduleClient
from flybot.schemas import FlybotRecommendRequest
from flybot.service import recommend


@pytest.mark.asyncio
async def test_recommend_happy_path():
    """AC-Integration-1: Happy path returns sorted recommendations."""
    # Create mock data
    now = datetime(2026, 1, 15, 10, 0)

    # Outbound flights (SEA -> ANC)
    empties = EmptiesSnapshot(
        snapshot_time=now,
        flights=[
            Flight(
                flight_number="AS100",
                origin="SEA",
                destination="ANC",
                departure=now + timedelta(minutes=30),
                arrival=now + timedelta(hours=3, minutes=30),
                open_seats=10,
                capacity=150,
            ),
            Flight(
                flight_number="AS102",
                origin="SEA",
                destination="ANC",
                departure=now + timedelta(minutes=45),
                arrival=now + timedelta(hours=3, minutes=45),
                open_seats=5,
                capacity=120,
            ),
        ],
    )

    # Return flights (ANC -> SEA)
    return_earliest = now + timedelta(hours=8)
    return_latest = now + timedelta(hours=12)

    returns = [
        Flight(
            flight_number="AS201",
            origin="ANC",
            destination="SEA",
            departure=return_earliest + timedelta(hours=1),
            arrival=return_earliest
            + timedelta(hours=2, minutes=30),  # Arrives before deadline-buffer
            capacity=150,
        ),
        Flight(
            flight_number="AS202",
            origin="ANC",
            destination="SEA",
            departure=return_earliest + timedelta(hours=2),
            arrival=return_earliest
            + timedelta(hours=3, minutes=15),  # Arrives before deadline-buffer
            capacity=150,
        ),
    ]

    # Create clients
    empties_client = MockEmptiesClient(snapshot=empties)
    schedule_client = MockScheduleClient(flights=returns)

    # Create request
    request = FlybotRecommendRequest(
        request_id="test-001",
        origin="SEA",
        destination="ANC",
        lookahead_minutes=60,
        return_window={
            "earliest": return_earliest.isoformat(),
            "latest": return_latest.isoformat(),
            "return_flex_minutes": 60,
        },
        travelers=[{"age_bucket": "adult"}, {"age_bucket": "child"}],
    )

    # Execute
    response = await recommend(
        request=request,
        empties_client=empties_client,
        schedule_client=schedule_client,
    )

    # Assertions
    assert response.request_id == "test-001"
    assert response.seats_required == 2
    assert response.required_return_buffer_minutes == 60
    assert len(response.recommendations) == 2
    assert response.fallback_used is True  # baseline model

    # Check sorting (higher score first)
    scores = [r.trip_score for r in response.recommendations]
    assert scores == sorted(scores, reverse=True)

    # Check structure
    rec = response.recommendations[0]
    assert rec.outbound.flight_number in ["AS100", "AS102"]
    assert len(rec.return_options) > 0
    assert len(rec.reason_codes) > 0
    assert len(rec.explanations) > 0
    assert rec.score_breakdown.formula is not None


@pytest.mark.asyncio
async def test_recommend_empties_unavailable():
    """AC-Integration-2: Empties unavailable triggers fallback."""
    now = datetime(2026, 1, 15, 10, 0)

    # Empties client fails
    empties_client = MockEmptiesClient(fail=True)

    # Return flights available
    returns = [
        Flight(
            flight_number="AS201",
            origin="ANC",
            destination="SEA",
            departure=now + timedelta(hours=8),
            arrival=now + timedelta(hours=11),
            capacity=150,
        ),
    ]
    schedule_client = MockScheduleClient(flights=returns)

    request = FlybotRecommendRequest(
        request_id="test-002",
        origin="SEA",
        destination="ANC",
        return_window={
            "earliest": (now + timedelta(hours=6)).isoformat(),
            "latest": (now + timedelta(hours=12)).isoformat(),
            "return_flex_minutes": 0,
        },
        travelers=[{"age_bucket": "adult"}],
    )

    response = await recommend(
        request=request,
        empties_client=empties_client,
        schedule_client=schedule_client,
    )

    # Should complete but with no recommendations (no outbound flights)
    assert response.request_id == "test-002"
    assert response.fallback_used is True
    assert len(response.recommendations) == 0  # No outbound candidates


@pytest.mark.asyncio
async def test_recommend_schedule_unavailable():
    """AC-Integration-3: Schedule unavailable uses fallback."""
    now = datetime(2026, 1, 15, 10, 0)

    # Empties available
    empties = EmptiesSnapshot(
        snapshot_time=now,
        flights=[
            Flight(
                flight_number="AS100",
                origin="SEA",
                destination="ANC",
                departure=now + timedelta(minutes=30),
                arrival=now + timedelta(hours=3, minutes=30),
                open_seats=10,
                capacity=150,
            ),
        ],
    )
    empties_client = MockEmptiesClient(snapshot=empties)

    # Schedule fails
    schedule_client = MockScheduleClient(fail=True)

    request = FlybotRecommendRequest(
        request_id="test-003",
        origin="SEA",
        destination="ANC",
        return_window={
            "earliest": (now + timedelta(hours=6)).isoformat(),
            "latest": (now + timedelta(hours=12)).isoformat(),
            "return_flex_minutes": 0,
        },
        travelers=[{"age_bucket": "adult"}],
    )

    response = await recommend(
        request=request,
        empties_client=empties_client,
        schedule_client=schedule_client,
    )

    # Should complete with degraded service
    assert response.request_id == "test-003"
    assert response.fallback_used is True
    # With no return flights, return prob = 0, so trip_score = 0
    if response.recommendations:
        assert all(r.trip_score == 0.0 for r in response.recommendations)


@pytest.mark.asyncio
async def test_recommend_stale_empties():
    """AC-Integration-2: Stale empties indicated in reason codes."""
    now = datetime(2026, 1, 15, 10, 0)

    # Stale empties
    empties = EmptiesSnapshot(
        snapshot_time=now - timedelta(minutes=30),  # Old snapshot
        flights=[
            Flight(
                flight_number="AS100",
                origin="SEA",
                destination="ANC",
                departure=now + timedelta(minutes=30),
                arrival=now + timedelta(hours=3, minutes=30),
                open_seats=10,
                capacity=150,
            ),
        ],
        is_stale=True,
    )
    empties_client = MockEmptiesClient(snapshot=empties)

    returns = [
        Flight(
            flight_number="AS201",
            origin="ANC",
            destination="SEA",
            departure=now + timedelta(hours=8),
            arrival=now + timedelta(hours=11),
            capacity=150,
        ),
    ]
    schedule_client = MockScheduleClient(flights=returns)

    request = FlybotRecommendRequest(
        request_id="test-004",
        origin="SEA",
        destination="ANC",
        return_window={
            "earliest": (now + timedelta(hours=6)).isoformat(),
            "latest": (now + timedelta(hours=12)).isoformat(),
            "return_flex_minutes": 0,
        },
        travelers=[{"age_bucket": "adult"}],
    )

    response = await recommend(
        request=request,
        empties_client=empties_client,
        schedule_client=schedule_client,
    )

    # Should have STALE_EMPTIES reason code
    if response.recommendations:
        rec = response.recommendations[0]
        assert "STALE_EMPTIES" in rec.reason_codes


@pytest.mark.asyncio
async def test_api_endpoint_integration():
    """AC-Integration-1: Test full API endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/v1/flybot/recommend",
            json={
                "request_id": "api-test-001",
                "origin": "SEA",
                "destination": "ANC",
                "return_window": {
                    "earliest": "2026-02-08T08:00:00",
                    "latest": "2026-02-08T18:00:00",
                    "return_flex_minutes": 60,
                },
                "travelers": [{"age_bucket": "adult"}],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["request_id"] == "api-test-001"
        assert "recommendations" in data
        assert "timing_ms" in data


@pytest.mark.asyncio
async def test_metrics_endpoint_smoke_test():
    """AC-Integration-Observability: Metrics endpoint returns summary."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # First make a request to generate some metrics
        await client.post(
            "/v1/flybot/recommend",
            json={
                "request_id": "metrics-test-001",
                "origin": "SEA",
                "destination": "ANC",
                "return_window": {
                    "earliest": "2026-02-08T08:00:00",
                    "latest": "2026-02-08T18:00:00",
                    "return_flex_minutes": 60,
                },
                "travelers": [{"age_bucket": "adult"}],
            },
        )

        # Now fetch metrics
        metrics_response = await client.get("/metrics")

        assert metrics_response.status_code == 200
        metrics = metrics_response.json()

        # Verify expected metrics structure
        assert "request_latency_ms" in metrics
        assert "errors" in metrics
        assert "dependency_latency_ms" in metrics
        assert "fallback_count" in metrics
        assert "return_coverage" in metrics

        # Verify request was recorded
        assert metrics["request_latency_ms"]["count"] >= 1
        assert metrics["fallback_count"] >= 1  # Baseline always used in tests

        # Verify dependency latencies recorded
        assert "empties" in metrics["dependency_latency_ms"]
        assert "schedule" in metrics["dependency_latency_ms"]
