from pathlib import Path


def root_path() -> Path:
    """Returns the absolute path to the root of the project."""
    return Path(__file__).parent.parent.resolve()


def root_dir() -> str:
    """Returns the absolute path to the root directory of the project."""
    return str(root_path())


ROOT_DIR = root_dir()
