from pathlib import Path

import pytest
from helpers import (
    _assert_success_rate,
    failures_within_margin_of_error_from_expected,
    generate_examples,
    is_within_expected,
    natural_sort_key,
)

from cat_ai.statistical_analysis import analyse_measure_from_test_sample


@pytest.mark.parametrize(
    "row",
    [
        (1, 5, 0.97),  # 1 failure out of 5 is 80% success and still within 97% success rate
        (2, 5, 0.95),  # 2 failures out of 5 is 60% success and still within 95% success rate
        (6, 100, 0.97),  # 6 failures out of 100 is 94% success rate, and still within 97% expected
        (15, 100, 0.80),  # 15 failures out of 100 is within 80% success rate, 14 will not
        (27, 100, 0.80),  # 27 failures out of 100 is within 80% success rate, 28 will not
    ],
    ids=lambda row: failures_within_margin_of_error_from_expected(row),
)
def test_assert_success_rate_pass(row):
    failure_count, sample_size, expected_success_rate = row
    table = generate_examples(failure_count, sample_size)
    _assert_success_rate(table, expected_success_rate)


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
                "Expecting: 0.744 <= 0.700 <= 1.000",
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
                "Expecting: 0.997 <= 0.980 <= 1.000",
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
        (
            0.97,
            1,
            133,
            "At 133 we can say that with 90% confidence 1 failure is within 97% success rate",
        ),
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
        (0, 100, 0.97, "100% success rate is not within 97% success rate"),
        (1, 50000, 0.9997, "99.99% success rate is below expected 97% success rate"),
        (0, 100, 0.9736, "97.36% success rate is not within 100% success rate"),
        (
            1,
            134,
            0.97,
            "At 134 we can say that with 90% confidence 1 failure is within 97% success rate",
        ),
    ],
)
def test_not_is_within_expected(failure_count, sample_size, expected_rate, message):
    assert not is_within_expected(expected_rate, failure_count, sample_size), message


def test_seventy_percent_confidence_ranges_from_fifty_to_ninety():
    starting_rate = 0.7
    sample_size = 10
    sample = analyse_measure_from_test_sample(sample_size * starting_rate, sample_size)
    assert sample.confidence_interval_count == (5, 9)
    assert sample.proportion == starting_rate
    assert sample.confidence_interval_prop == (
        pytest.approx(0.5, rel=0.1),
        pytest.approx(0.9, rel=0.1),
    )


def next_success_rate(sample_size) -> float:
    return 1 - 1 / (sample_size + 1)


def test_next_success_rate():
    assert next_success_rate(1) == 0.5
    assert next_success_rate(2) == 0.6666666666666667
    assert next_success_rate(3) == 0.75
    assert next_success_rate(4) == 0.8
    assert next_success_rate(10) == 0.9090909090909091
    assert next_success_rate(12) == 0.9230769230769231
    assert next_success_rate(55) == 0.9821428571428571
    assert next_success_rate(248) == 0.9959839357429718


@pytest.mark.parametrize(
    "success_rate, largest_sample_size",
    [
        (0.7, 10),
        (next_success_rate(10), 44),
        (next_success_rate(45), 184),
        (next_success_rate(185), 744),
        (next_success_rate(745), 2984),
    ],
)
def test_largest_sample_size_for_given_success_rate(success_rate, largest_sample_size):
    assert is_within_expected(success_rate, 1, largest_sample_size), "should be within expected"
    assert not is_within_expected(success_rate, 1, largest_sample_size + 1), (
        "next size should not be within expected"
    )


def test_next_sample_size():
    ## Next sample size should be larger than the current one by at least 4 times
    assert next_sample_size(10) == 45, (
        "passing 10 out of 10 should require 45 successful runs to be statistically significant"
    )
    assert next_sample_size(45) == 185, (
        "passing 45 out of 45 should require 185 successful runs to be statistically significant"
    )
    assert next_sample_size(185) == 745
    assert next_sample_size(745) == 2985
    assert next_sample_size(29) == 121
    assert next_sample_size(29) == next_sample_size_via_loop(29), "calculated via loop should match"

    assert 28 / 29 == pytest.approx(0.96, rel=0.01)
    before = analyse_measure_from_test_sample(28, 29)
    assert before.proportion == pytest.approx(0.96, rel=0.01)
    assert before.confidence_interval_prop == pytest.approx((0.91, 1.00), 0.01)

    analysis = analyse_measure_from_test_sample(120, 121)
    assert analysis.proportion == pytest.approx(0.99, rel=0.01)
    assert analysis.confidence_interval_prop == pytest.approx((0.98, 1.00), 0.01)


def next_sample_size(current):
    ## How many successful runs are needed to be statistically significant improvement
    # compared to the current sample size with 100% success rate at 90% confidence
    return 4 * current + 5


def next_sample_size_via_loop(sample_size: int) -> int:
    goal_success_rate = next_success_rate(sample_size)
    for i in range(sample_size, 5 * sample_size):
        if not is_within_expected(goal_success_rate, 1, i):
            return i
    return 0


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
