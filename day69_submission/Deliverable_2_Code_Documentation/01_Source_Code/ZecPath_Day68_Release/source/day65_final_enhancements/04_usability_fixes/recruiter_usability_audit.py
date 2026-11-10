
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
    / "recruiter_usability_audit.json"
)

# Decision-specific guidance expected in recruiter actions.
EXPECTED_ACTIONS = {
    "ELIGIBLE_FOR_NEXT_STAGE": [
        "review",
        "evidence"
    ],
    "MANUAL_REVIEW": [
        "manually",
        "review"
    ],
    "NOT_ELIGIBLE": [
        "review",
        "eligibility"
    ],
    "BLOCKED_PENDING_ATS": [
        "ats",
        "eligibility"
    ]
}


def audit_report(report, filename):
    issues = []

    candidate = report.get("candidate_information", {})
    overview = report.get("recruiter_overview", {})
    decision = report.get("final_decision", {})
    action = report.get("recruiter_action", {})
    assessments = report.get("assessment_summary", [])

    candidate_id = candidate.get("candidate_id", filename)

    decision_status = decision.get("status")
    explanation = str(decision.get("explanation", "")).lower()
    suggested_action = str(
        action.get("suggested_action", "")
    ).lower()

    # 1. Candidate identity must be visible.
    if not candidate_id:
        issues.append("Candidate identity is missing.")

    if not candidate.get("job_id"):
        issues.append("Job identity is missing.")

    # 2. Decision must have a useful explanation.
    if len(explanation.strip()) < 20:
        issues.append("Decision explanation is too short or missing.")

    # 3. Recruiter action must guide the next step.
    if len(suggested_action.strip()) < 20:
        issues.append("Recruiter action is too short or missing.")

    expected_words = EXPECTED_ACTIONS.get(decision_status, [])

    for word in expected_words:
        if word not in suggested_action:
            issues.append(
                f"Recruiter action does not clearly mention: {word}"
            )

    # 4. Missing scores must not be presented as zero.
    if overview.get("unified_score") is None:
        if overview.get("formatted_unified_score") != "Not available":
            issues.append(
                "Missing unified score must display as Not available."
            )

    # 5. Incomplete assessments must be identified.
    missing_rounds = [
        item.get("round_name", item.get("round", "Unknown"))
        for item in assessments
        if isinstance(item, dict) and item.get("score") is None
    ]

    if decision_status == "BLOCKED_PENDING_ATS":
        ats_item = next(
            (
                item for item in assessments
                if isinstance(item, dict)
                and item.get("round") == "ats"
            ),
            None
        )

        if ats_item is None or ats_item.get("score") is None:
            if "ats" not in suggested_action:
                issues.append(
                    "Blocked candidate needs an ATS-specific next action."
                )

    # 6. Demo warning must remain visible.
    warnings = report.get("warnings", [])

    if not any(
        "demo dataset" in str(warning).lower()
        for warning in warnings
    ):
        issues.append("Demo dataset warning is missing.")

    return {
        "candidate_id": candidate_id,
        "job_id": candidate.get("job_id"),
        "decision": decision_status,
        "missing_assessments": missing_rounds,
        "usability_status": "PASS" if not issues else "NEEDS_REVIEW",
        "issues": issues
    }


def main():
    print("=" * 65)
    print("ZECPath DAY 65 - RECRUITER USABILITY AUDIT")
    print("=" * 65)

    if not REPORTS_DIR.exists():
        print(f"ERROR: Reports directory not found: {REPORTS_DIR}")
        return 1

    report_files = sorted(REPORTS_DIR.glob("*_report.json"))

    if not report_files:
        print("ERROR: No recruiter reports found.")
        return 1

    results = []
    loading_errors = []

    for path in report_files:
        try:
            with path.open("r", encoding="utf-8") as file:
                report = json.load(file)

            result = audit_report(report, path.name)
            results.append(result)

            status = result["usability_status"]
            print(
                f"[{status}] {result['candidate_id']} - "
                f"{result['decision']}"
            )

            for issue in result["issues"]:
                print(f"    - {issue}")

        except (OSError, json.JSONDecodeError) as error:
            loading_errors.append({
                "file": path.name,
                "error": str(error)
            })

    passed = sum(
        1 for item in results
        if item["usability_status"] == "PASS"
    )

    needs_review = len(results) - passed

    summary = {
        "module": "Day 65 Recruiter Usability Audit",
        "reports_found": len(report_files),
        "reports_audited": len(results),
        "passed": passed,
        "needs_review": needs_review,
        "loading_errors": loading_errors,
        "overall_status": (
            "PASSED"
            if needs_review == 0 and not loading_errors
            else "NEEDS_REVIEW"
        ),
        "candidate_results": results
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4, ensure_ascii=False)

    print("\n" + "=" * 65)
    print("USABILITY AUDIT SUMMARY")
    print("=" * 65)
    print(f"Reports found : {len(report_files)}")
    print(f"Audited       : {len(results)}")
    print(f"Passed        : {passed}")
    print(f"Needs review  : {needs_review}")
    print(f"Loading errors: {len(loading_errors)}")
    print(f"Status        : {summary['overall_status']}")

    print(f"\nOutput saved to:\n{OUTPUT_FILE}")

    return 0 if summary["overall_status"] == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
