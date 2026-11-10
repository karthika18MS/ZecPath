from confidence_analyzer import ConfidenceAnalyzer


def run_test(test_name, condition):
    """
    Print test result and return whether the test passed.
    """

    status = "PASS" if condition else "FAIL"

    print(f"{test_name:<55} {status}")

    return condition


if __name__ == "__main__":

    print("=" * 70)
    print("CONFIDENCE ANALYZER TEST")
    print("=" * 70)

    analyzer = ConfidenceAnalyzer()

    passed = 0
    failed = 0

    # --------------------------------------------------
    # Test 1: No hesitation
    # --------------------------------------------------

    result = analyzer.detect_hesitation(
        "I have three years of backend development experience."
    )

    if run_test(
        "1. No hesitation detection",
        result["detected"] is False
        and result["count"] == 0
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 2: Hesitation detection
    # --------------------------------------------------

    result = analyzer.detect_hesitation(
        "Um, I think I have maybe three years of experience."
    )

    if run_test(
        "2. Hesitation pattern detection",
        result["detected"] is True
        and result["count"] >= 3
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 3: Uncertainty detection
    # --------------------------------------------------

    result = analyzer.detect_uncertainty(
        "I think I have maybe three years of experience."
    )

    if run_test(
        "3. Uncertainty detection",
        result["detected"] is True
        and result["count"] >= 2
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 4: No uncertainty
    # --------------------------------------------------

    result = analyzer.detect_uncertainty(
        "I have three years of backend development experience."
    )

    if run_test(
        "4. No uncertainty detection",
        result["detected"] is False
        and result["count"] == 0
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 5: Response length
    # --------------------------------------------------

    result = analyzer.measure_response_length(
        "I have three years of backend experience."
    )

    if run_test(
        "5. Response length measurement",
        result["word_count"] == 7
        and result["character_count"] > 0
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 6: Empty response length
    # --------------------------------------------------

    result = analyzer.measure_response_length("")

    if run_test(
        "6. Empty response length",
        result["word_count"] == 0
        and result["character_count"] == 0
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 7: WPM calculation
    # --------------------------------------------------

    # 20 words in 10 seconds
    # = 120 words per minute

    result = analyzer.calculate_words_per_minute(
        word_count=20,
        duration_seconds=10
    )

    if run_test(
        "7. Words-per-minute calculation",
        result == 120.0
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 8: Slow pace
    # --------------------------------------------------

    result = analyzer.classify_pace(60)

    if run_test(
        "8. Slow pace classification",
        result == "slow"
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 9: Normal pace
    # --------------------------------------------------

    result = analyzer.classify_pace(120)

    if run_test(
        "9. Normal pace classification",
        result == "normal"
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 10: Fast pace
    # --------------------------------------------------

    result = analyzer.classify_pace(180)

    if run_test(
        "10. Fast pace classification",
        result == "fast"
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 11: Complete pace analysis
    # --------------------------------------------------

    result = analyzer.analyze_pace(
        word_count=20,
        duration_seconds=10
    )

    if run_test(
        "11. Complete pace analysis",
        (
            result["duration_seconds"] == 10
            and result["words_per_minute"] == 120.0
            and result["classification"] == "normal"
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 12: Complete response analysis
    # --------------------------------------------------

    result = analyzer.analyze_response(
        candidate_id="candidate_006",
        question_id="BACKEND_EXP_001",
        answer=(
            "Um, I think I have maybe three years "
            "of backend development experience."
        ),
        duration_seconds=8.0
    )

    if run_test(
        "12. Complete confidence analysis",
        (
            result["candidate_id"] == "candidate_006"
            and result["question_id"] == "BACKEND_EXP_001"
            and "response_length" in result
            and "pace" in result
            and "hesitation" in result
            and "uncertainty" in result
            and "created_at" in result
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 13: Hesitation in complete analysis
    # --------------------------------------------------

    if run_test(
        "13. Hesitation in complete analysis",
        (
            result["hesitation"]["detected"] is True
            and result["hesitation"]["count"] >= 3
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 14: Uncertainty in complete analysis
    # --------------------------------------------------

    if run_test(
        "14. Uncertainty in complete analysis",
        (
            result["uncertainty"]["detected"] is True
            and result["uncertainty"]["count"] >= 2
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 15: Response pace in complete analysis
    # --------------------------------------------------

    if run_test(
        "15. Response pace in complete analysis",
        (
            result["pace"]["words_per_minute"] > 0
            and result["pace"]["classification"] == "normal"
        )
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Final test summary
    # --------------------------------------------------

    print("=" * 70)
    print(f"Total : {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 70)