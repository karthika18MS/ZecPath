
import json
import subprocess
import sys
import math
from pathlib import Path
from datetime import datetime
from statistics import mean


# ============================================================
# ZECPath DAY 63 - APTITUDE PIPELINE
# ============================================================

CURRENT_DIR = Path(__file__).resolve().parent
SIMULATION_DIR = CURRENT_DIR.parent

ADAPTER_FILE = (
    SIMULATION_DIR / "adapters" / "aptitude_adapter.py"
)

OUTPUT_DIR = SIMULATION_DIR / "outputs"

ADAPTER_OUTPUT = (
    OUTPUT_DIR / "aptitude_results.json"
)

PIPELINE_OUTPUT = (
    OUTPUT_DIR / "aptitude_pipeline_results.json"
)

SCORE_ORIGIN = "SIMULATED_HEURISTIC_DEMO"

VALID_STATUSES = {
    "COMPLETED",
    "INCOMPLETE",
    "PARTIAL",
    "INVALID_DATA",
    "NOT_PROVIDED"
}


# ============================================================
# 1. EXECUTE APTITUDE ADAPTER
# ============================================================

def run_aptitude_adapter():

    print("\n" + "=" * 65)
    print("STAGE 1: EXECUTING APTITUDE ADAPTER")
    print("=" * 65)

    if not ADAPTER_FILE.exists():
        raise FileNotFoundError(
            f"Aptitude adapter not found: {ADAPTER_FILE}"
        )

    process = subprocess.run(
        [sys.executable, str(ADAPTER_FILE)],
        capture_output=True,
        text=True
    )

    if process.stdout:
        print(process.stdout)

    if process.returncode != 0:
        print(process.stderr)

        raise RuntimeError(
            "Aptitude adapter execution failed."
        )

    print("Aptitude adapter execution successful.")


# ============================================================
# 2. LOAD ADAPTER OUTPUT
# ============================================================

def load_adapter_output():

    print("\n" + "=" * 65)
    print("STAGE 2: LOADING ADAPTER OUTPUT")
    print("=" * 65)

    if not ADAPTER_OUTPUT.exists():
        raise FileNotFoundError(
            f"Aptitude output not found: {ADAPTER_OUTPUT}"
        )

    with ADAPTER_OUTPUT.open(
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "Aptitude adapter output must be a JSON object."
        )

    candidates = data.get("candidates")

    if not isinstance(candidates, list):
        raise ValueError(
            "Aptitude adapter output must contain "
            "a candidates list."
        )

    print("Candidate records loaded:", len(candidates))

    return data


# ============================================================
# 3. VALIDATE CANDIDATE RESULTS
# ============================================================

def validate_candidate_results(candidates):

    print("\n" + "=" * 65)
    print("STAGE 3: VALIDATING CANDIDATE RESULTS")
    print("=" * 65)

    validation_errors = []
    seen_keys = set()

    for index, candidate in enumerate(
        candidates,
        start=1
    ):

        if not isinstance(candidate, dict):

            validation_errors.append(
                f"Record {index} is not a JSON object."
            )
            continue

        candidate_id = candidate.get("candidate_id")
        job_id = candidate.get("job_id")

        if not candidate_id or not job_id:

            validation_errors.append(
                f"Record {index}: Missing candidate_id or job_id."
            )
            continue

        key = (
            str(candidate_id).strip(),
            str(job_id).strip()
        )

        if key in seen_keys:

            validation_errors.append(
                f"{candidate_id}: Duplicate candidate/job record."
            )

        seen_keys.add(key)

        status = str(
            candidate.get("status", "")
        ).upper()

        if status not in VALID_STATUSES:

            validation_errors.append(
                f"{candidate_id}: Invalid assessment status: {status}"
            )
            continue

        score = candidate.get("aptitude_score")

        # ----------------------------------------------------
        # SCORE VALIDATION
        # ----------------------------------------------------

        if status == "COMPLETED":

            if (
                isinstance(score, bool)
                or not isinstance(score, (int, float))
                or not math.isfinite(float(score))
                or not 0 <= score <= 100
            ):

                validation_errors.append(
                    f"{candidate_id}: Completed candidate "
                    "must have a valid aptitude score."
                )

        else:

            if score is not None:

                validation_errors.append(
                    f"{candidate_id}: Non-completed candidate "
                    "must not have an aptitude score."
                )

        # ----------------------------------------------------
        # PROVENANCE VALIDATION
        # ----------------------------------------------------

        is_simulated = candidate.get("is_simulated")

        score_origin = candidate.get("score_origin")

        if not isinstance(is_simulated, bool):

            validation_errors.append(
                f"{candidate_id}: Simulation flag is missing."
            )

        if (
            not isinstance(score_origin, str)
            or not score_origin.strip()
        ):

            validation_errors.append(
                f"{candidate_id}: Score provenance is missing."
            )

    if validation_errors:

        print("\nValidation errors found:")

        for error in validation_errors:
            print("-", error)

        return False, validation_errors

    print("Candidate validation successful.")
    print("No validation errors found.")

    return True, []


# ============================================================
# 4. CALCULATE PIPELINE SUMMARY
# ============================================================

def calculate_summary(candidates, validation_errors):

    completed = [
        item for item in candidates
        if item.get("status") == "COMPLETED"
    ]

    incomplete = [
        item for item in candidates
        if item.get("status") == "INCOMPLETE"
    ]

    partial = [
        item for item in candidates
        if item.get("status") == "PARTIAL"
    ]

    invalid = [
        item for item in candidates
        if item.get("status") == "INVALID_DATA"
    ]

    not_provided = [
        item for item in candidates
        if item.get("status") == "NOT_PROVIDED"
    ]

    scores = [
        float(item["aptitude_score"])
        for item in completed
        if item.get("aptitude_score") is not None
    ]

    average_score = (
        round(mean(scores), 2)
        if scores else None
    )

    distribution = {
        "Strong": 0,
        "Moderate": 0,
        "Needs Improvement": 0
    }

    for candidate in completed:

        level = str(
            candidate.get("evaluation_level") or ""
        ).strip().lower()

        if level == "strong":
            distribution["Strong"] += 1

        elif level == "moderate":
            distribution["Moderate"] += 1

        elif level in (
            "needs improvement",
            "needs_improvement"
        ):
            distribution["Needs Improvement"] += 1

    return {

        "total_candidates": len(candidates),

        "completed": len(completed),

        "incomplete": len(incomplete),

        "partial": len(partial),

        "invalid_data": len(invalid),

        "not_provided": len(not_provided),

        "scored_candidates": len(scores),

        "average_score": average_score,

        "highest_score": max(scores) if scores else None,

        "lowest_score": min(scores) if scores else None,

        "evaluation_distribution": distribution,

        "validation_errors": len(validation_errors)
    }


# ============================================================
# 5. BUILD CANDIDATE REPORT
# ============================================================

def build_candidate_report(candidates):

    candidate_report = []

    for candidate in candidates:

        candidate_report.append({

            "candidate_id": candidate.get(
                "candidate_id"
            ),

            "job_id": candidate.get(
                "job_id"
            ),

            "status": candidate.get(
                "status"
            ),

            "response_status": candidate.get(
                "response_status"
            ),

            "aptitude_score": candidate.get(
                "aptitude_score"
            ),

            "evaluation_level": candidate.get(
                "evaluation_level"
            ),

            "score_origin": candidate.get(
                "score_origin",
                SCORE_ORIGIN
            ),

            "is_simulated": candidate.get(
                "is_simulated",
                True
            ),

            "logical_question_count": candidate.get(
                "logical_question_count",
                0
            ),

            "scenario_question_count": candidate.get(
                "scenario_question_count",
                0
            ),

            "message": candidate.get(
                "message"
            ),

            "scoring_note": candidate.get(
                "scoring_note",
                "Demo-only heuristic scoring. "
                "Not a human evaluation or trained AI assessment."
            )
        })

    return candidate_report


# ============================================================
# 6. SAVE PIPELINE OUTPUT
# ============================================================

def save_pipeline_output(output):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with PIPELINE_OUTPUT.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nPipeline output saved successfully:")
    print(PIPELINE_OUTPUT)


# ============================================================
# 7. MAIN PIPELINE
# ============================================================

def run_pipeline():

    start_time = datetime.now()

    print("\n")
    print("#" * 65)
    print("ZECPath DAY 63 - APTITUDE PIPELINE")
    print("#" * 65)

    # Stage 1
    run_aptitude_adapter()

    # Stage 2
    adapter_data = load_adapter_output()

    candidates = adapter_data["candidates"]

    # Stage 3
    validation_success, validation_errors = (
        validate_candidate_results(candidates)
    )

    # Stage 4
    summary = calculate_summary(
        candidates,
        validation_errors
    )

    # Stage 5
    candidate_report = build_candidate_report(
        candidates
    )

    execution_time = round(
        (datetime.now() - start_time).total_seconds(),
        3
    )

    # --------------------------------------------------------
    # FINAL PIPELINE OUTPUT
    # --------------------------------------------------------

    pipeline_output = {

        "pipeline": "ZecPath Day 63 Aptitude Pipeline",

        "adapter": "ZecPath Day 63 Aptitude Adapter",

        "pipeline_status": (
            "SUCCESS"
            if validation_success
            else "FAILED_VALIDATION"
        ),

        "score_type": adapter_data.get(
            "score_type",
            SCORE_ORIGIN
        ),

        "is_simulated": adapter_data.get(
            "is_simulated",
            True
        ),

        "score_source": adapter_data.get(
            "score_type",
            SCORE_ORIGIN
        ),

        "generated_at": datetime.now().astimezone().isoformat(),

        "execution_time_seconds": execution_time,

        "stages": {

            "adapter_execution": "SUCCESS",

            "data_loading": "SUCCESS",

            "candidate_validation": (
                "SUCCESS"
                if validation_success
                else "FAILED"
            ),

            "summary_calculation": "SUCCESS",

            "candidate_report_generation": "SUCCESS"
        },

        "validation": {

            "status": (
                "SUCCESS"
                if validation_success
                else "FAILED"
            ),

            "is_valid": validation_success,

            "total_validation_errors": len(
                validation_errors
            ),

            "errors": validation_errors
        },

        "summary": summary,

        "candidate_results": candidate_report,

        "source_output_file": str(ADAPTER_OUTPUT)
    }

    save_pipeline_output(pipeline_output)

    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("DAY 63 APTITUDE PIPELINE SUMMARY")
    print("=" * 65)

    print("Total candidates :", summary["total_candidates"])
    print("Completed        :", summary["completed"])
    print("Incomplete       :", summary["incomplete"])
    print("Partial          :", summary["partial"])
    print("Invalid          :", summary["invalid_data"])
    print("Not provided     :", summary["not_provided"])

    print("Average score    :", summary["average_score"])

    print(
        "Validation errors:",
        len(validation_errors)
    )

    print(
        "Pipeline status  :",
        pipeline_output["pipeline_status"]
    )

    print("=" * 65)

    return pipeline_output


if __name__ == "__main__":

    try:
        run_pipeline()

    except Exception as error:

        print("\nAPTITUDE PIPELINE EXECUTION FAILED")
        print("Reason:", error)

        raise
