"""Unit tests for trip score computation.

AC-6: Test trip_score = return_prob * (0.7 + 0.3*outbound_bonus).
"""

from __future__ import annotations

import math

import pytest

from flybot.scoring import compute_trip_score


def test_trip_score_perfect_return_perfect_outbound():
    """AC-6: return=1.0, bonus=1.0 → score = 1.0 * (0.7 + 0.3*1.0) = 1.0."""
    result = compute_trip_score(
        return_success_probability=1.0,
        outbound_margin_bonus=1.0,
    )
    assert math.isclose(result, 1.0, abs_tol=1e-9)


def test_trip_score_perfect_return_zero_outbound():
    """AC-6: return=1.0, bonus=0.0 → score = 1.0 * (0.7 + 0.3*0.0) = 0.7."""
    result = compute_trip_score(
        return_success_probability=1.0,
        outbound_margin_bonus=0.0,
    )
    assert math.isclose(result, 0.7, abs_tol=1e-9)


def test_trip_score_zero_return():
    """AC-6: return=0.0 → score = 0.0 regardless of outbound."""
    result = compute_trip_score(
        return_success_probability=0.0,
        outbound_margin_bonus=1.0,
    )
    assert result == 0.0


def test_trip_score_medium_return_medium_outbound():
    """AC-6: return=0.5, bonus=0.5 → score = 0.5 * (0.7 + 0.3*0.5) = 0.425."""
    result = compute_trip_score(
        return_success_probability=0.5,
        outbound_margin_bonus=0.5,
    )
    expected = 0.5 * (0.7 + 0.3 * 0.5)
    assert math.isclose(result, expected, abs_tol=1e-9)


def test_trip_score_high_return_low_outbound():
    """AC-6: return=0.8, bonus=0.2 → score = 0.8 * (0.7 + 0.3*0.2) = 0.608."""
    result = compute_trip_score(
        return_success_probability=0.8,
        outbound_margin_bonus=0.2,
    )
    expected = 0.8 * (0.7 + 0.3 * 0.2)
    assert math.isclose(result, expected, abs_tol=1e-9)


def test_trip_score_custom_weights():
    """AC-6: Custom weights alter formula correctly."""
    result = compute_trip_score(
        return_success_probability=0.6,
        outbound_margin_bonus=0.4,
        return_weight=0.8,
        outbound_weight=0.2,
    )
    expected = 0.6 * (0.8 + 0.2 * 0.4)
    assert math.isclose(result, expected, abs_tol=1e-9)


def test_trip_score_weights_sum_to_one():
    """AC-6: Default weights sum to 1.0."""
    # With bonus=1.0, coefficient should be exactly 1.0
    result = compute_trip_score(
        return_success_probability=1.0,
        outbound_margin_bonus=1.0,
        return_weight=0.7,
        outbound_weight=0.3,
    )
    assert math.isclose(result, 1.0, abs_tol=1e-9)


def test_trip_score_deterministic():
    """AC-6: Same inputs produce same output."""
    result1 = compute_trip_score(
        return_success_probability=0.65,
        outbound_margin_bonus=0.55,
    )
    result2 = compute_trip_score(
        return_success_probability=0.65,
        outbound_margin_bonus=0.55,
    )
    assert result1 == result2


def test_trip_score_return_dominates():
    """AC-6: Return probability dominates (weight=0.7 vs 0.3)."""
    # Same bonus, different returns → large impact
    score_low_return = compute_trip_score(
        return_success_probability=0.3,
        outbound_margin_bonus=0.9,
    )
    score_high_return = compute_trip_score(
        return_success_probability=0.9,
        outbound_margin_bonus=0.3,
    )
    # High return should score better despite worse outbound
    assert score_high_return > score_low_return
