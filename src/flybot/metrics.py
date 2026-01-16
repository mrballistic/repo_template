"""
Observability metrics for Fly Bot.

Provides counters and histograms for:
- Request latency
- Error counts by type
- Dependency latency
- Fallback usage
- Return coverage (# eligible flights)
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any


class MetricsCollector:
    """In-memory metrics collector (replace with Prometheus/StatsD in production)."""

    def __init__(self) -> None:
        self.request_latencies: list[int] = []
        self.error_counts: dict[str, int] = defaultdict(int)
        self.dependency_latencies: dict[str, list[int]] = defaultdict(list)
        self.fallback_count: int = 0
        self.return_coverages: list[int] = []

    def record_request_latency(self, latency_ms: int) -> None:
        """Record request latency in milliseconds."""
        self.request_latencies.append(latency_ms)

    def record_error(self, error_type: str) -> None:
        """Increment error counter for given error type."""
        self.error_counts[error_type] += 1

    def record_dependency_latency(self, dependency: str, latency_ms: int) -> None:
        """Record latency for a specific dependency call."""
        self.dependency_latencies[dependency].append(latency_ms)

    def record_fallback(self) -> None:
        """Increment fallback counter (baseline used instead of ML)."""
        self.fallback_count += 1

    def record_return_coverage(self, eligible_count: int) -> None:
        """Record number of eligible return flights."""
        self.return_coverages.append(eligible_count)

    def get_summary(self) -> dict[str, Any]:
        """Get summary of all metrics."""
        return {
            "request_latency_ms": self._histogram_summary(self.request_latencies),
            "errors": dict(self.error_counts),
            "dependency_latency_ms": {
                dep: self._histogram_summary(latencies)
                for dep, latencies in self.dependency_latencies.items()
            },
            "fallback_count": self.fallback_count,
            "return_coverage": self._histogram_summary(self.return_coverages),
        }

    def reset(self) -> None:
        """Reset all metrics (useful for testing)."""
        self.request_latencies.clear()
        self.error_counts.clear()
        self.dependency_latencies.clear()
        self.fallback_count = 0
        self.return_coverages.clear()

    def _histogram_summary(self, values: list[int]) -> dict[str, Any]:
        """Generate summary statistics for histogram data."""
        if not values:
            return {
                "count": 0,
                "sum": 0,
                "min": None,
                "max": None,
                "p50": None,
                "p95": None,
                "p99": None,
            }

        sorted_values = sorted(values)
        count = len(sorted_values)

        return {
            "count": count,
            "sum": sum(sorted_values),
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "p50": sorted_values[int(count * 0.50)],
            "p95": sorted_values[int(count * 0.95)] if count > 1 else sorted_values[0],
            "p99": sorted_values[int(count * 0.99)] if count > 1 else sorted_values[0],
        }


# Global singleton metrics collector
_metrics = MetricsCollector()


def record_request_latency(latency_ms: int) -> None:
    """Record request latency in milliseconds."""
    _metrics.record_request_latency(latency_ms)


def record_error(error_type: str) -> None:
    """Increment error counter for given error type."""
    _metrics.record_error(error_type)


def record_dependency_latency(dependency: str, latency_ms: int) -> None:
    """Record latency for a specific dependency call."""
    _metrics.record_dependency_latency(dependency, latency_ms)


def record_fallback() -> None:
    """Increment fallback counter (baseline used instead of ML)."""
    _metrics.record_fallback()


def record_return_coverage(eligible_count: int) -> None:
    """Record number of eligible return flights."""
    _metrics.record_return_coverage(eligible_count)


def get_metrics_summary() -> dict[str, Any]:
    """Get summary of all metrics."""
    return _metrics.get_summary()


def reset_metrics() -> None:
    """Reset all metrics (useful for testing)."""
    _metrics.reset()
