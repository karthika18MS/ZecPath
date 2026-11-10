
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict
from statistics import mean



# ============================================================
# CONFIGURABLE SIMULATION PATHS
# ============================================================

import sys
import importlib.util

SIMULATION_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = SIMULATION_ROOT.parents[1]

# Locate the shared configuration loader without assuming that
# the config folder is importable as a Python package.
_config_candidates = [
    SIMULATION_ROOT / "config" / "config_loader.py",
    SIMULATION_ROOT / "config_loader.py",
]

_config_file = next((path for path in _config_candidates if path.is_file()), None)

if _config_file is None:
    raise FileNotFoundError(
        "config_loader.py was not found. Checked: "
        + ", ".join(str(path) for path in _config_candidates)
    )

if str(SIMULATION_ROOT) not in sys.path:
    sys.path.insert(0, str(SIMULATION_ROOT))

_spec = importlib.util.spec_from_file_location(
    "_zecpath_simulation_config_loader", _config_file
)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load configuration module: {_config_file}")

_config_module = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _config_module
_spec.loader.exec_module(_config_module)

SimulationConfig = getattr(_config_module, "SimulationConfig", None)
if SimulationConfig is None:
    raise ImportError("SimulationConfig class was not found in config_loader.py")

CONFIG = SimulationConfig()

BASE_DIR = CONFIG.simulation_root
DATASET_ROOT = CONFIG.dataset_root
DATASET_NAME = CONFIG.dataset_name
DATASET_TYPE = CONFIG.dataset_type
OUTPUT_DIR = CONFIG.output_dir


INPUT_FILE = OUTPUT_DIR / "final_decision_pipeline_results.json"
JSON_OUTPUT = OUTPUT_DIR / "batch_report.json"
MARKDOWN_OUTPUT = OUTPUT_DIR / "batch_report.md"

# ============================================================
# LOAD DATA
# ============================================================

def load_final_decisions():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Final decision file not found: {INPUT_FILE}"
        )

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if data.get("pipeline_status") != "SUCCESS":
        raise ValueError(
            "Final decision pipeline did not complete successfully."
        )

    candidates = data.get("candidate_results")

    if not isinstance(candidates, list):
        raise ValueError(
            "Invalid candidate_results structure."
        )

    return data, candidates


# ============================================================
# SCORE STATISTICS
# ============================================================

def calculate_score_statistics(candidates):

    scores = [
        candidate.get("unified_score")
        for candidate in candidates
        if isinstance(candidate.get("unified_score"), (int, float))
        and not isinstance(candidate.get("unified_score"), bool)
    ]

    if not scores:
        return {
            "scored_candidates": 0,
            "average_score": None,
            "highest_score": None,
            "lowest_score": None
        }

    return {
        "scored_candidates": len(scores),
        "average_score": round(mean(scores), 2),
        "highest_score": round(max(scores), 2),
        "lowest_score": round(min(scores), 2)
    }


# ============================================================
# DECISION DISTRIBUTION
# ============================================================

def calculate_decision_distribution(candidates):

    decisions = Counter(
        candidate.get(
            "final_decision",
            "DECISION_UNAVAILABLE"
        )
        for candidate in candidates
    )

    return dict(decisions)


# ============================================================
# JOB-WISE SUMMARY
# ============================================================

def calculate_job_summary(candidates):

    jobs = defaultdict(list)

    for candidate in candidates:

        job_id = candidate.get("job_id", "UNKNOWN")

        jobs[job_id].append(candidate)

    job_summary = {}

    for job_id, records in jobs.items():

        scores = [
            item["unified_score"]
            for item in records
            if isinstance(item.get("unified_score"), (int, float))
            and not isinstance(item.get("unified_score"), bool)
        ]

        decisions = Counter(
            item.get("final_decision", "DECISION_UNAVAILABLE")
            for item in records
        )

        job_summary[job_id] = {

            "total_candidates": len(records),

            "scored_candidates": len(scores),

            "average_unified_score": (
                round(mean(scores), 2)
                if scores else None
            ),

            "decision_distribution": dict(decisions)
        }

    return job_summary


# ============================================================
# ASSESSMENT ROUND STATISTICS
# ============================================================

def calculate_round_statistics(candidates):

    round_names = (
        "ats",
        "hr",
        "aptitude",
        "technical",
        "machine_test"
    )

    statistics = {}

    for round_name in round_names:

        completed = 0
        missing = 0
        other = 0
        scores = []

        for candidate in candidates:

            round_data = candidate.get(
                "round_details", {}
            ).get(round_name, {})

            status = round_data.get(
                "assessment_status",
                "UNKNOWN"
            )

            score = round_data.get("score")

            if status == "COMPLETED" and score is not None:

                completed += 1

                if isinstance(score, (int, float)) and not isinstance(score, bool):
                    scores.append(score)

            elif status in ("NOT_PROVIDED", "INCOMPLETE"):

                missing += 1

            else:

                other += 1

        statistics[round_name] = {

            "completed": completed,

            "missing_or_incomplete": missing,

            "other_status": other,

            "average_score": (
                round(mean(scores), 2)
                if scores else None
            )
        }

    return statistics


# ============================================================
# BUILD BATCH REPORT
# ============================================================

def build_batch_report(source_data, candidates):

    summary = source_data.get("summary", {})

    return {

        "report_type": "BATCH_RECRUITMENT_REPORT",

        "module": "ZecPath Day 63 Batch Reporting",

        "dataset_name": DATASET_NAME,
        "dataset_root": str(DATASET_ROOT),

        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "source_pipeline_status": source_data.get(
            "pipeline_status"
        ),

        "batch_overview": {

            "total_candidates": len(candidates),

            "eligible_for_next_stage": summary.get(
                "eligible_for_next_stage", 0
            ),

            "manual_review": summary.get(
                "manual_review", 0
            ),

            "not_eligible": summary.get(
                "not_eligible", 0
            ),

            "blocked_pending_ats": summary.get(
                "blocked_pending_ats", 0
            ),

            "pending_assessments": summary.get(
                "pending_assessments", 0
            ),

            "eligible_assessments_incomplete": summary.get(
                "eligible_assessments_incomplete", 0
            )
        },

        "score_statistics": calculate_score_statistics(
            candidates
        ),

        "decision_distribution": calculate_decision_distribution(
            candidates
        ),

        "job_wise_summary": calculate_job_summary(
            candidates
        ),

        "assessment_round_statistics": calculate_round_statistics(
            candidates
        ),

        "validation": source_data.get(
            "validation", {}
        ),

        "data_quality_notice": {

            "dataset_type": DATASET_TYPE,

            "is_verified_real_hiring_evaluation": False,

            "notice": (
                "This batch report contains demonstration data. "
                "HR, aptitude, technical and machine-test scores "
                "include simulated assessment outputs. Machine-test "
                "execution and human review scores are illustrative. "
                "This report is not suitable for actual hiring decisions."
            )
        }
    }


# ============================================================
# BUILD MARKDOWN REPORT
# ============================================================

def build_markdown_report(report):

    overview = report["batch_overview"]

    scores = report["score_statistics"]

    lines = [

        "# ZecPath – Recruitment Batch Report",

        "",

        f"**Generated:** {report['generated_at']}",

        f"**Source Pipeline:** {report['source_pipeline_status']}",

        "",

        "## 1. Batch Overview",

        "",

        f"- Total Candidates: {overview['total_candidates']}",

        f"- Eligible for Next Stage: {overview['eligible_for_next_stage']}",

        f"- Manual Review: {overview['manual_review']}",

        f"- Not Eligible: {overview['not_eligible']}",

        f"- Blocked Pending ATS: {overview['blocked_pending_ats']}",

        f"- Pending Assessments: {overview['pending_assessments']}",

        f"- Eligible but Incomplete: {overview['eligible_assessments_incomplete']}",

        "",

        "## 2. Unified Score Statistics",

        "",

        f"- Scored Candidates: {scores['scored_candidates']}",

        f"- Average Score: {scores['average_score']}",

        f"- Highest Score: {scores['highest_score']}",

        f"- Lowest Score: {scores['lowest_score']}",

        "",

        "## 3. Decision Distribution",

        "",

        "| Final Decision | Candidate Count |",

        "|---|---:|"
    ]

    for decision, count in report["decision_distribution"].items():

        lines.append(f"| {decision} | {count} |")

    lines.extend([

        "",

        "## 4. Job-wise Summary",

        "",

        "| Job ID | Candidates | Scored | Average Score |",

        "|---|---:|---:|---:|"
    ])

    for job_id, details in report["job_wise_summary"].items():

        lines.append(

            f"| {job_id} "
            f"| {details['total_candidates']} "
            f"| {details['scored_candidates']} "
            f"| {details['average_unified_score']} |"
        )

    lines.extend([

        "",

        "## 5. Assessment Round Statistics",

        "",

        "| Assessment | Completed | Missing / Incomplete | Other | Average Score |",

        "|---|---:|---:|---:|---:|"
    ])

    for round_name, details in report[
        "assessment_round_statistics"
    ].items():

        lines.append(

            f"| {round_name.upper()} "
            f"| {details['completed']} "
            f"| {details['missing_or_incomplete']} "
            f"| {details['other_status']} "
            f"| {details['average_score']} |"
        )

    lines.extend([

        "",

        "## 6. Validation",

        "",

        f"- Valid: {report['validation'].get('is_valid')}",

        f"- Input Candidates: "
        f"{report['validation'].get('total_input_candidates')}",

        f"- Processed Candidates: "
        f"{report['validation'].get('processed_candidates')}",

        f"- Validation Errors: "
        f"{report['validation'].get('validation_error_count')}",

        "",

        "## 7. Data Quality Notice",

        report["data_quality_notice"]["notice"],

        "",

        "**This is a demonstration report, not a verified real hiring report.**",

        ""
    ])

    return "\n".join(lines)


# ============================================================
# SAVE REPORTS
# ============================================================

def save_reports(report):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        JSON_OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    with open(
        MARKDOWN_OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            build_markdown_report(report)
        )


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_batch_reporting():

    start_time = time.time()

    print("\n" + "=" * 65)

    print("ZECPath DAY 63 - BATCH REPORT GENERATION")

    print("=" * 65)

    source_data, candidates = load_final_decisions()

    print("\nCandidates loaded:", len(candidates))

    report = build_batch_report(
        source_data,
        candidates
    )

    save_reports(report)

    execution_time = round(
        time.time() - start_time,
        3
    )

    print("\nBATCH REPORT SUMMARY")

    for key, value in report["batch_overview"].items():

        print(f"{key}: {value}")

    print("\nScore statistics:")

    for key, value in report["score_statistics"].items():

        print(f"{key}: {value}")

    print("\nAssessment statistics generated.")

    print("\n" + "=" * 65)

    print("BATCH REPORT GENERATION COMPLETED")

    print("=" * 65)

    print("Pipeline status: SUCCESS")
    print("Dataset:", DATASET_NAME)

    print("Total candidates:", len(candidates))

    print("Execution time:", execution_time, "seconds")

    print("\nJSON report saved:")
    print(JSON_OUTPUT)

    print("\nMarkdown report saved:")
    print(MARKDOWN_OUTPUT)

    return report


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    run_batch_reporting()
