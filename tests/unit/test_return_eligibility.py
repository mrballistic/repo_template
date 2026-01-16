"""Unit tests for return flight eligibility.

AC-3: Test arrival <= latest-buffer → eligible, boundary cases.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from flybot.scoring import is_return_eligible


def test_return_eligible_well_before_deadline():
    """AC-3: Arrival well before deadline → eligible."""
    latest = datetime(2026, 2, 8, 18, 0)
    arrival = datetime(2026, 2, 8, 15, 0)  # 3 hours before
    buffer_minutes = 120
    assert is_return_eligible(arrival, latest, buffer_minutes) is True


def test_return_eligible_exactly_at_buffered_deadline():
    """AC-3: Arrival exactly at deadline-buffer → eligible (boundary)."""
    latest = datetime(2026, 2, 8, 18, 0)
    buffer_minutes = 120
    arrival = latest - timedelta(minutes=buffer_minutes)  # Exactly at deadline-120
    assert is_return_eligible(arrival, latest, buffer_minutes) is True


def test_return_not_eligible_after_buffered_deadline():
    """AC-3: Arrival after deadline-buffer → not eligible."""
    latest = datetime(2026, 2, 8, 18, 0)
    buffer_minutes = 120
    arrival = latest - timedelta(minutes=buffer_minutes - 1)  # 1 minute too late
    assert is_return_eligible(arrival, latest, buffer_minutes) is False


def test_return_not_eligible_after_deadline():
    """AC-3: Arrival after deadline → not eligible."""
    latest = datetime(2026, 2, 8, 18, 0)
    arrival = datetime(2026, 2, 8, 19, 0)
    buffer_minutes = 120
    assert is_return_eligible(arrival, latest, buffer_minutes) is False


def test_return_eligible_zero_buffer():
    """AC-3: Zero buffer allows up to exact deadline."""
    latest = datetime(2026, 2, 8, 18, 0)
    arrival = datetime(2026, 2, 8, 18, 0)
    buffer_minutes = 0
    assert is_return_eligible(arrival, latest, buffer_minutes) is True


def test_return_not_eligible_zero_buffer_one_minute_late():
    """AC-3: Zero buffer rejects even 1 minute late."""
    latest = datetime(2026, 2, 8, 18, 0)
    arrival = datetime(2026, 2, 8, 18, 1)
    buffer_minutes = 0
    assert is_return_eligible(arrival, latest, buffer_minutes) is False


def test_return_eligible_large_buffer():
    """AC-3: Large buffer restricts eligibility window."""
    latest = datetime(2026, 2, 8, 18, 0)
    buffer_minutes = 180  # 3 hours
    arrival = datetime(2026, 2, 8, 15, 0)  # Exactly 3 hours before
    assert is_return_eligible(arrival, latest, buffer_minutes) is True

    arrival_too_late = datetime(2026, 2, 8, 15, 1)  # 1 minute too late
    assert is_return_eligible(arrival_too_late, latest, buffer_minutes) is False
