import os
from typing import Callable, List, Optional

from .reporter import Reporter


class Runner:
    """Executes test functions and collects results using a reporter."""

    def __init__(self, test_function: Callable[..., bool], reporter: Reporter) -> None:
        """
        Initialize the Runner with a test function and reporter.

        Args:
            test_function: Function to execute during test runs
            reporter: Reporter instance to track and report test results
        """
        self.reporter = reporter
        self.test_function = test_function

    @staticmethod
    def get_sample_size(default_size: int = 1) -> int:
        """
        Get sample size from environment variable or use default.

        Args:
            default_size: Default sample size if not specified in environment

        Returns:
            Number of test runs to perform
        """
        return int(os.getenv("CAT_AI_SAMPLE_SIZE", str(default_size)))

    def run_once(self, run_number: int = 0) -> bool:
        """
        Execute the test function once.

        Args:
            run_number: Current run index for reporting

        Returns:
            Result from the test function
        """
        self.reporter.run_number = run_number
        return self.test_function(reporter=self.reporter)

    def run(self, sample_size: Optional[int] = None) -> List[bool]:
        """
        Execute the test function multiple times based on sample size.

        Args:
            sample_size: Number of times to run the test, defaults to
                         value from get_sample_size() if None

        Returns:
            List of results from all test runs
        """
        runs = sample_size or self.get_sample_size()
        return [self.run_once(i) for i in range(runs)]
