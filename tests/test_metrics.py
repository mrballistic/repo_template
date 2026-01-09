from __future__ import annotations

import pytest

from eval.metrics import accuracy


def test_accuracy_basic() -> None:
    assert accuracy([1, 0, 1], [1, 1, 1]) == pytest.approx(2/3)


def test_accuracy_length_mismatch_raises() -> None:
    with pytest.raises(ValueError):
        accuracy([1], [1, 0])
