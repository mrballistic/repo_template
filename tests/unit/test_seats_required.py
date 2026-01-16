"""Unit tests for seats_required function.

AC-1: Test adult/child/infant bucket cases and deterministic output.
"""

from __future__ import annotations

from flybot.scoring import AgeBucket, Traveler, seats_required


def test_seats_required_single_adult():
    """AC-1: Single adult requires 1 seat."""
    travelers = [Traveler(age_bucket=AgeBucket.ADULT)]
    assert seats_required(travelers) == 1


def test_seats_required_single_child():
    """AC-1: Single child requires 1 seat."""
    travelers = [Traveler(age_bucket=AgeBucket.CHILD)]
    assert seats_required(travelers) == 1


def test_seats_required_single_infant():
    """AC-1: Single infant requires 0 seats (lap child)."""
    travelers = [Traveler(age_bucket=AgeBucket.INFANT)]
    assert seats_required(travelers) == 0


def test_seats_required_adult_and_infant():
    """AC-1: Adult + infant requires 1 seat."""
    travelers = [
        Traveler(age_bucket=AgeBucket.ADULT),
        Traveler(age_bucket=AgeBucket.INFANT),
    ]
    assert seats_required(travelers) == 1


def test_seats_required_mixed_party():
    """AC-1: Mixed party: 2 adults + 1 child + 1 infant = 3 seats."""
    travelers = [
        Traveler(age_bucket=AgeBucket.ADULT),
        Traveler(age_bucket=AgeBucket.ADULT),
        Traveler(age_bucket=AgeBucket.CHILD),
        Traveler(age_bucket=AgeBucket.INFANT),
    ]
    assert seats_required(travelers) == 3


def test_seats_required_multiple_infants():
    """AC-1: Multiple infants require 0 seats."""
    travelers = [
        Traveler(age_bucket=AgeBucket.INFANT),
        Traveler(age_bucket=AgeBucket.INFANT),
    ]
    assert seats_required(travelers) == 0


def test_seats_required_empty_list():
    """AC-1: Empty traveler list requires 0 seats."""
    travelers = []
    assert seats_required(travelers) == 0


def test_seats_required_deterministic():
    """AC-1: Same input produces same output (deterministic)."""
    travelers = [
        Traveler(age_bucket=AgeBucket.ADULT),
        Traveler(age_bucket=AgeBucket.CHILD),
        Traveler(age_bucket=AgeBucket.INFANT),
    ]
    result1 = seats_required(travelers)
    result2 = seats_required(travelers)
    assert result1 == result2 == 2
