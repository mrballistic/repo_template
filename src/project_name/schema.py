from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PredictRequest:
    flight_id: str
    dep_delay_min: int
    distance_mi: int


@dataclass(frozen=True)
class PredictResponse:
    prediction: float
    confidence: float
    reason_codes: list[str]


def validate_request(payload: dict[str, Any]) -> PredictRequest:
    """Validate and normalize the incoming payload.

    Raise ValueError with a clear message on invalid inputs.
    """
    missing = [k for k in ["flight_id", "dep_delay_min", "distance_mi"] if k not in payload]
    if missing:
        raise ValueError(f"Missing required field(s): {', '.join(missing)}")

    flight_id = payload["flight_id"]
    dep_delay_min = payload["dep_delay_min"]
    distance_mi = payload["distance_mi"]

    if not isinstance(flight_id, str) or not flight_id.strip():
        raise ValueError("flight_id must be a non-empty string")
    if not isinstance(dep_delay_min, int):
        raise ValueError("dep_delay_min must be an int")
    if dep_delay_min < 0:
        raise ValueError("dep_delay_min must be >= 0")
    if not isinstance(distance_mi, int):
        raise ValueError("distance_mi must be an int")
    if distance_mi <= 0:
        raise ValueError("distance_mi must be > 0")

    return PredictRequest(flight_id=flight_id, dep_delay_min=dep_delay_min, distance_mi=distance_mi)
