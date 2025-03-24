import pytest
from statsmodels.stats.proportion import proportions_ztest


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
        "statistically proportion is larger then expected value"
    )
    assert proportions_ztest(9, 10, 0.7, alternative="two-sided")[1] < 0.05, (
        "statistically proportion is larger or smaller then expected value"
    )


def test_proportions_ztest_not_statistically_significantly():
    for count in range(4, 8):
        stat, p_value = proportions_ztest(count, 10, 0.7)
        assert p_value > 0.05, "NOT statistically significant improvement"


def test_proportions_ztest_significantly_worse():
    stat, p_value = proportions_ztest(3, 10, 0.7)
    assert p_value < 0.05, "statistically significant result"
    assert proportions_ztest(3, 10, 0.7, alternative="smaller")[1] < 0.05, (
        "statistically proportion is smaller then expected value"
    )
    assert proportions_ztest(3, 10, 0.7, alternative="two-sided")[1] < 0.05, (
        "statistically proportion is smaller then expected value"
    )


def test_proportions_ztest_no_change_is_not_significant():
    successes = [70, 70]
    n_observations = [100, 100]

    stat, p_value = proportions_ztest(successes, n_observations)
    assert p_value == 1
    assert p_value > 0.05, "statistically insignificant result"
    assert stat == 0


def calculate_p_value(success, failure, sample_size):
    return calculate_ztest(success, failure, sample_size)[1]


def calculate_ztest(success, failure, sample_size):
    measurements = [int(success * sample_size), failure]
    samples = [sample_size, sample_size]
    return proportions_ztest(measurements, samples)


def is_statistically_expected(success, failure, sample_size):
    return calculate_p_value(success, failure, sample_size) < 0.05


def test_is_statistically_significant():
    assert not is_statistically_expected(0.7, 3, 10)
    assert not is_statistically_expected(0.7, 70, 100)
    assert is_statistically_expected(0.9, 10, 100)
    assert is_statistically_expected(0.7, 30, 100)

    assert not is_statistically_expected(0.7, int(40 * 0.7), 40)
    print("finding")
    for i in range(40, 80):
        if is_statistically_expected(0.7, int(i * 0.7), i):
            print(i)
            break
    assert not is_statistically_expected(0.7, 31, 45)

    assert not is_statistically_expected(0.7, 3, 10)
    assert is_statistically_expected(0.7, 2, 10)
    assert is_statistically_expected(0.9, 1, 10)
    assert is_statistically_expected(0.9, 10, 100)
