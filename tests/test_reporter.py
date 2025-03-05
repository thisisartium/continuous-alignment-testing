import json
import time
from unittest.mock import mock_open, patch, MagicMock
from src.cat_ai.reporter import Reporter
from src.cat_ai.helpers.helpers import root_dir


def test_reporter_creates_a_unique_folder_path() -> None:
    test_name = "unique_folder_path"
    reporter1 = Reporter(test_name=test_name, output_dir=root_dir())
    expected_dir_path = f"{root_dir()}/test_runs/{test_name}"
    assert expected_dir_path in reporter1.folder_path
    time.sleep(2)
    reporter2 = Reporter(test_name=test_name, output_dir=root_dir())
    assert str(reporter1.folder_path) != str(reporter2.folder_path)


def test_reporter_can_accept_unique_id_override() -> None:
    test_name = "id_override"
    unique_id = "some_string"
    reporter1 = Reporter(test_name=test_name, output_dir=root_dir(), unique_id=unique_id)
    expected_dir_path = f"{root_dir()}/test_runs/{test_name}-{unique_id}"
    assert str(expected_dir_path) == str(reporter1.folder_path)


@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
def test_report_creates_correct_json(mock_open: MagicMock, mock_makedirs: MagicMock) -> None:
    test_name = "report_creates_correct_json"
    unique_id = "20231001_120000"
    reporter = Reporter(test_name=test_name, output_dir=root_dir(), unique_id=unique_id)

    response = "Sample response"
    results = {"test1": True, "test2": False}

    final_result = reporter.report(response, results)

    assert final_result is False
    expected_metadata = {
        "test_name": test_name,
        "folder_path": f"{root_dir()}/test_runs/{test_name}-{unique_id}",
        "output_file": "0-False.json",
        "metadata_path": f"{root_dir()}/test_runs/{test_name}-{unique_id}/metadata.json",
        "validations": results,
        "response": response,
    }
    expected_json_string = json.dumps(expected_metadata, indent=4)

    mock_makedirs.assert_called_once_with(reporter.folder_path, exist_ok=True)

    mock_open().write.assert_called_with(expected_json_string)
