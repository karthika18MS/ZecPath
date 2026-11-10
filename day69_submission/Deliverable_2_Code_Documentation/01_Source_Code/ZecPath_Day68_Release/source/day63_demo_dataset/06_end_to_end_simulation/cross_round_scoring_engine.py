import json
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter


# ============================================================
# ZecPath Day 63 - CONFIGURABLE CROSS-ROUND SCORING ENGINE
# ============================================================

SIMULATION_ROOT = Path(__file__).resolve().parent
if str(SIMULATION_ROOT) not in sys.path:
    sys.path.insert(0, str(SIMULATION_ROOT))

try:
    from config_loader import SimulationConfig
except ImportError:
    try:
        from config.config_loader import SimulationConfig
    except ImportError as error:
        raise ImportError(
            "Could not import SimulationConfig. Ensure config_loader.py "
            "is available in the simulation root/config folder."
        ) from error


def initialize_configuration(dataset_root=None):
    """Load shared simulation configuration and build all runtime paths."""
    if dataset_root:
        simulation_config = SimulationConfig(dataset_root=dataset_root)
    else:
        simulation_config = SimulationConfig()

    simulation_root = Path(simulation_config.simulation_root)
    output_dir = Path(simulation_config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    config_file = simulation_root / "config" / "cross_round_weights.json"
    results_dir = simulation_root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    # These are the actual output filenames used by the Day 63 pipelines.
    input_files = {
        "ats": output_dir / "ats_pipeline_results.json",
        "hr": output_dir / "hr_pipeline_results.json",
        "aptitude": output_dir / "aptitude_pipeline_results.json",
        "technical": output_dir / "technical_pipeline_results.json",
        "machine_test": output_dir / "machine_test_pipeline_results.json"
    }

    output_file = output_dir / "cross_round_scoring_results.json"
    legacy_output_file = results_dir / "cross_round_scoring_results.json"

    return {
        "simulation_config": simulation_config,
        "simulation_root": simulation_root,
        "dataset_root": Path(simulation_config.dataset_root),
        "output_dir": output_dir,
        "config_file": config_file,
        "results_dir": results_dir,
        "input_files": input_files,
        "output_file": output_file,
        "legacy_output_file": legacy_output_file
    }


# ============================================================
# SCORE FIELD ALIASES
# ============================================================

SCORE_FIELDS = {
    "ats": [
        "final_ats_score",
        "ats_score",
        "scores.final_ats_score"
    ],

    "hr": [
        "hr_score",
        "final_hr_score"
    ],

    "aptitude": [
        "aptitude_score",
        "final_aptitude_score"
    ],

    "technical": [
        "technical_score",
        "final_technical_score"
    ],

    "machine_test": [
        "machine_test_score",
        "final_machine_test_score",
        "machine_score",
        "final_score"
    ]
}


# ============================================================
# JSON HELPERS
# ============================================================

def load_json(file_path):
    """Load and validate a JSON file."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}"
        )

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON file: {file_path}\n{error}"
        )


def get_nested_value(data, field_path):
    """Read a nested JSON value using dot notation."""

    value = data

    for key in field_path.split("."):

        if not isinstance(value, dict):
            return None

        value = value.get(key)

    return value


def get_valid_score(value):
    """Accept numeric scores between 0 and 100."""

    if isinstance(value, bool):
        return None

    if not isinstance(value, (int, float)):
        return None

    if not 0 <= value <= 100:
        return None

    return round(float(value), 2)


def get_score(candidate, round_name):
    """Extract a score using the configured field aliases."""

    for field in SCORE_FIELDS[round_name]:

        value = get_nested_value(candidate, field)

        score = get_valid_score(value)

        if score is not None:
            return score

    return None


def get_candidate_key(candidate):
    """Create a unique candidate/job combination."""

    candidate_id = candidate.get("candidate_id")
    job_id = candidate.get("job_id")

    if not candidate_id or not job_id:
        return None

    return (
        str(candidate_id).strip(),
        str(job_id).strip()
    )


# ============================================================
# ASSESSMENT STATUS
# ============================================================

def get_assessment_status(candidate, round_name):
    """Extract the assessment status."""

    status_fields = [
        "assessment_status",
        "status",
        "score_status",
        "pipeline_status"
    ]

    for field in status_fields:

        value = candidate.get(field)

        if value is not None:
            return str(value).upper()

    if get_score(candidate, round_name) is not None:
        return "COMPLETED"

    return "NOT_PROVIDED"


# ============================================================
# PROVENANCE EXTRACTION
# ============================================================

def get_provenance(candidate, pipeline_data, round_name):
    """
    Preserve provenance from candidate-level and
    pipeline-level metadata.

    Machine-test metadata is stored partly at pipeline level
    in the Day 63 machine-test pipeline output.
    """

    scoring_policy = pipeline_data.get(
        "scoring_policy", {}
    )

    data_provenance = pipeline_data.get(
        "data_provenance", {}
    )

    if not isinstance(scoring_policy, dict):
        scoring_policy = {}

    if not isinstance(data_provenance, dict):
        data_provenance = {}

    is_simulated = candidate.get(
        "is_simulated",
        pipeline_data.get("is_simulated")
    )

    score_source = (
        candidate.get("score_source")
        or candidate.get("score_origin")
        or candidate.get("data_provenance")
        or pipeline_data.get("score_source")
        or pipeline_data.get("score_type")
    )

    provenance = {
        "is_simulated": is_simulated,
        "score_source": score_source
    }

    # --------------------------------------------------------
    # MACHINE TEST PROVENANCE
    # --------------------------------------------------------

    if round_name == "machine_test":

        candidate_provenance = candidate.get(
            "data_provenance"
        )

        # The Day 63 machine-test dataset is explicitly
        # identified as simulated demo data.
        provenance.update({

            "is_simulated": True,

            "score_source": (
                candidate_provenance
                or data_provenance.get("data_type")
                or "SIMULATED_DEMO_DATA"
            ),

            "test_results_are_simulated": (
                scoring_policy.get(
                    "test_results_are_simulated"
                )
            ),

            "review_scores_are_simulated": (
                scoring_policy.get(
                    "review_scores_are_simulated"
                )
            ),

            "is_verified_real_candidate_result": (
                candidate.get(
                    "is_verified_real_candidate_result",
                    False
                )
            )
        })

    return provenance


# ============================================================
# ATS ELIGIBILITY EXTRACTION
# ============================================================

def get_eligibility_status(candidate):
    """Extract ATS eligibility without changing its value."""

    possible_fields = [
        "eligibility_status",
        "eligibility.status",
        "eligibility.eligibility_status",
        "final_eligibility_status"
    ]

    for field in possible_fields:

        value = get_nested_value(candidate, field)

        if value is not None:
            return str(value).strip().upper()

    return None


# ============================================================
# PIPELINE VALIDATION
# ============================================================

def inspect_pipeline_status(pipeline_data, round_name):
    """Collect pipeline and validation warnings."""

    warnings = []

    pipeline_status = str(
        pipeline_data.get("pipeline_status", "UNKNOWN")
    ).upper()

    if pipeline_status != "SUCCESS":

        warnings.append(
            f"{round_name.upper()} pipeline status: "
            f"{pipeline_status}"
        )

    validation = pipeline_data.get("validation", {})

    if not isinstance(validation, dict):
        validation = {}

    is_valid = validation.get("is_valid")

    validation_status = str(
        validation.get("status", "")
    ).upper()

    errors = validation.get("errors", [])

    if is_valid is False or validation_status in (
        "FAILED",
        "FAILED_VALIDATION",
        "INVALID"
    ):

        warnings.append(
            f"{round_name.upper()} validation failed"
        )

    if errors:

        warnings.append(
            f"{round_name.upper()} has "
            f"{len(errors)} validation error(s)"
        )

    return warnings


# ============================================================
# LOAD ONE ASSESSMENT ROUND
# ============================================================

def load_round_data(round_name, file_path):

    print(f"\nLoading {round_name.upper()} results...")

    pipeline_data = load_json(file_path)

    candidate_list = pipeline_data.get("candidate_results")

    if not isinstance(candidate_list, list):

        raise ValueError(
            f"{round_name}: candidate_results "
            "must be a JSON list."
        )

    records = {}

    for candidate in candidate_list:

        if not isinstance(candidate, dict):

            raise ValueError(
                f"{round_name}: Invalid candidate record."
            )

        key = get_candidate_key(candidate)

        if key is None:

            raise ValueError(
                f"{round_name}: Missing candidate_id or job_id."
            )

        if key in records:

            raise ValueError(
                f"{round_name}: Duplicate candidate/job "
                f"record found: {key}"
            )

        score = get_score(candidate, round_name)

        records[key] = {
            "score": score,

            "assessment_status": get_assessment_status(
                candidate,
                round_name
            ),

            "provenance": get_provenance(
                candidate,
                pipeline_data,
                round_name
            )
        }

        if round_name == "ats":

            records[key]["eligibility_status"] = (
                get_eligibility_status(candidate)
            )

    print(
        f"{round_name.upper()} candidates loaded: "
        f"{len(records)}"
    )

    return pipeline_data, records


# ============================================================
# CONFIGURATION VALIDATION
# ============================================================

def load_configuration(config_file):

    config = load_json(config_file)

    weights = config.get("weights", {})

    required_rounds = [
        "ats",
        "hr",
        "aptitude",
        "technical",
        "machine_test"
    ]

    if set(weights.keys()) != set(required_rounds):

        raise ValueError(
            "Configuration must contain exactly: "
            + ", ".join(required_rounds)
        )

    for round_name, weight in weights.items():

        if isinstance(weight, bool) or not isinstance(
            weight, (int, float)
        ):

            raise ValueError(
                f"Invalid weight for {round_name}"
            )

        if weight < 0 or weight > 1:

            raise ValueError(
                f"Weight for {round_name} "
                "must be between 0 and 1."
            )

    total_weight = sum(weights.values())

    if abs(total_weight - 1.0) > 0.000001:

        raise ValueError(
            f"Weights must total 1.0. "
            f"Current total: {total_weight}"
        )

    return config


# ============================================================
# UNIFIED SCORE CALCULATION
# ============================================================

def calculate_unified_score(
    candidate_rounds,
    weights,
    precision
):
    """
    Calculate weighted score using available rounds only.

    Missing scores are never treated as zero.

    Score coverage represents the percentage of the original
    assessment weight available for this candidate.
    """

    weighted_total = 0.0

    available_weight = 0.0

    available_rounds = []

    missing_rounds = []

    round_scores = {}

    for round_name, weight in weights.items():

        round_data = candidate_rounds.get(
            round_name,
            {}
        )

        score = round_data.get("score")

        round_scores[round_name] = score

        if score is None:

            missing_rounds.append(round_name)

            continue

        weighted_total += score * weight

        available_weight += weight

        available_rounds.append(round_name)

    # No available assessment scores.

    if available_weight == 0:

        return {
            "unified_score": None,
            "score_coverage": 0.0,
            "available_weight": 0.0,
            "available_rounds": [],
            "missing_rounds": list(weights.keys()),
            "round_scores": round_scores,
            "scoring_status": "NO_SCORES_AVAILABLE"
        }

    # Normalize using available assessment weights.

    unified_score = (
        weighted_total / available_weight
    )

    score_coverage = (
        available_weight * 100
    )

    if missing_rounds:
        scoring_status = "INCOMPLETE"
    else:
        scoring_status = "COMPLETED"

    return {
        "unified_score": round(
            unified_score,
            precision
        ),

        "score_coverage": round(
            score_coverage,
            2
        ),

        "available_weight": round(
            available_weight,
            4
        ),

        "available_rounds": available_rounds,

        "missing_rounds": missing_rounds,

        "round_scores": round_scores,

        "scoring_status": scoring_status
    }


# ============================================================
# FINAL DECISION
# ============================================================

def determine_final_decision(
    eligibility_status,
    scoring_status
):
    """
    ATS eligibility remains a separate hiring gate.
    Unified score never overrides ATS eligibility.
    """

    if not eligibility_status:

        return "ELIGIBILITY_STATUS_UNAVAILABLE"

    status = eligibility_status.upper()

    if status == "REJECTED":

        return "NOT_ELIGIBLE"

    if status in ("BLOCKED", "BLOCKED_PENDING_ATS"):

        return "BLOCKED_PENDING_ATS"

    if status in ("REVIEW", "MANUAL_REVIEW"):

        return "MANUAL_REVIEW"

    if status == "ELIGIBLE":

        if scoring_status == "NO_SCORES_AVAILABLE":

            return "PENDING_ASSESSMENTS"

        if scoring_status == "INCOMPLETE":

            return "ELIGIBLE_ASSESSMENTS_INCOMPLETE"

        return "ELIGIBLE_FOR_NEXT_STAGE"

    return "ELIGIBILITY_STATUS_REQUIRES_REVIEW"


# ============================================================
# BUILD ROUND DETAILS
# ============================================================

def build_round_details(candidate_rounds, weights):

    details = {}

    for round_name, weight in weights.items():

        round_data = candidate_rounds.get(
            round_name,
            {}
        )

        details[round_name] = {

            "weight": weight,

            "score": round_data.get("score"),

            "assessment_status": round_data.get(
                "assessment_status",
                "NOT_FOUND"
            ),

            "provenance": round_data.get(
                "provenance",
                {}
            )
        }

    return details


# ============================================================
# OVERALL PIPELINE STATUS
# ============================================================

def determine_pipeline_status(
    pipeline_metadata,
    input_warnings
):
    """
    Report SUCCESS only when all input pipelines have
    successful status and no validation failures.
    """

    if input_warnings:
        return "SUCCESS_WITH_INPUT_WARNINGS"

    for metadata in pipeline_metadata.values():

        if metadata.get("pipeline_status") != "SUCCESS":

            return "SUCCESS_WITH_INPUT_WARNINGS"

        validation = metadata.get("validation", {})

        if isinstance(validation, dict):

            if validation.get("is_valid") is False:
                return "SUCCESS_WITH_INPUT_WARNINGS"

            if str(
                validation.get("status", "")
            ).upper() in (
                "FAILED",
                "FAILED_VALIDATION",
                "INVALID"
            ):
                return "SUCCESS_WITH_INPUT_WARNINGS"

    return "SUCCESS"


# ============================================================
# MAIN CROSS-ROUND SCORING ENGINE
# ============================================================

def run_cross_round_scoring(dataset_root=None):

    paths = initialize_configuration(dataset_root)
    simulation_config = paths["simulation_config"]
    input_files = paths["input_files"]
    output_file = paths["output_file"]
    legacy_output_file = paths["legacy_output_file"]

    print("\n" + "=" * 70)
    print("ZECPath DAY 63 - CROSS-ROUND SCORING ENGINE")
    print("=" * 70)

    # --------------------------------------------------------
    # LOAD CONFIGURATION
    # --------------------------------------------------------

    config = load_configuration(paths["config_file"])

    weights = config["weights"]

    precision = config.get(
        "score_precision",
        2
    )

    # --------------------------------------------------------
    # LOAD ALL FIVE ASSESSMENT ROUNDS
    # --------------------------------------------------------

    all_round_data = {}

    pipeline_metadata = {}

    input_warnings = []

    for round_name, file_path in input_files.items():

        pipeline_data, records = load_round_data(
            round_name,
            file_path
        )

        all_round_data[round_name] = records

        warnings = inspect_pipeline_status(
            pipeline_data,
            round_name
        )

        input_warnings.extend(warnings)

        pipeline_metadata[round_name] = {

            "pipeline_status": pipeline_data.get(
                "pipeline_status",
                "UNKNOWN"
            ),

            "validation": pipeline_data.get(
                "validation",
                {}
            ),

            "is_simulated": pipeline_data.get(
                "is_simulated"
            ),

            "score_source": (
                pipeline_data.get("score_source")
                or pipeline_data.get("score_type")
            ),

            "candidate_records_loaded": len(records)
        }

        # Preserve machine-test pipeline-level provenance.

        if round_name == "machine_test":

            pipeline_metadata[round_name][
                "scoring_policy"
            ] = pipeline_data.get(
                "scoring_policy",
                {}
            )

            pipeline_metadata[round_name][
                "data_provenance"
            ] = pipeline_data.get(
                "data_provenance",
                {}
            )

    # --------------------------------------------------------
    # COLLECT UNIQUE CANDIDATE/JOB COMBINATIONS
    # --------------------------------------------------------

    all_candidate_keys = set()

    for records in all_round_data.values():

        all_candidate_keys.update(
            records.keys()
        )

    sorted_keys = sorted(all_candidate_keys)

    print(
        "\nTotal unique candidate/job combinations:",
        len(sorted_keys)
    )

    # --------------------------------------------------------
    # PROCESS EACH CANDIDATE
    # --------------------------------------------------------

    candidate_results = []

    scoring_counter = Counter()

    decision_counter = Counter()

    for candidate_id, job_id in sorted_keys:

        candidate_rounds = {}

        # Collect scores from all five rounds.

        for round_name, records in all_round_data.items():

            candidate_rounds[round_name] = records.get(
                (candidate_id, job_id),
                {
                    "score": None,
                    "assessment_status": "NOT_FOUND",
                    "provenance": {}
                }
            )

        # Calculate unified score.

        score_result = calculate_unified_score(
            candidate_rounds,
            weights,
            precision
        )

        # Read ATS eligibility separately.

        eligibility_status = candidate_rounds[
            "ats"
        ].get("eligibility_status")

        # Determine final decision.

        final_decision = determine_final_decision(
            eligibility_status,
            score_result["scoring_status"]
        )

        # Build round-level details.

        round_details = build_round_details(
            candidate_rounds,
            weights
        )

        # Create candidate result.

        candidate_result = {

            "candidate_id": candidate_id,

            "job_id": job_id,

            "round_details": round_details,

            "unified_score": score_result[
                "unified_score"
            ],

            "score_coverage": score_result[
                "score_coverage"
            ],

            "available_weight": score_result[
                "available_weight"
            ],

            "available_rounds": score_result[
                "available_rounds"
            ],

            "missing_rounds": score_result[
                "missing_rounds"
            ],

            "scoring_status": score_result[
                "scoring_status"
            ],

            "ats_eligibility_status": eligibility_status,

            "final_decision": final_decision
        }

        candidate_results.append(
            candidate_result
        )

        scoring_counter[
            score_result["scoring_status"]
        ] += 1

        decision_counter[
            final_decision
        ] += 1

        print(
            f"{candidate_id} | {job_id} | "
            f"Score: {score_result['unified_score']} | "
            f"Coverage: {score_result['score_coverage']}% | "
            f"Status: {score_result['scoring_status']} | "
            f"Decision: {final_decision}"
        )

    # --------------------------------------------------------
    # SUMMARY CALCULATION
    # --------------------------------------------------------

    scored_candidates = [
        candidate
        for candidate in candidate_results
        if candidate["unified_score"] is not None
    ]

    scores = [
        candidate["unified_score"]
        for candidate in scored_candidates
    ]

    average_score = (
        round(sum(scores) / len(scores), precision)
        if scores
        else None
    )

    highest_score = (
        max(scores)
        if scores
        else None
    )

    lowest_score = (
        min(scores)
        if scores
        else None
    )

    summary = {

        "total_candidates": len(candidate_results),

        "scored_candidates": len(scored_candidates),

        "no_scores_available": scoring_counter.get(
            "NO_SCORES_AVAILABLE",
            0
        ),

        "completed": scoring_counter.get(
            "COMPLETED",
            0
        ),

        "incomplete": scoring_counter.get(
            "INCOMPLETE",
            0
        ),

        "average_unified_score": average_score,

        "highest_unified_score": highest_score,

        "lowest_unified_score": lowest_score,

        "scoring_status_counts": dict(
            scoring_counter
        ),

        "final_decision_counts": dict(
            decision_counter
        )
    }

    # --------------------------------------------------------
    # DETERMINE OVERALL PIPELINE STATUS
    # --------------------------------------------------------

    overall_status = determine_pipeline_status(
        pipeline_metadata,
        input_warnings
    )

    # --------------------------------------------------------
    # BUILD FINAL OUTPUT
    # --------------------------------------------------------

    output = {

        "module": (
            "ZecPath Day 63 Cross-Round Scoring Engine"
        ),

        "pipeline_status": overall_status,

        "generated_at": datetime.now().astimezone().isoformat(),

        "dataset": {
            "dataset_name": simulation_config.dataset_name,
            "dataset_type": simulation_config.dataset_type,
            "dataset_root": str(paths["dataset_root"])
        },

        "scoring_method": (
            "AVAILABLE_ROUNDS_WEIGHTED_NORMALIZATION"
        ),

        "weights": weights,

        "missing_score_policy": (
            "Calculate using available rounds, "
            "report score coverage, and mark incomplete."
        ),

        "eligibility_policy": (
            "ATS eligibility remains separate "
            "from unified score."
        ),

        "score_range": {
            "minimum": config.get("minimum_score", 0),
            "maximum": config.get("maximum_score", 100)
        },

        "pipeline_metadata": pipeline_metadata,

        "input_warnings": input_warnings,

        "summary": summary,

        "candidate_results": candidate_results
    }

    # --------------------------------------------------------
    # SAVE OUTPUT JSON
    # --------------------------------------------------------

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    # Keep the former results/ location available for older consumers.
    with legacy_output_file.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=4, ensure_ascii=False)

    # --------------------------------------------------------
    # DISPLAY FINAL SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("CROSS-ROUND SCORING COMPLETED")
    print("=" * 70)

    print("Pipeline status:", overall_status)

    print(
        "Total candidates:",
        summary["total_candidates"]
    )

    print(
        "Scored candidates:",
        summary["scored_candidates"]
    )

    print(
        "Completed:",
        summary["completed"]
    )

    print(
        "Incomplete:",
        summary["incomplete"]
    )

    print(
        "No scores available:",
        summary["no_scores_available"]
    )

    print(
        "Average unified score:",
        summary["average_unified_score"]
    )

    print(
        "Highest unified score:",
        summary["highest_unified_score"]
    )

    print(
        "Lowest unified score:",
        summary["lowest_unified_score"]
    )

    print("\nInput warnings:")

    if input_warnings:

        for warning in input_warnings:
            print("-", warning)

    else:

        print("No input warnings.")

    print("\nOutput saved successfully:")

    print(output_file)


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        run_cross_round_scoring()

    except Exception as error:

        print("\nCROSS-ROUND SCORING FAILED")

        print("Error:", str(error))

        raise
