
"""
ZecPath - Deliverable 3
Refined Stability Checker

Purpose:
1. Validate the Day 56 system report.
2. Detect demo data and human-vs-AI comparison flags.
3. Validate candidate ATS scores.
4. Check cross-round candidate score completeness.
5. Recalculate cross-round scores using configured weights.
6. Generate JSON and Markdown stability reports.

Uses only Python standard-library modules.
"""

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

DAY56_REPORT = (
    ROOT
    / "day56_full_system_simulation"
    / "results"
    / "end_to_end_test_report.json"
)

RESULTS_DIR = (
    ROOT
    / "day57_debugging_stabilization"
    / "results"
)

JSON_REPORT = RESULTS_DIR / "stability_test_report.json"
MARKDOWN_REPORT = RESULTS_DIR / "stability_test_report.md"

CANDIDATE_IDS = [
    f"candidate_{number:03d}"
    for number in range(6, 14)
]

ROUND_WEIGHTS = {
    "ats": 0.30,
    "hr": 0.30,
    "aptitude": 0.40,
}

REQUIRED_CROSS_ROUND_FIELDS = [
    "ats_score",
    "hr_score",
    "logical_reasoning_score",
    "scenario_evaluation_score",
    "final_cross_round_score",
]


# ---------------------------------------------------------
# GENERAL UTILITIES
# ---------------------------------------------------------

def load_json(path):
    """Load a JSON file safely."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, OSError) as error:
        return {
            "_load_error": str(error)
        }


def save_json(path, data):
    """Save a JSON report."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def find_score(data, possible_keys):
    """
    Find a valid numeric score using known possible key names.

    Scores must be between 0 and 100.
    Boolean values are not accepted as scores.
    """
    if not isinstance(data, dict):
        return None

    for key in possible_keys:
        value = data.get(key)

        if isinstance(value, (int, float)) and not isinstance(
            value, bool
        ):
            if 0 <= value <= 100:
                return float(value)

    return None


def read_score_file(path, possible_keys):
    """Read a score from a JSON file."""
    data = load_json(path)

    if not isinstance(data, dict):
        return None

    # Check the root object first.
    score = find_score(data, possible_keys)

    if score is not None:
        return score

    # Check common nested result objects.
    for nested_key in (
        "scores",
        "result",
        "evaluation",
        "final_evaluation",
        "interview_summary",
        "candidate_information",
    ):
        nested = data.get(nested_key)

        if isinstance(nested, dict):
            score = find_score(nested, possible_keys)

            if score is not None:
                return score

    return None


def add_check(report, name, status, details):
    """Add one validation check to the report."""
    report["checks"].append({
        "check": name,
        "status": status,
        "details": details,
    })


# ---------------------------------------------------------
# DAY 56 REPORT VALIDATION
# ---------------------------------------------------------

def validate_day56_report(report):
    """Check Day 56 output and its important status flags."""

    path = DAY56_REPORT

    if not path.exists():
        add_check(
            report,
            "Day 56 report",
            "REVIEW_REQUIRED",
            f"Report not found: {path}",
        )
        return

    data = load_json(path)

    if not isinstance(data, dict) or "_load_error" in data:
        add_check(
            report,
            "Day 56 report",
            "FAIL",
            "The report is not valid readable JSON.",
        )
        return

    add_check(
        report,
        "Day 56 report",
        "PASS",
        "Day 56 report exists and contains valid JSON.",
    )

    summary = data.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}

    # Prefer top-level values. Use summary as a fallback.
    flag_names = (
        "demo_data_used",
        "human_vs_ai_comparison_performed",
    )

    for flag in flag_names:
        if flag in data:
            value = data[flag]
        elif flag in summary:
            value = summary[flag]
        else:
            add_check(
                report,
                flag,
                "REVIEW_REQUIRED",
                "Flag is missing from both the report and summary.",
            )
            continue

        if not isinstance(value, bool):
            add_check(
                report,
                flag,
                "REVIEW_REQUIRED",
                f"Expected a Boolean value; received {value!r}.",
            )
            continue

        if flag == "demo_data_used" and value is True:
            add_check(
                report,
                flag,
                "REVIEW_REQUIRED",
                "Demo data was used. Do not interpret demo results "
                "as real candidate results.",
            )

        elif (
            flag == "human_vs_ai_comparison_performed"
            and value is False
        ):
            add_check(
                report,
                flag,
                "REVIEW_REQUIRED",
                "Human-vs-AI comparison has not been performed.",
            )

        else:
            add_check(
                report,
                flag,
                "PASS",
                f"{flag} = {value}.",
            )

    # Check pipeline stage counts when available.
    total_stages = summary.get("total_stages")
    passed_stages = summary.get("passed_stages")

    if (
        isinstance(total_stages, int)
        and not isinstance(total_stages, bool)
        and isinstance(passed_stages, int)
        and not isinstance(passed_stages, bool)
    ):
        if (
            total_stages >= 0
            and 0 <= passed_stages <= total_stages
        ):
            status = (
                "PASS"
                if passed_stages == total_stages
                else "REVIEW_REQUIRED"
            )

            add_check(
                report,
                "Day 56 stage results",
                status,
                f"{passed_stages}/{total_stages} stages passed.",
            )
        else:
            add_check(
                report,
                "Day 56 stage results",
                "REVIEW_REQUIRED",
                "Stage counts are inconsistent.",
            )


# ---------------------------------------------------------
# CANDIDATE OUTPUT DISCOVERY
# ---------------------------------------------------------

def find_candidate_file(base_dir, candidate_id):
    """Find a candidate JSON file in a results directory."""

    if not base_dir.exists():
        return None

    # Common structure: results/candidate_006/*.json
    candidate_dir = base_dir / candidate_id

    if candidate_dir.is_dir():
        files = sorted(candidate_dir.glob("*.json"))

        if files:
            return files[0]

    # Common structure: results/candidate_006.json
    direct_file = base_dir / f"{candidate_id}.json"

    if direct_file.is_file():
        return direct_file

    # Search nested result folders, including Day 18 formats.
    matching_files = []

    try:
        for path in base_dir.rglob("*.json"):
            if candidate_id.lower() in str(path).lower():
                matching_files.append(path)
    except OSError:
        return None

    # Prefer files whose names suggest final ATS results.
    preferred = [
        path for path in matching_files
        if "ats" in path.name.lower()
        or "optimized" in path.name.lower()
    ]

    if preferred:
        return sorted(preferred)[0]

    return sorted(matching_files)[0] if matching_files else None



def candidate_ats_score(candidate_id):
    """Load the final ATS score from the correct Day 18 file."""

    base_dir = (
        ROOT
        / "day18_optimization"
        / "results"
        / candidate_id
    )

    path = base_dir / "day18_optimized_ats_score.json"

    if not path.exists():
        return None, None

    score_data = load_json(path)

    if not isinstance(score_data, dict):
        return None, str(path)

    score = read_score_file(
        path,
        [
            "final_ats_score",
            "ats_score",
            "overall_ats_score",
            "score",
        ],
    )

    return score, str(path)

def inspect_ats_coverage(report):
    """Check candidate-level ATS results for candidates 006-013."""

    results = []

    for candidate_id in CANDIDATE_IDS:
        score, source = candidate_ats_score(candidate_id)

        if score is None:
            status = "INCOMPLETE"
            details = "No valid ATS score was found."
        else:
            status = "PASS"
            details = f"Valid ATS score: {score:.2f}/100."

        results.append({
            "candidate_id": candidate_id,
            "status": status,
            "ats_score": score,
            "source": source,
            "details": details,
        })

    complete = sum(
        item["status"] == "PASS" for item in results
    )

    add_check(
        report,
        "Candidate ATS coverage",
        "PASS" if complete == len(results) else "REVIEW_REQUIRED",
        f"{complete}/{len(results)} candidates have valid ATS scores.",
    )

    report["candidate_ats_coverage"] = results


# ---------------------------------------------------------
# CROSS-ROUND SCORE VALIDATION
# ---------------------------------------------------------

def find_cross_round_file(candidate_id):
    """Find a candidate-specific cross-round output file."""

    possible_dirs = [
        ROOT / "day41_cross_round_scoring" / "results",
        ROOT / "day41_cross_round_scoring",
        ROOT / "day41_cross_round_scoring_system" / "results",
        ROOT / "day41_cross_round_scoring_system",
    ]

    for base_dir in possible_dirs:
        if not base_dir.exists():
            continue

        direct = base_dir / f"{candidate_id}.json"

        if direct.is_file():
            return direct

        candidate_dir = base_dir / candidate_id

        if candidate_dir.is_dir():
            files = sorted(candidate_dir.glob("*.json"))

            if files:
                return files[0]

        matches = sorted(
            path for path in base_dir.rglob("*.json")
            if candidate_id.lower() in str(path).lower()
        )

        if matches:
            return matches[0]

    return None



def validate_cross_round_candidate(candidate_id):
    """Validate cross-round scores using the actual Day 41 JSON schema."""

    path = find_cross_round_file(candidate_id)

    if path is None:
        return {
            "candidate_id": candidate_id,
            "status": "INCOMPLETE",
            "missing_fields": [
                "ats_score",
                "hr_score",
                "aptitude_score",
                "cross_round_score",
            ],
            "source": None,
            "details": "Cross-round candidate output not found.",
        }

    data = load_json(path)

    if not isinstance(data, dict) or "_load_error" in data:
        return {
            "candidate_id": candidate_id,
            "status": "INVALID",
            "missing_fields": [],
            "source": str(path),
            "details": "Cross-round output is not valid JSON.",
        }

    # Actual Day 41 structure stores scores inside round_scores.
    round_scores = data.get("round_scores", {})

    if not isinstance(round_scores, dict):
        round_scores = {}

    field_mapping = {
        "ats_score": (round_scores, ["ats"]),
        "hr_score": (round_scores, ["hr"]),
        "aptitude_score": (round_scores, ["aptitude"]),
        "cross_round_score": (
            data,
            ["cross_round_score", "final_cross_round_score"],
        ),
    }

    scores = {}
    missing = []

    for field, (source_data, possible_keys) in field_mapping.items():
        score = find_score(source_data, possible_keys)

        if score is None:
            missing.append(field)
        else:
            scores[field] = score

    if missing:
        status = "INCOMPLETE"
        details = "One or more required cross-round scores are missing."
    else:
        status = "PASS"
        details = "All required cross-round scores are present and valid."

    return {
        "candidate_id": candidate_id,
        "status": status,
        "scores": scores,
        "missing_fields": missing,
        "source": str(path),
        "details": details,
    }

def calculate_cross_round_score(ats, hr, logical, scenario):
    """
    Cross-round formula:
    ATS 30% + HR 30% + mean(logical, scenario) 40%.
    """

    aptitude = (logical + scenario) / 2

    final_score = (
        ats * ROUND_WEIGHTS["ats"]
        + hr * ROUND_WEIGHTS["hr"]
        + aptitude * ROUND_WEIGHTS["aptitude"]
    )

    return round(final_score, 2)


def inspect_cross_round_coverage(report):
    """Report actual cross-round data completeness."""

    results = [
        validate_cross_round_candidate(candidate_id)
        for candidate_id in CANDIDATE_IDS
    ]

    complete = sum(
        item["status"] == "PASS" for item in results
    )

    add_check(
        report,
        "Cross-round data completeness",
        "PASS" if complete == len(results) else "REVIEW_REQUIRED",
        f"{complete}/{len(results)} candidates have all required "
        "cross-round scores in their candidate output.",
    )

    report["cross_round_coverage"] = results


# ---------------------------------------------------------
# WEIGHT VALIDATION
# ---------------------------------------------------------

def validate_weights(report):
    """Ensure configured weights are valid."""

    total = sum(ROUND_WEIGHTS.values())

    valid = (
        all(
            isinstance(weight, (int, float))
            and not isinstance(weight, bool)
            and weight >= 0
            for weight in ROUND_WEIGHTS.values()
        )
        and abs(total - 1.0) < 1e-9
    )

    add_check(
        report,
        "Cross-round weights",
        "PASS" if valid else "FAIL",
        f"Weights: {ROUND_WEIGHTS}; total = {total:.2f}.",
    )


# ---------------------------------------------------------
# REPORT GENERATION
# ---------------------------------------------------------

def determine_overall_status(report):
    """Determine status without hiding review findings."""

    statuses = [
        item["status"] for item in report["checks"]
    ]

    if "FAIL" in statuses:
        return "FAIL"

    if "REVIEW_REQUIRED" in statuses:
        return "PASS_WITH_LIMITATIONS"

    return "PASS"


def write_markdown_report(report):
    """Create a readable Markdown report."""

    lines = [
        "# ZecPath Deliverable 3 - Stability Report",
        "",
        f"- Generated: {report['generated_at']}",
        f"- Overall status: **{report['overall_status']}**",
        "",
        "## Validation checks",
        "",
        "| Check | Status | Details |",
        "|---|---|---|",
    ]

    for item in report["checks"]:
        details = str(item["details"]).replace("|", "\\|")
        lines.append(
            f"| {item['check']} | {item['status']} | {details} |"
        )

    lines.extend([
        "",
        "## Candidate ATS coverage",
        "",
        "| Candidate | Status | ATS score | Details |",
        "|---|---|---:|---|",
    ])

    for item in report.get("candidate_ats_coverage", []):
        score = item.get("ats_score")
        score_text = f"{score:.2f}" if score is not None else "N/A"

        lines.append(
            f"| {item['candidate_id']} | {item['status']} | "
            f"{score_text} | {item['details']} |"
        )

    lines.extend([
        "",
        "## Cross-round coverage",
        "",
        "| Candidate | Status | Missing fields | Details |",
        "|---|---|---|---|",
    ])

    for item in report.get("cross_round_coverage", []):
        missing = ", ".join(item.get("missing_fields", [])) or "None"

        lines.append(
            f"| {item['candidate_id']} | {item['status']} | "
            f"{missing} | {item['details']} |"
        )

    lines.extend([
        "",
        "## Interpretation",
        "",
        "- This checker validates available output files and scores.",
        "- Missing data is reported as incomplete; it is not invented.",
        "- Demo data does not establish real-world hiring accuracy.",
        "- A successful stability check does not prove fairness or "
        "predictive accuracy.",
        "- Human-vs-AI evaluation must be performed and documented "
        "separately.",
        "",
    ])

    MARKDOWN_REPORT.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN_REPORT.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

def inspect_source_round_scores(report):
    """Validate actual HR and aptitude score files."""

    checks = [
        (
            "HR interview score",
            ROOT / "day37_hr_interview_scoring"
            / "results" / "hr_interview_score.json",
            ["final_hr_interview_score", "hr_score"],
        ),
        (
            "Logical reasoning score",
            ROOT / "day38_aptitude_logic"
            / "results" / "logical_reasoning_results.json",
            ["logical_reasoning_score"],
        ),
        (
            "Scenario evaluation score",
            ROOT / "day38_aptitude_logic"
            / "results" / "scenario_evaluation_results.json",
            ["scenario_evaluation_score"],
        ),
    ]

    results = []

    for name, path, score_keys in checks:
        data = load_json(path)

        if not isinstance(data, dict) or "_load_error" in data:
            results.append({
                "check": name,
                "status": "INCOMPLETE",
                "candidate_id": None,
                "score": None,
                "details": "Missing or invalid JSON file.",
            })
            continue

        candidate_id = data.get("candidate_id")
        score = find_score(data, score_keys)

        if score is None:
            status = "INCOMPLETE"
            details = "Valid score not found."
        else:
            status = "PASS"
            details = f"Score: {score:.2f}/100."

        results.append({
            "check": name,
            "status": status,
            "candidate_id": candidate_id,
            "score": score,
            "source": str(path),
            "details": details,
        })

    report["source_round_score_validation"] = results

    complete = sum(
        item["status"] == "PASS" for item in results
    )

    add_check(
        report,
        "HR and aptitude source scores",
        "PASS" if complete == len(results) else "REVIEW_REQUIRED",
        f"{complete}/{len(results)} source score files contain valid scores.",
    )



# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():
    started = time.perf_counter()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    report = {
        "project": "ZecPath",
        "deliverable": "Deliverable 3 - Refined Stability Checker",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "overall_status": "NOT_RUN",
        "round_weights": ROUND_WEIGHTS,
        "checks": [],
        "candidate_ats_coverage": [],
        "cross_round_coverage": [],
    }

    print("=" * 65)
    print("ZecPath - Deliverable 3: Refined Stability Checker")
    print("=" * 65)

    validate_day56_report(report)
    validate_weights(report)
    inspect_ats_coverage(report)
    inspect_source_round_scores(report)
    inspect_cross_round_coverage(report)

    report["execution_time_seconds"] = round(
        time.perf_counter() - started, 3
    )

    report["overall_status"] = determine_overall_status(report)

    save_json(JSON_REPORT, report)
    write_markdown_report(report)

    print("\nVALIDATION RESULTS")
    print("-" * 65)

    for item in report["checks"]:
        print(f"[{item['status']}] {item['check']}")
        print(f"    {item['details']}")

    print("\nCANDIDATE ATS COVERAGE")

    for item in report["candidate_ats_coverage"]:
        score = item.get("ats_score")
        score_text = f"{score:.2f}" if score is not None else "N/A"

        print(
            f"{item['candidate_id']}: {item['status']} "
            f"| ATS score: {score_text}"
        )

    print("\nCROSS-ROUND COVERAGE")

    for item in report["cross_round_coverage"]:
        missing = item.get("missing_fields", [])
        missing_text = ", ".join(missing) if missing else "None"

        print(
            f"{item['candidate_id']}: {item['status']} "
            f"| Missing: {missing_text}"
        )

    print("\n" + "=" * 65)
    print(f"OVERALL STATUS: {report['overall_status']}")
    print(f"Execution time: {report['execution_time_seconds']} seconds")
    print(f"JSON report: {JSON_REPORT}")
    print(f"Markdown report: {MARKDOWN_REPORT}")
    print("=" * 65)

    # A FAIL indicates a broken validation condition.
    # PASS_WITH_LIMITATIONS means review items remain.
    return 1 if report["overall_status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
