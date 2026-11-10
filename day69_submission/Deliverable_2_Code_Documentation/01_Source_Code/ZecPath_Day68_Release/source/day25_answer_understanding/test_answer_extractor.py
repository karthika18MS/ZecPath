from answer_extractor import AnswerExtractor


def main():

    extractor = AnswerExtractor()

    test_cases = [

        {
            "name": "Skills",
            "answer": (
                "I work with Python, Django, "
                "FastAPI and PostgreSQL."
            )
        },

        {
            "name": "Experience",
            "answer": (
                "I have three years of "
                "backend development experience."
            )
        },

        {
            "name": "Immediate Availability",
            "answer": (
                "I can join immediately."
            )
        },

        {
            "name": "Notice Period",
            "answer": (
                "I can join after 30 days."
            )
        },

        {
            "name": "Salary",
            "answer": (
                "I expect 6 lakhs per year."
            )
        },

        {
            "name": "Combined",
            "answer": (
                "I have three years of backend "
                "development experience with "
                "Python, Django and Docker. "
                "I can join immediately and "
                "expect 6 lakhs per year."
            )
        }
    ]

    print("=" * 70)
    print("ANSWER EXTRACTOR TEST")
    print("=" * 70)

    passed = 0
    failed = 0

    for index, test in enumerate(
        test_cases,
        start=1
    ):

        result = extractor.extract_all(
            test["answer"]
        )

        print(
            f"\nTest {index}: {test['name']}"
        )

        print(
            f"Answer: {test['answer']}"
        )

        print(
            "Extracted:"
        )

        print(result)

        if result:
            passed += 1
            print("Status: PASS")
        else:
            failed += 1
            print("Status: FAIL")

    print("\n" + "=" * 70)
    print("ANSWER EXTRACTOR TEST COMPLETED")
    print("=" * 70)

    print(f"Total : {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    print("=" * 70)


if __name__ == "__main__":
    main()