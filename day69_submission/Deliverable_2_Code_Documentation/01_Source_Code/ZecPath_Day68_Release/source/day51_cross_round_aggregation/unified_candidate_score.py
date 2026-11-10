
import json
from pathlib import Path
from datetime import datetime, timezone


# ============================================================
# ZecPath Day 51 - Deliverable 3
# Unified Candidate Score Object
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

INPUT_FILE = RESULTS_DIR / "cross_round_aggregation.json"
OUTPUT_FILE = RESULTS_DIR / "unified_candidate_score.json"

EXPECTED_ROUNDS = (
    "ats",
    "screening",
    "hr_interview",
    "technical_interview",
    "machine_test",
)


# ============================================================
# Utilities
# ============================================================

def load_json(file_path):
    """Load a JSON object from a file."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}. "
            "Run cross_round_aggregation_engine.py first."
        )

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Input JSON must contain an object.")

    return data


def validate_score(score, round_name):
    """Validate and normalize a score to a 0-100 scale."""

    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise ValueError(
            f"Invalid numeric score for round: {round_name}"
        )

    if not 0 <= score <= 100:
        raise ValueError(
            f"Score for {round_name} must be between 0 and 100."
        )

    return round(float(score), 2)


def validate_weights(weights):
    """Validate that all five round weights total 100%."""

    if set(weights.keys()) != set(EXPECTED_ROUNDS):
        raise ValueError(
            "Input must contain weights for all five rounds."
        )

    for name, weight in weights.items():
        if (
            isinstance(weight, bool)
            or not isinstance(weight, (int, float))
            or weight < 0
        ):
            raise ValueError(f"Invalid weight for {name}.")

    if abs(sum(weights.values()) - 1.0) > 1e-6:
        raise ValueError("Round weights must total 100%.")


# ============================================================
# Build unified candidate object
# ============================================================

def build_unified_candidate_score(aggregation):
    """Create one standardized object for the candidate."""

    candidate_id = aggregation.get("candidate_id", "")
    job_id = aggregation.get("job_id", "")

    if not candidate_id or not job_id:
        raise ValueError("Candidate ID and job ID are required.")

    weights = aggregation.get("round_weights", {})
    validate_weights(weights)

    breakdown = aggregation.get("round_breakdown", {})

    missing_rounds = [
        name for name in EXPECTED_ROUNDS
        if name not in breakdown
    ]

    if missing_rounds:
        raise ValueError(
            "Aggregation is missing rounds: "
            + ", ".join(missing_rounds)
        )

    round_scores = {}
    total_score = 0.0
    demo_rounds = []

    for round_name in EXPECTED_ROUNDS:
        source = breakdown[round_name]

        score = validate_score(
            source.get("normalized_score"),
            round_name,
        )

        weight = float(weights[round_name])
        contribution = round(score * weight, 4)

        is_demo = bool(source.get("is_demo_data", False))

        if is_demo:
            demo_rounds.append(round_name)

        round_scores[round_name] = {
            "score": score,
            "normalized_score": score,
            "weight": weight,
            "weight_percentage": round(weight * 100, 2),
            "weighted_contribution": contribution,
            "source_status": source.get(
                "source_status", "UNKNOWN"
            ),
            "data_type": source.get(
                "data_type", "UNKNOWN"
            ),
            "is_demo_data": is_demo,
            "explanation": (
                f"{score:.2f} x {weight:.2f} = "
                f"{contribution:.4f}"
            ),
        }

        total_score += contribution

    calculated_score = round(total_score, 2)

    # Verify consistency with the aggregation engine's result.
    engine_score = validate_score(
        aggregation.get("hiring_fit_score"),
        "hiring_fit_score",
    )

    if abs(calculated_score - engine_score) > 0.02:
        raise ValueError(
            "Unified score does not match the aggregation engine."
        )

    report_type = aggregation.get("report_type", "DEMO_ONLY")

    # Demo data must never be presented as a verified hiring result.
    if demo_rounds or report_type == "DEMO_ONLY":
        report_type = "DEMO_ONLY"
        verified_status = "NOT_EVALUATED"
    else:
        verified_status = aggregation.get(
            "verified_hiring_fit_status",
            "REQUIRES_INDEPENDENT_VALIDATION",
        )

    return {
        "schema_name": "ZecPath Unified Candidate Score Object",
        "schema_version": "1.0",
        "object_status": "SUCCESS",
        "report_type": report_type,

        "candidate": {
            "candidate_id": candidate_id,
            "job_id": job_id,
        },

        "overall_evaluation": {
            "hiring_fit_score": calculated_score,
            "score_scale": "0-100",
            "aggregation_status": aggregation.get(
                "aggregation_status", "SUCCESS"
            ),
            "verified_hiring_fit_status": verified_status,
            "demo_rounds": demo_rounds,
        },

        "evaluation_rounds": round_scores,

        "weight_summary": {
            "weights": weights,
            "total_weight_percentage": round(
                sum(weights.values()) * 100, 2
            ),
        },

        "scoring_transparency": {
            "normalization": (
                "Scores validated on a common 0-100 scale."
            ),
            "aggregation_method": "Weighted sum",
            "formula": (
                "Hiring Fit Score = sum(round score x round weight)"
            ),
            "weighted_contributions_sum": round(
                sum(
                    item["weighted_contribution"]
                    for item in round_scores.values()
                ),
                4,
            ),
            "demo_data_used": bool(demo_rounds),
            "verified_hiring_decision_made": False,
        },

        "data_quality": {
            "all_five_rounds_present": True,
            "all_round_scores_numeric": True,
            "all_scores_within_range": True,
            "weights_valid": True,
            "demo_rounds": demo_rounds,
            "data_quality_status": (
                "DEMO_DATA_PRESENT"
                if demo_rounds
                else "SOURCE_DATA_REQUIRES_VALIDATION"
            ),
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

    aggregation = load_json(INPUT_FILE)
    unified_object = build_unified_candidate_score(aggregation)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(unified_object, file, indent=4)

    print("=" * 65)
    print("ZecPath Day 51 - Unified Candidate Score Object")
    print("=" * 65)

    print(
        "Object status: "
        f"{unified_object['object_status']}"
    )
    print(
        "Report type: "
        f"{unified_object['report_type']}"
    )
    print(
        "Candidate ID: "
        f"{unified_object['candidate']['candidate_id']}"
    )
    print(
        "Job ID: "
        f"{unified_object['candidate']['job_id']}"
    )

    print("\nEvaluation scores:")

    for name, result in unified_object[
        "evaluation_rounds"
    ].items():
        print(
            f"{name:24s} "
            f"Score: {result['score']:7.2f}  "
            f"Contribution: "
            f"{result['weighted_contribution']:.4f}"
        )

    print("\n" + "-" * 65)
    print(
        "Total weight: "
        f"{unified_object['weight_summary']['total_weight_percentage']:.2f}%"
    )
    print(
        "Unified Hiring Fit Score: "
        f"{unified_object['overall_evaluation']['hiring_fit_score']:.2f}/100"
    )
    print(
        "Verified hiring status: "
        f"{unified_object['overall_evaluation']['verified_hiring_fit_status']}"
    )
    print(
        "Data quality: "
        f"{unified_object['data_quality']['data_quality_status']}"
    )
    print(f"\nOutput saved to: {OUTPUT_FILE}")
    print("=" * 65)


if __name__ == "__main__":
    main()
