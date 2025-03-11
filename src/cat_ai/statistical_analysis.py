import math
from dataclasses import astuple, dataclass
from typing import Tuple, Any
from statistics import NormalDist


@dataclass
class StatisticalAnalysis:
    """Class for statistical analysis results of test runs."""

    failure_count: int
    sample_size: int
    margin_of_error_count: int
    confidence_interval_count: Tuple[int, int]
    proportion: float
    standard_error: float
    margin_of_error: float
    confidence_interval_prop: Tuple[float, float]

    def as_csv_row(self) -> list:
        """Return a flat tuple representation suitable for CSV writing."""
        # Unpack nested tuples for CSV-friendly format
        flat_data: list[Any] = []
        for item in astuple(self):
            if isinstance(item, tuple):
                flat_data.extend(item)
            else:
                flat_data.append(item)
        return flat_data

    @classmethod
    def get_csv_headers(cls) -> list[str]:
        """Generate CSV headers based on class fields."""
        headers = [
            "failure_count",
            "sample_size",
            "margin_of_error_count",
            "confidence_lower",
            "confidence_upper",
            "proportion",
            "standard_error",
            "margin_of_error",
            "confidence_proportion_lower",
            "confidence_proportion_upper",
        ]
        return headers


def analyse_sample_from_test(failure_count: int, sample_size: int) -> StatisticalAnalysis:
    """
    Calculate the error margin and confidence interval for a given sample.

    Args:
        failure_count (int): Number of failures in the sample
        sample_size (int): Total size of the sample

    Returns:
        StatisticalAnalysis: Object containing all statistical analysis data
    """
    # Calculate sample proportion
    p_hat = failure_count / sample_size

    # Define our 90% confidence level as a constant
    confidence_for_non_determinism: int = 90
    confidence_level_percent = confidence_for_non_determinism
    confidence_level = confidence_level_percent / 100.0

    # For a two-tailed, we need (1 + confidence_level)/2 percentile
    confidence_percentile = (1 + confidence_level) / 2  # Derives 0.95 from our 90% constant
    # Calculate the appropriate z-score for our confidence level
    z = NormalDist().inv_cdf(confidence_percentile)
    # Calculate standard error
    se = math.sqrt(p_hat * (1 - p_hat) / sample_size)

    # Calculate margin of error
    me = z * se

    # Calculate confidence interval bounds as proportions
    lower_bound_prop = p_hat - me
    upper_bound_prop = p_hat + me

    # Convert proportion bounds to integer counts
    lower_bound_count: int = math.ceil(lower_bound_prop * sample_size)
    upper_bound_count: int = int(upper_bound_prop * sample_size)

    half_max_distance: float = (upper_bound_count - lower_bound_count) / 2
    margin_of_error: float = me * sample_size
    margin_of_error_count = int(max(margin_of_error, half_max_distance))

    return StatisticalAnalysis(
        failure_count=failure_count,
        sample_size=sample_size,
        proportion=p_hat,
        standard_error=se,
        margin_of_error=me,
        confidence_interval_prop=(lower_bound_prop, upper_bound_prop),
        confidence_interval_count=(lower_bound_count, upper_bound_count),
        margin_of_error_count=margin_of_error_count,
    )
