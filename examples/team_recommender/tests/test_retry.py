import logging

import pytest
from retry import retry

TINY_TEST_DELAY = 0.01
tiny = TINY_TEST_DELAY


def test_retry_success():
    assert always_success() == "success"


def test_retry_ends_in_failure():
    with pytest.raises(ValueError, match="Always failing"):
        always_fail()


def test_retry_ends_in_success(caplog):
    global retry_attempt_counter
    retry_attempt_counter = 0
    with caplog.at_level(logging.WARNING, logger=example_logger_name):
        assert succeeds_after_one_failure() == "succeeded_eventually"
    assert retry_attempt_counter == 1
    log_messages = [record.message for record in caplog.records]
    assert log_messages == [
        "Attempt 1/3 failed with TestError: Intermittent failure. Retrying in 0.01s..."
    ]


def test_retry_logs_attempts_as_warnings(caplog):
    with caplog.at_level(logging.WARNING, logger=example_logger_name):
        with pytest.raises(TestError, match="Always failing"):
            always_fail()

    log_messages = [record.message for record in caplog.records]
    assert log_messages == [
        "Attempt 1/3 failed with TestError: Always failing. Retrying in 0.01s...",
        "Attempt 2/3 failed with TestError: Always failing. Retrying in 0.02s...",
        "Failed after 3 attempts: TestError: Always failing",
    ]


longest_delay_to_wait_for_retry = 100_000_000
should_never_be_retrying = longest_delay_to_wait_for_retry


@retry(initial_delay=should_never_be_retrying)
def always_success():
    return "success"


global retry_attempt_counter

example_logger_name = "logger_for_retry_tests"


class TestError(RuntimeError):
    pass


@retry(exceptions=(TestError,), initial_delay=tiny, logger_name=example_logger_name)
def succeeds_after_one_failure():
    global retry_attempt_counter
    if retry_attempt_counter == 0:
        retry_attempt_counter += 1
        raise TestError("Intermittent failure")
    return "succeeded_eventually"


@retry(exceptions=(TestError,), logger_name=example_logger_name, initial_delay=tiny)
def always_fail():
    raise TestError("Always failing")
