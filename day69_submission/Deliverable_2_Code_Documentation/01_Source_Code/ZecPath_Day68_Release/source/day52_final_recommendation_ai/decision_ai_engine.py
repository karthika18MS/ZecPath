
import json
from pathlib import Path
from datetime import datetime, timezone

from recommendation_logic import make_recommendation


# ============================================================
# ZecPath Day 52 - Deliverable 1
# Decision AI Engine
# Integrated with Deliverable 2: Recommendation Logic
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
RESULTS_DIR = BASE_DIR / "results"

INPUT_FILE = (
    PROJECT_DIR
    / "day51_cross_round_aggregation"
    / "results"
    / "unified_candidate_score.json"
)

OUTPUT_FILE = RESULTS_DIR / "candidate_decision_output.json"


# ============================================================
# Configurable decision rules
# ============================================================

DECISION_RULES = {
    "selected_minimum_score": 80.0,
    "review_minimum_score": 60.0,
    "require_verified_data_for_selection": True,
    "review_if_demo_data": True,
    "review_if_risk_flags": True,
    "review_if_low_confidence": True,
    "minimum_confidence_for_selection": 80.0,
}


# ============================================================
# File handling
# ============================================================

def load_json(file_path):
    """Load a JSON object."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}\n"
            "Run the Day 51 unified candidate score module first."
        )

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object.")

    return data


def save_json(file_path, data):
    """Save a JSON object."""

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


# ============================================================
# Candidate validation
# ============================================================

def validate_candidate(candidate):
    """Validate candidate identity and round scores."""

    candidate_info = candidate.get("candidate", {})
    evaluation = candidate.get("overall_evaluation", {})
    rounds = candidate.get("evaluation_rounds", {})

    candidate_id = candidate_info.get("candidate_id")
    job_id = candidate_info.get("job_id")
    score = evaluation.get("hiring_fit_score")

    if not candidate_id or not job_id:
        raise ValueError("Candidate ID and job ID are required.")

    if (
        isinstance(score, bool)
        or not isinstance(score, (int, float))
        or not 0 <= score <= 100
    ):
        raise ValueError(
            "Hiring-fit score must be between 0 and 100."
        )

    required_rounds = (
        "ats",
        "screening",
        "hr_interview",
        "technical_interview",
        "machine_test",
    )

    for name in required_rounds:
        if name not in rounds:
            raise ValueError(f"Missing evaluation round: {name}")

        round_score = rounds[name].get("score")

        if (
            isinstance(round_score, bool)
            or not isinstance(round_score, (int, float))
            or not 0 <= round_score <= 100
        ):
            raise ValueError(f"Invalid score for round: {name}")

    return candidate_id, job_id, float(score)


# ============================================================
# Confidence indicator
# ============================================================

def calculate_confidence(candidate):
    """
    Calculate a data-completeness indicator.

    This is not a probability of hiring success.
    """

    rounds = candidate["evaluation_rounds"]

    required_rounds = (
        "ats",
        "screening",
        "hr_interview",
        "technical_interview",
        "machine_test",
    )

    verified_count = 0

    for name in required_rounds:
        data = rounds[name]

        is_demo = (
            data.get("is_demo_data", False)
            or data.get("data_type") == "DEMO_ONLY"
        )

        if not is_demo:
            verified_count += 1

    total = len(required_rounds)
    confidence_score = round(
        verified_count / total * 100, 2
    )

    return {
        "confidence_score": confidence_score,
        "scale": "0-100",
        "verified_rounds": verified_count,
        "total_rounds": total,
        "method": (
            "Percentage of rounds not labelled as demo data."
        ),
        "interpretation": (
            "Data-completeness indicator, not a probability "
            "of hiring success."
        ),
    }


# ============================================================
# Risk evaluation
# ============================================================

def evaluate_risk(candidate):
    """Check explicit risk flags and demo-data rounds."""

    supplied_flags = candidate.get("risk_flags", [])

    if not isinstance(supplied_flags, list):
        raise ValueError("risk_flags must be a list.")

    risk_flags = []

    for flag in supplied_flags:
        if isinstance(flag, str) and flag.strip():
            risk_flags.append(flag.strip())

        elif isinstance(flag, dict):
            name = flag.get("name")
            description = flag.get("description", "")

            if isinstance(name, str) and name.strip():
                risk_flags.append({
                    "name": name.strip(),
                    "description": (
                        description
                        if isinstance(description, str)
                        else ""
                    ),
                })

    demo_rounds = []

    for name, data in candidate["evaluation_rounds"].items():
        if (
            data.get("is_demo_data", False)
            or data.get("data_type") == "DEMO_ONLY"
        ):
            demo_rounds.append(name)

    return {
        "risk_flags": risk_flags,
        "demo_data_rounds": sorted(demo_rounds),
        "requires_human_review": bool(
            risk_flags or demo_rounds
        ),
        "method": (
            "Explicit input flags and evaluation-data labels."
        ),
    }


# ============================================================
# Decision pipeline
# ============================================================

def run_decision_engine(candidate):
    """Run validation, confidence, risk, and recommendation logic."""

    candidate_id, job_id, score = validate_candidate(candidate)

    confidence = calculate_confidence(candidate)
    risk = evaluate_risk(candidate)

    recommendation = make_recommendation(
        score=score,
        confidence=confidence,
        risk=risk,
        candidate=candidate,
        eligibility=None,
        rules=DECISION_RULES,
    )

    decision = recommendation["decision"]

    return {
        "engine": "ZecPath Day 52 Decision AI Engine",
        "engine_version": "1.1",
        "output_status": "SUCCESS",
        "report_type": candidate.get("report_type", "DEMO_ONLY"),
        "candidate_id": candidate_id,
        "job_id": job_id,
        "hiring_fit_score": round(score, 2),
        "decision": decision,
        "confidence": confidence,
        "risk_assessment": risk,
        "explanation": {
            "reasons": recommendation["reasons"],
            "decision_policy": recommendation["decision_policy"],
            "score_thresholds": recommendation["score_thresholds"],
            "eligibility_status": recommendation[
                "eligibility_status"
            ],
        },
        "human_review_required": (
            recommendation["human_review_required"]
            or risk["requires_human_review"]
        ),
        "automated_hiring_action_taken": False,
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
    }


# ============================================================
# Main
# ============================================================

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    candidate = load_json(INPUT_FILE)
    output = run_decision_engine(candidate)

    save_json(OUTPUT_FILE, output)

    print("=" * 65)
    print("ZecPath Day 52 - Decision AI Engine")
    print("=" * 65)

    print(f"Candidate ID: {output['candidate_id']}")
    print(f"Job ID: {output['job_id']}")
    print(f"Hiring Fit Score: {output['hiring_fit_score']:.2f}/100")
    print(f"Decision: {output['decision']}")
    print(
        "Confidence Indicator: "
        f"{output['confidence']['confidence_score']:.2f}/100"
    )
    print(
        "Demo rounds: "
        f"{output['risk_assessment']['demo_data_rounds']}"
    )

    print("\nDecision reasons:")

    for reason in output["explanation"]["reasons"]:
        print(f"- {reason}")

    print(
        "\nHuman review required: "
        f"{output['human_review_required']}"
    )
    print(f"\nOutput saved to: {OUTPUT_FILE}")
    print("=" * 65)


if __name__ == "__main__":
    main()
