import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from .statistical_analysis import StatisticalAnalysis, analyse_sample_from_test


class Reporter:
    run_number: int = 0
    test_name: str
    folder_path: str

    @staticmethod
    def _create_unique_id_from_time() -> str:
        return datetime.now().strftime("%m%d-%H_%M_%S")

    def __init__(
        self,
        test_name: str,
        output_dir: str,
        unique_id: str | None = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.test_name = test_name
        self.metadata = metadata or {}

        if not unique_id:
            unique_id = self._create_unique_id_from_time()

        unique_dir_name = f"{test_name}-{unique_id}"
        self.folder_path = os.path.join(output_dir, "test_runs", unique_dir_name)
        os.makedirs(self.folder_path, exist_ok=True)

    def report(self, response: str, results: Dict[str, bool]) -> bool:
        metadata_path = os.path.join(self.folder_path, "metadata.json")
        if not os.path.exists(metadata_path):
            with open(metadata_path, "w") as file:
                file.write(json.dumps(self.metadata, indent=4))

        final_result = all(results.values())
        file_name = f"{'pass' if final_result else 'fail'}-{self.run_number}.json"
        output_path = os.path.join(self.folder_path, file_name)

        run_report = {
            "test_name": self.test_name,
            "folder_path": self.folder_path,
            "output_file": file_name,
            "metadata_path": metadata_path,
            "validations": results,
            "response": response,
        }

        json_object = json.dumps(run_report, indent=4)
        print(json_object)

        with open(output_path, "w") as file:
            file.write(json_object)

        return final_result

    @staticmethod
    def format_summary(to_report: StatisticalAnalysis) -> str:
        """
        Format the statistical analysis as a markdown string.

        Args:
            to_report: StatisticalAnalysis object containing analysis data

        Returns:
            str: Formatted string with the error margin calculations and confidence interval
        """
        output = "> [!NOTE]\n"
        output += (
            f"> ## {to_report.failure_count} ± {to_report.margin_of_error_count} "
            "failures detected ({to_report.sample_size} samples)\n"
        )
        output += "> \n"
        output += (
            f"> **90% Confidence Range:** {to_report.confidence_interval_count[0]}-"
            "{to_report.confidence_interval_count[1]} failures\n"
        )
        output += "> \n"
        output += "> **Details:**\n"
        output += (
            f"> - Proportion: {to_report.proportion:.4f} "
            "[{to_report.confidence_interval_prop[0]:.4f}, {to_report.confidence_interval_prop[1]:.4f}]\n"
        )
        output += f"> - Standard Error: {to_report.standard_error:.4f}\n"
        output += f"> - Margin of Error: {to_report.margin_of_error:.4f}\n"
        return output


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python reporter.py failure_count sample_size")
        sys.exit(1)

    failure_count = int(sys.argv[1])
    sample_size = int(sys.argv[2])

    analysis = analyse_sample_from_test(failure_count, sample_size)

    print(Reporter.format_summary(analysis))
