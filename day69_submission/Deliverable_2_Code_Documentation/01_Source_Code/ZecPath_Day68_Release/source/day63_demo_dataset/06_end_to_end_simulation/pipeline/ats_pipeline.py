
"""
ZecPath Day64 - Integrated ATS Pipeline

Integrates:
1. Dataset ATS input preparation
2. Day63 ATS scoring
3. Existing Day21 eligibility engine

The original scoring engines are reused without modification.

Updated:
- Reuses existing ATS input and scoring results.
- Prevents duplicate ATS pipeline execution.
- Uses configurable dataset paths through ATSAdapter.
"""

import json
import subprocess
import sys

from datetime import datetime
from pathlib import Path


# ==========================================================
# PROJECT PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

SIMULATION_ROOT = (
    PROJECT_ROOT
    / "day63_demo_dataset"
    / "06_end_to_end_simulation"
)

OUTPUT_DIR = SIMULATION_ROOT / "outputs"

ADAPTER_PATH = (
    SIMULATION_ROOT
    / "adapters"
    / "ats_adapter.py"
)

ELIGIBILITY_RUNNER = (
    PROJECT_ROOT
    / "eligibility_engine"
    / "run_day63_eligibility.py"
)

ELIGIBILITY_RESULTS = (
    PROJECT_ROOT
    / "eligibility_engine"
    / "day63_results"
    / "day63_eligibility_summary.json"
)

FINAL_OUTPUT = OUTPUT_DIR / "ats_pipeline_results.json"


# ==========================================================
# JSON HELPERS
# ==========================================================

def load_json(file_path):

    if not file_path.exists():

        raise FileNotFoundError(
            f"Required result file not found: {file_path}"
        )

    with file_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_json(data, file_path):

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with file_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ==========================================================
# RUN ELIGIBILITY ENGINE
# ==========================================================

def run_eligibility_engine():

    print("\n" + "=" * 65)

    print("RUNNING DAY21 ELIGIBILITY ENGINE")

    print("=" * 65)

    if not ELIGIBILITY_RUNNER.exists():

        raise FileNotFoundError(
            f"Eligibility runner not found: {ELIGIBILITY_RUNNER}"
        )

    process = subprocess.run(
        [
            sys.executable,
            str(ELIGIBILITY_RUNNER)
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False
    )

    if process.stdout:
        print(process.stdout)

    if process.stderr:
        print(process.stderr)

    if process.returncode != 0:

        raise RuntimeError(
            "Day21 Eligibility Engine execution failed. "
            f"Return code: {process.returncode}"
        )

    eligibility_data = load_json(
        ELIGIBILITY_RESULTS
    )

    if not isinstance(
        eligibility_data.get("candidate_results"),
        list
    ):

        raise ValueError(
            "Eligibility output does not contain "
            "a valid candidate_results list."
        )

    print("Eligibility Engine: SUCCESS")

    return eligibility_data


# ==========================================================
# MERGE ATS AND ELIGIBILITY RESULTS
# ==========================================================

def merge_candidate_results(
    ats_candidates,
    eligibility_candidates
):

    eligibility_map = {}

    for item in eligibility_candidates:

        candidate_id = item.get("candidate_id")

        if not candidate_id:

            raise ValueError(
                "Eligibility result contains a missing candidate ID."
            )

        if candidate_id in eligibility_map:

            raise ValueError(
                f"Duplicate eligibility result: {candidate_id}"
            )

        eligibility_map[candidate_id] = item

    merged_candidates = []

    for ats_candidate in ats_candidates:

        candidate_id = ats_candidate.get(
            "candidate_id"
        )

        if not candidate_id:

            raise ValueError(
                "ATS result contains a missing candidate ID."
            )

        candidate = dict(ats_candidate)

        eligibility_result = eligibility_map.get(
            candidate_id
        )

        if eligibility_result is None:

            eligibility_result = {
                "candidate_id": candidate_id,
                "eligibility_status": "NOT_EVALUATED",
                "reason": (
                    "No matching eligibility result was found."
                ),
                "failed_rules": []
            }

        # Keep the complete eligibility result nested.
        candidate["eligibility"] = eligibility_result

        candidate["eligibility_status"] = (
            eligibility_result.get(
                "eligibility_status",
                "NOT_EVALUATED"
            )
        )

        merged_candidates.append(candidate)

    return merged_candidates


# ==========================================================
# BUILD SUMMARY
# ==========================================================

def build_summary(candidates):

    total = len(candidates)

    ats_completed = sum(
        item.get("ats_scoring_status") == "COMPLETED"
        for item in candidates
    )

    ats_blocked = sum(
        item.get("ats_scoring_status") == "BLOCKED"
        for item in candidates
    )

    ats_errors = sum(
        item.get("ats_scoring_status") == "ERROR"
        for item in candidates
    )

    eligible = sum(
        item.get("eligibility_status") == "Eligible"
        for item in candidates
    )

    review = sum(
        item.get("eligibility_status") == "Review"
        for item in candidates
    )

    rejected = sum(
        item.get("eligibility_status") == "Rejected"
        for item in candidates
    )

    eligibility_blocked = sum(
        item.get("eligibility_status") == "BLOCKED"
        for item in candidates
    )

    eligibility_errors = sum(
        item.get("eligibility_status") == "ERROR"
        for item in candidates
    )

    not_evaluated = sum(
        item.get("eligibility_status") == "NOT_EVALUATED"
        for item in candidates
    )

    return {

        "total_candidates": total,

        "ats_completed": ats_completed,

        "ats_blocked": ats_blocked,

        "ats_errors": ats_errors,

        "eligible": eligible,

        "review": review,

        "rejected": rejected,

        "eligibility_blocked": eligibility_blocked,

        "eligibility_errors": eligibility_errors,

        "not_evaluated": not_evaluated

    }


# ==========================================================
# MAIN ATS PIPELINE
# ==========================================================

class ATSPipeline:

    def __init__(self):

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        print("\nInitializing ZecPath Integrated ATS Pipeline...")

        print("Pipeline initialized successfully.")

    # ------------------------------------------------------
    # RUN ATS ADAPTER
    # ------------------------------------------------------

    def run_ats_adapter(self):

        print("\n" + "=" * 65)

        print("STEP 1: ATS ADAPTER")

        print("=" * 65)

        if not ADAPTER_PATH.exists():

            raise FileNotFoundError(
                f"ATS adapter not found: {ADAPTER_PATH}"
            )

        # Import only after setting the project root.
        sys.path.insert(
            0,
            str(SIMULATION_ROOT)
        )

        from adapters.ats_adapter import ATSAdapter

        ats_adapter = ATSAdapter()

        # Reuse previously generated ATS results.
        # Do not execute ATS input or scoring again.

        ats_result = ats_adapter.run(
            reuse_existing_results=True
        )

        return ats_result

    # ------------------------------------------------------
    # EXECUTE COMPLETE PIPELINE
    # ------------------------------------------------------

    def run(self):

        print("\n" + "#" * 65)

        print("ZECPath DAY64 - INTEGRATED ATS PIPELINE")

        print("#" * 65)

        start_time = datetime.now()

        # --------------------------------------------------
        # STEP 1: ATS ADAPTER
        # --------------------------------------------------

        print("\nSTEP 1: REUSING EXISTING ATS RESULTS")

        ats_result = self.run_ats_adapter()

        if ats_result.get("status") != "SUCCESS":

            raise RuntimeError(
                "ATS result reuse failed: "
                f"{ats_result.get('status')}"
            )

        ats_candidates = ats_result.get(
            "candidate_results",
            []
        )

        if not isinstance(ats_candidates, list):

            raise ValueError(
                "ATS adapter returned invalid candidate results."
            )

        print(
            "\nATS candidates received:",
            len(ats_candidates)
        )

        print(
            "ATS results reused:",
            ats_result.get("results_reused", False)
        )

        print(
            "ATS pipelines executed:",
            len(ats_result.get("execution_log", []))
        )

        # --------------------------------------------------
        # STEP 2: ELIGIBILITY ENGINE
        # --------------------------------------------------

        eligibility_data = run_eligibility_engine()

        eligibility_candidates = eligibility_data[
            "candidate_results"
        ]

        # --------------------------------------------------
        # STEP 3: MERGE RESULTS
        # --------------------------------------------------

        print("\n" + "=" * 65)

        print("STEP 3: MERGING ATS AND ELIGIBILITY RESULTS")

        print("=" * 65)

        merged_candidates = merge_candidate_results(
            ats_candidates,
            eligibility_candidates
        )

        # --------------------------------------------------
        # STEP 4: SUMMARY
        # --------------------------------------------------

        summary = build_summary(
            merged_candidates
        )

        execution_time = (
            datetime.now() - start_time
        ).total_seconds()

        pipeline_status = (
            "SUCCESS"
            if (
                summary["ats_errors"] == 0
                and summary["eligibility_errors"] == 0
                and summary["not_evaluated"] == 0
            )
            else "PARTIAL_SUCCESS"
        )

        final_output = {

            "engine": "ZecPath Day64 Integrated ATS Pipeline",

            "pipeline_status": pipeline_status,

            "generated_at": datetime.now().astimezone().isoformat(),

            "execution_time_seconds": round(
                execution_time,
                4
            ),

            "stages": {

                "ats_adapter": ats_result["status"],

                "ats_results_reused": ats_result.get(
                    "results_reused",
                    False
                ),

                "ats_pipelines_executed": len(
                    ats_result.get("execution_log", [])
                ),

                "eligibility_engine": "SUCCESS"

            },

            "summary": summary,

            "candidate_results": merged_candidates

        }

        # --------------------------------------------------
        # STEP 5: SAVE RESULTS
        # --------------------------------------------------

        save_json(
            final_output,
            FINAL_OUTPUT
        )

        # --------------------------------------------------
        # FINAL REPORT
        # --------------------------------------------------

        print("\n" + "=" * 65)

        print("INTEGRATED ATS PIPELINE SUMMARY")

        print("=" * 65)

        print("Pipeline Status:", pipeline_status)

        print("Total Candidates:", summary["total_candidates"])

        print("ATS Completed:", summary["ats_completed"])

        print("ATS Blocked:", summary["ats_blocked"])

        print("ATS Errors:", summary["ats_errors"])

        print("Eligible:", summary["eligible"])

        print("Review:", summary["review"])

        print("Rejected:", summary["rejected"])

        print("Eligibility Blocked:", summary["eligibility_blocked"])

        print("Eligibility Errors:", summary["eligibility_errors"])

        print("Not Evaluated:", summary["not_evaluated"])

        print(
            "ATS Results Reused:",
            ats_result.get("results_reused", False)
        )

        print(
            "ATS Pipelines Executed:",
            len(ats_result.get("execution_log", []))
        )

        print(
            "Execution Time:",
            round(execution_time, 4),
            "seconds"
        )

        print("\nResults saved to:")

        print(FINAL_OUTPUT)

        print("\nIntegrated ATS Pipeline completed.")

        return final_output


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    pipeline = ATSPipeline()

    result = pipeline.run()

    print("\nFinal pipeline status:", result["pipeline_status"])
