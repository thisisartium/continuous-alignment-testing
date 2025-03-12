import logging

import pytest
from retry import retry


def test_retry_success():
    @retry()
    def always_success():
        return "success"

    assert always_success() == "success"


def test_retry_failure():
    @retry(max_attempts=3, exceptions=(ValueError,))
    def always_fail():
        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        always_fail()


def test_retry_eventual_success():
    attempt_counter = 0

    @retry(max_attempts=3, exceptions=(ValueError,))
    def succeeds_after_one_failure():
        nonlocal attempt_counter
        if attempt_counter == 0:
            attempt_counter += 1
            raise ValueError("Test error")
        return "success"

    assert succeeds_after_one_failure() == "success"


def test_retry_with_custom_logger(caplog):
    logger_name = "custom_logger"

    @retry(max_attempts=3, exceptions=(ValueError,), logger_name=logger_name)
    def always_fail():
        raise ValueError("Test error")

    with caplog.at_level(logging.WARNING, logger=logger_name):
        with pytest.raises(ValueError, match="Test error"):
            always_fail()

    log_messages = [record.message for record in caplog.records]
    assert any("Attempt 1/3 failed with ValueError: Test error" in msg for msg in log_messages)
    assert any("Retrying in 1.00s..." in msg for msg in log_messages)
