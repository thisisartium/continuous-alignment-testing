import json
import time
from typing import Callable
from unittest.mock import MagicMock, mock_open, patch

from cat_ai.helpers.helpers import root_dir


def test_reporter_creates_a_unique_folder_path(reporter_factory: Callable) -> None:
    reporter1 = reporter_factory()
    expected_dir_path = f"{root_dir()}/test_runs/test_reporter_creates_a_unique_folder_path"
    assert expected_dir_path in reporter1.folder_path

    time.sleep(2)
    reporter2 = reporter_factory()
    assert str(reporter1.folder_path) != str(reporter2.folder_path)


def test_reporter_can_accept_unique_id_override(reporter_factory: Callable) -> None:
    unique_id = "timestamp_or_any_unique_id"
    reporter = reporter_factory(unique_id=unique_id)

    expected_dir_path = (
        f"{root_dir()}/test_runs/test_reporter_can_accept_unique_id_override-{unique_id}"
    )
    assert str(expected_dir_path) == str(reporter.folder_path)


@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
def test_report_creates_correct_json(
    mock_open: MagicMock, mock_makedirs: MagicMock, reporter_factory: Callable
) -> None:
    test_name = "test_report_creates_correct_json"
    unique_id = "20231001_120000"
    reporter = reporter_factory(unique_id=unique_id)

    response = "Sample response"
    results = {"test1": True, "test2": False}

    final_result = reporter.report(response, results)

    assert final_result is False
    expected_metadata = {
        "test_name": test_name,
        "folder_path": f"{root_dir()}/test_runs/{test_name}-{unique_id}",
        "output_file": "fail-0.json",
        "metadata_path": f"{root_dir()}/test_runs/{test_name}-{unique_id}/metadata.json",
        "validations": results,
        "response": response,
    }
    expected_json_string = json.dumps(expected_metadata, indent=4)

    mock_makedirs.assert_called_once_with(reporter.folder_path, exist_ok=True)
    mock_open().write.assert_called_with(expected_json_string)


def test_format_summary_with_failure_analysis(analyze_failure_rate):
    from cat_ai.reporter import Reporter

    failure_analysis = analyze_failure_rate(6, 100)
    assert Reporter.format_summary(failure_analysis) == (
        "> [!NOTE]\n"
        "> ## 6 ± 3 failures detected (100 samples)\n"
        "> \n"
        "> **90% Confidence Range:** 3-9 failures\n"
        "> \n"
        "> **Details:**\n"
        "> - Proportion: 0.0600 [0.0209, 0.0991]\n"
        "> - Standard Error: 0.0237\n"
        "> - Margin of Error: 0.0391\n"
    )
