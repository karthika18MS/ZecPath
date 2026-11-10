
"""
ZecPath - Reusable HR Pipeline

Features:
1. Uses shared SimulationConfig.
2. Uses configurable output directory.
3. Executes the HR adapter.
4. Validates HR results.
5. Detects duplicate candidate/job records.
6. Generates HR summary statistics.
7. Preserves data provenance.
8. Handles missing and invalid output files.
"""

import json
import subprocess
import sys
import time

from pathlib import Path
from datetime import datetime, timezone


# ============================================================
# PATH CONFIGURATION
# ============================================================

SIMULATION_ROOT = Path(__file__).resolve().parents[1]

PROJECT_ROOT = SIMULATION_ROOT.parents[1]

ADAPTER_FILE = (
    SIMULATION_ROOT / "adapters" / "hr_adapter.py"
)


# ============================================================
# LOAD SHARED CONFIGURATION
# ============================================================

sys.path.insert(0, str(SIMULATION_ROOT))

from config_loader import SimulationConfig


CONFIG = SimulationConfig()

OUTPUT_DIR = CONFIG.output_dir

HR_OUTPUT_FILE = OUTPUT_DIR / "hr_results.json"

PIPELINE_OUTPUT_FILE = (
    OUTPUT_DIR / "hr_pipeline_results.json"
)


# ============================================================
# JSON HELPERS
# ============================================================

def load_json(file_path):

    if not file_path.exists():

        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except json.JSONDecodeError as error:

        raise ValueError(
            f"Invalid JSON in {file_path}: {error}"
        )


def save_json(data, file_path):

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# RUN HR ADAPTER
# ============================================================

def run_hr_adapter():

    print("\n" + "=" * 65)

    print("STEP 1: RUNNING HR ADAPTER")

    print("=" * 65)

    if not ADAPTER_FILE.exists():

        raise FileNotFoundError(
            f"HR adapter not found: {ADAPTER_FILE}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    process = subprocess.run(

        [
            sys.executable,
            str(ADAPTER_FILE)
        ],

        cwd=str(PROJECT_ROOT),

        capture_output=True,

        text=True,

        encoding="utf-8",

        errors="replace",

        timeout=CONFIG.timeout_seconds

    )

    if process.stdout:

        print(process.stdout)

    if process.stderr:

        print("\nADAPTER LOG:")

        print(process.stderr)

    if process.returncode != 0:

        raise RuntimeError(
            "HR adapter execution failed. "
            f"Return code: {process.returncode}"
        )

    if not HR_OUTPUT_FILE.exists():

        raise FileNotFoundError(
            "HR adapter did not generate hr_results.json. "
            f"Expected location: {HR_OUTPUT_FILE}"
        )

    print("\nHR adapter execution: SUCCESS")


# ============================================================
# VALIDATE HR RESULTS
# ============================================================

def validate_hr_results(data):

    errors = []

    warnings = []

    if not isinstance(data, dict):

        return False, [
            "HR output must be a JSON object."
        ], []

    candidates = data.get("candidate_results")

    if not isinstance(candidates, list):

        return False, [
            "candidate_results must be a list."
        ], []

    if not candidates:

        errors.append(
            "No HR candidate results found."
        )

    seen_ids = set()

    valid_statuses = {

        "COMPLETED",

        "PENDING_MANUAL_EVALUATION",

        "INCOMPLETE",

        "INVALID_DATA",

        "ERROR"

    }

    for index, candidate in enumerate(candidates):

        if not isinstance(candidate, dict):

            errors.append(
                f"Candidate record {index} is not an object."
            )

            continue

        candidate_id = candidate.get("candidate_id")

        job_id = candidate.get("job_id")

        status = candidate.get("status")

        score = candidate.get("hr_score")

        if not candidate_id:

            errors.append(
                f"Candidate record {index}: "
                "missing candidate_id."
            )

            continue

        if not isinstance(candidate_id, str):

            errors.append(
                f"Candidate record {index}: "
                "candidate_id must be a string."
            )

            continue

        if not job_id:

            errors.append(
                f"{candidate_id}: missing job_id."
            )

        key = (candidate_id, job_id)

        if key in seen_ids:

            errors.append(
                f"Duplicate candidate/job result: {key}"
            )

        seen_ids.add(key)

        if status not in valid_statuses:

            errors.append(
                f"{candidate_id}: invalid HR status {status}."
            )

        if status == "COMPLETED":

            if isinstance(score, bool) or not isinstance(
                score,
                (int, float)
            ):

                errors.append(
                    f"{candidate_id}: completed HR result "
                    "has no numeric score."
                )

            elif not 0 <= score <= 100:

                errors.append(
                    f"{candidate_id}: HR score is outside 0-100."
                )

        elif score is not None:

            warnings.append(
                f"{candidate_id}: non-completed result "
                "contains a score."
            )

    return len(errors) == 0, errors, warnings


# ============================================================
# BUILD PIPELINE SUMMARY
# ============================================================

def build_summary(candidates):

    statuses = [

        "COMPLETED",

        "PENDING_MANUAL_EVALUATION",

        "INCOMPLETE",

        "INVALID_DATA",

        "ERROR"

    ]

    summary = {

        "total_candidates": len(candidates)

    }

    for status in statuses:

        summary[status.lower()] = sum(

            item.get("status") == status

            for item in candidates

            if isinstance(item, dict)

        )

    scores = [

        item["hr_score"]

        for item in candidates

        if isinstance(item, dict)

        and item.get("status") == "COMPLETED"

        and isinstance(
            item.get("hr_score"),
            (int, float)
        )

        and not isinstance(
            item.get("hr_score"),
            bool
        )

    ]

    summary["scored_candidates"] = len(scores)

    summary["average_hr_score"] = (

        round(sum(scores) / len(scores), 2)

        if scores else None

    )

    summary["highest_hr_score"] = (

        max(scores) if scores else None

    )

    summary["lowest_hr_score"] = (

        min(scores) if scores else None

    )

    return summary


# ============================================================
# MAIN HR PIPELINE
# ============================================================

def run_pipeline():

    start_time = time.time()

    print("\n" + "#" * 65)

    print("ZECPath - REUSABLE HR PIPELINE")

    print("#" * 65)

    print("\nDataset name:", CONFIG.dataset_name)

    print("Dataset type:", CONFIG.dataset_type)

    print("Dataset root:", CONFIG.dataset_root)

    print("Output directory:", OUTPUT_DIR)

    print("Project root:", PROJECT_ROOT)

    errors = []

    warnings = []

    try:

        # STEP 1: Execute HR adapter.

        run_hr_adapter()

        # STEP 2: Load adapter output.

        hr_data = load_json(HR_OUTPUT_FILE)

        # STEP 3: Validate HR results.

        is_valid, validation_errors, validation_warnings = (
            validate_hr_results(hr_data)
        )

        errors.extend(validation_errors)

        warnings.extend(validation_warnings)

        candidates = hr_data.get(
            "candidate_results",
            []
        )

        # STEP 4: Build summary.

        summary = build_summary(candidates)

        pipeline_status = (

            "SUCCESS"

            if is_valid

            else "FAILED_VALIDATION"

        )

        # STEP 5: Preserve provenance.

        data_provenance = hr_data.get(

            "data_provenance",

            {

                "source": "HR adapter output",

                "provenance_note": (

                    "Original HR result fields are preserved. "

                    "No additional claim about real or simulated "
                    "evaluation is inferred by this pipeline."

                )

            }

        )

        # STEP 6: Build final output.

        output = {

            "module": "ZecPath Reusable HR Pipeline",

            "dataset": {

                "dataset_name": CONFIG.dataset_name,

                "dataset_type": CONFIG.dataset_type,

                "dataset_root": str(CONFIG.dataset_root)

            },

            "pipeline_status": pipeline_status,

            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "execution_time_seconds": round(
                time.time() - start_time,
                4
            ),

            "validation": {

                "is_valid": is_valid,

                "total_validation_errors": len(errors),

                "errors": errors,

                "warnings": warnings

            },

            "summary": summary,

            "candidate_results": candidates,

            "data_provenance": data_provenance

        }

        # STEP 7: Save pipeline output.

        save_json(
            output,
            PIPELINE_OUTPUT_FILE
        )

        # STEP 8: Display summary.

        print("\n" + "=" * 65)

        print("HR PIPELINE SUMMARY")

        print("=" * 65)

        print(
            "Pipeline status:",
            pipeline_status
        )

        print(
            "Dataset:",
            CONFIG.dataset_name
        )

        print(
            "Total candidates:",
            summary["total_candidates"]
        )

        print(
            "Completed:",
            summary["completed"]
        )

        print(
            "Pending manual evaluation:",
            summary["pending_manual_evaluation"]
        )

        print(
            "Incomplete:",
            summary["incomplete"]
        )

        print(
            "Invalid data:",
            summary["invalid_data"]
        )

        print(
            "Errors:",
            summary["error"]
        )

        print(
            "Average HR score:",
            summary["average_hr_score"]
        )

        print(
            "Validation errors:",
            len(errors)
        )

        print("\nOutput saved:")

        print(PIPELINE_OUTPUT_FILE)

        if not is_valid:

            raise RuntimeError(
                "HR pipeline validation failed. "
                "Check hr_pipeline_results.json."
            )

        return output

    except Exception as error:

        print("\nHR PIPELINE FAILED:", error)

        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    run_pipeline()
