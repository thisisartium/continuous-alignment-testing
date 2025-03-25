import pytest
from helpers import is_within_expected
from statsmodels.stats.proportion import proportions_ztest
from test_helpers import next_success_rate


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


def calculate_p_value(success, failure, sample_size) -> float:
    return calculate_ztest(success, failure, sample_size)[1]


def calculate_ztest(success, failure, sample_size) -> tuple[float, float]:
    measurements = [int(success * sample_size), sample_size - failure]
    samples = [sample_size, sample_size]
    zstat, p_value = proportions_ztest(measurements, samples)
    return zstat, p_value


def is_statistically_significant(success, failure, sample_size):
    return calculate_p_value(success, failure, sample_size) < 0.05


def test_not_is_statistically_significant():
    assert not is_statistically_significant(0.7, 3, 10), "same proportion"
    assert not is_statistically_significant(0.9, 10, 100), "same proportion"
    assert not is_statistically_significant(0.7, 30, 100), "same proportion"
    assert not is_statistically_significant(0.7, 0, 10), "covers 100% success rate"


def test_is_statistically_significant():
    assert is_statistically_significant(0.9, 0, 100), "0 out of 100 > 90% success rate"
    assert is_statistically_significant(0.7, 0, 11), "0 out of 11 > 70% success rate"
    assert is_statistically_significant(0.9, 0, 31), "0 out of 31 > 90% success rate"
    assert is_statistically_significant(0.909090, 0, 33), "0 out of 33 > 90.9% success rate"


def test_is_statistically_significant_with_next_success_rate():
    sample_size = 10
    assert not is_statistically_significant(next_success_rate(sample_size), 0, sample_size)
    assert is_statistically_significant(next_success_rate(sample_size), 0, 34)
    assert is_statistically_significant(next_success_rate(35), 0, 109)


def test_compare_is_within_expected_and_is_statistically_significant():
    assert is_within_expected(0.7, 3, 10), "not significant result for 3/10=70%"
    assert not is_statistically_significant(0.7, 3, 10), "not significant for 3/10=70%"

    assert is_within_expected(0.7, 0, 3), "not significant result for 0 out of 3"
    assert not is_statistically_significant(0.7, 0, 3), "not significant result for 0 out of 3"


def test_improvement_from_70_percent():
    assert is_within_expected(0.7, 0, 3), "no improvement detected at 3"
    assert not is_statistically_significant(0.7, 0, 10), "no improvement detected at 10"

    assert not is_within_expected(0.7, 0, 4), "improvement detected at 4"
    assert is_statistically_significant(0.7, 0, 11), "improvement detected at 11"


def test_improvement_from_97_percent():
    assert is_within_expected(0.97, 0, 66), "no improvement detected at 66"
    assert not is_statistically_significant(0.97, 0, 100), "no improvement detected at 100"

    assert not is_within_expected(0.97, 0, 67), "significantly better at 67"
    assert is_statistically_significant(0.97, 0, 101), "significantly better at 101"
