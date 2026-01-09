from __future__ import annotations

from typing import Any

from .schema import PredictResponse, validate_request


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def predict(payload: dict[str, Any]) -> dict[str, Any]:
    """Toy prediction function.

    In real usage, this would call a model artifact, feature pipeline, etc.
    This implementation is deterministic and intentionally simple.
    """
    req = validate_request(payload)

    # Toy score: more delay minutes -> higher risk; longer distance -> slightly higher risk
    raw = (req.dep_delay_min / 120.0) + (req.distance_mi / 5000.0) * 0.2
    prediction = _clamp01(raw)

    # Toy confidence: higher when dep_delay is very small or very large (just for example)
    conf_raw = 0.6 + min(req.dep_delay_min, 120) / 400.0
    confidence = _clamp01(conf_raw)

    reasons: list[str] = []
    if req.dep_delay_min >= 30:
        reasons.append("HIGH_DEP_DELAY")
    if req.distance_mi >= 2000:
        reasons.append("LONG_DISTANCE")

    resp = PredictResponse(prediction=prediction, confidence=confidence, reason_codes=reasons)
    return {
        "prediction": resp.prediction,
        "confidence": resp.confidence,
        "reason_codes": resp.reason_codes,
    }
