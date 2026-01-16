"""Unit tests for deterministic ranking and tie-breaking.

AC-7: Test epsilon tie handling and order stability.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from flybot.scoring import ScoredTrip, rank_trips_deterministic


def test_rank_by_trip_score():
    """AC-7: Trips ranked by trip_score in descending order."""
    trips = [
        ScoredTrip(
            trip_id="A",
            trip_score=0.5,
            return_success_probability=0.6,
            seat_margin=5,
            outbound_departure=datetime(2026, 1, 15, 10, 0),
        ),
        ScoredTrip(
            trip_id="B",
            trip_score=0.8,
            return_success_probability=0.85,
            seat_margin=3,
            outbound_departure=datetime(2026, 1, 15, 11, 0),
        ),
        ScoredTrip(
            trip_id="C",
            trip_score=0.3,
            return_success_probability=0.4,
            seat_margin=2,
            outbound_departure=datetime(2026, 1, 15, 9, 0),
        ),
    ]
    ranked = rank_trips_deterministic(trips)
    assert [t.trip_id for t in ranked] == ["B", "A", "C"]


def test_rank_tie_break_by_return_probability():
    """AC-7: Tie in trip_score (within epsilon) breaks by return_probability."""
    base_time = datetime(2026, 1, 15, 10, 0)
    trips = [
        ScoredTrip(
            trip_id="A",
            trip_score=0.700,
            return_success_probability=0.75,
            seat_margin=5,
            outbound_departure=base_time,
        ),
        ScoredTrip(
            trip_id="B",
            trip_score=0.702,  # Within epsilon of 0.700
            return_success_probability=0.85,  # Higher return prob
            seat_margin=5,
            outbound_departure=base_time,
        ),
    ]
    ranked = rank_trips_deterministic(trips, epsilon=0.005)
    assert ranked[0].trip_id == "B"  # Higher return probability wins


def test_rank_tie_break_by_seat_margin():
    """AC-7: Tie in score and return_prob breaks by seat_margin."""
    base_time = datetime(2026, 1, 15, 10, 0)
    trips = [
        ScoredTrip(
            trip_id="A",
            trip_score=0.700,
            return_success_probability=0.75,
            seat_margin=3,
            outbound_departure=base_time,
        ),
        ScoredTrip(
            trip_id="B",
            trip_score=0.702,  # Within epsilon
            return_success_probability=0.75,  # Same
            seat_margin=7,  # Higher margin
            outbound_departure=base_time,
        ),
    ]
    ranked = rank_trips_deterministic(trips, epsilon=0.005)
    assert ranked[0].trip_id == "B"  # Higher seat margin wins


def test_rank_tie_break_by_departure_time():
    """AC-7: Tie in score, return_prob, and margin breaks by earlier departure."""
    base_time = datetime(2026, 1, 15, 10, 0)
    trips = [
        ScoredTrip(
            trip_id="A",
            trip_score=0.700,
            return_success_probability=0.75,
            seat_margin=5,
            outbound_departure=base_time + timedelta(minutes=30),  # Later
        ),
        ScoredTrip(
            trip_id="B",
            trip_score=0.702,  # Within epsilon
            return_success_probability=0.75,  # Same
            seat_margin=5,  # Same
            outbound_departure=base_time,  # Earlier
        ),
    ]
    ranked = rank_trips_deterministic(trips, epsilon=0.005)
    assert ranked[0].trip_id == "B"  # Earlier departure wins


def test_rank_stability():
    """AC-7: Same input produces same order (stable sort)."""
    base_time = datetime(2026, 1, 15, 10, 0)
    trips = [
        ScoredTrip(
            trip_id=f"Trip{i}",
            trip_score=0.7 + i * 0.001,  # All within epsilon
            return_success_probability=0.75,
            seat_margin=5,
            outbound_departure=base_time + timedelta(minutes=i * 10),
        )
        for i in range(5)
    ]

    ranked1 = rank_trips_deterministic(trips, epsilon=0.01)
    ranked2 = rank_trips_deterministic(trips, epsilon=0.01)

    ids1 = [t.trip_id for t in ranked1]
    ids2 = [t.trip_id for t in ranked2]
    assert ids1 == ids2


def test_rank_epsilon_boundary():
    """AC-7: Scores exactly epsilon apart are not tied."""
    base_time = datetime(2026, 1, 15, 10, 0)
    trips = [
        ScoredTrip(
            trip_id="A",
            trip_score=0.700,
            return_success_probability=0.70,  # Lower
            seat_margin=10,  # Would win tiebreak
            outbound_departure=base_time,
        ),
        ScoredTrip(
            trip_id="B",
            trip_score=0.706,  # Just over epsilon=0.005
            return_success_probability=0.60,
            seat_margin=1,
            outbound_departure=base_time + timedelta(hours=1),
        ),
    ]
    ranked = rank_trips_deterministic(trips, epsilon=0.005)
    # B should win because score difference > epsilon
    assert ranked[0].trip_id == "B"


def test_rank_empty_list():
    """AC-7: Empty list returns empty list."""
    ranked = rank_trips_deterministic([])
    assert ranked == []


def test_rank_single_trip():
    """AC-7: Single trip returns as-is."""
    trip = ScoredTrip(
        trip_id="Solo",
        trip_score=0.5,
        return_success_probability=0.6,
        seat_margin=3,
        outbound_departure=datetime(2026, 1, 15, 10, 0),
    )
    ranked = rank_trips_deterministic([trip])
    assert len(ranked) == 1
    assert ranked[0].trip_id == "Solo"
