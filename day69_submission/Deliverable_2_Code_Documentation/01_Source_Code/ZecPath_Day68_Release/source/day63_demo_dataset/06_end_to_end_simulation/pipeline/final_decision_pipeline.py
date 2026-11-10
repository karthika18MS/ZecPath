
import json
import sys
import time
import importlib.util
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter


# ============================================================
# CONFIGURABLE SIMULATION PATHS
# ============================================================

# This file is stored in:
# 06_end_to_end_simulation/pipeline/final_decision_pipeline.py
SIMULATION_ROOT = Path(__file__).resolve().parents[1]

# Make the simulation root importable when this file is run directly.
if str(SIMULATION_ROOT) not in sys.path:
    sys.path.insert(0, str(SIMULATION_ROOT))

# Locate config_loader.py without assuming that "config" is a package.
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

_CONFIG_SPEC = importlib.util.spec_from_file_location(
    "zecpath_final_decision_config_loader",
    _CONFIG_LOADER_PATH,
)
if _CONFIG_SPEC is None or _CONFIG_SPEC.loader is None:
    raise ImportError(
        f"Could not load configuration module: {_CONFIG_LOADER_PATH}"
    )

_CONFIG_MODULE = importlib.util.module_from_spec(_CONFIG_SPEC)
sys.modules[_CONFIG_SPEC.name] = _CONFIG_MODULE
_CONFIG_SPEC.loader.exec_module(_CONFIG_MODULE)

if not hasattr(_CONFIG_MODULE, "SimulationConfig"):
    raise ImportError(
        f"SimulationConfig class was not found in {_CONFIG_LOADER_PATH}"
    )

SimulationConfig = _CONFIG_MODULE.SimulationConfig
CONFIG = SimulationConfig()

INPUT_FILE = CONFIG.output_dir / "cross_round_pipeline_results.json"
OUTPUT_DIR = CONFIG.output_dir
OUTPUT_FILE = OUTPUT_DIR / "final_decision_pipeline_results.json"

# The engine is in the simulation root in the configurable structure.
ENGINE_FILE = SIMULATION_ROOT / "cross_round_scoring_engine.py"


# ============================================================
# LOAD EXISTING DECISION FUNCTION
# ============================================================

def load_decision_function():

    if not ENGINE_FILE.exists():
        raise FileNotFoundError(
            f"Cross-round engine not found: {ENGINE_FILE}"
        )

    spec = importlib.util.spec_from_file_location(
        "cross_round_scoring_engine",
        ENGINE_FILE
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            "Unable to load cross-round scoring engine."
        )

    engine_module = importlib.util.module_from_spec(spec)

    sys.modules[spec.name] = engine_module

    spec.loader.exec_module(engine_module)

    decision_function = getattr(
        engine_module,
        "determine_final_decision",
        None
    )

    if not callable(decision_function):
        raise AttributeError(
            "determine_final_decision() not found."
        )

    return decision_function


# ============================================================
# LOAD CROSS-ROUND RESULTS
# ============================================================

def load_cross_round_results():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "Cross-round output must be a JSON object."
        )

    if data.get("pipeline_status") != "SUCCESS":
        raise ValueError(
            "Cross-round pipeline was not successful."
        )

    candidates = data.get("candidate_results")

    if not isinstance(candidates, list):
        raise ValueError(
            "candidate_results must be a list."
        )

    return data, candidates


# ============================================================
# VALIDATE CANDIDATE DATA
# ============================================================

def validate_candidate(candidate):

    errors = []

    if not isinstance(candidate, dict):
        return ["Candidate record must be an object."]

    if not candidate.get("candidate_id"):
        errors.append("Missing candidate_id.")

    if not candidate.get("job_id"):
        errors.append("Missing job_id.")

    if not candidate.get("ats_eligibility_status"):
        errors.append("Missing ats_eligibility_status.")

    if not candidate.get("scoring_status"):
        errors.append("Missing scoring_status.")

    return errors


# ============================================================
# PROCESS FINAL DECISIONS
# ============================================================

def process_candidates(candidates, decision_function):

    results = []
    validation_errors = []

    seen_candidates = set()

    for candidate in candidates:

        errors = validate_candidate(candidate)

        if errors:
            validation_errors.append({
                "candidate_id": (
                    candidate.get("candidate_id")
                    if isinstance(candidate, dict)
                    else None
                ),
                "errors": errors
            })
            continue

        candidate_id = candidate["candidate_id"]
        job_id = candidate["job_id"]

        unique_key = (candidate_id, job_id)

        if unique_key in seen_candidates:

            validation_errors.append({
                "candidate_id": candidate_id,
                "job_id": job_id,
                "errors": ["Duplicate candidate/job combination."]
            })
            continue

        seen_candidates.add(unique_key)

        eligibility_status = candidate[
            "ats_eligibility_status"
        ]

        scoring_status = candidate["scoring_status"]

        final_decision = decision_function(
            eligibility_status,
            scoring_status
        )

        result = candidate.copy()

        result["final_decision"] = final_decision

        result["decision_metadata"] = {
            "ats_eligibility_status": eligibility_status,
            "scoring_status": scoring_status,
            "decision_source": (
                "CROSS_ROUND_SCORING_ENGINE"
            ),
            "ats_gate_applied": True
        }

        results.append(result)

    return results, validation_errors


# ============================================================
# BUILD SUMMARY
# ============================================================

def build_summary(results):

    decision_counts = Counter(
        item["final_decision"]
        for item in results
    )

    return {
        "total_candidates": len(results),

        "eligible_for_next_stage": decision_counts.get(
            "ELIGIBLE_FOR_NEXT_STAGE", 0
        ),

        "manual_review": decision_counts.get(
            "MANUAL_REVIEW", 0
        ),

        "not_eligible": decision_counts.get(
            "NOT_ELIGIBLE", 0
        ),

        "blocked_pending_ats": decision_counts.get(
            "BLOCKED_PENDING_ATS", 0
        ),

        "pending_assessments": decision_counts.get(
            "PENDING_ASSESSMENTS", 0
        ),

        "eligible_assessments_incomplete": decision_counts.get(
            "ELIGIBLE_ASSESSMENTS_INCOMPLETE", 0
        ),

        "other_decisions": {
            key: value
            for key, value in decision_counts.items()
            if key not in {
                "ELIGIBLE_FOR_NEXT_STAGE",
                "MANUAL_REVIEW",
                "NOT_ELIGIBLE",
                "BLOCKED_PENDING_ATS",
                "PENDING_ASSESSMENTS",
                "ELIGIBLE_ASSESSMENTS_INCOMPLETE"
            }
        },

        "decision_distribution": dict(decision_counts)
    }


# ============================================================
# SAVE FINAL RESULTS
# ============================================================

def save_results(data):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline():

    start_time = time.time()

    print("\n" + "=" * 65)
    print("ZECPath DAY 63 - FINAL DECISION PIPELINE")
    print("=" * 65)

    try:

        print("\nSTEP 1: LOADING DECISION ENGINE")

        decision_function = load_decision_function()

        print("Decision function loaded successfully.")

        print("\nSTEP 2: LOADING CROSS-ROUND RESULTS")

        source_data, candidates = load_cross_round_results()

        print("Candidates loaded:", len(candidates))

        print("\nSTEP 3: PROCESSING FINAL DECISIONS")

        results, validation_errors = process_candidates(
            candidates,
            decision_function
        )

        for item in results:

            print(
                f'{item["candidate_id"]} | '
                f'{item["job_id"]} | '
                f'{item["final_decision"]}'
            )

        print("\nSTEP 4: BUILDING SUMMARY")

        summary = build_summary(results)

        print(
            "Eligible:",
            summary["eligible_for_next_stage"]
        )

        print(
            "Manual review:",
            summary["manual_review"]
        )

        print(
            "Not eligible:",
            summary["not_eligible"]
        )

        print(
            "Blocked:",
            summary["blocked_pending_ats"]
        )

        print(
            "Pending assessments:",
            summary["pending_assessments"]
        )

        print(
            "Eligible but incomplete:",
            summary["eligible_assessments_incomplete"]
        )

        pipeline_status = (
            "SUCCESS"
            if not validation_errors
            and len(results) == len(candidates)
            else "COMPLETED_WITH_ERRORS"
        )

        output_data = {

            "module": "ZecPath Day 63 Final Decision Pipeline",
            "dataset": {
                "name": CONFIG.dataset_name,
                "type": CONFIG.dataset_type,
                "root": str(CONFIG.dataset_root)
            },

            "pipeline_status": pipeline_status,

            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "execution_time_seconds": round(
                time.time() - start_time,
                3
            ),

            "source_pipeline_status": source_data.get(
                "pipeline_status"
            ),

            "summary": summary,

            "validation": {
                "is_valid": len(validation_errors) == 0,
                "total_input_candidates": len(candidates),
                "processed_candidates": len(results),
                "validation_error_count": len(validation_errors),
                "errors": validation_errors
            },

            "decision_policy": {
                "decision_function": (
                    "determine_final_decision"
                ),
                "decision_logic_source": str(ENGINE_FILE),
                "dataset_name": CONFIG.dataset_name,
                "dataset_type": CONFIG.dataset_type,
                "dataset_root": str(CONFIG.dataset_root),
                "ats_eligibility_is_separate_gate": True,
                "unified_score_cannot_override_ats": True,
                "missing_scores_are_not_zero": True
            },

            "candidate_results": results
        }

        print("\nSTEP 5: SAVING FINAL DECISIONS")

        save_results(output_data)

        print("\n" + "=" * 65)
        print("FINAL DECISION PIPELINE COMPLETED")
        print("=" * 65)

        print("Pipeline status:", pipeline_status)

        print("Total candidates:", len(candidates))

        print("Processed candidates:", len(results))

        print("Validation errors:", len(validation_errors))

        print("\nOutput saved:")
        print(OUTPUT_FILE)

        return output_data

    except Exception as error:

        print("\nFINAL DECISION PIPELINE FAILED")
        print("Error:", str(error))

        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    run_pipeline()
