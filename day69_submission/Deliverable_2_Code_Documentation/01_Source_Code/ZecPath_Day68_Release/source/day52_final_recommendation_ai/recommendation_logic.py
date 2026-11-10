
# ============================================================
# ZecPath Day 52 - Deliverable 2
# Recommendation Logic
# ============================================================

DEFAULT_RULES = {
    "selected_minimum_score": 80.0,
    "review_minimum_score": 60.0,
    "require_verified_data_for_selection": True,
    "review_if_demo_data": True,
    "review_if_risk_flags": True,
    "review_if_low_confidence": True,
    "minimum_confidence_for_selection": 80.0,
}

VALID_DECISIONS = (
    "Selected",
    "Hold / Review",
    "Rejected",
)


def validate_rules(rules):
    """Validate decision thresholds."""

    required_keys = (
        "selected_minimum_score",
        "review_minimum_score",
        "minimum_confidence_for_selection",
    )

    for key in required_keys:
        value = rules.get(key)

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not 0 <= value <= 100
        ):
            raise ValueError(
                f"{key} must be a number between 0 and 100."
            )

    if (
        rules["review_minimum_score"]
        > rules["selected_minimum_score"]
    ):
        raise ValueError(
            "Review threshold cannot exceed selection threshold."
        )


def get_demo_rounds(candidate):
    """Find rounds that explicitly contain demo data."""

    rounds = candidate.get("evaluation_rounds", {})
    demo_rounds = []

    for name, data in rounds.items():
        if not isinstance(data, dict):
            continue

        if (
            data.get("is_demo_data", False)
            or data.get("data_type") == "DEMO_ONLY"
        ):
            demo_rounds.append(name)

    return sorted(demo_rounds)


def make_recommendation(
    score,
    confidence,
    risk,
    candidate,
    eligibility=None,
    rules=None,
):
    """
    Apply score thresholds and decision safeguards.

    Decision categories:
        Selected
        Hold / Review
        Rejected

    A high score alone cannot override data-quality safeguards.
    """

    active_rules = dict(DEFAULT_RULES)
    if rules:
        active_rules.update(rules)

    validate_rules(active_rules)

    if (
        isinstance(score, bool)
        or not isinstance(score, (int, float))
        or not 0 <= score <= 100
    ):
        raise ValueError("Score must be between 0 and 100.")

    confidence_score = confidence.get("confidence_score", 0)

    if (
        isinstance(confidence_score, bool)
        or not isinstance(confidence_score, (int, float))
        or not 0 <= confidence_score <= 100
    ):
        raise ValueError(
            "Confidence score must be between 0 and 100."
        )

    eligibility = eligibility or {}
    eligibility_status = eligibility.get(
        "status", "NOT_PROVIDED"
    )

    risk_flags = risk.get("risk_flags", [])
    demo_rounds = get_demo_rounds(candidate)

    reasons = []

    if demo_rounds and active_rules["review_if_demo_data"]:
        reasons.append(
            "Demo data is present in: "
            + ", ".join(demo_rounds)
        )

    if risk_flags and active_rules["review_if_risk_flags"]:
        reasons.append(
            "Explicit risk flags require human review."
        )

    if eligibility_status == "NOT_PROVIDED":
        reasons.append(
            "Eligibility status was not provided."
        )
    elif eligibility_status == "REVIEW":
        reasons.append(
            "Eligibility requirements need further review."
        )
    elif eligibility_status == "REJECTED":
        return {
            "decision": "Rejected",
            "reasons": [
                "A documented, job-related eligibility requirement "
                "was not met."
            ],
            "decision_policy": "Rule-based recommendation.",
            "score_thresholds": active_rules,
            "eligibility_status": eligibility_status,
            "human_review_required": True,
        }
    elif eligibility_status != "ELIGIBLE":
        reasons.append(
            "Eligibility is not confirmed."
        )

    if (
        active_rules["review_if_low_confidence"]
        and confidence_score
        < active_rules["minimum_confidence_for_selection"]
    ):
        reasons.append(
            "Confidence indicator is below the configured threshold."
        )

    verified_status = candidate.get(
        "overall_evaluation", {}
    ).get(
        "verified_hiring_fit_status", "NOT_EVALUATED"
    )

    verified_data_available = (
        not demo_rounds
        and verified_status not in (
            "NOT_EVALUATED",
            "INCOMPLETE",
        )
    )

    verified_requirement_passed = (
        verified_data_available
        or not active_rules["require_verified_data_for_selection"]
    )

    safeguards_passed = (
        not demo_rounds
        and not risk_flags
        and eligibility_status == "ELIGIBLE"
        and confidence_score
        >= active_rules["minimum_confidence_for_selection"]
        and verified_requirement_passed
    )

    if score >= active_rules["selected_minimum_score"]:
        if safeguards_passed:
            decision = "Selected"
            reasons.append(
                "The score meets the selection threshold and "
                "all configured safeguards passed."
            )
        else:
            decision = "Hold / Review"
            reasons.append(
                "The score meets the selection threshold, but "
                "one or more safeguards require review."
            )

    elif score >= active_rules["review_minimum_score"]:
        decision = "Hold / Review"
        reasons.append(
            "The score falls within the configured review range."
        )

    else:
        decision = "Rejected"
        reasons.append(
            "The score is below the configured review threshold."
        )

    return {
        "decision": decision,
        "reasons": reasons,
        "decision_policy": (
            "Score thresholds combined with eligibility, "
            "confidence, risk, and data-quality safeguards."
        ),
        "score_thresholds": active_rules,
        "eligibility_status": eligibility_status,
        "human_review_required": decision == "Hold / Review",
    }
