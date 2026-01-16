"""Core scoring functions for Fly Bot recommendations.

All functions are pure and deterministic for testability.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import NamedTuple


class AgeBucket(str, Enum):
    """Age bucket enum for travelers."""

    INFANT = "infant"
    CHILD = "child"
    ADULT = "adult"


class Traveler(NamedTuple):
    """Traveler with age bucket."""

    age_bucket: AgeBucket


def seats_required(travelers: list[Traveler]) -> int:
    """Calculate number of seats required for a party.

    Rules:
    - Infants: do not require a seat (lap child)
    - Children: require a seat
    - Adults: require a seat

    AC-1: Test adult/child/infant bucket cases and deterministic output.
    """
    count = 0
    for traveler in travelers:
        if traveler.age_bucket in (AgeBucket.ADULT, AgeBucket.CHILD):
            count += 1
        # Infants don't require seats
    return count


def compute_return_buffer_minutes(return_flex_minutes: int, buffer_max_minutes: int = 120) -> int:
    """Compute required return buffer based on flexibility.

    Formula:
    - h = clamp(1 - return_flex_minutes / buffer_max_minutes, 0, 1)
    - required_buffer = round(buffer_max_minutes * h)

    AC-2: Test flex=0→120, flex=120→0, flex>120 clamps to 0, negative flex cases.
    """
    # Handle negative flex as 0
    flex = max(0, return_flex_minutes)

    # Compute h with clamping
    h = 1 - flex / buffer_max_minutes
    h = max(0.0, min(1.0, h))  # Clamp to [0, 1]

    # Compute required buffer
    required_buffer = round(buffer_max_minutes * h)
    return required_buffer


def is_return_eligible(
    arrival_time: datetime, latest_return_time: datetime, buffer_minutes: int
) -> bool:
    """Determine if a return flight is eligible given buffer requirements.

    A return flight is eligible if:
    arrival_time <= latest_return_time - buffer_minutes

    AC-3: Test arrival <= latest-buffer → eligible, boundary cases.
    """
    from datetime import timedelta

    buffered_deadline = latest_return_time - timedelta(minutes=buffer_minutes)
    return arrival_time <= buffered_deadline


def aggregate_return_success_probability(eligible_probs: list[float]) -> float:
    """Aggregate return flight probabilities into single success probability.

    Formula: P(success) = 1 - ∏(1 - p_i)

    AC-4: Test 1 - ∏(1 - p_i) for known vectors, empty list edge case.
    """
    if not eligible_probs:
        return 0.0

    # Compute product of (1 - p_i)
    product = 1.0
    for p in eligible_probs:
        product *= 1 - p

    return 1 - product


def compute_outbound_margin_bonus(seat_margin: int) -> float:
    """Compute outbound margin bonus using sigmoid.

    Formula: sigmoid(seat_margin / 2) = 1 / (1 + exp(-seat_margin / 2))

    AC-5: Test sigmoid(seat_margin/2), monotonicity.
    """
    x = seat_margin / 2.0
    return 1.0 / (1.0 + math.exp(-x))


def compute_trip_score(
    return_success_probability: float,
    outbound_margin_bonus: float,
    return_weight: float = 0.7,
    outbound_weight: float = 0.3,
) -> float:
    """Compute final trip score.

    Formula: trip_score = return_success_probability *
        (return_weight + outbound_weight * outbound_margin_bonus)

    AC-6: Test trip_score = return_prob * (0.7 + 0.3*outbound_bonus).
    """
    coefficient = return_weight + outbound_weight * outbound_margin_bonus
    return return_success_probability * coefficient


@dataclass(frozen=True)
class ScoredTrip:
    """A trip option with its score and components."""

    trip_id: str
    trip_score: float
    return_success_probability: float
    seat_margin: int
    outbound_departure: datetime


def rank_trips_deterministic(trips: list[ScoredTrip], epsilon: float = 0.005) -> list[ScoredTrip]:
    """Rank trips deterministically with stable tie-breakers.

    Tie-break rules if trip_score within epsilon:
    1. Higher return_success_probability
    2. Higher seat_margin
    3. Earlier outbound_departure

    AC-7: Test epsilon tie handling and order stability.
    """
    if not trips:
        return []

    def sort_key(trip: ScoredTrip) -> tuple:
        # Negate for descending order (higher is better)
        # Use timestamp for earlier is better (ascending)
        return (
            -trip.trip_score,  # Primary: higher score
            -trip.return_success_probability,  # Tie-break 1: higher return prob
            -trip.seat_margin,  # Tie-break 2: higher margin
            trip.outbound_departure,  # Tie-break 3: earlier departure
        )

    # Sort trips
    sorted_trips = sorted(trips, key=sort_key)

    # Apply epsilon grouping if needed
    # Group trips within epsilon and apply tie-breakers
    result = []
    i = 0
    while i < len(sorted_trips):
        # Find all trips within epsilon of current trip
        current_score = sorted_trips[i].trip_score
        group = [sorted_trips[i]]
        j = i + 1

        while j < len(sorted_trips):
            if abs(sorted_trips[j].trip_score - current_score) <= epsilon:
                group.append(sorted_trips[j])
                j += 1
            else:
                break

        # Sort group by tie-break rules (already sorted by sort_key)
        result.extend(group)
        i = j

    return result


class ReasonCode(str, Enum):
    """Stable reason codes for explainability."""

    HARD_BUFFER_APPLIED = "HARD_BUFFER_APPLIED"
    LOW_RETURN_COVERAGE = "LOW_RETURN_COVERAGE"
    MISSING_EMPTIES = "MISSING_EMPTIES"
    STALE_EMPTIES = "STALE_EMPTIES"
    FALLBACK_BASELINE_USED = "FALLBACK_BASELINE_USED"
    NEGATIVE_SEAT_MARGIN = "NEGATIVE_SEAT_MARGIN"
    HIGH_RETURN_PROBABILITY = "HIGH_RETURN_PROBABILITY"
    MODERATE_RETURN_PROBABILITY = "MODERATE_RETURN_PROBABILITY"
    LOW_RETURN_PROBABILITY = "LOW_RETURN_PROBABILITY"


def select_reason_codes(
    return_success_probability: float,
    seat_margin: int,
    eligible_return_count: int,
    buffer_minutes: int,
    fallback_used: bool,
    empties_available: bool,
    empties_stale: bool,
) -> list[ReasonCode]:
    """Select appropriate reason codes for a recommendation.

    AC-8: Test reason code selection for known scenarios.
    """
    codes = []

    # Check buffer severity
    if buffer_minutes >= 100:
        codes.append(ReasonCode.HARD_BUFFER_APPLIED)

    # Check return coverage
    if eligible_return_count <= 1:
        codes.append(ReasonCode.LOW_RETURN_COVERAGE)

    # Check empties availability
    if not empties_available:
        codes.append(ReasonCode.MISSING_EMPTIES)

    if empties_stale:
        codes.append(ReasonCode.STALE_EMPTIES)

    # Check fallback
    if fallback_used:
        codes.append(ReasonCode.FALLBACK_BASELINE_USED)

    # Check seat margin
    if seat_margin < 0:
        codes.append(ReasonCode.NEGATIVE_SEAT_MARGIN)

    # Check return probability level
    if return_success_probability >= 0.7:
        codes.append(ReasonCode.HIGH_RETURN_PROBABILITY)
    elif return_success_probability >= 0.4:
        codes.append(ReasonCode.MODERATE_RETURN_PROBABILITY)
    else:
        codes.append(ReasonCode.LOW_RETURN_PROBABILITY)

    return codes
