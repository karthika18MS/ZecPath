from screening_report_builder import ScreeningReportBuilder


def run_test(test_name, condition):

    status = "PASS" if condition else "FAIL"

    print(
        f"{test_name:<60} {status}"
    )

    return condition


if __name__ == "__main__":

    print("=" * 70)
    print("AI SCREENING REPORT BUILDER TEST")
    print("=" * 70)

    builder = ScreeningReportBuilder()

    passed = 0
    failed = 0

    # --------------------------------------------------
    # Sample Day 25 data
    # --------------------------------------------------

    answer_data = {

        "candidate_id": "candidate_006",

        "job_id": "JOB_BACKEND_001",

        "question_id": "BACKEND_EXP_001",

        "question": (
            "How many years of backend development "
            "experience do you have?"
        ),

        "question_category": "experience",

        "normalized_answer": (
            "I have three years of backend development "
            "experience. I have worked with Python "
            "and Django."
        ),

        "intent": "experience",

        "answer_status": "valid",

        "off_topic": False,

        "semantic_object": {

            "skills": [
                "Python",
                "Django"
            ],

            "experience": {

                "years": 3,

                "months": None,

                "domain": "backend development"
            }
        }
    }

    # --------------------------------------------------
    # Sample Day 26 data
    # --------------------------------------------------

    scoring_data = {

        "candidate_id": "candidate_006",

        "job_id": "JOB_BACKEND_001",

        "screening_summary": {

            "total_questions": 4,

            "answered_questions": 4,

            "no_response_questions": 0,

            "off_topic_questions": 0
        },

        "average_scores": {

            "clarity": 8.75,

            "relevance": 9.75,

            "completeness": 9.5,

            "consistency": 9.0
        },

        "final_screening_score": 92.5,

        "score_scale": "0-100",

        "explanation": {

            "strengths": [],

            "weaknesses": []
        },

        "question_scores": [

            {

                "question_id":
                    "BACKEND_EXP_001",

                "question":
                    "How many years of backend "
                    "development experience do "
                    "you have?",

                "question_category":
                    "experience",

                "normalized_score": 95.0,

                "answer_status": "valid",

                "intent": "experience",

                "off_topic": False,

                "explanation": {

                    "strengths": [
                        "Clear response.",
                        "Relevant experience provided."
                    ],

                    "weaknesses": []
                }
            }
        ]
    }

    # --------------------------------------------------
    # Sample Day 27 data
    # --------------------------------------------------

    behavioral_data = {

        "candidate_id":
            "candidate_006",

        "question_id":
            "BACKEND_SKILLS_001",

        "communication_indicators": {

            "confidence": {
                "score": 100,
                "level": "strong"
            },

            "clarity": {
                "score": 100,
                "level": "strong"
            },

            "engagement": {
                "score": 90,
                "level": "strong"
            },

            "consistency": {
                "score": 100,
                "level": "strong"
            },

            "communication_strength": {
                "score": 97.5,
                "level": "strong"
            }
        },

        "behavioral_signals": {

            "hesitation_count": 0,

            "uncertainty_count": 0,

            "response_word_count": 14,

            "pace": "normal",

            "sentiment": "positive",

            "sentiment_score": 100.0,

            "contradiction_detected": False
        }
    }

    # --------------------------------------------------
    # Test 1: Key answer extraction
    # --------------------------------------------------

    result = builder.extract_key_answers(
        answer_data
    )

    if run_test(
        "1. Key answer extraction",
        (
            result["experience"]["years"] == 3

            and result["experience"]["domain"]
            == "backend development"

            and result["response"]
            == (
                "I have three years of backend "
                "development experience. I have "
                "worked with Python and Django."
            )
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 2: Screening score extraction
    # --------------------------------------------------

    result = builder.extract_screening_score(
        scoring_data
    )

    if run_test(
        "2. Screening score extraction",
        (
            result["final_screening_score"] == 92.5

            and result["score_scale"] == "0-100"

            and result["average_scores"]["clarity"]
            == 8.75
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 3: Question score extraction
    # --------------------------------------------------

    result = builder.extract_question_scores(
        scoring_data
    )

    if run_test(
        "3. Question score extraction",
        (
            len(result) == 1

            and result[0]["question_id"]
            == "BACKEND_EXP_001"

            and result[0]["normalized_score"]
            == 95.0
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 4: Strength extraction
    # --------------------------------------------------

    result = builder.extract_strengths(
        scoring_data,
        behavioral_data
    )

    if run_test(
        "4. Strength extraction",
        (
            len(result) >= 4

            and any(
                "confidence" in item.lower()
                for item in result
            )

            and any(
                "clarity" in item.lower()
                for item in result
            )
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 5: Risk extraction
    # --------------------------------------------------

    result = builder.extract_risks(
        scoring_data,
        behavioral_data
    )

    if run_test(
        "5. Risk extraction",
        isinstance(result, list)
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 6: Missing data detection
    # --------------------------------------------------

    result = builder.identify_missing_data(
        answer_data
    )

    if run_test(
        "6. Missing data detection",
        isinstance(result, list)
        and len(result) == 0
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 7: Skill confirmation
    # --------------------------------------------------

    result = builder.extract_skill_confirmations(
        answer_data
    )

    if run_test(
        "7. Skill confirmation extraction",
        (
            result == [
                "Python",
                "Django"
            ]
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 8: Complete screening report
    # --------------------------------------------------

    result = builder.build_report(

        candidate_id="candidate_006",

        job_id="JOB_BACKEND_001",

        answer_data=answer_data,

        scoring_data=scoring_data,

        behavioral_data=behavioral_data
    )

    if run_test(
        "8. Complete screening report",
        (
            result["report_type"]
            == "AI Screening Report"

            and result["candidate_id"]
            == "candidate_006"

            and result["job_id"]
            == "JOB_BACKEND_001"

            and "key_answers"
            in result

            and "screening_evaluation"
            in result

            and "strengths"
            in result

            and "risks"
            in result

            and "missing_data"
            in result

            and "highlights"
            in result

            and "communication_summary"
            in result

            and "created_at"
            in result
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 9: Final screening score
    # --------------------------------------------------

    if run_test(
        "9. Final screening score included",
        (
            result[
                "screening_evaluation"
            ][
                "final_screening_score"
            ] == 92.5
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 10: Communication strength
    # --------------------------------------------------

    if run_test(
        "10. Communication strength included",
        (
            result[
                "communication_summary"
            ][
                "communication_strength"
            ][
                "score"
            ] == 97.5
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 11: Behavioral signals
    # --------------------------------------------------

    if run_test(
        "11. Behavioral signals included",
        (
            result[
                "behavioral_signals"
            ][
                "sentiment"
            ] == "positive"

            and result[
                "behavioral_signals"
            ][
                "pace"
            ] == "normal"

            and result[
                "behavioral_signals"
            ][
                "contradiction_detected"
            ] is False
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 12: Candidate and job identification
    # --------------------------------------------------

    if run_test(
        "12. Candidate and job identification",
        (
            result["candidate_id"]
            == "candidate_006"

            and result["job_id"]
            == "JOB_BACKEND_001"
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 13: Salary highlight
    # --------------------------------------------------

    if run_test(
        "13. Salary expectation highlight",
        (
            "salary_expectation"
            in result["highlights"]

            and result["highlights"][
                "salary_expectation"
            ] is None
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 14: Availability highlight
    # --------------------------------------------------

    if run_test(
        "14. Availability highlight",
        (
            "availability"
            in result["highlights"]

            and result["highlights"][
                "availability"
            ] is None
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 15: Skill confirmation highlight
    # --------------------------------------------------

    if run_test(
        "15. Skill confirmation highlight",
        (
            result[
                "highlights"
            ][
                "skill_confirmations"
            ]
            == [
                "Python",
                "Django"
            ]
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Final summary
    # --------------------------------------------------

    print("=" * 70)
    print(f"Total : {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 70)