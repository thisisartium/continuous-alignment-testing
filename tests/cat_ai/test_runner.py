import pytest
from src.cat_ai.runner import Runner
from src.cat_ai.reporter import Reporter

# Dummy test function that will be passed to Runner
def dummy_test_function(reporter: Reporter):
    # Imagine that this function does something meaningful
    return f"Running test with run number {reporter.run_number}"


def test_runner_sample_size(monkeypatch):
    # Set an environment variable to test
    monkeypatch.setenv("CAT_AI_SAMPLE_SIZE", "5")
    assert Runner.sample_size() == 5

    # Test default size
    monkeypatch.delenv("CAT_AI_SAMPLE_SIZE", raising=False)
    assert Runner.sample_size(default_size=3) == 3


def test_run_once():
    # Create a Reporter with necessary arguments
    reporter = Reporter(test_name="test_run_once", output_dir="/tmp")

    # Initialize Runner with dummy test function and Reporter
    runner = Runner(test_function=dummy_test_function, reporter=reporter)

    # Test run_once
    result = runner.run_once(run_number=1)
    assert result == "Running test with run number 1"
    assert reporter.run_number == 1


def test_run_loop(monkeypatch):
    # Set the environment variable for a controlled loop
    monkeypatch.setenv("CAT_AI_SAMPLE_SIZE", "3")

    # Create a Reporter with necessary arguments
    reporter = Reporter(test_name="test_run_loop", output_dir="/tmp")
    
    # Initialize Runner with dummy test function and Reporter
    runner = Runner(test_function=dummy_test_function, reporter=reporter)

    # Test run_loop
    tries = Runner.sample_size()

    results = runner.run_loop(tries=tries)
    assert len(results) == 3
    assert all(res.startswith("Running test with run number ") for res in results)
    expected_results = [
        "Running test with run number 0",
        "Running test with run number 1",
        "Running test with run number 2"
    ]
    assert results == expected_results
