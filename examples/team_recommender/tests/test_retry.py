import logging

import pytest
from retry import retry


def test_retry_success():
    @retry()
    def always_success():
        return "success"

    assert always_success() == "success"


TINY_TEST_DELAY = 0.01
tiny = TINY_TEST_DELAY


def test_retry_ends_in_failure():
    with pytest.raises(ValueError, match="Always failing"):
        always_fail()


def test_retry_ends_in_success():
    attempt_counter = 0

    @retry(max_attempts=3, exceptions=(ValueError,), initial_delay=tiny)
    def succeeds_after_one_failure():
        nonlocal attempt_counter
        if attempt_counter == 0:
            attempt_counter += 1
            raise ValueError("Test error")
        return "success"

    assert succeeds_after_one_failure() == "success"
    assert attempt_counter == 1


example_logger_name = "logger_for_retry_tests"


@retry(exceptions=(ValueError,), logger_name=example_logger_name, initial_delay=tiny)
def always_fail():
    raise ValueError("Always failing")


def test_retry_logs_attempts_as_warnings(caplog):
    with caplog.at_level(logging.WARNING, logger=example_logger_name):
        with pytest.raises(ValueError, match="Always failing"):
            always_fail()

    log_messages = [record.message for record in caplog.records]
    assert log_messages == [
        "Attempt 1/3 failed with ValueError: Always failing. Retrying in 0.01s...",
        "Attempt 2/3 failed with ValueError: Always failing. Retrying in 0.02s...",
        "Failed after 3 attempts: ValueError: Always failing",
    ]
