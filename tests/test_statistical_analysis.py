import csv
import io
import os

import pytest
from statistics import NormalDist
import math
import matplotlib.pyplot as plt
import numpy as np

from cat_ai.statistical_analysis import analyse_sample_from_test, StatisticalAnalysis


@pytest.mark.parametrize(
    "failure_count,sample_size,expected_proportion",
    [
        (0, 100, 0.0),
        (6, 100, 0.06),
        (100, 100, 1.0),
    ],
)
def test_analyse_sample_from_test(failure_count, sample_size, expected_proportion):
    """Test the statistical analysis function with various edge cases."""
    result = analyse_sample_from_test(failure_count, sample_size)

    # Basic assertions
    assert result.failure_count == failure_count
    assert result.sample_size == sample_size
    assert result.proportion == expected_proportion

    # Calculate expected values for validation
    p_hat = failure_count / sample_size
    z = NormalDist().inv_cdf(0.95)  # 95th percentile for 90% CI
    expected_se = math.sqrt(p_hat * (1 - p_hat) / sample_size) if p_hat * (1 - p_hat) > 0 else 0
    expected_me = z * expected_se

    # Validate calculations
    assert result.standard_error == pytest.approx(expected_se)
    assert result.margin_of_error == pytest.approx(expected_me)

    # Check confidence interval bounds
    expected_lower = max(0.0, p_hat - expected_me)
    expected_upper = min(1.0, p_hat + expected_me)
    assert result.confidence_interval_prop[0] == pytest.approx(expected_lower)
    assert result.confidence_interval_prop[1] == pytest.approx(expected_upper)

    # Validate integer confidence bounds
    expected_lower_count = math.ceil(expected_lower * sample_size)
    expected_upper_count = int(expected_upper * sample_size)
    assert result.confidence_interval_count[0] == expected_lower_count
    assert result.confidence_interval_count[1] == expected_upper_count

    # Test boundary conditions
    if failure_count == 0:
        assert result.confidence_interval_prop[0] == 0.0
    if failure_count == sample_size:
        assert result.confidence_interval_prop[1] == 1.0


@pytest.mark.parametrize(
    "failures, total, expected_error, expected_ci",
    [
        (0, 100, 0.0, (0, 0)),
        (6, 100, 0.023748684174075833, (3, 9)),
        (50, 100, 0.05, (42, 58)),
        (95, 100, 0.021794494717703377, (92, 98)),
        (100, 100, 0.0, (100, 100)),
    ],
)
def test_edges_cases(failures, total, expected_error, expected_ci):
    result = analyse_sample_from_test(failures, total)
    assert result.standard_error == expected_error
    assert result.confidence_interval_count == expected_ci


def export_results_to_csv_string(results: list[StatisticalAnalysis]) -> str:
    """Export a list of StatisticalAnalysis objects to a CSV-formatted string."""
    # Create a CSV writer with MacOS-style newlines to match the snapshot
    output = io.StringIO(newline="\n")  # Let CSV writer handle newline translation
    writer = csv.writer(output, lineterminator="\n")  # Explicitly set line terminator

    # Write header
    writer.writerow(StatisticalAnalysis.get_csv_headers())

    # Write rows
    for result in results:
        writer.writerow(result.as_csv_row())

    return output.getvalue()


def running_in_ci() -> bool:
    return os.getenv("CI") is not None


@pytest.mark.skipif(running_in_ci(), reason="Unstable image comparison in CI")
def test_failure_rate_bar_graph(snapshot):
    # Sample data points - choosing strategic values to test boundary conditions
    failure_counts = list(range(101))
    assert failure_counts[0] == 0
    assert failure_counts[100] == 100
    sample_size = 100

    # Calculate results for each data point
    results = [analyse_sample_from_test(f, sample_size) for f in failure_counts]
    csv = export_results_to_csv_string(results)
    csv_bytes = io.BytesIO(csv.encode("utf-8"))
    snapshot.assert_match(csv_bytes.getvalue(), "failure_rate_results.csv")
    rates = [r.proportion for r in results]
    errors = [r.margin_of_error for r in results]

    # Create the bar plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot bars with error bars
    bars = ax.bar(
        failure_counts, rates, yerr=errors, capsize=5, color="steelblue", alpha=0.7, width=8
    )

    # # Add annotations on top of each bar
    # for bar, rate, error in zip(bars, rates, errors):
    #     height = bar.get_height()
    #     ax.text(
    #         bar.get_x() + bar.get_width() / 2.0,
    #         height + error + 0.01,
    #         f"{rate:.2f}±{error:.2f}",
    #         ha="center",
    #         va="bottom",
    #         rotation=0,
    #         fontsize=9,
    #     )

    # Add labels and title
    ax.set_xlabel("Number of Failures")
    ax.set_ylabel("Failure Rate")
    ax.set_title("Failure Rate with Error Margins")
    ax.set_ylim(0, 1.2)  # Set y-axis to accommodate annotations
    ax.grid(True, linestyle="--", alpha=0.7, axis="both")

    # Deterministic rendering for snapshot testing
    plt.tight_layout()
    buf = io.BytesIO()
    plt.rcParams["svg.hashsalt"] = "matplotlib"
    os.environ["SOURCE_DATE_EPOCH"] = "1234567890"
    fig.savefig(buf, format="png")
    buf.seek(0)

    # Compare with snapshot
    snapshot.assert_match(buf.read(), "failure_rate_bar_graph.png")

    plt.close()


@pytest.mark.skipif(running_in_ci(), reason="Unstable image comparison in CI")
def test_failure_rate_graph(snapshot):
    # Generate a series of failure rates
    totals = np.ones(100) * 100
    failures = np.arange(0, 100)

    # Calculate results for each rate
    results = [analyse_sample_from_test(f, t) for f, t in zip(failures, totals)]

    # Extract data for plotting
    rates = [r.proportion for r in results]
    errors = [r.standard_error for r in results]
    failing_errors = [e for e in errors if e > 0.05]
    assert len(failing_errors) == 0, f"Errors exceeding threshold 0.05: {failing_errors}"
    lower_bounds = [r.confidence_interval_prop[0] for r in results]
    upper_bounds = [r.confidence_interval_prop[1] for r in results]

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(0, 100)

    # Plot the rate line
    ax.plot(x, rates, "b-", label="Failure Rate")

    # Plot confidence interval as shaded region
    ax.fill_between(
        x, lower_bounds, upper_bounds, alpha=0.3, color="blue", label="90% Confidence Interval"
    )

    # Add labels and title
    ax.set_xlabel("Number of Failures")
    ax.set_ylabel("Failure Rate")
    ax.set_title("Failure Rate with Confidence Intervals")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.7)

    # Save to buffer for snapshot comparison
    plt.tight_layout()
    buf = io.BytesIO()
    plt.rcParams["svg.hashsalt"] = "matplotlib"
    os.environ["SOURCE_DATE_EPOCH"] = "1234567890"
    fig.savefig(buf, format="png")
    buf.seek(0)

    # Compare with snapshot
    snapshot.assert_match(buf.read(), "failure_rate_graph.png")

    plt.close()
