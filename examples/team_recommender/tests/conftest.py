from pathlib import Path

import pytest
from settings import root_path


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
    return set([d for d in tests_dir.glob("example_*") if d.is_dir()])


def natural_sort_key(s):
    """Sort strings with embedded numbers in natural order."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", s)]


def find_latest_example() -> str | None:
    """Find the latest example directory without relying on interactive commands"""
    # Avoid debugger evaluation of non-essential code branches
    try:
        examples = list(example_dirs())
        examples.sort(
            key=natural_sort_key
        )  # Natural sort to handle numerical directories correctly
        return str(examples[-1]) if examples else None
    except Exception:
        # Fail silently - better to run all tests than break the test runner
        return None


def number_of_examples(items):
    examples = {
        Path(item.fspath).parent.name
        for item in items
        if Path(item.fspath).parent.name.startswith("example_")
    }
    return len(examples)


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--all"):
        examples = number_of_examples(items)

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
