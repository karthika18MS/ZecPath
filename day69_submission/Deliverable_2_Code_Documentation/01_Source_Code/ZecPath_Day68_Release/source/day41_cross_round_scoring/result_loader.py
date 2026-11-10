import json
import os


class ResultLoader:

    def __init__(self, base_directory):
        self.base_directory = base_directory

    def load_json(self, file_path):
        """
        Load a JSON file.
        """

        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def get_candidate_ids(self, directory):
        """
        Find candidate folders inside a directory.

        Example:
        candidate_006
        candidate_007
        candidate_008
        """

        full_directory = os.path.join(
            self.base_directory,
            directory
        )

        if not os.path.exists(full_directory):
            return []

        candidate_ids = []

        for item in os.listdir(full_directory):

            item_path = os.path.join(
                full_directory,
                item
            )

            if (
                os.path.isdir(item_path)
                and item.lower().startswith("candidate_")
            ):
                candidate_ids.append(item)

        return sorted(candidate_ids)

    def load_candidate_file(
        self,
        directory,
        candidate_id,
        filename
    ):
        """
        Load a candidate-specific result file.
        """

        file_path = os.path.join(
            self.base_directory,
            directory,
            candidate_id,
            filename
        )

        if not os.path.exists(file_path):
            return None

        try:
            return self.load_json(file_path)

        except (json.JSONDecodeError, OSError):
            return None

    def load_ats_results(
        self,
        directory,
        filename
    ):
        """
        Load all Day 18 ATS results.
        """

        results = {}

        candidate_ids = self.get_candidate_ids(
            directory
        )

        for candidate_id in candidate_ids:

            data = self.load_candidate_file(
                directory,
                candidate_id,
                filename
            )

            if data is not None:
                results[candidate_id] = data

        return results

    def load_hr_results(
        self,
        directory,
        filename
    ):
        """
        Load Day 37 HR result.

        The current Day 37 output is a common result file
        containing candidate information.
        """

        file_path = os.path.join(
            self.base_directory,
            directory,
            filename
        )

        if not os.path.exists(file_path):
            return {}

        try:
            data = self.load_json(file_path)

        except (json.JSONDecodeError, OSError):
            return {}

        if isinstance(data, dict):

            candidate_info = data.get(
                "candidate_information",
                {}
            )

            candidate_id = candidate_info.get(
                "candidate_id"
            )

            if candidate_id:
                return {
                    candidate_id: data
                }

        return {}

    def load_aptitude_results(
        self,
        logical_file,
        scenario_file
    ):
        """
        Load Day 38 aptitude results.
        """

        logical_path = os.path.join(
            self.base_directory,
            logical_file
        )

        scenario_path = os.path.join(
            self.base_directory,
            scenario_file
        )

        if not os.path.exists(logical_path):
            return {}

        if not os.path.exists(scenario_path):
            return {}

        try:

            logical_data = self.load_json(
                logical_path
            )

            scenario_data = self.load_json(
                scenario_path
            )

        except (json.JSONDecodeError, OSError):
            return {}

        logical_candidate = logical_data.get(
            "candidate_id"
        )

        scenario_candidate = scenario_data.get(
            "candidate_id"
        )

        if (
            logical_candidate
            and logical_candidate == scenario_candidate
        ):
            return {
                logical_candidate: {
                    "logical": logical_data,
                    "scenario": scenario_data
                }
            }

        return {}