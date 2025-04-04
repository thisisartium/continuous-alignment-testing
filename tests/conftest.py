import csv
import io
import os
from typing import Callable, Generator, Optional

import matplotlib
import pytest

from cat_ai.helpers.helpers import root_dir
from cat_ai.reporter import Reporter
from cat_ai.statistical_analysis import StatisticalAnalysis, analyse_measure_from_test_sample


@pytest.fixture
def test_name(request: pytest.FixtureRequest) -> str:
    return str(request.node.name)


@pytest.fixture
def reporter_factory(test_name: str) -> Callable:
    """Factory fixture for creating Reporter instances with default settings."""

    def _create_reporter(
        unique_id: Optional[str] = None,
    ) -> Reporter:
        return Reporter(test_name=test_name, output_dir=root_dir(), unique_id=unique_id)

    return _create_reporter


@pytest.fixture
def tmp_reporter() -> "Reporter":
    """Creates a reporter that writes to /tmp."""
    return Reporter(test_name="test_fixture", output_dir="/tmp")


@pytest.fixture
def analyze_failure_rate() -> Callable:
    """Helper fixture to analyze failure rates."""

    def _analyze(failure_count: int, sample_size: int) -> StatisticalAnalysis:
        return analyse_measure_from_test_sample(failure_count, sample_size)

    return _analyze


def export_results_to_csv(results: list[StatisticalAnalysis]) -> str:
    output = io.StringIO(newline="\n")
    writer = csv.writer(output, lineterminator="\n")

    # Write header
    writer.writerow(StatisticalAnalysis.get_csv_headers())

    # Write rows
    for result in results:
        writer.writerow(result.as_csv_row())

    return output.getvalue()


@pytest.fixture
def configure_matplotlib() -> Generator[None, None, None]:
    """Configure matplotlib for consistent snapshot testing."""
    matplotlib.use("Agg")  # Force CPU-based renderer

    # Configure for deterministic rendering
    matplotlib.rcParams.update(
        {
            "figure.max_open_warning": 0,
            "svg.hashsalt": "matplotlib",
            "figure.dpi": 100,
            "savefig.dpi": 100,
            "path.simplify": False,
            "agg.path.chunksize": 0,
            "pdf.fonttype": 42,  # Ensures text is stored as text, not paths
            "ps.fonttype": 42,
        }
    )

    yield

    # Clean up any open figures
    import matplotlib.pyplot as plt

    plt.close("all")


def running_in_ci() -> bool:
    """Check if tests are running in CI environment."""
    return os.getenv("CI") is not None
