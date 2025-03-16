import logging
from pathlib import Path

import pytest
from helpers import _assert_success_rate, natural_sort_key
from settings import root_path


@pytest.fixture(autouse=True)
def setup_openai_logger() -> logging.Logger:
    # Configure the logger you mentioned in your retry decorator
    logger = logging.getLogger("openai.api")
    logger.setLevel(logging.DEBUG)

    # Create a console handler if you want it separate from pytest's logging
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


@pytest.fixture
def assert_success_rate():
    return _assert_success_rate


def pytest_addoption(parser):
    parser.addoption(
        "--all",
        action="store_true",
        default=False,
        help="Run all examples instead of just the latest",
    )


def pytest_configure(config):
    # Register a marker for example tests
    config.addinivalue_line("markers", "example: mark test as belonging to an example")


# Completely avoid any debugger-dependent hooks
# pytest_collect_file can trigger PyCharm's debugger in unpredictable ways


def example_dirs() -> set[Path]:
    tests_dir = root_path() / "tests"
    matching_examples = tests_dir.glob("example_*")
    return {d for d in matching_examples if d.is_dir()}


def find_latest_example() -> str | None:
    """Find the latest example directory without relying on interactive commands"""
    # Avoid debugger evaluation of non-essential code branches
    # noinspection PyBroadException
    try:
        examples = list(example_dirs())
        examples.sort(
            key=natural_sort_key
        )  # Natural sort to handle numerical directories correctly
        return str(examples[-1]) if examples else None
    except Exception:
        # Fail silently - better to run all tests than break the test runner
        return None


def number_of_unique_examples(items):
    examples = {
        parent_name
        for item in items
        if (parent_name := Path(item.fspath).parent.name).startswith("example_")
    }
    return len(examples)


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--all"):
        examples = number_of_unique_examples(items)

        if examples != len(example_dirs()):
            return

        latest_example = find_latest_example()
        print("latest_example", latest_example)
        if latest_example:
            mark_skip_all_except_matching_example(items, latest_example)


def mark_skip_all_except_matching_example(items, latest_example: str):
    skip_older = pytest.mark.skip(reason="Only running latest example (use --all to run all)")
    for item in items:
        if str(latest_example) not in str(item.fspath):
            item.add_marker(skip_older)
