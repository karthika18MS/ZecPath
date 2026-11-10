import json
import re
from pathlib import Path
from datetime import datetime


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

PROFILE_FILE = BASE_DIR / "candidate_profiles.json"

RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = RESULTS_DIR / "hr_interview_test_report.json"


# ============================================================
# SCORE LIMITS
# ============================================================

MIN_SCORE = 0
MAX_SCORE = 100


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def clamp_score(score):
    """
    Keep a score between 0 and 100.
    """

    return round(
        max(MIN_SCORE, min(MAX_SCORE, score)),
        2
    )


def word_count(text):
    """
    Return the number of words in a response.
    """

    return len(text.split())


def contains_any(text, keywords):
    """
    Check whether any keyword is present.
    """

    text = text.lower()

    return any(
        keyword.lower() in text
        for keyword in keywords
    )


def count_matches(text, keywords):
    """
    Count how many keywords are present.
    """

    text = text.lower()

    return sum(
        1
        for keyword in keywords
        if keyword.lower() in text
    )


# ============================================================
# LOAD INPUT
# ============================================================

def load_profiles():

    with open(
        PROFILE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# ANSWER RELEVANCE
# ============================================================

def evaluate_relevance(question_category, response):

    response_lower = response.lower()

    category_keywords = {

        "self_introduction": [
            "developer",
            "software",
            "experience",
            "study",
            "career",
            "backend",
            "project"
        ],

        "strengths": [
            "strength",
            "communication",
            "teamwork",
            "problem solving",
            "adaptability",
            "learning",
            "dedication",
            "leadership"
        ],

        "problem_solving": [
            "problem",
            "issue",
            "solution",
            "team",
            "identified",
            "analyzed",
            "implemented",
            "resolved",
            "discussed"
        ],

        "career_goals": [
            "role",
            "career",
            "skills",
            "learn",
            "opportunity",
            "contribute",
            "experience",
            "development"
        ]
    }

    keywords = category_keywords.get(
        question_category,
        []
    )

    matches = count_matches(
        response_lower,
        keywords
    )

    if matches >= 4:
        score = 95

    elif matches == 3:
        score = 90

    elif matches == 2:
        score = 80

    elif matches == 1:
        score = 70

    else:
        score = 50

    return clamp_score(score)


# ============================================================
# COMMUNICATION EVALUATION
# ============================================================

def evaluate_communication(response):

    words = word_count(response)

    score = 65

    # Response length
    if words >= 20:
        score += 15

    elif words >= 12:
        score += 10

    elif words >= 7:
        score += 5

    # Sentence structure
    sentences = len(
        re.findall(
            r"[.!?]",
            response
        )
    )

    if sentences >= 2:
        score += 5

    # Communication indicators
    if contains_any(
        response,
        [
            "because",
            "therefore",
            "then",
            "first",
            "finally",
            "discussed",
            "explained"
        ]
    ):
        score += 5

    # Excessive hesitation
    hesitation_words = [
        "um",
        "uh",
        "maybe",
        "not sure",
        "i think"
    ]

    hesitation_count = sum(
        response.lower().count(word)
        for word in hesitation_words
    )

    score -= hesitation_count * 5

    return clamp_score(score)


# ============================================================
# CONFIDENCE EVALUATION
# ============================================================

def evaluate_confidence(response):

    hesitation_markers = [
        "um",
        "uh",
        "maybe",
        "not sure",
        "i think",
        "i am not completely sure",
        "was not sure"
    ]

    hesitation_count = sum(
        response.lower().count(marker)
        for marker in hesitation_markers
    )

    score = 90

    score -= hesitation_count * 12

    # Clear action statements
    if contains_any(
        response,
        [
            "i identified",
            "i analyzed",
            "i helped",
            "i discussed",
            "i implemented",
            "i coordinated"
        ]
    ):
        score += 5

    return clamp_score(score)


# ============================================================
# CONSISTENCY EVALUATION
# ============================================================

def evaluate_consistency(responses):

    contradiction_markers = [
        "never",
        "always",
        "no experience",
        "several years",
        "recently completed"
    ]

    detected = []

    combined_text = " ".join(
        responses
    ).lower()

    # Basic contradiction check.
    # The purpose is to flag obvious conflicting indicators.
    if (
        "recently completed" in combined_text
        and "several years of experience" in combined_text
    ):
        detected.append(
            "Potential experience inconsistency"
        )

    for marker in contradiction_markers:

        occurrences = combined_text.count(
            marker
        )

        if occurrences >= 2:

            # Do not automatically treat repeated
            # words as contradictions.
            continue

    if detected:
        score = 70

    else:
        score = 100

    return {
        "score": clamp_score(score),
        "inconsistencies": detected
    }


# ============================================================
# LOGICAL REASONING EVALUATION
# ============================================================

def evaluate_logical_reasoning(response):

    reasoning_indicators = [
        "identified",
        "analyzed",
        "discussed",
        "solution",
        "implemented",
        "tested",
        "resolved",
        "problem",
        "issue"
    ]

    matches = count_matches(
        response,
        reasoning_indicators
    )

    if matches >= 5:
        score = 95

    elif matches >= 4:
        score = 90

    elif matches >= 3:
        score = 85

    elif matches >= 2:
        score = 75

    elif matches >= 1:
        score = 65

    else:
        score = 50

    return clamp_score(score)


# ============================================================
# SCENARIO / PROBLEM-SOLVING EVALUATION
# ============================================================

def evaluate_scenario(response):

    scenario_indicators = [
        "problem",
        "issue",
        "identified",
        "discussed",
        "solution",
        "team",
        "implemented",
        "resolved",
        "tested",
        "deadline"
    ]

    matches = count_matches(
        response,
        scenario_indicators
    )

    if matches >= 6:
        score = 95

    elif matches >= 5:
        score = 90

    elif matches >= 4:
        score = 85

    elif matches >= 3:
        score = 80

    elif matches >= 2:
        score = 70

    else:
        score = 60

    return clamp_score(score)


# ============================================================
# QUESTION EVALUATION
# ============================================================

def evaluate_question(
    question,
    response
):

    relevance = evaluate_relevance(
        question["category"],
        response
    )

    communication = evaluate_communication(
        response
    )

    confidence = evaluate_confidence(
        response
    )

    logical_reasoning = 0
    scenario_score = 0

    if question["category"] == "problem_solving":

        logical_reasoning = evaluate_logical_reasoning(
            response
        )

        scenario_score = evaluate_scenario(
            response
        )

    return {
        "question_id": question["question_id"],
        "question": question["question"],
        "category": question["category"],
        "response": response,
        "response_status": (
            "valid"
            if response.strip()
            else "missing"
        ),
        "scores": {
            "relevance": relevance,
            "communication": communication,
            "confidence": confidence,
            "logical_reasoning": logical_reasoning,
            "scenario": scenario_score
        }
    }


# ============================================================
# HR INTERVIEW SCORE
# ============================================================

def calculate_hr_score(
    question_results
):

    relevance_scores = []
    communication_scores = []
    confidence_scores = []
    consistency_scores = []

    for result in question_results:

        relevance_scores.append(
            result["scores"]["relevance"]
        )

        communication_scores.append(
            result["scores"]["communication"]
        )

        confidence_scores.append(
            result["scores"]["confidence"]
        )

        # Consistency is evaluated at
        # session level, so added later.

    avg_relevance = (
        sum(relevance_scores)
        / len(relevance_scores)
    )

    avg_communication = (
        sum(communication_scores)
        / len(communication_scores)
    )

    avg_confidence = (
        sum(confidence_scores)
        / len(confidence_scores)
    )

    return {
        "relevance": clamp_score(
            avg_relevance
        ),
        "communication": clamp_score(
            avg_communication
        ),
        "confidence": clamp_score(
            avg_confidence
        )
    }


# ============================================================
# PERFORMANCE LEVEL
# ============================================================

def performance_level(score):

    if score >= 80:
        return "Strong"

    elif score >= 60:
        return "Moderate"

    return "Needs Improvement"


# ============================================================
# STRENGTHS
# ============================================================

def identify_strengths(
    relevance,
    communication,
    confidence,
    consistency,
    reasoning,
    scenario
):

    strengths = []

    if communication >= 80:
        strengths.append(
            "Strong communication skills"
        )

    if confidence >= 80:
        strengths.append(
            "Strong confidence indicators"
        )

    if relevance >= 80:
        strengths.append(
            "Relevant and focused responses"
        )

    if consistency >= 80:
        strengths.append(
            "Consistent responses"
        )

    if reasoning >= 80:
        strengths.append(
            "Good logical reasoning ability"
        )

    if scenario >= 80:
        strengths.append(
            "Good practical problem-solving ability"
        )

    return strengths


# ============================================================
# WEAKNESSES
# ============================================================

def identify_weaknesses(
    relevance,
    communication,
    confidence,
    consistency,
    reasoning,
    scenario
):

    weaknesses = []

    if relevance < 60:
        weaknesses.append(
            "Response relevance requires improvement"
        )

    if communication < 60:
        weaknesses.append(
            "Communication requires improvement"
        )

    if confidence < 60:
        weaknesses.append(
            "Confidence indicators require improvement"
        )

    if consistency < 60:
        weaknesses.append(
            "Response consistency requires improvement"
        )

    if reasoning < 60:
        weaknesses.append(
            "Logical reasoning requires improvement"
        )

    if scenario < 60:
        weaknesses.append(
            "Problem-solving clarity requires improvement"
        )

    return weaknesses


# ============================================================
# CULTURAL / WORKPLACE INDICATORS
# ============================================================

def identify_cultural_indicators(
    communication,
    consistency,
    scenario,
    responses
):

    indicators = []

    if communication >= 80:
        indicators.append(
            "Communicates ideas clearly"
        )

    if scenario >= 80:
        indicators.append(
            "Demonstrates practical problem-solving"
        )

    if consistency >= 80:
        indicators.append(
            "Demonstrates consistent responses"
        )

    combined = " ".join(
        responses
    ).lower()

    if "team" in combined:
        indicators.append(
            "Demonstrates teamwork orientation"
        )

    if any(
        word in combined
        for word in [
            "adaptability",
            "adapt",
            "learning",
            "learn"
        ]
    ):
        indicators.append(
            "Demonstrates adaptability"
        )

    return indicators


# ============================================================
# RISK FLAGS
# ============================================================

def identify_risk_flags(
    confidence,
    consistency,
    responses,
    question_results
):

    flags = []

    if confidence < 60:
        flags.append(
            "Low confidence indicators detected"
        )

    if consistency < 60:
        flags.append(
            "Potential response consistency issue detected"
        )

    missing_count = sum(
        1
        for result in question_results
        if result["response_status"] == "missing"
    )

    if missing_count > 0:
        flags.append(
            "Missing or incomplete responses detected"
        )

    if not responses:
        flags.append(
            "No interview responses available"
        )

    return flags


# ============================================================
# OVERALL SCORE
# ============================================================

def calculate_overall_score(
    hr_score,
    communication,
    confidence,
    reasoning,
    scenario
):

    score = (
        hr_score
        + communication
        + confidence
        + reasoning
        + scenario
    ) / 5

    return clamp_score(score)


# ============================================================
# SESSION EVALUATION
# ============================================================

def evaluate_candidate(
    candidate,
    questions
):

    responses = candidate["responses"]

    question_results = []

    for question, response in zip(
        questions,
        responses
    ):

        result = evaluate_question(
            question,
            response
        )

        question_results.append(
            result
        )

    # ----------------------------------------
    # HR score components
    # ----------------------------------------

    hr_components = calculate_hr_score(
        question_results
    )

    relevance = hr_components["relevance"]

    communication = hr_components[
        "communication"
    ]

    confidence = hr_components[
        "confidence"
    ]

    # ----------------------------------------
    # Consistency
    # ----------------------------------------

    consistency_result = evaluate_consistency(
        responses
    )

    consistency = consistency_result[
        "score"
    ]

    inconsistencies = consistency_result[
        "inconsistencies"
    ]

    # ----------------------------------------
    # Reasoning
    # ----------------------------------------

    reasoning_scores = [
        result["scores"]["logical_reasoning"]
        for result in question_results
        if result["scores"]["logical_reasoning"] > 0
    ]

    reasoning = (
        sum(reasoning_scores)
        / len(reasoning_scores)
        if reasoning_scores
        else 0
    )

    # ----------------------------------------
    # Scenario
    # ----------------------------------------

    scenario_scores = [
        result["scores"]["scenario"]
        for result in question_results
        if result["scores"]["scenario"] > 0
    ]

    scenario = (
        sum(scenario_scores)
        / len(scenario_scores)
        if scenario_scores
        else 0
    )

    # ----------------------------------------
    # HR Interview Score
    # ----------------------------------------

    hr_interview_score = (
        (
            relevance * 0.30
            + communication * 0.25
            + confidence * 0.20
            + consistency * 0.25
        )
    )

    hr_interview_score = clamp_score(
        hr_interview_score
    )

    # ----------------------------------------
    # Overall score
    # ----------------------------------------

    overall_score = calculate_overall_score(
        hr_interview_score,
        communication,
        confidence,
        reasoning,
        scenario
    )

    # ----------------------------------------
    # Summary
    # ----------------------------------------

    level = performance_level(
        overall_score
    )

    strengths = identify_strengths(
        relevance,
        communication,
        confidence,
        consistency,
        reasoning,
        scenario
    )

    weaknesses = identify_weaknesses(
        relevance,
        communication,
        confidence,
        consistency,
        reasoning,
        scenario
    )

    cultural_indicators = identify_cultural_indicators(
        communication,
        consistency,
        scenario,
        responses
    )

    risk_flags = identify_risk_flags(
        confidence,
        consistency,
        responses,
        question_results
    )

    if level == "Strong":

        summary = (
            "The candidate demonstrated strong "
            "overall HR interview performance."
        )

    elif level == "Moderate":

        summary = (
            "The candidate demonstrated moderate "
            "overall HR interview performance."
        )

    else:

        summary = (
            "The candidate requires improvement "
            "in several interview evaluation areas."
        )

    return {

        "candidate_id":
            candidate["candidate_id"],

        "candidate_type":
            candidate["candidate_type"],

        "interview_status":
            "completed",

        "question_count":
            len(questions),

        "question_results":
            question_results,

        "evaluation_scores": {

            "relevance":
                relevance,

            "communication":
                communication,

            "confidence":
                confidence,

            "consistency":
                consistency,

            "hr_interview_score":
                hr_interview_score,

            "logical_reasoning_score":
                clamp_score(reasoning),

            "scenario_score":
                clamp_score(scenario),

            "overall_score":
                overall_score
        },

        "performance_level":
            level,

        "summary":
            summary,

        "strengths":
            strengths,

        "weaknesses":
            weaknesses,

        "cultural_fit_indicators":
            cultural_indicators,

        "risk_flags":
            risk_flags,

        "inconsistencies":
            inconsistencies,

        "response_metrics": {

            "total_responses":
                len(responses),

            "answered_responses":
                sum(
                    1
                    for response in responses
                    if response.strip()
                ),

            "empty_responses":
                sum(
                    1
                    for response in responses
                    if not response.strip()
                ),

            "completion_rate":
                round(
                    (
                        sum(
                            1
                            for response in responses
                            if response.strip()
                        )
                        / len(responses)
                    ) * 100,
                    2
                )
                if responses
                else 0,

            "total_word_count":
                sum(
                    word_count(response)
                    for response in responses
                ),

            "average_words_per_response":
                round(
                    (
                        sum(
                            word_count(response)
                            for response in responses
                        )
                        / len(responses)
                    ),
                    2
                )
                if responses
                else 0
        }
    }


# ============================================================
# COMPLETE REPORT
# ============================================================

def generate_report(data):

    questions = data[
        "interview_questions"
    ]

    candidates = data[
        "candidate_profiles"
    ]

    sessions = []

    for candidate in candidates:

        result = evaluate_candidate(
            candidate,
            questions
        )

        sessions.append(
            result
        )

    return {

        "report_title":
            "Day 40 - Complete HR Interview Test Report",

        "test_objective":
            "Test the HR interview system "
            "end-to-end using multiple "
            "simulated candidate types.",

        "test_date":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "candidate_types_tested": [

            "confident",
            "hesitant",
            "inexperienced",
            "overqualified"
        ],

        "total_sessions":
            len(sessions),

        "evaluation_dimensions": [

            "relevance",
            "communication",
            "confidence",
            "consistency",
            "HR interview score",
            "logical reasoning",
            "scenario evaluation",
            "overall performance"
        ],

        "sessions":
            sessions
    }


# ============================================================
# SAVE REPORT
# ============================================================

def save_report(report):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    return OUTPUT_FILE


# ============================================================
# CONSOLE REPORT
# ============================================================

def print_report(report):

    print()
    print("=" * 75)
    print("DAY 40 - COMPLETE HR INTERVIEW TEST REPORT")
    print("=" * 75)

    print(
        f"Total Sessions : "
        f"{report['total_sessions']}"
    )

    print()

    for session in report["sessions"]:

        print("-" * 75)

        print(
            f"Candidate ID   : "
            f"{session['candidate_id']}"
        )

        print(
            f"Candidate Type : "
            f"{session['candidate_type']}"
        )

        print(
            f"Interview      : "
            f"{session['interview_status']}"
        )

        scores = session[
            "evaluation_scores"
        ]

        print(
            f"Relevance      : "
            f"{scores['relevance']}"
        )

        print(
            f"Communication  : "
            f"{scores['communication']}"
        )

        print(
            f"Confidence     : "
            f"{scores['confidence']}"
        )

        print(
            f"Consistency    : "
            f"{scores['consistency']}"
        )

        print(
            f"HR Score       : "
            f"{scores['hr_interview_score']}"
        )

        print(
            f"Logical Reason : "
            f"{scores['logical_reasoning_score']}"
        )

        print(
            f"Scenario Score : "
            f"{scores['scenario_score']}"
        )

        print(
            f"Overall Score  : "
            f"{scores['overall_score']}"
        )

        print(
            f"Performance    : "
            f"{session['performance_level']}"
        )

        print(
            f"Completion     : "
            f"{session['response_metrics']['completion_rate']}%"
        )

        print(
            "Strengths      : "
            + (
                ", ".join(
                    session["strengths"]
                )
                if session["strengths"]
                else "None identified"
            )
        )

        print(
            "Weaknesses     : "
            + (
                ", ".join(
                    session["weaknesses"]
                )
                if session["weaknesses"]
                else "None identified"
            )
        )

        print(
            "Risk Flags     : "
            + (
                ", ".join(
                    session["risk_flags"]
                )
                if session["risk_flags"]
                else "None"
            )
        )

        print(
            "Inconsistencies: "
            + (
                ", ".join(
                    session["inconsistencies"]
                )
                if session["inconsistencies"]
                else "None"
            )
        )

    print("-" * 75)

    print(
        "\nComplete HR interview test report "
        "generated successfully."
    )

    print(
        "\nSaved Result:"
    )

    print(OUTPUT_FILE)


# ============================================================
# MAIN
# ============================================================

def main():

    data = load_profiles()

    report = generate_report(
        data
    )

    save_report(
        report
    )

    print_report(
        report
    )


if __name__ == "__main__":
    main()
