import math
from dataclasses import astuple, dataclass
from typing import Tuple, Any
from statistics import NormalDist


@dataclass
class StatisticalAnalysis:
    """Class for statistical analysis results of test runs."""

    failure_count: int
    sample_size: int
    proportion: float
    standard_error: float
    margin_of_error: float
    confidence_interval_prop: Tuple[float, float]
    confidence_interval_count: Tuple[int, int]

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
            "proportion",
            "standard_error",
            "margin_of_error",
            "confidence_proportion_lower",
            "confidence_proportion_upper",
            "confidence_lower",
            "confidence_upper",
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

    # Determine z-score for 90% confidence level using NormalDist
    z = NormalDist().inv_cdf(0.95)  # For 90% CI, we need 95% percentile (two-tailed)

    # Calculate standard error
    se = math.sqrt(p_hat * (1 - p_hat) / sample_size)

    # Calculate margin of error
    me = z * se

    # Calculate confidence interval bounds as proportions
    lower_bound_prop = p_hat - me
    upper_bound_prop = p_hat + me

    # Convert proportion bounds to integer counts
    lower_bound_count = math.ceil(lower_bound_prop * sample_size)
    upper_bound_count = int(upper_bound_prop * sample_size)

    return StatisticalAnalysis(
        failure_count=failure_count,
        sample_size=sample_size,
        proportion=p_hat,
        standard_error=se,
        margin_of_error=me,
        confidence_interval_prop=(lower_bound_prop, upper_bound_prop),
        confidence_interval_count=(lower_bound_count, upper_bound_count),
    )
