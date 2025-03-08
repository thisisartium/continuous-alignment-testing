import json
import math
import os
import sys
from datetime import datetime
from typing import Optional, Any, Dict


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
    def error_margin_summary(failure_count: int, sample_size: int) -> str:
        """
        Calculate the error margin and confidence interval for a given sample.

        Args:
            failure_count (int): Number of failures in the sample
            sample_size (int): Total size of the sample

        Returns:
            str: Formatted string with the error margin calculations and confidence interval
        """
        # Calculate sample proportion
        p_hat = failure_count / sample_size

        # Determine z-score for 90% confidence level (approximately 1.645)
        z = 1.645

        # Calculate standard error
        se = math.sqrt(p_hat * (1 - p_hat) / sample_size)

        # Calculate margin of error
        me = z * se

        # Calculate confidence interval bounds as proportions
        lower_bound_prop = p_hat - me
        upper_bound_prop = p_hat + me

        # Convert proportion bounds to integer counts
        lower_bound_count = math.ceil(lower_bound_prop * sample_size)
        upper_bound_count = int(upper_bound_prop * sample_size)

        # Format the output string
        output = f"> [!NOTE]\n"
        output += f"> ### There are {failure_count} failures out of {sample_size} generations.\n"
        output += f"> Sample Proportion (p̂): {p_hat:.4f}\n"
        output += f"> Standard Error (SE): {se:.6f}\n"
        output += f"> Margin of Error (ME): {me:.6f}\n"
        output += f"> 90% Confidence Interval: [{lower_bound_prop:.6f}, {upper_bound_prop:.6f}]\n"
        output += f"> 90% Confidence Interval (Count): [{lower_bound_count}, {upper_bound_count}]"

        return output

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python reporter.py failure_count sample_size")
        sys.exit(1)

    failure_count = int(sys.argv[1])
    sample_size = int(sys.argv[2])

    print(Reporter.error_margin_summary(failure_count, sample_size))
