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


def find_latest_example() -> str | None:
    """Find the latest example directory without relying on interactive commands"""
    # Avoid debugger evaluation of non-essential code branches
    try:
        tests_dir = root_path() / "tests"
        example_dirs = [d for d in tests_dir.glob("example_*") if d.is_dir()]
        example_dirs.sort()  # Natural sort to handle numerical directories correctly
        return str(example_dirs[-1]) if example_dirs else None
    except Exception:
        # Fail silently - better to run all tests than break the test runner
        return None


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--all"):
        latest_example = find_latest_example()
        if latest_example:
            mark_skip_all_except_matching_example(items, latest_example)


def mark_skip_all_except_matching_example(items, latest_example: str):
    skip_older = pytest.mark.skip(reason="Only running latest example (use --all to run all)")
    for item in items:
        if str(latest_example) not in str(item.fspath):
            item.add_marker(skip_older)
