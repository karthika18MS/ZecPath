import os
import sys
import json
import time


# ==========================================================
# ZecPath DAY 18
# BATCH ATS RUNNER
# ==========================================================
#
# Purpose:
#
# 1. Load Sentence Transformer model only once
# 2. Reuse the model for multiple candidates
# 3. Run the validated Day 18 ATS engine
# 4. Measure batch performance
# 5. Save a batch summary
#
# Usage:
#
# python -m day18_optimization.day18_batch_runner
#
# Optional:
#
# python -m day18_optimization.day18_batch_runner \
#     candidate_006 candidate_007 candidate_008
#
# ==========================================================


# ==========================================================
# PROJECT ROOT
# ==========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(
        0,
        PROJECT_ROOT
    )


# ==========================================================
# IMPORT VALIDATED DAY 18 ENGINE
# ==========================================================

from day18_optimization.optimized_ats_engine import (
    run_optimized_ats
)


# ==========================================================
# IMPORT CACHED SEMANTIC MODEL
# ==========================================================

from models.semantic_model import (
    get_semantic_model
)


# ==========================================================
# CANDIDATE CONFIGURATION
# ==========================================================

CANDIDATES = {

    "candidate_006": {
        "target_role":
            "Backend Developer",

        "job_description":
            "backend_developer.txt"
    },

    "candidate_007": {
        "target_role":
            "HR Executive",

        "job_description":
            "hr_executive.txt"
    },

    "candidate_008": {
        "target_role":
            "Marketing Executive",

        "job_description":
            "marketing_executive.txt"
    },

    "candidate_009": {
        "target_role":
            "Fresher Python Developer",

        "job_description":
            "fresher_python_developer.txt"
    },

    "candidate_010": {
        "target_role":
            "Fresher Data Analyst",

        "job_description":
            "fresher_data_analyst.txt"
    },

    "candidate_011": {
        "target_role":
            "Senior Python Developer",

        "job_description":
            "senior_python_developer.txt"
    },

    "candidate_012": {
        "target_role":
            "Senior Backend Developer",

        "job_description":
            "senior_backend_developer.txt"
    },

    "candidate_013": {
        "target_role":
            "Python Developer",

        "job_description":
            "python_developer.txt"
    }
}


# ==========================================================
# OUTPUT DIRECTORY
# ==========================================================

RESULTS_DIRECTORY = os.path.join(

    PROJECT_ROOT,

    "day18_optimization",

    "results"
)


# ==========================================================
# SAVE JSON
# ==========================================================

def save_json(
    data,
    file_path
):

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ==========================================================
# SELECT CANDIDATES
# ==========================================================

def get_selected_candidates():

    # ------------------------------------------------------
    # No command-line candidate IDs:
    # Run all candidates
    # ------------------------------------------------------

    if len(sys.argv) <= 1:

        return list(
            CANDIDATES.keys()
        )

    # ------------------------------------------------------
    # Candidate IDs supplied manually
    # ------------------------------------------------------

    selected = []

    for candidate_id in sys.argv[1:]:

        if candidate_id not in CANDIDATES:

            print()

            print(
                f"WARNING: Unknown candidate: "
                f"{candidate_id}"
            )

            continue

        selected.append(
            candidate_id
        )

    return selected


# ==========================================================
# MODEL WARM-UP
# ==========================================================

def load_model_once():

    print()

    print(
        "=" * 70
    )

    print(
        "       ZecPath DAY 18 MODEL REUSE"
    )

    print(
        "=" * 70
    )

    print()

    print(
        "Loading Sentence Transformer model once..."
    )

    print(
        "Model: all-MiniLM-L6-v2"
    )

    model_start = (
        time.perf_counter()
    )

    model = get_semantic_model()

    model_load_time = (
        time.perf_counter()
        - model_start
    )

    print()

    print(
        f"Model loaded successfully."
    )

    print(
        f"Initial model load time: "
        f"{model_load_time:.6f} seconds"
    )

    print()

    print(
        "MODEL REUSE ENABLED"
    )

    print(
        "The same model instance will be reused "
        "for all candidates in this process."
    )

    return (
        model,
        model_load_time
    )


# ==========================================================
# RUN ONE CANDIDATE
# ==========================================================

def run_candidate(
    candidate_id
):

    configuration = CANDIDATES[
        candidate_id
    ]

    target_role = configuration[
        "target_role"
    ]

    job_description = configuration[
        "job_description"
    ]

    print()

    print(
        "#" * 70
    )

    print(
        f"PROCESSING {candidate_id.upper()}"
    )

    print(
        "#" * 70
    )

    print()

    print(
        f"Candidate : {candidate_id}"
    )

    print(
        f"Role      : {target_role}"
    )

    print(
        f"JD        : {job_description}"
    )

    candidate_start = (
        time.perf_counter()
    )

    result = run_optimized_ats(

        candidate_id,

        target_role,

        job_description
    )

    candidate_time = (
        time.perf_counter()
        - candidate_start
    )

    final_score = (
        result[
            "scores"
        ][
            "final_ats_score"
        ]
    )

    semantic_score = (
        result[
            "scores"
        ][
            "semantic_similarity"
        ]
    )

    skill_score = (
        result[
            "scores"
        ][
            "skill_matching"
        ]
    )

    experience_score = (
        result[
            "scores"
        ][
            "experience_relevance"
        ]
    )

    education_score = (
        result[
            "scores"
        ][
            "education_alignment"
        ]
    )

    performance = (
        result[
            "performance"
        ]
    )

    print()

    print(
        "-" * 70
    )

    print(
        "BATCH RESULT"
    )

    print(
        "-" * 70
    )

    print(
        f"Skill Matching       : "
        f"{skill_score:.2f}%"
    )

    print(
        f"Experience           : "
        f"{experience_score:.2f}%"
    )

    print(
        f"Education            : "
        f"{education_score:.2f}%"
    )

    print(
        f"Semantic Similarity  : "
        f"{semantic_score:.2f}%"
    )

    print(
        f"Final ATS            : "
        f"{final_score:.2f}%"
    )

    print(
        f"Candidate Time       : "
        f"{candidate_time:.6f} sec"
    )

    return {

        "candidate_id":
            candidate_id,

        "target_role":
            target_role,

        "job_description":
            job_description,

        "skill_matching":
            skill_score,

        "experience_relevance":
            experience_score,

        "education_alignment":
            education_score,

        "semantic_similarity":
            semantic_score,

        "final_ats_score":
            final_score,

        "matching_status":
            result.get(
                "matching_status"
            ),

        "shortlisting_status":
            result.get(
                "shortlisting_status"
            ),

        "recommendation":
            result.get(
                "recommendation"
            ),

        "candidate_pipeline_time_seconds":
            round(
                candidate_time,
                6
            ),

        "engine_performance":
            performance
    }


# ==========================================================
# BATCH PERFORMANCE CALCULATION
# ==========================================================

def calculate_batch_statistics(
    candidate_results,
    model_load_time,
    total_batch_time
):

    if not candidate_results:

        return {

            "candidate_count":
                0,

            "model_load_time_seconds":
                round(
                    model_load_time,
                    6
                ),

            "total_batch_time_seconds":
                round(
                    total_batch_time,
                    6
                )
        }

    candidate_times = [

        result[
            "candidate_pipeline_time_seconds"
        ]

        for result in candidate_results
    ]

    semantic_times = [

        result[
            "engine_performance"
        ][
            "semantic_processing_time_seconds"
        ]

        for result in candidate_results
    ]

    extraction_times = [

        result[
            "engine_performance"
        ][
            "extraction_time_seconds"
        ]

        for result in candidate_results
    ]

    cleaning_times = [

        result[
            "engine_performance"
        ][
            "cleaning_time_seconds"
        ]

        for result in candidate_results
    ]

    entity_times = [

        result[
            "engine_performance"
        ][
            "entity_detection_time_seconds"
        ]

        for result in candidate_results
    ]

    skill_times = [

        result[
            "engine_performance"
        ][
            "skill_matching_time_seconds"
        ]

        for result in candidate_results
    ]

    return {

        "candidate_count":
            len(candidate_results),

        "model_load_time_seconds":
            round(
                model_load_time,
                6
            ),

        "total_batch_time_seconds":
            round(
                total_batch_time,
                6
            ),

        "candidate_processing_time_total_seconds":
            round(
                sum(candidate_times),
                6
            ),

        "average_candidate_time_seconds":
            round(
                sum(candidate_times)
                / len(candidate_times),
                6
            ),

        "average_semantic_time_seconds":
            round(
                sum(semantic_times)
                / len(semantic_times),
                6
            ),

        "average_extraction_time_seconds":
            round(
                sum(extraction_times)
                / len(extraction_times),
                6
            ),

        "average_cleaning_time_seconds":
            round(
                sum(cleaning_times)
                / len(cleaning_times),
                6
            ),

        "average_entity_detection_time_seconds":
            round(
                sum(entity_times)
                / len(entity_times),
                6
            ),

        "average_skill_matching_time_seconds":
            round(
                sum(skill_times)
                / len(skill_times),
                6
            ),

        "fastest_candidate_seconds":
            round(
                min(candidate_times),
                6
            ),

        "slowest_candidate_seconds":
            round(
                max(candidate_times),
                6
            )
    }


# ==========================================================
# MAIN BATCH PROCESS
# ==========================================================

def main():

    selected_candidates = (
        get_selected_candidates()
    )

    if not selected_candidates:

        print()

        print(
            "ERROR: No valid candidates selected."
        )

        return

    # ======================================================
    # LOAD MODEL ONCE
    # ======================================================

    model, model_load_time = (
        load_model_once()
    )

    # ------------------------------------------------------
    # Keep a reference to the model.
    #
    # This prevents accidental garbage collection during
    # the batch process.
    # ------------------------------------------------------

    _model_reference = model

    # ======================================================
    # BATCH START
    # ======================================================

    batch_start = (
        time.perf_counter()
    )

    candidate_results = []

    # ======================================================
    # PROCESS CANDIDATES
    # ======================================================

    for candidate_id in selected_candidates:

        try:

            result = run_candidate(
                candidate_id
            )

            candidate_results.append(
                result
            )

        except Exception as error:

            print()

            print(
                f"ERROR processing "
                f"{candidate_id}:"
            )

            print(
                str(error)
            )

            candidate_results.append({

                "candidate_id":
                    candidate_id,

                "pipeline_status":
                    "FAILED",

                "error":
                    str(error)
            })

    # ======================================================
    # TOTAL BATCH TIME
    # ======================================================

    total_batch_time = (
        time.perf_counter()
        - batch_start
    )

    # ======================================================
    # PERFORMANCE STATISTICS
    # ======================================================

    successful_results = [

        result

        for result in candidate_results

        if result.get(
            "final_ats_score"
        ) is not None
    ]

    statistics = (
        calculate_batch_statistics(

            successful_results,

            model_load_time,

            total_batch_time
        )
    )

    # ======================================================
    # BATCH SUMMARY
    # ======================================================

    batch_summary = {

        "engine":
            "ZecPath Day 18 Batch ATS Runner",

        "optimization":
            "Sentence Transformer Model Reuse",

        "model":
            "all-MiniLM-L6-v2",

        "model_loaded_once":
            True,

        "candidate_ids":
            selected_candidates,

        "successful_candidates":
            len(successful_results),

        "failed_candidates":
            (
                len(candidate_results)
                - len(successful_results)
            ),

        "candidates":
            candidate_results,

        "performance":
            statistics
    }

    # ======================================================
    # SAVE RESULT
    # ======================================================

    os.makedirs(
        RESULTS_DIRECTORY,
        exist_ok=True
    )

    output_path = os.path.join(

        RESULTS_DIRECTORY,

        "day18_batch_summary.json"
    )

    save_json(
        batch_summary,
        output_path
    )

    # ======================================================
    # DISPLAY FINAL SUMMARY
    # ======================================================

    print()

    print(
        "=" * 70
    )

    print(
        "       ZecPath DAY 18 BATCH SUMMARY"
    )

    print(
        "=" * 70
    )

    print()

    print(
        f"Model                    : "
        f"all-MiniLM-L6-v2"
    )

    print(
        f"Model Loaded Once        : YES"
    )

    print(
        f"Candidates Processed     : "
        f"{len(candidate_results)}"
    )

    print(
        f"Successful               : "
        f"{len(successful_results)}"
    )

    print(
        f"Failed                   : "
        f"{len(candidate_results) - len(successful_results)}"
    )

    print()

    print(
        "PERFORMANCE"
    )

    print(
        f"Initial Model Load       : "
        f"{model_load_time:.6f} sec"
    )

    print(
        f"Total Batch Time         : "
        f"{total_batch_time:.6f} sec"
    )

    if successful_results:

        print(
            f"Average Candidate Time  : "
            f"{statistics['average_candidate_time_seconds']:.6f} sec"
        )

        print(
            f"Average Semantic Time   : "
            f"{statistics['average_semantic_time_seconds']:.6f} sec"
        )

        print(
            f"Fastest Candidate       : "
            f"{statistics['fastest_candidate_seconds']:.6f} sec"
        )

        print(
            f"Slowest Candidate       : "
            f"{statistics['slowest_candidate_seconds']:.6f} sec"
        )

    print()

    print(
        "FINAL ATS RESULTS"
    )

    print()

    for result in successful_results:

        print(

            f"{result['candidate_id']} "
            f"| Skill: "
            f"{result['skill_matching']:.2f}% "
            f"| Semantic: "
            f"{result['semantic_similarity']:.2f}% "
            f"| Final: "
            f"{result['final_ats_score']:.2f}%"
        )

    print()

    print(
        "Batch summary saved to:"
    )

    print(
        output_path
    )

    print()

    print(
        "MODEL REUSE TEST COMPLETED SUCCESSFULLY."
    )

    print()

    # Prevent the reference from being optimized away.
    _ = _model_reference


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()
