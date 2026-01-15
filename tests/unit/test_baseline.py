"""Unit tests for baseline heuristic model.

AC-Baseline-1: Baseline return probabilities are bounded within [0, 1].
AC-Baseline-2: Probabilities decrease as seats_required increases.
AC-Baseline-3: Deterministic for same inputs.
"""

from __future__ import annotations

import pytest

from flybot.baseline import baseline_model_predict, baseline_return_probability


def test_baseline_probability_bounded():
    """AC-Baseline-1: Baseline probability is bounded within [0, 1]."""
    # Test various scenarios
    test_cases = [
        (1, None, None),
        (5, None, None),
        (1, 50, 2.0),
        (10, 200, 10.0),
        (1, None, 0.5),
    ]
    
    for seats_req, capacity, hours in test_cases:
        prob = baseline_return_probability(seats_req, capacity, hours)
        assert 0.0 <= prob <= 1.0, f"Probability {prob} out of bounds for inputs: seats={seats_req}, cap={capacity}, hours={hours}"


def test_baseline_decreases_with_party_size():
    """AC-Baseline-2: Probability decreases as seats_required increases."""
    # Hold other factors constant
    capacity = 150
    hours = 4.0
    
    probs = []
    for seats in range(1, 8):
        prob = baseline_return_probability(seats, capacity, hours)
        probs.append(prob)
    
    # Each probability should be less than or equal to the previous
    for i in range(1, len(probs)):
        assert probs[i] <= probs[i - 1], f"Probability should decrease with party size: {probs}"


def test_baseline_party_penalty_applied():
    """AC-Baseline-2: Larger parties have lower probability."""
    prob_1 = baseline_return_probability(1, 150, 4.0)
    prob_5 = baseline_return_probability(5, 150, 4.0)
    
    assert prob_5 < prob_1, "5-person party should have lower probability than 1-person"
    
    # Verify penalty is reasonable (not too extreme)
    penalty_per_seat = (prob_1 - prob_5) / 4
    assert 0.01 <= penalty_per_seat <= 0.1, "Penalty per additional seat should be reasonable"


def test_baseline_capacity_bonus():
    """AC-Baseline-1: Larger capacity flights get a bonus."""
    prob_small = baseline_return_probability(2, 80, 4.0)
    prob_large = baseline_return_probability(2, 180, 4.0)
    
    # Large capacity should have higher or equal probability
    assert prob_large >= prob_small


def test_baseline_advance_time_bonus():
    """AC-Baseline-1: More advance time increases probability."""
    prob_soon = baseline_return_probability(2, 150, 2.0)
    prob_later = baseline_return_probability(2, 150, 6.0)
    
    # More advance time should have higher or equal probability
    assert prob_later >= prob_soon


def test_baseline_deterministic():
    """AC-Baseline-3: Same inputs produce same output."""
    seats = 3
    capacity = 150
    hours = 5.0
    
    prob1 = baseline_return_probability(seats, capacity, hours)
    prob2 = baseline_return_probability(seats, capacity, hours)
    prob3 = baseline_return_probability(seats, capacity, hours)
    
    assert prob1 == prob2 == prob3, "Baseline should be deterministic"


def test_baseline_extreme_party_size():
    """AC-Baseline-1: Extreme party sizes stay within bounds."""
    # Very large party
    prob_large_party = baseline_return_probability(20, 150, 4.0)
    assert 0.0 <= prob_large_party <= 1.0
    
    # Should be clamped at minimum
    assert prob_large_party >= 0.1, "Probability should not go below 0.1"


def test_baseline_no_optional_params():
    """AC-Baseline-1: Works without optional parameters."""
    prob = baseline_return_probability(2)
    assert 0.0 <= prob <= 1.0


def test_baseline_model_predict_batch():
    """AC-Baseline-3: Batch prediction works correctly."""
    flights = [
        (150, 4.0),
        (80, 2.0),
        (200, 6.0),
        (None, None),
    ]
    seats_required = 2
    
    probs = baseline_model_predict(flights, seats_required)
    
    assert len(probs) == len(flights)
    for prob in probs:
        assert 0.0 <= prob <= 1.0


def test_baseline_model_predict_deterministic():
    """AC-Baseline-3: Batch prediction is deterministic."""
    flights = [
        (150, 4.0),
        (120, 3.0),
        (180, 5.0),
    ]
    seats_required = 3
    
    probs1 = baseline_model_predict(flights, seats_required)
    probs2 = baseline_model_predict(flights, seats_required)
    
    assert probs1 == probs2


def test_baseline_model_predict_empty_list():
    """AC-Baseline-1: Empty flight list returns empty list."""
    probs = baseline_model_predict([], 2)
    assert probs == []


def test_baseline_reasonable_range():
    """AC-Baseline-1: Baseline probabilities stay in reasonable range [0.1, 0.9]."""
    # Test a variety of realistic scenarios
    test_scenarios = [
        (1, 150, 5.0),   # Solo, good capacity, advance notice
        (2, 120, 3.0),   # Couple, medium capacity, moderate notice
        (4, 180, 6.0),   # Family, large capacity, good notice
        (6, 100, 2.0),   # Large group, small capacity, short notice
    ]
    
    for seats, cap, hours in test_scenarios:
        prob = baseline_return_probability(seats, cap, hours)
        assert 0.1 <= prob <= 0.9, f"Probability {prob} outside reasonable range [0.1, 0.9]"


def test_baseline_single_seat_favorable():
    """AC-Baseline-2: Single seat with good conditions has high probability."""
    prob = baseline_return_probability(
        seats_required=1,
        capacity=180,
        time_to_departure_hours=6.0,
    )
    assert prob >= 0.6, "Single seat with favorable conditions should have high probability"


def test_baseline_large_party_unfavorable():
    """AC-Baseline-2: Large party with poor conditions has low probability."""
    prob = baseline_return_probability(
        seats_required=8,
        capacity=80,
        time_to_departure_hours=1.0,
    )
    assert prob <= 0.4, "Large party with unfavorable conditions should have low probability"
