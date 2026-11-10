import json
import os


# =========================================================
# FILE PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

AI_RESULT_FILE = os.path.join(
    BASE_DIR,
    "results",
    "hr_interview_test_report.json"
)

MANUAL_RESULT_FILE = os.path.join(
    BASE_DIR,
    "manual_evaluation.json"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "results"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "accuracy_evaluation.json"
)


# =========================================================
# EVALUATION DIMENSIONS
# =========================================================

DIMENSIONS = [
    "relevance",
    "communication",
    "confidence",
    "consistency",
    "logical_reasoning",
    "scenario"
]


# =========================================================
# LOAD JSON FILE
# =========================================================

def load_json(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# =========================================================
# GET AI SCORE
# =========================================================

def get_ai_score(ai_candidate, dimension):

    evaluation_scores = ai_candidate.get(
        "evaluation_scores",
        {}
    )

    # First four dimensions
    if dimension in evaluation_scores:

        return evaluation_scores[dimension]

    # Logical reasoning
    if dimension == "logical_reasoning":

        if "logical_reasoning_score" in evaluation_scores:

            return evaluation_scores[
                "logical_reasoning_score"
            ]

    # Scenario
    if dimension == "scenario":

        if "scenario_score" in evaluation_scores:

            return evaluation_scores[
                "scenario_score"
            ]

    raise KeyError(
        f"AI score for '{dimension}' "
        f"not found for candidate "
        f"{ai_candidate.get('candidate_id')}"
    )


# =========================================================
# GET MANUAL SCORE
# =========================================================

def get_manual_score(
    manual_candidate,
    dimension
):

    if dimension in manual_candidate:

        return manual_candidate[dimension]

    raise KeyError(
        f"Manual score for '{dimension}' "
        f"not found."
    )


# =========================================================
# CALCULATE ABSOLUTE ERROR
# =========================================================

def calculate_absolute_error(
    ai_score,
    manual_score
):

    return round(
        abs(
            float(ai_score) -
            float(manual_score)
        ),
        2
    )


# =========================================================
# MAIN ACCURACY EVALUATION
# =========================================================

def evaluate_accuracy():

    print("=" * 75)
    print("DAY 40 - HR INTERVIEW ACCURACY EVALUATION")
    print("=" * 75)

    # -----------------------------------------------------
    # Load files
    # -----------------------------------------------------

    print()
    print("Loading AI interview results...")
    print(AI_RESULT_FILE)

    print()
    print("Loading manual reference evaluation...")
    print(MANUAL_RESULT_FILE)

    ai_data = load_json(
        AI_RESULT_FILE
    )

    manual_data = load_json(
        MANUAL_RESULT_FILE
    )

    # -----------------------------------------------------
    # Get candidates
    # -----------------------------------------------------

    ai_candidates = ai_data.get(
        "sessions",
        []
    )

    manual_candidates = manual_data.get(
        "candidates",
        {}
    )

    if not ai_candidates:

        raise ValueError(
            "No sessions found in AI report."
        )

    if not manual_candidates:

        raise ValueError(
            "No candidates found in manual evaluation."
        )

    # -----------------------------------------------------
    # Initialize calculations
    # -----------------------------------------------------

    candidate_results = []

    total_error = 0

    total_comparisons = 0

    dimension_errors = {
        dimension: []
        for dimension in DIMENSIONS
    }

    # =====================================================
    # PROCESS EACH CANDIDATE
    # =====================================================

    for ai_candidate in ai_candidates:

        candidate_id = ai_candidate[
            "candidate_id"
        ]

        candidate_type = ai_candidate.get(
            "candidate_type",
            "unknown"
        )

        print()
        print("-" * 75)

        print(
            f"Evaluating: {candidate_id}"
        )

        # -------------------------------------------------
        # Check manual evaluation
        # -------------------------------------------------

        if candidate_id not in manual_candidates:

            print(
                f"WARNING: Manual evaluation "
                f"not found for {candidate_id}"
            )

            continue

        manual_candidate = manual_candidates[
            candidate_id
        ]

        comparison = {}

        candidate_total_error = 0

        # =================================================
        # COMPARE DIMENSIONS
        # =================================================

        for dimension in DIMENSIONS:

            ai_score = get_ai_score(
                ai_candidate,
                dimension
            )

            manual_score = get_manual_score(
                manual_candidate,
                dimension
            )

            error = calculate_absolute_error(
                ai_score,
                manual_score
            )

            # Store comparison
            comparison[dimension] = {

                "ai_score": ai_score,

                "manual_score": manual_score,

                "absolute_error": error
            }

            # Update totals
            candidate_total_error += error

            total_error += error

            total_comparisons += 1

            dimension_errors[
                dimension
            ].append(error)

        # -------------------------------------------------
        # Candidate MAE
        # -------------------------------------------------

        candidate_mae = round(
            candidate_total_error /
            len(DIMENSIONS),
            2
        )

        # -------------------------------------------------
        # Store candidate result
        # -------------------------------------------------

        candidate_results.append({

            "candidate_id":
                candidate_id,

            "candidate_type":
                candidate_type,

            "comparison":
                comparison,

            "mean_absolute_error":
                candidate_mae
        })

        # -------------------------------------------------
        # Print candidate result
        # -------------------------------------------------

        print(
            f"Candidate Type : "
            f"{candidate_type}"
        )

        print(
            f"Mean Absolute Error : "
            f"{candidate_mae}"
        )

        for dimension, values in comparison.items():

            print(
                f"{dimension:<20} "
                f"AI={values['ai_score']:<7} "
                f"Manual={values['manual_score']:<7} "
                f"Error={values['absolute_error']}"
            )

    # =====================================================
    # OVERALL MAE
    # =====================================================

    if total_comparisons > 0:

        overall_mae = round(
            total_error /
            total_comparisons,
            2
        )

    else:

        overall_mae = 0

    # =====================================================
    # DIMENSION-WISE MAE
    # =====================================================

    dimension_mae = {}

    for dimension in DIMENSIONS:

        errors = dimension_errors[
            dimension
        ]

        if errors:

            dimension_mae[dimension] = round(
                sum(errors) /
                len(errors),
                2
            )

        else:

            dimension_mae[dimension] = 0

    # =====================================================
    # FIND MAXIMUM ERROR
    # =====================================================

    maximum_error = 0

    maximum_error_details = None

    for candidate in candidate_results:

        for dimension, values in candidate[
            "comparison"
        ].items():

            error = values[
                "absolute_error"
            ]

            if error > maximum_error:

                maximum_error = error

                maximum_error_details = {

                    "candidate_id":
                        candidate["candidate_id"],

                    "candidate_type":
                        candidate["candidate_type"],

                    "dimension":
                        dimension,

                    "ai_score":
                        values["ai_score"],

                    "manual_score":
                        values["manual_score"],

                    "absolute_error":
                        error
                }

    # =====================================================
    # IDENTIFY AREAS REQUIRING ATTENTION
    # =====================================================

    dimensions_requiring_attention = []

    for dimension, mae in dimension_mae.items():

        if mae >= 3:

            dimensions_requiring_attention.append({

                "dimension":
                    dimension,

                "mean_absolute_error":
                    mae,

                "reason":
                    "Higher difference between AI "
                    "and manual reference scores."
            })

    # =====================================================
    # OVERALL EVALUATION
    # =====================================================

    if overall_mae <= 2:

        overall_evaluation = (
            "High agreement"
        )

    elif overall_mae <= 4:

        overall_evaluation = (
            "Moderate agreement"
        )

    else:

        overall_evaluation = (
            "Lower agreement"
        )

    # =====================================================
    # CREATE FINAL REPORT
    # =====================================================

    result = {

        "report_title":
            "Day 40 - HR Interview Accuracy Evaluation",

        "evaluation_type":
            "AI vs Manual Reference Comparison",

        "objective":
            (
                "Compare AI-generated HR interview "
                "evaluation scores with manually "
                "defined reference scores for "
                "simulated candidate profiles."
            ),

        "total_candidates_evaluated":
            len(candidate_results),

        "total_score_comparisons":
            total_comparisons,

        "evaluation_dimensions":
            DIMENSIONS,

        "candidate_results":
            candidate_results,

        "dimension_mean_absolute_error":
            dimension_mae,

        "overall_mean_absolute_error":
            overall_mae,

        "maximum_scoring_difference":
            maximum_error_details,

        "dimensions_requiring_attention":
            dimensions_requiring_attention,

        "overall_evaluation":
            overall_evaluation,

        "interpretation":
            (
                "The evaluation measures score "
                "differences between the AI "
                "simulation and controlled manual "
                "reference values. Manual values "
                "are reference labels created "
                "for this test and do not represent "
                "independent recruiter ratings."
            )
    }

    # =====================================================
    # SAVE RESULT
    # =====================================================

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4
        )

    # =====================================================
    # PRINT DIMENSION MAE
    # =====================================================

    print()
    print("=" * 75)
    print("DIMENSION-WISE MEAN ABSOLUTE ERROR")
    print("=" * 75)

    for dimension, mae in dimension_mae.items():

        print(
            f"{dimension:<25}: {mae}"
        )

    # =====================================================
    # PRINT OVERALL RESULT
    # =====================================================

    print()
    print("=" * 75)
    print("OVERALL ACCURACY EVALUATION")
    print("=" * 75)

    print(
        f"Total Candidates : "
        f"{len(candidate_results)}"
    )

    print(
        f"Total Comparisons: "
        f"{total_comparisons}"
    )

    print(
        f"Overall MAE      : "
        f"{overall_mae}"
    )

    print(
        f"Evaluation       : "
        f"{overall_evaluation}"
    )

    # =====================================================
    # PRINT MAXIMUM DIFFERENCE
    # =====================================================

    if maximum_error_details:

        print()
        print("=" * 75)
        print("MAXIMUM SCORING DIFFERENCE")
        print("=" * 75)

        print(
            f"Candidate : "
            f"{maximum_error_details['candidate_id']}"
        )

        print(
            f"Type      : "
            f"{maximum_error_details['candidate_type']}"
        )

        print(
            f"Dimension : "
            f"{maximum_error_details['dimension']}"
        )

        print(
            f"AI Score  : "
            f"{maximum_error_details['ai_score']}"
        )

        print(
            f"Manual    : "
            f"{maximum_error_details['manual_score']}"
        )

        print(
            f"Error     : "
            f"{maximum_error_details['absolute_error']}"
        )

    # =====================================================
    # PRINT ATTENTION AREAS
    # =====================================================

    print()

    if dimensions_requiring_attention:

        print("=" * 75)
        print("DIMENSIONS REQUIRING ATTENTION")
        print("=" * 75)

        for item in dimensions_requiring_attention:

            print(
                f"- {item['dimension']}: "
                f"MAE = "
                f"{item['mean_absolute_error']}"
            )

    else:

        print(
            "No dimensions exceeded "
            "the attention threshold."
        )

    # =====================================================
    # SUCCESS
    # =====================================================

    print()
    print("=" * 75)
    print(
        "ACCURACY EVALUATION COMPLETED SUCCESSFULLY"
    )
    print("=" * 75)

    print()
    print("Saved Result:")

    print(
        OUTPUT_FILE
    )


# =========================================================
# PROGRAM ENTRY POINT
# =========================================================

if __name__ == "__main__":

    evaluate_accuracy()