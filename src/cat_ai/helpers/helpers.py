from pathlib import Path


def find_root_dir(start_path: Path) -> Path:
    """Recursively searches for the project root directory."""
    # Check if the current directory contains a specific file or directory that indicates the root
    if (start_path / "setup.py").exists() or (start_path / "pyproject.toml").exists():
        return start_path
    # If not, move up one directory and check again
    parent_path = start_path.parent
    if parent_path == start_path:  # If we've reached the root of the filesystem
        raise FileNotFoundError("Project root not found.")
    return find_root_dir(parent_path)


def root_path() -> Path:
    """Returns the absolute path to the root of the project."""
    return find_root_dir(Path(__file__).resolve())


def root_dir() -> str:
    """Returns the absolute path to the root directory of the project."""
    return str(root_path())
