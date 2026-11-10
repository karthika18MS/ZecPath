
"""
ZecPath Day 54 - Deliverable 1: Improved AI Accuracy

Standalone, rule-based evaluator for a controlled evaluation dataset.
The included evaluation_dataset.json uses illustrative synthetic cases.
Do not interpret these metrics as real-world hiring accuracy.
"""

import json
import time
from pathlib import Path
from statistics import mean


# ============================================================
# 1. FILE PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATASET_FILE = BASE_DIR / "evaluation_dataset.json"
RESULTS_DIR = BASE_DIR / "results"
REPORT_FILE = RESULTS_DIR / "accuracy_evaluation.json"


# ============================================================
# 2. CONFIGURATION
# ============================================================

# Initial settings. Validate these against reviewed historical data
# before using this system in a real hiring workflow.
SELECT_THRESHOLD = 80.0
REVIEW_THRESHOLD = 60.0
MAX_SCORE_DIFFERENCE = 10.0
MAX_ROUND_SPREAD = 20.0

ROUND_WEIGHTS = {
    "ats": 0.20,
    "screening": 0.10,
    "hr_interview": 0.20,
    "technical_interview": 0.25,
    "machine_test": 0.25,
}

MANDATORY_ROUNDS = list(ROUND_WEIGHTS.keys())


# ============================================================
# 3. LOAD DATASET
# ============================================================

def load_dataset():
    """Load and validate evaluation_dataset.json."""

    if not DATASET_FILE.exists():
        raise FileNotFoundError(
            f"Dataset file not found: {DATASET_FILE}"
        )

    with DATASET_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "evaluation_dataset.json must contain a JSON list."
        )

    return data


def validate_score(value, field_name):
    """Validate that a score is numeric and between 0 and 100."""

    if isinstance(value, bool):
        raise ValueError(
            f"{field_name} must be numeric, not boolean."
        )

    try:
        score = float(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"{field_name} must be numeric."
        )

    if not 0.0 <= score <= 100.0:
        raise ValueError(
            f"{field_name} must be between 0 and 100."
        )

    return score


# ============================================================
# 4. ASSESSMENT ROUND EVALUATION
# ============================================================

def evaluate_rounds(case):
    """
    Calculate the weighted score from completed, verified,
    non-demo assessment rounds.

    Missing and demo rounds are recorded separately.
    """

    round_data = case.get("round_scores", {})

    if not isinstance(round_data, dict):
        raise ValueError(
            "round_scores must be a JSON object."
        )

    valid_scores = {}
    missing_rounds = []
    demo_rounds = []

    for name, weight in ROUND_WEIGHTS.items():

        item = round_data.get(name)

        if not isinstance(item, dict):
            missing_rounds.append(name)
            continue

        if item.get("status") != "completed":
            missing_rounds.append(name)
            continue

        if item.get("is_demo", False) is True:
            demo_rounds.append(name)
            continue

        if item.get("verified") is not True:
            missing_rounds.append(name)
            continue

        if item.get("score") is None:
            missing_rounds.append(name)
            continue

        score = validate_score(
            item["score"],
            f"{name}.score"
        )

        valid_scores[name] = {
            "score": score,
            "weight": weight,
        }

    # Return safely when no usable rounds exist.
    if not valid_scores:
        return {
            "weighted_score": None,
            "valid_rounds": [],
            "missing_rounds": sorted(set(missing_rounds)),
            "demo_rounds": demo_rounds,
            "round_spread": None,
            "verified_round_count": 0,
        }

    # Normalize weights across available valid rounds.
    # Missing mandatory rounds still prevent selection.
    total_weight = sum(
        item["weight"]
        for item in valid_scores.values()
    )

    weighted_score = sum(
        item["score"] * item["weight"]
        for item in valid_scores.values()
    ) / total_weight

    scores = [
        item["score"]
        for item in valid_scores.values()
    ]

    round_spread = max(scores) - min(scores)

    return {
        "weighted_score": round(weighted_score, 2),
        "valid_rounds": list(valid_scores.keys()),
        "missing_rounds": sorted(set(missing_rounds)),
        "demo_rounds": demo_rounds,
        "round_spread": round(round_spread, 2),
        "verified_round_count": len(valid_scores),
    }


# ============================================================
# 5. ELIGIBILITY AND RISK CHECKS
# ============================================================

def detect_intent(case):
    """Check eligibility status and manual-review risk flags."""

    status = str(
        case.get("eligibility_status", "UNKNOWN")
    ).strip().upper()

    risk_flags = case.get("risk_flags", [])

    if not isinstance(risk_flags, list):
        return (
            "REVIEW",
            "risk_flags must be a list."
        )

    if status == "REJECTED":
        return (
            "NOT_QUALIFIED",
            "Eligibility status is REJECTED."
        )

    if status != "ELIGIBLE":
        return (
            "REVIEW",
            "Eligibility is missing, uncertain, or unrecognized."
        )

    if risk_flags:
        return (
            "REVIEW",
            "Risk flags require human review."
        )

    return (
        "SCORE_EVALUATION",
        "Eligibility checks passed."
    )


# ============================================================
# 6. SCORE CONSISTENCY CHECK
# ============================================================

def check_score_consistency(
    supplied_score,
    calculated_score
):
    """
    Compare the supplied hiring-fit score with the score
    recalculated from verified, non-demo assessment rounds.

    A difference greater than MAX_SCORE_DIFFERENCE triggers review.
    """

    if (
        supplied_score is None
        or calculated_score is None
    ):
        return {
            "checked": False,
            "score_difference": None,
            "review_required": False,
            "message": (
                "Consistency could not be checked because "
                "a score is unavailable."
            ),
        }

    difference = round(
        abs(supplied_score - calculated_score),
        2
    )

    mismatch = difference > MAX_SCORE_DIFFERENCE

    if mismatch:
        message = (
            "Supplied score differs from the verified-round "
            f"weighted score by more than "
            f"{MAX_SCORE_DIFFERENCE} points."
        )
    else:
        message = (
            "Supplied and calculated scores are consistent."
        )

    return {
        "checked": True,
        "score_difference": difference,
        "review_required": mismatch,
        "message": message,
    }


# ============================================================
# 7. EVALUATE ONE CANDIDATE
# ============================================================

def evaluate_case(case):
    """Evaluate one candidate and return an explainable result."""

    started = time.perf_counter()

    candidate_id = str(
        case.get("candidate_id", "UNKNOWN")
    )

    round_result = evaluate_rounds(case)

    intent, intent_reason = detect_intent(case)

    supplied_value = case.get("hiring_fit_score")

    if supplied_value is not None:
        supplied_score = validate_score(
            supplied_value,
            "hiring_fit_score"
        )
    else:
        supplied_score = None

    calculated_score = round_result["weighted_score"]

    consistency = check_score_consistency(
        supplied_score,
        calculated_score
    )

    # Prefer the supplied score when available.
    # Otherwise, use the recalculated score.
    score_used = (
        supplied_score
        if supplied_score is not None
        else calculated_score
    )

    reasons = [intent_reason]

    # Decision checks are applied in a fixed order.
    if intent == "NOT_QUALIFIED":

        decision = "NOT_QUALIFIED"

    elif intent == "REVIEW":

        decision = "REVIEW"

    elif score_used is None:

        decision = "REVIEW"
        reasons.append(
            "No usable overall score is available."
        )

    elif consistency["review_required"]:

        decision = "REVIEW"
        reasons.append(consistency["message"])

    elif round_result["missing_rounds"]:

        decision = "REVIEW"
        reasons.append(
            "Mandatory rounds are missing, incomplete, "
            "or unverified."
        )

    elif round_result["demo_rounds"]:

        decision = "REVIEW"
        reasons.append(
            "Demo round data cannot support selection."
        )

    elif (
        round_result["verified_round_count"]
        < len(MANDATORY_ROUNDS)
    ):

        decision = "REVIEW"
        reasons.append(
            "Not all mandatory rounds are verified."
        )

    elif (
        round_result["round_spread"] is not None
        and round_result["round_spread"] > MAX_ROUND_SPREAD
    ):

        decision = "REVIEW"
        reasons.append(
            "Assessment scores vary beyond the configured limit."
        )

    elif score_used >= SELECT_THRESHOLD:

        decision = "SELECT"
        reasons.append(
            "Score meets the configured selection threshold."
        )

    elif score_used >= REVIEW_THRESHOLD:

        decision = "REVIEW"
        reasons.append(
            "Score falls within the configured review range."
        )

    else:

        decision = "NOT_QUALIFIED"
        reasons.append(
            "Score is below the configured review threshold."
        )

    elapsed_ms = (
        time.perf_counter() - started
    ) * 1000

    return {
        "candidate_id": candidate_id,

        "expected_outcome": str(
            case.get("expected_outcome", "unlabelled")
        ).strip().lower(),

        "supplied_hiring_fit_score": supplied_score,
        "round_weighted_score": calculated_score,
        "score_used": score_used,

        "score_consistency": consistency,

        "decision": decision,
        "intent": intent,
        "intent_reason": intent_reason,

        "valid_rounds": round_result["valid_rounds"],
        "missing_rounds": round_result["missing_rounds"],
        "demo_rounds": round_result["demo_rounds"],

        "verified_round_count": (
            round_result["verified_round_count"]
        ),

        "round_spread": round_result["round_spread"],

        "reasons": reasons,

        "processing_time_ms": round(elapsed_ms, 4),
    }


# ============================================================
# 8. ACCURACY AND ERROR METRICS
# ============================================================

def calculate_metrics(results):
    """
    Calculate binary classification metrics.

    REVIEW cases are reported separately and are not treated
    automatically as qualified or not qualified.
    """

    tp = 0
    tn = 0
    fp = 0
    fn = 0

    review_count = 0
    excluded_count = 0

    for item in results:

        expected = item["expected_outcome"]
        predicted = item["decision"]

        if expected not in {
            "qualified",
            "not_qualified"
        }:
            excluded_count += 1
            continue

        if predicted == "REVIEW":
            review_count += 1
            continue

        predicted_positive = predicted == "SELECT"
        expected_positive = expected == "qualified"

        if predicted_positive and expected_positive:
            tp += 1

        elif (
            not predicted_positive
            and not expected_positive
        ):
            tn += 1

        elif predicted_positive and not expected_positive:
            fp += 1

        else:
            fn += 1

    binary_count = tp + tn + fp + fn

    def percentage(numerator, denominator):
        if denominator == 0:
            return None

        return round(
            numerator / denominator * 100,
            2
        )

    return {
        "true_positives": tp,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,

        "review_count": review_count,
        "excluded_count": excluded_count,
        "binary_decision_count": binary_count,

        "accuracy_percent": percentage(
            tp + tn,
            binary_count
        ),

        "precision_percent": percentage(
            tp,
            tp + fp
        ),

        "recall_percent": percentage(
            tp,
            tp + fn
        ),

        "false_positive_rate_percent": percentage(
            fp,
            fp + tn
        ),

        "false_negative_rate_percent": percentage(
            fn,
            fn + tp
        ),

        "review_rate_percent": percentage(
            review_count,
            len(results)
        ),
    }


# ============================================================
# 9. MAIN EVALUATION PIPELINE
# ============================================================

def main():

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    try:
        dataset = load_dataset()

    except (
        OSError,
        ValueError,
        json.JSONDecodeError
    ) as exc:

        print(
            f"ERROR: Could not load evaluation dataset: {exc}"
        )
        return

    results = []
    errors = []

    pipeline_started = time.perf_counter()

    for index, case in enumerate(dataset, start=1):

        if not isinstance(case, dict):

            errors.append({
                "case_index": index,
                "candidate_id": "UNKNOWN",
                "error": (
                    "Dataset entry must be a JSON object."
                ),
            })
            continue

        try:

            result = evaluate_case(case)
            results.append(result)

        except Exception as exc:

            errors.append({
                "case_index": index,
                "candidate_id": case.get(
                    "candidate_id",
                    "UNKNOWN"
                ),
                "error": str(exc),
            })

    total_ms = (
        time.perf_counter() - pipeline_started
    ) * 1000

    metrics = calculate_metrics(results)

    case_times = [
        item["processing_time_ms"]
        for item in results
    ]

    report = {
        "project": "ZecPath",

        "deliverable": (
            "Day 54 - Deliverable 1: Improved AI Accuracy"
        ),

        "report_version": "1.3",

        "dataset_type": "Synthetic evaluation cases",

        "evaluation_method": (
            "Rule-based evaluation of labelled synthetic cases "
            "using verified-round score recalculation, eligibility "
            "and risk checks, score consistency, mandatory-round "
            "validation, and review reporting."
        ),

        "configuration": {
            "select_threshold": SELECT_THRESHOLD,
            "review_threshold": REVIEW_THRESHOLD,
            "maximum_score_difference": MAX_SCORE_DIFFERENCE,
            "maximum_round_spread": MAX_ROUND_SPREAD,
            "mandatory_rounds": MANDATORY_ROUNDS,
            "round_weights": ROUND_WEIGHTS,
        },

        "dataset_count": len(dataset),
        "evaluated_count": len(results),
        "error_count": len(errors),

        "metrics": metrics,

        "performance": {
            "total_processing_time_ms": round(
                total_ms,
                4
            ),

            "average_time_per_case_ms": (
                round(mean(case_times), 4)
                if case_times
                else None
            ),
        },

        "results": results,
        "errors": errors,

        "limitations": [
            "Dataset scores and labels are illustrative synthetic data.",
            "These metrics do not establish real-world hiring accuracy.",
            "Thresholds and weights require validation against reviewed historical data.",
            "Review cases are reported separately from binary metrics.",
            "Score consistency is a safeguard, not proof of correctness.",
            "This evaluator does not modify the Day 52 decision engine.",
            "This script does not make or execute actual hiring decisions.",
            "Human oversight is required for real hiring workflows.",
        ],
    }

    with REPORT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # TERMINAL SUMMARY
    # --------------------------------------------------------

    print()
    print("=" * 52)
    print("ZecPath Day 54 - Improved AI Accuracy")
    print("=" * 52)

    print(f"Dataset cases:      {len(dataset)}")
    print(f"Evaluated cases:    {len(results)}")
    print(f"Errors:             {len(errors)}")

    print(
        f"True positives:     {metrics['true_positives']}"
    )
    print(
        f"True negatives:     {metrics['true_negatives']}"
    )
    print(
        f"False positives:    {metrics['false_positives']}"
    )
    print(
        f"False negatives:    {metrics['false_negatives']}"
    )

    print(
        f"Review decisions:   {metrics['review_count']}"
    )
    print(
        f"Accuracy (%):       {metrics['accuracy_percent']}"
    )
    print(
        f"Precision (%):      {metrics['precision_percent']}"
    )
    print(
        f"Recall (%):         {metrics['recall_percent']}"
    )
    print(
        f"Review rate (%):    {metrics['review_rate_percent']}"
    )

    print(f"Report saved to:    {REPORT_FILE}")

    if errors:
        print("\nEvaluation errors:")

        for error in errors:
            print(
                f"  Case {error['case_index']} "
                f"({error['candidate_id']}): "
                f"{error['error']}"
            )


if __name__ == "__main__":
    main()
