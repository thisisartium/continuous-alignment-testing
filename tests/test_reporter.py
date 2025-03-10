import json
import time
from unittest.mock import mock_open, patch, MagicMock

from cat_ai import StatisticalAnalysis, analyse_sample_from_test
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
    test_name = "example_test"
    unique_id = "timestamp_or_any_unique_id"
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
        "output_file": "fail-0.json",
        "metadata_path": f"{root_dir()}/test_runs/{test_name}-{unique_id}/metadata.json",
        "validations": results,
        "response": response,
    }
    expected_json_string = json.dumps(expected_metadata, indent=4)

    mock_makedirs.assert_called_once_with(reporter.folder_path, exist_ok=True)

    mock_open().write.assert_called_with(expected_json_string)


def test_format_summary():
    analysis = analyse_sample_from_test(6, 100)
    assert analysis == StatisticalAnalysis(
        failure_count=6,
        sample_size=100,
        proportion=0.06,
        standard_error=0.023748684174075833,
        margin_of_error=0.039063109299053655,
        confidence_interval_prop=(
            0.020936890700946342,
            0.09906310929905365
        ),
        confidence_interval_count=(3, 9)
    )
    assert Reporter.format_summary(analysis) == (
        '> [!NOTE]\n'
        '> ### There are 6 failures out of 100 generations.\n'
        '> Sample Proportion (p̂): 0.0600\n'
        '> Standard Error (SE): 0.023749\n'
        '> Margin of Error (ME): 0.039063\n'
        '> 90% Confidence Interval: [0.020937, 0.099063]\n'
        '> 90% Confidence Interval (Count): [3, 9]'
    )
