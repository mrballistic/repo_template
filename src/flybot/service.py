"""Core service logic for Fly Bot recommendations.

Orchestrates scoring, client calls, and response building.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta

from flybot.baseline import baseline_model_predict
from flybot.clients import EmptiesClient, EmptiesSnapshot, Flight, ScheduleClient
from flybot.schemas import (
    FlybotRecommendRequest,
    FlybotRecommendResponse,
    OutboundFlight,
    Recommendation,
    ReturnFlightOption,
    ScoreBreakdown,
    TimingMs,
)
from flybot.scoring import (
    AgeBucket,
    ReasonCode,
    ScoredTrip,
    Traveler,
    aggregate_return_success_probability,
    compute_outbound_margin_bonus,
    compute_return_buffer_minutes,
    compute_trip_score,
    is_return_eligible,
    rank_trips_deterministic,
    seats_required,
    select_reason_codes,
)


def _ms_elapsed(start_time: float) -> int:
    """Compute milliseconds elapsed since start_time."""
    return int((time.perf_counter() - start_time) * 1000)


async def recommend(
    request: FlybotRecommendRequest,
    empties_client: EmptiesClient,
    schedule_client: ScheduleClient,
    model_version: str = "baseline-v1",
    use_ml: bool = False,
) -> FlybotRecommendResponse:
    """Generate flight recommendations.
    
    Args:
        request: Validated request
        empties_client: Client for empties data
        schedule_client: Client for schedule data
        model_version: Model version identifier
        use_ml: Whether to use ML model (False = baseline only)
    
    Returns:
        FlybotRecommendResponse with ranked recommendations
    """
    start_time = time.perf_counter()
    timing = {}
    
    # Stage 1: Compute derived values
    validation_start = time.perf_counter()
    
    travelers_list = [
        Traveler(age_bucket=AgeBucket(t.age_bucket.value))
        for t in request.travelers
    ]
    seats_req = seats_required(travelers_list)
    buffer_minutes = compute_return_buffer_minutes(request.return_window.return_flex_minutes)
    
    timing["validation"] = _ms_elapsed(validation_start)
    
    # Stage 2: Fetch outbound empties
    fetch_outbound_start = time.perf_counter()
    
    now = datetime.now()
    empties_snapshot = await empties_client.get_empties(
        origin=request.origin,
        destination=request.destination,
        lookahead_minutes=request.lookahead_minutes,
        snapshot_time=now,
    )
    
    timing["fetch_outbound"] = _ms_elapsed(fetch_outbound_start)
    
    empties_available = empties_snapshot is not None
    empties_stale = empties_snapshot.is_stale if empties_snapshot else False
    
    # Default empty snapshot if unavailable
    if not empties_snapshot:
        empties_snapshot = EmptiesSnapshot(
            snapshot_time=now,
            flights=[],
            is_stale=False,
        )
    
    # Filter outbound flights by seat margin
    outbound_candidates = []
    for flight in empties_snapshot.flights:
        if flight.open_seats is not None:
            margin = flight.open_seats - seats_req
            # Default: exclude negative margin flights
            if margin >= 0:
                outbound_candidates.append((flight, margin))
    
    # Stage 3: For each outbound, fetch return options
    fetch_return_start = time.perf_counter()
    
    return_flights = await schedule_client.get_return_flights(
        origin=request.destination,  # Reversed
        destination=request.origin,
        earliest=request.return_window.earliest,
        latest=request.return_window.latest,
    )
    
    timing["fetch_return"] = _ms_elapsed(fetch_return_start)
    
    schedule_available = return_flights is not None
    if not return_flights:
        return_flights = []
    
    # Stage 4: Score trips
    scoring_start = time.perf_counter()
    
    scored_trips = []
    
    for outbound_flight, seat_margin in outbound_candidates:
        # Filter eligible return flights
        eligible_returns = [
            rf for rf in return_flights
            if is_return_eligible(
                rf.arrival,
                request.return_window.latest,
                buffer_minutes,
            )
        ]
        
        # Predict return probabilities (baseline for now)
        if eligible_returns:
            # Extract features for baseline
            flight_features = [
                (rf.capacity, (rf.departure - now).total_seconds() / 3600)
                for rf in eligible_returns
            ]
            return_probs = baseline_model_predict(flight_features, seats_req)
            
            # Aggregate
            return_success_prob = aggregate_return_success_probability(return_probs)
        else:
            return_probs = []
            return_success_prob = 0.0
        
        # Compute outbound bonus
        outbound_bonus = compute_outbound_margin_bonus(seat_margin)
        
        # Compute trip score
        trip_score_value = compute_trip_score(return_success_prob, outbound_bonus)
        
        # Create scored trip
        scored_trip = ScoredTrip(
            trip_id=f"{outbound_flight.flight_number}_{len(scored_trips)}",
            trip_score=trip_score_value,
            return_success_probability=return_success_prob,
            seat_margin=seat_margin,
            outbound_departure=outbound_flight.departure,
        )
        
        scored_trips.append((
            scored_trip,
            outbound_flight,
            eligible_returns,
            return_probs,
            outbound_bonus,
        ))
    
    # Rank trips
    ranked = rank_trips_deterministic([st[0] for st in scored_trips])
    
    timing["scoring"] = _ms_elapsed(scoring_start)
    
    # Stage 5: Build response
    fallback_used = not use_ml or not schedule_available
    
    recommendations = []
    for scored_trip in ranked:
        # Find original data
        trip_data = next(
            td for td in scored_trips
            if td[0].trip_id == scored_trip.trip_id
        )
        _, outbound_flight, eligible_returns, return_probs, outbound_bonus = trip_data
        
        # Build recommendation
        reason_codes = select_reason_codes(
            return_success_probability=scored_trip.return_success_probability,
            seat_margin=scored_trip.seat_margin,
            eligible_return_count=len(eligible_returns),
            buffer_minutes=buffer_minutes,
            fallback_used=fallback_used,
            empties_available=empties_available,
            empties_stale=empties_stale,
        )
        
        # Generate explanations from reason codes
        explanations = _generate_explanations(reason_codes, scored_trip)
        
        rec = Recommendation(
            trip_score=scored_trip.trip_score,
            score_breakdown=ScoreBreakdown(
                formula="trip_score = return_success_probability * (0.7 + 0.3 * outbound_margin_bonus)",
                return_success_probability=scored_trip.return_success_probability,
                outbound_margin_bonus=outbound_bonus,
                trip_score=scored_trip.trip_score,
            ),
            outbound=OutboundFlight(
                flight_number=outbound_flight.flight_number,
                departure=outbound_flight.departure,
                arrival=outbound_flight.arrival,
                open_seats_now=outbound_flight.open_seats,
                seat_margin=scored_trip.seat_margin,
            ),
            return_options=[
                ReturnFlightOption(
                    flight_number=rf.flight_number,
                    departure=rf.departure,
                    arrival=rf.arrival,
                    clearance_probability=prob,
                )
                for rf, prob in zip(eligible_returns, return_probs)
            ],
            explanations=explanations,
            reason_codes=[rc.value for rc in reason_codes],
        )
        recommendations.append(rec)
    
    # Build final response
    total_ms = _ms_elapsed(start_time)
    
    return FlybotRecommendResponse(
        request_id=request.request_id,
        model_version=model_version,
        generated_at=datetime.now(),
        seats_required=seats_req,
        required_return_buffer_minutes=buffer_minutes,
        recommendations=recommendations,
        fallback_used=fallback_used,
        timing_ms=TimingMs(
            total=total_ms,
            validation=timing.get("validation"),
            fetch_outbound=timing.get("fetch_outbound"),
            fetch_return=timing.get("fetch_return"),
            scoring=timing.get("scoring"),
        ),
    )


def _generate_explanations(
    reason_codes: list[ReasonCode],
    scored_trip: ScoredTrip,
) -> list[str]:
    """Generate user-facing explanations from reason codes."""
    explanations = []
    
    for code in reason_codes:
        if code == ReasonCode.HIGH_RETURN_PROBABILITY:
            explanations.append(
                f"High return probability ({scored_trip.return_success_probability:.0%}) "
                "with multiple eligible flights"
            )
        elif code == ReasonCode.MODERATE_RETURN_PROBABILITY:
            explanations.append(
                f"Moderate return probability ({scored_trip.return_success_probability:.0%})"
            )
        elif code == ReasonCode.LOW_RETURN_PROBABILITY:
            explanations.append(
                f"Limited return options ({scored_trip.return_success_probability:.0%} probability)"
            )
        elif code == ReasonCode.LOW_RETURN_COVERAGE:
            explanations.append("Few eligible return flights within time window")
        elif code == ReasonCode.HARD_BUFFER_APPLIED:
            explanations.append("Strict return deadline requires early arrival")
        elif code == ReasonCode.NEGATIVE_SEAT_MARGIN:
            explanations.append("Outbound flight has limited available seats")
        elif code == ReasonCode.FALLBACK_BASELINE_USED:
            explanations.append("Using baseline estimates (ML model unavailable)")
    
    return explanations
