
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORTS_DIR = (
    PROJECT_ROOT
    / "day65_final_enhancements"
    / "09_final_outputs"
    / "recruiter_reports"
)

EXPECTED_ROUNDS = {
    "ats",
    "hr",
    "aptitude",
    "technical",
    "machine_test"
}

DEMO_WARNING = (
    "This report uses a demo dataset and is not suitable "
    "for real hiring decisions."
)


def check(condition, message, errors):
    if not condition:
        errors.append(message)


def validate_report(report, file_name):
    errors = []

    check(
        isinstance(report, dict),
        "Report must be a JSON object.",
        errors
    )

    if not isinstance(report, dict):
        return errors

    # 1. Candidate information
    candidate_info = report.get("candidate_information", {})
    overview = report.get("recruiter_overview", {})

    check(
        isinstance(candidate_info, dict),
        "Candidate information must be an object.",
        errors
    )

    check(
        isinstance(overview, dict),
        "Recruiter overview must be an object.",
        errors
    )

    if isinstance(candidate_info, dict) and isinstance(overview, dict):
        candidate_id = candidate_info.get("candidate_id")
        job_id = candidate_info.get("job_id")

        check(bool(candidate_id), "Candidate ID is missing.", errors)
        check(bool(job_id), "Job ID is missing.", errors)

        check(
            overview.get("candidate_id") == candidate_id,
            "Candidate ID mismatch in recruiter overview.",
            errors
        )

        check(
            overview.get("job_id") == job_id,
            "Job ID mismatch in recruiter overview.",
            errors
        )

        # 2. Unified score display
        score = overview.get("unified_score")
        formatted_score = overview.get("formatted_unified_score")

        if score is None:
            check(
                formatted_score == "Not available",
                "Missing unified score is not displayed clearly.",
                errors
            )
        else:
            try:
                expected = f"{float(score):.2f}/100"
                check(
                    formatted_score == expected,
                    f"Incorrect unified score formatting: expected {expected}.",
                    errors
                )
            except (TypeError, ValueError):
                errors.append("Unified score is not numeric.")

        # 3. Coverage display
        coverage = overview.get("score_coverage")
        formatted_coverage = overview.get("formatted_coverage")

        try:
            expected_coverage = f"{float(coverage):.2f}%"
            check(
                formatted_coverage == expected_coverage,
                "Score coverage formatting is incorrect.",
                errors
            )
        except (TypeError, ValueError):
            errors.append("Score coverage is missing or invalid.")

    # 4. Assessment readability
    assessments = report.get("assessment_summary")

    check(
        isinstance(assessments, list),
        "Assessment summary must be a list.",
        errors
    )

    if isinstance(assessments, list):
        actual_rounds = {
            item.get("round")
            for item in assessments
            if isinstance(item, dict)
        }

        check(
            actual_rounds == EXPECTED_ROUNDS,
            "Assessment rounds are missing or unexpected.",
            errors
        )

        for item in assessments:
            if not isinstance(item, dict):
                errors.append("Invalid assessment entry.")
                continue

            round_name = item.get("round_name", "Unknown round")
            score = item.get("score")
            formatted = item.get("formatted_score")

            if score is None:
                check(
                    formatted == "Not available",
                    f"{round_name}: missing score is not clearly displayed.",
                    errors
                )
            else:
                try:
                    expected = f"{float(score):.2f}/100"
                    check(
                        formatted == expected,
                        f"{round_name}: incorrect score formatting.",
                        errors
                    )
                except (TypeError, ValueError):
                    errors.append(f"{round_name}: invalid numeric score.")

            if item.get("is_simulated") is True:
                check(
                    bool(item.get("score_source")),
                    f"{round_name}: simulation source is not identified.",
                    errors
                )

    # 5. Final decision explanation
    decision = report.get("final_decision", {})

    check(
        isinstance(decision, dict),
        "Final decision must be an object.",
        errors
    )

    if isinstance(decision, dict):
        check(
            bool(decision.get("status")),
            "Final decision status is missing.",
            errors
        )

        check(
            bool(decision.get("explanation")),
            "Final decision explanation is missing.",
            errors
        )

    # 6. Recruiter action
    action = report.get("recruiter_action", {})

    check(
        isinstance(action, dict),
        "Recruiter action must be an object.",
        errors
    )

    if isinstance(action, dict):
        check(
            bool(action.get("suggested_action")),
            "Recruiter action is not clearly explained.",
            errors
        )

    # 7. Demo-data warning
    warnings = report.get("warnings", [])

    check(
        isinstance(warnings, list),
        "Warnings must be a list.",
        errors
    )

    if isinstance(warnings, list):
        check(
            any(DEMO_WARNING in str(w) for w in warnings),
            "Important demo dataset warning is missing.",
            errors
        )

    return errors


def main():
    print("=" * 65)
    print("ZECPath DAY 65 - RECRUITER OUTPUT READABILITY TEST")
    print("=" * 65)

    print(f"Reports directory: {REPORTS_DIR}")

    if not REPORTS_DIR.exists():
        print("ERROR: Recruiter reports directory not found.")
        return 1

    report_files = sorted(REPORTS_DIR.glob("*_report.json"))

    print(f"\nReports found: {len(report_files)}")

    if not report_files:
        print("ERROR: No recruiter JSON reports found.")
        return 1

    passed = 0
    failed = 0
    all_errors = []

    for file_path in report_files:
        try:
            with file_path.open("r", encoding="utf-8") as file:
                report = json.load(file)

            errors = validate_report(report, file_path.name)

            if errors:
                failed += 1
                print(f"\n[FAIL] {file_path.name}")

                for error in errors:
                    print(f"  - {error}")
                    all_errors.append({
                        "file": file_path.name,
                        "error": error
                    })
            else:
                passed += 1
                print(f"[PASS] {file_path.name}")

        except json.JSONDecodeError as error:
            failed += 1
            message = f"Invalid JSON: {error}"
            print(f"\n[FAIL] {file_path.name}: {message}")

            all_errors.append({
                "file": file_path.name,
                "error": message
            })

        except OSError as error:
            failed += 1
            message = f"File reading error: {error}"
            print(f"\n[FAIL] {file_path.name}: {message}")

            all_errors.append({
                "file": file_path.name,
                "error": message
            })

    summary = {
        "module": "Day 65 Recruiter Output Readability Test",
        "reports_found": len(report_files),
        "reports_passed": passed,
        "reports_failed": failed,
        "status": "PASSED" if failed == 0 else "FAILED",
        "errors": all_errors
    }

    output_path = (
        PROJECT_ROOT
        / "day65_final_enhancements"
        / "09_final_outputs"
        / "recruiter_readability_test_report.json"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4, ensure_ascii=False)

    print("\n" + "=" * 65)
    print("READABILITY TEST SUMMARY")
    print("=" * 65)

    print(f"Reports found : {len(report_files)}")
    print(f"Passed        : {passed}")
    print(f"Failed        : {failed}")
    print(f"Final status  : {summary['status']}")

    print(f"\nTest report saved to:\n{output_path}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
