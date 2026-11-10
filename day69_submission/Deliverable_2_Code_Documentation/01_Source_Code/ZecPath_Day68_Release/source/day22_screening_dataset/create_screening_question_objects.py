import json
from pathlib import Path


BASE_DIR = Path(__file__).parent

QUESTIONS_FILE = BASE_DIR / "screening_questions.json"
OUTPUT_FILE = BASE_DIR / "screening_question_objects.json"


def load_questions():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def create_question_object(question):
    answer_type = question["expected_answer_type"]
    mandatory = question["mandatory"]
    importance = question["scoring_importance"]

    if answer_type in ["location", "yes_no"]:
        allow_follow_up = False
        max_follow_ups = 0
        follow_up_if_missing = False

    else:
        allow_follow_up = True
        max_follow_ups = 1
        follow_up_if_missing = mandatory

    return {
        "question_id": question["question_id"],
        "role": question["role"],
        "category": question["category"],

        "prompt": question["question"],

        "expected_answer": {
            "type": answer_type,
            "required": mandatory
        },

        "conversation": {
            "allow_follow_up": allow_follow_up,
            "max_follow_ups": max_follow_ups,
            "follow_up_if_missing": follow_up_if_missing
        },

        "evaluation": {
            "scoring_importance": importance
        }
    }


def generate_objects():
    data = load_questions()

    question_objects = []

    for question in data["questions"]:
        question_object = create_question_object(question)
        question_objects.append(question_object)

    output = {
        "dataset_name": "ZecPath AI Conversation-Ready Screening Questions",
        "dataset_version": "1.0",

        "language_config": data.get(
            "language_config",
            {
                "default_language": "en",
                "supported_languages": ["en"],
                "fallback_language": "en"
            }
        ),

        "conversation_config": {
            "allow_follow_up": True,
            "default_max_follow_ups": 1,
            "stop_after_mandatory_questions": True
        },

        "questions": question_objects
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("AI conversation-ready question objects generated successfully.")
    print(f"Total questions: {len(question_objects)}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_objects()