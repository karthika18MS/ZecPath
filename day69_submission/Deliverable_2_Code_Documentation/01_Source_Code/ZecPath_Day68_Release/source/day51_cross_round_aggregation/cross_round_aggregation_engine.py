
import json
from pathlib import Path
from datetime import datetime, timezone


# ============================================================
# ZecPath Day 51 - Deliverable 2
# Cross-Round Aggregation Engine
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

INPUT_FILE = RESULTS_DIR / "hiring_fit_score.json"
OUTPUT_FILE = RESULTS_DIR / "cross_round_aggregation.json"

EXPECTED_ROUNDS = (
    "ats",
    "screening",
    "hr_interview",
    "technical_interview",
    "machine_test",
)

DEFAULT_WEIGHTS = {
    "ats": 0.15,
    "screening": 0.10,
    "hr_interview": 0.20,
    "technical_interview": 0.25,
    "machine_test": 0.30,
}


# ============================================================
# Validation
# ============================================================

def validate_weights(weights):
    """Ensure all expected rounds have valid weights."""

    if set(weights) != set(EXPECTED_ROUNDS):
        raise ValueError(
            "Weights must be defined for all five evaluation rounds."
        )

    for round_name, weight in weights.items():
        if (
            isinstance(weight, bool)
            or not isinstance(weight, (int, float))
            or weight < 0
        ):
            raise ValueError(
                f"Invalid weight for {round_name}: {weight}"
            )

    if abs(sum(weights.values()) - 1.0) > 1e-6:
        raise ValueError("Round weights must total 100%.")


def normalize_score(score):
    """
    Validate and normalize a score to the common 0-100 scale.

    The input score is already expected to be on a 0-100 scale.
    This function validates that scale and returns a two-decimal
    normalized score.
    """

    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise ValueError("Every round must have a numeric score.")

    if not 0 <= score <= 100:
        raise ValueError("Every score must be between 0 and 100.")

    return round(float(score), 2)


# ============================================================
# Input loading
# ============================================================

def load_input():
    """Load the completed Deliverable 1 report."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input report not found: {INPUT_FILE}\n"
            "Run hiring_fit_calculator.py first."
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        report = json.load(file)

    if not isinstance(report, dict):
        raise ValueError("Hiring fit report must be a JSON object.")

    if report.get("candidate_id") == "":
        raise ValueError("Candidate ID cannot be empty.")

    if report.get("job_id") == "":
        raise ValueError("Job ID cannot be empty.")

    return report


# ============================================================
# Cross-round aggregation
# ============================================================

def aggregate_scores(report):
    """
    Combine all evaluation rounds into a unified score object.

    Demo scores remain explicitly labelled DEMO_ONLY.
    This engine does not convert demo scores into verified scores.
    """

    weights = report.get("round_weights", DEFAULT_WEIGHTS)
    validate_weights(weights)

    source_results = report.get("round_results", [])

    results_by_name = {
        item.get("round"): item
        for item in source_results
        if isinstance(item, dict)
    }

    missing_rounds = [
        name for name in EXPECTED_ROUNDS
        if name not in results_by_name
    ]

    if missing_rounds:
        raise ValueError(
            "Input report does not contain all five rounds: "
            + ", ".join(missing_rounds)
        )

    round_breakdown = {}
    total_score = 0.0
    demo_rounds = []

    for round_name in EXPECTED_ROUNDS:
        source = results_by_name[round_name]

        score = normalize_score(source.get("score"))
        weight = float(weights[round_name])
        contribution = round(score * weight, 4)

        status = source.get("status", "UNKNOWN")
        data_type = source.get("data_type", "UNKNOWN")

        is_demo = (
            status in ("DEMO_SOURCE", "DEMO_FALLBACK", "TEST_DATA")
            or data_type == "DEMO_ONLY"
        )

        if is_demo:
            demo_rounds.append(round_name)

        total_score += contribution

        round_breakdown[round_name] = {
            "normalized_score": score,
            "weight": weight,
            "weight_percentage": round(weight * 100, 2),
            "weighted_contribution": contribution,
            "source_status": status,
            "data_type": data_type,
            "is_demo_data": is_demo,
            "explanation": (
                f"{score:.2f} x {weight:.2f} = "
                f"{contribution:.4f}"
            ),
        }

    final_score = round(total_score, 2)

    report_type = report.get("report_type", "DEMO_ONLY")

    if demo_rounds or report_type == "DEMO_ONLY":
        report_type = "DEMO_ONLY"
        verified_status = "NOT_EVALUATED"
    else:
        verified_status = "REQUIRES_INDEPENDENT_VALIDATION"

    return {
        "engine": "ZecPath Cross-Round Aggregation Engine",
        "engine_version": "1.0",
        "report_type": report_type,
        "aggregation_status": "SUCCESS",
        "candidate_id": report.get("candidate_id", "candidate_006"),
        "job_id": report.get("job_id", "JOB_BACKEND_001"),
        "normalized_score_scale": "0-100",
        "round_weights": weights,
        "round_breakdown": round_breakdown,
        "total_weight_percentage": round(
            sum(weights.values()) * 100, 2
        ),
        "hiring_fit_score": final_score,
        "verified_hiring_fit_status": verified_status,
        "demo_rounds": demo_rounds,
        "transparency": {
            "normalization_method": (
                "Validate scores on a common 0-100 scale "
                "and round to two decimal places."
            ),
            "aggregation_method": (
                "Weighted sum of normalized round scores."
            ),
            "formula": (
                "Hiring Fit Score = sum(normalized score "
                "x round weight)"
            ),
            "demo_data_used": bool(demo_rounds),
            "verified_decision_made": False,
        },
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
    }


# ============================================================
# Main
# ============================================================

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    report = load_input()
    result = aggregate_scores(report)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=4)

    print("=" * 65)
    print("ZecPath Day 51 - Cross-Round Aggregation Engine")
    print("=" * 65)

    print(f"Candidate ID: {result['candidate_id']}")
    print(f"Job ID: {result['job_id']}")
    print(f"Aggregation Status: {result['aggregation_status']}")
    print(f"Report Type: {result['report_type']}")

    print("\nRound breakdown:")

    for name, item in result["round_breakdown"].items():
        print(
            f"{name:24s} "
            f"Score: {item['normalized_score']:7.2f}  "
            f"Weight: {item['weight_percentage']:5.1f}%  "
            f"Contribution: {item['weighted_contribution']:.4f}"
        )

    print("\n" + "-" * 65)
    print(f"Total weight: {result['total_weight_percentage']:.2f}%")
    print(f"Hiring Fit Score: {result['hiring_fit_score']:.2f}/100")
    print(
        "Verified hiring status: "
        f"{result['verified_hiring_fit_status']}"
    )

    if result["demo_rounds"]:
        print(
            "Demo rounds: "
            + ", ".join(result["demo_rounds"])
        )
    else:
        print("Demo rounds: None")

    print(f"\nOutput saved to: {OUTPUT_FILE}")
    print("=" * 65)


if __name__ == "__main__":
    main()
