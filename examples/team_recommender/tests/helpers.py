import json
import re
from pathlib import Path

import pytest
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
        Expected value: {expected} is less than higher_boundary: {higher_boundary:3f}
        Got: analysis.higher_boundary={higher_boundary:.3f} <= expected={expected}
        """


def failures_within_margin_of_error_from_expected(row: tuple[int, int, float]) -> str:
    return f"{row[0]} failures out of {row[1]} is within {row[2] * 100:.0f}% success rate"


def generate_examples(failure_count, total_test_runs) -> list[bool]:
    return failure_count * [False] + (total_test_runs - failure_count) * [True]


@pytest.mark.parametrize(
    "row",
    [
        (
            1,
            5,
            0.97,
        ),  # 1 failure out of 5 is 80% and still within 97% success rate on a such small sample
        (2, 5, 0.95),  # 2 failures out of 5 is 60% success and still within 95% success rate
        (6, 100, 0.97),  # 6 failures out of 100 is 94% success rate, and still within 97% expected
        (15, 100, 0.80),  # 15 failures out of 100 is within 80% success rate, 14 will not
        (27, 100, 0.80),  # 27 failures out of 100 is within 80% success rate, 28 will not
    ],
    ids=lambda row: failures_within_margin_of_error_from_expected(row),
)
def test_assert_success_rate(row):
    failure_count, sample_size, expected_success_rate = row
    table = generate_examples(failure_count, sample_size)
    _assert_success_rate(table, expected_success_rate)


def process_row(row: tuple[int, int, float]) -> str:
    return f"{row[0]} failures out of {row[1]} is within {row[2] * 100:.0f}% success rate"


@pytest.mark.parametrize(
    "row",
    [
        (1, 5, 0.97),  # 1 failure out of 5 is within 97% success rate
        (2, 5, 0.95),  # 2 failures out of 5 is within 95% success rate
        (6, 100, 0.97),  # 6 failures out of 100 is within 97% success rate
        (15, 100, 0.80),  # 15 failures out of 100 is within 80% success rate
        (27, 100, 0.80),  # 27 failures out of 100 is within 80% success rate
    ],
    ids=lambda row: process_row(row),
)
def test_success_rate_is_within_expected_error_margin_with_90_percent_confidence(
    assert_success_rate, row
):
    failure_count, total_test_runs, expected_rate = row
    results = generate_examples(failure_count, total_test_runs)
    assert_success_rate(results, expected_rate)


@pytest.mark.parametrize(
    "row",
    [
        (
            6,
            10,
            0.70,
            [
                "New Success rate 0.400 with 90% confidence LOWER that expected: 0.7",
                "Failure rate 0.400 not within 90% confidence of expected 0.7",
                "Expected value: 0.7 is less than higher_boundary: 0.654820",
                "Got: analysis.higher_boundary=0.655 <= expected=0.7",
            ],
        ),
        (
            1,
            10,
            0.70,
            [
                "New Success rate 0.900 with 90% confidence exceeds expected: 0.7",
                "Broken Record:",
                "Expecting: 0.744 <= 0.700 <= 1.056",
                "Got: expected=0.7 <= analysis.lower_interval=0.74",
            ],
        ),
        (
            1,
            1000,
            0.98,
            [
                "New Success rate 0.999 with 90% confidence exceeds expected: 0.98",
                "Broken Record:",
                "Expecting: 0.997 <= 0.980 <= 1.001",
                "Got: expected=0.98 <= analysis.lower_interval=0.997",
            ],
        ),
    ],
    ids=lambda row: row[-1][0],
)
def test_beyond_expected_success_rate(assert_success_rate, row):
    failure_count, total_test_runs, expected_rate, success_messages = row
    results = generate_examples(failure_count, total_test_runs)
    with pytest.raises(AssertionError) as excinfo:
        assert_success_rate(results, expected_rate)

    message = str(excinfo.value)
    for expected_message in success_messages:
        assert expected_message in message, (
            f"Expected message: {expected_message}\n not found in: {message}"
        )
    assert "Got: " in message
    assert " analysis." in message


def is_within_expected(success_rate: float, failure_count: int, sample_size: int) -> bool:
    print(f"is_within_expected({success_rate}, {failure_count}, {sample_size})")
    if sample_size <= 1:
        return True

    expected_success_count = int(success_rate * sample_size)
    success_analysis = analyse_measure_from_test_sample(expected_success_count, sample_size)
    measured_success_count = sample_size - failure_count
    measured_success_rate = measured_success_count / sample_size

    interval_min, interval_max = success_analysis.confidence_interval_count
    print(f"Expecting {measured_success_count} to be between {interval_min} and {interval_max}")
    if measured_success_count < interval_min:
        print(
            f"Failure count {failure_count} is below the minimum of {interval_min},"
            + f" current success rate {measured_success_rate} < "
            + f"lower limit:{success_analysis.confidence_interval_prop[0]:.3f}"
        )
    if measured_success_count > interval_max:
        print(
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


@pytest.mark.parametrize(
    "success_rate, failure_count, sample_size, message",
    [
        (0.8, 0, 5, None),
        (0.8, 2, 5, None),
        (0.8, 26, 100, None),
        (0.8, 14, 100, None),
        (0.97, 1, 8, None),
        (0.97, 0, 1, "after measuring 2x 100 runs and getting 3 failures"),
        (0.97, 1, 133, "At 133 we can say that with 90% confidence 1 failure is within 97% success rate"),
        (0.98, 0, 100, "97.5% success rate is within 100% success rate"),
        (0.97999999999999999, 0, 100, "97.37% success rate is within 100% success rate"),
        (0.5, 1, 2, None),
    ],
)
def test_is_within_expected(success_rate, failure_count, sample_size, message):
    if message:
        assert is_within_expected(success_rate, failure_count, sample_size), message
    else:
        assert is_within_expected(success_rate, failure_count, sample_size)


@pytest.mark.parametrize(
    "failure_count, sample_size, expected_rate, message",
    [
        (3, 5, 0.8, "40% success rate is below expected 80% success rate"),
        (1, 50000, 0.9997, "99.99% success rate is below expected 97% success rate"),
        (0, 100, 0.97, "100% success rate is not within 97% success rate"),
        (0, 100, 0.9736, "97.36% success rate is not within 100% success rate"),
        (1, 134, 0.97, "At 134 we can say that with 90% confidence 1 failure is within 97% success rate"),
    ],
)
def test_not_is_within_expected(failure_count, sample_size, expected_rate, message):
    assert not is_within_expected(expected_rate, failure_count, sample_size), message


def test_success_rate():
    tiny_set_analysis = analyse_measure_from_test_sample(1, 2)
    assert tiny_set_analysis.proportion == 0.5
    interval = tiny_set_analysis.confidence_interval_prop

    assert interval[0] <= 0 and interval[1] >= 1, (
        f"interval includes all possible values: {interval} does not contain [0, 1]"
    )


def test_confidence_interval():
    analysis = analyse_measure_from_test_sample(measure=97, sample_size=100)
    assert analysis.observation == 97
    assert analysis.sample_size == 100
    assert analysis.proportion == 0.97
    assert analysis.confidence_interval_count == (95, 99)
    interval_min, interval_max = analysis.confidence_interval_prop
    assert interval_min == pytest.approx(0.942, rel=0.001)
    assert interval_max == pytest.approx(0.998, rel=0.001)


def test_sort_names_with_numbers():
    unsorted = [
        "example_1_text_response",
        "example_10_threshold",
        "example_2_unit",
        "example_8_retry_network",
        "example_9_retry_with_open_telemetry",
    ]
    assert [
        "example_10_threshold",
        "example_1_text_response",
        "example_2_unit",
        "example_8_retry_network",
        "example_9_retry_with_open_telemetry",
    ] == sorted(unsorted), "The list should be sorted by the number in the name"

    correctly_sorted = [
        "example_1_text_response",
        "example_2_unit",
        "example_8_retry_network",
        "example_9_retry_with_open_telemetry",
        "example_10_threshold",
    ]
    assert sorted([Path(p) for p in unsorted], key=natural_sort_key) == [
        Path(p) for p in correctly_sorted
    ], "example_10_threshold should be last, while example_1_text_response should be first"
