from pathlib import Path

import pytest
from helpers import (
    _assert_success_rate,
    failures_within_margin_of_error_from_expected,
    generate_examples,
    is_within_expected,
    natural_sort_key,
    process_row,
)

from cat_ai.statistical_analysis import analyse_measure_from_test_sample


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
                "Failure rate 0.400 not within 90% confidence of expected 0.7",
                "New Success rate 0.400 with 90% confidence LOWER that expected: 0.7",
                "Expected value: 0.7 is higher than higher_boundary: 0.654820",
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


@pytest.mark.parametrize(
    "success_rate, failure_count, sample_size, message",
    [
        (0.8, 0, 5, None),
        (0.8, 2, 5, None),
        (0.8, 26, 100, None),
        (0.8, 14, 100, None),
        (0.97, 1, 8, None),
        (0.97, 0, 1, "after measuring 2x 100 runs and getting 3 failures"),
        (0.975, 0, 100, "97.5% success rate is within 100% success rate"),
        (0.9737, 0, 100, "97.37% success rate is within 100% success rate"),
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
        (1, 2, 0.97, "50% success rate is below expected 97% success rate"),
        (0, 100, 0.97, "100% success rate is not within 97% success rate"),
        (0, 100, 0.9736, "97.36% success rate is not within 100% success rate"),
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
