from typing import Dict, Any


# Day 54 - D3: Refined Scoring Logic

DEFAULT_WEIGHTS = {
    "ats": 0.15,
    "screening": 0.15,
    "hr_interview": 0.15,
    "technical_interview": 0.30,
    "machine_test": 0.25
}

DEFAULT_THRESHOLDS = {
    "selection": 80.0,
    "review": 60.0
}


def validate_weights(weights: Dict[str, float]) -> None:
    if not weights:
        raise ValueError("Weights cannot be empty.")

    for name, weight in weights.items():
        if not isinstance(weight, (int, float)) or isinstance(weight, bool):
            raise ValueError(f"Invalid weight for {name}.")

        if weight < 0:
            raise ValueError(f"Weight cannot be negative: {name}")

    if abs(sum(weights.values()) - 1.0) > 1e-9:
        raise ValueError("All weights must total 1.0.")


def validate_thresholds(thresholds: Dict[str, float]) -> None:
    selection = thresholds["selection"]
    review = thresholds["review"]

    if not (0 <= review <= selection <= 100):
        raise ValueError(
            "Thresholds must satisfy 0 <= review <= selection <= 100."
        )


def calculate_refined_score(
    scores: Dict[str, Any],
    weights: Dict[str, float] = None,
    thresholds: Dict[str, float] = None,
    eligibility_status: str = "ELIGIBLE",
    integrity_review_required: bool = False
) -> Dict[str, Any]:

    weights = weights or DEFAULT_WEIGHTS
    thresholds = thresholds or DEFAULT_THRESHOLDS

    validate_weights(weights)
    validate_thresholds(thresholds)

    missing = [name for name in weights if name not in scores]
    if missing:
        raise ValueError(
            "Missing scores: " + ", ".join(missing)
        )

    validated_scores = {}

    for name in weights:
        value = scores[name]

        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not 0 <= value <= 100
        ):
            raise ValueError(
                f"{name} must be a numeric score between 0 and 100."
            )

        validated_scores[name] = float(value)

    contributions = {
        name: round(validated_scores[name] * weights[name], 2)
        for name in weights
    }

    final_score = round(sum(contributions.values()), 2)

    # Eligibility and review rules take precedence over score.
    if str(eligibility_status).strip().upper() not in {
        "ELIGIBLE", "PASS"
    }:
        recommendation = "REJECTED"
        reason = "Mandatory eligibility requirements were not met."

    elif integrity_review_required:
        recommendation = "HOLD / REVIEW"
        reason = "Integrity-related evidence requires human review."

    elif final_score >= thresholds["selection"]:
        recommendation = "SELECTED"
        reason = "Score meets the configured selection threshold."

    elif final_score >= thresholds["review"]:
        recommendation = "HOLD / REVIEW"
        reason = "Score falls within the configured review range."

    else:
        recommendation = "REJECTED"
        reason = "Score is below the configured review threshold."

    return {
        "round_scores": validated_scores,
        "weights": weights,
        "weighted_contributions": contributions,
        "final_score": final_score,
        "thresholds": thresholds,
        "recommendation": recommendation,
        "explanation": reason,
        "calculation_method": "Weighted average",
        "status": "CALCULATED"
    }


if __name__ == "__main__":
    sample_scores = {
        "ats": 80,
        "screening": 85,
        "hr_interview": 86.75,
        "technical_interview": 90.04,
        "machine_test": 87
    }

    result = calculate_refined_score(sample_scores)

    print("DAY 54 - REFINED SCORING LOGIC")
    for key, value in result.items():
        print(f"{key}: {value}")