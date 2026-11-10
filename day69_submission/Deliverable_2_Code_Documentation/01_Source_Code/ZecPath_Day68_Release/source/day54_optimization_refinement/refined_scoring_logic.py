
"""
ZecPath Day 54 - Deliverable 3
Refined Scoring Logic

Purpose:
- Validate candidate assessment data.
- Calculate scores using verified assessment rounds.
- Detect missing rounds, demo data, score inconsistencies,
  high score variation, and risk flags.
- Produce explainable candidate decisions.
- Save results separately from the existing evaluator.

This module does not modify the Day 52 decision engine.
"""

import json
from pathlib import Path
from statistics import mean


BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "evaluation_dataset.json"
OUTPUT_PATH = BASE_DIR / "results" / "refined_scoring_results.json"

ROUND_WEIGHTS = {
    "ats": 0.20,
    "screening": 0.10,
    "hr_interview": 0.20,
    "technical_interview": 0.25,
    "machine_test": 0.25,
}

SELECT_THRESHOLD = 80.0
REVIEW_THRESHOLD = 60.0
MAX_SCORE_DIFFERENCE = 10.0
MAX_ROUND_SPREAD = 20.0


def load_dataset():
    """Load candidate test cases from the existing dataset."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "The evaluation dataset must contain a JSON list."
        )

    return data


def valid_score(value):
    """Return True only for numeric scores from 0 to 100."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and 0 <= value <= 100
    )


def calculate_verified_score(round_scores):
    """
    Calculate a weighted score using only completed,
    verified, non-demo assessment rounds.

    Missing or invalid rounds are reported separately.
    A partial score is diagnostic only and cannot justify
    final selection.
    """
    usable_scores = {}
    missing_rounds = []
    demo_rounds = []
    invalid_rounds = []

    for round_name in ROUND_WEIGHTS:
        round_data = round_scores.get(round_name)

        if not isinstance(round_data, dict):
            missing_rounds.append(round_name)
            continue

        if round_data.get("is_demo") is True:
            demo_rounds.append(round_name)
            continue

        if (
            round_data.get("status") != "completed"
            or round_data.get("verified") is not True
        ):
            missing_rounds.append(round_name)
            continue

        score = round_data.get("score")

        if not valid_score(score):
            invalid_rounds.append(round_name)
            continue

        usable_scores[round_name] = float(score)

    if not usable_scores:
        return {
            "calculated_score": None,
            "usable_rounds": [],
            "missing_rounds": missing_rounds,
            "demo_rounds": demo_rounds,
            "invalid_rounds": invalid_rounds,
            "round_spread": None,
        }

    total_weight = sum(
        ROUND_WEIGHTS[name] for name in usable_scores
    )

    # Normalize weights for diagnostic calculations when
    # fewer than all mandatory rounds are available.
    calculated_score = sum(
        usable_scores[name] * ROUND_WEIGHTS[name]
        for name in usable_scores
    ) / total_weight

    spread = (
        max(usable_scores.values()) - min(usable_scores.values())
        if len(usable_scores) > 1
        else 0.0
    )

    return {
        "calculated_score": round(calculated_score, 2),
        "usable_rounds": list(usable_scores.keys()),
        "missing_rounds": missing_rounds,
        "demo_rounds": demo_rounds,
        "invalid_rounds": invalid_rounds,
        "round_spread": round(spread, 2),
    }


def evaluate_candidate(candidate):
    """Apply refined scoring rules to one candidate."""
    candidate_id = candidate.get(
        "candidate_id", "unknown_candidate"
    )

    reasons = []
    review_flags = []

    eligibility = str(
        candidate.get("eligibility_status", "")
    ).strip().upper()

    risk_flags = candidate.get("risk_flags", [])

    if not isinstance(risk_flags, list):
        risk_flags = ["invalid_risk_flags_format"]

    round_scores = candidate.get("round_scores", {})

    if not isinstance(round_scores, dict):
        round_scores = {}

    score_details = calculate_verified_score(round_scores)
    calculated_score = score_details["calculated_score"]

    supplied_score = candidate.get("hiring_fit_score")

    if supplied_score is not None and not valid_score(supplied_score):
        review_flags.append("invalid_supplied_score")
        reasons.append(
            "The supplied hiring fit score is invalid."
        )
        supplied_score = None

    score_difference = None

    if (
        supplied_score is not None
        and calculated_score is not None
    ):
        score_difference = round(
            abs(float(supplied_score) - calculated_score), 2
        )

        if score_difference > MAX_SCORE_DIFFERENCE:
            review_flags.append("score_inconsistency")
            reasons.append(
                "The supplied score differs from the "
                "recalculated score beyond the allowed tolerance."
            )

    # The refined system uses the recalculated verified score.
    # A partial score is never sufficient for final selection.
    score_used = calculated_score

    if eligibility == "REJECTED":
        decision = "NOT_QUALIFIED"
        reasons.append(
            "Eligibility status is REJECTED."
        )

    elif not eligibility:
        decision = "REVIEW"
        reasons.append(
            "Eligibility status is missing."
        )

    elif eligibility not in {"ELIGIBLE", "REVIEW"}:
        decision = "REVIEW"
        reasons.append(
            "Eligibility status is not recognized."
        )

    elif eligibility == "REVIEW":
        decision = "REVIEW"
        reasons.append(
            "Eligibility rules require further review."
        )

    elif risk_flags:
        decision = "REVIEW"
        reasons.append(
            "Risk flags require human review."
        )

    elif score_details["invalid_rounds"]:
        decision = "REVIEW"
        reasons.append(
            "One or more assessment rounds have invalid scores."
        )

    elif score_details["missing_rounds"]:
        decision = "REVIEW"
        reasons.append(
            "Mandatory assessment rounds are missing, "
            "incomplete, or unverified."
        )

    elif score_details["demo_rounds"]:
        decision = "REVIEW"
        reasons.append(
            "Demo assessment data cannot support final selection."
        )

    elif calculated_score is None:
        decision = "REVIEW"
        reasons.append(
            "No usable verified assessment scores are available."
        )

    elif "score_inconsistency" in review_flags:
        decision = "REVIEW"
        reasons.append(
            "The overall score requires consistency review."
        )

    elif (
        score_details["round_spread"] is not None
        and score_details["round_spread"] > MAX_ROUND_SPREAD
    ):
        decision = "REVIEW"
        reasons.append(
            "Assessment scores vary beyond the configured limit."
        )

    elif calculated_score >= SELECT_THRESHOLD:
        decision = "SELECT"
        reasons.append(
            "Verified weighted score meets the selection threshold."
        )

    elif calculated_score >= REVIEW_THRESHOLD:
        decision = "REVIEW"
        reasons.append(
            "Verified weighted score falls within the review range."
        )

    else:
        decision = "NOT_QUALIFIED"
        reasons.append(
            "Verified weighted score is below the review threshold."
        )

    if not score_details["missing_rounds"] and not score_details["demo_rounds"]:
        if len(score_details["usable_rounds"]) == len(ROUND_WEIGHTS):
            reasons.append(
                "All mandatory assessment rounds are available "
                "as completed, verified, non-demo results."
            )

    return {
        "candidate_id": candidate_id,
        "expected_outcome": candidate.get("expected_outcome"),
        "eligibility_status": eligibility or None,
        "supplied_hiring_fit_score": supplied_score,
        "recalculated_verified_score": calculated_score,
        "score_used_for_decision": score_used,
        "score_difference": score_difference,
        "usable_rounds": score_details["usable_rounds"],
        "missing_rounds": score_details["missing_rounds"],
        "demo_rounds": score_details["demo_rounds"],
        "invalid_rounds": score_details["invalid_rounds"],
        "round_spread": score_details["round_spread"],
        "review_flags": review_flags,
        "decision": decision,
        "reasons": reasons,
        "human_review_required": decision == "REVIEW",
    }


def main():
    try:
        candidates = load_dataset()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: Could not load dataset: {error}")
        return

    results = []
    errors = []

    for index, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, dict):
            errors.append({
                "case_number": index,
                "error": "Candidate record must be a JSON object.",
            })
            continue

        try:
            results.append(evaluate_candidate(candidate))
        except Exception as error:
            errors.append({
                "candidate_id": candidate.get(
                    "candidate_id", f"case_{index}"
                ),
                "error": str(error),
            })

    output = {
        "project": "ZecPath",
        "deliverable": "Day 54 - Deliverable 3: Refined Scoring Logic",
        "dataset_type": "Synthetic evaluation cases",
        "dataset_count": len(candidates),
        "evaluated_count": len(results),
        "error_count": len(errors),
        "configuration": {
            "round_weights": ROUND_WEIGHTS,
            "select_threshold": SELECT_THRESHOLD,
            "review_threshold": REVIEW_THRESHOLD,
            "maximum_score_difference": MAX_SCORE_DIFFERENCE,
            "maximum_round_spread": MAX_ROUND_SPREAD,
        },
        "decision_summary": {
            "select": sum(
                item["decision"] == "SELECT" for item in results
            ),
            "review": sum(
                item["decision"] == "REVIEW" for item in results
            ),
            "not_qualified": sum(
                item["decision"] == "NOT_QUALIFIED"
                for item in results
            ),
        },
        "results": results,
        "errors": errors,
        "limitations": [
            "The evaluation dataset contains synthetic records.",
            "Expected labels are not independently validated hiring outcomes.",
            "A recalculated score is not proof of candidate suitability.",
            "Human review is required for uncertain cases.",
            "This module does not modify the Day 52 decision engine.",
        ],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=4)

    print("=" * 55)
    print("ZecPath Day 54 - Refined Scoring Logic")
    print("=" * 55)
    print(f"Dataset cases:      {len(candidates)}")
    print(f"Evaluated cases:    {len(results)}")
    print(f"Errors:             {len(errors)}")
    print(f"Selected:           {output['decision_summary']['select']}")
    print(f"Review:             {output['decision_summary']['review']}")
    print(
        "Not qualified:     "
        f"{output['decision_summary']['not_qualified']}"
    )
    print(f"Report saved to:    {OUTPUT_PATH}")

    if errors:
        print("\nErrors:")
        for item in errors:
            print(item)


if __name__ == "__main__":
    main()
