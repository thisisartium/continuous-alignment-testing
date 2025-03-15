import json
import re
from pathlib import Path

from settings import root_path


def load_json_fixture(file_name: str) -> dict:
    """
    Utility function to load a JSON fixture file.

    :param file_name: Name of the JSON file to load.
    :return: Parsed JSON data as a dictionary.
    """
    json_path = root_path() / "tests" / "fixtures" / file_name
    with open(json_path, "r") as file:
        return json.load(file)


def natural_sort_key(s: Path):
    """Sort strings with embedded numbers in natural order."""
    return [
        int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", str(s.name))
    ]
