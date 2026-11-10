
import json
import math
from pathlib import Path
from datetime import datetime, timezone


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "day63_demo_dataset"
    / "06_end_to_end_simulation"
    / "outputs"
    / "cross_round_scoring_results.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "day65_final_enhancements"
    / "09_final_outputs"
    / "recruiter_reports"
)


# --------------------------------------------------
# ASSESSMENT CONFIGURATION
# --------------------------------------------------

ROUND_LABELS = {
    "ats": "ATS Screening",
    "hr": "HR Interview",
    "aptitude": "Aptitude Assessment",
    "technical": "Technical Interview",
    "machine_test": "Machine Test"
}


DECISION_EXPLANATIONS = {
    "ELIGIBLE_FOR_NEXT_STAGE":
        "The scoring engine marked this candidate eligible for the "
        "next stage. This is a system recommendation, not a final "
        "hiring decision.",

    "MANUAL_REVIEW":
        "This candidate requires manual recruiter review. Inspect "
        "the assessment results and ATS eligibility before deciding "
        "whether to proceed.",

    "NOT_ELIGIBLE":
        "The scoring engine marked this candidate as not eligible "
        "under its configured decision rules. Review the underlying "
        "results and applicable policy before taking action.",

    "BLOCKED_PENDING_ATS":
        "Progress is blocked because ATS eligibility is missing or "
        "blocked. Do not use the unified score alone to advance "
        "this candidate."
}


RECRUITER_ACTIONS = {
    "ELIGIBLE_FOR_NEXT_STAGE":
        "Review the assessment evidence and data provenance. If "
        "verified and permitted by hiring policy, consider inviting "
        "the candidate to the next stage.",

    "MANUAL_REVIEW":
        "Manually inspect the assessment scores, missing information, "
        "and ATS eligibility. Record the review outcome.",

    "NOT_ELIGIBLE":
        "Review the configured eligibility rules and assessment "
        "evidence before confirming any rejection action.",

    "BLOCKED_PENDING_ATS":
        "Obtain or verify the candidate's ATS eligibility result "
        "before considering further progression."
}


# --------------------------------------------------
# SAFE FORMATTING HELPERS
# --------------------------------------------------

def format_score(score):
    """Format a score without confusing missing data with zero."""

    if score is None:
        return "Not available"

    if isinstance(score, bool):
        return "Invalid score"

    try:
        numeric_score = float(score)

        if not math.isfinite(numeric_score):
            return "Invalid score"

        return f"{numeric_score:.2f}/100"

    except (TypeError, ValueError):
        return "Invalid score"


def format_percentage(value):
    """Safely format percentage values."""

    if value is None or isinstance(value, bool):
        return "Not available"

    try:
        numeric_value = float(value)

        if not math.isfinite(numeric_value):
            return "Not available"

        return f"{numeric_value:.2f}%"

    except (TypeError, ValueError):
        return "Not available"


def safe_text(value, default="Not available"):
    """Return readable text for missing values."""

    if value is None:
        return default

    return str(value)


# --------------------------------------------------
# RECRUITER ACTION
# --------------------------------------------------

def get_recruiter_action(decision):
    return RECRUITER_ACTIONS.get(
        decision,
        "Review the candidate record, assessment evidence, "
        "and applicable hiring policy manually."
    )


# --------------------------------------------------
# BUILD INDIVIDUAL CANDIDATE REPORT
# --------------------------------------------------

def build_candidate_report(candidate, global_metadata):

    if not isinstance(candidate, dict):
        raise ValueError("Candidate record must be a JSON object.")

    if not isinstance(global_metadata, dict):
        global_metadata = {}

    candidate_id = candidate.get("candidate_id", "UNKNOWN")
    job_id = candidate.get("job_id", "UNKNOWN")

    round_details = candidate.get("round_details", {})

    if not isinstance(round_details, dict):
        round_details = {}

    missing_rounds = candidate.get("missing_rounds", [])

    if not isinstance(missing_rounds, list):
        missing_rounds = []

    assessment_results = []
    simulated_rounds = []
    unknown_provenance_rounds = []
    available_rounds = []

    # Process all assessment rounds
    for round_name, label in ROUND_LABELS.items():

        details = round_details.get(round_name, {})

        if not isinstance(details, dict):
            details = {}

        provenance = details.get("provenance", {})

        if not isinstance(provenance, dict):
            provenance = {}

        score = details.get("score")

        assessment_status = details.get(
            "assessment_status",
            "UNKNOWN"
        )

        is_simulated = provenance.get("is_simulated")

        if is_simulated is True:
            simulated_rounds.append(label)

        elif is_simulated is None:
            unknown_provenance_rounds.append(label)

        if score is not None:
            available_rounds.append(round_name)

        assessment_results.append({
            "round": round_name,
            "round_name": label,
            "score": score,
            "formatted_score": format_score(score),
            "assessment_status": assessment_status,
            "is_simulated": is_simulated,
            "score_source": provenance.get("score_source")
        })

    # Overall scoring information
    unified_score = candidate.get("unified_score")
    coverage = candidate.get("score_coverage", 0)

    decision = candidate.get("final_decision", "UNKNOWN")

    warnings = []

    # Missing assessment warnings
    if missing_rounds:

        missing_labels = [
            ROUND_LABELS.get(name, name)
            for name in missing_rounds
        ]

        warnings.append(
            "Missing assessments: " + ", ".join(missing_labels)
        )

    # Simulated data warning
    if simulated_rounds:

        warnings.append(
            "Simulated assessment data detected: "
            + ", ".join(simulated_rounds)
        )

    # Unknown provenance warning
    if unknown_provenance_rounds:

        warnings.append(
            "Provenance is not specified for: "
            + ", ".join(unknown_provenance_rounds)
        )

    # Missing unified score
    if unified_score is None:

        warnings.append(
            "No unified score is available because no round scores "
            "were provided."
        )

    # Incomplete coverage
    try:
        numeric_coverage = float(coverage)
    except (TypeError, ValueError):
        numeric_coverage = 0

    if numeric_coverage < 100:

        warnings.append(
            "Assessment coverage is incomplete: "
            + format_percentage(coverage)
        )

    # Demo dataset warning
    if global_metadata.get("dataset_type") == "DEMO_DATASET":

        warnings.append(
            "This report uses a demo dataset and is not suitable "
            "for real hiring decisions."
        )

    # General data-quality warning
    warnings.append(
        "Recruiters must independently verify candidate information "
        "and assessment evidence before making hiring decisions."
    )

    # ATS status is kept separate from unified score
    ats_eligibility = candidate.get(
        "ats_eligibility_status",
        "UNKNOWN"
    )

    # Construct report
    report = {
        "report_type": "Recruiter-Friendly Candidate Summary",

        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "candidate_information": {
            "candidate_id": candidate_id,
            "job_id": job_id
        },

        "recruiter_overview": {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "unified_score": unified_score,
            "formatted_unified_score": format_score(unified_score),
            "score_coverage": coverage,
            "formatted_coverage": format_percentage(coverage),
            "scoring_status": candidate.get("scoring_status"),
            "ats_eligibility": ats_eligibility,
            "final_decision": decision
        },

        "assessment_summary": assessment_results,

        "overall_evaluation": {
            "unified_score": unified_score,
            "score_coverage": coverage,
            "scoring_status": candidate.get("scoring_status"),
            "available_rounds": candidate.get(
                "available_rounds",
                available_rounds
            ),
            "missing_rounds": missing_rounds
        },

        "ats_eligibility": ats_eligibility,

        "final_decision": {
            "status": decision,
            "explanation": DECISION_EXPLANATIONS.get(
                decision,
                "No explanation is configured for this decision status."
            )
        },

        "recruiter_action": {
            "suggested_action": get_recruiter_action(decision),
            "requires_human_review": True
        },

        "data_provenance": {
            "dataset_type": global_metadata.get("dataset_type"),
            "simulated_assessments": simulated_rounds,
            "unknown_provenance_assessments": unknown_provenance_rounds
        },

        "warnings": warnings
    }

    return report


# --------------------------------------------------
# CREATE READABLE TEXT REPORT
# --------------------------------------------------

def create_text_report(report):

    candidate = report["candidate_information"]
    overview = report["recruiter_overview"]
    overall = report["overall_evaluation"]
    decision = report["final_decision"]
    recruiter_action = report["recruiter_action"]
    provenance = report["data_provenance"]

    lines = [

        "=" * 76,
        "ZECPath - RECRUITER CANDIDATE REPORT",
        "=" * 76,

        "",
        "1. CANDIDATE OVERVIEW",
        "-" * 76,

        f"Candidate ID          : {candidate['candidate_id']}",
        f"Job ID                : {candidate['job_id']}",
        f"Unified Score         : {overview['formatted_unified_score']}",
        f"Assessment Coverage   : {overview['formatted_coverage']}",
        f"Scoring Status        : {safe_text(overview['scoring_status'])}",
        f"ATS Eligibility       : {safe_text(overview['ats_eligibility'])}",
        f"Final Decision        : {overview['final_decision']}",

        "",
        "2. ASSESSMENT BREAKDOWN",
        "-" * 76,

        f"{'Assessment':<27} {'Score':<19} {'Status'}",
        "-" * 76
    ]

    for assessment in report["assessment_summary"]:

        lines.append(
            f"{assessment['round_name']:<27} "
            f"{assessment['formatted_score']:<19} "
            f"{assessment['assessment_status']}"
        )

    lines.extend([

        "",
        "3. ASSESSMENT COMPLETENESS",
        "-" * 76,

        f"Available Rounds : {', '.join(overall['available_rounds']) or 'None'}",
        f"Missing Rounds   : {', '.join(overall['missing_rounds']) or 'None'}",
        f"Coverage         : {format_percentage(overall['score_coverage'])}",

        "",
        "4. FINAL DECISION",
        "-" * 76,

        f"Decision : {decision['status']}",
        "",
        decision["explanation"],

        "",
        "5. SUGGESTED RECRUITER ACTION",
        "-" * 76,

        recruiter_action["suggested_action"],
        "",
        "Human review required: YES",

        "",
        "6. DATA PROVENANCE",
        "-" * 76,

        f"Dataset Type       : {safe_text(provenance['dataset_type'])}",

        "Simulated Rounds   : "
        + (
            ", ".join(provenance["simulated_assessments"])
            or "None identified"
        ),

        "Unknown Provenance : "
        + (
            ", ".join(provenance["unknown_provenance_assessments"])
            or "None identified"
        ),

        "",
        "7. WARNINGS",
        "-" * 76
    ])

    if report["warnings"]:

        for warning in report["warnings"]:
            lines.append(f"[!] {warning}")

    else:
        lines.append("No warnings.")

    lines.extend([

        "",
        "=" * 76,
        "END OF REPORT",
        "=" * 76
    ])

    return "\n".join(lines)


# --------------------------------------------------
# MAIN REPORT GENERATION
# --------------------------------------------------

def main():

    print("=" * 76)
    print("ZECPath DAY 65 - ENHANCED RECRUITER REPORT GENERATOR")
    print("=" * 76)

    # Validate input file
    if not INPUT_FILE.is_file():

        print("\nERROR: Cross-round scoring results not found.")
        print(INPUT_FILE)
        return

    # Load source data safely
    try:

        with INPUT_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

    except (OSError, json.JSONDecodeError) as exc:

        print("\nERROR: Unable to load cross-round scoring results.")
        print(str(exc))
        return

    if not isinstance(data, dict):

        print("\nERROR: Input JSON root must be an object.")
        return

    candidates = data.get("candidate_results", [])
    global_metadata = data.get("dataset", {})

    if not isinstance(candidates, list) or not candidates:

        print("\nERROR: No valid candidate records found.")
        return

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    index = []

    successful = 0
    failed = 0
    errors = []

    # Generate individual reports
    for candidate in candidates:

        candidate_id = "UNKNOWN"

        try:

            if isinstance(candidate, dict):
                candidate_id = candidate.get(
                    "candidate_id",
                    "UNKNOWN"
                )

            report = build_candidate_report(
                candidate,
                global_metadata
            )

            candidate_id = report[
                "candidate_information"
            ]["candidate_id"]

            json_path = OUTPUT_DIR / f"{candidate_id}_report.json"
            text_path = OUTPUT_DIR / f"{candidate_id}_report.txt"

            # Save JSON report
            with json_path.open(
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    report,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            # Save readable TXT report
            with text_path.open(
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    create_text_report(report)
                )

            successful += 1

            index.append({
                "candidate_id": candidate_id,
                "job_id": report["candidate_information"]["job_id"],
                "unified_score": report["overall_evaluation"]["unified_score"],
                "coverage": report["overall_evaluation"]["score_coverage"],
                "final_decision": report["final_decision"]["status"],
                "warnings_count": len(report["warnings"]),
                "json_report": json_path.name,
                "text_report": text_path.name
            })

            print(
                f"Generated report: {candidate_id} | "
                f"Decision: {report['final_decision']['status']}"
            )

        except Exception as exc:

            failed += 1

            error_record = {
                "candidate_id": candidate_id,
                "error": str(exc)
            }

            errors.append(error_record)

            print(
                f"FAILED: {candidate_id} | {exc}"
            )

    # Generate report index
    index_report = {

        "module": "ZecPath Day 65 Enhanced Recruiter Report Generator",

        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "dataset_type": global_metadata.get("dataset_type"),

        "total_candidates": len(candidates),

        "successful_reports": successful,

        "failed_reports": failed,

        "generation_errors": errors,

        "candidate_report_index": index
    }

    index_path = OUTPUT_DIR / "recruiter_report_index.json"

    try:

        with index_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                index_report,
                file,
                indent=4,
                ensure_ascii=False
            )

    except OSError as exc:

        print("\nERROR: Unable to save report index.")
        print(str(exc))
        return

    # Final summary
    print("\n" + "=" * 76)
    print("ENHANCED REPORT GENERATION SUMMARY")
    print("=" * 76)

    print("Total candidates:", len(candidates))
    print("Successful reports:", successful)
    print("Failed reports:", failed)

    print("Output directory:", OUTPUT_DIR)
    print("Index report:", index_path)

    print("\nREPORT GENERATION COMPLETED")


# --------------------------------------------------
# DIRECT EXECUTION
# --------------------------------------------------

if __name__ == "__main__":
    main()
