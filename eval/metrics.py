from __future__ import annotations

from collections.abc import Iterable


def accuracy(y_true: Iterable[int], y_pred: Iterable[int]) -> float:
    """Legacy accuracy function - kept for compatibility."""
    yt = list(y_true)
    yp = list(y_pred)
    if len(yt) != len(yp):
        raise ValueError("y_true and y_pred must have the same length")
    if not yt:
        raise ValueError("inputs must be non-empty")
    correct = sum(1 for a, b in zip(yt, yp, strict=True) if a == b)
    return correct / len(yt)


def brier_score(y_true: list[int], y_pred_proba: list[float]) -> float:
    """Compute Brier score (mean squared error of probabilities).

    Lower is better. Perfect predictions = 0.0, worst = 1.0.

    Args:
        y_true: Binary labels (0 or 1)
        y_pred_proba: Predicted probabilities [0, 1]

    Returns:
        Brier score (MSE of predictions)
    """
    if len(y_true) != len(y_pred_proba):
        raise ValueError("y_true and y_pred_proba must have the same length")

    mse = sum((yt - yp) ** 2 for yt, yp in zip(y_true, y_pred_proba, strict=True)) / len(y_true)
    return mse


def accuracy_score(y_true: list[int], y_pred_proba: list[float], threshold: float = 0.5) -> float:
    """Compute accuracy from probabilities using threshold.

    Args:
        y_true: Binary labels (0 or 1)
        y_pred_proba: Predicted probabilities [0, 1]
        threshold: Threshold for converting to binary (default 0.5)

    Returns:
        Accuracy (fraction correct)
    """
    y_pred_binary = [1 if p >= threshold else 0 for p in y_pred_proba]
    correct = sum(yt == yp for yt, yp in zip(y_true, y_pred_binary, strict=True))
    return correct / len(y_true)


def precision_recall_f1(
    y_true: list[int], y_pred_proba: list[float], threshold: float = 0.5
) -> tuple[float, float, float]:
    """Compute precision, recall, and F1 score.

    Args:
        y_true: Binary labels (0 or 1)
        y_pred_proba: Predicted probabilities [0, 1]
        threshold: Threshold for converting to binary

    Returns:
        (precision, recall, f1) tuple
    """
    y_pred_binary = [1 if p >= threshold else 0 for p in y_pred_proba]

    tp = sum(yt == 1 and yp == 1 for yt, yp in zip(y_true, y_pred_binary, strict=True))
    fp = sum(yt == 0 and yp == 1 for yt, yp in zip(y_true, y_pred_binary, strict=True))
    fn = sum(yt == 1 and yp == 0 for yt, yp in zip(y_true, y_pred_binary, strict=True))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return precision, recall, f1


def calibration_curve(y_true: list[int], y_pred_proba: list[float], n_bins: int = 10) -> list[dict]:
    """Compute calibration curve (predicted vs actual probabilities by bin).

    Args:
        y_true: Binary labels (0 or 1)
        y_pred_proba: Predicted probabilities [0, 1]
        n_bins: Number of bins

    Returns:
        List of dicts with mean_predicted, mean_actual, count per bin
    """
    # Sort by predicted probability
    sorted_pairs = sorted(zip(y_pred_proba, y_true, strict=True))

    bin_size = len(sorted_pairs) // n_bins
    calibration = []

    for i in range(n_bins):
        start_idx = i * bin_size
        end_idx = start_idx + bin_size if i < n_bins - 1 else len(sorted_pairs)

        bin_pairs = sorted_pairs[start_idx:end_idx]
        if not bin_pairs:
            continue

        preds = [p for p, _ in bin_pairs]
        labels = [label for _, label in bin_pairs]

        calibration.append(
            {
                "mean_predicted": sum(preds) / len(preds),
                "mean_actual": sum(labels) / len(labels),
                "count": len(bin_pairs),
            }
        )

    return calibration


def compute_metrics(y_true: list[int], y_pred_proba: list[float], threshold: float = 0.5) -> dict:
    """Compute all evaluation metrics.

    Args:
        y_true: Binary labels (0 or 1)
        y_pred_proba: Predicted probabilities [0, 1]
        threshold: Threshold for binary classification

    Returns:
        Dictionary of metrics
    """
    brier = brier_score(y_true, y_pred_proba)
    acc = accuracy_score(y_true, y_pred_proba, threshold)
    precision, recall, f1 = precision_recall_f1(y_true, y_pred_proba, threshold)

    return {
        "brier_score": brier,
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "mean_prediction": sum(y_pred_proba) / len(y_pred_proba),
        "mean_label": sum(y_true) / len(y_true),
        "num_examples": len(y_true),
    }
