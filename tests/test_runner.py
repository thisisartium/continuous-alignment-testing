from src.cat_ai.reporter import Reporter
from src.cat_ai.runner import Runner


# Dummy test function that will be passed to Runner
def dummy_test_function(reporter: Reporter) -> bool:
    # Imagine that this function does something meaningful
    # Simply returning True instead of trying to log
    return True


def test_runner_sample_size(monkeypatch):
    # Set an environment variable to test
    monkeypatch.setenv("CAT_AI_SAMPLE_SIZE", "5")
    assert Runner.get_sample_size() == 5

    # Test default size
    monkeypatch.delenv("CAT_AI_SAMPLE_SIZE", raising=False)
    assert Runner.get_sample_size(default_size=3) == 3


def test_run_once():
    # Create a Reporter with necessary arguments
    reporter = Reporter(test_name="test_run_once", output_dir="/tmp")

    # Initialize Runner with dummy test function and Reporter
    runner = Runner(test_function=dummy_test_function, reporter=reporter)

    # Test run_once
    result = runner.run_once()
    assert result is True
    assert reporter.run_number == 0


def test_run_multiple():
    # Create a Reporter with necessary arguments
    reporter = Reporter(test_name="test_run", output_dir="/tmp")

    # Initialize Runner with dummy test function and Reporter
    runner = Runner(test_function=dummy_test_function, reporter=reporter)

    # Test with explicit sample size parameter
    results = runner.run_multiple(sample_size=2)
    assert len(results) == 2
    assert all(results)
    expected_results = [True, True]
    assert results == expected_results


def test_run_with_env_variable(monkeypatch):
    # Set the environment variable for a controlled test
    monkeypatch.setenv("CAT_AI_SAMPLE_SIZE", "3")

    # Create a Reporter with necessary arguments
    reporter = Reporter(test_name="test_run_with_env", output_dir="/tmp")

    # Initialize Runner with dummy test function and Reporter
    runner = Runner(test_function=dummy_test_function, reporter=reporter)

    # Test without explicit sample size (should use environment variable)
    results = runner.run_multiple()
    assert len(results) == 3
    expected_results = [True, True, True]
    assert results == expected_results
