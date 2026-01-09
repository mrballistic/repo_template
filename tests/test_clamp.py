from __future__ import annotations

from project_name.predict import predict


def test_prediction_and_confidence_are_clamped_to_0_1() -> None:
    # AC-4
    out = predict({"flight_id": "F1", "dep_delay_min": 10_000, "distance_mi": 999_999})
    assert 0.0 <= out["prediction"] <= 1.0
    assert 0.0 <= out["confidence"] <= 1.0
