"""
Unit tests for structured logging.

Tests verify:
- Required fields present per flybot_predictions_log schema
- No PII in logs
- request_id propagation
- fallback_used flag correct
- Timing data included
"""

import json
from datetime import UTC, datetime

from flybot.logging import log_prediction


def test_log_prediction_contains_required_fields(caplog):
    """Verify all required fields from flybot_predictions_log schema are logged."""
    request_id = "test-req-123"
    model_version = "baseline-v1"
    origin = "SEA"
    destination = "LAX"
    lookahead_minutes = 60
    seats_required = 2
    return_deadline = datetime(2026, 1, 20, 18, 0, tzinfo=UTC)
    return_flex_minutes = 120
    required_buffer_minutes = 37
    outbound_flight_id = "AS123"
    outbound_open_seats = 15
    outbound_seat_margin = 13
    return_flight_ids = ["AS456", "AS789"]
    return_probs = [0.75, 0.85]
    return_success_prob = 0.9625
    outbound_margin_bonus = 0.28
    trip_score = 0.758
    fallback_used = False
    reason_codes = ["high_return_prob", "positive_outbound_margin"]
    timing_total_ms = 120

    with caplog.at_level("INFO"):
        log_prediction(
            request_id=request_id,
            model_version=model_version,
            origin=origin,
            destination=destination,
            lookahead_minutes=lookahead_minutes,
            seats_required=seats_required,
            return_deadline_ts=return_deadline,
            return_flex_minutes=return_flex_minutes,
            required_return_buffer_minutes=required_buffer_minutes,
            outbound_flight_id=outbound_flight_id,
            outbound_open_seats_now=outbound_open_seats,
            outbound_seat_margin=outbound_seat_margin,
            return_flight_ids=return_flight_ids,
            return_probs=return_probs,
            return_success_probability=return_success_prob,
            outbound_margin_bonus=outbound_margin_bonus,
            trip_score=trip_score,
            fallback_used=fallback_used,
            reason_codes=reason_codes,
            timing_total_ms=timing_total_ms,
        )

    # Check log was emitted
    assert len(caplog.records) == 1
    record = caplog.records[0]

    # Parse the JSON log message
    log_data = json.loads(record.message)

    # Verify all required fields present
    assert log_data["request_id"] == request_id
    assert log_data["model_version"] == model_version
    assert log_data["origin"] == origin
    assert log_data["destination"] == destination
    assert log_data["lookahead_minutes"] == lookahead_minutes
    assert log_data["seats_required"] == seats_required
    assert log_data["return_deadline_ts"] == return_deadline.isoformat()
    assert log_data["return_flex_minutes"] == return_flex_minutes
    assert log_data["required_return_buffer_minutes"] == required_buffer_minutes
    assert log_data["outbound_flight_id"] == outbound_flight_id
    assert log_data["outbound_open_seats_now"] == outbound_open_seats
    assert log_data["outbound_seat_margin"] == outbound_seat_margin
    assert log_data["return_flight_ids"] == return_flight_ids
    assert log_data["return_probs"] == return_probs
    assert log_data["return_success_probability"] == return_success_prob
    assert log_data["outbound_margin_bonus"] == outbound_margin_bonus
    assert log_data["trip_score"] == trip_score
    assert log_data["fallback_used"] == fallback_used
    assert log_data["reason_codes"] == reason_codes
    assert log_data["timing_total_ms"] == timing_total_ms
    assert "logged_at" in log_data


def test_log_prediction_no_pii(caplog):
    """Verify no PII fields are logged (no raw age, traveler names, etc)."""
    # This test ensures we only log aggregate counts, age buckets, not raw personal data
    request_id = "req-456"
    model_version = "baseline-v1"

    with caplog.at_level("INFO"):
        log_prediction(
            request_id=request_id,
            model_version=model_version,
            origin="PDX",
            destination="SFO",
            lookahead_minutes=30,
            seats_required=1,
            return_deadline_ts=datetime(2026, 1, 22, 12, 0, tzinfo=UTC),
            return_flex_minutes=0,
            required_return_buffer_minutes=0,
            outbound_flight_id="AS999",
            outbound_open_seats_now=10,
            outbound_seat_margin=9,
            return_flight_ids=["AS111"],
            return_probs=[0.5],
            return_success_probability=0.5,
            outbound_margin_bonus=0.15,
            trip_score=0.545,
            fallback_used=True,
            reason_codes=["fallback_used"],
            timing_total_ms=50,
        )

    # Parse log
    assert len(caplog.records) == 1
    log_data = json.loads(caplog.records[0].message)

    # Ensure PII fields not present
    assert "traveler_name" not in log_data
    assert "traveler_age" not in log_data
    assert "email" not in log_data
    assert "phone" not in log_data
    assert "passenger_name" not in log_data


def test_log_prediction_fallback_flag_true(caplog):
    """Verify fallback_used=true is logged when baseline used."""
    with caplog.at_level("INFO"):
        log_prediction(
            request_id="fallback-test",
            model_version="baseline-v1",
            origin="SEA",
            destination="LAX",
            lookahead_minutes=60,
            seats_required=2,
            return_deadline_ts=datetime(2026, 1, 20, 18, 0, tzinfo=UTC),
            return_flex_minutes=120,
            required_return_buffer_minutes=37,
            outbound_flight_id="AS123",
            outbound_open_seats_now=15,
            outbound_seat_margin=13,
            return_flight_ids=["AS456"],
            return_probs=[0.7],
            return_success_probability=0.7,
            outbound_margin_bonus=0.25,
            trip_score=0.665,
            fallback_used=True,  # Fallback active
            reason_codes=["fallback_used"],
            timing_total_ms=80,
        )

    log_data = json.loads(caplog.records[0].message)
    assert log_data["fallback_used"] is True
    assert "fallback_used" in log_data["reason_codes"]
    assert log_data["model_version"] == "baseline-v1"


def test_log_prediction_fallback_flag_false(caplog):
    """Verify fallback_used=false when ML model used."""
    with caplog.at_level("INFO"):
        log_prediction(
            request_id="ml-test",
            model_version="gbdt-v1.2",
            origin="SEA",
            destination="LAX",
            lookahead_minutes=60,
            seats_required=2,
            return_deadline_ts=datetime(2026, 1, 20, 18, 0, tzinfo=UTC),
            return_flex_minutes=120,
            required_return_buffer_minutes=37,
            outbound_flight_id="AS123",
            outbound_open_seats_now=15,
            outbound_seat_margin=13,
            return_flight_ids=["AS456"],
            return_probs=[0.8],
            return_success_probability=0.8,
            outbound_margin_bonus=0.25,
            trip_score=0.735,
            fallback_used=False,  # ML active
            reason_codes=["high_return_prob"],
            timing_total_ms=150,
        )

    log_data = json.loads(caplog.records[0].message)
    assert log_data["fallback_used"] is False
    assert log_data["model_version"] == "gbdt-v1.2"


def test_log_prediction_request_id_propagation(caplog):
    """Verify request_id is propagated correctly for tracing."""
    unique_id = "trace-xyz-789"

    with caplog.at_level("INFO"):
        log_prediction(
            request_id=unique_id,
            model_version="baseline-v1",
            origin="SEA",
            destination="LAX",
            lookahead_minutes=60,
            seats_required=1,
            return_deadline_ts=datetime(2026, 1, 20, 18, 0, tzinfo=UTC),
            return_flex_minutes=60,
            required_return_buffer_minutes=18,
            outbound_flight_id="AS100",
            outbound_open_seats_now=20,
            outbound_seat_margin=19,
            return_flight_ids=["AS200"],
            return_probs=[0.6],
            return_success_probability=0.6,
            outbound_margin_bonus=0.3,
            trip_score=0.63,
            fallback_used=False,
            reason_codes=["adequate_coverage"],
            timing_total_ms=100,
        )

    log_data = json.loads(caplog.records[0].message)
    assert log_data["request_id"] == unique_id


def test_log_prediction_timing_included(caplog):
    """Verify timing_total_ms is logged for latency monitoring."""
    with caplog.at_level("INFO"):
        log_prediction(
            request_id="timing-test",
            model_version="baseline-v1",
            origin="SEA",
            destination="LAX",
            lookahead_minutes=60,
            seats_required=1,
            return_deadline_ts=datetime(2026, 1, 20, 18, 0, tzinfo=UTC),
            return_flex_minutes=60,
            required_return_buffer_minutes=18,
            outbound_flight_id="AS100",
            outbound_open_seats_now=20,
            outbound_seat_margin=19,
            return_flight_ids=["AS200"],
            return_probs=[0.6],
            return_success_probability=0.6,
            outbound_margin_bonus=0.3,
            trip_score=0.63,
            fallback_used=False,
            reason_codes=["adequate_coverage"],
            timing_total_ms=275,  # Specific timing value
        )

    log_data = json.loads(caplog.records[0].message)
    assert log_data["timing_total_ms"] == 275
    assert isinstance(log_data["timing_total_ms"], int)


def test_log_prediction_multiple_return_flights(caplog):
    """Verify arrays (return_flight_ids, return_probs) are logged correctly."""
    with caplog.at_level("INFO"):
        log_prediction(
            request_id="multi-return-test",
            model_version="baseline-v1",
            origin="SEA",
            destination="LAX",
            lookahead_minutes=60,
            seats_required=3,
            return_deadline_ts=datetime(2026, 1, 20, 22, 0, tzinfo=UTC),
            return_flex_minutes=180,
            required_return_buffer_minutes=56,
            outbound_flight_id="AS300",
            outbound_open_seats_now=25,
            outbound_seat_margin=22,
            return_flight_ids=["AS401", "AS402", "AS403", "AS404"],
            return_probs=[0.65, 0.70, 0.75, 0.80],
            return_success_probability=0.9899,
            outbound_margin_bonus=0.3,
            trip_score=0.902,
            fallback_used=False,
            reason_codes=["high_return_prob", "positive_outbound_margin", "high_coverage"],
            timing_total_ms=180,
        )

    log_data = json.loads(caplog.records[0].message)
    assert len(log_data["return_flight_ids"]) == 4
    assert len(log_data["return_probs"]) == 4
    assert log_data["return_flight_ids"] == ["AS401", "AS402", "AS403", "AS404"]
    assert log_data["return_probs"] == [0.65, 0.70, 0.75, 0.80]


def test_log_prediction_optional_fields_omitted(caplog):
    """Verify optional fields can be None and are handled correctly."""
    with caplog.at_level("INFO"):
        log_prediction(
            request_id="optional-test",
            model_version="baseline-v1",
            origin="SEA",
            destination="LAX",
            lookahead_minutes=60,
            seats_required=1,
            return_deadline_ts=datetime(2026, 1, 20, 18, 0, tzinfo=UTC),
            return_flex_minutes=60,
            required_return_buffer_minutes=18,
            outbound_flight_id="AS100",
            outbound_open_seats_now=None,  # Optional
            outbound_seat_margin=None,  # Optional
            return_flight_ids=["AS200"],
            return_probs=[0.6],
            return_success_probability=0.6,
            outbound_margin_bonus=0.0,
            trip_score=0.42,
            fallback_used=True,
            reason_codes=["fallback_used"],
            timing_total_ms=90,
        )

    log_data = json.loads(caplog.records[0].message)
    # Optional fields should be null in JSON
    assert log_data["outbound_open_seats_now"] is None
    assert log_data["outbound_seat_margin"] is None
    # Required fields still present
    assert log_data["request_id"] == "optional-test"
    assert log_data["trip_score"] == 0.42
