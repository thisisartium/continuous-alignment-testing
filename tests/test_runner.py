import pytest

from cat_ai.runner import Runner


def test_runner_sample_size(monkeypatch):
    # Set an environment variable to test
    monkeypatch.setenv("CAT_AI_SAMPLE_SIZE", "5")
    assert Runner.get_sample_size() == 5

    # Test default size
    monkeypatch.delenv("CAT_AI_SAMPLE_SIZE", raising=False)
    assert Runner.get_sample_size(default_size=3) == 3


@pytest.mark.parametrize("return_value", [True, False])
def test_run_once(tmp_reporter, return_value):
    # Initialize Runner with dummy test function and Reporter
    runner = Runner(test_function=lambda x: return_value, reporter=tmp_reporter)

    # Test run_once
    result = runner.run_once()
    assert result is return_value
    assert tmp_reporter.run_number == 0


@pytest.mark.parametrize("return_value", [True, False])
def test_run_multiple(tmp_reporter, return_value):
    # Initialize Runner with dummy test function and Reporter
    runner = Runner(test_function=lambda _: return_value, reporter=tmp_reporter)

    # Test with explicit sample size parameter
    results = runner.run_multiple(sample_size=2)
    assert len(results) == 2
    expected_results = [return_value, return_value]
    assert results == expected_results


@pytest.mark.parametrize("sample_size", [3, 5])
def test_run_with_env_variable(monkeypatch, tmp_reporter, sample_size):
    # Set the environment variable for a controlled test
    monkeypatch.setenv("CAT_AI_SAMPLE_SIZE", str(sample_size))

    # Initialize Runner with dummy test function and Reporter
    runner = Runner(test_function=lambda x: True, reporter=tmp_reporter)

    # Test without explicit sample size (should use environment variable)
    results = runner.run_multiple()
    assert len(results) == sample_size
    expected_results = [True] * sample_size
    assert results == expected_results
