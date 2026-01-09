from __future__ import annotations

from typing import Iterable


def accuracy(y_true: Iterable[int], y_pred: Iterable[int]) -> float:
    yt = list(y_true)
    yp = list(y_pred)
    if len(yt) != len(yp):
        raise ValueError("y_true and y_pred must have the same length")
    if not yt:
        raise ValueError("inputs must be non-empty")
    correct = sum(1 for a, b in zip(yt, yp) if a == b)
    return correct / len(yt)
