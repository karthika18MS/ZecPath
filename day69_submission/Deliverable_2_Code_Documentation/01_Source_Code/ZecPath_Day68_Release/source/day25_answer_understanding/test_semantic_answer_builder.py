import json

from semantic_answer_builder import (
    SemanticAnswerBuilder
)


def run_test(
    number,
    candidate_id,
    job_id,
    question_id,
    question,
    category,
    raw_answer,
    normalized_answer
):

    builder = SemanticAnswerBuilder()

    result = builder.build(
        candidate_id=candidate_id,
        job_id=job_id,
        question_id=question_id,
        question=question,
        question_category=category,
        raw_answer=raw_answer,
        normalized_answer=normalized_answer
    )

    print("\n" + "-" * 70)

    print(
        f"Test {number}"
    )

    print("-" * 70)

    print(
        f"Question: {question}"
    )

    print(
        f"Answer: {normalized_answer}"
    )

    print(
        "\nSemantic Object:"
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    return result


def main():

    print("=" * 70)
    print("SEMANTIC ANSWER BUILDER TEST")
    print("=" * 70)

    # -----------------------------------------
    # Test 1 - Experience + Skills
    # -----------------------------------------

    result_1 = run_test(
        1,
        "candidate_006",
        "JOB_BACKEND_001",
        "BACKEND_EXP_001",
        "How many years of backend development experience do you have?",
        "experience",
        (
            "Um, I have like three years of backend "
            "development experience. I have worked "
            "with Python and Django."
        ),
        (
            "I have three years of backend "
            "development experience. I have worked "
            "with Python and Django."
        )
    )

    # -----------------------------------------
    # Test 2 - Availability
    # -----------------------------------------

    result_2 = run_test(
        2,
        "candidate_006",
        "JOB_BACKEND_001",
        "BACKEND_AVAIL_001",
        "When can you join?",
        "availability",
        "I can join immediately.",
        "I can join immediately."
    )

    # -----------------------------------------
    # Test 3 - Salary
    # -----------------------------------------

    result_3 = run_test(
        3,
        "candidate_006",
        "JOB_BACKEND_001",
        "BACKEND_SALARY_001",
        "What are your salary expectations?",
        "salary",
        "I am expecting around 6 lakhs per year.",
        "I am expecting around 6 lakhs per year."
    )

    # -----------------------------------------
    # Test 4 - Off-topic
    # -----------------------------------------

    result_4 = run_test(
        4,
        "candidate_006",
        "JOB_BACKEND_001",
        "BACKEND_SKILLS_001",
        "What technical skills do you have?",
        "skills",
        "I really enjoy watching movies.",
        "I really enjoy watching movies."
    )

    # -----------------------------------------
    # Test 5 - No response
    # -----------------------------------------

    result_5 = run_test(
        5,
        "candidate_006",
        "JOB_BACKEND_001",
        "BACKEND_LOC_001",
        "Where are you currently located?",
        "location",
        "",
        ""
    )

    # -----------------------------------------
    # Validation
    # -----------------------------------------

    passed = 0
    failed = 0

    # Test 1
    if (
        result_1["intent"] == "experience"
        and result_1["answer_status"] == "valid"
        and result_1["semantic_object"][
            "experience"
        ]["years"] == 3
        and "Python"
        in result_1["semantic_object"]["skills"]
        and "Django"
        in result_1["semantic_object"]["skills"]
    ):
        passed += 1
    else:
        failed += 1

    # Test 2
    if (
        result_2["intent"] == "availability"
        and result_2["answer_status"] == "valid"
        and result_2["semantic_object"][
            "availability"
        ]["status"] == "immediate"
    ):
        passed += 1
    else:
        failed += 1

    # Test 3
    if (
        result_3["intent"] == "salary"
        and result_3["answer_status"] == "valid"
        and result_3["semantic_object"][
            "salary_expectation"
        ]["amount"] == 600000
    ):
        passed += 1
    else:
        failed += 1

    # Test 4
    if (
        result_4["answer_status"] == "off_topic"
        and result_4["off_topic"] is True
    ):
        passed += 1
    else:
        failed += 1

    # Test 5
    if (
        result_5["answer_status"] == "no_response"
        and result_5["intent"] == "no_response"
    ):
        passed += 1
    else:
        failed += 1

    print("\n" + "=" * 70)
    print("SEMANTIC ANSWER BUILDER TEST COMPLETED")
    print("=" * 70)

    print(f"Total : {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    print("=" * 70)


if __name__ == "__main__":
    main()