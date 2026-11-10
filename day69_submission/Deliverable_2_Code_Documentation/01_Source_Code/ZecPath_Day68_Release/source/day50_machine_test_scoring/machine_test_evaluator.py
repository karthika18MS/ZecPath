
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "input" / "machine_test_submission.json"
RESULTS_DIR = BASE_DIR / "results"
OUTPUT_FILE = RESULTS_DIR / "machine_test_score.json"


def load_input():
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_input(data):
    if not data.get("candidate_id"):
        raise ValueError("Candidate ID is required.")

    if not data.get("job_id"):
        raise ValueError("Job ID is required.")

    task = data.get("task")
    if not isinstance(task, dict):
        raise ValueError("Task details are required.")

    if not task.get("requirements"):
        raise ValueError("At least one task requirement is required.")

    if not task.get("candidate_code", "").strip():
        raise ValueError("Candidate code is required.")

    test_results = task.get("test_results", {})
    total = test_results.get("total_tests")
    passed = test_results.get("passed_tests")

    if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
        raise ValueError("total_tests must be a positive integer.")

    if not isinstance(passed, int) or isinstance(passed, bool):
        raise ValueError("passed_tests must be an integer.")

    if not 0 <= passed <= total:
        raise ValueError("passed_tests must be between 0 and total_tests.")

    review_scores = task.get("review_scores", {})
    required_scores = [
        "requirement_coverage",
        "code_quality",
        "readability",
    ]

    for key in required_scores:
        score = review_scores.get(key)
        if (
            not isinstance(score, (int, float))
            or isinstance(score, bool)
            or not 0 <= score <= 100
        ):
            raise ValueError(
                f"{key} must be a number between 0 and 100."
            )


def evaluate_submission(data):
    task = data["task"]
    test_results = task["test_results"]
    review = task["review_scores"]

    total_tests = test_results["total_tests"]
    passed_tests = test_results["passed_tests"]

    test_pass_rate = round(
        (passed_tests / total_tests) * 100, 2
    )

    # Configurable proposed weights; total = 100%.
    weights = {
        "test_pass_rate": 0.50,
        "requirement_coverage": 0.20,
        "code_quality": 0.20,
        "readability": 0.10,
    }

    components = {
        "test_pass_rate": test_pass_rate,
        "requirement_coverage": review["requirement_coverage"],
        "code_quality": review["code_quality"],
        "readability": review["readability"],
    }

    contributions = {
        key: round(components[key] * weights[key], 2)
        for key in weights
    }

    final_score = round(sum(contributions.values()), 2)

    return {
        "engine": "ZecPath Machine Test Evaluation Engine",
        "data_type": "TEST_INPUT",
        "generated_at": datetime.now().astimezone().isoformat(),
        "candidate_id": data["candidate_id"],
        "job_id": data["job_id"],
        "task_id": task.get("task_id"),
        "task_title": task.get("title"),
        "evaluation_status": "SUCCESS",
        "test_results": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "test_pass_rate": test_pass_rate,
        },
        "scoring_weights": weights,
        "component_scores": components,
        "weighted_contributions": contributions,
        "machine_test_score": final_score,
        "score_category": (
            "strong" if final_score >= 80
            else "moderate" if final_score >= 60
            else "needs_improvement"
        ),
        "requirements": task["requirements"],
        "scoring_note": (
            "Review scores are supplied inputs and must be supported "
            "by a human review. Test results must come from actually "
            "executing the candidate's submission against test cases. "
            "This output is test data, not a verified real-candidate result."
        ),
    }


def main():
    data = load_input()
    validate_input(data)
    result = evaluate_submission(data)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print("=" * 55)
    print("ZecPath Machine Test Evaluation Engine")
    print("=" * 55)
    print("Candidate:", result["candidate_id"])
    print("Job:", result["job_id"])
    print("Tests passed:", result["test_results"]["passed_tests"],
          "/", result["test_results"]["total_tests"])
    print("Machine Test Score:", result["machine_test_score"])
    print("Evaluation Status:", result["evaluation_status"])
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    try:
        main()
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as error:
        print("Evaluation failed:", error)
