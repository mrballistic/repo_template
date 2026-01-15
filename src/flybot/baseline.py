"""Baseline heuristic model for return flight probability.

Provides deterministic fallback when ML model is unavailable.
"""

from __future__ import annotations

import math


def baseline_return_probability(
    seats_required: int,
    capacity: int | None = None,
    time_to_departure_hours: float | None = None,
) -> float:
    """Compute baseline return probability using simple heuristics.
    
    Baseline approach:
    - Base probability: 0.5
    - Penalty for party size: -0.05 per seat required (more people = harder)
    - Bonus for capacity: +0.1 if capacity > 100 (larger planes)
    - Bonus for advance time: +0.1 if > 4 hours to departure
    
    Result is clamped to [0.1, 0.9] to avoid extreme predictions.
    
    This is intentionally simple and serves as a safe fallback.
    """
    base = 0.5
    
    # Party size penalty
    party_penalty = seats_required * 0.05
    
    # Capacity bonus
    capacity_bonus = 0.1 if capacity and capacity > 100 else 0.0
    
    # Advance time bonus
    time_bonus = 0.1 if time_to_departure_hours and time_to_departure_hours > 4 else 0.0
    
    prob = base - party_penalty + capacity_bonus + time_bonus
    
    # Clamp to reasonable range
    return max(0.1, min(0.9, prob))


def baseline_model_predict(
    flights: list[tuple[int | None, float | None]],  # (capacity, hours_to_departure)
    seats_required: int,
) -> list[float]:
    """Predict probabilities for multiple flights.
    
    Args:
        flights: List of (capacity, hours_to_departure) tuples
        seats_required: Number of seats party needs
    
    Returns:
        List of probabilities aligned with input flights
    """
    return [
        baseline_return_probability(seats_required, capacity, hours)
        for capacity, hours in flights
    ]
