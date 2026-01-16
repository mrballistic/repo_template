"""Integration tests for dev demo data mode.

AC-DEMOMODE-1: With FLYBOT_DEMO_DATA=1, API returns non-empty recommendations.
AC-DEMOMODE-2: With fixed seed + now, top recommendation is stable.
"""

from __future__ import annotations

import importlib

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_demo_mode_returns_recommendations(monkeypatch):
    """AC-DEMOMODE-1"""
    monkeypatch.setenv("FLYBOT_DEMO_DATA", "1")
    monkeypatch.setenv("FLYBOT_DEMO_SEED", "7")
    monkeypatch.setenv("FLYBOT_DEMO_OUTBOUND_COUNT", "250")
    monkeypatch.setenv("FLYBOT_DEMO_RETURN_COUNT", "600")
    monkeypatch.setenv("FLYBOT_DEMO_NOW_ISO", "2026-01-15T10:00:00")

    # Reload module so lifespan reads env vars.
    import flybot.api as api_module

    importlib.reload(api_module)
    app = api_module.app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/v1/flybot/recommend",
            json={
                "request_id": "demo-001",
                "origin": "SEA",
                "destination": "ANC",
                "lookahead_minutes": 60,
                "return_window": {
                    "earliest": "2026-01-15T18:00:00",
                    "latest": "2026-01-15T23:00:00",
                    "return_flex_minutes": 60,
                },
                "travelers": [{"age_bucket": "adult"}],
            },
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["request_id"] == "demo-001"
        assert len(data["recommendations"]) > 0


@pytest.mark.asyncio
async def test_demo_mode_is_deterministic(monkeypatch):
    """AC-DEMOMODE-2"""
    monkeypatch.setenv("FLYBOT_DEMO_DATA", "1")
    monkeypatch.setenv("FLYBOT_DEMO_SEED", "42")
    monkeypatch.setenv("FLYBOT_DEMO_OUTBOUND_COUNT", "200")
    monkeypatch.setenv("FLYBOT_DEMO_RETURN_COUNT", "500")
    monkeypatch.setenv("FLYBOT_DEMO_NOW_ISO", "2026-01-15T10:00:00")

    import flybot.api as api_module

    importlib.reload(api_module)
    app = api_module.app

    request_json = {
        "request_id": "demo-002",
        "origin": "SEA",
        "destination": "ANC",
        "lookahead_minutes": 60,
        "return_window": {
            "earliest": "2026-01-15T18:00:00",
            "latest": "2026-01-15T23:00:00",
            "return_flex_minutes": 60,
        },
        "travelers": [{"age_bucket": "adult"}],
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r1 = await client.post("/v1/flybot/recommend", json=request_json)
        r2 = await client.post("/v1/flybot/recommend", json=request_json)

        assert r1.status_code == 200
        assert r2.status_code == 200

        top1 = r1.json()["recommendations"][0]["outbound"]["flight_number"]
        top2 = r2.json()["recommendations"][0]["outbound"]["flight_number"]
        assert top1 == top2
