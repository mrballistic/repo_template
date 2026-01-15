"""Synthetic dataset generator for evaluation.

Creates realistic test scenarios for baseline model evaluation.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path


@dataclass
class EvalExample:
    """Single evaluation example."""

    example_id: str
    seats_required: int
    capacity: int
    time_to_departure_hours: float
    label_cleared: int  # 1 if cleared, 0 if not
    scenario: str  # Description of scenario


def generate_synthetic_dataset(num_examples: int = 100) -> list[EvalExample]:
    """Generate synthetic evaluation dataset with known patterns.
    
    Creates scenarios with varying difficulty:
    - Easy: Solo travelers, large capacity, advance notice
    - Medium: Small groups, medium capacity, moderate notice
    - Hard: Large groups, small capacity, short notice
    """
    examples = []
    
    # Easy scenarios (high success rate)
    for i in range(num_examples // 3):
        example = EvalExample(
            example_id=f"easy_{i:03d}",
            seats_required=1,
            capacity=150 + (i % 50),
            time_to_departure_hours=4.0 + (i % 4),
            label_cleared=1 if i % 10 < 8 else 0,  # 80% success
            scenario="easy",
        )
        examples.append(example)
    
    # Medium scenarios (moderate success rate)
    for i in range(num_examples // 3):
        example = EvalExample(
            example_id=f"medium_{i:03d}",
            seats_required=2 + (i % 2),
            capacity=100 + (i % 30),
            time_to_departure_hours=2.0 + (i % 3),
            label_cleared=1 if i % 10 < 5 else 0,  # 50% success
            scenario="medium",
        )
        examples.append(example)
    
    # Hard scenarios (low success rate)
    for i in range(num_examples - 2 * (num_examples // 3)):
        example = EvalExample(
            example_id=f"hard_{i:03d}",
            seats_required=4 + (i % 4),
            capacity=80 + (i % 20),
            time_to_departure_hours=1.0 + (i % 2) * 0.5,
            label_cleared=1 if i % 10 < 2 else 0,  # 20% success
            scenario="hard",
        )
        examples.append(example)
    
    return examples


def save_dataset(examples: list[EvalExample], output_path: Path) -> None:
    """Save dataset to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "num_examples": len(examples),
            "description": "Synthetic evaluation dataset for baseline model",
        },
        "examples": [asdict(ex) for ex in examples],
    }
    
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved {len(examples)} examples to {output_path}")


def load_dataset(dataset_path: Path) -> list[EvalExample]:
    """Load dataset from JSON file."""
    with open(dataset_path) as f:
        data = json.load(f)
    
    examples = [EvalExample(**ex) for ex in data["examples"]]
    return examples


if __name__ == "__main__":
    # Generate and save dataset
    dataset_path = Path("eval/data/baseline_eval_dataset.json")
    examples = generate_synthetic_dataset(num_examples=300)
    save_dataset(examples, dataset_path)
    
    # Print statistics
    print(f"\nDataset statistics:")
    print(f"  Total examples: {len(examples)}")
    
    by_scenario = {}
    for ex in examples:
        by_scenario.setdefault(ex.scenario, []).append(ex)
    
    for scenario, scenario_examples in sorted(by_scenario.items()):
        cleared_count = sum(ex.label_cleared for ex in scenario_examples)
        print(f"  {scenario.capitalize()}: {len(scenario_examples)} examples, "
              f"{cleared_count}/{len(scenario_examples)} cleared "
              f"({100*cleared_count/len(scenario_examples):.1f}%)")
