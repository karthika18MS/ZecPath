import json
import importlib.util
import sys
from pathlib import Path
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

SIMULATION_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIMULATION_ROOT))

from config_loader import SimulationConfig


class MachineTestAdapter:

    def __init__(self, dataset_root=None):
        self.config = SimulationConfig()

        self.dataset_root = (
            Path(dataset_root).resolve()
            if dataset_root
            else self.config.dataset_root
        )

        self.input_dir = (
            self.dataset_root
            / "04_candidate_responses"
            / "machine_test_responses"
        )

        self.profile_dir = (
            self.dataset_root / "01_candidate_profiles"
        )

        self.output_dir = self.config.output_dir
        self.output_file = self.output_dir / "machine_test_results.json"

        self.day50_engine_path = (
            self.config.project_root
            / "day50_machine_test_scoring"
            / "machine_test_evaluator.py"
        )

        self.output_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # LOAD DAY 50 MACHINE TEST ENGINE
    # --------------------------------------------------------

    def load_day50_engine(self):
        if not self.day50_engine_path.exists():
            raise FileNotFoundError(
                f"Day 50 engine not found: {self.day50_engine_path}"
            )

        spec = importlib.util.spec_from_file_location(
            "day50_machine_test_evaluator",
            self.day50_engine_path
        )

        if spec is None or spec.loader is None:
            raise ImportError(
                "Unable to load Day 50 machine test evaluator."
            )

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    # --------------------------------------------------------
    # LOAD JSON
    # --------------------------------------------------------

    @staticmethod
    def load_json(file_path):
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("JSON file must contain an object.")

        return data

    # --------------------------------------------------------
    # BUILD CANDIDATE ROSTER FROM CONFIGURED DATASET
    # --------------------------------------------------------

    def load_candidate_roster(self):
        if not self.profile_dir.exists():
            raise FileNotFoundError(
                f"Candidate profile directory not found: {self.profile_dir}"
            )

        profiles = sorted(self.profile_dir.glob("*.json"))
        if not profiles:
            raise FileNotFoundError(
                f"No candidate profile JSON files found: {self.profile_dir}"
            )

        roster = []
        seen_ids = set()

        for profile_path in profiles:
            profile = self.load_json(profile_path)
            candidate_id = profile.get("candidate_id")

            if not isinstance(candidate_id, str) or not candidate_id.strip():
                raise ValueError(
                    f"Missing or invalid candidate_id in {profile_path.name}"
                )

            candidate_id = candidate_id.strip()

            if candidate_id in seen_ids:
                raise ValueError(
                    f"Duplicate candidate_id in profiles: {candidate_id}"
                )

            seen_ids.add(candidate_id)

            job_id = (
                profile.get("job_id")
                or profile.get("assigned_job_id")
                or profile.get("target_job_id")
            )

            roster.append({
                "candidate_id": candidate_id,
                "job_id": job_id,
                "profile_file": profile_path.name
            })

        return roster

    # --------------------------------------------------------
    # FIND CANDIDATE SUBMISSION
    # --------------------------------------------------------

    def find_submission(self, candidate_id):
        candidate_number = candidate_id.replace("CAND", "")
        file_path = (
            self.input_dir
            / f"candidate_{candidate_number}_machine_test.json"
        )
        return file_path if file_path.is_file() else None

    # --------------------------------------------------------
    # VALIDATE SIMULATED DATA PROVENANCE
    # --------------------------------------------------------

    @staticmethod
    def validate_demo_provenance(data):
        if data.get("data_type") != "SIMULATED_DEMO_DATA":
            raise ValueError(
                "Submission must be labelled SIMULATED_DEMO_DATA."
            )

        if data.get("is_simulated") is not True:
            raise ValueError("Submission is missing is_simulated=True.")

        if data.get("score_source") != "SIMULATED_DEMO_INPUT":
            raise ValueError("Invalid demo score source.")

        if data.get("test_results_are_simulated") is not True:
            raise ValueError("Test results must be labelled as simulated.")

        if data.get("review_scores_are_simulated") is not True:
            raise ValueError("Review scores must be labelled as simulated.")

        task = data.get("task")
        if not isinstance(task, dict):
            raise ValueError("Submission task must be a JSON object.")

        test_results = task.get("test_results")
        review_scores = task.get("review_scores")

        if not isinstance(test_results, dict):
            raise ValueError("task.test_results must be a JSON object.")

        if not isinstance(review_scores, dict):
            raise ValueError("task.review_scores must be a JSON object.")

        if test_results.get("is_simulated") is not True:
            raise ValueError("Test result provenance is missing.")

        if test_results.get("execution_status") != "SIMULATED_NOT_EXECUTED":
            raise ValueError("Unexpected test execution provenance.")

        if review_scores.get("is_simulated") is not True:
            raise ValueError("Reviewer score provenance is missing.")

        if review_scores.get("review_status") != "SIMULATED_NOT_HUMAN_REVIEWED":
            raise ValueError("Unexpected reviewer provenance.")

        return True

    # --------------------------------------------------------
    # EVALUATE ONE CANDIDATE
    # --------------------------------------------------------

    def evaluate_candidate(self, candidate, engine):
        candidate_id = candidate["candidate_id"]
        expected_job_id = candidate.get("job_id")
        file_path = self.find_submission(candidate_id)

        if file_path is None:
            return {
                "candidate_id": candidate_id,
                "job_id": expected_job_id,
                "assessment_status": "NOT_PROVIDED",
                "machine_test_score": None,
                "score_category": None,
                "score_status": "NOT_SCORED",
                "source_file": None,
                "is_simulated": False,
                "score_source": None,
                "data_provenance": "NO_SUBMISSION_AVAILABLE",
                "is_verified_real_candidate_result": False
            }

        data = self.load_json(file_path)

        if data.get("candidate_id") != candidate_id:
            raise ValueError(
                "Candidate ID does not match candidate profile."
            )

        actual_job_id = data.get("job_id")
        if not isinstance(actual_job_id, str) or not actual_job_id.strip():
            raise ValueError("Submission has a missing or invalid job_id.")

        if expected_job_id and actual_job_id != expected_job_id:
            raise ValueError(
                f"Job ID mismatch: profile={expected_job_id}, "
                f"submission={actual_job_id}."
            )

        self.validate_demo_provenance(data)
        engine.validate_input(data)
        evaluation_result = engine.evaluate_submission(data)

        machine_test_score = evaluation_result["machine_test_score"]

        if (
            isinstance(machine_test_score, bool)
            or not isinstance(machine_test_score, (int, float))
            or not 0 <= machine_test_score <= 100
        ):
            raise ValueError("Machine test score must be between 0 and 100.")

        return {
            "candidate_id": candidate_id,
            "job_id": actual_job_id,
            "assessment_status": "COMPLETED",
            "machine_test_score": machine_test_score,
            "score_category": evaluation_result["score_category"],
            "score_status": "SCORED",
            "source_file": file_path.name,
            "is_simulated": True,
            "score_source": "SIMULATED_DEMO_DATA",
            "test_results_are_simulated": True,
            "review_scores_are_simulated": True,
            "is_verified_real_candidate_result": False,
            "data_provenance": (
                "SIMULATED_TEST_RESULTS_AND_SIMULATED_REVIEW_SCORES"
            ),
            "evaluation_result": evaluation_result
        }

    # --------------------------------------------------------
    # RUN BATCH
    # --------------------------------------------------------

    def run(self):
        print("\n" + "=" * 65)
        print("ZecPath - CONFIGURABLE MACHINE TEST ADAPTER")
        print("=" * 65)
        print(f"Dataset: {self.config.dataset_name}")
        print(f"Dataset root: {self.dataset_root}")
        print(f"Input directory: {self.input_dir}")
        print(f"Output directory: {self.output_dir}")
        print("Data mode: SIMULATED DEMO DATA")

        if not self.input_dir.exists():
            raise FileNotFoundError(
                f"Machine test response directory not found: {self.input_dir}"
            )

        engine = self.load_day50_engine()
        candidates = self.load_candidate_roster()

        candidate_results = []
        file_errors = []

        for candidate in candidates:
            candidate_id = candidate["candidate_id"]
            print(f"\nProcessing: {candidate_id}")

            try:
                result = self.evaluate_candidate(candidate, engine)
                candidate_results.append(result)

                print("Status:", result["assessment_status"])
                print("Machine Test Score:", result["machine_test_score"])
                print("Simulated:", result["is_simulated"])

            except (
                OSError,
                json.JSONDecodeError,
                ValueError,
                KeyError,
                TypeError,
            ) as error:
                file_path = self.find_submission(candidate_id)
                error_message = str(error)

                file_errors.append({
                    "candidate_id": candidate_id,
                    "source_file": file_path.name if file_path else None,
                    "error": error_message
                })

                candidate_results.append({
                    "candidate_id": candidate_id,
                    "job_id": candidate.get("job_id"),
                    "assessment_status": "INVALID_DATA",
                    "machine_test_score": None,
                    "score_category": None,
                    "score_status": "NOT_SCORED",
                    "source_file": file_path.name if file_path else None,
                    "is_simulated": None,
                    "score_source": None,
                    "is_verified_real_candidate_result": False,
                    "error": error_message
                })
                print("Invalid data:", error_message)

        total = len(candidate_results)
        completed = sum(
            item["assessment_status"] == "COMPLETED"
            for item in candidate_results
        )
        not_provided = sum(
            item["assessment_status"] == "NOT_PROVIDED"
            for item in candidate_results
        )
        invalid = sum(
            item["assessment_status"] == "INVALID_DATA"
            for item in candidate_results
        )

        scores = [
            item["machine_test_score"]
            for item in candidate_results
            if item.get("machine_test_score") is not None
        ]

        average_score = round(sum(scores) / len(scores), 2) if scores else None
        highest_score = max(scores) if scores else None
        lowest_score = min(scores) if scores else None

        score_categories = {}
        for item in candidate_results:
            if item["assessment_status"] != "COMPLETED":
                continue
            score_category = item["score_category"]
            score_categories[score_category] = (
                score_categories.get(score_category, 0) + 1
            )

        output = {
            "engine": "ZecPath Configurable Machine Test Adapter",
            "scoring_engine": (
                "ZecPath Day 50 Machine Test Evaluation Engine"
            ),
            "dataset": self.config.dataset_name,
            "dataset_type": self.config.dataset_type,
            "dataset_root": str(self.dataset_root),
            "pipeline_status": (
                "SUCCESS" if not file_errors else "PARTIAL_SUCCESS"
            ),
            "scoring_mode": "DEMO",
            "is_simulated": True,
            "score_source": "SIMULATED_DEMO_DATA",
            "generated_at": datetime.now().astimezone().isoformat(),
            "scoring_policy": {
                "test_pass_rate_weight": 0.50,
                "requirement_coverage_weight": 0.20,
                "code_quality_weight": 0.20,
                "readability_weight": 0.10,
                "human_review_required": True,
                "test_execution_required": True,
                "automatic_code_execution": False,
                "test_results_are_simulated": True,
                "review_scores_are_simulated": True,
                "is_verified_real_candidate_result": False
            },
            "data_provenance": {
                "data_type": "SIMULATED_DEMO_DATA",
                "candidate_code": (
                    "Illustrative sample code, not actual candidate submissions."
                ),
                "test_results": (
                    "Illustrative values; test cases were not executed."
                ),
                "review_scores": (
                    "Illustrative values; no human review was performed."
                ),
                "hiring_use": (
                    "Demo testing only. Not suitable for real hiring decisions."
                )
            },
            "summary": {
                "total_candidates": total,
                "completed": completed,
                "not_provided": not_provided,
                "invalid_data": invalid,
                "scored_candidates": len(scores),
                "average_machine_test_score": average_score,
                "highest_machine_test_score": highest_score,
                "lowest_machine_test_score": lowest_score,
                "score_categories": score_categories,
                "file_errors": len(file_errors)
            },
            "candidate_results": candidate_results,
            "file_errors": file_errors
        }

        with self.output_file.open("w", encoding="utf-8") as file:
            json.dump(output, file, indent=4, ensure_ascii=False)

        print("\n" + "=" * 65)
        print("MACHINE TEST ADAPTER SUMMARY")
        print("=" * 65)
        print("Total candidates :", total)
        print("Completed        :", completed)
        print("Not provided     :", not_provided)
        print("Invalid data     :", invalid)
        print("Scored candidates:", len(scores))
        print("Average score    :", average_score)
        print("Highest score    :", highest_score)
        print("Lowest score     :", lowest_score)
        print("File errors      :", len(file_errors))
        print("\nOutput saved to:")
        print(self.output_file)
        print("=" * 65)

        return output


if __name__ == "__main__":
    adapter = MachineTestAdapter()
    adapter.run()
