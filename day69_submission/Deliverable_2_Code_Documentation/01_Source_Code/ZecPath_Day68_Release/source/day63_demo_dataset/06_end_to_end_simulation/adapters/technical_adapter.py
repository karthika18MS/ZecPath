
import json
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


# ============================================================
# ZecPath Day 63 - Technical Interview Adapter
# Integrated with Day 47 Technical Scoring Engine
# ============================================================

# DEMO   = Simulated reviewer scores for pipeline testing
# MANUAL = Actual reviewer scores required

SCORING_MODE = "DEMO"


# ============================================================
# 1. CONFIGURABLE PATHS
# ============================================================

SIMULATION_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = SIMULATION_ROOT.parents[1]

# Import shared simulation configuration.
import sys
sys.path.insert(0, str(SIMULATION_ROOT))

from config_loader import SimulationConfig

CONFIG = SimulationConfig()

DATASET_ROOT = CONFIG.dataset_root
INPUT_DIR = DATASET_ROOT / "04_candidate_responses" / "technical_responses"

OUTPUT_DIR = CONFIG.output_dir
OUTPUT_FILE = OUTPUT_DIR / "technical_results.json"

DAY47_ENGINE_PATH = (
    CONFIG.project_root
    / "day47_technical_skill_scoring"
    / "technical_scoring_engine.py"
)


# ============================================================
# 2. REVIEWER SCORE PARAMETERS
# ============================================================

REQUIRED_SCORE_FIELDS = {
    "accuracy",
    "depth",
    "logical_reasoning",
    "real_world_applicability"
}


# ============================================================
# 3. LOAD DAY 47 SCORING ENGINE
# ============================================================

def load_day47_engine():

    if not DAY47_ENGINE_PATH.exists():
        raise FileNotFoundError(
            f"Day 47 engine not found: {DAY47_ENGINE_PATH}"
        )

    spec = importlib.util.spec_from_file_location(
        "day47_technical_scoring_engine",
        DAY47_ENGINE_PATH
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            "Unable to load Day 47 technical scoring engine."
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


# ============================================================
# 4. LOAD JSON FILE
# ============================================================

def load_json(file_path: Path) -> Dict[str, Any]:

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "JSON file must contain an object."
        )

    return data


# ============================================================
# 5. NORMALIZE QUESTION TYPE
# ============================================================

def normalize_question_type(question_type: str) -> str:

    question_type = str(question_type).lower().strip()

    mapping = {
        "conceptual": "conceptual",
        "experience_based": "experience_based",
        "experience-based": "experience_based",
        "scenario": "scenario_based",
        "scenario_based": "scenario_based",
        "scenario-based": "scenario_based",
        "technical_follow_up": "technical_follow_up",
        "technical-follow-up": "technical_follow_up"
    }

    return mapping.get(question_type, "")


# ============================================================
# 6. IMPROVED SKILL DOMAIN DETECTION
# ============================================================

def infer_skill_domain(
    question: Dict[str, Any],
    job_id: str
) -> str:

    question_text = str(
        question.get("question", "")
    ).lower()

    answer = str(
        question.get("answer", "")
    ).lower()

    text = question_text + " " + answer

    # --------------------------------------------------------
    # Specific technologies first
    # --------------------------------------------------------

    if "django" in question_text:
        return "Django"

    if "spring boot" in question_text:
        return "Spring Boot"

    if "dependency injection" in question_text:
        return "Spring Boot"

    if "mongodb" in question_text or "mongo" in question_text:
        return "MongoDB"

    if "pandas" in question_text:
        return "Python"

    if (
        "python list" in question_text
        or "list and tuple" in question_text
        or "python" in question_text
    ):
        return "Python"

    if (
        "interface" in question_text
        and "abstract class" in question_text
    ):
        return "Java"

    if "object-oriented programming" in question_text:
        return "Java"

    if "exception in java" in question_text:
        return "Java"

    if "microservices" in question_text:
        if job_id == "JD003":
            return "Spring Boot"
        return "Node.js"

    # --------------------------------------------------------
    # MERN / backend technologies
    # --------------------------------------------------------

    if "middleware" in question_text:
        return "Express.js"

    if "express.js" in question_text or "express" in question_text:
        return "Express.js"

    if (
        "node.js" in question_text
        or "node js" in question_text
    ):
        return "Node.js"

    if (
        "react" in question_text
        or "virtual dom" in question_text
        or "react component" in question_text
        or "react state" in question_text
        or "react form" in question_text
        or "props" in question_text
    ):
        return "React"

    if "javascript" in question_text:
        return "JavaScript"

    if "get and post" in question_text:
        return "Express.js"

    if "rest api" in question_text:
        return "Node.js"

    # --------------------------------------------------------
    # Database-related questions
    # --------------------------------------------------------

    if (
        "select query" in text
        or "sql query" in question_text
        or "sql" in question_text
    ):
        return "SQL"

    # --------------------------------------------------------
    # Job-specific fallback
    # --------------------------------------------------------

    job_mapping = {
        "JD001": "JavaScript",
        "JD002": "Python",
        "JD003": "Java"
    }

    return job_mapping.get(
        job_id,
        "General Technical"
    )


# ============================================================
# 7. INFER DIFFICULTY FOR DEMO METADATA
# ============================================================

def infer_difficulty(
    question: Dict[str, Any]
) -> str:

    question_type = normalize_question_type(
        question.get("question_type", "")
    )

    if question_type == "conceptual":
        return "basic"

    if question_type == "experience_based":
        return "intermediate"

    if question_type == "scenario_based":
        return "intermediate"

    if question_type == "technical_follow_up":
        return "advanced"

    return "basic"


# ============================================================
# 8. GENERATE SIMULATED DEMO REVIEW SCORES
# ============================================================

def generate_demo_scores(
    answer: str
) -> Dict[str, float]:

    """
    Generate synthetic reviewer parameters for testing.

    This is a heuristic demonstration mechanism.
    It does not verify factual correctness.
    """

    answer = str(answer).strip()

    words = answer.split()
    word_count = len(words)

    answer_lower = answer.lower()

    explanation_keywords = [
        "because",
        "therefore",
        "reason",
        "process",
        "how",
        "why",
        "approach",
        "logic"
    ]

    practical_keywords = [
        "project",
        "application",
        "production",
        "implemented",
        "developed",
        "example",
        "used",
        "testing"
    ]

    technical_keywords = [
        "api",
        "database",
        "authentication",
        "security",
        "component",
        "state",
        "middleware",
        "query",
        "performance",
        "optimization",
        "react",
        "python",
        "java",
        "node",
        "django",
        "sql",
        "mongodb",
        "spring"
    ]

    explanation_count = sum(
        1 for word in explanation_keywords
        if word in answer_lower
    )

    practical_count = sum(
        1 for word in practical_keywords
        if word in answer_lower
    )

    technical_count = sum(
        1 for word in technical_keywords
        if word in answer_lower
    )

    accuracy = min(
        90,
        55
        + (min(word_count, 60) * 0.35)
        + (min(technical_count, 5) * 2)
    )

    depth = min(
        92,
        45
        + (min(word_count, 80) * 0.45)
        + (min(technical_count, 5) * 3)
    )

    logical_reasoning = min(
        90,
        55
        + (min(explanation_count, 5) * 5)
        + (min(word_count, 50) * 0.20)
    )

    real_world_applicability = min(
        92,
        50
        + (min(practical_count, 5) * 6)
        + (min(technical_count, 5) * 2)
    )

    return {
        "accuracy": round(accuracy, 2),
        "depth": round(depth, 2),
        "logical_reasoning": round(
            logical_reasoning, 2
        ),
        "real_world_applicability": round(
            real_world_applicability, 2
        )
    }


# ============================================================
# 9. VALIDATE REVIEWER SCORES
# ============================================================

def validate_reviewer_scores(scores: Any) -> bool:

    if not isinstance(scores, dict):
        return False

    if set(scores.keys()) != REQUIRED_SCORE_FIELDS:
        return False

    try:
        for value in scores.values():

            numeric_value = float(value)

            if not 0 <= numeric_value <= 100:
                return False

    except (TypeError, ValueError):
        return False

    return True


# ============================================================
# 10. PREPARE QUESTION FOR DAY 47 ENGINE
# ============================================================

def prepare_question(
    question: Dict[str, Any],
    job_id: str
) -> Dict[str, Any]:

    question_type = normalize_question_type(
        question.get("question_type", "")
    )

    if not question.get("question_id"):
        raise ValueError("Missing question_id.")

    if not question.get("question"):
        raise ValueError("Missing question text.")

    answer = str(
        question.get("answer", "")
    ).strip()

    if not answer:
        raise ValueError("Candidate answer is empty.")

    if not question_type:
        raise ValueError("Unsupported question type.")

    skill_domain = question.get("skill_domain")
    difficulty = question.get("difficulty")

    # --------------------------------------------------------
    # DEMO MODE
    # --------------------------------------------------------

    if SCORING_MODE == "DEMO":

        if not skill_domain:
            skill_domain = infer_skill_domain(
                question,
                job_id
            )

        if difficulty not in {
            "basic",
            "intermediate",
            "advanced"
        }:
            difficulty = infer_difficulty(question)

        parameter_scores = generate_demo_scores(answer)

    # --------------------------------------------------------
    # MANUAL MODE
    # --------------------------------------------------------

    else:

        parameter_scores = question.get(
            "reviewer_scores"
        )

        if not validate_reviewer_scores(parameter_scores):

            return {
                "ready": False,
                "reason": "Waiting for human reviewer scores."
            }

        if not skill_domain or difficulty not in {
            "basic",
            "intermediate",
            "advanced"
        }:

            return {
                "ready": False,
                "reason": (
                    "Waiting for skill domain and "
                    "difficulty metadata."
                )
            }

    if not validate_reviewer_scores(parameter_scores):
        raise ValueError("Invalid parameter scores.")

    return {
        "ready": True,
        "question": {
            "question_id": question["question_id"],
            "skill_domain": skill_domain,
            "question_type": question_type,
            "difficulty": difficulty,
            "question_text": question["question"],
            "candidate_answer": answer,
            "parameter_scores": parameter_scores
        }
    }


# ============================================================
# 11. EVALUATE ONE CANDIDATE
# ============================================================

def evaluate_candidate(
    data: Dict[str, Any],
    file_name: str,
    engine
) -> Dict[str, Any]:

    candidate_id = data.get("candidate_id")
    job_id = data.get("job_id")

    response_status = str(
        data.get("response_status", "")
    ).lower()

    questions = data.get("questions", [])

    if not candidate_id or not job_id:
        raise ValueError(
            "Missing candidate_id or job_id."
        )

    if not isinstance(questions, list):
        raise ValueError(
            "Questions must be a list."
        )

    if response_status != "completed" or not questions:

        return {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "assessment_status": "NOT_PROVIDED",
            "technical_score": None,
            "score_status": "NOT_SCORED",
            "total_questions": 0,
            "question_wise_scores": []
        }

    prepared_questions = []
    pending_questions = []

    for index, question in enumerate(
        questions,
        start=1
    ):

        if not isinstance(question, dict):
            raise ValueError(
                f"Question {index} is not a JSON object."
            )

        prepared = prepare_question(
            question,
            job_id
        )

        if not prepared["ready"]:

            pending_questions.append({
                "question_id": question.get("question_id"),
                "reason": prepared["reason"]
            })

        else:

            prepared_questions.append(
                prepared["question"]
            )

    if pending_questions:

        return {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "assessment_status": "PENDING_REVIEW",
            "technical_score": None,
            "score_status": "NOT_SCORED",
            "total_questions": len(questions),
            "questions_pending_review": pending_questions,
            "question_wise_scores": []
        }

    # Use original Day 47 engine.

    question_results = engine.evaluate_all_questions(
        candidate_id,
        job_id,
        prepared_questions
    )

    final_result = engine.build_final_result(
        candidate_id,
        job_id,
        question_results
    )

    evaluation_summary = final_result[
        "evaluation_summary"
    ]

    technical_score = evaluation_summary[
        "overall_technical_score"
    ]

    return {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "assessment_status": "COMPLETED",
        "score_status": "SCORED",
        "technical_score": technical_score,
        "score_category": evaluation_summary[
            "overall_score_category"
        ],
        "total_questions": len(prepared_questions),
        "scoring_engine": (
            "ZecPath Day 47 Technical Scoring Engine"
        ),
        "scoring_mode": SCORING_MODE,
        "is_simulated": SCORING_MODE == "DEMO",
        "score_source": (
            "SIMULATED_HEURISTIC_DEMO"
            if SCORING_MODE == "DEMO"
            else "HUMAN_REVIEWER"
        ),
        "evaluation_summary": evaluation_summary,
        "question_wise_scores": question_results
    }


# ============================================================
# 12. RUN TECHNICAL ADAPTER
# ============================================================

def run_adapter():

    print("=" * 65)
    print("ZecPath Day 63 - Technical Interview Adapter")
    print("=" * 65)

    print("Scoring mode:", SCORING_MODE)
    print("Dataset:", CONFIG.dataset_name)
    print("Dataset root:", DATASET_ROOT)
    print("Input directory:", INPUT_DIR)
    print("Output directory:", OUTPUT_DIR)

    if SCORING_MODE not in {"DEMO", "MANUAL"}:
        raise ValueError(
            "SCORING_MODE must be DEMO or MANUAL."
        )

    engine = load_day47_engine()

    if not INPUT_DIR.exists():
        raise FileNotFoundError(
            f"Input directory not found: {INPUT_DIR}"
        )

    input_files = sorted(
        INPUT_DIR.glob("candidate_*_technical.json")
    )

    if not input_files:
        raise FileNotFoundError(
            "No candidate technical response files found."
        )

    candidate_results = []
    file_errors = []

    for file_path in input_files:

        print("\nProcessing:", file_path.name)

        try:

            data = load_json(file_path)

            result = evaluate_candidate(
                data,
                file_path.name,
                engine
            )

            result["source_file"] = file_path.name

            candidate_results.append(result)

            print("Candidate:", result["candidate_id"])
            print("Status:", result["assessment_status"])
            print(
                "Technical Score:",
                result.get("technical_score")
            )

        except Exception as error:

            file_errors.append({
                "file": file_path.name,
                "error": str(error)
            })

            print("Error:", error)

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    total = len(candidate_results)

    completed = sum(
        item["assessment_status"] == "COMPLETED"
        for item in candidate_results
    )

    pending = sum(
        item["assessment_status"] == "PENDING_REVIEW"
        for item in candidate_results
    )

    not_provided = sum(
        item["assessment_status"] == "NOT_PROVIDED"
        for item in candidate_results
    )

    invalid = sum(
        item["assessment_status"] == "INVALID_DATA"
        for item in candidate_results
    )

    scores = [
        item["technical_score"]
        for item in candidate_results
        if item.get("technical_score") is not None
    ]

    average_score = (
        round(sum(scores) / len(scores), 2)
        if scores else None
    )

    # --------------------------------------------------------
    # OUTPUT JSON
    # --------------------------------------------------------

    output = {

        "engine": "ZecPath Configurable Technical Adapter",

        "dataset": CONFIG.dataset_name,
        "dataset_type": CONFIG.dataset_type,
        "dataset_root": str(DATASET_ROOT),

        "scoring_engine": (
            "ZecPath Day 47 Technical Scoring Engine"
        ),

        "pipeline_status": (
            "SUCCESS"
            if not file_errors
            else "PARTIAL_SUCCESS"
        ),

        "scoring_mode": SCORING_MODE,

        "is_simulated": SCORING_MODE == "DEMO",

        "score_source": (
            "SIMULATED_HEURISTIC_DEMO"
            if SCORING_MODE == "DEMO"
            else "HUMAN_REVIEWER"
        ),

        "generated_at": datetime.now().astimezone().isoformat(),

        "scoring_policy": {

            "original_day47_weights_used": True,

            "simulated_scores_used": (
                SCORING_MODE == "DEMO"
            ),

            "human_review_required": (
                SCORING_MODE == "MANUAL"
            ),

            "demo_score_warning": (
                "Demo parameter scores are generated "
                "using answer-length and keyword heuristics. "
                "They do not verify factual correctness "
                "and must not be used as genuine hiring decisions."
            )
        },

        "summary": {

            "total_candidates": total,

            "completed": completed,

            "pending_review": pending,

            "not_provided": not_provided,

            "invalid_data": invalid,

            "average_technical_score": average_score,

            "file_errors": len(file_errors)
        },

        "candidate_results": candidate_results,

        "file_errors": file_errors
    }

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # PRINT SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("TECHNICAL ADAPTER SUMMARY")
    print("=" * 65)

    print("Total candidates :", total)
    print("Completed        :", completed)
    print("Pending review   :", pending)
    print("Not provided     :", not_provided)
    print("Invalid data     :", invalid)
    print("Average score    :", average_score)
    print("File errors      :", len(file_errors))

    print("\nOutput saved to:")
    print(OUTPUT_FILE)

    print("=" * 65)

    return output


# ============================================================
# 13. MAIN
# ============================================================

if __name__ == "__main__":

    try:
        run_adapter()

    except Exception as error:

        print("\nTechnical adapter failed:", error)
        raise
