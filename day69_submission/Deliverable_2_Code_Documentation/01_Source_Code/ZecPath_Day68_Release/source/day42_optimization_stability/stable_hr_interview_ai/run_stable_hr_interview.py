import json
from pathlib import Path

from .stable_hr_interview_engine import (
    StableHRInterviewEngine
)

from .hr_score_validator import (
    HRScoreValidator
)


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = (
    Path(__file__).resolve().parents[2]
)


# ============================================================
# DAY 42 MODULE DIRECTORY
# ============================================================

MODULE_DIR = (
    PROJECT_ROOT
    / "day42_optimization_stability"
    / "stable_hr_interview_ai"
)


# ============================================================
# CONFIG FILE
# ============================================================

CONFIG_FILE = (
    MODULE_DIR
    / "config.json"
)


# ============================================================
# DAY 37 REAL HR RESULT
# ============================================================

SOURCE_FILE = (
    PROJECT_ROOT
    / "day37_hr_interview_scoring"
    / "results"
    / "hr_interview_score.json"
)


# ============================================================
# DAY 42 RESULT
# ============================================================

RESULT_FILE = (
    MODULE_DIR
    / "results"
    / "stable_hr_interview_report.json"
)


# ============================================================
# LOAD JSON
# ============================================================

def load_json(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# SAVE JSON
# ============================================================

def save_json(
    file_path,
    data
):

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


# ============================================================
# EXTRACT DAY 37 INTERVIEW DATA
# ============================================================

def extract_interview_questions(
    hr_result
):
    """
    Read the real question-level data from Day 37.

    Day 37 provides:

        question_id
        question_text
        candidate_answer
        question_score

    Day 42 adds:

        response_status
        followup_count
    """

    questions = []

    question_scores = (
        hr_result.get(
            "question_scores",
            []
        )
    )

    for item in question_scores:

        question_id = item.get(
            "question_id"
        )

        question_text = item.get(
            "question_text",
            ""
        )

        candidate_answer = item.get(
            "candidate_answer",
            ""
        )

        question_score = item.get(
            "question_score"
        )

        questions.append({

            "question_id":
                question_id,

            "question_text":
                question_text,

            "candidate_answer":
                candidate_answer,

            "question_score":
                question_score,

            "response_status":
                "scored",

            "followup_count":
                0
        })

    return questions


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 75)

    print(
        "       ZecPath DAY 42 - "
        "STABLE HR INTERVIEW AI"
    )

    print("=" * 75)

    # --------------------------------------------------------
    # Load configuration
    # --------------------------------------------------------

    config = load_json(
        CONFIG_FILE
    )

    # --------------------------------------------------------
    # Display source
    # --------------------------------------------------------

    print()

    print(
        "Loading real Day 37 HR result..."
    )

    print(
        f"Source: {SOURCE_FILE}"
    )

    # --------------------------------------------------------
    # Check Day 37 file
    # --------------------------------------------------------

    if not SOURCE_FILE.exists():

        raise FileNotFoundError(
            "Day 37 HR result not found:\n"
            f"{SOURCE_FILE}"
        )

    # --------------------------------------------------------
    # Load Day 37 result
    # --------------------------------------------------------

    hr_result = load_json(
        SOURCE_FILE
    )

    print()

    print(
        f"Candidate : "
        f"{hr_result.get('candidate_id')}"
    )

    print(
        f"Job       : "
        f"{hr_result.get('job_id')}"
    )

    print(
        f"HR Score  : "
        f"{hr_result.get('final_hr_interview_score')}"
    )

    # ========================================================
    # HR SCORE VALIDATION
    # ========================================================

    score_validator = (
        HRScoreValidator(
            config
        )
    )

    score_validation = (
        score_validator.validate_result(
            hr_result
        )
    )

    print()

    print(
        "HR scoring validation:"
    )

    if score_validation["valid"]:

        print(
            "PASS - HR score structure is valid."
        )

    else:

        print(
            "FAIL - HR scoring issues found."
        )

        for error in (
            score_validation["errors"]
        ):

            print(
                f"  - {error}"
            )

    # ========================================================
    # EXTRACT QUESTIONS
    # ========================================================

    questions = (
        extract_interview_questions(
            hr_result
        )
    )

    # ========================================================
    # DEBUG CHECK
    # ========================================================

    print()

    print(
        "Day 37 question data check:"
    )

    print(
        "  Questions loaded:",
        len(questions)
    )

    question_text_count = sum(
        1
        for question in questions
        if question.get("question_text")
    )

    candidate_answer_count = sum(
        1
        for question in questions
        if question.get("candidate_answer")
    )

    print(
        "  Question text found:",
        question_text_count
    )

    print(
        "  Candidate answers found:",
        candidate_answer_count
    )

    # ========================================================
    # STABLE INTERVIEW ENGINE
    # ========================================================

    stability_rules = (
        config[
            "stability_rules"
        ]
    )

    stable_engine = (
        StableHRInterviewEngine(

            max_followups_per_question=
                stability_rules[
                    "max_followups_per_question"
                ],

            max_total_questions=
                stability_rules[
                    "max_total_questions"
                ],

            prevent_duplicate_questions=
                stability_rules[
                    "prevent_duplicate_questions"
                ]
        )
    )

    stability_report = (
        stable_engine.validate_interview(
            questions
        )
    )

    # ========================================================
    # INTERVIEW STABILITY RESULT
    # ========================================================

    print()

    print(
        "Interview stability validation:"
    )

    if stability_report["stable"]:

        print(
            "PASS - Interview flow is stable."
        )

    else:

        print(
            "FAIL - Interview flow issues found."
        )

        for error in (
            stability_report["errors"]
        ):

            print(
                f"  - {error}"
            )

    # ========================================================
    # QUESTION CONTENT VALIDATION
    # ========================================================

    question_validation = (
        stability_report[
            "question_validation"
        ]
    )

    print()

    print(
        "Question content validation:"
    )

    print(
        "  Total questions:",
        stability_report[
            "total_questions"
        ]
    )

    print(
        "  Question text available:",
        question_validation[
            "question_text_available"
        ]
    )

    print(
        "  Candidate answers available:",
        question_validation[
            "candidate_answer_available"
        ]
    )

    print(
        "  Response status available:",
        question_validation[
            "response_status_available"
        ]
    )

    print(
        "  Complete questions:",
        question_validation[
            "complete_questions"
        ]
    )

    # ========================================================
    # OVERALL STATUS
    # ========================================================

    overall_stable = (
        score_validation["valid"]
        and stability_report["stable"]
    )

    report = {

        "system":
            "ZecPath Day 42 Stable HR Interview AI",

        "candidate_id":
            hr_result.get(
                "candidate_id"
            ),

        "job_id":
            hr_result.get(
                "job_id"
            ),

        "source":
            str(SOURCE_FILE),

        "hr_score_validation":
            score_validation,

        "interview_stability":
            stability_report,

        "overall_status":
            (
                "STABLE"
                if overall_stable
                else "NEEDS_REVIEW"
            )
    }

    # ========================================================
    # SAVE REPORT
    # ========================================================

    save_json(
        RESULT_FILE,
        report
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()

    print("=" * 75)

    print(
        f"Overall status: "
        f"{report['overall_status']}"
    )

    print()

    print(
        "Questions       :",
        stability_report[
            "total_questions"
        ]
    )

    print(
        "Question text   :",
        question_validation[
            "question_text_available"
        ]
    )

    print(
        "Candidate answers:",
        question_validation[
            "candidate_answer_available"
        ]
    )

    print(
        "Duplicates      :",
        len(
            stability_report[
                "duplicate_questions"
            ]
        )
    )

    print(
        "Errors          :",
        len(
            stability_report[
                "errors"
            ]
        )
    )

    print(
        "Warnings        :",
        len(
            stability_report[
                "warnings"
            ]
        )
    )

    print()

    print(
        "Report saved to:"
    )

    print(
        RESULT_FILE
    )

    print("=" * 75)


if __name__ == "__main__":
    main()