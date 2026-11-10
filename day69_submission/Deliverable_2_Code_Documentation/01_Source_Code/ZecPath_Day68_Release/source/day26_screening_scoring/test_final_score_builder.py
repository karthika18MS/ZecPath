import json
import os

from final_score_builder import FinalScoreBuilder


def run_test(name, condition):

    status = "PASS" if condition else "FAIL"

    print(
        f"{name:<45} {status}"
    )

    return condition


def validate_final_result(result):
    """
    Validate the structure of the final score object.
    """

    required_fields = [
        "candidate_id",
        "job_id",
        "screening_summary",
        "average_scores",
        "final_screening_score",
        "score_scale",
        "explanation",
        "question_scores",
        "created_at"
    ]

    for field in required_fields:

        if field not in result:
            return False

    average_scores = result[
        "average_scores"
    ]

    required_parameters = {
        "clarity",
        "relevance",
        "completeness",
        "consistency"
    }

    if set(average_scores.keys()) != required_parameters:
        return False

    if not 0 <= result[
        "final_screening_score"
    ] <= 100:
        return False

    if result["score_scale"] != "0-100":
        return False

    return True


if __name__ == "__main__":

    print("=" * 70)
    print("FINAL SCORE BUILDER TEST")
    print("=" * 70)

    builder = FinalScoreBuilder()

    passed = 0
    failed = 0

    # --------------------------------------------------
    # Test data
    # --------------------------------------------------

    question_scores = [

        {
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
                    "Answer is clear and easy to understand."
                ],
                "weaknesses": []
            }
        },

        {
            "candidate_id": "candidate_006",
            "job_id": "JOB_BACKEND_001",
            "question_id": "BACKEND_SKILLS_001",

            "question": (
                "Which technical skills do you have?"
            ),

            "question_category": "skills",

            "scores": {
                "clarity": 8,
                "relevance": 9,
                "completeness": 9,
                "consistency": 8
            },

            "weighted_score": 8.5,
            "normalized_score": 85.0,

            "answer_status": "valid",
            "intent": "skills",
            "off_topic": False,

            "explanation": {
                "strengths": [
                    "Answer directly addresses the question."
                ],
                "weaknesses": [
                    "More technical details could be provided."
                ]
            }
        },

        {
            "candidate_id": "candidate_006",
            "job_id": "JOB_BACKEND_001",
            "question_id": "BACKEND_LOCATION_001",

            "question": (
                "Where are you currently located?"
            ),

            "question_category": "location",

            "scores": {
                "clarity": 9,
                "relevance": 10,
                "completeness": 8,
                "consistency": 9
            },

            "weighted_score": 9.0,
            "normalized_score": 90.0,

            "answer_status": "valid",
            "intent": "location",
            "off_topic": False,

            "explanation": {
                "strengths": [
                    "Answer directly addresses the question."
                ],
                "weaknesses": []
            }
        }
    ]

    # --------------------------------------------------
    # Test 1: Final score calculation
    # --------------------------------------------------

    final_result = builder.build_final_score(
        candidate_id="candidate_006",
        job_id="JOB_BACKEND_001",
        question_scores=question_scores
    )

    expected_score = (
        95.0 + 85.0 + 90.0
    ) / 3

    expected_score = round(
        expected_score,
        2
    )

    if run_test(
        "1. Final score calculation",
        (
            final_result[
                "final_screening_score"
            ] == expected_score
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 2: Question count
    # --------------------------------------------------

    if run_test(
        "2. Total question count",
        (
            final_result[
                "screening_summary"
            ][
                "total_questions"
            ] == 3
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 3: Answered question count
    # --------------------------------------------------

    if run_test(
        "3. Answered question count",
        (
            final_result[
                "screening_summary"
            ][
                "answered_questions"
            ] == 3
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 4: Average parameter scores
    # --------------------------------------------------

    average_scores = final_result[
        "average_scores"
    ]

    expected_clarity = round(
        (9 + 8 + 9) / 3,
        2
    )

    expected_relevance = round(
        (10 + 9 + 10) / 3,
        2
    )

    expected_completeness = round(
        (10 + 9 + 8) / 3,
        2
    )

    expected_consistency = round(
        (9 + 8 + 9) / 3,
        2
    )

    if run_test(
        "4. Average parameter scores",
        (
            average_scores["clarity"]
            == expected_clarity
            and
            average_scores["relevance"]
            == expected_relevance
            and
            average_scores["completeness"]
            == expected_completeness
            and
            average_scores["consistency"]
            == expected_consistency
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 5: Explanation
    # --------------------------------------------------

    if run_test(
        "5. Explainable strengths and weaknesses",
        (
            len(
                final_result[
                    "explanation"
                ]["strengths"]
            ) > 0
            and
            len(
                final_result[
                    "explanation"
                ]["weaknesses"]
            ) > 0
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 6: Question scores retained
    # --------------------------------------------------

    if run_test(
        "6. Question-level scores retained",
        (
            len(
                final_result[
                    "question_scores"
                ]
            ) == 3
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 7: Final result structure
    # --------------------------------------------------

    if run_test(
        "7. Final score object structure",
        validate_final_result(
            final_result
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 8: JSON storage
    # --------------------------------------------------

    filename = (
        "test_final_score.json"
    )

    saved_path = builder.save_final_score(
        final_result,
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
                    "final_screening_score"
                ]
                == expected_score
            )

        except Exception:

            valid_json = False

    if run_test(
        "8. Final score JSON storage",
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