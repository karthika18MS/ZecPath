import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# ============================================================
# ZecPath Day 63 - Configurable Machine Test Pipeline
# Uses the Day 63 configurable adapter and Day 50 evaluator.
# ============================================================

SIMULATION_ROOT = Path(__file__).resolve().parents[1]

# Make the simulation configuration module importable when this
# pipeline is executed directly from the command line.
if str(SIMULATION_ROOT) not in sys.path:
    sys.path.insert(0, str(SIMULATION_ROOT))

try:
    from config.config_loader import SimulationConfig
except ImportError:
    try:
        from config_loader import SimulationConfig
    except ImportError as error:
        raise ImportError(
            "Could not import SimulationConfig. Check that "
            "config_loader.py is available in the simulation config folder."
        ) from error


class MachineTestPipeline:
    """Runs, validates, summarizes, and saves machine-test results."""

    VALID_STATUSES = {"COMPLETED", "NOT_PROVIDED", "INVALID_DATA"}

    def __init__(self, dataset_root=None):
        self.config = SimulationConfig(dataset_root=dataset_root) if dataset_root else SimulationConfig()
        self.dataset_root = Path(self.config.dataset_root)
        self.output_dir = Path(self.config.output_dir)
        self.adapter_path = (
            Path(self.config.simulation_root)
            / "adapters"
            / "machine_test_adapter.py"
        )
        self.adapter_output = self.output_dir / "machine_test_results.json"
        self.pipeline_output = self.output_dir / "machine_test_pipeline_results.json"

    def run_adapter(self):
        print("\n" + "=" * 65)
        print("STAGE 1: RUNNING MACHINE TEST ADAPTER")
        print("=" * 65)

        if not self.adapter_path.is_file():
            raise FileNotFoundError(
                f"Machine test adapter not found: {self.adapter_path}"
            )

        result = subprocess.run(
            [sys.executable, str(self.adapter_path)],
            capture_output=True,
            text=True,
            cwd=str(self.config.project_root),
            timeout=self.config.timeout_seconds,
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Adapter warnings/errors:")
            print(result.stderr)

        if result.returncode != 0:
            raise RuntimeError(
                "Machine test adapter execution failed. "
                f"Exit code: {result.returncode}"
            )

        if not self.adapter_output.is_file():
            raise FileNotFoundError(
                "Machine test adapter did not generate its output JSON: "
                f"{self.adapter_output}"
            )

        print("Machine test adapter executed successfully.")
        return True

    def load_adapter_output(self):
        print("\n" + "=" * 65)
        print("STAGE 2: LOADING MACHINE TEST RESULTS")
        print("=" * 65)

        try:
            with self.adapter_output.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Adapter output contains invalid JSON: {error}"
            ) from error

        if not isinstance(data, dict):
            raise ValueError("Machine test results must contain a JSON object.")

        candidates = data.get("candidate_results")
        if not isinstance(candidates, list):
            raise ValueError(
                "Adapter output must contain candidate_results as a list."
            )

        print("Candidate records loaded:", len(candidates))
        return data

    def validate_candidate_results(self, candidates):
        print("\n" + "=" * 65)
        print("STAGE 3: VALIDATING MACHINE TEST RESULTS")
        print("=" * 65)

        errors = []
        seen_ids = set()

        for index, candidate in enumerate(candidates, start=1):
            if not isinstance(candidate, dict):
                errors.append(f"Record {index} is not a JSON object.")
                continue

            candidate_id = candidate.get("candidate_id")
            job_id = candidate.get("job_id")

            if not isinstance(candidate_id, str) or not candidate_id.strip():
                errors.append(f"Record {index}: Missing or invalid candidate_id.")
                continue

            if not isinstance(job_id, str) or not job_id.strip():
                errors.append(f"{candidate_id}: Missing or invalid job_id.")

            if candidate_id in seen_ids:
                errors.append(f"{candidate_id}: Duplicate candidate record.")
            seen_ids.add(candidate_id)

            status = candidate.get("assessment_status")
            if status not in self.VALID_STATUSES:
                errors.append(f"{candidate_id}: Invalid assessment status: {status!r}.")
                continue

            score = candidate.get("machine_test_score")
            if status == "COMPLETED":
                if (
                    not isinstance(score, (int, float))
                    or isinstance(score, bool)
                    or not 0 <= score <= 100
                ):
                    errors.append(
                        f"{candidate_id}: COMPLETED candidate must have "
                        "a numeric machine_test_score between 0 and 100."
                    )
            elif score is not None:
                errors.append(
                    f"{candidate_id}: {status} candidate must not have a score."
                )

        if errors:
            print("\nValidation errors found:")
            for error in errors:
                print("-", error)
            return False, errors

        print("Candidate validation successful.")
        print("No validation errors found.")
        return True, []

    @staticmethod
    def calculate_summary(candidates):
        completed = [
            item for item in candidates
            if isinstance(item, dict)
            and item.get("assessment_status") == "COMPLETED"
        ]
        not_provided = [
            item for item in candidates
            if isinstance(item, dict)
            and item.get("assessment_status") == "NOT_PROVIDED"
        ]
        invalid = [
            item for item in candidates
            if isinstance(item, dict)
            and item.get("assessment_status") == "INVALID_DATA"
        ]
        scores = [
            item["machine_test_score"]
            for item in completed
            if isinstance(item.get("machine_test_score"), (int, float))
            and not isinstance(item.get("machine_test_score"), bool)
        ]

        categories = {}
        for candidate in completed:
            category = candidate.get("score_category") or "Uncategorized"
            categories[category] = categories.get(category, 0) + 1

        return {
            "total_candidates": len(candidates),
            "completed": len(completed),
            "not_provided": len(not_provided),
            "invalid_data": len(invalid),
            "scored_candidates": len(scores),
            "average_machine_test_score": round(sum(scores) / len(scores), 2) if scores else None,
            "highest_machine_test_score": max(scores) if scores else None,
            "lowest_machine_test_score": min(scores) if scores else None,
            "score_categories": categories,
        }

    @staticmethod
    def build_candidate_report(candidates):
        fields = (
            "candidate_id",
            "job_id",
            "assessment_status",
            "machine_test_score",
            "score_category",
            "score_status",
            "source_file",
            "data_provenance",
            "is_verified_real_candidate_result",
        )
        return [
            {field: candidate.get(field, False if field == "is_verified_real_candidate_result" else None)
             for field in fields}
            for candidate in candidates
            if isinstance(candidate, dict)
        ]

    def save_output(self, output):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with self.pipeline_output.open("w", encoding="utf-8") as file:
            json.dump(output, file, indent=4, ensure_ascii=False)
        print("\nPipeline output saved successfully:")
        print(self.pipeline_output)

    def run(self):
        start_time = datetime.now()
        print("\n" + "#" * 65)
        print("ZECPath - CONFIGURABLE MACHINE TEST PIPELINE")
        print("#" * 65)
        print("Dataset:", self.config.dataset_name)
        print("Dataset root:", self.dataset_root)
        print("Output directory:", self.output_dir)

        self.run_adapter()
        adapter_data = self.load_adapter_output()
        candidates = adapter_data["candidate_results"]
        validation_success, validation_errors = self.validate_candidate_results(candidates)
        summary = self.calculate_summary(candidates)
        candidate_report = self.build_candidate_report(candidates)
        execution_time = round((datetime.now() - start_time).total_seconds(), 3)

        output = {
            "pipeline": "ZecPath Day 63 Configurable Machine Test Pipeline",
            "adapter": "ZecPath Day 63 Configurable Machine Test Adapter",
            "scoring_engine": "ZecPath Day 50 Machine Test Evaluation Engine",
            "dataset": {
                "dataset_name": self.config.dataset_name,
                "dataset_type": self.config.dataset_type,
                "dataset_root": str(self.dataset_root),
            },
            "pipeline_status": "SUCCESS" if validation_success else "VALIDATION_FAILED",
            "scoring_policy": adapter_data.get("scoring_policy", {}),
            "data_provenance": adapter_data.get("data_provenance"),
            "generated_at": datetime.now().astimezone().isoformat(),
            "execution_time_seconds": execution_time,
            "stages": {
                "adapter_execution": "SUCCESS",
                "data_loading": "SUCCESS",
                "candidate_validation": "SUCCESS" if validation_success else "FAILED",
                "summary_calculation": "SUCCESS",
                "candidate_report_generation": "SUCCESS",
            },
            "validation": {
                "is_valid": validation_success,
                "total_validation_errors": len(validation_errors),
                "errors": validation_errors,
            },
            "summary": summary,
            "candidate_results": candidate_report,
            "source_output_file": str(self.adapter_output),
            "adapter_file_errors": adapter_data.get("file_errors", []),
        }

        self.save_output(output)

        print("\n" + "#" * 65)
        print("MACHINE TEST PIPELINE EXECUTION SUMMARY")
        print("#" * 65)
        print("Pipeline Status :", output["pipeline_status"])
        print("Total Candidates:", summary["total_candidates"])
        print("Completed       :", summary["completed"])
        print("Not Provided    :", summary["not_provided"])
        print("Invalid Data    :", summary["invalid_data"])
        print("Average Score   :", summary["average_machine_test_score"])
        print("Execution Time  :", execution_time, "seconds")
        print("#" * 65)

        if not validation_success:
            raise RuntimeError(
                "Machine test pipeline validation failed. "
                "Check the validation errors in the output JSON."
            )

        return output


def run_pipeline(dataset_root=None):
    return MachineTestPipeline(dataset_root=dataset_root).run()


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as error:
        print("\nMACHINE TEST PIPELINE FAILED")
        print("Reason:", error)
        raise
