import csv
import io
import math
import os
from statistics import NormalDist

import matplotlib

matplotlib.use("Agg")  # Force CPU-based renderer before any pyplot import

import matplotlib.pyplot as plt
import numpy as np
import pytest

from cat_ai.statistical_analysis import StatisticalAnalysis, analyse_measure_from_test_sample


def analyse_failure_rate_from_test_sample(
    failure_count: int, sample_size: int
) -> StatisticalAnalysis:
    return analyse_measure_from_test_sample(failure_count, sample_size)


@pytest.mark.parametrize(
    "failure_count,sample_size,expected_proportion",
    [(0, 100, 0.0), (6, 100, 0.06), (100, 100, 1.0), (1, 47, 0.0213)],
)
def test_analyse_sample_from_test(failure_count, sample_size, expected_proportion):
    """Test the statistical analysis function with various edge cases."""
    result = analyse_failure_rate_from_test_sample(failure_count, sample_size)

    # Basic assertions
    assert result.observation == failure_count
    assert result.sample_size == sample_size
    assert expected_proportion == pytest.approx(result.proportion, rel=0.01)

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
    assert max(0.0, result.confidence_interval_prop[0]) == pytest.approx(expected_lower, rel=0.001)
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
        (6, 100, 0.0237, (3, 9)),
        (50, 100, 0.05, (42, 58)),
        (95, 100, 0.0218, (92, 98)),
        (100, 100, 0.0, (100, 100)),
    ],
)
def test_edges_cases(failures, total, expected_error, expected_ci):
    result = analyse_failure_rate_from_test_sample(failures, total)
    print("hello world")
    assert math.isclose(result.standard_error, expected_error, abs_tol=0.0001)
    assert result.confidence_interval_count == expected_ci


next_success_after_97 = 0.9709704495337362
next_success_after_90 = 0.925327195595728
digress_from_0_999 = 0.9986779845027858

progress_from_0_999 = 0.9992400558756847


def test_measured_constants():
    assert 1.0 > progress_from_0_999 > 0.999
    assert 0.99 < digress_from_0_999 < 0.999
    assert 1.0 > next_success_after_90 > 0.90
    assert 1.0 > next_success_after_97 > 0.97


@pytest.mark.parametrize(
    "failures, total, current_success_rate, next_success_rate",
    [
        (0, 100, 0.97, next_success_after_97),
        (1, 47, 0.95, 0.9545),
        (0, 100, next_success_after_97, next_success_after_97),
        (1, 100, 0.97, next_success_after_97),
        (6, 100, 0.90, next_success_after_90),
        (10, 100, 0.90, next_success_after_90),
        (1, 100, 0.90, next_success_after_90),
        (50, 100, 0.5, 0.7088786593262133),
        (2, 100, 0.98, 0.9784860246113397),
        (1, 100, 0.99, 0.9868169565265201),
        (1, 1000, 0.999, digress_from_0_999),
        (0, 1000, 0.999, digress_from_0_999),
        (2, 1000, 0.999, digress_from_0_999),
        (1, 10000, 0.999, progress_from_0_999),
    ],
)
def test_next_success_rate(failures, total, current_success_rate, next_success_rate):
    result = analyse_failure_rate_from_test_sample(failures, total)
    assert result.next_success_rate(current_success_rate) == pytest.approx(
        next_success_rate, rel=0.001
    )


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


# This test is skipped on CI as it fails to render the difference due to Timeout >10.0s
# https://github.com/thisisartium/continuous-alignment-testing/issues/53
@pytest.mark.skipif(running_in_ci(), reason="Image comparison fails to produce diff on CI")
def test_failure_rate_bar_graph(snapshot):
    # Sample data points - choosing strategic values to test boundary conditions
    sample_size = 100
    failure_counts = list(range(sample_size + 1))
    assert failure_counts[0] == 0
    assert failure_counts[sample_size] == sample_size

    # Calculate results for each data point
    results = [analyse_failure_rate_from_test_sample(f, sample_size) for f in failure_counts]
    csv = export_results_to_csv_string(results)
    csv_bytes = io.BytesIO(csv.encode("utf-8"))
    snapshot.assert_match(csv_bytes.getvalue(), "failure_rate_results.csv")
    rates = [r.proportion for r in results]
    errors = [r.margin_of_error for r in results]

    # Create the bar plot
    # When creating the figure, set specific dimensions
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)  # Explicitly set DPI here too

    # Plot bars with error bars
    ax.bar(failure_counts, rates, yerr=errors, capsize=5, color="steelblue", alpha=0.7, width=8)

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

    # Add these parameters before saving the figure
    plt.rcParams["svg.hashsalt"] = "matplotlib"  # Fix the hash salt for deterministic rendering
    plt.rcParams["figure.dpi"] = 100  # Fix the DPI
    plt.rcParams["savefig.dpi"] = 100  # Fix the saving DPI
    plt.rcParams["path.simplify"] = False  # Don't simplify paths
    plt.rcParams["agg.path.chunksize"] = 0  # Disable path chunking

    # Before saving, set more explicit parameters
    fig.savefig(
        buf,
        format="png",
        metadata={"CreationDate": None},
        dpi=100,
        bbox_inches="tight",  # Consistent bounding box
        pad_inches=0.1,
    )  # Consistent padding

    # fig.savefig(buf, format="png", metadata={"CreationDate": None})
    buf.seek(0)

    # Compare with snapshot
    snapshot.assert_match(buf.read(), "failure_rate_bar_graph.png")

    plt.close()


# This test is skipped on CI as it fails to render the difference due to Timeout >10.0s
# https://github.com/thisisartium/continuous-alignment-testing/issues/53
@pytest.mark.skipif(running_in_ci(), reason="Image comparison fails to produce diff on CI")
def test_failure_rate_graph(snapshot):
    # Also useful to ensure thread safety and determinism
    matplotlib.rcParams["figure.max_open_warning"] = 0
    matplotlib.rcParams["pdf.fonttype"] = 42  # Ensures text is stored as text, not paths
    matplotlib.rcParams["ps.fonttype"] = 42

    # Generate a series of failure rates
    totals = [100] * 100
    failures = list(range(100))
    assert len(failures) == len(totals)
    # Calculate results for each rate
    results = [
        analyse_failure_rate_from_test_sample(f, t) for f, t in zip(failures, totals, strict=True)
    ]

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
    fig.savefig(buf, format="png", metadata={"CreationDate": None})
    buf.seek(0)

    # Compare with snapshot
    snapshot.assert_match(buf.read(), "failure_rate_graph.png")

    plt.close()
