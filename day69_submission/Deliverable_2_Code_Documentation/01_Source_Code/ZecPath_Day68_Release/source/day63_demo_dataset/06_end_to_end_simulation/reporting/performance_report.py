
import json
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


JSON_OUTPUT = OUTPUT_DIR / "performance_report.json"
MARKDOWN_OUTPUT = OUTPUT_DIR / "performance_report.md"

# ============================================================
# PIPELINE FILE CONFIGURATION
# ============================================================

PIPELINES = {

    "ATS": "ats_pipeline_results.json",

    "HR": "hr_pipeline_results.json",

    "APTITUDE": "aptitude_pipeline_results.json",

    "TECHNICAL": "technical_pipeline_results.json",

    "MACHINE_TEST": "machine_test_pipeline_results.json",

    "CROSS_ROUND": "cross_round_pipeline_results.json",

    "FINAL_DECISION": "final_decision_pipeline_results.json"
}


# ============================================================
# LOAD JSON FILE
# ============================================================

def load_json_file(file_path):

    if not file_path.exists():
        return None

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return None


# ============================================================
# EXTRACT PIPELINE STATUS
# ============================================================

def get_pipeline_status(data):

    if not isinstance(data, dict):
        return "INVALID_OUTPUT"

    return data.get(
        "pipeline_status",
        data.get(
            "overall_status",
            data.get("status", "STATUS_NOT_AVAILABLE")
        )
    )


# ============================================================
# EXTRACT CANDIDATE COUNT
# ============================================================

def get_candidate_count(data):

    if not isinstance(data, dict):
        return None

    summary = data.get("summary", {})

    if isinstance(summary, dict):

        for key in (
            "total_candidates",
            "total_candidate_count",
            "candidates_processed"
        ):

            if isinstance(summary.get(key), int):
                return summary[key]

    for key in (
        "candidate_results",
        "candidates"
    ):

        records = data.get(key)

        if isinstance(records, list):
            return len(records)

    return None


# ============================================================
# EXTRACT VALIDATION ERRORS
# ============================================================

def get_validation_errors(data):

    if not isinstance(data, dict):
        return None

    validation = data.get("validation", {})

    if isinstance(validation, dict):

        for key in (
            "validation_error_count",
            "error_count",
            "total_errors"
        ):

            value = validation.get(key)

            if isinstance(value, int):
                return value

        errors = validation.get("errors")

        if isinstance(errors, list):
            return len(errors)

    errors = data.get("errors")

    if isinstance(errors, list):
        return len(errors)

    return None


# ============================================================
# EXTRACT EXECUTION TIME
# ============================================================

def get_execution_time(data):

    if not isinstance(data, dict):
        return None

    value = data.get("execution_time_seconds")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return round(value, 3)

    return None


# ============================================================
# ANALYZE INDIVIDUAL PIPELINES
# ============================================================

def analyze_pipelines():

    results = []

    for pipeline_name, filename in PIPELINES.items():

        file_path = OUTPUT_DIR / filename

        data = load_json_file(file_path)

        if data is None:

            results.append({

                "pipeline_name": pipeline_name,

                "output_file": filename,

                "status": "OUTPUT_NOT_AVAILABLE",

                "candidate_count": None,

                "execution_time_seconds": None,

                "validation_errors": None,

                "output_exists": file_path.exists()

            })

            continue

        results.append({

            "pipeline_name": pipeline_name,

            "output_file": filename,

            "status": get_pipeline_status(data),

            "candidate_count": get_candidate_count(data),

            "execution_time_seconds": get_execution_time(data),

            "validation_errors": get_validation_errors(data),

            "output_exists": True

        })

    return results


# ============================================================
# CALCULATE OVERALL PERFORMANCE
# ============================================================

def calculate_overall_performance(results):

    total = len(results)

    successful = sum(
        1 for item in results
        if item["status"] == "SUCCESS"
    )

    failed = sum(
        1 for item in results
        if item["status"] in (
            "FAILED",
            "FAILED_VALIDATION",
            "INVALID_OUTPUT"
        )
    )

    unavailable = sum(
        1 for item in results
        if item["status"] == "OUTPUT_NOT_AVAILABLE"
    )

    known_times = [
        item["execution_time_seconds"]
        for item in results
        if item["execution_time_seconds"] is not None
    ]

    known_errors = [
        item["validation_errors"]
        for item in results
        if item["validation_errors"] is not None
    ]

    return {

        "total_pipelines": total,

        "successful_pipelines": successful,

        "failed_pipelines": failed,

        "unavailable_pipelines": unavailable,

        "other_status_pipelines": (
            total - successful - failed - unavailable
        ),

        "known_execution_time_count": len(known_times),

        "total_reported_execution_time_seconds": round(
            sum(known_times), 3
        ),

        "total_known_validation_errors": sum(known_errors),

        "pipelines_with_execution_time": len(known_times),

        "pipelines_with_validation_metrics": len(known_errors)
    }


# ============================================================
# BUILD PERFORMANCE REPORT
# ============================================================

def build_performance_report(results):

    overall = calculate_overall_performance(results)

    return {

        "module": "ZecPath Day 63 Performance Reporting",

        "dataset_name": DATASET_NAME,
        "dataset_root": str(DATASET_ROOT),

        "report_type": "PIPELINE_PERFORMANCE_REPORT",

        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "pipeline_status": (
            "SUCCESS"
            if overall["failed_pipelines"] == 0
            and overall["unavailable_pipelines"] == 0
            and overall["other_status_pipelines"] == 0
            else "COMPLETED_WITH_WARNINGS"
        ),

        "overall_performance": overall,

        "pipeline_details": results,

        "measurement_notes": {

            "execution_time": (
                "Uses execution_time_seconds recorded by each "
                "pipeline. Missing timings are not estimated."
            ),

            "validation_errors": (
                "Counts are taken from each pipeline output when "
                "available. Missing validation metrics are not "
                "assumed to be zero."
            ),

            "dataset_type": DATASET_TYPE,

            "hiring_evaluation_verified": False,

            "notice": (
                "This report monitors demo pipeline execution. "
                "It does not establish the accuracy of assessment "
                "scores or verify real candidate performance."
            )
        }
    }


# ============================================================
# BUILD MARKDOWN REPORT
# ============================================================

def build_markdown_report(report):

    overall = report["overall_performance"]

    lines = [

        "# ZecPath – Pipeline Performance Report",

        "",

        f"**Generated:** {report['generated_at']}",

        f"**Report Status:** {report['pipeline_status']}",

        "",

        "## 1. Overall Performance",

        "",

        f"- Total Pipelines: {overall['total_pipelines']}",

        f"- Successful Pipelines: {overall['successful_pipelines']}",

        f"- Failed Pipelines: {overall['failed_pipelines']}",

        f"- Unavailable Pipelines: {overall['unavailable_pipelines']}",

        f"- Other Status Pipelines: {overall['other_status_pipelines']}",

        f"- Total Reported Execution Time: "
        f"{overall['total_reported_execution_time_seconds']} seconds",

        f"- Known Validation Errors: "
        f"{overall['total_known_validation_errors']}",

        "",

        "## 2. Individual Pipeline Details",

        "",

        "| Pipeline | Status | Candidates | Execution Time (s) | Validation Errors |",

        "|---|---|---:|---:|---:|"
    ]

    for item in report["pipeline_details"]:

        lines.append(

            f"| {item['pipeline_name']} "
            f"| {item['status']} "
            f"| {item['candidate_count']} "
            f"| {item['execution_time_seconds']} "
            f"| {item['validation_errors']} |"
        )

    lines.extend([

        "",

        "## 3. Measurement Notes",

        "",

        report["measurement_notes"]["execution_time"],

        "",

        report["measurement_notes"]["validation_errors"],

        "",

        "## 4. Data Quality Notice",

        report["measurement_notes"]["notice"],

        "",

        "**This is a demonstration performance report, "
        "not a verified real hiring evaluation.**",

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
# MAIN
# ============================================================

def run_performance_reporting():

    start_time = time.time()

    print("\n" + "=" * 65)

    print("ZECPath DAY 63 - PERFORMANCE REPORT GENERATION")

    print("=" * 65)

    results = analyze_pipelines()

    report = build_performance_report(results)

    save_reports(report)

    overall = report["overall_performance"]

    print("\nPIPELINE PERFORMANCE SUMMARY")

    for key, value in overall.items():

        print(f"{key}: {value}")

    print("\nINDIVIDUAL PIPELINE STATUS")

    for item in results:

        print(
            f"{item['pipeline_name']} | "
            f"{item['status']} | "
            f"Candidates: {item['candidate_count']} | "
            f"Time: {item['execution_time_seconds']}"
        )

    execution_time = round(
        time.time() - start_time,
        3
    )

    print("\n" + "=" * 65)

    print("PERFORMANCE REPORT GENERATION COMPLETED")

    print("=" * 65)

    print("Report status:", report["pipeline_status"])
    print("Dataset:", DATASET_NAME)

    print("Execution time:", execution_time, "seconds")

    print("\nJSON report:")
    print(JSON_OUTPUT)

    print("\nMarkdown report:")
    print(MARKDOWN_OUTPUT)

    return report


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    run_performance_reporting()
