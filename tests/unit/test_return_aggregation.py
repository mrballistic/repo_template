"""Unit tests for return success probability aggregation.

AC-4: Test 1 - ∏(1 - p_i) for known vectors, empty list edge case.
"""

from __future__ import annotations

import math

from flybot.scoring import aggregate_return_success_probability


def test_aggregate_single_probability_zero():
    """AC-4: Single p=0 → success=0."""
    assert aggregate_return_success_probability([0.0]) == 0.0


def test_aggregate_single_probability_one():
    """AC-4: Single p=1 → success=1."""
    assert aggregate_return_success_probability([1.0]) == 1.0


def test_aggregate_single_probability_half():
    """AC-4: Single p=0.5 → success=0.5."""
    assert aggregate_return_success_probability([0.5]) == 0.5


def test_aggregate_two_independent_half():
    """AC-4: Two p=0.5 → success = 1 - (0.5 * 0.5) = 0.75."""
    result = aggregate_return_success_probability([0.5, 0.5])
    assert math.isclose(result, 0.75, abs_tol=1e-9)


def test_aggregate_two_different_probabilities():
    """AC-4: p=[0.3, 0.4] → success = 1 - (0.7 * 0.6) = 0.58."""
    result = aggregate_return_success_probability([0.3, 0.4])
    expected = 1 - (0.7 * 0.6)
    assert math.isclose(result, expected, abs_tol=1e-9)


def test_aggregate_three_probabilities():
    """AC-4: p=[0.2, 0.3, 0.5] → success = 1 - (0.8 * 0.7 * 0.5) = 0.72."""
    result = aggregate_return_success_probability([0.2, 0.3, 0.5])
    expected = 1 - (0.8 * 0.7 * 0.5)
    assert math.isclose(result, expected, abs_tol=1e-9)


def test_aggregate_all_zeros():
    """AC-4: All p=0 → success=0."""
    result = aggregate_return_success_probability([0.0, 0.0, 0.0])
    assert result == 0.0


def test_aggregate_one_certain_option():
    """AC-4: One p=1.0 among others → success=1."""
    result = aggregate_return_success_probability([0.3, 1.0, 0.2])
    assert math.isclose(result, 1.0, abs_tol=1e-9)


def test_aggregate_empty_list():
    """AC-4: Empty list edge case → success=0 (no options)."""
    result = aggregate_return_success_probability([])
    assert result == 0.0


def test_aggregate_many_small_probabilities():
    """AC-4: Many small probabilities compound."""
    # 10 flights each with p=0.1
    # success = 1 - (0.9)^10 ≈ 0.6513
    result = aggregate_return_success_probability([0.1] * 10)
    expected = 1 - (0.9**10)
    assert math.isclose(result, expected, abs_tol=1e-9)


def test_aggregate_deterministic():
    """AC-4: Same input produces same output."""
    probs = [0.25, 0.35, 0.45]
    result1 = aggregate_return_success_probability(probs)
    result2 = aggregate_return_success_probability(probs)
    assert result1 == result2
