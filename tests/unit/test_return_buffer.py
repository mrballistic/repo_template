"""Unit tests for return buffer computation.

AC-2: Test flex=0→120, flex=120→0, flex>120 clamps to 0, negative flex cases.
"""

from __future__ import annotations

from flybot.scoring import compute_return_buffer_minutes


def test_buffer_flex_zero():
    """AC-2: flex=0 (hard deadline) → buffer=120 minutes."""
    assert compute_return_buffer_minutes(return_flex_minutes=0) == 120


def test_buffer_flex_sixty():
    """AC-2: flex=60 → buffer=60 minutes."""
    assert compute_return_buffer_minutes(return_flex_minutes=60) == 60


def test_buffer_flex_120():
    """AC-2: flex=120 → buffer=0 minutes."""
    assert compute_return_buffer_minutes(return_flex_minutes=120) == 0


def test_buffer_flex_greater_than_max():
    """AC-2: flex>120 clamps to 0."""
    assert compute_return_buffer_minutes(return_flex_minutes=180) == 0
    assert compute_return_buffer_minutes(return_flex_minutes=200) == 0


def test_buffer_negative_flex():
    """AC-2: negative flex treated as 0 → buffer=120."""
    assert compute_return_buffer_minutes(return_flex_minutes=-10) == 120
    assert compute_return_buffer_minutes(return_flex_minutes=-100) == 120


def test_buffer_custom_max():
    """AC-2: Custom buffer_max_minutes scales correctly."""
    assert compute_return_buffer_minutes(return_flex_minutes=0, buffer_max_minutes=180) == 180
    assert compute_return_buffer_minutes(return_flex_minutes=90, buffer_max_minutes=180) == 90
    assert compute_return_buffer_minutes(return_flex_minutes=180, buffer_max_minutes=180) == 0


def test_buffer_deterministic():
    """AC-2: Same inputs produce same output."""
    result1 = compute_return_buffer_minutes(return_flex_minutes=45)
    result2 = compute_return_buffer_minutes(return_flex_minutes=45)
    assert result1 == result2 == 75
