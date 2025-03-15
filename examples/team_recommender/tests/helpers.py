import json
import re
from pathlib import Path

from settings import root_path

from cat_ai import analyse_sample_from_test


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
    analysis = analyse_sample_from_test(number_of_successes, actual_count)
    # Handle case when a list of results is passed
    lower_boundary = analysis.confidence_interval_prop[0]
    higher_boundary = analysis.confidence_interval_prop[1]
    assert expected > lower_boundary, f"""
        Broken Record:  
        New Success rate {analysis.proportion:.3f} with 90% confidence exceeds expected: {expected}
        Expecting: {lower_boundary:.3f} <= {expected:.3f} <= {higher_boundary:.3f}
        Got: expected={expected} <= analysis.lower_interval={lower_boundary}
        """
    assert expected < higher_boundary, f"""
        Failure rate {analysis.proportion} not within 90% confidence of expected {expected}
        New Success rate {analysis.proportion} with 90% confidence lower that expected: {expected}
        Expecting: {lower_boundary} <= {expected} <= {higher_boundary}
        Got:  analysis.higher_boundary={higher_boundary} <= expected={expected}
        """
