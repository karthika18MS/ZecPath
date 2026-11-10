
"""
ZecPath Day 63/64 - Reusable End-to-End Simulation Orchestrator

Features:
1. Configurable dataset root.
2. Shared configuration loader.
3. Configurable execution timeout.
4. Configurable failure handling.
5. Dataset schema validation before simulation.
6. Dataset validation report generation.
7. Output validation.
8. Duplicate ATS execution prevention.
9. Dependency-aware pipeline execution.
10. Simulation summary and reporting.

Pipeline stages:
ATS_INPUT
ATS_SCORING
ATS
HR
APTITUDE
TECHNICAL
MACHINE_TEST
CROSS_ROUND
FINAL_DECISION
CANDIDATE_REPORT
BATCH_REPORT
PERFORMANCE_REPORT
"""

import json
import sys
import time
import subprocess

from pathlib import Path
from datetime import datetime, timezone


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

PROJECT_DIR = BASE_DIR.parents[1]

PIPELINE_DIR = BASE_DIR / "pipeline"

REPORTING_DIR = BASE_DIR / "reporting"

VALIDATOR_DIR = BASE_DIR / "validators"


# ============================================================
# LOAD SHARED CONFIGURATION
# ============================================================

sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(VALIDATOR_DIR))

from config_loader import SimulationConfig
from input_validator import InputValidator


CONFIG = SimulationConfig()

DATASET_ROOT = CONFIG.dataset_root

DATASET_NAME = CONFIG.dataset_name

DATASET_TYPE = CONFIG.dataset_type

OUTPUT_DIR = CONFIG.output_dir

SUMMARY_FILE = OUTPUT_DIR / "simulation_run_summary.json"

DATASET_VALIDATION_FILE = (
    OUTPUT_DIR / "dataset_validation_report.json"
)

TIMEOUT_SECONDS = CONFIG.timeout_seconds

CONTINUE_ON_FAILURE = CONFIG.continue_on_stage_failure

VALIDATE_OUTPUTS = CONFIG.validate_outputs


# ============================================================
# PIPELINE DEFINITIONS
# ============================================================

STAGES = {

    "ATS_INPUT": {
        "script": PIPELINE_DIR / "ats_input_pipeline.py",
        "output": OUTPUT_DIR / "ats_input_results.json"
    },

    "ATS_SCORING": {
        "script": PIPELINE_DIR / "ats_scoring_pipeline.py",
        "output": OUTPUT_DIR / "ats_scoring_results.json"
    },

    "ATS": {
        "script": PIPELINE_DIR / "ats_pipeline.py",
        "output": OUTPUT_DIR / "ats_pipeline_results.json"
    },

    "HR": {
        "script": PIPELINE_DIR / "hr_pipeline.py",
        "output": OUTPUT_DIR / "hr_pipeline_results.json"
    },

    "APTITUDE": {
        "script": PIPELINE_DIR / "aptitude_pipeline.py",
        "output": OUTPUT_DIR / "aptitude_pipeline_results.json"
    },

    "TECHNICAL": {
        "script": PIPELINE_DIR / "technical_pipeline.py",
        "output": OUTPUT_DIR / "technical_pipeline_results.json"
    },

    "MACHINE_TEST": {
        "script": PIPELINE_DIR / "machine_test_pipeline.py",
        "output": OUTPUT_DIR / "machine_test_pipeline_results.json"
    },

    "CROSS_ROUND": {
        "script": PIPELINE_DIR / "cross_round_pipeline.py",
        "output": OUTPUT_DIR / "cross_round_pipeline_results.json"
    },

    "FINAL_DECISION": {
        "script": PIPELINE_DIR / "final_decision_pipeline.py",
        "output": OUTPUT_DIR / "final_decision_pipeline_results.json"
    },

    "CANDIDATE_REPORT": {
        "script": REPORTING_DIR / "candidate_report.py",
        "output": OUTPUT_DIR / "candidate_results"
    },

    "BATCH_REPORT": {
        "script": REPORTING_DIR / "batch_report.py",
        "output": OUTPUT_DIR / "batch_report.json"
    },

    "PERFORMANCE_REPORT": {
        "script": REPORTING_DIR / "performance_report.py",
        "output": OUTPUT_DIR / "performance_report.json"
    }

}


# ============================================================
# REQUIRED CORE STAGES
# ============================================================

CORE_STAGES = [
    "ATS",
    "HR",
    "APTITUDE",
    "TECHNICAL",
    "MACHINE_TEST"
]


# ============================================================
# JSON VALIDATION
# ============================================================

def validate_json_output(output_file):

    if not output_file.exists():

        return False, "Expected output file does not exist."

    try:

        with open(
            output_file,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if not isinstance(data, dict):

            return False, "Output JSON must contain an object."

        status = data.get(
            "pipeline_status",
            data.get("overall_status")
        )

        if status in (
            "FAILED",
            "FAILED_VALIDATION",
            "COMPLETED_WITH_ERRORS"
        ):

            return False, f"Output pipeline status: {status}"

        return True, "Output JSON validated."

    except json.JSONDecodeError as error:

        return False, f"Invalid JSON: {error}"

    except OSError as error:

        return False, f"Unable to read output: {error}"


# ============================================================
# DATASET SCHEMA VALIDATION
# ============================================================

def run_dataset_validation():

    print("\n" + "=" * 70)
    print("PRE-SIMULATION DATASET VALIDATION")
    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    try:

        validator = InputValidator(
            dataset_root=DATASET_ROOT
        )

        validation_result = validator.validate_dataset()

        validation_status = (
            "PASSED"
            if validation_result.get("overall_valid", False)
            else "INCOMPLETE"
        )

        report = {

            "module": "ZecPath Dataset Schema Validation",

            "dataset_name": DATASET_NAME,

            "dataset_type": DATASET_TYPE,

            "dataset_root": str(DATASET_ROOT),

            "validation_status": validation_status,

            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "validation_result": validation_result

        }

        with open(
            DATASET_VALIDATION_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            "\nDataset validation status:",
            validation_status
        )

        print("\nValidation result:")

        print(
            json.dumps(
                validation_result,
                indent=4,
                ensure_ascii=False
            )
        )

        print("\nValidation report saved:")
        print(DATASET_VALIDATION_FILE)

        if validation_status == "PASSED":

            print("\nDATASET VALIDATION PASSED")

        else:

            print("\nWARNING: DATASET IS INCOMPLETE")

            print(
                "The simulation will continue. "
                "Individual pipelines will handle missing inputs."
            )

        return report

    except Exception as error:

        print("\nDATASET VALIDATION EXECUTION FAILED")

        print("Error:", str(error))

        report = {

            "module": "ZecPath Dataset Schema Validation",

            "dataset_name": DATASET_NAME,

            "dataset_type": DATASET_TYPE,

            "dataset_root": str(DATASET_ROOT),

            "validation_status": "VALIDATION_ERROR",

            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "error": str(error)

        }

        with open(
            DATASET_VALIDATION_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False
            )

        print("\nValidation error report saved:")
        print(DATASET_VALIDATION_FILE)

        return report


# ============================================================
# RUN INDIVIDUAL STAGE
# ============================================================

def run_stage(stage_name):

    configuration = STAGES[stage_name]

    script = configuration["script"]

    expected_output = configuration["output"]

    start_time = time.time()

    print("\n" + "=" * 70)

    print(f"RUNNING STAGE: {stage_name}")

    print("=" * 70)

    result = {

        "stage_name": stage_name,

        "script": str(script),

        "expected_output": str(expected_output),

        "status": "NOT_STARTED",

        "execution_time_seconds": None,

        "return_code": None,

        "error": None

    }

    if not script.exists():

        result["status"] = "SCRIPT_NOT_FOUND"

        result["error"] = str(script)

        return result

    try:

        process = subprocess.run(

            [
                sys.executable,
                str(script)
            ],

            cwd=str(PROJECT_DIR),

            capture_output=True,

            text=True,

            encoding="utf-8",

            errors="replace",

            timeout=TIMEOUT_SECONDS

        )

        print(process.stdout)

        if process.stderr:

            print("\nERROR OUTPUT:")

            print(process.stderr)

        result["return_code"] = process.returncode

        result["execution_time_seconds"] = round(
            time.time() - start_time,
            3
        )

        if process.returncode != 0:

            result["status"] = "FAILED"

            result["error"] = (
                process.stderr[-3000:]
                if process.stderr
                else "Process returned a non-zero exit code."
            )

            return result

        # Validate generated output.

        if expected_output.is_dir():

            files = list(
                expected_output.glob("*.json")
            )

            if not files:

                result["status"] = "OUTPUT_NOT_FOUND"

                result["error"] = (
                    "No candidate JSON reports were generated."
                )

                return result

        elif VALIDATE_OUTPUTS:

            valid, message = validate_json_output(
                expected_output
            )

            if not valid:

                result["status"] = "OUTPUT_VALIDATION_FAILED"

                result["error"] = message

                return result

        result["status"] = "SUCCESS"

        print(f"\n{stage_name} completed successfully.")

    except subprocess.TimeoutExpired:

        result["status"] = "TIMEOUT"

        result["error"] = (
            f"Stage exceeded {TIMEOUT_SECONDS} seconds."
        )

    except Exception as error:

        result["status"] = "FAILED"

        result["error"] = str(error)

    result["execution_time_seconds"] = round(
        time.time() - start_time,
        3
    )

    return result


# ============================================================
# SAVE SIMULATION SUMMARY
# ============================================================

def save_summary(summary):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        SUMMARY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# FAILURE HANDLING
# ============================================================

def should_continue():

    return CONTINUE_ON_FAILURE


def create_skipped_result(stage_name, reason):

    return {

        "stage_name": stage_name,

        "status": "SKIPPED_DEPENDENCY_FAILURE",

        "error": reason

    }


# ============================================================
# MAIN SIMULATION
# ============================================================

def run_simulation():

    simulation_start = time.time()

    stage_results = {}

    print("\n" + "#" * 70)

    print("ZECPath - REUSABLE END-TO-END SIMULATION")

    print("#" * 70)

    print("\nProject directory:", PROJECT_DIR)

    print("Simulation directory:", BASE_DIR)

    print("Dataset name:", DATASET_NAME)

    print("Dataset type:", DATASET_TYPE)

    print("Dataset root:", DATASET_ROOT)

    print("Execution timeout:", TIMEOUT_SECONDS)

    print("Continue on stage failure:", CONTINUE_ON_FAILURE)

    print("Validate outputs:", VALIDATE_OUTPUTS)

    CONFIG.display()

    # --------------------------------------------------------
    # STEP 0: DATASET VALIDATION
    # --------------------------------------------------------

    dataset_validation_report = run_dataset_validation()

    print("\nStarting complete simulation...")

    # --------------------------------------------------------
    # STEP 1: ATS INPUT AND SCORING
    # --------------------------------------------------------

    print("\nSTEP 1: ATS WORKFLOW")

    for stage_name in (
        "ATS_INPUT",
        "ATS_SCORING"
    ):

        stage_results[stage_name] = run_stage(
            stage_name
        )

        if (
            stage_results[stage_name]["status"] != "SUCCESS"
            and not should_continue()
        ):

            break

    # --------------------------------------------------------
    # STEP 2: INTEGRATED ATS PIPELINE
    # --------------------------------------------------------

    ats_prerequisites_success = all(

        stage_results.get(name, {}).get("status") == "SUCCESS"

        for name in (
            "ATS_INPUT",
            "ATS_SCORING"
        )

    )

    if ats_prerequisites_success:

        print("\nSTEP 2: INTEGRATED ATS PIPELINE")

        stage_results["ATS"] = run_stage("ATS")

    else:

        stage_results["ATS"] = create_skipped_result(
            "ATS",
            "ATS input or scoring stage failed."
        )

    # --------------------------------------------------------
    # STEP 3: OTHER ASSESSMENT PIPELINES
    # --------------------------------------------------------

    print("\nSTEP 3: ASSESSMENT PIPELINES")

    for stage_name in (
        "HR",
        "APTITUDE",
        "TECHNICAL",
        "MACHINE_TEST"
    ):

        if (
            not should_continue()
            and any(
                stage_results.get(name, {}).get("status") != "SUCCESS"
                for name in CORE_STAGES
                if name in stage_results
            )
        ):

            stage_results[stage_name] = create_skipped_result(
                stage_name,
                "Stopped because an earlier core stage failed."
            )

            continue

        stage_results[stage_name] = run_stage(
            stage_name
        )

    # --------------------------------------------------------
    # STEP 4: CHECK CORE PIPELINES
    # --------------------------------------------------------

    print("\nSTEP 4: CHECKING CORE PIPELINE RESULTS")

    core_success = all(

        stage_results.get(name, {}).get("status") == "SUCCESS"

        for name in CORE_STAGES

    )

    if core_success:

        print("All core assessment pipelines succeeded.")

    else:

        print("Some core assessment pipelines failed.")

        print("Cross-round scoring will be skipped.")

    # --------------------------------------------------------
    # STEP 5: CROSS-ROUND SCORING
    # --------------------------------------------------------

    if core_success:

        print("\nSTEP 5: CROSS-ROUND SCORING")

        stage_results["CROSS_ROUND"] = run_stage(
            "CROSS_ROUND"
        )

    else:

        stage_results["CROSS_ROUND"] = create_skipped_result(
            "CROSS_ROUND",
            "One or more core pipelines failed."
        )

    # --------------------------------------------------------
    # STEP 6: FINAL DECISION
    # --------------------------------------------------------

    if stage_results["CROSS_ROUND"]["status"] == "SUCCESS":

        print("\nSTEP 6: FINAL DECISION")

        stage_results["FINAL_DECISION"] = run_stage(
            "FINAL_DECISION"
        )

    else:

        stage_results["FINAL_DECISION"] = create_skipped_result(
            "FINAL_DECISION",
            "Cross-round scoring was not successful."
        )

    # --------------------------------------------------------
    # STEP 7: REPORT GENERATION
    # --------------------------------------------------------

    final_success = (

        stage_results["FINAL_DECISION"]["status"] == "SUCCESS"

    )

    reporting_settings = CONFIG.reporting

    if final_success:

        print("\nSTEP 7: REPORT GENERATION")

        if reporting_settings.get(
            "generate_candidate_reports",
            True
        ):

            stage_results["CANDIDATE_REPORT"] = run_stage(
                "CANDIDATE_REPORT"
            )

        else:

            stage_results["CANDIDATE_REPORT"] = {
                "stage_name": "CANDIDATE_REPORT",
                "status": "SKIPPED_BY_CONFIGURATION"
            }

        if reporting_settings.get(
            "generate_batch_report",
            True
        ):

            stage_results["BATCH_REPORT"] = run_stage(
                "BATCH_REPORT"
            )

        else:

            stage_results["BATCH_REPORT"] = {
                "stage_name": "BATCH_REPORT",
                "status": "SKIPPED_BY_CONFIGURATION"
            }

    else:

        print("\nSTEP 7: REPORT GENERATION SKIPPED")

        for name in (
            "CANDIDATE_REPORT",
            "BATCH_REPORT"
        ):

            stage_results[name] = create_skipped_result(
                name,
                "Final decision output is unavailable."
            )

    # --------------------------------------------------------
    # STEP 8: PERFORMANCE REPORT
    # --------------------------------------------------------

    print("\nSTEP 8: PERFORMANCE REPORT")

    if reporting_settings.get(
        "generate_performance_report",
        True
    ):

        stage_results["PERFORMANCE_REPORT"] = run_stage(
            "PERFORMANCE_REPORT"
        )

    else:

        stage_results["PERFORMANCE_REPORT"] = {
            "stage_name": "PERFORMANCE_REPORT",
            "status": "SKIPPED_BY_CONFIGURATION"
        }

    # --------------------------------------------------------
    # STEP 9: BUILD FINAL SUMMARY
    # --------------------------------------------------------

    total_time = round(
        time.time() - simulation_start,
        3
    )

    successful = sum(

        1 for item in stage_results.values()

        if item["status"] == "SUCCESS"

    )

    failed = sum(

        1 for item in stage_results.values()

        if item["status"] in (
            "FAILED",
            "TIMEOUT",
            "OUTPUT_NOT_FOUND",
            "OUTPUT_VALIDATION_FAILED",
            "SCRIPT_NOT_FOUND"
        )

    )

    skipped = sum(

        1 for item in stage_results.values()

        if item["status"].startswith("SKIPPED")

    )

    overall_status = (

        "SUCCESS"

        if (
            successful == len(STAGES)
            and failed == 0
            and skipped == 0
        )

        else "COMPLETED_WITH_WARNINGS"

    )

    summary = {

        "module": "ZecPath Reusable End-to-End Simulation",

        "dataset": {

            "dataset_name": DATASET_NAME,

            "dataset_type": DATASET_TYPE,

            "dataset_root": str(DATASET_ROOT)

        },

        "dataset_validation": {

            "validation_status": dataset_validation_report.get(
                "validation_status",
                "UNKNOWN"
            ),

            "validation_report": str(
                DATASET_VALIDATION_FILE
            )

        },

        "pipeline_status": overall_status,

        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "execution_time_seconds": total_time,

        "execution_configuration": {

            "timeout_seconds": TIMEOUT_SECONDS,

            "continue_on_stage_failure": CONTINUE_ON_FAILURE,

            "validate_outputs": VALIDATE_OUTPUTS

        },

        "statistics": {

            "total_stages": len(STAGES),

            "executed_stages": len(stage_results),

            "successful_stages": successful,

            "failed_stages": failed,

            "skipped_stages": skipped

        },

        "stage_results": stage_results,

        "data_quality_notice": {

            "dataset_type": DATASET_TYPE,

            "is_verified_real_hiring_evaluation": False,

            "notice": (

                "This simulation uses demonstration data. "

                "HR, aptitude, technical and machine-test outputs "

                "include simulated assessment results. "

                "Machine-test execution and human review are illustrative. "

                "Results must not be treated as verified real hiring decisions."

            )

        }

    }

    save_summary(summary)

    # --------------------------------------------------------
    # FINAL TERMINAL REPORT
    # --------------------------------------------------------

    print("\n" + "#" * 70)

    print("ZECPath - SIMULATION SUMMARY")

    print("#" * 70)

    print("\nDataset validation:")

    print(
        dataset_validation_report.get(
            "validation_status",
            "UNKNOWN"
        )
    )

    for name, result in stage_results.items():

        print(
            f"{name:20} | "
            f"{result['status']}"
        )

    print("\nDataset:", DATASET_NAME)

    print("Dataset type:", DATASET_TYPE)

    print("Total stages:", len(STAGES))

    print("Executed stages:", len(stage_results))

    print("Successful stages:", successful)

    print("Failed stages:", failed)

    print("Skipped stages:", skipped)

    print("Total execution time:", total_time, "seconds")

    print("\nOverall pipeline status:", overall_status)

    print("\nDataset validation report:")
    print(DATASET_VALIDATION_FILE)

    print("\nSimulation summary saved:")
    print(SUMMARY_FILE)

    print("\n" + "#" * 70)

    print("END-TO-END SIMULATION FINISHED")

    print("#" * 70)

    return summary


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        run_simulation()

    except Exception as error:

        print("\nSIMULATION FAILED")

        print("Error:", error)

        raise
