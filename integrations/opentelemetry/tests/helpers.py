import json
from pathlib import Path


def root_path() -> Path:
    """Returns the absolute path to the root of the project."""
    return Path(__file__).parent.parent.resolve()


def load_json_fixture(file_name: str) -> dict:
    """
    Utility function to load a JSON fixture file.

    :param file_name: Name of the JSON file to load.
    :return: Parsed JSON data as a dictionary.
    """
    json_path = root_path() / "tests" / "fixtures" / file_name
    with open(json_path, "r") as file:
        return json.load(file)
