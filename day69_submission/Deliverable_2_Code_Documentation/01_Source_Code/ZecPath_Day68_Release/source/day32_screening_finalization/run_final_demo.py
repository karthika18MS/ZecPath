import json
import sys
from pathlib import Path


# ==========================================================
# PROJECT ROOT
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from day32_screening_finalization.final_screening_pipeline import (
    FinalScreeningPipeline
)


# ==========================================================
# LIVE DEMO
# ==========================================================

def run_live_demo():

    print()
    print("=" * 75)
    print("ZecPath AI Screening System — LIVE DEMO")
    print("=" * 75)

    candidate_id = "candidate_006"
    job_id = "JOB_BACKEND_001"

    print(f"Candidate : {candidate_id}")
    print(f"Job       : {job_id}")

    print()
    print("Initializing complete AI screening pipeline...")

    pipeline = FinalScreeningPipeline()


    # ======================================================
    # SCREENING QUESTIONS
    # ======================================================

    questions = [

        {
            "question_id":
                "BACKEND_EXP_001",

            "question":
                "How many years of backend development experience do you have?",

            "question_category":
                "experience",

            "answer":
                (
                    "I have three years of backend development "
                    "experience. I have worked with Python and Django."
                ),

            "duration_seconds": 8,

            "audio_quality": 1.0,

            "background_noise": 0.0
        },


        {
            "question_id":
                "BACKEND_SKILLS_001",

            "question":
                "What technical skills do you have?",

            "question_category":
                "skills",

            "answer":
                (
                    "I have experience with Python, Django, "
                    "Docker and PostgreSQL."
                ),

            "duration_seconds": 9,

            "audio_quality": 1.0,

            "background_noise": 0.0
        },


        {
            "question_id":
                "BACKEND_AVAILABILITY_001",

            "question":
                "When would you be available to join?",

            "question_category":
                "availability",

            "answer":
                "I can join immediately.",

            "duration_seconds": 5,

            "audio_quality": 1.0,

            "background_noise": 0.0
        },


        {
            "question_id":
                "BACKEND_SALARY_001",

            "question":
                "What is your expected salary?",

            "question_category":
                "salary",

            "answer":
                "I expect 6 lakhs per year.",

            "duration_seconds": 5,

            "audio_quality": 1.0,

            "background_noise": 0.0
        }
    ]


    # ======================================================
    # DISPLAY SCREENING SESSION
    # ======================================================

    print()
    print("-" * 75)
    print("SCREENING SESSION STARTED")
    print("-" * 75)


    for index, question in enumerate(
        questions,
        start=1
    ):

        print()
        print(
            f"Question {index}/{len(questions)}"
        )

        print(
            f"Question ID : "
            f"{question['question_id']}"
        )

        print(
            f"Question    : "
            f"{question['question']}"
        )

        print(
            f"Candidate   : "
            f"{question['answer']}"
        )


    # ======================================================
    # RUN COMPLETE DAY 32 PIPELINE
    # ======================================================

    result = pipeline.process_screening_session(

        candidate_id=candidate_id,

        job_id=job_id,

        questions=questions
    )


    # ======================================================
    # READ ACTUAL DAY 32 RESULT STRUCTURE
    # ======================================================

    summary = result.get(
        "screening_summary",
        {}
    )

    responses = result.get(
        "responses",
        []
    )


    total_questions = summary.get(
        "total_questions",
        0
    )

    successfully_processed = summary.get(
        "successfully_processed",
        0
    )

    edge_cases_handled = summary.get(
        "edge_cases_handled",
        0
    )

    final_screening_score = summary.get(
        "final_screening_score",
        0
    )

    average_communication = summary.get(
        "average_communication",
        {}
    )


    # ======================================================
    # LIVE DEMO RESULT
    # ======================================================

    print()
    print("=" * 75)
    print("LIVE DEMO RESULT")
    print("=" * 75)

    print(
        f"Candidate             : "
        f"{result.get('candidate_id')}"
    )

    print(
        f"Job                   : "
        f"{result.get('job_id')}"
    )

    print(
        f"Total Questions       : "
        f"{total_questions}"
    )

    print(
        f"Successfully Processed: "
        f"{successfully_processed}"
    )

    print(
        f"Edge Cases Handled    : "
        f"{edge_cases_handled}"
    )

    print(
        f"Final Screening Score : "
        f"{final_screening_score}/100"
    )


    # ======================================================
    # COMMUNICATION
    # ======================================================

    print()
    print("Average Communication")
    print("-" * 75)

    print(
        f"Confidence            : "
        f"{average_communication.get('confidence', 0)}"
    )

    print(
        f"Clarity               : "
        f"{average_communication.get('clarity', 0)}"
    )

    print(
        f"Engagement            : "
        f"{average_communication.get('engagement', 0)}"
    )

    print(
        f"Consistency           : "
        f"{average_communication.get('consistency', 0)}"
    )

    print(
        f"Communication Strength: "
        f"{average_communication.get('communication_strength', 0)}"
    )


    # ======================================================
    # QUESTION RESULTS
    # ======================================================

    print()
    print("Question Results")
    print("-" * 75)


    for response in responses:

        question_data = response.get(
            "question",
            {}
        )

        question_id = question_data.get(
            "question_id",
            "unknown"
        )


        scoring = response.get(
            "screening_scoring",
            {}
        )

        score = scoring.get(
            "normalized_score",
            0
        )


        conversation = response.get(
            "conversation_flow",
            {}
        )

        action = conversation.get(
            "action",
            "unknown"
        )


        print(
            f"{question_id}: "
            f"score={score}, "
            f"action={action}"
        )


    # ======================================================
    # EXTRACTED CANDIDATE INFORMATION
    # ======================================================

    print()
    print("Extracted Candidate Information")
    print("-" * 75)


    for response in responses:

        answer_understanding = response.get(
            "answer_understanding",
            {}
        )


        semantic = answer_understanding.get(
            "semantic_object",
            {}
        )


        # --------------------------------------------------
        # Skills
        # --------------------------------------------------

        skills = semantic.get(
            "skills"
        )

        if skills:

            print(
                f"Skills       : "
                f"{', '.join(skills)}"
            )


        # --------------------------------------------------
        # Experience
        # --------------------------------------------------

        experience = semantic.get(
            "experience"
        )

        if experience:

            years = experience.get(
                "years"
            )

            domain = experience.get(
                "domain"
            )


            if years is not None:

                print(
                    f"Experience   : "
                    f"{years} years"
                )


            if domain:

                print(
                    f"Domain       : "
                    f"{domain}"
                )


        # --------------------------------------------------
        # Availability
        # --------------------------------------------------

        availability = semantic.get(
            "availability"
        )

        if availability:

            print(
                f"Availability : "
                f"{availability}"
            )


        # --------------------------------------------------
        # Salary
        # --------------------------------------------------

        salary = semantic.get(
            "salary_expectation"
        )

        if salary:

            print(
                f"Salary       : "
                f"{salary}"
            )


    # ======================================================
    # SAVE LIVE DEMO OUTPUT
    # ======================================================

    results_dir = (
        Path(__file__).resolve().parent
        / "results"
    )

    results_dir.mkdir(
        parents=True,
        exist_ok=True
    )


    output_file = (
        results_dir
        / "live_demo_output.txt"
    )


    # ======================================================
    # WRITE TEXT REPORT
    # ======================================================

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "ZecPath AI Screening System — LIVE DEMO\n"
        )

        file.write(
            "=" * 75 + "\n"
        )

        file.write(
            f"Candidate: "
            f"{result.get('candidate_id')}\n"
        )

        file.write(
            f"Job: "
            f"{result.get('job_id')}\n"
        )

        file.write(
            f"Total Questions: "
            f"{total_questions}\n"
        )

        file.write(
            f"Successfully Processed: "
            f"{successfully_processed}\n"
        )

        file.write(
            f"Edge Cases Handled: "
            f"{edge_cases_handled}\n"
        )

        file.write(
            f"Final Screening Score: "
            f"{final_screening_score}/100\n"
        )


        file.write(
            "\nAverage Communication\n"
        )

        file.write(
            "-" * 75 + "\n"
        )


        for key, value in (
            average_communication.items()
        ):

            file.write(
                f"{key}: {value}\n"
            )


        file.write(
            "\nQuestion Results\n"
        )

        file.write(
            "-" * 75 + "\n"
        )


        for response in responses:

            question_data = response.get(
                "question",
                {}
            )

            question_id = question_data.get(
                "question_id",
                "unknown"
            )


            scoring = response.get(
                "screening_scoring",
                {}
            )

            score = scoring.get(
                "normalized_score",
                0
            )


            conversation = response.get(
                "conversation_flow",
                {}
            )

            action = conversation.get(
                "action",
                "unknown"
            )


            file.write(
                f"{question_id}: "
                f"score={score}, "
                f"action={action}\n"
            )


    # ======================================================
    # COMPLETION MESSAGE
    # ======================================================

    print()
    print("=" * 75)
    print("LIVE DEMO COMPLETED SUCCESSFULLY")
    print("=" * 75)

    print(
        f"Demo output saved to: "
        f"{output_file}"
    )

    print("=" * 75)


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    run_live_demo()