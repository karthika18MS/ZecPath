
"""
Day63 Aptitude Adapter

Integrates Day38 LogicalReasoningScorer and ScenarioEvaluation.

IMPORTANT:
Parameter scores are simulated heuristic demo values.
They are not actual human evaluations or AI/LLM assessments.
"""

import json
import re
import sys
import time
from pathlib import Path
from statistics import mean


# ============================================================
# PATH CONFIGURATION
# ============================================================

CURRENT_DIR = Path(__file__).resolve().parent
SIMULATION_DIR = CURRENT_DIR.parent
PROJECT_ROOT = SIMULATION_DIR.parents[1]

# Load the shared simulation configuration.
if str(SIMULATION_DIR) not in sys.path:
    sys.path.insert(0, str(SIMULATION_DIR))

from config_loader import SimulationConfig

CONFIG = SimulationConfig()
DAY38_DIR = CONFIG.project_root / "day38_aptitude_logic"

if str(DAY38_DIR) not in sys.path:
    sys.path.insert(0, str(DAY38_DIR))


# ============================================================
# IMPORT DAY38 SCORERS
# ============================================================

try:
    from logical_reasoning_scorer import LogicalReasoningScorer
    from scenario_evaluation import ScenarioEvaluation

except ImportError as exc:
    raise ImportError(
        "Could not import Day38 scoring modules.\n"
        f"Check: {DAY38_DIR / 'logical_reasoning_scorer.py'}\n"
        f"Check: {DAY38_DIR / 'scenario_evaluation.py'}"
    ) from exc


# Input and output paths are resolved per adapter instance
# from SimulationConfig. This allows dataset changes through
# pipeline_config.json without editing Python source.


# ============================================================
# SCORING PARAMETERS
# ============================================================

LOGICAL_KEYS = {
    "problem_understanding",
    "reasoning",
    "decision_quality",
    "explanation_clarity",
    "conclusion",
}

SCENARIO_KEYS = {
    "situation_understanding",
    "problem_identification",
    "decision_making",
    "problem_solving",
    "communication_clarity",
    "outcome_awareness",
}

CATEGORY_WEIGHTS = {
    "logical_reasoning": 0.50,
    "scenario_evaluation": 0.50,
}

SCORE_ORIGIN = "SIMULATED_HEURISTIC_DEMO"


# ============================================================
# JSON HELPERS
# ============================================================

def load_json(path):

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# TEXT HELPERS
# ============================================================

def normalized_numbers(value):

    return re.findall(
        r"\d+(?:\.\d+)?",
        str(value)
    )


# ============================================================
# LOGICAL REASONING DEMO SCORING
# ============================================================

def logical_demo_scores(answer, expected_answer):

    """
    Generates heuristic demo parameter scores.

    Uses:
    - Expected answer comparison
    - Response completeness
    - Reasoning indicators
    - Explanation clarity

    These are demo values, not human assessments.
    """

    text = (answer or "").strip()
    lower = text.lower()

    words = re.findall(
        r"\b\w+\b",
        text
    )

    expected_numbers = normalized_numbers(
        expected_answer
    )

    answer_numbers = normalized_numbers(
        text
    )

    if expected_numbers:

        correct = (
            expected_numbers[0] in answer_numbers
        )

    else:

        expected_terms = re.findall(
            r"[a-zA-Z]+",
            str(expected_answer).lower()
        )

        correct = (
            bool(expected_terms)
            and all(term in lower for term in expected_terms)
        )

    has_reasoning = any(
        term in lower
        for term in (
            "because",
            "therefore",
            "since",
            "multiply",
            "divided",
            "difference",
            "each",
            "first",
            "then",
            "which means",
            "so ",
            "equals",
            "total"
        )
    )

    has_steps = any(
        term in lower
        for term in (
            "first",
            "then",
            "after",
            "step",
            "calculate",
            "identify"
        )
    )

    if not text:

        return {
            key: 0
            for key in LOGICAL_KEYS
        }

    correctness = 92 if correct else 35

    length_factor = min(
        len(words) / 18,
        1.0
    )

    reasoning = min(
        100,
        (55 if has_reasoning else 35)
        + 35 * length_factor
    )

    understanding = min(
        100,
        (correctness * 0.75)
        + (20 if len(words) >= 5 else 5)
    )

    decision = min(
        100,
        (correctness * 0.8)
        + (15 if has_steps or has_reasoning else 5)
    )

    clarity = min(
        100,
        45 + min(len(words), 25) * 2
    )

    conclusion = min(
        100,
        (correctness * 0.85)
        + (12 if answer_numbers else 5)
    )

    return {
        "problem_understanding": round(understanding, 2),
        "reasoning": round(reasoning, 2),
        "decision_quality": round(decision, 2),
        "explanation_clarity": round(clarity, 2),
        "conclusion": round(conclusion, 2),
    }


# ============================================================
# SCENARIO EVALUATION DEMO SCORING
# ============================================================

def scenario_demo_scores(answer):

    """
    Generates heuristic demo parameter scores for scenario answers.

    Looks for:
    - Situation understanding
    - Problem identification
    - Decision making
    - Problem solving
    - Communication
    - Outcome awareness
    """

    text = (answer or "").strip()
    lower = text.lower()

    words = re.findall(
        r"\b\w+\b",
        text
    )

    if not text:

        return {
            key: 0
            for key in SCENARIO_KEYS
        }

    def has_any(*terms):

        return any(
            term in lower
            for term in terms
        )

    length = min(
        len(words) / 45,
        1.0
    )

    investigation = has_any(
        "check",
        "identify",
        "inspect",
        "review",
        "logs",
        "error",
        "understand",
        "root cause",
        "monitor"
    )

    action = has_any(
        "fix",
        "solve",
        "optimize",
        "debug",
        "test",
        "rollback",
        "help",
        "create",
        "redistribute",
        "resolve",
        "restart"
    )

    communication = has_any(
        "communicate",
        "inform",
        "ask",
        "discuss",
        "team",
        "senior",
        "lead",
        "clarify",
        "coordinate"
    )

    outcome = has_any(
        "deadline",
        "users",
        "impact",
        "ensure",
        "monitor",
        "prevent",
        "result",
        "complete",
        "performance",
        "test"
    )

    base = 42 + 38 * length

    return {

        "situation_understanding": round(
            min(
                100,
                base + (10 if investigation else 0)
            ),
            2
        ),

        "problem_identification": round(
            min(
                100,
                base + (12 if investigation else 0)
            ),
            2
        ),

        "decision_making": round(
            min(
                100,
                base + (10 if action else 0)
            ),
            2
        ),

        "problem_solving": round(
            min(
                100,
                base + (15 if action else 0)
            ),
            2
        ),

        "communication_clarity": round(
            min(
                100,
                45 + 45 * length
                + (8 if communication else 0)
            ),
            2
        ),

        "outcome_awareness": round(
            min(
                100,
                base + (12 if outcome else 0)
            ),
            2
        ),
    }


# ============================================================
# EVALUATION CATEGORY
# ============================================================

def category(score):

    if score >= 80:
        return "strong"

    if score >= 60:
        return "moderate"

    return "needs_improvement"


# ============================================================
# APTITUDE ADAPTER CLASS
# ============================================================

class AptitudeAdapter:

    def __init__(self, dataset_root=None):

        self.config = SimulationConfig()

        # Optional override; otherwise use pipeline_config.json.
        self.dataset_root = (
            Path(dataset_root).resolve()
            if dataset_root
            else self.config.dataset_root
        )

        self.aptitude_input_dir = (
            self.dataset_root
            / "04_candidate_responses"
            / "aptitude_responses"
        )

        self.output_dir = self.config.output_dir
        self.output_file = self.output_dir / "aptitude_results.json"

        weight_file = DAY38_DIR / "scoring_weights.json"

        self.logical_scorer = LogicalReasoningScorer(
            str(weight_file)
            if weight_file.exists()
            else None
        )

        # Scenario scorer uses its own default six weights.
        self.scenario_scorer = ScenarioEvaluation()

    # --------------------------------------------------------
    # LOGICAL REASONING SCORER
    # --------------------------------------------------------

    def run_logical_scorer(
        self,
        candidate_id,
        question_id,
        question,
        response,
        parameter_scores,
        difficulty="medium"
    ):

        result = self.logical_scorer.score_response(
            candidate_id=candidate_id,
            question_id=question_id,
            question=question,
            difficulty=difficulty,
            response=response,
            parameter_scores=parameter_scores
        )

        if not isinstance(result, dict):

            raise ValueError(
                "Invalid output from LogicalReasoningScorer."
            )

        if "logical_reasoning_score" not in result:

            raise ValueError(
                "Logical scorer output is missing "
                "'logical_reasoning_score'."
            )

        return result

    # --------------------------------------------------------
    # SCENARIO EVALUATION SCORER
    # --------------------------------------------------------

    def run_scenario_scorer(
        self,
        candidate_id,
        scenario_id,
        scenario,
        response,
        parameter_scores
    ):

        """
        IMPORTANT: Original Day38 method requires FIVE arguments:

        evaluate_scenario(
            candidate_id,
            scenario_id,
            scenario,
            response,
            parameter_scores
        )
        """

        result = self.scenario_scorer.evaluate_scenario(
            candidate_id,
            scenario_id,
            scenario,
            response,
            parameter_scores
        )

        if not isinstance(result, dict):

            raise ValueError(
                "Invalid output from ScenarioEvaluation."
            )

        if "scenario_evaluation_score" not in result:

            raise ValueError(
                "ScenarioEvaluation output is missing "
                "'scenario_evaluation_score'."
            )

        return result

    # --------------------------------------------------------
    # PROCESS ONE CANDIDATE
    # --------------------------------------------------------

    def process_candidate(self, file_path):

        data = load_json(file_path)

        candidate_id = (
            data.get("candidate_id")
            or file_path.stem
        )

        job_id = data.get("job_id")

        response_status = str(
            data.get("response_status", "")
        ).lower()

        # ----------------------------------------------------
        # INCOMPLETE CANDIDATE
        # ----------------------------------------------------

        if response_status != "completed":

            return {

                "candidate_id": candidate_id,
                "job_id": job_id,

                "status": "INCOMPLETE",

                "response_status": (
                    response_status or "missing"
                ),

                "logical_question_count": 0,
                "scenario_question_count": 0,

                "logical_reasoning_average": None,
                "scenario_evaluation_average": None,

                "category_weights": CATEGORY_WEIGHTS,

                "aptitude_score": None,
                "evaluation_level": None,

                "logical_reasoning_results": [],
                "scenario_evaluation_results": [],

                "score_origin": SCORE_ORIGIN,
                "is_simulated": True,

                "errors": [],

                "message": (
                    "Assessment was not provided or "
                    "was not completed."
                ),
            }

        # ----------------------------------------------------
        # VALIDATE RESPONSE COLLECTIONS
        # ----------------------------------------------------

        logical_questions = data.get(
            "logical_reasoning",
            []
        )

        scenario_questions = data.get(
            "scenario_evaluation",
            []
        )

        if not isinstance(logical_questions, list):

            raise ValueError(
                "'logical_reasoning' must be a list."
            )

        if not isinstance(scenario_questions, list):

            raise ValueError(
                "'scenario_evaluation' must be a list."
            )

        logical_results = []
        scenario_results = []
        errors = []

        # ----------------------------------------------------
        # PROCESS LOGICAL REASONING QUESTIONS
        # ----------------------------------------------------

        for index, item in enumerate(
            logical_questions,
            start=1
        ):

            try:

                if not isinstance(item, dict):

                    raise ValueError(
                        "Logical question must be a JSON object."
                    )

                question_id = item.get("question_id")

                question = item.get("question", "")

                answer = item.get("answer", "")

                expected = item.get(
                    "expected_answer",
                    ""
                )

                if (
                    not question_id
                    or not question
                    or not isinstance(answer, str)
                    or not answer.strip()
                ):

                    raise ValueError(
                        "Question ID, question text and "
                        "answer are required."
                    )

                demo_scores = logical_demo_scores(
                    answer,
                    expected
                )

                result = self.run_logical_scorer(
                    candidate_id=candidate_id,
                    question_id=question_id,
                    question=question,
                    response=answer,
                    parameter_scores=demo_scores,
                    difficulty=item.get(
                        "difficulty",
                        "medium"
                    )
                )

                result["expected_answer"] = expected

                result["score_origin"] = SCORE_ORIGIN

                result["is_simulated"] = True

                logical_results.append(result)

            except Exception as exc:

                item_id = (
                    item.get("question_id", f"LOG{index:03d}")
                    if isinstance(item, dict)
                    else f"LOG{index:03d}"
                )
                errors.append(f"Logical {item_id}: {exc}")

        # ----------------------------------------------------
        # PROCESS SCENARIO EVALUATION QUESTIONS
        # ----------------------------------------------------

        for index, item in enumerate(
            scenario_questions,
            start=1
        ):

            try:

                if not isinstance(item, dict):

                    raise ValueError(
                        "Scenario question must be a JSON object."
                    )

                question_id = item.get("question_id")

                question = item.get("question", "")

                answer = item.get("answer", "")

                if (
                    not question_id
                    or not question
                    or not isinstance(answer, str)
                    or not answer.strip()
                ):

                    raise ValueError(
                        "Question ID, question text and "
                        "answer are required."
                    )

                demo_scores = scenario_demo_scores(
                    answer
                )

                # FIXED: candidate_id is now passed as well.
                result = self.run_scenario_scorer(
                    candidate_id=candidate_id,
                    scenario_id=question_id,
                    scenario=question,
                    response=answer,
                    parameter_scores=demo_scores
                )

                result["score_origin"] = SCORE_ORIGIN

                result["is_simulated"] = True

                scenario_results.append(result)

            except Exception as exc:

                item_id = (
                    item.get("question_id", f"SCN{index:03d}")
                    if isinstance(item, dict)
                    else f"SCN{index:03d}"
                )
                errors.append(f"Scenario {item_id}: {exc}")

        # ----------------------------------------------------
        # CALCULATE LOGICAL AND SCENARIO AVERAGES
        # ----------------------------------------------------

        logical_scores = [
            item["logical_reasoning_score"]
            for item in logical_results
        ]

        scenario_scores = [
            item["scenario_evaluation_score"]
            for item in scenario_results
        ]

        logical_average = (
            round(mean(logical_scores), 2)
            if logical_scores
            else None
        )

        scenario_average = (
            round(mean(scenario_scores), 2)
            if scenario_scores
            else None
        )

        # ----------------------------------------------------
        # FINAL APTITUDE SCORE
        # ----------------------------------------------------

        if (
            logical_scores
            and scenario_scores
            and not errors
        ):

            final_score = round(
                logical_average * CATEGORY_WEIGHTS["logical_reasoning"]
                + scenario_average * CATEGORY_WEIGHTS["scenario_evaluation"],
                2
            )

            status = "COMPLETED"

        else:

            final_score = None

            if logical_scores or scenario_scores:

                status = "PARTIAL"

            else:

                status = "INVALID_DATA"

        # ----------------------------------------------------
        # CANDIDATE RESULT
        # ----------------------------------------------------

        return {

            "candidate_id": candidate_id,
            "job_id": job_id,

            "status": status,

            "response_status": response_status,

            "logical_question_count": len(logical_results),

            "scenario_question_count": len(scenario_results),

            "logical_reasoning_average": logical_average,

            "scenario_evaluation_average": scenario_average,

            "category_weights": CATEGORY_WEIGHTS,

            "aptitude_score": final_score,

            "evaluation_level": (
                category(final_score)
                if final_score is not None
                else None
            ),

            "logical_reasoning_results": logical_results,

            "scenario_evaluation_results": scenario_results,

            "errors": errors,

            "score_origin": SCORE_ORIGIN,

            "is_simulated": True,

            "scoring_note": (
                "Demo-only heuristic parameter scores generated "
                "from answer text. Not a human evaluation or "
                "a trained AI assessment."
            ),
        }

    # --------------------------------------------------------
    # RUN ALL CANDIDATES
    # --------------------------------------------------------

    def run(self):

        start_time = time.time()

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        files = (
            sorted(self.aptitude_input_dir.glob("*.json"))
            if self.aptitude_input_dir.exists()
            else []
        )

        if not files:

            raise FileNotFoundError(
                "No candidate aptitude JSON files found in "
                f"{self.aptitude_input_dir}"
            )

        results = []

        # ----------------------------------------------------
        # PROCESS EVERY JSON FILE
        # ----------------------------------------------------

        for file_path in files:

            try:

                result = self.process_candidate(
                    file_path
                )

                results.append(result)

            except Exception as exc:

                results.append({

                    "candidate_id": file_path.stem,

                    "status": "ERROR",

                    "errors": [str(exc)],

                    "aptitude_score": None,

                    "score_origin": SCORE_ORIGIN,

                    "is_simulated": True,
                })

        # ----------------------------------------------------
        # SUMMARY COUNTS
        # ----------------------------------------------------

        counts = {

            "total_candidates": len(results),

            "completed": sum(
                item.get("status") == "COMPLETED"
                for item in results
            ),

            "incomplete": sum(
                item.get("status") == "INCOMPLETE"
                for item in results
            ),

            "partial": sum(
                item.get("status") == "PARTIAL"
                for item in results
            ),

            "invalid_data": sum(
                item.get("status") == "INVALID_DATA"
                for item in results
            ),

            "errors": sum(
                item.get("status") == "ERROR"
                or bool(item.get("errors"))
                for item in results
            ),
        }

        # ----------------------------------------------------
        # PIPELINE OUTPUT
        # ----------------------------------------------------

        output = {

            "module": "Configurable Aptitude Adapter",
            "dataset": self.config.dataset_name,
            "dataset_type": self.config.dataset_type,
            "dataset_root": str(self.dataset_root),

            "pipeline_status": (
                "SUCCESS"
                if counts["errors"] == 0
                else "COMPLETED_WITH_ERRORS"
            ),

            "score_type": SCORE_ORIGIN,

            "is_simulated": True,

            "candidate_summary": counts,

            "execution_time_seconds": round(
                time.time() - start_time,
                4
            ),

            "candidates": results,
        }

        save_json(
            self.output_file,
            output
        )

        # ----------------------------------------------------
        # CONSOLE REPORT
        # ----------------------------------------------------

        print("\nDAY63 APTITUDE ADAPTER")
        print("---------------------")

        print(
            f"Total candidates : {counts['total_candidates']}"
        )

        print(
            f"Completed        : {counts['completed']}"
        )

        print(
            f"Incomplete       : {counts['incomplete']}"
        )

        print(
            f"Partial          : {counts['partial']}"
        )

        print(
            f"Invalid data     : {counts['invalid_data']}"
        )

        print(
            f"Errors           : {counts['errors']}"
        )

        print(
            f"Output           : {self.output_file}"
        )

        print("\nCandidate Scores")

        for candidate in results:

            score = candidate.get(
                "aptitude_score"
            )

            score_text = (
                f"{score}/100"
                if score is not None
                else "No score"
            )

            print(
                f"{candidate.get('candidate_id')}: "
                f"{candidate.get('status')} - {score_text}"
            )

        return output


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":

    adapter = AptitudeAdapter()

    adapter.run()
