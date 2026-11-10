import json
from pathlib import Path


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DAY37_RESULT = (
    BASE_DIR.parent
    / "day37_hr_interview_scoring"
    / "results"
    / "hr_interview_score.json"
)

DAY42_STABILITY_RESULT = (
    BASE_DIR.parent
    / "day42_optimization_stability"
    / "stable_hr_interview_ai"
    / "results"
    / "stable_hr_interview_report.json"
)

DAY42_REFINED_RESULT = (
    BASE_DIR.parent
    / "day42_optimization_stability"
    / "refined_scoring_engine"
    / "results"
    / "refined_hr_score.json"
)

DEMO_DATASET = (
    BASE_DIR
    / "demo_dataset.json"
)

OUTPUT_DIR = BASE_DIR / "results"

OUTPUT_FILE = (
    OUTPUT_DIR
    / "production_hr_interview_result.json"
)


# ============================================================
# LOAD JSON
# ============================================================

def load_json(file_path):

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# VALIDATE WEIGHTS
# ============================================================

def validate_weights(weights):

    required_weights = {
        "answer_relevance",
        "communication",
        "confidence",
        "consistency"
    }

    if set(weights.keys()) != required_weights:
        return False

    for value in weights.values():

        if not isinstance(value, (int, float)):
            return False

        if value < 0:
            return False

    return round(sum(weights.values()), 5) == 1.0


# ============================================================
# VALIDATE PARAMETER SCORES
# ============================================================

def validate_parameter_scores(parameter_scores):

    required_parameters = {
        "answer_relevance",
        "communication",
        "confidence",
        "consistency"
    }

    if set(parameter_scores.keys()) != required_parameters:
        return False

    for value in parameter_scores.values():

        if not isinstance(value, (int, float)):
            return False

        if value < 0 or value > 100:
            return False

    return True


# ============================================================
# MAIN PROCESS
# ============================================================

def process_hr_interview():

    print("=" * 60)
    print("ZecPath Production-Ready HR Interview Module")
    print("=" * 60)

    # --------------------------------------------------------
    # Load Day 37
    # --------------------------------------------------------

    print("\nLoading Day 37 HR Interview result...")

    day37_data = load_json(
        DAY37_RESULT
    )

    candidate_id = day37_data.get(
        "candidate_id"
    )

    job_id = day37_data.get(
        "job_id"
    )

    total_questions = day37_data.get(
        "total_questions",
        0
    )

    scoring_weights = day37_data.get(
        "scoring_weights",
        {}
    )

    # Day 37 stores parameter values as parameter_averages
    parameter_averages = day37_data.get(
        "parameter_averages",
        {}
    )

    # Day 37 stores question scoring data as question_scores
    question_scores = day37_data.get(
        "question_scores",
        []
    )

    original_hr_score = day37_data.get(
        "final_hr_interview_score"
    )

    print(
        f"Candidate : {candidate_id}"
    )

    print(
        f"Job       : {job_id}"
    )

    print(
        f"Questions : {total_questions}"
    )

    # --------------------------------------------------------
    # Load Day 45 Demo Dataset
    # --------------------------------------------------------

    print("\nLoading Day 45 demo dataset...")

    demo_data = load_json(
        DEMO_DATASET
    )

    interview_data = demo_data.get(
        "interview",
        {}
    )

    demo_questions = interview_data.get(
        "questions",
        []
    )

    print(
        f"Demo Questions : {len(demo_questions)}"
    )

    # --------------------------------------------------------
    # Combine Day 37 scores with Day 45
    # demo question text and answers
    # --------------------------------------------------------

    questions = []

    score_lookup = {
        item.get("question_id"): item
        for item in question_scores
    }

    for demo_question in demo_questions:

        question_id = demo_question.get(
            "question_id"
        )

        score_data = score_lookup.get(
            question_id,
            {}
        )

        combined_question = {

            "question_id":
                question_id,

            "question_text":
                demo_question.get(
                    "question_text"
                ),

            "candidate_answer":
                demo_question.get(
                    "candidate_answer"
                ),

            "answer_relevance":
                score_data.get(
                    "answer_relevance"
                ),

            "communication_score":
                score_data.get(
                    "communication_score"
                ),

            "confidence_score":
                score_data.get(
                    "confidence_score"
                ),

            "consistency_score":
                score_data.get(
                    "consistency_score"
                ),

            "weighted_contribution":
                score_data.get(
                    "weighted_contribution",
                    {}
                ),

            "question_score":
                score_data.get(
                    "question_score"
                )
        }

        questions.append(
            combined_question
        )

    # --------------------------------------------------------
    # Load Day 42 Stability Result
    # --------------------------------------------------------

    print(
        "\nLoading Day 42 stability result..."
    )

    stability_data = load_json(
        DAY42_STABILITY_RESULT
    )

    interview_stability = stability_data.get(
        "interview_stability",
        {}
    )

    question_validation = (
        interview_stability.get(
            "question_validation",
            {}
        )
    )

    stability_status = (
        interview_stability.get(
            "stable",
            False
        )
    )

    duplicate_questions = (
        interview_stability.get(
            "duplicate_questions",
            []
        )
    )

    errors = (
        interview_stability.get(
            "errors",
            []
        )
    )

    warnings = (
        interview_stability.get(
            "warnings",
            []
        )
    )

    print(
        "Interview Stability : "
        + (
            "PASS"
            if stability_status
            else "FAIL"
        )
    )

    print(
        "Question Text       : "
        f"{question_validation.get('question_text_available', 0)}"
    )

    print(
        "Candidate Answers   : "
        f"{question_validation.get('candidate_answer_available', 0)}"
    )

    print(
        "Response Status     : "
        f"{question_validation.get('response_status_available', 0)}"
    )

    print(
        "Complete Questions  : "
        f"{question_validation.get('complete_questions', 0)}"
    )

    # --------------------------------------------------------
    # Load Day 42 Refined Score
    # --------------------------------------------------------

    print(
        "\nLoading Day 42 refined scoring result..."
    )

    refined_data = load_json(
        DAY42_REFINED_RESULT
    )

    refined_hr_score = refined_data.get(
        "refined_hr_score"
    )

    if refined_hr_score is None:

        refined_hr_score = refined_data.get(
            "final_hr_interview_score"
        )

    score_difference = round(
        refined_hr_score - original_hr_score,
        2
    )

    print(
        f"Refined HR Score    : {refined_hr_score}"
    )

    print(
        f"Score Difference    : {score_difference}"
    )

    # --------------------------------------------------------
    # Validate Scoring Configuration
    # --------------------------------------------------------

    print(
        "\nValidating scoring configuration..."
    )

    weights_valid = validate_weights(
        scoring_weights
    )

    if weights_valid:

        print(
            "PASS - Scoring weights are valid."
        )

    else:

        print(
            "FAIL - Scoring weights are invalid."
        )

    # --------------------------------------------------------
    # Validate Interview Structure
    # --------------------------------------------------------

    print(
        "\nValidating interview structure..."
    )

    question_text_count = 0
    candidate_answer_count = 0
    question_score_count = 0

    question_ids = []
    duplicate_question_ids = []

    for question in questions:

        question_id = question.get(
            "question_id"
        )

        question_text = question.get(
            "question_text"
        )

        candidate_answer = question.get(
            "candidate_answer"
        )

        question_score = question.get(
            "question_score"
        )

        if question_text:
            question_text_count += 1

        if candidate_answer:
            candidate_answer_count += 1

        if question_score is not None:
            question_score_count += 1

        if question_id in question_ids:

            duplicate_question_ids.append(
                question_id
            )

        question_ids.append(
            question_id
        )

    interview_structure_valid = (
        len(questions) == total_questions
        and question_text_count == total_questions
        and candidate_answer_count == total_questions
        and question_score_count == total_questions
        and len(duplicate_question_ids) == 0
    )

    if interview_structure_valid:

        print(
            "PASS - Interview structure is valid."
        )

    else:

        print(
            "FAIL - Interview structure validation failed."
        )

    print(
        f"Question text available : "
        f"{question_text_count}"
    )

    print(
        f"Candidate answers       : "
        f"{candidate_answer_count}"
    )

    print(
        f"Question scores         : "
        f"{question_score_count}"
    )

    print(
        f"Duplicate questions     : "
        f"{len(duplicate_question_ids)}"
    )

    # --------------------------------------------------------
    # Validate Parameter Scores
    # --------------------------------------------------------

    print(
        "\nValidating parameter scores..."
    )

    parameter_scores = parameter_averages

    parameter_scores_valid = (
        validate_parameter_scores(
            parameter_scores
        )
    )

    if parameter_scores_valid:

        print(
            "PASS - Parameter scores are valid."
        )

    else:

        print(
            "FAIL - Parameter scores are invalid."
        )

    # --------------------------------------------------------
    # Calculate Weighted Contributions
    # --------------------------------------------------------

    weighted_contributions = {}

    for parameter, score in parameter_scores.items():

        weight = scoring_weights.get(
            parameter,
            0
        )

        weighted_contributions[
            parameter
        ] = round(
            score * weight,
            2
        )

    # --------------------------------------------------------
    # Print Scoring Breakdown
    # --------------------------------------------------------

    print(
        "\nScoring Breakdown:"
    )

    for parameter in parameter_scores:

        score = parameter_scores[
            parameter
        ]

        weight = scoring_weights[
            parameter
        ]

        contribution = (
            weighted_contributions[
                parameter
            ]
        )

        print(
            f"  {parameter:<18}"
            f"Score: {score:<6}"
            f"Weight: {weight * 100:.1f}% "
            f"Contribution: {contribution}"
        )

    # --------------------------------------------------------
    # Determine Production Status
    # --------------------------------------------------------

    production_ready = (
        weights_valid
        and parameter_scores_valid
        and interview_structure_valid
        and stability_status
        and len(errors) == 0
        and refined_hr_score is not None
    )

    if production_ready:

        overall_status = (
            "PRODUCTION_READY"
        )

    else:

        overall_status = (
            "VALIDATION_FAILED"
        )

    # --------------------------------------------------------
    # Build Production Result
    # --------------------------------------------------------

    production_result = {

        "system_name":
            "ZecPath Production-Ready HR Interview Module",

        "system_version":
            "Day 45",

        "candidate_information": {

            "candidate_id":
                candidate_id,

            "job_id":
                job_id
        },

        "interview_summary": {

            "total_questions":
                total_questions,

            "question_text_available":
                question_text_count,

            "candidate_answers_available":
                candidate_answer_count,

            "question_scores_available":
                question_score_count,

            "duplicate_questions":
                duplicate_question_ids
        },

        "questions":
            questions,

        "scoring_weights":
            scoring_weights,

        "parameter_scores":
            parameter_scores,

        "weighted_contributions":
            weighted_contributions,

        "score_summary": {

            "original_hr_score":
                original_hr_score,

            "refined_hr_score":
                refined_hr_score,

            "final_hr_score":
                refined_hr_score,

            "score_difference":
                score_difference,

            "score_range":
                "0-100"
        },

        "stability": {

            "stable":
                stability_status,

            "errors":
                errors,

            "warnings":
                warnings,

            "duplicate_questions":
                duplicate_questions,

            "question_validation":
                question_validation
        },

        "validation": {

            "weights_valid":
                weights_valid,

            "parameter_scores_valid":
                parameter_scores_valid,

            "interview_structure_valid":
                interview_structure_valid,

            "stability_valid":
                stability_status,

            "refined_score_available":
                refined_hr_score is not None
        },

        # ====================================================
        # UPDATED EXPLAINABILITY
        # ====================================================

        "explainability": {

            "formula":
                "Final HR Score = "
                "(Answer Relevance × Weight) + "
                "(Communication × Weight) + "
                "(Confidence × Weight) + "
                "(Consistency × Weight)",

            "score_source":
                "Day 42 refined scoring result",

            "weighted_contributions":
                weighted_contributions
        },

        "production_status":
            overall_status
    }

    # --------------------------------------------------------
    # Save Production Result
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            production_result,
            file,
            indent=4,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # Final Output
    # --------------------------------------------------------

    print(
        f"\nOriginal HR Score : "
        f"{original_hr_score}"
    )

    print(
        f"Final HR Score    : "
        f"{refined_hr_score}"
    )

    print(
        f"Difference        : "
        f"{score_difference}"
    )

    print(
        f"Production Status : "
        f"{overall_status}"
    )

    print(
        "\nProduction result saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "Production HR Interview Module Completed"
    )

    print(
        "=" * 60
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    process_hr_interview()