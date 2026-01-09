from __future__ import annotations

import pytest

from project_name.predict import predict
from project_name.schema import validate_request


def test_validate_request_missing_fields_raises() -> None:
    # AC-? (example): missing field handling
    with pytest.raises(ValueError) as e:
        validate_request({"flight_id": "F1"})
    assert "Missing required field" in str(e.value)


def test_predict_returns_expected_keys() -> None:
    # AC-1
    out = predict({"flight_id": "F1", "dep_delay_min": 10, "distance_mi": 500})
    assert set(out.keys()) == {"prediction", "confidence", "reason_codes"}
