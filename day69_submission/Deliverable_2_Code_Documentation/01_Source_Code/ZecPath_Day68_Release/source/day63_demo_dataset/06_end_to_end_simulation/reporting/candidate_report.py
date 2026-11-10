
import json
import re
import time
from pathlib import Path
from datetime import datetime, timezone



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
CANDIDATE_OUTPUT_DIR = OUTPUT_DIR / "candidate_results"

# ============================================================
# LOAD FINAL DECISION DATA
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
            "Final decision pipeline is not successful."
        )

    candidates = data.get("candidate_results")

    if not isinstance(candidates, list):
        raise ValueError(
            "Invalid candidate_results structure."
        )

    return data, candidates


# ============================================================
# BUILD CANDIDATE REPORT
# ============================================================

def build_candidate_report(candidate):

    round_details = candidate.get("round_details", {})

    round_reports = {}

    for round_name, details in round_details.items():

        provenance = details.get("provenance", {})

        round_reports[round_name] = {

            "score": details.get("score"),

            "weight": details.get("weight"),

            "assessment_status": details.get(
                "assessment_status",
                "UNKNOWN"
            ),

            "provenance": provenance
        }

    return {

        "report_type": "INDIVIDUAL_CANDIDATE_REPORT",

        "dataset_name": DATASET_NAME,
        "dataset_root": str(DATASET_ROOT),

        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "candidate_information": {

            "candidate_id": candidate.get("candidate_id"),

            "job_id": candidate.get("job_id")
        },

        "assessment_summary": {

            "round_details": round_reports,

            "unified_score": candidate.get("unified_score"),

            "score_coverage": candidate.get("score_coverage"),

            "available_weight": candidate.get("available_weight"),

            "available_rounds": candidate.get(
                "available_rounds", []
            ),

            "missing_rounds": candidate.get(
                "missing_rounds", []
            ),

            "scoring_status": candidate.get(
                "scoring_status"
            )
        },

        "eligibility_evaluation": {

            "ats_eligibility_status": candidate.get(
                "ats_eligibility_status"
            ),

            "final_decision": candidate.get(
                "final_decision"
            ),

            "decision_metadata": candidate.get(
                "decision_metadata", {}
            )
        },

        "data_quality_notice": {

            "dataset_type": DATASET_TYPE,

            "is_verified_real_hiring_evaluation": False,

            "notice": (
                "This report contains demonstration assessment "
                "outputs. Several assessment scores are simulated "
                "and must not be treated as verified real hiring results."
            )
        }
    }


# ============================================================
# BUILD MARKDOWN REPORT
# ============================================================

def build_markdown_report(report):

    candidate = report["candidate_information"]

    assessment = report["assessment_summary"]

    eligibility = report["eligibility_evaluation"]

    lines = [

        "# Individual Candidate Report",

        "",

        f"**Candidate ID:** {candidate['candidate_id']}",

        f"**Job ID:** {candidate['job_id']}",

        f"**Generated:** {report['generated_at']}",

        "",

        "## Assessment Summary",

        "",

        f"- Unified Score: {assessment['unified_score']}",

        f"- Score Coverage: {assessment['score_coverage']}%",

        f"- Scoring Status: {assessment['scoring_status']}",

        f"- Available Rounds: {', '.join(assessment['available_rounds']) or 'None'}",

        f"- Missing Rounds: {', '.join(assessment['missing_rounds']) or 'None'}",

        "",

        "## Round-wise Scores",

        "",

        "| Assessment | Score | Weight | Status |",

        "|---|---:|---:|---|"
    ]

    for name, details in assessment["round_details"].items():

        score = details["score"]

        score_text = (
            str(score)
            if score is not None
            else "Not available"
        )

        weight = details["weight"]

        status = details["assessment_status"]

        lines.append(
            f"| {name.upper()} | {score_text} | {weight} | {status} |"
        )

    lines.extend([

        "",

        "## Eligibility Evaluation",

        "",

        f"- ATS Eligibility: {eligibility['ats_eligibility_status']}",

        f"- Final Decision: {eligibility['final_decision']}",

        f"- ATS Gate Applied: "
        f"{eligibility['decision_metadata'].get('ats_gate_applied')}",

        "",

        "## Data Quality Notice",

        report["data_quality_notice"]["notice"],

        "",

        "**This report is for demonstration purposes only. "
        "It is not a verified real hiring evaluation.**",

        ""
    ])

    return "\n".join(lines)


# ============================================================
# SAVE REPORTS
# ============================================================

def save_candidate_report(report):

    candidate_id = report[
        "candidate_information"
    ]["candidate_id"]

    job_id = report[
        "candidate_information"
    ]["job_id"]

    safe_candidate_id = re.sub(
        r"[^A-Za-z0-9_-]",
        "_",
        str(candidate_id)
    )

    safe_job_id = re.sub(
        r"[^A-Za-z0-9_-]",
        "_",
        str(job_id)
    )

    filename = f"{safe_candidate_id}_{safe_job_id}"

    json_path = CANDIDATE_OUTPUT_DIR / f"{filename}.json"

    markdown_path = CANDIDATE_OUTPUT_DIR / f"{filename}.md"

    with open(
        json_path,
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
        markdown_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(build_markdown_report(report))

    return json_path, markdown_path


# ============================================================
# RUN CANDIDATE REPORT GENERATION
# ============================================================

def run_candidate_reporting():

    start_time = time.time()

    print("\n" + "=" * 65)

    print("ZECPath DAY 63 - CANDIDATE REPORT GENERATION")

    print("=" * 65)

    CANDIDATE_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    source_data, candidates = load_final_decisions()

    print("\nCandidates loaded:", len(candidates))

    successful = 0

    failed = 0

    errors = []

    for candidate in candidates:

        try:

            report = build_candidate_report(candidate)

            json_path, markdown_path = save_candidate_report(
                report
            )

            successful += 1

            print(
                f"{candidate['candidate_id']} | "
                f"Report generated successfully"
            )

        except Exception as error:

            failed += 1

            errors.append({

                "candidate_id": candidate.get("candidate_id"),

                "error": str(error)
            })

            print(
                f"{candidate.get('candidate_id')} | "
                f"FAILED: {error}"
            )

    execution_time = round(
        time.time() - start_time,
        3
    )

    print("\n" + "=" * 65)

    print("CANDIDATE REPORTING COMPLETED")

    print("=" * 65)

    print("Total candidates:", len(candidates))

    print("Reports generated:", successful)

    print("Failed reports:", failed)

    print("Execution time:", execution_time, "seconds")

    print("Output directory:", CANDIDATE_OUTPUT_DIR)

    print("Source pipeline:", source_data["pipeline_status"])
    print("Dataset:", DATASET_NAME)

    if errors:
        print("\nErrors:")
        print(json.dumps(errors, indent=4))

    return {

        "pipeline_status": (
            "SUCCESS" if failed == 0 else "COMPLETED_WITH_ERRORS"
        ),

        "total_candidates": len(candidates),

        "reports_generated": successful,

        "failed_reports": failed,

        "execution_time_seconds": execution_time,

        "errors": errors
    }


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    run_candidate_reporting()
