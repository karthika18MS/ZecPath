from sentiment_scorer import SentimentScorer


def run_test(test_name, condition):
    """
    Print test result and return whether the test passed.
    """

    status = "PASS" if condition else "FAIL"

    print(
        f"{test_name:<55} {status}"
    )

    return condition


if __name__ == "__main__":

    print("=" * 70)
    print("SENTIMENT SCORER TEST")
    print("=" * 70)

    scorer = SentimentScorer()

    passed = 0
    failed = 0

    # --------------------------------------------------
    # Test 1: Positive sentiment
    # --------------------------------------------------

    result = scorer.score_response(
        "I really enjoy backend development and I am confident."
    )

    if run_test(
        "1. Positive sentiment detection",
        (
            result["sentiment"] == "positive"
            and result["sentiment_score"] > 50
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 2: Negative sentiment
    # --------------------------------------------------

    result = scorer.score_response(
        "I struggled with the difficult project and felt frustrated."
    )

    if run_test(
        "2. Negative sentiment detection",
        (
            result["sentiment"] == "negative"
            and result["sentiment_score"] < 50
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 3: Neutral sentiment
    # --------------------------------------------------

    result = scorer.score_response(
        "I have three years of backend development experience."
    )

    if run_test(
        "3. Neutral sentiment detection",
        (
            result["sentiment"] == "neutral"
            and result["sentiment_score"] == 50.0
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 4: Equal positive and negative signals
    # --------------------------------------------------

    result = scorer.score_response(
        "The project was excellent but the deployment was difficult."
    )

    if run_test(
        "4. Mixed sentiment detection",
        (
            result["positive_count"] == 1
            and result["negative_count"] == 1
            and result["sentiment_score"] == 50.0
            and result["sentiment"] == "neutral"
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 5: Multiple positive words
    # --------------------------------------------------

    result = scorer.score_response(
        "I am confident, motivated, interested and excited."
    )

    if run_test(
        "5. Multiple positive signals",
        (
            result["positive_count"] == 4
            and result["negative_count"] == 0
            and result["sentiment_score"] == 100.0
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 6: Multiple negative words
    # --------------------------------------------------

    result = scorer.score_response(
        "I was confused, worried, stressed and frustrated."
    )

    if run_test(
        "6. Multiple negative signals",
        (
            result["negative_count"] == 4
            and result["positive_count"] == 0
            and result["sentiment_score"] == 0.0
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 7: Case-insensitive detection
    # --------------------------------------------------

    result = scorer.score_response(
        "I am CONFIDENT and EXCITED about this opportunity."
    )

    if run_test(
        "7. Case-insensitive sentiment detection",
        (
            result["sentiment"] == "positive"
            and result["positive_count"] == 2
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 8: Empty response
    # --------------------------------------------------

    result = scorer.score_response("")

    if run_test(
        "8. Empty response handling",
        (
            result["sentiment"] == "neutral"
            and result["sentiment_score"] == 50.0
            and result["positive_count"] == 0
            and result["negative_count"] == 0
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 9: Complete analysis object
    # --------------------------------------------------

    result = scorer.analyze_response(
        candidate_id="candidate_006",
        question_id="BACKEND_SKILLS_001",
        answer=(
            "I enjoy backend development "
            "and I am confident working with Python."
        )
    )

    if run_test(
        "9. Complete sentiment analysis",
        (
            result["candidate_id"] == "candidate_006"
            and result["question_id"]
            == "BACKEND_SKILLS_001"
            and "raw_answer" in result
            and "normalized_answer" in result
            and "sentiment_analysis" in result
            and "created_at" in result
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