from intent_classifier import IntentClassifier


def main():

    classifier = IntentClassifier()

    test_cases = [

        {
            "name": "Relevant Experience",
            "question": "How many years of experience do you have?",
            "answer": "I have three years of backend development experience.",
            "category": "experience",
            "expected": False
        },

        {
            "name": "Relevant Skills",
            "question": "What technical skills do you have?",
            "answer": "I know Python, Django and Docker.",
            "category": "skills",
            "expected": False
        },

        {
            "name": "Relevant Location",
            "question": "Where are you located?",
            "answer": "I am currently in Kochi.",
            "category": "location",
            "expected": False
        },

        {
            "name": "Relevant Salary",
            "question": "What are your salary expectations?",
            "answer": "I expect 6 lakhs per year.",
            "category": "salary",
            "expected": False
        },

        {
            "name": "Relevant Availability",
            "question": "When can you join?",
            "answer": "I can join immediately.",
            "category": "availability",
            "expected": False
        },

        {
            "name": "Relevant Notice",
            "question": "What is your notice period?",
            "answer": "My notice period is 30 days.",
            "category": "notice_period",
            "expected": False
        },

        {
            "name": "Movies",
            "question": "What technical skills do you have?",
            "answer": "I really enjoy watching movies.",
            "category": "skills",
            "expected": True
        },

        {
            "name": "Cooking",
            "question": "How many years of experience do you have?",
            "answer": "I enjoy cooking with my family.",
            "category": "experience",
            "expected": True
        },

        {
            "name": "Cricket",
            "question": "What technical skills do you have?",
            "answer": "I love playing cricket.",
            "category": "skills",
            "expected": True
        },

        {
            "name": "Mismatch",
            "question": "What are your salary expectations?",
            "answer": "I completed my MCA from a university.",
            "category": "salary",
            "expected": True
        },

        {
            "name": "Vague",
            "question": "How many years of experience do you have?",
            "answer": "I don't know.",
            "category": "experience",
            "expected": False
        },

        {
            "name": "Relevant Technical",
            "question": "What technical skills do you have?",
            "answer": "I have worked with Python and PostgreSQL.",
            "category": "skills",
            "expected": False
        }
    ]

    passed = 0
    failed = 0

    print("=" * 70)
    print("OFF-TOPIC DETECTION TEST")
    print("=" * 70)

    for index, test in enumerate(
        test_cases,
        start=1
    ):

        result = classifier.detect_off_topic(
            question=test["question"],
            answer=test["answer"],
            question_category=test["category"]
        )

        actual = result["is_off_topic"]

        if actual == test["expected"]:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1

        print(
            f"{index}. {test['name']:<22} "
            f"Expected: {str(test['expected']):<5} "
            f"Actual: {str(actual):<5} "
            f"{status}"
        )

    print("=" * 70)
    print(f"Total : {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 70)


if __name__ == "__main__":
    main()