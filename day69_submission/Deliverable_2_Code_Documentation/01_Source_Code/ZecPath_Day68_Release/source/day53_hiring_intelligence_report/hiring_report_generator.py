
"""
ZecPath Day 53 - Hiring Intelligence Report Generator

Combines existing ATS, screening, HR, technical, machine-test,
unified-score and final-decision outputs into one JSON report.

Missing sources are reported as unavailable.
Source scores are not recalculated.
"""

import json
from pathlib import Path
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path(__file__).resolve().parent / "results"

SOURCE_FILES = {
    "ats": (
        ROOT_DIR
        / "day18_optimization"
        / "results"
        / "candidate_006"
        / "day18_optimized_ats_score.json"
    ),
    "screening": (
        ROOT_DIR
        / "day32_screening_finalization"
        / "results"
        / "final_screening_pipeline_result.json"
    ),
    "hr_interview": (
        ROOT_DIR
        / "day37_hr_interview_scoring"
        / "results"
        / "hr_interview_score.json"
    ),
    "technical_performance": (
        ROOT_DIR
        / "day47_technical_skill_scoring"
        / "results"
        / "candidate_technical_evaluation.json"
    ),
    "machine_test": (
        ROOT_DIR
        / "day50_machine_test_scoring"
        / "results"
        / "machine_test_score.json"
    ),
    "unified_candidate_score": (
        ROOT_DIR
        / "day51_cross_round_aggregation"
        / "results"
        / "unified_candidate_score.json"
    ),
    "final_recommendation": (
        ROOT_DIR
        / "day52_final_recommendation_ai"
        / "results"
        / "candidate_decision_output.json"
    ),
}


def load_json(path):
    """Load one JSON file without hiding parsing errors."""
    if not path.exists():
        return None, "MISSING"

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return None, "INVALID_FORMAT"

        return data, "AVAILABLE"

    except (json.JSONDecodeError, OSError):
        return None, "READ_ERROR"


def find_value(data, candidate_keys):
    """Find a value using known field names, including nested objects."""
    if not isinstance(data, dict):
        return None

    for key in candidate_keys:
        if key in data and data[key] is not None:
            return data[key]

    for value in data.values():
        if isinstance(value, dict):
            result = find_value(value, candidate_keys)
            if result is not None:
                return result

    return None


def build_section(source_name, path, data, status):
    """Build a report section while preserving the source data."""
    section = {
        "source_name": source_name,
        "source_file": str(path.relative_to(ROOT_DIR)),
        "status": status,
        "data": data,
    }

    if data is not None:
        section["source_score"] = find_value(
            data,
            [
                "final_ats_score",
                "ats_score",
                "screening_score",
                "hr_interview_score",
                "technical_score",
                "technical_evaluation_score",
                "machine_test_score",
                "overall_score",
                "hiring_fit_score",
            ],
        )

        section["source_decision"] = find_value(
            data,
            ["decision", "eligibility", "eligibility_status"],
        )

    return section


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sections = {}
    source_status = {}

    for name, path in SOURCE_FILES.items():
        data, status = load_json(path)
        source_status[name] = status

        sections[name] = build_section(
            source_name=name,
            path=path,
            data=data,
            status=status,
        )

    decision_data = sections["final_recommendation"]["data"]
    unified_data = sections["unified_candidate_score"]["data"]

    candidate_id = None
    job_id = None

    for source in (decision_data, unified_data):
        if source:
            candidate_id = candidate_id or find_value(
                source, ["candidate_id"]
            )
            job_id = job_id or find_value(
                source, ["job_id"]
            )

    report_type = "DEMO_ONLY"

    if decision_data:
        report_type = decision_data.get(
            "report_type", report_type
        )

    missing_sources = [
        name
        for name, status in source_status.items()
        if status != "AVAILABLE"
    ]

    report = {
        "report_title": "ZecPath Hiring Intelligence Report",
        "report_version": "1.0",
        "report_type": report_type,
        "report_status": (
            "PARTIAL" if missing_sources else "SUCCESS"
        ),
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),

        "candidate_information": {
            "candidate_id": candidate_id,
            "job_id": job_id,
        },

        "source_summary": {
            "total_sources": len(SOURCE_FILES),
            "available_sources": sum(
                status == "AVAILABLE"
                for status in source_status.values()
            ),
            "missing_or_invalid_sources": missing_sources,
            "source_status": source_status,
        },

        "evaluation_sections": sections,

        "final_recommendation": {
            "decision": (
                find_value(decision_data, ["decision"])
                if decision_data else None
            ),
            "hiring_fit_score": (
                find_value(
                    decision_data, ["hiring_fit_score"]
                )
                if decision_data else None
            ),
            "confidence": (
                decision_data.get("confidence")
                if decision_data else None
            ),
            "risk_assessment": (
                decision_data.get("risk_assessment")
                if decision_data else None
            ),
            "explanation": (
                decision_data.get("explanation")
                if decision_data else None
            ),
            "human_review_required": (
                decision_data.get("human_review_required")
                if decision_data else None
            ),
            "automated_hiring_action_taken": (
                decision_data.get(
                    "automated_hiring_action_taken"
                )
                if decision_data else None
            ),
        },

        "report_limitations": [
            "Source outputs are preserved and not rescored.",
            "Missing source data is not inferred or fabricated.",
            "A source being available does not mean its data is verified.",
            "Demo results must not be treated as verified hiring evidence.",
            "The report is decision support and requires appropriate "
            "human review.",
        ],
    }

    output_file = OUTPUT_DIR / "hiring_intelligence_report.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print("=" * 60)
    print("ZecPath Day 53 - Hiring Intelligence Report Generator")
    print("=" * 60)
    print("Candidate ID:", candidate_id or "NOT FOUND")
    print("Job ID:", job_id or "NOT FOUND")
    print(
        "Available sources:",
        report["source_summary"]["available_sources"],
        "/",
        report["source_summary"]["total_sources"],
    )
    print("Report status:", report["report_status"])

    if missing_sources:
        print("Missing or invalid sources:")
        for source in missing_sources:
            print(" -", source)

    print("Output saved to:", output_file)


if __name__ == "__main__":
    main()
