import json
import logging
import re
from pathlib import Path

from settings import root_path

from cat_ai.statistical_analysis import analyse_measure_from_test_sample


def load_json_fixture(file_name: str) -> dict:
    """
    Utility function to load a JSON fixture file.

    :param file_name: Name of the JSON file to load.
    :return: Parsed JSON data as a dictionary.
    """
    json_path = root_path() / "tests" / "fixtures" / file_name
    with open(json_path, "r") as file:
        return json.load(file)


def natural_sort_key(s: Path):
    """Sort strings with embedded numbers in natural order."""
    return [
        int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", str(s.name))
    ]


def _assert_success_rate(actual: list[bool], expected: float):
    number_of_successes = sum(1 for r in actual if r)
    actual_success_rate = number_of_successes / len(actual)
    assert actual_success_rate >= 0.0, (
        f"Cannot have less than 0% success rate, was: {actual_success_rate}"
    )
    assert actual_success_rate <= 1.0, (
        f"Cannot have more than 100% success rate, was: {actual_success_rate}"
    )
    actual_count = len(actual)
    success_analysis = analyse_measure_from_test_sample(number_of_successes, actual_count)
    # Handle case when a list of results is passed
    lower_boundary = success_analysis.confidence_interval_prop[0]
    higher_boundary = success_analysis.confidence_interval_prop[1]
    recommendation_to_decrease = (
        success_analysis.proportion
        if success_analysis.proportion < 1.0
        else lower_boundary + ((1 - lower_boundary) / 2)
    )
    step_down_alternative = f"or to {recommendation_to_decrease:.3f}"
    assert expected >= lower_boundary, f"""
        Broken Record: Adjust the expected success rate to at least {lower_boundary} {step_down_alternative}
        New Success rate {success_analysis.proportion:.3f} with 90% confidence exceeds expected: {expected}
        Expecting: {lower_boundary:.3f} <= {expected:.3f} <= {higher_boundary:.3f}
        Got: expected={expected} <= analysis.lower_interval={lower_boundary}
        """
    recommendation_to_increase = (
        success_analysis.proportion
        if success_analysis.proportion < 1.0
        else higher_boundary - ((1 - higher_boundary) / 2)
    )
    step_up_alternative = f"or to {recommendation_to_increase:.3f}"
    assert expected <= higher_boundary, f"""
        Broken Record: Adjust the expected success rate to at least {higher_boundary} {step_up_alternative}
        Failure rate {success_analysis.proportion:.3f} not within 90% confidence of expected {expected}
        New Success rate {success_analysis.proportion:.3f} with 90% confidence LOWER that expected: {expected}
        Expected value: {expected} is higher than higher_boundary: {higher_boundary:3f}
        Got: analysis.higher_boundary={higher_boundary:.3f} <= expected={expected}
        """


def failures_within_margin_of_error_from_expected(row: tuple[int, int, float]) -> str:
    return f"{row[0]} failures out of {row[1]} is within {row[2] * 100:.0f}% success rate"


def generate_examples(failure_count, total_test_runs) -> list[bool]:
    return failure_count * [False] + (total_test_runs - failure_count) * [True]


def process_row(row: tuple[int, int, float]) -> str:
    return f"{row[0]} failures out of {row[1]} is within {row[2] * 100:.0f}% success rate"


def is_statistically_significant(success_rate: float, failure_count: int, sample_size: int) -> bool:
    return not is_within_expected(success_rate, failure_count, sample_size)


logger = logging.getLogger(__name__)


def is_within_expected(success_rate: float, failure_count: int, sample_size: int) -> bool:
    logger.info(f"is_within_expected({success_rate}, {failure_count}, {sample_size})")
    if sample_size <= 1:
        return True

    expected_success_count = int(success_rate * sample_size)
    success_analysis = analyse_measure_from_test_sample(expected_success_count, sample_size)
    measured_success_count = sample_size - failure_count
    measured_success_rate = measured_success_count / sample_size

    interval_min, interval_max = success_analysis.confidence_interval_count
    logger.info(
        f"Expecting {measured_success_count} to be between {interval_min} and {interval_max}"
    )
    if measured_success_count < interval_min:
        logger.info(
            f"Failure count {failure_count} is below the minimum of {interval_min},"
            + f" current success rate {measured_success_rate} < "
            + f"lower limit:{success_analysis.confidence_interval_prop[0]:.3f}"
        )
    if measured_success_count > interval_max:
        logger.info(
            f"Failure count {failure_count} is above the maximum of {interval_max},"
            + f" current success rate {measured_success_rate} > "
            + f"higher limit:{success_analysis.confidence_interval_prop[1]:.3f}"
        )
    return is_within_a_range(
        measured_success_count,
        interval_min,
        interval_max,
    )


def is_within_a_range(value: float, left: float, right: float) -> bool:
    return left <= value <= right
