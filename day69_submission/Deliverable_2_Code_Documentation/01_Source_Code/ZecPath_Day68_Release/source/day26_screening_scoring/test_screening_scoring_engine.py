from screening_scoring_engine import ScreeningScoringEngine


def validate_result(result):
    """
    Validate the basic structure of a scoring result.
    """

    required_score_keys = {
        "clarity",
        "relevance",
        "completeness",
        "consistency"
    }

    scores = result.get("scores", {})

    if set(scores.keys()) != required_score_keys:
        return False

    if not 0 <= result["normalized_score"] <= 100:
        return False

    if not 0 <= result["weighted_score"] <= 10:
        return False

    if "strengths" not in result["explanation"]:
        return False

    if "weaknesses" not in result["explanation"]:
        return False

    return True


def run_test(
    engine,
    name,
    expected_min_score,
    **kwargs
):
    """
    Run one scoring test.
    """

    result = engine.score_response(**kwargs)

    score = result["normalized_score"]

    passed = (
        score >= expected_min_score
        and validate_result(result)
    )

    status = "PASS" if passed else "FAIL"

    print(
        f"{name:<28} "
        f"Score: {score:<6} "
        f"{status}"
    )

    return passed


if __name__ == "__main__":

    print("=" * 70)
    print("SCREENING SCORING ENGINE TEST")
    print("=" * 70)

    engine = ScreeningScoringEngine()

    passed = 0
    failed = 0

    # --------------------------------------------------
    # Test 1: Strong Experience Answer
    # --------------------------------------------------

    if run_test(
        engine,
        "1. Strong Experience Answer",

        expected_min_score=80,

        candidate_id="candidate_006",
        job_id="JOB_BACKEND_001",
        question_id="BACKEND_EXP_001",

        question=(
            "How many years of backend development "
            "experience do you have?"
        ),

        question_category="experience",

        normalized_answer=(
            "I have three years of backend development "
            "experience. I have worked with Python and Django."
        ),

        intent="experience",

        answer_status="valid",

        off_topic=False,

        semantic_object={
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
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 2: Technical Skills Answer
    # --------------------------------------------------

    if run_test(
        engine,
        "2. Technical Skills Answer",

        expected_min_score=80,

        candidate_id="candidate_006",
        job_id="JOB_BACKEND_001",
        question_id="BACKEND_SKILLS_001",

        question=(
            "Which technical skills do you have?"
        ),

        question_category="skills",

        normalized_answer=(
            "I have experience with Python, Django, "
            "Docker and AWS."
        ),

        intent="skills",

        answer_status="valid",

        off_topic=False,

        semantic_object={
            "skills": [
                "Python",
                "Django",
                "Docker",
                "AWS"
            ]
        }
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 3: Off-topic Answer
    # --------------------------------------------------

    if run_test(
        engine,
        "3. Off-topic Answer",

        expected_min_score=30,

        candidate_id="candidate_006",
        job_id="JOB_BACKEND_001",
        question_id="BACKEND_EXP_001",

        question=(
            "How many years of backend development "
            "experience do you have?"
        ),

        question_category="experience",

        normalized_answer=(
            "I like watching movies and cricket."
        ),

        intent="off_topic",

        answer_status="valid",

        off_topic=True,

        semantic_object={}
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 4: No Response
    # --------------------------------------------------

    if run_test(
        engine,
        "4. No Response",

        expected_min_score=0,

        candidate_id="candidate_006",
        job_id="JOB_BACKEND_001",
        question_id="BACKEND_EXP_001",

        question=(
            "How many years of backend development "
            "experience do you have?"
        ),

        question_category="experience",

        normalized_answer="",

        intent="no_response",

        answer_status="no_response",

        off_topic=False,

        semantic_object={}
    ):
        passed += 1
    else:
        failed += 1

    # --------------------------------------------------
    # Test 5: Vague Answer
    # --------------------------------------------------

    if run_test(
        engine,
        "5. Vague Answer",

        expected_min_score=30,

        candidate_id="candidate_006",
        job_id="JOB_BACKEND_001",
        question_id="BACKEND_EXP_001",

        question=(
            "How many years of backend development "
            "experience do you have?"
        ),

        question_category="experience",

        normalized_answer="I don't know.",

        intent="vague",

        answer_status="vague",

        off_topic=False,

        semantic_object={}
    ):
        passed += 1
    else:
        failed += 1

    print("=" * 70)
    print(f"Total : {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 70)