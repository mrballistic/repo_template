"""Unit tests for reason code selection.

AC-8: Test reason code selection for known scenarios.
"""

from __future__ import annotations

import pytest

from flybot.scoring import ReasonCode, select_reason_codes


def test_reason_hard_buffer_applied():
    """AC-8: Hard buffer (buffer >= 100) triggers HARD_BUFFER_APPLIED."""
    codes = select_reason_codes(
        return_success_probability=0.6,
        seat_margin=5,
        eligible_return_count=3,
        buffer_minutes=120,
        fallback_used=False,
        empties_available=True,
        empties_stale=False,
    )
    assert ReasonCode.HARD_BUFFER_APPLIED in codes


def test_reason_low_return_coverage():
    """AC-8: 1 or fewer eligible returns triggers LOW_RETURN_COVERAGE."""
    codes = select_reason_codes(
        return_success_probability=0.3,
        seat_margin=5,
        eligible_return_count=1,
        buffer_minutes=60,
        fallback_used=False,
        empties_available=True,
        empties_stale=False,
    )
    assert ReasonCode.LOW_RETURN_COVERAGE in codes


def test_reason_missing_empties():
    """AC-8: empties_available=False triggers MISSING_EMPTIES."""
    codes = select_reason_codes(
        return_success_probability=0.5,
        seat_margin=0,
        eligible_return_count=5,
        buffer_minutes=60,
        fallback_used=False,
        empties_available=False,
        empties_stale=False,
    )
    assert ReasonCode.MISSING_EMPTIES in codes


def test_reason_stale_empties():
    """AC-8: empties_stale=True triggers STALE_EMPTIES."""
    codes = select_reason_codes(
        return_success_probability=0.5,
        seat_margin=5,
        eligible_return_count=5,
        buffer_minutes=60,
        fallback_used=False,
        empties_available=True,
        empties_stale=True,
    )
    assert ReasonCode.STALE_EMPTIES in codes


def test_reason_fallback_baseline_used():
    """AC-8: fallback_used=True triggers FALLBACK_BASELINE_USED."""
    codes = select_reason_codes(
        return_success_probability=0.4,
        seat_margin=5,
        eligible_return_count=5,
        buffer_minutes=60,
        fallback_used=True,
        empties_available=True,
        empties_stale=False,
    )
    assert ReasonCode.FALLBACK_BASELINE_USED in codes


def test_reason_negative_seat_margin():
    """AC-8: seat_margin < 0 triggers NEGATIVE_SEAT_MARGIN."""
    codes = select_reason_codes(
        return_success_probability=0.5,
        seat_margin=-2,
        eligible_return_count=5,
        buffer_minutes=60,
        fallback_used=False,
        empties_available=True,
        empties_stale=False,
    )
    assert ReasonCode.NEGATIVE_SEAT_MARGIN in codes


def test_reason_high_return_probability():
    """AC-8: return_prob >= 0.7 triggers HIGH_RETURN_PROBABILITY."""
    codes = select_reason_codes(
        return_success_probability=0.85,
        seat_margin=5,
        eligible_return_count=5,
        buffer_minutes=60,
        fallback_used=False,
        empties_available=True,
        empties_stale=False,
    )
    assert ReasonCode.HIGH_RETURN_PROBABILITY in codes


def test_reason_moderate_return_probability():
    """AC-8: 0.4 <= return_prob < 0.7 triggers MODERATE_RETURN_PROBABILITY."""
    codes = select_reason_codes(
        return_success_probability=0.55,
        seat_margin=5,
        eligible_return_count=5,
        buffer_minutes=60,
        fallback_used=False,
        empties_available=True,
        empties_stale=False,
    )
    assert ReasonCode.MODERATE_RETURN_PROBABILITY in codes


def test_reason_low_return_probability():
    """AC-8: return_prob < 0.4 triggers LOW_RETURN_PROBABILITY."""
    codes = select_reason_codes(
        return_success_probability=0.25,
        seat_margin=5,
        eligible_return_count=5,
        buffer_minutes=60,
        fallback_used=False,
        empties_available=True,
        empties_stale=False,
    )
    assert ReasonCode.LOW_RETURN_PROBABILITY in codes


def test_reason_multiple_codes():
    """AC-8: Multiple conditions can trigger multiple codes."""
    codes = select_reason_codes(
        return_success_probability=0.15,  # Low return prob
        seat_margin=-3,  # Negative margin
        eligible_return_count=1,  # Low coverage
        buffer_minutes=120,  # Hard buffer
        fallback_used=True,  # Fallback
        empties_available=False,  # Missing empties
        empties_stale=True,  # Stale empties
    )
    
    # Should have all applicable codes
    expected_codes = {
        ReasonCode.LOW_RETURN_PROBABILITY,
        ReasonCode.NEGATIVE_SEAT_MARGIN,
        ReasonCode.LOW_RETURN_COVERAGE,
        ReasonCode.HARD_BUFFER_APPLIED,
        ReasonCode.FALLBACK_BASELINE_USED,
        ReasonCode.MISSING_EMPTIES,
        ReasonCode.STALE_EMPTIES,
    }
    
    for code in expected_codes:
        assert code in codes


def test_reason_deterministic():
    """AC-8: Same inputs produce same codes."""
    codes1 = select_reason_codes(
        return_success_probability=0.5,
        seat_margin=3,
        eligible_return_count=4,
        buffer_minutes=80,
        fallback_used=False,
        empties_available=True,
        empties_stale=False,
    )
    codes2 = select_reason_codes(
        return_success_probability=0.5,
        seat_margin=3,
        eligible_return_count=4,
        buffer_minutes=80,
        fallback_used=False,
        empties_available=True,
        empties_stale=False,
    )
    assert codes1 == codes2
