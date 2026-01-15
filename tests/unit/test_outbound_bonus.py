"""Unit tests for outbound margin bonus computation.

AC-5: Test sigmoid(seat_margin/2), monotonicity.
"""

from __future__ import annotations

import math

import pytest

from flybot.scoring import compute_outbound_margin_bonus


def test_outbound_bonus_zero_margin():
    """AC-5: seat_margin=0 → sigmoid(0) = 0.5."""
    result = compute_outbound_margin_bonus(0)
    assert math.isclose(result, 0.5, abs_tol=1e-9)


def test_outbound_bonus_positive_margin():
    """AC-5: seat_margin=2 → sigmoid(1) ≈ 0.7311."""
    result = compute_outbound_margin_bonus(2)
    expected = 1 / (1 + math.exp(-1))
    assert math.isclose(result, expected, abs_tol=1e-4)


def test_outbound_bonus_large_positive_margin():
    """AC-5: Large positive margin → approaches 1.0."""
    result = compute_outbound_margin_bonus(20)
    assert result > 0.99


def test_outbound_bonus_negative_margin():
    """AC-5: seat_margin=-2 → sigmoid(-1) ≈ 0.2689."""
    result = compute_outbound_margin_bonus(-2)
    expected = 1 / (1 + math.exp(1))
    assert math.isclose(result, expected, abs_tol=1e-4)


def test_outbound_bonus_large_negative_margin():
    """AC-5: Large negative margin → approaches 0.0."""
    result = compute_outbound_margin_bonus(-20)
    assert result < 0.01


def test_outbound_bonus_monotonicity():
    """AC-5: Bonus increases monotonically with seat_margin."""
    margins = [-10, -5, -2, 0, 2, 5, 10]
    bonuses = [compute_outbound_margin_bonus(m) for m in margins]
    
    # Check that each bonus is greater than the previous
    for i in range(1, len(bonuses)):
        assert bonuses[i] > bonuses[i - 1], f"Monotonicity violated at index {i}"


def test_outbound_bonus_symmetric_around_zero():
    """AC-5: sigmoid is symmetric: sigmoid(-x) = 1 - sigmoid(x)."""
    margin = 4
    bonus_pos = compute_outbound_margin_bonus(margin)
    bonus_neg = compute_outbound_margin_bonus(-margin)
    assert math.isclose(bonus_pos + bonus_neg, 1.0, abs_tol=1e-9)


def test_outbound_bonus_deterministic():
    """AC-5: Same input produces same output."""
    margin = 3
    result1 = compute_outbound_margin_bonus(margin)
    result2 = compute_outbound_margin_bonus(margin)
    assert result1 == result2
