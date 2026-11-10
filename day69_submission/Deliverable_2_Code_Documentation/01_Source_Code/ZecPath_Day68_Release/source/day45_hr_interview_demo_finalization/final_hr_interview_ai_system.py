"""
ZecPath - Day 45
Deliverable 1: Final HR Interview AI System

Updated after Day 37 and Day 42.

Data flow:

    Day 37 HR Interview Result
                |
                v
    Day 42 Stable HR Interview AI
                |
                v
    Day 42 Refined Scoring Engine
                |
                v
    Day 45 Final HR Interview AI


Features:
1. Loads the real Day 37 HR interview result.
2. Loads the Day 42 stability result.
3. Loads the Day 42 refined scoring result.
4. Validates interview structure.
5. Validates question text.
6. Validates candidate answers.
7. Validates question scores.
8. Validates parameter scores.
9. Validates scoring weights.
10. Uses the Day 42 refined HR score.
11. Displays weighted scoring contributions.
12. Provides explainability.
13. Saves the final Day 45 result.
"""

import json
from pathlib import Path


# ============================================================
# PATH CONFIGURATION
# ============================================================

# ZecPath-AI project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------
# Day 37 HR Interview Result
# ------------------------------------------------------------

DAY37_RESULT = (
    PROJECT_ROOT
    / "day37_hr_interview_scoring"
    / "results"
    / "hr_interview_score.json"
)


# ------------------------------------------------------------
# Day 42 Stable HR Interview Result
# ------------------------------------------------------------

DAY42_STABILITY_RESULT = (
    PROJECT_ROOT
    / "day42_optimization_stability"
    / "stable_hr_interview_ai"
    / "results"
    / "stable_hr_interview_report.json"
)


# ------------------------------------------------------------
# Day 42 Refined Scoring Result
# ------------------------------------------------------------

DAY42_REFINED_RESULT = (
    PROJECT_ROOT
    / "day42_optimization_stability"
    / "refined_scoring_engine"
    / "results"
    / "refined_hr_score.json"
)


# ------------------------------------------------------------
# Day 45 Output
# ------------------------------------------------------------

OUTPUT_DIR = (
    Path(__file__).resolve().parent
    / "results"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "final_hr_interview_result.json"
)


# ============================================================
# HR SCORING WEIGHTS
# ============================================================

SCORING_WEIGHTS = {
    "answer_relevance": 0.30,
    "communication": 0.25,
    "confidence": 0.20,
    "consistency": 0.25
}


# ============================================================
# LOAD JSON FILE
# ============================================================

def load_json(file_path):
    """
    Load JSON data from the given file path.
    """

    if not file_path.exists():

        raise FileNotFoundError(
            f"Required file not found:\n{file_path}"
        )

    with file_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# VALIDATE SCORING WEIGHTS
# ============================================================

def validate_weights(weights):
    """
    Validate the HR scoring weights.

    Required parameters:
        answer_relevance
        communication
        confidence
        consistency

    Total weight must equal 1.0.
    """

    required_parameters = {
        "answer_relevance",
        "communication",
        "confidence",
        "consistency"
    }

    # --------------------------------------------------------
    # Check parameter names
    # --------------------------------------------------------

    if set(weights.keys()) != required_parameters:

        raise ValueError(
            "Invalid scoring parameters."
        )

    # --------------------------------------------------------
    # Check individual weights
    # --------------------------------------------------------

    for parameter, weight in weights.items():

        if not isinstance(
            weight,
            (int, float)
        ):

            raise ValueError(
                f"Weight for {parameter} "
                "must be numeric."
            )

        if weight < 0:

            raise ValueError(
                f"Weight for {parameter} "
                "cannot be negative."
            )

    # --------------------------------------------------------
    # Check total weight
    # --------------------------------------------------------

    total_weight = sum(
        weights.values()
    )

    if round(
        total_weight,
        6
    ) != 1.0:

        raise ValueError(
            "Scoring weights must add up to 1.0."
        )


# ============================================================
# VALIDATE SCORE
# ============================================================

def validate_score(
    score,
    name
):
    """
    Validate that a score is between 0 and 100.
    """

    if not isinstance(
        score,
        (int, float)
    ):

        raise ValueError(
            f"{name} must be numeric."
        )

    if not 0 <= score <= 100:

        raise ValueError(
            f"{name} must be between 0 and 100."
        )


# ============================================================
# VALIDATE DAY 37 INTERVIEW DATA
# ============================================================

def validate_interview_data(data):
    """
    Validate the updated Day 37 HR interview structure.

    Required question information:

        question_id
        question_text
        candidate_answer
        question_score
    """

    errors = []
    warnings = []

    # --------------------------------------------------------
    # Candidate ID
    # --------------------------------------------------------

    candidate_id = data.get(
        "candidate_id"
    )

    if not candidate_id:

        errors.append(
            "Candidate ID is missing."
        )

    # --------------------------------------------------------
    # Job ID
    # --------------------------------------------------------

    job_id = data.get(
        "job_id"
    )

    if not job_id:

        errors.append(
            "Job ID is missing."
        )

    # --------------------------------------------------------
    # Question list
    # --------------------------------------------------------

    questions = data.get(
        "question_scores",
        []
    )

    if not isinstance(
        questions,
        list
    ):

        errors.append(
            "question_scores must be a list."
        )

        questions = []

    # --------------------------------------------------------
    # Counters
    # --------------------------------------------------------

    question_ids = []

    question_text_count = 0

    candidate_answer_count = 0

    question_score_count = 0

    # --------------------------------------------------------
    # Validate each question
    # --------------------------------------------------------

    for index, question in enumerate(
        questions,
        start=1
    ):

        # ----------------------------------------------------
        # Question object
        # ----------------------------------------------------

        if not isinstance(
            question,
            dict
        ):

            errors.append(
                f"Question {index} is invalid."
            )

            continue

        # ----------------------------------------------------
        # Question ID
        # ----------------------------------------------------

        question_id = question.get(
            "question_id"
        )

        if not question_id:

            errors.append(
                f"Question {index} "
                "is missing question_id."
            )

        else:

            question_ids.append(
                question_id
            )

        # ----------------------------------------------------
        # Question text
        # ----------------------------------------------------

        if question.get(
            "question_text"
        ):

            question_text_count += 1

        else:

            warnings.append(
                f"{question_id or index}: "
                "Question text is missing."
            )

        # ----------------------------------------------------
        # Candidate answer
        # ----------------------------------------------------

        if question.get(
            "candidate_answer"
        ):

            candidate_answer_count += 1

        else:

            warnings.append(
                f"{question_id or index}: "
                "Candidate answer is missing."
            )

        # ----------------------------------------------------
        # Question score
        # ----------------------------------------------------

        if "question_score" in question:

            question_score_count += 1

        else:

            warnings.append(
                f"{question_id or index}: "
                "Question score is missing."
            )

    # --------------------------------------------------------
    # Detect duplicate question IDs
    # --------------------------------------------------------

    duplicate_ids = sorted(
        {
            question_id
            for question_id in question_ids
            if question_ids.count(
                question_id
            ) > 1
        }
    )

    if duplicate_ids:

        errors.append(
            "Duplicate question IDs: "
            + ", ".join(
                duplicate_ids
            )
        )

    # --------------------------------------------------------
    # Validate question count
    # --------------------------------------------------------

    expected_count = data.get(
        "total_questions"
    )

    if (
        expected_count is not None
        and expected_count != len(questions)
    ):

        errors.append(
            "Question count does not match "
            "question_scores."
        )

    # --------------------------------------------------------
    # Return validation result
    # --------------------------------------------------------

    return {

        "valid": not errors,

        "errors": errors,

        "warnings": warnings,

        "total_questions": len(
            questions
        ),

        "duplicate_question_count": len(
            duplicate_ids
        ),

        "question_text_available":
            question_text_count,

        "candidate_answer_available":
            candidate_answer_count,

        "question_score_available":
            question_score_count
    }


# ============================================================
# VALIDATE PARAMETER SCORES
# ============================================================

def validate_parameter_scores(data):
    """
    Validate the four HR parameter averages.
    """

    errors = []

    parameter_scores = data.get(
        "parameter_averages",
        {}
    )

    # --------------------------------------------------------
    # Validate every required parameter
    # --------------------------------------------------------

    for parameter in SCORING_WEIGHTS:

        if parameter not in parameter_scores:

            errors.append(
                f"Missing parameter score: "
                f"{parameter}"
            )

            continue

        try:

            validate_score(
                parameter_scores[
                    parameter
                ],
                parameter
            )

        except ValueError as error:

            errors.append(
                str(error)
            )

    return {

        "valid": not errors,

        "errors": errors
    }


# ============================================================
# EXTRACT DAY 42 QUESTION VALIDATION
# ============================================================

def extract_day42_question_validation(
    stability_data
):
    """
    Extract question validation information
    from the Day 42 stability result.

    Important:
    Day 42 stores these values inside:

        interview_stability
            -> question_validation

    Example:

        question_validation:
            question_text_available
            candidate_answer_available
            response_status_available
            complete_questions
    """

    interview_stability = (
        stability_data.get(
            "interview_stability",
            {}
        )
    )

    question_validation = (
        interview_stability.get(
            "question_validation",
            {}
        )
    )

    return (
        interview_stability,
        question_validation
    )


# ============================================================
# BUILD FINAL RESULT
# ============================================================

def build_result(
    day37_data,
    stability_data,
    refined_data,
    interview_validation,
    score_validation
):
    """
    Build the complete Day 45 final result.
    """

    # --------------------------------------------------------
    # Parameter scores
    # --------------------------------------------------------

    parameter_scores = day37_data[
        "parameter_averages"
    ]

    # --------------------------------------------------------
    # Day 42 stability information
    # --------------------------------------------------------

    (
        interview_stability,
        question_validation
    ) = extract_day42_question_validation(
        stability_data
    )

    # --------------------------------------------------------
    # Refined score
    # --------------------------------------------------------

    refined_score = refined_data.get(
        "refined_hr_score"
    )

    validate_score(
        refined_score,
        "refined_hr_score"
    )

    # --------------------------------------------------------
    # Original Day 37 score
    # --------------------------------------------------------

    original_score = day37_data.get(
        "final_hr_interview_score"
    )

    score_difference = None

    if original_score is not None:

        validate_score(
            original_score,
            "original_hr_score"
        )

        score_difference = round(
            refined_score
            - float(original_score),
            2
        )

    # --------------------------------------------------------
    # Stability status
    # --------------------------------------------------------

    stability_valid = (
        interview_stability.get(
            "stable",
            False
        )
    )

    # --------------------------------------------------------
    # Refined score validation
    # --------------------------------------------------------

    refined_score_valid = (
        refined_data.get(
            "score_difference"
        ) == 0.0
    )

    # --------------------------------------------------------
    # Overall status
    # --------------------------------------------------------

    if (
        interview_validation["valid"]
        and score_validation["valid"]
        and stability_valid
        and refined_score_valid
    ):

        overall_status = "SUCCESS"

    else:

        overall_status = "NEEDS_REVIEW"

    # --------------------------------------------------------
    # Duplicate question count
    # --------------------------------------------------------

    duplicate_questions = (
        interview_stability.get(
            "duplicate_questions",
            []
        )
    )

    duplicate_question_count = len(
        duplicate_questions
    )

    # --------------------------------------------------------
    # Build result
    # --------------------------------------------------------

    return {

        "system":
            "ZecPath Day 45 "
            "Final HR Interview AI",

        "source":
            str(DAY37_RESULT),

        "stability_source":
            str(DAY42_STABILITY_RESULT),

        "refined_score_source":
            str(DAY42_REFINED_RESULT),

        "candidate_id":
            day37_data.get(
                "candidate_id"
            ),

        "job_id":
            day37_data.get(
                "job_id"
            ),

        "total_questions":
            day37_data.get(
                "total_questions"
            ),

        # ----------------------------------------------------
        # Complete question information
        # ----------------------------------------------------

        "questions":
            day37_data.get(
                "question_scores",
                []
            ),

        # ----------------------------------------------------
        # Scoring
        # ----------------------------------------------------

        "scoring_weights":
            SCORING_WEIGHTS,

        "parameter_scores":
            parameter_scores,

        "weighted_contributions":
            refined_data.get(
                "weighted_contributions",
                {}
            ),

        "original_hr_score":
            original_score,

        "final_hr_score":
            refined_score,

        "score_difference":
            score_difference,

        # ----------------------------------------------------
        # Day 42 stability
        # ----------------------------------------------------

        "day42_stability": {

            "stable":
                stability_valid,

            "total_questions":
                interview_stability.get(
                    "total_questions",
                    0
                ),

            "duplicate_question_count":
                duplicate_question_count,

            "duplicate_questions":
                duplicate_questions,

            "errors":
                interview_stability.get(
                    "errors",
                    []
                ),

            "warnings":
                interview_stability.get(
                    "warnings",
                    []
                ),

            "question_validation": {

                "question_text_available":
                    question_validation.get(
                        "question_text_available",
                        0
                    ),

                "candidate_answer_available":
                    question_validation.get(
                        "candidate_answer_available",
                        0
                    ),

                "response_status_available":
                    question_validation.get(
                        "response_status_available",
                        0
                    ),

                "complete_questions":
                    question_validation.get(
                        "complete_questions",
                        0
                    )
            }
        },

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        "validation": {

            "interview_structure":
                interview_validation,

            "parameter_scores":
                score_validation,

            "refined_score_validation": {

                "valid":
                    refined_score_valid
            }
        },

        # ----------------------------------------------------
        # Explainability
        # ----------------------------------------------------

        "explainability": {

            "formula":
                "Answer Relevance x 0.30 + "
                "Communication x 0.25 + "
                "Confidence x 0.20 + "
                "Consistency x 0.25",

            "description":
                "The final HR score uses the "
                "validated Day 37 parameter "
                "averages and the refined "
                "Day 42 scoring result."
        },

        # ----------------------------------------------------
        # Final status
        # ----------------------------------------------------

        "overall_status":
            overall_status
    }


# ============================================================
# SAVE RESULT
# ============================================================

def save_result(result):
    """
    Save the final Day 45 result.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4
        )

    return OUTPUT_FILE


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 70)

    print(
        "       ZecPath DAY 45 - "
        "FINAL HR INTERVIEW AI"
    )

    print("=" * 70)

    # ========================================================
    # LOAD DAY 37
    # ========================================================

    print(
        "\nLoading updated Day 37 HR result..."
    )

    print(
        f"Source: {DAY37_RESULT}"
    )

    day37_data = load_json(
        DAY37_RESULT
    )

    print(
        f"Candidate : "
        f"{day37_data.get('candidate_id')}"
    )

    print(
        f"Job       : "
        f"{day37_data.get('job_id')}"
    )

    print(
        f"Questions : "
        f"{day37_data.get('total_questions')}"
    )

    # ========================================================
    # LOAD DAY 42 STABILITY
    # ========================================================

    print(
        "\nLoading Day 42 stability result..."
    )

    print(
        f"Source: {DAY42_STABILITY_RESULT}"
    )

    stability_data = load_json(
        DAY42_STABILITY_RESULT
    )

    (
        interview_stability,
        question_validation
    ) = extract_day42_question_validation(
        stability_data
    )

    # --------------------------------------------------------
    # Display Day 42 stability
    # --------------------------------------------------------

    stability_status = (
        "PASS"
        if interview_stability.get(
            "stable",
            False
        )
        else "REVIEW"
    )

    print(
        "Interview Stability : "
        f"{stability_status}"
    )

    print(
        "Question Text       : "
        f"{question_validation.get(
            'question_text_available',
            0
        )}"
    )

    print(
        "Candidate Answers   : "
        f"{question_validation.get(
            'candidate_answer_available',
            0
        )}"
    )

    print(
        "Response Status     : "
        f"{question_validation.get(
            'response_status_available',
            0
        )}"
    )

    print(
        "Complete Questions  : "
        f"{question_validation.get(
            'complete_questions',
            0
        )}"
    )

    # ========================================================
    # LOAD DAY 42 REFINED SCORE
    # ========================================================

    print(
        "\nLoading Day 42 refined scoring result..."
    )

    print(
        f"Source: {DAY42_REFINED_RESULT}"
    )

    refined_data = load_json(
        DAY42_REFINED_RESULT
    )

    print(
        "Refined HR Score    : "
        f"{refined_data.get('refined_hr_score')}"
    )

    print(
        "Score Difference    : "
        f"{refined_data.get('score_difference')}"
    )

    # ========================================================
    # VALIDATE WEIGHTS
    # ========================================================

    print(
        "\nValidating scoring configuration..."
    )

    validate_weights(
        SCORING_WEIGHTS
    )

    print(
        "PASS - Scoring weights are valid."
    )

    # ========================================================
    # VALIDATE DAY 37 INTERVIEW
    # ========================================================

    print(
        "\nValidating updated Day 37 interview..."
    )

    interview_validation = (
        validate_interview_data(
            day37_data
        )
    )

    if interview_validation["valid"]:

        print(
            "PASS - Interview structure is valid."
        )

    else:

        print(
            "FAIL - Interview structure "
            "requires review."
        )

    print(
        "Question text available : "
        f"{interview_validation[
            'question_text_available'
        ]}"
    )

    print(
        "Candidate answers       : "
        f"{interview_validation[
            'candidate_answer_available'
        ]}"
    )

    print(
        "Question scores         : "
        f"{interview_validation[
            'question_score_available'
        ]}"
    )

    print(
        "Duplicate questions     : "
        f"{interview_validation[
            'duplicate_question_count'
        ]}"
    )

    # --------------------------------------------------------
    # Print warnings
    # --------------------------------------------------------

    for warning in interview_validation[
        "warnings"
    ]:

        print(
            f"  WARNING: {warning}"
        )

    # ========================================================
    # VALIDATE PARAMETER SCORES
    # ========================================================

    print(
        "\nValidating parameter scores..."
    )

    score_validation = (
        validate_parameter_scores(
            day37_data
        )
    )

    if score_validation["valid"]:

        print(
            "PASS - Parameter scores are valid."
        )

    else:

        print(
            "FAIL - Parameter scores "
            "require review."
        )

    for error in score_validation[
        "errors"
    ]:

        print(
            f"  ERROR: {error}"
        )

    # ========================================================
    # BUILD FINAL RESULT
    # ========================================================

    result = build_result(
        day37_data,
        stability_data,
        refined_data,
        interview_validation,
        score_validation
    )

    # ========================================================
    # DISPLAY SCORING BREAKDOWN
    # ========================================================

    print(
        "\nScoring Breakdown:"
    )

    for parameter, score in (
        result[
            "parameter_scores"
        ].items()
    ):

        weight = (
            result[
                "scoring_weights"
            ][parameter]
            * 100
        )

        contribution = (
            result[
                "weighted_contributions"
            ][parameter]
        )

        print(
            f"  {parameter:18} "
            f"Score: {score:6.2f} "
            f"Weight: {weight:5.1f}% "
            f"Contribution: {contribution:6.2f}"
        )

    # ========================================================
    # FINAL SCORE
    # ========================================================

    print(
        "\nOriginal HR Score : "
        f"{result['original_hr_score']}"
    )

    print(
        "Final HR Score    : "
        f"{result['final_hr_score']}"
    )

    print(
        "Difference        : "
        f"{result['score_difference']}"
    )

    print(
        "Overall Status    : "
        f"{result['overall_status']}"
    )

    # ========================================================
    # SAVE
    # ========================================================

    output_file = save_result(
        result
    )

    print(
        "\nFinal result saved to:"
    )

    print(
        output_file
    )

    print("=" * 70)


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()