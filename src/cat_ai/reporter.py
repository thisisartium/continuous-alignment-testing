import json
import os
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
