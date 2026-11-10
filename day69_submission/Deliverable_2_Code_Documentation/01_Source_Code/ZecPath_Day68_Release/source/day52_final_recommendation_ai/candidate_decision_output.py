
"""
ZecPath Day 52 - Candidate Decision Output Format

Reads the Decision AI Engine JSON output and creates a
standardized candidate decision report.

This formatter preserves the original decision and does not
make an independent hiring decision.
"""

import json
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    BASE_DIR / "results" / "candidate_decision_output.json"
)

OUTPUT_FILE = (
    BASE_DIR / "results" / "formatted_candidate_decision.json"
)

VALID_DECISIONS = {
    "Selected",
    "Hold / Review",
    "Rejected",
}


def load_json(file_path):
    """Load and return JSON data."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}"
        )

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_input(data):
    """Validate the required fields."""
    if not isinstance(data, dict):
        raise ValueError(
            "Input must be a JSON object."
        )

    required_fields = [
        "candidate_id",
        "job_id",
        "hiring_fit_score",
        "decision",
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in data or data[field] is None
    ]

    if missing_fields:
        raise ValueError(
            "Missing required fields: "
            + ", ".join(missing_fields)
        )

    try:
        score = float(data["hiring_fit_score"])
    except (TypeError, ValueError):
        raise ValueError(
            "hiring_fit_score must be numeric."
        )

    if not 0 <= score <= 100:
        raise ValueError(
            "hiring_fit_score must be between 0 and 100."
        )

    if data["decision"] not in VALID_DECISIONS:
        raise ValueError(
            f"Invalid decision: {data['decision']}"
        )

    return score


def build_standard_report(data):
    """Map the engine's nested JSON into a standard format."""

    score = validate_input(data)

    # Read the nested objects from the original engine output.
    confidence_data = data.get("confidence", {})
    risk_data = data.get("risk_assessment", {})
    explanation_data = data.get("explanation", {})

    if not isinstance(confidence_data, dict):
        confidence_data = {}

    if not isinstance(risk_data, dict):
        risk_data = {}

    if not isinstance(explanation_data, dict):
        explanation_data = {}

    # Confidence is stored inside confidence.confidence_score.
    confidence_value = confidence_data.get(
        "confidence_score", data.get("confidence_score", 0)
    )

    try:
        confidence_value = float(confidence_value)
    except (TypeError, ValueError):
        raise ValueError(
            "The confidence score must be numeric."
        )

    if not 0 <= confidence_value <= 100:
        raise ValueError(
            "The confidence score must be between 0 and 100."
        )

    # Reasons are stored inside explanation.reasons.
    reasons = explanation_data.get(
        "reasons",
        data.get("decision_reasons", data.get("reasons", [])),
    )

    if not isinstance(reasons, list):
        raise ValueError(
            "Decision reasons must be a list."
        )

    # Demo rounds and risk flags are nested in risk_assessment.
    demo_rounds = risk_data.get(
        "demo_data_rounds",
        data.get("demo_data_rounds", []),
    )

    risk_flags = risk_data.get(
        "risk_flags",
        data.get("risk_flags", []),
    )

    if not isinstance(demo_rounds, list):
        raise ValueError(
            "demo_data_rounds must be a list."
        )

    if not isinstance(risk_flags, list):
        raise ValueError(
            "risk_flags must be a list."
        )

    eligibility = explanation_data.get(
        "eligibility_status",
        data.get("eligibility_status", "NOT_PROVIDED"),
    )

    human_review = data.get(
        "human_review_required",
        risk_data.get("requires_human_review", True),
    )

    if not isinstance(human_review, bool):
        raise ValueError(
            "human_review_required must be true or false."
        )

    automated_action = data.get(
        "automated_hiring_action_taken", False
    )

    if not isinstance(automated_action, bool):
        raise ValueError(
            "automated_hiring_action_taken must be true or false."
        )

    report = {
        "report_type": data.get("report_type", "DEMO_ONLY"),
        "output_status": "SUCCESS",
        "engine": (
            "ZecPath Day 52 Candidate Decision Output Formatter"
        ),
        "format_version": "1.1",

        "candidate_information": {
            "candidate_id": str(data["candidate_id"]),
            "job_id": str(data["job_id"]),
        },

        "decision_summary": {
            "hiring_fit_score": round(score, 2),
            "decision": data["decision"],
            "confidence_score": round(confidence_value, 2),
            "confidence_method": confidence_data.get(
                "method", "NOT_PROVIDED"
            ),
            "verified_rounds": confidence_data.get(
                "verified_rounds"
            ),
            "total_rounds": confidence_data.get(
                "total_rounds"
            ),
            "eligibility_status": eligibility,
        },

        "evaluation_quality": {
            "demo_data_rounds": demo_rounds,
            "risk_flags": risk_flags,
            "verified_hiring_fit_status": (
                "NOT_EVALUATED"
                if data.get("report_type") == "DEMO_ONLY"
                else data.get(
                    "verified_hiring_fit_status",
                    "NOT_EVALUATED",
                )
            ),
            "human_review_required": human_review,
            "automated_hiring_action_taken": automated_action,
        },

        "decision_reasons": [
            str(reason) for reason in reasons
        ],

        "decision_policy": explanation_data.get(
            "decision_policy", "NOT_PROVIDED"
        ),

        "score_thresholds": explanation_data.get(
            "score_thresholds", {}
        ),

        "audit_information": {
            "source_file": INPUT_FILE.name,
            "source_generated_at_utc": data.get(
                "generated_at_utc"
            ),
            "formatted_at_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "decision_changed_by_formatter": False,
        },
    }

    return report


def main():
    try:
        source_data = load_json(INPUT_FILE)
        report = build_standard_report(source_data)

        OUTPUT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with OUTPUT_FILE.open(
            "w", encoding="utf-8"
        ) as file:
            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False,
            )

        print("=" * 55)
        print("ZecPath Day 52 - Candidate Decision Output Format")
        print("=" * 55)

        print(
            "Candidate ID:",
            report["candidate_information"]["candidate_id"],
        )
        print(
            "Job ID:",
            report["candidate_information"]["job_id"],
        )
        print(
            "Hiring Fit Score:",
            f"{report['decision_summary']['hiring_fit_score']}/100",
        )
        print(
            "Decision:",
            report["decision_summary"]["decision"],
        )
        print(
            "Confidence:",
            f"{report['decision_summary']['confidence_score']}/100",
        )
        print(
            "Demo rounds:",
            report["evaluation_quality"]["demo_data_rounds"],
        )
        print(
            "Decision reasons:",
            len(report["decision_reasons"]),
        )
        print(
            "Human review required:",
            report["evaluation_quality"]["human_review_required"],
        )
        print(f"Output saved to: {OUTPUT_FILE}")

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        ValueError,
    ) as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
