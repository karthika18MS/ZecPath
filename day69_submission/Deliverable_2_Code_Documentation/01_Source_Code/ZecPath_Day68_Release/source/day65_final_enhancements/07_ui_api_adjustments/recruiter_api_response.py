
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORTS_DIR = (
    PROJECT_ROOT
    / "day65_final_enhancements"
    / "09_final_outputs"
    / "recruiter_reports"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "day65_final_enhancements"
    / "09_final_outputs"
    / "recruiter_api_response_preview.json"
)


def build_candidate_response(report):
    """
    Convert one recruiter report into a standardized
    frontend/API-friendly response.
    """

    candidate_info = report.get("candidate_information", {})
    overview = report.get("recruiter_overview", {})

    response_data = {
        "candidate": {
            "candidate_id": candidate_info.get("candidate_id"),
            "job_id": candidate_info.get("job_id")
        },

        "overview": {
            "unified_score": overview.get("unified_score"),
            "formatted_score": overview.get(
                "formatted_unified_score", "Not available"
            ),
            "score_coverage": overview.get("score_coverage"),
            "formatted_coverage": overview.get(
                "formatted_coverage", "Not available"
            ),
            "scoring_status": overview.get("scoring_status"),
            "ats_eligibility": overview.get("ats_eligibility"),
            "final_decision": overview.get("final_decision")
        },

        "assessments": report.get("assessment_summary", []),

        "evaluation": report.get("overall_evaluation", {}),

        "decision": report.get("final_decision", {}),

        "recruiter_action": report.get("recruiter_action", {}),

        "data_provenance": report.get("data_provenance", {}),

        "warnings": report.get("warnings", [])
    }

    return {
        "success": True,
        "message": "Candidate report retrieved successfully.",
        "data": response_data,
        "errors": []
    }


def load_candidate_report(file_path):
    """Safely load and format one candidate report."""

    try:
        with file_path.open("r", encoding="utf-8") as file:
            report = json.load(file)

        if not isinstance(report, dict):
            raise ValueError("Report must contain a JSON object.")

        required_sections = [
            "candidate_information",
            "recruiter_overview",
            "assessment_summary",
            "overall_evaluation",
            "final_decision",
            "recruiter_action"
        ]

        missing_sections = [
            section for section in required_sections
            if section not in report
        ]

        if missing_sections:
            raise ValueError(
                "Missing report sections: "
                + ", ".join(missing_sections)
            )

        return build_candidate_response(report)

    except (OSError, json.JSONDecodeError, ValueError) as error:
        return {
            "success": False,
            "message": "Unable to load candidate report.",
            "data": None,
            "errors": [str(error)]
        }


def build_batch_response():
    """Build a standardized response for all recruiter reports."""

    if not REPORTS_DIR.exists():
        return {
            "success": False,
            "message": "Recruiter reports directory not found.",
            "count": 0,
            "results": [],
            "errors": [str(REPORTS_DIR)]
        }

    report_files = sorted(REPORTS_DIR.glob("*_report.json"))

    results = []
    errors = []

    for file_path in report_files:
        response = load_candidate_report(file_path)

        if response["success"]:
            results.append(response["data"])
        else:
            errors.append({
                "file": file_path.name,
                "errors": response["errors"]
            })

    return {
        "success": len(errors) == 0,
        "message": "Recruiter batch response generated.",
        "count": len(results),
        "results": results,
        "errors": errors
    }


def main():
    print("=" * 65)
    print("ZECPath DAY 65 - RECRUITER API RESPONSE FORMATTER")
    print("=" * 65)

    response = build_batch_response()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            response,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nAPI RESPONSE SUMMARY")
    print("-" * 65)
    print(f"Success       : {response['success']}")
    print(f"Reports loaded: {response['count']}")
    print(f"Errors        : {len(response['errors'])}")

    print("\nOUTPUT FILE")
    print(OUTPUT_FILE)

    if response["success"]:
        print("\nAPI RESPONSE FORMATTING COMPLETED")
        return 0

    print("\nAPI RESPONSE FORMATTING COMPLETED WITH ERRORS")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
