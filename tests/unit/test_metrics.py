"""Tests for evaluation metrics.

AC-Metrics-1: Brier score is correct for known cases.
AC-Metrics-2: Calibration curve bins predictions correctly.
"""

from __future__ import annotations

import math

from eval.metrics import (
    accuracy_score,
    brier_score,
    calibration_curve,
    compute_metrics,
    precision_recall_f1,
)


def test_brier_score_perfect():
    """AC-Metrics-1: Perfect predictions have Brier score of 0."""
    y_true = [0, 0, 1, 1]
    y_pred = [0.0, 0.0, 1.0, 1.0]

    score = brier_score(y_true, y_pred)
    assert score == 0.0


def test_brier_score_worst():
    """AC-Metrics-1: Worst predictions have Brier score of 1."""
    y_true = [0, 0, 1, 1]
    y_pred = [1.0, 1.0, 0.0, 0.0]

    score = brier_score(y_true, y_pred)
    assert score == 1.0


def test_brier_score_known_value():
    """AC-Metrics-1: Brier score matches manual calculation."""
    y_true = [1, 0, 1]
    y_pred = [0.8, 0.3, 0.6]

    # Manual: ((1-0.8)^2 + (0-0.3)^2 + (1-0.6)^2) / 3
    # = (0.04 + 0.09 + 0.16) / 3 = 0.29 / 3
    expected = (0.04 + 0.09 + 0.16) / 3

    score = brier_score(y_true, y_pred)
    assert math.isclose(score, expected, abs_tol=1e-9)


def test_accuracy_score_perfect():
    """AC-Metrics-1: Perfect predictions have 100% accuracy."""
    y_true = [0, 0, 1, 1]
    y_pred = [0.1, 0.2, 0.9, 0.8]

    acc = accuracy_score(y_true, y_pred, threshold=0.5)
    assert acc == 1.0


def test_accuracy_score_threshold():
    """AC-Metrics-1: Threshold affects accuracy."""
    y_true = [0, 0, 1, 1]
    y_pred = [0.4, 0.3, 0.6, 0.7]

    acc_05 = accuracy_score(y_true, y_pred, threshold=0.5)
    acc_04 = accuracy_score(y_true, y_pred, threshold=0.4)

    assert acc_05 == 1.0
    assert acc_04 < 1.0  # 0.4 would be predicted as 1, making first two wrong


def test_precision_recall_f1_perfect():
    """AC-Metrics-1: Perfect predictions have precision/recall/F1 of 1."""
    y_true = [0, 0, 1, 1]
    y_pred = [0.1, 0.2, 0.9, 0.8]

    precision, recall, f1 = precision_recall_f1(y_true, y_pred, threshold=0.5)

    assert precision == 1.0
    assert recall == 1.0
    assert f1 == 1.0


def test_precision_recall_f1_known_values():
    """AC-Metrics-1: Precision/recall match manual calculation."""
    y_true = [1, 0, 1, 0]
    y_pred = [0.8, 0.6, 0.9, 0.4]  # threshold 0.5 -> [1, 1, 1, 0]

    # TP=2 (indices 0,2), FP=1 (index 1), FN=0, TN=1 (index 3)
    # Precision = TP/(TP+FP) = 2/3
    # Recall = TP/(TP+FN) = 2/2 = 1.0
    # F1 = 2*P*R/(P+R) = 2*(2/3)*1/(2/3+1) = 4/3 / 5/3 = 4/5

    precision, recall, f1 = precision_recall_f1(y_true, y_pred, threshold=0.5)

    assert math.isclose(precision, 2 / 3, abs_tol=1e-9)
    assert math.isclose(recall, 1.0, abs_tol=1e-9)
    assert math.isclose(f1, 0.8, abs_tol=1e-9)


def test_precision_recall_no_positives():
    """AC-Metrics-1: Handle edge case with no predicted positives."""
    y_true = [0, 0, 1, 1]
    y_pred = [0.1, 0.2, 0.3, 0.4]  # All below 0.5

    precision, recall, f1 = precision_recall_f1(y_true, y_pred, threshold=0.5)

    assert precision == 0.0
    assert recall == 0.0
    assert f1 == 0.0


def test_calibration_curve_perfect():
    """AC-Metrics-2: Perfect calibration has predicted = actual."""
    # Create perfectly calibrated predictions
    y_true = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    y_pred = [0.0, 0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9, 1.0]

    curve = calibration_curve(y_true, y_pred, n_bins=2)

    # Low bin: 0.0-0.4, should have mean_actual ≈ 0
    # High bin: 0.6-1.0, should have mean_actual ≈ 1
    assert len(curve) == 2
    assert curve[0]["mean_actual"] < 0.5
    assert curve[1]["mean_actual"] > 0.5


def test_calibration_curve_bins():
    """AC-Metrics-2: Calibration curve creates correct number of bins."""
    y_true = [0, 1] * 50  # 100 examples
    y_pred = [i / 100 for i in range(100)]

    curve = calibration_curve(y_true, y_pred, n_bins=5)

    assert len(curve) == 5
    assert all(bin_data["count"] > 0 for bin_data in curve)


def test_compute_metrics_complete():
    """AC-Metrics-1: compute_metrics returns all expected fields."""
    y_true = [0, 0, 1, 1]
    y_pred = [0.2, 0.3, 0.8, 0.9]

    metrics = compute_metrics(y_true, y_pred)

    required_fields = [
        "brier_score",
        "accuracy",
        "precision",
        "recall",
        "f1",
        "mean_prediction",
        "mean_label",
        "num_examples",
    ]

    for field in required_fields:
        assert field in metrics

    assert metrics["num_examples"] == 4
    assert 0 <= metrics["brier_score"] <= 1
    assert 0 <= metrics["accuracy"] <= 1


def test_legacy_accuracy_function():
    """Ensure legacy accuracy function still works."""
    from eval.metrics import accuracy

    y_true = [1, 0, 1, 0]
    y_pred = [1, 0, 1, 1]

    acc = accuracy(y_true, y_pred)
    assert acc == 0.75
