from __future__ import annotations

from project_name.predict import predict


def test_predict_is_deterministic() -> None:
    # AC-3
    payload = {"flight_id": "F1", "dep_delay_min": 10, "distance_mi": 500}
    out1 = predict(payload)
    out2 = predict(payload)
    assert out1 == out2
