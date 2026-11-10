
import json
from pathlib import Path
from datetime import datetime

from technical_scoring_engine import (
    get_question_weights,
    validate_weights,
    normalize_score,
    calculate_weighted_score,
    normalize_for_difficulty,
    get_score_category,
    detect_answer_depth,
)

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "input" / "candidate_technical_answers.json"
OUTPUT_DIR = BASE_DIR / "results"
OUTPUT_FILE = OUTPUT_DIR / "candidate_technical_evaluation.json"


def evaluate_candidate():
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    candidate_id = data.get("candidate_id")
    job_id = data.get("job_id")
    questions = data.get("questions", [])

    if not candidate_id or not job_id or not questions:
        raise ValueError(
            "Candidate ID, job ID, and questions are required."
        )

    evaluated_questions = []

    for question in questions:
        answer = question.get("candidate_answer", "").strip()
        scores = question.get("reviewer_scores", {})

        if not answer or answer.lower().startswith("enter the candidate"):
            raise ValueError(
                f"Enter the actual answer for {question.get('question_id')}."
            )

        required = [
            "accuracy",
            "depth",
            "logical_reasoning",
            "real_world_applicability",
        ]

        if any(scores.get(key) is None for key in required):
            raise ValueError(
                f"Reviewer scores are incomplete for "
                f"{question.get('question_id')}."
            )

        parameter_scores = {}
        for key in required:
            value = scores[key]
            if not isinstance(value, (int, float)) or not 0 <= value <= 100:
                raise ValueError(
                    f"{key} must be a number between 0 and 100."
                )
            parameter_scores[key] = normalize_score(value)

        question_type = question.get("question_type", "conceptual")
        difficulty = question.get("difficulty", "basic")

        weights = get_question_weights(question_type)

        if not validate_weights(weights):
            raise ValueError(f"Invalid weights for {question_type}.")

        weighted = calculate_weighted_score(parameter_scores, weights)
        final_score = normalize_for_difficulty(
            weighted["technical_score"], difficulty
        )

        evaluated_questions.append({
            "question_id": question["question_id"],
            "skill_domain": question["skill_domain"],
            "question_text": question["question_text"],
            "candidate_answer": answer,
            "answer_analysis": detect_answer_depth(answer),
            "parameter_scores": parameter_scores,
            "scoring_weights": weights,
            "technical_score": final_score,
            "score_category": get_score_category(final_score),
        })

    overall_score = round(
        sum(item["technical_score"] for item in evaluated_questions)
        / len(evaluated_questions),
        2,
    )

    result = {
        "engine": "ZecPath Candidate Technical Evaluator",
        "data_type": "REVIEWER_SCORED_TEST_INPUT",
        "candidate_id": candidate_id,
        "job_id": job_id,
        "generated_at": datetime.now().astimezone().isoformat(),
        "evaluation_summary": {
            "total_questions": len(evaluated_questions),
            "overall_technical_score": overall_score,
            "score_category": get_score_category(overall_score),
        },
        "question_results": evaluated_questions,
        "score_source": (
            "Reviewer-provided parameter scores; "
            "not an automatic factual assessment of answer correctness."
        ),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print("Technical evaluation completed.")
    print("Candidate:", candidate_id)
    print("Technical score:", overall_score)
    print("Output saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    try:
        evaluate_candidate()
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        print("Evaluation could not be completed:", error)
