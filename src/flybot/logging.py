"""
Structured logging for Fly Bot predictions.

Logs aligned to flybot_predictions_log schema from DATA_SCHEMA.md.
No PII is logged - only aggregate counts, age buckets, and derived features.
"""

import json
import logging
from datetime import UTC, datetime

# Configure logger
logger = logging.getLogger(__name__)


def log_prediction(
    request_id: str,
    model_version: str,
    origin: str,
    destination: str,
    lookahead_minutes: int,
    seats_required: int,
    return_deadline_ts: datetime,
    return_flex_minutes: int,
    required_return_buffer_minutes: int,
    outbound_flight_id: str,
    outbound_open_seats_now: int | None,
    outbound_seat_margin: int | None,
    return_flight_ids: list[str],
    return_probs: list[float],
    return_success_probability: float,
    outbound_margin_bonus: float,
    trip_score: float,
    fallback_used: bool,
    reason_codes: list[str],
    timing_total_ms: int,
) -> None:
    """
    Log a prediction in structured JSON format.

    Fields align to flybot_predictions_log schema from DATA_SCHEMA.md.
    No PII is included - only aggregate metrics and derived features.

    Args:
        request_id: Unique request identifier for tracing
        model_version: Model version used (e.g., "baseline-v1", "gbdt-v1.2")
        origin: Origin airport IATA code
        destination: Destination airport IATA code
        lookahead_minutes: Lookahead window for outbound flight search
        seats_required: Number of seats required (derived from travelers)
        return_deadline_ts: Return deadline timestamp (latest acceptable arrival)
        return_flex_minutes: Return flexibility in minutes
        required_return_buffer_minutes: Computed buffer minutes
        outbound_flight_id: Selected outbound flight identifier
        outbound_open_seats_now: Open seats on outbound (optional)
        outbound_seat_margin: Seat margin on outbound (optional)
        return_flight_ids: List of eligible return flight IDs
        return_probs: Aligned probabilities for each return flight
        return_success_probability: Aggregated return success probability
        outbound_margin_bonus: Outbound margin bonus [0, 0.3]
        trip_score: Final trip score
        fallback_used: True if baseline fallback was used
        reason_codes: List of stable reason codes
        timing_total_ms: Total request latency in milliseconds
    """
    log_data = {
        "request_id": request_id,
        "logged_at": datetime.now(UTC).isoformat(),
        "model_version": model_version,
        "origin": origin,
        "destination": destination,
        "lookahead_minutes": lookahead_minutes,
        "seats_required": seats_required,
        "return_deadline_ts": return_deadline_ts.isoformat(),
        "return_flex_minutes": return_flex_minutes,
        "required_return_buffer_minutes": required_return_buffer_minutes,
        "outbound_flight_id": outbound_flight_id,
        "outbound_open_seats_now": outbound_open_seats_now,
        "outbound_seat_margin": outbound_seat_margin,
        "return_flight_ids": return_flight_ids,
        "return_probs": return_probs,
        "return_success_probability": return_success_probability,
        "outbound_margin_bonus": outbound_margin_bonus,
        "trip_score": trip_score,
        "fallback_used": fallback_used,
        "reason_codes": reason_codes,
        "timing_total_ms": timing_total_ms,
    }

    # Log as structured JSON (single line for easy parsing)
    logger.info(json.dumps(log_data))
