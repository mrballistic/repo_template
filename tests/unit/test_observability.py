"""
Unit tests for observability metrics.

Tests verify:
- Metric recording functions work correctly
- Counters increment properly
- Histograms record values
- Metrics can be retrieved
"""

from flybot.metrics import (
    get_metrics_summary,
    record_dependency_latency,
    record_error,
    record_fallback,
    record_request_latency,
    record_return_coverage,
    reset_metrics,
)


def test_record_request_latency():
    """Verify request latency is recorded in histogram."""
    reset_metrics()

    record_request_latency(150)
    record_request_latency(200)
    record_request_latency(180)

    summary = get_metrics_summary()

    assert "request_latency_ms" in summary
    assert summary["request_latency_ms"]["count"] == 3
    assert summary["request_latency_ms"]["sum"] == 530
    assert summary["request_latency_ms"]["min"] == 150
    assert summary["request_latency_ms"]["max"] == 200


def test_record_error_increments_counter():
    """Verify error counter increments by error type."""
    reset_metrics()

    record_error("empties_timeout")
    record_error("empties_timeout")
    record_error("schedule_error")

    summary = get_metrics_summary()

    assert "errors" in summary
    assert summary["errors"]["empties_timeout"] == 2
    assert summary["errors"]["schedule_error"] == 1


def test_record_dependency_latency():
    """Verify dependency latency is tracked per dependency."""
    reset_metrics()

    record_dependency_latency("empties", 45)
    record_dependency_latency("empties", 50)
    record_dependency_latency("schedule", 75)

    summary = get_metrics_summary()

    assert "dependency_latency_ms" in summary
    assert "empties" in summary["dependency_latency_ms"]
    assert "schedule" in summary["dependency_latency_ms"]
    assert summary["dependency_latency_ms"]["empties"]["count"] == 2
    assert summary["dependency_latency_ms"]["empties"]["sum"] == 95
    assert summary["dependency_latency_ms"]["schedule"]["count"] == 1
    assert summary["dependency_latency_ms"]["schedule"]["sum"] == 75


def test_record_fallback_increments_counter():
    """Verify fallback counter tracks when baseline used."""
    reset_metrics()

    record_fallback()
    record_fallback()

    summary = get_metrics_summary()

    assert "fallback_count" in summary
    assert summary["fallback_count"] == 2


def test_record_return_coverage():
    """Verify return coverage histogram tracks eligible returns."""
    reset_metrics()

    record_return_coverage(5)
    record_return_coverage(3)
    record_return_coverage(8)
    record_return_coverage(0)  # No eligible returns

    summary = get_metrics_summary()

    assert "return_coverage" in summary
    assert summary["return_coverage"]["count"] == 4
    assert summary["return_coverage"]["sum"] == 16
    assert summary["return_coverage"]["min"] == 0
    assert summary["return_coverage"]["max"] == 8


def test_reset_metrics_clears_all():
    """Verify reset clears all metrics."""
    reset_metrics()

    # Record some metrics
    record_request_latency(100)
    record_error("test_error")
    record_fallback()

    # Verify they exist
    summary = get_metrics_summary()
    assert summary["request_latency_ms"]["count"] > 0
    assert summary["errors"]["test_error"] > 0
    assert summary["fallback_count"] > 0

    # Reset
    reset_metrics()

    # Verify cleared
    summary = get_metrics_summary()
    assert summary["request_latency_ms"]["count"] == 0
    assert len(summary["errors"]) == 0
    assert summary["fallback_count"] == 0


def test_metrics_collector_singleton():
    """Verify MetricsCollector maintains state across calls."""
    reset_metrics()

    # Record using different functions
    record_request_latency(100)
    record_error("error1")
    record_fallback()

    # All should be in same collector
    summary = get_metrics_summary()
    assert summary["request_latency_ms"]["count"] == 1
    assert "error1" in summary["errors"]
    assert summary["fallback_count"] == 1


def test_multiple_error_types_tracked_separately():
    """Verify different error types are tracked independently."""
    reset_metrics()

    record_error("empties_timeout")
    record_error("empties_timeout")
    record_error("schedule_error")
    record_error("validation_error")
    record_error("schedule_error")

    summary = get_metrics_summary()

    assert summary["errors"]["empties_timeout"] == 2
    assert summary["errors"]["schedule_error"] == 2
    assert summary["errors"]["validation_error"] == 1


def test_latency_percentiles():
    """Verify latency metrics calculate percentiles correctly."""
    reset_metrics()

    # Record 100 values
    for i in range(1, 101):
        record_request_latency(i * 10)  # 10, 20, 30, ..., 1000

    summary = get_metrics_summary()
    latency = summary["request_latency_ms"]

    assert latency["count"] == 100
    assert latency["min"] == 10
    assert latency["max"] == 1000
    assert latency["p50"] == 500 or latency["p50"] == 510  # Median
    assert latency["p95"] >= 900  # 95th percentile
    assert latency["p99"] >= 980  # 99th percentile


def test_zero_coverage_tracked():
    """Verify zero eligible returns is tracked (important edge case)."""
    reset_metrics()

    record_return_coverage(0)

    summary = get_metrics_summary()

    assert summary["return_coverage"]["count"] == 1
    assert summary["return_coverage"]["sum"] == 0
    assert summary["return_coverage"]["min"] == 0
