import json
import os

from question_score_breakdown import QuestionScoreBreakdown


def validate_breakdown(breakdown):
    """
    Validate the structure of a per-question
    score breakdown.
    """

    required_fields = [
        "candidate_id",
        "job_id",
        "question_id",
        "question",
        "question_category",
        "scores",
        "weighted_score",
        "normalized_score",
        "answer_status",
        "intent",
        "off_topic",
        "explanation"
    ]

    for field in required_fields:

        if field not in breakdown:
            return False

    required_scores = {
        "clarity",
        "relevance",
        "completeness",
        "consistency"
    }

    if set(breakdown["scores"].keys()) != required_scores:
        return False

    if not 0 <= breakdown["weighted_score"] <= 10:
        return False

    if not 0 <= breakdown["normalized_score"] <= 100:
        return False

    if "strengths" not in breakdown["explanation"]:
        return False

    if "weaknesses" not in breakdown["explanation"]:
        return False

    return True


def run_test(name, condition):

    status = "PASS" if condition else "FAIL"

    print(
        f"{name:<40} {status}"
    )

    return condition


if __name__ == "__main__":

    print("=" * 70)
    print("PER-QUESTION SCORE BREAKDOWN TEST")
    print("=" * 70)

    builder = QuestionScoreBreakdown()

    passed = 0
    failed = 0

    # --------------------------------------------------
    # Test 1: Strong Experience Question
    # --------------------------------------------------

    experience_result = {

        "candidate_id": "candidate_006",
        "job_id": "JOB_BACKEND_001",
        "question_id": "BACKEND_EXP_001",

        "question": (
            "How many years of backend development "
            "experience do you have?"
        ),

        "question_category": "experience",

        "scores": {
            "clarity": 9,
            "relevance": 10,
            "completeness": 10,
            "consistency": 9
        },

        "weighted_score": 9.5,
        "normalized_score": 95.0,

        "answer_status": "valid",
        "intent": "experience",
        "off_topic": False,

        "explanation": {
            "strengths": [
                "Answer is clear and easy to understand.",
                "Answer directly addresses the question."
            ],
            "weaknesses": []
        }
    }

    experience_breakdown = (
        builder.build_question_breakdown(
            experience_result
        )
    )

    if run_test(
        "1. Experience question breakdown",
        validate_breakdown(
            experience_breakdown
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 2: Technical Skills Question
    # --------------------------------------------------

    skills_result = {

        "candidate_id": "candidate_006",
        "job_id": "JOB_BACKEND_001",
        "question_id": "BACKEND_SKILLS_001",

        "question": (
            "Which technical skills do you have?"
        ),

        "question_category": "skills",

        "scores": {
            "clarity": 9,
            "relevance": 10,
            "completeness": 10,
            "consistency": 9
        },

        "weighted_score": 9.5,
        "normalized_score": 95.0,

        "answer_status": "valid",
        "intent": "skills",
        "off_topic": False,

        "explanation": {
            "strengths": [
                "Answer directly addresses the question."
            ],
            "weaknesses": []
        }
    }

    skills_breakdown = (
        builder.build_question_breakdown(
            skills_result
        )
    )

    if run_test(
        "2. Skills question breakdown",
        (
            validate_breakdown(
                skills_breakdown
            )
            and
            skills_breakdown["question_category"]
            == "skills"
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 3: Off-topic Question
    # --------------------------------------------------

    off_topic_result = {

        "candidate_id": "candidate_006",
        "job_id": "JOB_BACKEND_001",
        "question_id": "BACKEND_EXP_001",

        "question": (
            "How many years of backend development "
            "experience do you have?"
        ),

        "question_category": "experience",

        "scores": {
            "clarity": 2,
            "relevance": 1,
            "completeness": 1,
            "consistency": 3
        },

        "weighted_score": 1.75,
        "normalized_score": 17.5,

        "answer_status": "valid",
        "intent": "off_topic",
        "off_topic": True,

        "explanation": {
            "strengths": [],
            "weaknesses": [
                "Answer does not address the screening question."
            ]
        }
    }

    off_topic_breakdown = (
        builder.build_question_breakdown(
            off_topic_result
        )
    )

    if run_test(
        "3. Off-topic question breakdown",
        (
            validate_breakdown(
                off_topic_breakdown
            )
            and
            off_topic_breakdown["off_topic"] is True
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 4: No Response
    # --------------------------------------------------

    no_response_result = {

        "candidate_id": "candidate_006",
        "job_id": "JOB_BACKEND_001",
        "question_id": "BACKEND_EXP_001",

        "question": (
            "How many years of backend development "
            "experience do you have?"
        ),

        "question_category": "experience",

        "scores": {
            "clarity": 0,
            "relevance": 0,
            "completeness": 0,
            "consistency": 0
        },

        "weighted_score": 0.0,
        "normalized_score": 0.0,

        "answer_status": "no_response",
        "intent": "no_response",
        "off_topic": False,

        "explanation": {
            "strengths": [],
            "weaknesses": [
                "No meaningful answer was provided."
            ]
        }
    }

    no_response_breakdown = (
        builder.build_question_breakdown(
            no_response_result
        )
    )

    if run_test(
        "4. No-response question breakdown",
        (
            validate_breakdown(
                no_response_breakdown
            )
            and
            no_response_breakdown[
                "normalized_score"
            ] == 0.0
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 5: Candidate-level breakdown
    # --------------------------------------------------

    candidate_results = [
        experience_result,
        skills_result,
        off_topic_result,
        no_response_result
    ]

    candidate_breakdown = (
        builder.build_candidate_breakdown(
            candidate_results
        )
    )

    if run_test(
        "5. Candidate question collection",
        (
            candidate_breakdown[
                "total_questions"
            ] == 4
            and
            len(
                candidate_breakdown[
                    "question_scores"
                ]
            ) == 4
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 6: JSON save
    # --------------------------------------------------

    filename = (
        "test_question_score_breakdown.json"
    )

    saved_path = builder.save_breakdown(
        candidate_breakdown,
        filename
    )

    file_exists = os.path.exists(
        saved_path
    )

    valid_json = False

    if file_exists:

        try:

            with open(
                saved_path,
                "r",
                encoding="utf-8"
            ) as file:

                loaded_data = json.load(file)

            valid_json = (
                loaded_data[
                    "total_questions"
                ] == 4
            )

        except Exception:
            valid_json = False

    if run_test(
        "6. JSON result storage",
        file_exists and valid_json
    ):
        passed += 1
    else:
        failed += 1

    print("=" * 70)
    print(f"Total : {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 70)