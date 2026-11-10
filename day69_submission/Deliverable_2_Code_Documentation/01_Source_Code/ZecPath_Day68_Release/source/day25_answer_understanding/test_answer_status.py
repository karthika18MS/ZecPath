from intent_classifier import IntentClassifier


def main():

    classifier = IntentClassifier()

    test_cases = [

        # Missing
        ("Empty", "", "no_response"),
        ("No response", "No response", "no_response"),
        ("Inaudible", "[inaudible]", "no_response"),
        ("Unclear", "[unclear]", "no_response"),

        # Vague
        ("Don't know", "I don't know.", "vague"),
        ("Not sure", "I'm not sure.", "vague"),
        ("Maybe", "Maybe around that.", "vague"),
        ("Think so", "I think so.", "vague"),
        ("Probably", "Probably.", "vague"),
        ("No idea", "No idea.", "vague"),

        # Valid
        (
            "Experience",
            "I have three years of experience.",
            "valid"
        ),

        (
            "Skills",
            "I have experience with Python and Django.",
            "valid"
        ),

        (
            "Availability",
            "I can join immediately.",
            "valid"
        ),

        (
            "Salary",
            "I expect 6 lakhs per year.",
            "valid"
        ),

        (
            "Location",
            "I am currently in Kochi.",
            "valid"
        ),

        (
            "Education",
            "I completed my MCA.",
            "valid"
        )
    ]

    passed = 0
    failed = 0

    print("=" * 70)
    print("ANSWER STATUS TEST")
    print("=" * 70)

    for index, (
        name,
        answer,
        expected
    ) in enumerate(
        test_cases,
        start=1
    ):

        result = classifier.detect_answer_status(
            answer
        )

        actual = result["status"]

        if actual == expected:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1

        print(
            f"{index}. {name:<18} "
            f"Expected: {expected:<12} "
            f"Actual: {actual:<12} "
            f"{status}"
        )

    print("=" * 70)
    print(f"Total : {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 70)


if __name__ == "__main__":
    main()