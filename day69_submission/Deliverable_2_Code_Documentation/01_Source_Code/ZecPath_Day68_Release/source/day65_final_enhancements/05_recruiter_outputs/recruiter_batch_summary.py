
import json
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter


PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_DIR = (
    PROJECT_ROOT
    / "day65_final_enhancements"
    / "09_final_outputs"
    / "recruiter_reports"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "day65_final_enhancements"
    / "09_final_outputs"
)

JSON_OUTPUT = OUTPUT_DIR / "recruiter_batch_summary.json"
TEXT_OUTPUT = OUTPUT_DIR / "recruiter_batch_summary.txt"


def load_candidate_reports():
    reports = []
    errors = []

    if not REPORT_DIR.is_dir():
        raise FileNotFoundError(
            f"Recruiter report directory not found: {REPORT_DIR}"
        )

    report_files = sorted(REPORT_DIR.glob("CAND*_report.json"))

    if not report_files:
        raise FileNotFoundError("No candidate JSON reports found.")

    for report_file in report_files:
        try:
            with report_file.open("r", encoding="utf-8") as file:
                report = json.load(file)

            if not isinstance(report, dict):
                raise ValueError("Report must contain a JSON object.")

            candidate_info = report.get("candidate_information", {})
            if not candidate_info.get("candidate_id"):
                raise ValueError("Candidate ID is missing.")

            reports.append(report)

        except (OSError, json.JSONDecodeError, ValueError) as error:
            errors.append({
                "file": report_file.name,
                "error": str(error)
            })

    return reports, errors


def build_candidate_summary(report):
    candidate = report.get("candidate_information", {})
    overall = report.get("overall_evaluation", {})
    decision = report.get("final_decision", {})
    provenance = report.get("data_provenance", {})

    return {
        "candidate_id": candidate.get("candidate_id"),
        "job_id": candidate.get("job_id"),
        "unified_score": overall.get("unified_score"),
        "score_coverage": overall.get("score_coverage", 0),
        "scoring_status": overall.get("scoring_status"),
        "ats_eligibility": report.get("ats_eligibility"),
        "final_decision": decision.get("status"),
        "missing_assessments": overall.get("missing_rounds", []),
        "simulated_assessments": provenance.get(
            "simulated_assessments", []
        ),
        "warnings": report.get("warnings", [])
    }


def build_batch_summary(reports, errors):
    candidate_summaries = [
        build_candidate_summary(report)
        for report in reports
    ]

    decision_counts = Counter(
        item["final_decision"]
        for item in candidate_summaries
    )

    status_counts = Counter(
        item["scoring_status"]
        for item in candidate_summaries
    )

    scored_candidates = [
        item for item in candidate_summaries
        if item["unified_score"] is not None
    ]

    scores = [
        item["unified_score"] for item in scored_candidates
    ]

    average_score = (
        round(sum(scores) / len(scores), 2)
        if scores else None
    )

    highest_score = max(scores) if scores else None
    lowest_score = min(scores) if scores else None

    return {
        "module": "ZecPath Day 65 Recruiter Batch Summary",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_type": "DEMO_DATASET",
        "batch_summary": {
            "total_reports_loaded": len(reports),
            "failed_reports": len(errors),
            "scored_candidates": len(scored_candidates),
            "candidates_without_scores": (
                len(candidate_summaries) - len(scored_candidates)
            ),
            "average_unified_score": average_score,
            "highest_unified_score": highest_score,
            "lowest_unified_score": lowest_score,
            "decision_counts": dict(decision_counts),
            "scoring_status_counts": dict(status_counts)
        },
        "candidate_summaries": candidate_summaries,
        "report_loading_errors": errors,
        "important_notice": (
            "This is a demo dataset. Some assessment results are simulated "
            "and some assessment provenance is unknown. This summary is "
            "not suitable for real hiring decisions."
        )
    }


def create_text_summary(data):
    summary = data["batch_summary"]

    lines = [
        "=" * 90,
        "ZECPath - RECRUITER BATCH SUMMARY",
        "=" * 90,
        "",
        f"Generated at: {data['generated_at']}",
        f"Dataset type: {data['dataset_type']}",
        "",
        "BATCH OVERVIEW",
        "-" * 90,
        f"Reports loaded: {summary['total_reports_loaded']}",
        f"Failed reports: {summary['failed_reports']}",
        f"Candidates with scores: {summary['scored_candidates']}",
        f"Candidates without scores: {summary['candidates_without_scores']}",
        f"Average unified score: {summary['average_unified_score']}",
        f"Highest unified score: {summary['highest_unified_score']}",
        f"Lowest unified score: {summary['lowest_unified_score']}",
        "",
        "FINAL DECISION COUNTS",
        "-" * 90
    ]

    for decision, count in summary["decision_counts"].items():
        lines.append(f"{decision}: {count}")

    lines.extend([
        "",
        "SCORING STATUS COUNTS",
        "-" * 90
    ])

    for status, count in summary["scoring_status_counts"].items():
        lines.append(f"{status}: {count}")

    lines.extend([
        "",
        "CANDIDATE OVERVIEW",
        "-" * 90,
        f"{'Candidate':<13} {'Job':<8} {'Score':<12} "
        f"{'Coverage':<12} {'Decision'}",
        "-" * 90
    ])

    for candidate in data["candidate_summaries"]:
        score = candidate["unified_score"]
        score_text = f"{score:.2f}" if score is not None else "N/A"

        lines.append(
            f"{candidate['candidate_id']:<13} "
            f"{candidate['job_id']:<8} "
            f"{score_text:<12} "
            f"{candidate['score_coverage']:<12.2f} "
            f"{candidate['final_decision']}"
        )

        missing = candidate["missing_assessments"]

        if missing:
            lines.append(
                "    Missing assessments: " + ", ".join(missing)
            )

    lines.extend([
        "",
        "REPORT LOADING ERRORS",
        "-" * 90
    ])

    if data["report_loading_errors"]:
        for error in data["report_loading_errors"]:
            lines.append(f"{error['file']}: {error['error']}")
    else:
        lines.append("No report loading errors.")

    lines.extend([
        "",
        "IMPORTANT NOTICE",
        "-" * 90,
        data["important_notice"],
        "",
        "=" * 90,
        "END OF BATCH SUMMARY",
        "=" * 90
    ])

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("ZECPath DAY 65 - RECRUITER BATCH SUMMARY")
    print("=" * 70)

    try:
        reports, errors = load_candidate_reports()
        data = build_batch_summary(reports, errors)

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        with JSON_OUTPUT.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        with TEXT_OUTPUT.open("w", encoding="utf-8") as file:
            file.write(create_text_summary(data))

        summary = data["batch_summary"]

        print("\nBATCH SUMMARY")
        print("-" * 70)
        print("Reports loaded:", summary["total_reports_loaded"])
        print("Failed reports:", summary["failed_reports"])
        print("Scored candidates:", summary["scored_candidates"])
        print("Candidates without scores:",
              summary["candidates_without_scores"])
        print("Average unified score:",
              summary["average_unified_score"])

        print("\nFINAL DECISION COUNTS")
        for decision, count in summary["decision_counts"].items():
            print(f"{decision}: {count}")

        print("\nOUTPUT FILES")
        print("JSON:", JSON_OUTPUT)
        print("TEXT:", TEXT_OUTPUT)

        print("\nBATCH SUMMARY COMPLETED")

    except (OSError, ValueError, json.JSONDecodeError) as error:
        print("ERROR:", error)


if __name__ == "__main__":
    main()
