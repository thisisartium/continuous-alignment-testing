import json
import os
import time
from pathlib import Path
from typing import Callable

from cat_ai.helpers.helpers import root_dir
from cat_ai.reporter import Reporter


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


def test_report_creates_correct_json(test_name: str, snapshot) -> None:
    temp_dir = "/tmp"
    unique_id = "20231001_120000"
    reporter = Reporter(test_name=test_name, output_dir=temp_dir, unique_id=unique_id)
    reporter.metadata = {"ai-model": "champion-1"}

    # Generate test data
    response = "Alice is the oldest."
    results = {"can-talk": True, "can-think": False}

    # Call report method
    final_result = reporter.report(response, results)

    # Verify return value (should be False because not all results are True)
    assert final_result is False

    # Expected output paths
    expected_dir_path = Path(temp_dir) / "test_runs" / (test_name + "-" + unique_id)
    expected_metadata_path = expected_dir_path / "metadata.json"
    with open(expected_metadata_path, "r") as file:
        contents = json.load(file)
    assert contents == {}
    expected_output_path = expected_dir_path / "fail-0.json"
    assert os.path.isfile(expected_metadata_path)
    assert os.path.isfile(expected_output_path)

    with open(expected_output_path, "r") as file:
        content = json.load(file)
    snapshot.assert_match(json.dumps(content, indent=2), "expected_report.json")


def test_format_summary_with_failure_analysis(analyze_failure_rate):
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
