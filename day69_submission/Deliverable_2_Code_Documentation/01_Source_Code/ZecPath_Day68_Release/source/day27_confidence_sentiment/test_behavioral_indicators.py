from behavioral_indicators import BehavioralIndicators


def run_test(test_name, condition):
    """
    Print test result.
    """

    status = "PASS" if condition else "FAIL"

    print(
        f"{test_name:<55} {status}"
    )

    return condition


if __name__ == "__main__":

    print("=" * 70)
    print("BEHAVIORAL INDICATORS TEST")
    print("=" * 70)

    builder = BehavioralIndicators()

    passed = 0
    failed = 0

    # --------------------------------------------------
    # Test 1: Strong confidence
    # --------------------------------------------------

    score = builder.calculate_confidence_indicator(
        hesitation_count=0,
        uncertainty_count=0,
        pace_classification="normal",
        answer_status="valid"
    )

    if run_test(
        "1. Strong confidence indicator",
        score == 100
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 2: Hesitation and uncertainty impact
    # --------------------------------------------------

    score = builder.calculate_confidence_indicator(
        hesitation_count=2,
        uncertainty_count=1,
        pace_classification="normal",
        answer_status="valid"
    )

    if run_test(
        "2. Hesitation and uncertainty impact",
        score == 70
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 3: Clarity
    # --------------------------------------------------

    score = builder.calculate_clarity_indicator(
        response_length={
            "word_count": 14
        },
        hesitation_count=0,
        answer_status="valid"
    )

    if run_test(
        "3. Strong clarity indicator",
        score == 100
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 4: Engagement
    # --------------------------------------------------

    score = builder.calculate_engagement_indicator(
        response_length={
            "word_count": 14
        },
        sentiment="positive",
        answer_status="valid"
    )

    # 60 base + 15 for 7-14 words + 15 positive sentiment
    # = 90

    if run_test(
        "4. Positive engagement indicator",
        score == 90
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 5: Consistency
    # --------------------------------------------------

    score = builder.calculate_consistency_indicator(
        contradiction_detected=False
    )

    if run_test(
        "5. Consistent communication indicator",
        score == 100
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 6: Contradiction impact
    # --------------------------------------------------

    score = builder.calculate_consistency_indicator(
        contradiction_detected=True
    )

    if run_test(
        "6. Contradiction impact",
        score == 30
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 7: Overall communication strength
    # --------------------------------------------------

    score = builder.calculate_communication_strength(
        confidence=100,
        clarity=100,
        engagement=90,
        consistency=100
    )

    # (100 + 100 + 90 + 100) / 4 = 97.5

    if run_test(
        "7. Overall communication strength",
        score == 97.5
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 8: Strong classification
    # --------------------------------------------------

    result = builder.classify_score(90)

    if run_test(
        "8. Strong score classification",
        result == "strong"
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 9: Moderate classification
    # --------------------------------------------------

    result = builder.classify_score(70)

    if run_test(
        "9. Moderate score classification",
        result == "moderate"
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 10: Needs improvement classification
    # --------------------------------------------------

    result = builder.classify_score(40)

    if run_test(
        "10. Needs-improvement classification",
        result == "needs_improvement"
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 11: Complete behavioral report
    # --------------------------------------------------

    confidence_analysis = {

        "response_length": {
            "word_count": 14,
            "character_count": 82
        },

        "pace": {
            "duration_seconds": 8.0,
            "words_per_minute": 105.0,
            "classification": "normal"
        },

        "hesitation": {
            "detected": False,
            "count": 0,
            "patterns": []
        },

        "uncertainty": {
            "detected": False,
            "count": 0,
            "patterns": []
        }
    }

    sentiment_analysis = {

        "sentiment_analysis": {

            "sentiment": "positive",

            "sentiment_score": 100.0,

            "positive_count": 3,

            "negative_count": 0
        }
    }

    contradiction_analysis = {

        "contradiction_analysis": {

            "detected": False,

            "count": 0,

            "types": [],

            "details": []
        }
    }

    result = builder.build_indicators(

        candidate_id="candidate_006",

        question_id="BACKEND_SKILLS_001",

        confidence_analysis=confidence_analysis,

        sentiment_analysis=sentiment_analysis,

        contradiction_analysis=contradiction_analysis,

        answer_status="valid"
    )

    if run_test(
        "11. Complete behavioral indicator report",
        (
            result["candidate_id"]
            == "candidate_006"

            and result["question_id"]
            == "BACKEND_SKILLS_001"

            and "communication_indicators"
            in result

            and "behavioral_signals"
            in result

            and "created_at"
            in result
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 12: Communication strength
    # --------------------------------------------------

    communication = result[
        "communication_indicators"
    ]

    if run_test(
        "12. Communication strength result",
        (
            communication[
                "communication_strength"
            ]["score"] == 97.5

            and communication[
                "communication_strength"
            ]["level"] == "strong"
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 13: Behavioral signals
    # --------------------------------------------------

    signals = result[
        "behavioral_signals"
    ]

    if run_test(
        "13. Behavioral signals included",
        (
            signals["hesitation_count"] == 0

            and signals["uncertainty_count"] == 0

            and signals["response_word_count"] == 14

            and signals["pace"] == "normal"

            and signals["sentiment"] == "positive"

            and signals["sentiment_score"] == 100.0

            and signals[
                "contradiction_detected"
            ] is False
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 14: No-response handling
    # --------------------------------------------------

    result = builder.build_indicators(

        candidate_id="candidate_006",

        question_id="BACKEND_EXP_001",

        confidence_analysis={

            "response_length": {
                "word_count": 0
            },

            "pace": {
                "classification": "unknown"
            },

            "hesitation": {
                "count": 0
            },

            "uncertainty": {
                "count": 0
            }
        },

        sentiment_analysis={
            "sentiment": "neutral",
            "sentiment_score": 50.0
        },

        contradiction_analysis={
            "detected": False
        },

        answer_status="no_response"
    )

    if run_test(
        "14. No-response handling",
        (
            result[
                "communication_indicators"
            ][
                "confidence"
            ]["score"] == 0

            and result[
                "communication_indicators"
            ][
                "clarity"
            ]["score"] == 0

            and result[
                "communication_indicators"
            ][
                "engagement"
            ]["score"] == 0
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