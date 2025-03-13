import logging
import time
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Type, TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    logger_name: Optional[str] = None,
) -> Callable:
    """
    Retry decorator with exponential backoff for handling transient errors.

    Args:
        max_attempts: Maximum number of attempts (including first try)
        exceptions: Tuple of exception types to catch and retry
        initial_delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
        logger_name: Optional logger name for custom logging

    Returns:
        Decorated function with retry logic
    """
    local_logger = logger
    if logger_name:
        local_logger = logging.getLogger(logger_name)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            attempt = 1
            current_delay = initial_delay

            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        local_logger.error(
                            f"Failed after {max_attempts} attempts: {e.__class__.__name__}: {str(e)}"
                        )
                        raise

                    local_logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed with {e.__class__.__name__}: {str(e)}. "
                        f"Retrying in {current_delay:.2f}s..."
                    )

                    time.sleep(current_delay)
                    current_delay *= backoff_factor
                    attempt += 1

        return wrapper

    return decorator
