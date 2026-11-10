
"""
ZecPath Day64 - Configurable ATS Adapter

Connects the existing ATS input and ATS scoring pipelines
to the End-to-End Simulation Environment.

The adapter does not calculate ATS scores itself.
It reuses the existing ATS pipelines and validates their outputs.
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime


# ==========================================================
# CONFIGURATION IMPORT
# ==========================================================

SIMULATION_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = SIMULATION_ROOT.parents[1]

# Add paths for importing project modules.
for path in (PROJECT_ROOT, SIMULATION_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from config_loader import SimulationConfig


# ==========================================================
# ATS ADAPTER
# ==========================================================

class ATSAdapter:

    def __init__(self, dataset_root=None):

        self.config = SimulationConfig()

        self.project_root = PROJECT_ROOT
        self.simulation_root = SIMULATION_ROOT

        # Use configured dataset root unless explicitly supplied.
        self.dataset_root = (
            Path(dataset_root).resolve()
            if dataset_root
            else self.config.dataset_root
        )

        self.pipeline_root = self.simulation_root / "pipeline"
        self.output_root = self.simulation_root / "outputs"

        self.output_root.mkdir(
            parents=True,
            exist_ok=True
        )

        # Pipeline paths.
        self.ats_input_pipeline = (
            self.pipeline_root / "ats_input_pipeline.py"
        )

        self.ats_scoring_pipeline = (
            self.pipeline_root / "ats_scoring_pipeline.py"
        )

        # Result paths.
        self.ats_input_results = (
            self.output_root / "ats_input_results.json"
        )

        self.ats_scoring_results = (
            self.output_root / "ats_scoring_results.json"
        )

        self.execution_log = []

        print("\nInitializing ZecPath ATS Adapter...")
        print("ATS Adapter initialized successfully.")
        print("Dataset Root:", self.dataset_root)
        print("Simulation Root:", self.simulation_root)
        print("Output Directory:", self.output_root)

    # ------------------------------------------------------
    # RUN PYTHON PIPELINE
    # ------------------------------------------------------

    def execute_pipeline(self, pipeline_path, pipeline_name):

        print("\n" + "=" * 60)
        print(f"Executing: {pipeline_name}")
        print("=" * 60)

        if not pipeline_path.exists():
            raise FileNotFoundError(
                f"{pipeline_name} not found: {pipeline_path}"
            )

        start_time = datetime.now()

        process = subprocess.run(
            [
                sys.executable,
                str(pipeline_path)
            ],
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False
        )

        execution_time = (
            datetime.now() - start_time
        ).total_seconds()

        log_entry = {
            "pipeline": pipeline_name,
            "status": (
                "SUCCESS"
                if process.returncode == 0
                else "FAILED"
            ),
            "return_code": process.returncode,
            "execution_time_seconds": round(
                execution_time, 4
            ),
            "stdout": process.stdout,
            "stderr": process.stderr
        }

        self.execution_log.append(log_entry)

        if process.stdout:
            print(process.stdout)

        if process.returncode != 0:

            if process.stderr:
                print(process.stderr)

            raise RuntimeError(
                f"{pipeline_name} failed with "
                f"return code {process.returncode}"
            )

        print(f"{pipeline_name}: SUCCESS")

        return log_entry

    # ------------------------------------------------------
    # LOAD JSON RESULTS
    # ------------------------------------------------------

    @staticmethod
    def load_json(file_path):

        if not file_path.exists():
            raise FileNotFoundError(
                f"ATS result file not found: {file_path}"
            )

        try:
            with file_path.open(
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid JSON in {file_path}: {error}"
            ) from error

        if not isinstance(data, dict):
            raise ValueError(
                f"Invalid result structure in {file_path}. "
                "Expected a JSON object."
            )

        return data

    # ------------------------------------------------------
    # VALIDATE ATS INPUT RESULTS
    # ------------------------------------------------------

    def validate_input_results(self):

        data = self.load_json(
            self.ats_input_results
        )

        candidates = data.get("candidate_results")

        if not isinstance(candidates, list):
            raise ValueError(
                "Invalid ATS input results: "
                "candidate_results must be a list."
            )

        candidate_ids = set()

        for candidate in candidates:

            if not isinstance(candidate, dict):
                raise ValueError(
                    "ATS input results contain an invalid candidate."
                )

            candidate_id = candidate.get("candidate_id")

            if not candidate_id:
                raise ValueError(
                    "ATS input result contains a candidate "
                    "without candidate_id."
                )

            if candidate_id in candidate_ids:
                raise ValueError(
                    f"Duplicate ATS input result for {candidate_id}"
                )

            candidate_ids.add(candidate_id)

        return {
            "total_candidates": len(candidates),
            "candidates": candidates
        }

    # ------------------------------------------------------
    # VALIDATE ATS SCORING RESULTS
    # ------------------------------------------------------

    def validate_scoring_results(self):

        data = self.load_json(
            self.ats_scoring_results
        )

        candidates = data.get("candidate_results")

        if not isinstance(candidates, list):
            raise ValueError(
                "Invalid ATS scoring results: "
                "candidate_results must be a list."
            )

        candidate_ids = set()

        for candidate in candidates:

            if not isinstance(candidate, dict):
                raise ValueError(
                    "ATS scoring results contain an invalid candidate."
                )

            candidate_id = candidate.get("candidate_id")

            if not candidate_id:
                raise ValueError(
                    "ATS result contains a candidate "
                    "without candidate_id."
                )

            if candidate_id in candidate_ids:
                raise ValueError(
                    f"Duplicate ATS result for {candidate_id}"
                )

            candidate_ids.add(candidate_id)

            status = candidate.get("ats_scoring_status")

            if status == "COMPLETED":

                scores = candidate.get("scores", {})

                if not isinstance(scores, dict):
                    raise ValueError(
                        f"{candidate_id} has invalid score data."
                    )

                final_score = scores.get("final_ats_score")

                if (
                    isinstance(final_score, bool)
                    or not isinstance(final_score, (int, float))
                ):
                    raise ValueError(
                        f"{candidate_id} has no valid "
                        "final ATS score."
                    )

                if not 0 <= final_score <= 100:
                    raise ValueError(
                        f"{candidate_id} has an ATS score "
                        "outside the 0-100 range."
                    )

            elif status not in ("BLOCKED", "ERROR"):
                raise ValueError(
                    f"{candidate_id} has an unknown "
                    f"ATS scoring status: {status}"
                )

        return {
            "total_candidates": len(candidates),
            "candidates": candidates
        }

    # ------------------------------------------------------
    # RUN ATS INPUT PIPELINE
    # ------------------------------------------------------

    def run_input_pipeline(self):

        self.execute_pipeline(
            self.ats_input_pipeline,
            "ATS Input Pipeline"
        )

        return self.validate_input_results()

    # ------------------------------------------------------
    # RUN ATS SCORING PIPELINE
    # ------------------------------------------------------

    def run_scoring_pipeline(self):

        self.execute_pipeline(
            self.ats_scoring_pipeline,
            "ATS Scoring Pipeline"
        )

        return self.validate_scoring_results()

    # ------------------------------------------------------
    # REUSE EXISTING RESULTS
    # ------------------------------------------------------

    def reuse_pipeline_results(self):

        print("\nReusing existing ATS pipeline results...")

        input_result = self.validate_input_results()

        scoring_result = self.validate_scoring_results()

        print("ATS input results validated.")
        print("ATS scoring results validated.")
        print("No ATS pipeline was executed again.")

        return input_result, scoring_result

    # ------------------------------------------------------
    # RUN COMPLETE ATS PROCESS
    # ------------------------------------------------------

    def run(self, reuse_existing_results=False):

        print("\n" + "#" * 60)
        print("ZECPath DAY64 - ATS ADAPTER")
        print("#" * 60)

        start_time = datetime.now()

        if reuse_existing_results:

            # Use results already generated by the orchestrator.
            input_result, scoring_result = (
                self.reuse_pipeline_results()
            )

        else:

            # Standalone execution: run both pipelines.
            input_result = self.run_input_pipeline()

            print(
                "\nCandidates prepared:",
                input_result["total_candidates"]
            )

            scoring_result = self.run_scoring_pipeline()

        candidates = scoring_result["candidates"]

        completed = sum(
            item.get("ats_scoring_status") == "COMPLETED"
            for item in candidates
        )

        blocked = sum(
            item.get("ats_scoring_status") == "BLOCKED"
            for item in candidates
        )

        errors = sum(
            item.get("ats_scoring_status") == "ERROR"
            for item in candidates
        )

        execution_time = (
            datetime.now() - start_time
        ).total_seconds()

        result = {
            "adapter": "ZecPath Day64 ATS Adapter",
            "status": "SUCCESS",
            "dataset_root": str(self.dataset_root),
            "results_reused": reuse_existing_results,
            "total_input_candidates": input_result["total_candidates"],
            "total_candidates": len(candidates),
            "completed": completed,
            "blocked": blocked,
            "errors": errors,
            "execution_time_seconds": round(
                execution_time, 4
            ),
            "candidate_results": candidates,
            "execution_log": self.execution_log
        }

        print("\n" + "=" * 60)
        print("ATS ADAPTER SUMMARY")
        print("=" * 60)

        print(
            "Input Candidates:",
            input_result["total_candidates"]
        )
        print("Total Scoring Candidates:", len(candidates))
        print("ATS Completed:", completed)
        print("ATS Blocked:", blocked)
        print("ATS Errors:", errors)
        print("Results Reused:", reuse_existing_results)

        print(
            "Execution Time:",
            round(execution_time, 4),
            "seconds"
        )

        print("\nATS Adapter completed successfully.")

        return result


# ==========================================================
# STANDALONE EXECUTION
# ==========================================================

if __name__ == "__main__":

    adapter = ATSAdapter()

    # Standalone execution runs ATS input and scoring pipelines.
    result = adapter.run(
        reuse_existing_results=False
    )

    print("\nATS Adapter Result:")

    print(
        json.dumps(
            {
                "status": result["status"],
                "total_candidates": result["total_candidates"],
                "completed": result["completed"],
                "blocked": result["blocked"],
                "errors": result["errors"],
                "results_reused": result["results_reused"]
            },
            indent=4
        )
    )
