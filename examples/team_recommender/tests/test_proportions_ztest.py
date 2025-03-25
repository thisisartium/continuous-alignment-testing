from math import isnan

import pytest
from helpers import is_statistically_significant, is_within_expected
from statsmodels.stats.proportion import proportions_ztest
from test_helpers import (
    next_sample_size_no_failure,
    next_sample_size_via_loop_with_1_failure,
    next_sample_size_with_1_failure,
    next_success_rate,
)


def _calculate_p_value(success, failure, sample_size) -> float:
    return _calculate_ztest(success, failure, sample_size)[1]


def _calculate_ztest(success, failure, sample_size) -> tuple[float, float]:
    zstat, p_value = proportions_ztest(sample_size - failure, sample_size, value=success)
    return zstat, p_value


def _is_statistically_significant(success, failure, sample_size):
    zstat, p_value = _calculate_ztest(success, failure, sample_size)
    return p_value < 0.05


def test_proportions_ztest_improvement():
    successes = [70, 90]
    n_observations = [100, 100]

    stat, p_value = proportions_ztest(successes, n_observations)
    assert p_value == pytest.approx(0.00040695, rel=0.001)
    assert p_value < 0.05, "statistically significant result"
    assert stat == pytest.approx(-3.5355, rel=0.001)


def test_proportions_ztest_exact_match():
    stat, p_value = proportions_ztest(7, 10, 0.7)
    assert p_value == 1.0, "statistically insignificant result"
    assert stat == 0

    stat, p_value = proportions_ztest(7, 10, 0.7, prop_var=1)
    assert isnan(p_value)
    assert isnan(stat)

    stat, p_value = proportions_ztest(1, 10, 0.7, prop_var=0.5)
    assert p_value == pytest.approx(0.00014, rel=0.1)
    assert stat == pytest.approx(-3.79, rel=0.01)


def test_proportions_ztest_significantly_better():
    stat, p_value = proportions_ztest(9, 10, 0.7)
    assert p_value < 0.05, "statistically significant improvement"
    assert proportions_ztest(9, 10, 0.7, alternative="larger")[1] < 0.05, (
        "statistically proportion is larger than expected value"
    )
    assert proportions_ztest(9, 10, 0.7, alternative="two-sided")[1] < 0.05, (
        "statistically proportion is larger or smaller than expected value"
    )


def test_proportions_ztest_not_statistically_significantly():
    for count in range(4, 8):
        stat, p_value = proportions_ztest(count, 10, 0.7)
        assert p_value > 0.05, "NO statistically significant deviation"


def test_proportions_ztest_significantly_worse():
    stat, p_value = proportions_ztest(3, 10, 0.7)
    assert p_value < 0.05, "statistically significant result"
    assert proportions_ztest(3, 10, 0.7, alternative="smaller")[1] < 0.05, (
        "statistically proportion is smaller than expected value"
    )
    assert proportions_ztest(3, 10, 0.7, alternative="two-sided")[1] < 0.05, (
        "statistically proportion is smaller than expected value"
    )


def test_not__is_statistically_significant():
    assert not _is_statistically_significant(0.7, 3, 10), "same proportion"
    assert not _is_statistically_significant(0.9, 10, 100), "same proportion"
    assert not _is_statistically_significant(0.7, 30, 100), "same proportion"


def test__is_statistically_significant():
    assert _is_statistically_significant(0.7, 0, 10), "70% does not covers 100% success rate"
    assert _is_statistically_significant(0.9, 0, 100), "0 out of 100 > 90% success rate"
    assert _is_statistically_significant(0.7, 0, 11), "0 out of 11 > 70% success rate"
    assert _is_statistically_significant(0.9, 0, 31), "0 out of 31 > 90% success rate"
    assert _is_statistically_significant(0.909090, 0, 33), "0 out of 33 > 90.9% success rate"


def test__is_statistically_significant_with_next_success_rate():
    sample_size = 10
    assert _is_statistically_significant(next_success_rate(sample_size), 0, sample_size)
    assert _is_statistically_significant(
        next_success_rate(sample_size), 0, next_sample_size_with_1_failure(sample_size)
    )
    assert _is_statistically_significant(next_success_rate(35), 0, 109)


def test_example_on_wiki():
    sample_size = 47
    success_rate = 0.950
    assert not is_statistically_significant(success_rate, 1, sample_size)
    next_rate = next_success_rate(sample_size)
    next_size = next_sample_size_no_failure(sample_size)
    assert next_sample_size_via_loop_with_1_failure(sample_size) == 193
    assert next_size == 97
    assert next_rate == pytest.approx(0.98, rel=0.01)

    assert not is_within_expected(0.95, 1, next_size)
    assert not is_within_expected(next_rate, 0, next_size)
    assert is_within_expected(next_rate, 1, next_size)

    assert _is_statistically_significant(next_rate, 0, next_size)
    assert not _is_statistically_significant(next_rate, 1, next_size)


def test_compare_is_within_expected_and_is_statistically_significant():
    assert is_within_expected(0.7, 3, 10), "not significant result for 3/10=70%"
    assert not _is_statistically_significant(0.7, 3, 10), "not significant for 3/10=70%"

    assert is_within_expected(0.7, 0, 3), "not significant result for 0 out of 3"
    assert _is_statistically_significant(0.7, 0, 1000), "not significant result for 0 out of 3"


def test_improvement_from_70_percent():
    assert not is_statistically_significant(0.7, 0, 3), "no improvement detected at 3"
    assert _is_statistically_significant(0.7, 0, 10), "no improvement detected at 10"

    assert is_statistically_significant(0.7, 0, 4), "improvement detected at 4"
    assert _is_statistically_significant(0.7, 0, 11), "improvement detected at 11"


def test_improvement_from_97_percent_using_is_within_expected():
    assert not is_statistically_significant(0.97, 0, 66), "no improvement detected at 66"
    assert is_statistically_significant(0.97, 0, 67), "significantly better at 67"


def test_improvement_from_97_percent_using_statistically_significant():
    assert not _is_statistically_significant(0.97, 1, 67), (
        "no improvement detected with 1 failure at 67"
    )
    assert _is_statistically_significant(0.97, 1, 99), "significantly better at 99"


def test_no_failures_always_cause_insignificance():
    print(_calculate_ztest(0.97, 0, 10))
    assert _is_statistically_significant(0.97, 0, 10), (
        "BUG: improvement is always detected with 0 failure"
    )
    assert _is_statistically_significant(0.97, 0, 10_000), (
        "BUG: improvement is always detected with 0 failure"
    )
