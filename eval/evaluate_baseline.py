"""Evaluation script for baseline model.

Computes metrics (Brier score, accuracy, calibration) on held-out dataset.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from eval.dataset import EvalExample, load_dataset
from eval.metrics import (
    calibration_curve,
    compute_metrics,
)
from flybot.baseline import baseline_return_probability


def evaluate_baseline(
    examples: list[EvalExample],
    threshold: float = 0.5,
) -> dict:
    """Evaluate baseline model on dataset.

    Args:
        examples: List of evaluation examples
        threshold: Threshold for converting probabilities to binary predictions

    Returns:
        Dictionary of metrics
    """
    # Make predictions
    predictions = []
    labels = []

    for ex in examples:
        prob = baseline_return_probability(
            seats_required=ex.seats_required,
            capacity=ex.capacity,
            time_to_departure_hours=ex.time_to_departure_hours,
        )
        predictions.append(prob)
        labels.append(ex.label_cleared)

    # Compute metrics
    metrics = compute_metrics(labels, predictions, threshold=threshold)

    return metrics


def evaluate_by_scenario(examples: list[EvalExample]) -> dict:
    """Evaluate baseline model by scenario difficulty."""
    by_scenario = {}
    for ex in examples:
        by_scenario.setdefault(ex.scenario, []).append(ex)

    results = {}
    for scenario, scenario_examples in sorted(by_scenario.items()):
        metrics = evaluate_baseline(scenario_examples)
        results[scenario] = metrics

    return results


def print_metrics(metrics: dict, prefix: str = "") -> None:
    """Pretty print metrics."""
    print(f"{prefix}Brier Score: {metrics['brier_score']:.4f}")
    print(f"{prefix}Accuracy: {metrics['accuracy']:.2%}")
    print(f"{prefix}Precision: {metrics['precision']:.2%}")
    print(f"{prefix}Recall: {metrics['recall']:.2%}")
    print(f"{prefix}F1 Score: {metrics['f1']:.2%}")
    print(f"{prefix}Mean Prediction: {metrics['mean_prediction']:.2%}")
    print(f"{prefix}Mean Label: {metrics['mean_label']:.2%}")


def run_evaluation(dataset_path: Path) -> dict:
    """Run full evaluation pipeline."""
    print(f"Loading dataset from {dataset_path}...")
    examples = load_dataset(dataset_path)
    print(f"Loaded {len(examples)} examples\n")

    # Overall metrics
    print("=" * 60)
    print("OVERALL METRICS")
    print("=" * 60)
    overall_metrics = evaluate_baseline(examples)
    print_metrics(overall_metrics)

    # By scenario
    print("\n" + "=" * 60)
    print("METRICS BY SCENARIO")
    print("=" * 60)
    scenario_metrics = evaluate_by_scenario(examples)

    for scenario, metrics in sorted(scenario_metrics.items()):
        print(f"\n{scenario.upper()}:")
        print_metrics(metrics, prefix="  ")

    # Calibration analysis
    print("\n" + "=" * 60)
    print("CALIBRATION ANALYSIS")
    print("=" * 60)

    labels = [ex.label_cleared for ex in examples]
    predictions = [
        baseline_return_probability(ex.seats_required, ex.capacity, ex.time_to_departure_hours)
        for ex in examples
    ]

    calibration = calibration_curve(labels, predictions, n_bins=5)
    print("\nCalibration curve (predicted vs actual):")
    for bin_data in calibration:
        print(
            f"  Predicted: {bin_data['mean_predicted']:.2%}, "
            f"Actual: {bin_data['mean_actual']:.2%}, "
            f"Count: {bin_data['count']}"
        )

    # Save results
    results = {
        "overall": overall_metrics,
        "by_scenario": scenario_metrics,
        "calibration": calibration,
    }

    return results


def save_results(results: dict, output_path: Path) -> None:
    """Save evaluation results to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    # Generate dataset if it doesn't exist
    dataset_path = Path("eval/data/baseline_eval_dataset.json")
    if not dataset_path.exists():
        print("Dataset not found. Generating...")
        from eval.dataset import generate_synthetic_dataset, save_dataset

        examples = generate_synthetic_dataset(num_examples=300)
        save_dataset(examples, dataset_path)
        print()

    # Run evaluation
    results = run_evaluation(dataset_path)

    # Save results
    output_path = Path("eval/results/baseline_eval_results.json")
    save_results(results, output_path)

    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
