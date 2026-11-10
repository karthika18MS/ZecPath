
import json
from pathlib import Path
from datetime import datetime, timezone


# ============================================================
# ZecPath Day 51 - Complete Demo Hiring Fit Calculator
# Always generates a complete report with numeric scores.
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
RESULTS_DIR = BASE_DIR / "results"
OUTPUT_FILE = RESULTS_DIR / "hiring_fit_score.json"

CANDIDATE_ID = "candidate_006"
JOB_ID = "JOB_BACKEND_001"

ROUND_WEIGHTS = {
    "ats": 0.15,
    "screening": 0.10,
    "hr_interview": 0.20,
    "technical_interview": 0.25,
    "machine_test": 0.30,
}

# Demo fallback scores are used when source data cannot be read.
# These values are demonstration inputs, not verified assessments.
DEMO_SCORES = {
    "ats": 90.10,
    "screening": 95.00,
    "hr_interview": 91.47,
    "technical_interview": 81.25,
    "machine_test": 94.00,
}

SOURCE_FILES = {
    "ats": Path(
        "day18_optimization/results/candidate_006/"
        "day18_optimized_ats_score.json"
    ),
    "screening": Path(
        "day32_screening_finalization/results/"
        "final_screening_pipeline_result.json"
    ),
    "hr_interview": Path(
        "day37_hr_interview_scoring/results/hr_interview_score.json"
    ),
    "technical_interview": Path(
        "day47_technical_skill_scoring/results/"
        "candidate_technical_evaluation.json"
    ),
    "machine_test": Path(
        "day50_machine_test_scoring/results/machine_test_score.json"
    ),
}

SCORE_KEYS = (
    "final_ats_score",
    "final_screening_score",
    "screening_score",
    "final_hr_interview_score",
    "final_hr_score",
    "overall_technical_score",
    "technical_score",
    "machine_test_score",
    "final_score",
    "overall_score",
    "score",
)

NESTED_KEYS = (
    "scores",
    "screening_summary",
    "evaluation_summary",
    "score_summary",
    "final_evaluation",
    "interview_summary",
    "results",
)


def load_json(path):
    """Return a JSON dictionary, or None if unavailable."""

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict):
            return data

    except (OSError, json.JSONDecodeError):
        pass

    return None


def find_score(data):
    """Find a valid score in a source JSON dictionary."""

    if not isinstance(data, dict):
        return None

    for key in SCORE_KEYS:
        value = data.get(key)

        if (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and 0 <= value <= 100
        ):
            return round(float(value), 2)

    for key in NESTED_KEYS:
        nested = data.get(key)

        if isinstance(nested, dict):
            score = find_score(nested)

            if score is not None:
                return score

    return None


def contains_test_label(data):
    """Detect source data labelled as test or demonstration data."""

    if not isinstance(data, dict):
        return False

    fields = (
        "data_type",
        "data_source",
        "source_type",
        "evaluation_type",
        "environment",
    )

    markers = ("test", "demo", "sample", "mock", "synthetic")

    for key in fields:
        value = data.get(key)

        if isinstance(value, str):
            if any(marker in value.lower() for marker in markers):
                return True

    for key in ("metadata", "evaluation_metadata"):
        nested = data.get(key)

        if isinstance(nested, dict) and contains_test_label(nested):
            return True

    return False


def find_candidate_id(data):
    """Find the candidate ID when provided by a source."""

    if not isinstance(data, dict):
        return ""

    for key in ("candidate_id", "candidateId", "applicant_id"):
        value = data.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    for key in ("candidate_information", "candidate", "metadata"):
        nested = data.get(key)

        if isinstance(nested, dict):
            candidate_id = find_candidate_id(nested)

            if candidate_id:
                return candidate_id

    return ""


def evaluate_round(round_name, relative_path):
    """Use a valid source score or a configured demo fallback."""

    path = PROJECT_DIR / relative_path
    data = load_json(path)
    source_score = find_score(data)
    source_candidate = find_candidate_id(data)

    candidate_matches = (
        not source_candidate
        or source_candidate.lower() == CANDIDATE_ID.lower()
    )

    use_source = (
        data is not None
        and source_score is not None
        and candidate_matches
    )

    if use_source:
        score = source_score

        if contains_test_label(data):
            data_status = "DEMO_SOURCE"
            explanation = (
                "Numeric score loaded from a source labelled "
                "as test or demonstration data."
            )
        else:
            data_status = "SOURCE_SCORE"
            explanation = "Numeric score loaded from the source file."

    else:
        score = DEMO_SCORES[round_name]
        data_status = "DEMO_FALLBACK"

        if source_candidate and not candidate_matches:
            explanation = (
                "Source candidate ID did not match; "
                "configured demo score used."
            )
        elif data is None:
            explanation = (
                "Source unavailable or unreadable; "
                "configured demo score used."
            )
        else:
            explanation = (
                "Supported source score unavailable; "
                "configured demo score used."
            )

    weight = ROUND_WEIGHTS[round_name]

    return {
        "round": round_name,
        "source_file": str(relative_path),
        "score": round(score, 2),
        "weight": weight,
        "weighted_contribution": round(score * weight, 4),
        "status": data_status,
        "data_type": (
            "DEMO_ONLY"
            if data_status != "SOURCE_SCORE"
            else "SOURCE_REPORTED"
        ),
        "explanation": explanation,
    }


def main():
    """Generate the complete demo hiring-fit report."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    if abs(sum(ROUND_WEIGHTS.values()) - 1.0) > 1e-6:
        raise ValueError("Round weights must total 100%.")

    print("=" * 65)
    print("ZecPath Day 51 - Hiring Fit Calculator")
    print("Complete Demo Cross-Round Aggregation")
    print("=" * 65)

    print(f"Candidate ID: {CANDIDATE_ID}")
    print(f"Job ID: {JOB_ID}")

    print("\nRound weights:")

    for name, weight in ROUND_WEIGHTS.items():
        print(f"  {name:24s}: {weight * 100:5.1f}%")

    round_results = []

    print("\nEvaluating rounds...\n")

    for name, relative_path in SOURCE_FILES.items():
        result = evaluate_round(name, relative_path)
        round_results.append(result)

        print(
            f"{name:24s} "
            f"Score: {result['score']:7.2f}  "
            f"Status: {result['status']}"
        )
        print(
            f"  Weighted contribution: "
            f"{result['weighted_contribution']:.4f}"
        )

    # All five scores are numeric, so the demo report is complete.
    demo_score = round(
        sum(
            item["score"] * item["weight"]
            for item in round_results
        ),
        2,
    )

    output = {
        "engine": "ZecPath Day 51 Hiring Fit Calculator",
        "report_type": "DEMO_ONLY",
        "evaluation_status": "SUCCESS_DEMO",
        "candidate_id": CANDIDATE_ID,
        "job_id": JOB_ID,
        "hiring_fit_score": demo_score,
        "verified_hiring_fit_score": "NOT_EVALUATED",
        "round_weights": ROUND_WEIGHTS,
        "round_results": round_results,
        "score_interpretation": (
            "Demonstration score using available source scores "
            "and configured demo fallback scores. "
            "Not a verified hiring decision."
        ),
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=4)

    print("\n" + "-" * 65)
    print("Report Type: DEMO_ONLY")
    print("Evaluation Status: SUCCESS_DEMO")
    print(f"Final Demo Hiring Fit Score: {demo_score:.2f}/100")
    print("Verified Hiring Fit: NOT_EVALUATED")
    print("All five rounds have numeric scores.")
    print(f"\nReport saved to: {OUTPUT_FILE}")
    print("=" * 65)


if __name__ == "__main__":
    main()
