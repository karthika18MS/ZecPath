
import json
import subprocess
import sys

from pathlib import Path
from datetime import datetime


# ============================================================
# ZecPath Day 63 - Technical Interview Pipeline
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

ADAPTER_PATH = (
    BASE_DIR
    / "adapters"
    / "technical_adapter.py"
)

OUTPUT_DIR = BASE_DIR / "outputs"

ADAPTER_OUTPUT = (
    OUTPUT_DIR
    / "technical_results.json"
)

PIPELINE_OUTPUT = (
    OUTPUT_DIR
    / "technical_pipeline_results.json"
)


# ============================================================
# 1. RUN TECHNICAL ADAPTER
# ============================================================

def run_technical_adapter():

    print("\n" + "=" * 65)
    print("STAGE 1: RUNNING TECHNICAL ADAPTER")
    print("=" * 65)

    if not ADAPTER_PATH.exists():
        raise FileNotFoundError(
            f"Technical adapter not found: {ADAPTER_PATH}"
        )

    result = subprocess.run(
        [
            sys.executable,
            str(ADAPTER_PATH)
        ],
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR)
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print("Adapter warnings/errors:")
        print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(
            "Technical adapter execution failed. "
            f"Exit code: {result.returncode}"
        )

    if not ADAPTER_OUTPUT.exists():
        raise FileNotFoundError(
            "Technical adapter did not generate its output JSON."
        )

    print("\nTechnical adapter executed successfully.")

    return True


# ============================================================
# 2. LOAD ADAPTER OUTPUT
# ============================================================

def load_adapter_output():

    print("\n" + "=" * 65)
    print("STAGE 2: LOADING TECHNICAL RESULTS")
    print("=" * 65)

    with ADAPTER_OUTPUT.open(
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "Technical results must contain a JSON object."
        )

    if "candidate_results" not in data:
        raise ValueError(
            "Missing candidate_results in adapter output."
        )

    candidates = data["candidate_results"]

    if not isinstance(candidates, list):
        raise ValueError(
            "candidate_results must be a list."
        )

    print(
        "Candidate records loaded:",
        len(candidates)
    )

    return data


# ============================================================
# 3. VALIDATE CANDIDATE RESULTS
# ============================================================

def validate_candidate_results(candidates):

    print("\n" + "=" * 65)
    print("STAGE 3: VALIDATING CANDIDATE RESULTS")
    print("=" * 65)

    validation_errors = []
    seen_candidate_ids = set()

    valid_statuses = {
        "COMPLETED",
        "PENDING_REVIEW",
        "NOT_PROVIDED",
        "INVALID_DATA"
    }

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

        if not candidate_id:

            validation_errors.append(
                f"Record {index}: Missing candidate_id."
            )
            continue

        if candidate_id in seen_candidate_ids:

            validation_errors.append(
                f"{candidate_id}: Duplicate candidate record."
            )

        seen_candidate_ids.add(candidate_id)

        status = candidate.get(
            "assessment_status"
        )

        if status not in valid_statuses:

            validation_errors.append(
                f"{candidate_id}: Invalid assessment status."
            )
            continue

        score = candidate.get("technical_score")

        if status == "COMPLETED":

            if not isinstance(score, (int, float)):

                validation_errors.append(
                    f"{candidate_id}: Completed candidate "
                    "has no numeric technical score."
                )

            elif isinstance(score, bool) or not 0 <= score <= 100:

                validation_errors.append(
                    f"{candidate_id}: Technical score "
                    "must be between 0 and 100."
                )

        else:

            if score is not None:

                validation_errors.append(
                    f"{candidate_id}: Non-completed candidate "
                    "must not have a technical score."
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

def calculate_summary(candidates):

    print("\n" + "=" * 65)
    print("STAGE 4: CALCULATING SUMMARY STATISTICS")
    print("=" * 65)

    total_candidates = len(candidates)

    completed = [
        candidate
        for candidate in candidates
        if candidate.get("assessment_status") == "COMPLETED"
    ]

    pending = [
        candidate
        for candidate in candidates
        if candidate.get("assessment_status") == "PENDING_REVIEW"
    ]

    not_provided = [
        candidate
        for candidate in candidates
        if candidate.get("assessment_status") == "NOT_PROVIDED"
    ]

    invalid = [
        candidate
        for candidate in candidates
        if candidate.get("assessment_status") == "INVALID_DATA"
    ]

    scores = [
        candidate["technical_score"]
        for candidate in completed
    ]

    average_score = (
        round(sum(scores) / len(scores), 2)
        if scores else None
    )

    highest_score = (
        max(scores)
        if scores else None
    )

    lowest_score = (
        min(scores)
        if scores else None
    )

    score_categories = {}

    for candidate in completed:

        category = candidate.get(
            "score_category",
            "Uncategorized"
        )

        score_categories[category] = (
            score_categories.get(category, 0) + 1
        )

    summary = {

        "total_candidates": total_candidates,

        "completed": len(completed),

        "pending_review": len(pending),

        "not_provided": len(not_provided),

        "invalid_data": len(invalid),

        "scored_candidates": len(scores),

        "average_technical_score": average_score,

        "highest_technical_score": highest_score,

        "lowest_technical_score": lowest_score,

        "score_categories": score_categories
    }

    print("Total candidates :", total_candidates)
    print("Completed        :", len(completed))
    print("Pending review   :", len(pending))
    print("Not provided     :", len(not_provided))
    print("Invalid data     :", len(invalid))
    print("Average score    :", average_score)
    print("Highest score    :", highest_score)
    print("Lowest score     :", lowest_score)

    return summary


# ============================================================
# 5. BUILD CANDIDATE-WISE REPORT
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

            "assessment_status": candidate.get(
                "assessment_status"
            ),

            "technical_score": candidate.get(
                "technical_score"
            ),

            "score_category": candidate.get(
                "score_category"
            ),

            "score_status": candidate.get(
                "score_status"
            ),

            "is_simulated": candidate.get(
                "is_simulated",
                True
            ),

            "score_source": candidate.get(
                "score_source",
                "SIMULATED_HEURISTIC_DEMO"
            ),

            "total_questions": candidate.get(
                "total_questions",
                0
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
    print("ZECPath DAY 63 - TECHNICAL INTERVIEW PIPELINE")
    print("#" * 65)

    # Stage 1: Execute adapter
    run_technical_adapter()

    # Stage 2: Load results
    adapter_data = load_adapter_output()

    candidates = adapter_data["candidate_results"]

    # Stage 3: Validate results
    validation_success, validation_errors = (
        validate_candidate_results(candidates)
    )

    # Stage 4: Calculate summary
    summary = calculate_summary(candidates)

    # Stage 5: Build candidate report
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

        "pipeline": "ZecPath Day 63 Technical Interview Pipeline",

        "adapter": "ZecPath Day 63 Technical Adapter",

        "scoring_engine": (
            "ZecPath Day 47 Technical Scoring Engine"
        ),

        "pipeline_status": (
            "SUCCESS"
            if validation_success
            else "VALIDATION_FAILED"
        ),

        "scoring_mode": adapter_data.get(
            "scoring_mode",
            "UNKNOWN"
        ),

        "is_simulated": adapter_data.get(
            "is_simulated",
            True
        ),

        "score_source": adapter_data.get(
            "score_source",
            "UNKNOWN"
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

    # Save final output
    save_pipeline_output(pipeline_output)

    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------

    print("\n" + "#" * 65)
    print("TECHNICAL PIPELINE EXECUTION SUMMARY")
    print("#" * 65)

    print(
        "Pipeline Status :",
        pipeline_output["pipeline_status"]
    )

    print(
        "Total Candidates:",
        summary["total_candidates"]
    )

    print(
        "Completed       :",
        summary["completed"]
    )

    print(
        "Pending Review  :",
        summary["pending_review"]
    )

    print(
        "Not Provided    :",
        summary["not_provided"]
    )

    print(
        "Average Score   :",
        summary["average_technical_score"]
    )

    print(
        "Execution Time  :",
        execution_time,
        "seconds"
    )

    print("#" * 65)

    if not validation_success:

        raise RuntimeError(
            "Technical pipeline validation failed. "
            "Check the validation errors in the output."
        )

    return pipeline_output


# ============================================================
# 8. EXECUTION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        run_pipeline()

    except Exception as error:

        print("\nTECHNICAL PIPELINE FAILED")
        print("Reason:", error)

        raise
