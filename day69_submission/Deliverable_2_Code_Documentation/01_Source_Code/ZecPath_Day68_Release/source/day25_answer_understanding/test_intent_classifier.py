from intent_classifier import IntentClassifier


def main():

    classifier = IntentClassifier()

    test_cases = [

        {
            "name": "Introduction",
            "question": "Can you introduce yourself?",
            "answer": "My name is Karthika and I am an MCA graduate.",
            "category": "introduction",
            "expected": "introduction"
        },

        {
            "name": "Education",
            "question": "What is your highest qualification?",
            "answer": "I completed my MCA.",
            "category": "education",
            "expected": "education"
        },

        {
            "name": "Experience",
            "question": "How many years of experience do you have?",
            "answer": "I have three years of backend development experience.",
            "category": "experience",
            "expected": "experience"
        },

        {
            "name": "Skills",
            "question": "What technical skills do you have?",
            "answer": "I have experience with Python, Django and Docker.",
            "category": "skills",
            "expected": "skills"
        },

        {
            "name": "Location",
            "question": "Where are you currently located?",
            "answer": "I am currently located in Kochi.",
            "category": "location",
            "expected": "location"
        },

        {
            "name": "Salary",
            "question": "What are your salary expectations?",
            "answer": "I expect around 6 lakhs per year.",
            "category": "salary",
            "expected": "salary"
        },

        {
            "name": "Notice Period",
            "question": "What is your notice period?",
            "answer": "My notice period is 30 days.",
            "category": "notice_period",
            "expected": "notice_period"
        },

        {
            "name": "Availability",
            "question": "When can you join?",
            "answer": "I can join immediately.",
            "category": "availability",
            "expected": "availability"
        },

        {
            "name": "Vague",
            "question": "How many years of experience do you have?",
            "answer": "I don't know.",
            "category": "experience",
            "expected": "vague"
        },

        {
            "name": "Off Topic",
            "question": "What technical skills do you have?",
            "answer": "I really enjoy watching movies.",
            "category": "skills",
            "expected": "off_topic"
        },

        {
            "name": "No Response",
            "question": "Where are you located?",
            "answer": "",
            "category": "location",
            "expected": "no_response"
        }
    ]

    passed = 0
    failed = 0

    print("=" * 70)
    print("INTENT CLASSIFIER TEST")
    print("=" * 70)

    for index, test in enumerate(
        test_cases,
        start=1
    ):

        result = classifier.classify(
            question=test["question"],
            answer=test["answer"],
            question_category=test["category"]
        )

        actual = result["intent"]

        if actual == test["expected"]:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1

        print(
            f"{index}. {test['name']:<18} "
            f"Expected: {test['expected']:<15} "
            f"Actual: {actual:<15} "
            f"{status}"
        )

    print("=" * 70)
    print(f"Total : {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 70)


if __name__ == "__main__":
    main()