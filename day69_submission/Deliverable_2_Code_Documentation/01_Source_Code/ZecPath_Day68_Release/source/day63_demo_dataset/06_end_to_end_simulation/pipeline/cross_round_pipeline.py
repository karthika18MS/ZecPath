import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime


# ============================================================
# CONFIGURABLE SIMULATION PATHS
# ============================================================

SIMULATION_ROOT = Path(__file__).resolve().parents[1]

# Make the simulation root importable when this file is run directly.
if str(SIMULATION_ROOT) not in sys.path:
    sys.path.insert(0, str(SIMULATION_ROOT))

# Locate config_loader.py without assuming it is a Python package.
# Supported locations:
#   1. 06_end_to_end_simulation/config/config_loader.py
#   2. 06_end_to_end_simulation/config_loader.py
import importlib.util

_CONFIG_LOADER_CANDIDATES = [
    SIMULATION_ROOT / "config" / "config_loader.py",
    SIMULATION_ROOT / "config_loader.py",
]

_CONFIG_LOADER_PATH = next(
    (path for path in _CONFIG_LOADER_CANDIDATES if path.is_file()),
    None,
)

if _CONFIG_LOADER_PATH is None:
    searched_locations = "\\n".join(
        f"  - {path}" for path in _CONFIG_LOADER_CANDIDATES
    )
    raise FileNotFoundError(
        "Could not locate config_loader.py. Checked these locations:\\n"
        f"{searched_locations}"
    )

_spec = importlib.util.spec_from_file_location(
    "zecpath_simulation_config_loader",
    _CONFIG_LOADER_PATH,
)
if _spec is None or _spec.loader is None:
    raise ImportError(
        f"Could not load configuration module: {_CONFIG_LOADER_PATH}"
    )

_config_module = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _config_module
_spec.loader.exec_module(_config_module)

if not hasattr(_config_module, "SimulationConfig"):
    raise ImportError(
        f"SimulationConfig class was not found in {_CONFIG_LOADER_PATH}"
    )

SimulationConfig = _config_module.SimulationConfig


def get_simulation_config():
    """Load the shared Day 63 simulation configuration."""
    return SimulationConfig()


CONFIG = get_simulation_config()

ENGINE_FILE = SIMULATION_ROOT / "cross_round_scoring_engine.py"
OUTPUT_DIR = CONFIG.output_dir
ENGINE_OUTPUT = OUTPUT_DIR / "cross_round_scoring_results.json"
PIPELINE_OUTPUT = OUTPUT_DIR / "cross_round_pipeline_results.json"


# ============================================================
# JSON HELPERS
# ============================================================

def load_json(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"Required file not found: {file_path}")

    try:
        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON file: {file_path}. Details: {error}"
        ) from error


def save_json(data, file_path):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# ============================================================
# RUN CROSS-ROUND SCORING ENGINE
# ============================================================

def run_cross_round_engine():
    print("\n" + "=" * 70)
    print("STEP 1: RUNNING CROSS-ROUND SCORING ENGINE")
    print("=" * 70)
    print("Engine:", ENGINE_FILE)
    print("Output:", ENGINE_OUTPUT)

    if not ENGINE_FILE.is_file():
        raise FileNotFoundError(
            f"Cross-round scoring engine not found: {ENGINE_FILE}"
        )

    process = subprocess.run(
        [sys.executable, str(ENGINE_FILE)],
        cwd=str(SIMULATION_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if process.stdout:
        print(process.stdout)

    if process.stderr:
        print("Engine stderr:")
        print(process.stderr)

    if process.returncode != 0:
        raise RuntimeError(
            "Cross-round scoring engine execution failed. "
            f"Exit code: {process.returncode}"
        )

    if not ENGINE_OUTPUT.is_file():
        raise FileNotFoundError(
            "Cross-round engine did not create its expected output: "
            f"{ENGINE_OUTPUT}"
        )

    print("Cross-round engine execution: SUCCESS")


# ============================================================
# VALIDATE CROSS-ROUND OUTPUT
# ============================================================

def validate_cross_round_output(data):
    errors = []

    if not isinstance(data, dict):
        return False, ["Cross-round output must be a JSON object."]

    candidates = data.get("candidate_results")
    if not isinstance(candidates, list):
        return False, ["candidate_results must be a list."]

    if not candidates:
        errors.append("No candidate results found.")

    seen = set()

    for index, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, dict):
            errors.append(f"Candidate record {index} is not an object.")
            continue

        candidate_id = candidate.get("candidate_id")
        job_id = candidate.get("job_id")

        if not isinstance(candidate_id, str) or not candidate_id.strip():
            errors.append(
                f"Candidate record {index} has a missing/invalid candidate_id."
            )
            continue

        if not isinstance(job_id, str) or not job_id.strip():
            errors.append(
                f"{candidate_id}: missing/invalid job_id."
            )
            continue

        key = (candidate_id.strip(), job_id.strip())
        if key in seen:
            errors.append(f"Duplicate candidate/job result: {key}")
        seen.add(key)

        score = candidate.get("unified_score")
        if score is not None:
            if isinstance(score, bool) or not isinstance(score, (int, float)):
                errors.append(f"{candidate_id}: unified score is not numeric.")
            elif not 0 <= score <= 100:
                errors.append(
                    f"{candidate_id}: unified score must be between 0 and 100."
                )

        coverage = candidate.get("score_coverage")
        if coverage is not None:
            if (
                isinstance(coverage, bool)
                or not isinstance(coverage, (int, float))
                or not 0 <= coverage <= 100
            ):
                errors.append(
                    f"{candidate_id}: score_coverage must be between 0 and 100."
                )

    return len(errors) == 0, errors


# ============================================================
# BUILD AND SAVE PIPELINE OUTPUT
# ============================================================

def run_pipeline():
    start_time = time.time()

    print("\n" + "#" * 70)
    print("ZECPath - CONFIGURABLE CROSS-ROUND PIPELINE")
    print("#" * 70)
    print("Dataset:", CONFIG.dataset_name)
    print("Dataset root:", CONFIG.dataset_root)
    print("Simulation root:", SIMULATION_ROOT)
    print("Output directory:", OUTPUT_DIR)

    run_cross_round_engine()
    engine_data = load_json(ENGINE_OUTPUT)

    is_valid, validation_errors = validate_cross_round_output(engine_data)

    engine_status = str(engine_data.get("pipeline_status", "UNKNOWN")).upper()
    accepted_engine_statuses = {"SUCCESS", "SUCCESS_WITH_INPUT_WARNINGS"}

    if not is_valid:
        pipeline_status = "FAILED_VALIDATION"
    elif engine_status not in accepted_engine_statuses:
        pipeline_status = "FAILED"
    elif engine_status == "SUCCESS_WITH_INPUT_WARNINGS":
        pipeline_status = "SUCCESS_WITH_INPUT_WARNINGS"
    else:
        pipeline_status = "SUCCESS"

    candidates = engine_data.get("candidate_results", [])
    summary = engine_data.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}

    # Always reuse the weights actually applied by the scoring engine.
    scoring_weights = engine_data.get("weights", {})
    if not isinstance(scoring_weights, dict):
        scoring_weights = {}

    output = {
        "module": "ZecPath Day 63 Configurable Cross-Round Pipeline",
        "dataset": {
            "name": CONFIG.dataset_name,
            "type": CONFIG.dataset_type,
            "root": str(CONFIG.dataset_root)
        },
        "pipeline_status": pipeline_status,
        "generated_at": datetime.now().astimezone().isoformat(),
        "execution_time_seconds": round(time.time() - start_time, 4),
        "engine_status": engine_status,
        "stages": {
            "engine_execution": "SUCCESS",
            "engine_output_loading": "SUCCESS",
            "output_validation": "SUCCESS" if is_valid else "FAILED",
            "pipeline_report_generation": "SUCCESS"
        },
        "validation": {
            "is_valid": is_valid,
            "total_validation_errors": len(validation_errors),
            "errors": validation_errors
        },
        "summary": summary,
        "candidate_results": candidates,
        "scoring_configuration": {
            "weights": scoring_weights,
            "scoring_method": engine_data.get("scoring_method"),
            "missing_score_policy": engine_data.get("missing_score_policy"),
            "eligibility_policy": engine_data.get("eligibility_policy"),
            "source_engine": str(ENGINE_FILE)
        },
        "input_warnings": engine_data.get("input_warnings", []),
        "source_output": str(ENGINE_OUTPUT)
    }

    save_json(output, PIPELINE_OUTPUT)

    print("\n" + "=" * 70)
    print("CROSS-ROUND PIPELINE SUMMARY")
    print("=" * 70)
    print("Pipeline status:", pipeline_status)
    print("Total candidates:", summary.get("total_candidates"))
    print("Scored candidates:", summary.get("scored_candidates"))
    print("Completed:", summary.get("completed"))
    print("Incomplete:", summary.get("incomplete"))
    print("No scores available:", summary.get("no_scores_available"))
    print("Average unified score:", summary.get("average_unified_score"))
    print("Validation errors:", len(validation_errors))
    print("\nPipeline output saved:")
    print(PIPELINE_OUTPUT)

    if pipeline_status not in accepted_engine_statuses:
        raise RuntimeError(
            "Cross-round pipeline did not complete successfully. "
            "Check the validation errors and source engine status."
        )

    return output


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as error:
        print("\nCROSS-ROUND PIPELINE FAILED")
        print("Error:", str(error))
        raise
