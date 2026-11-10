import json
import os


class LogicalReasoningScorer:

    DEFAULT_WEIGHTS = {
        "problem_understanding": 0.20,
        "reasoning": 0.30,
        "decision_quality": 0.20,
        "explanation_clarity": 0.15,
        "conclusion": 0.15
    }

    def __init__(self, weight_file=None):
        self.weights = self.load_weights(weight_file)

    def load_weights(self, weight_file=None):
        """
        Load scoring weights from JSON configuration.
        If the configuration is missing or invalid,
        use the default weights.
        """

        if weight_file is None:
            weight_file = os.path.join(
                os.path.dirname(__file__),
                "scoring_weights.json"
            )

        try:
            with open(weight_file, "r", encoding="utf-8") as file:
                weights = json.load(file)

            self.validate_weights(weights)
            return weights

        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            print("Warning: Invalid weight configuration. Using default weights.")
            return self.DEFAULT_WEIGHTS.copy()

    def validate_weights(self, weights):
        """
        Validate scoring weights.
        """

        required_keys = set(self.DEFAULT_WEIGHTS.keys())

        if set(weights.keys()) != required_keys:
            raise ValueError("Weight configuration contains invalid parameters.")

        total = 0.0

        for key, value in weights.items():

            if not isinstance(value, (int, float)):
                raise ValueError(f"Weight for {key} must be numeric.")

            if value < 0:
                raise ValueError(f"Weight for {key} cannot be negative.")

            total += value

        if abs(total - 1.0) > 0.0001:
            raise ValueError("Scoring weights must add up to 1.0.")

    def normalize_score(self, score):
        """
        Keep score within 0-100.
        """

        if not isinstance(score, (int, float)):
            raise ValueError("Score must be numeric.")

        return round(max(0, min(100, score)), 2)

    def calculate_score(self, parameter_scores):
        """
        Calculate weighted logical reasoning score.
        """

        required_parameters = set(self.weights.keys())

        if set(parameter_scores.keys()) != required_parameters:
            raise ValueError(
                "Parameter scores do not match the configured scoring parameters."
            )

        normalized_scores = {}

        for parameter, score in parameter_scores.items():
            normalized_scores[parameter] = self.normalize_score(score)

        weighted_contributions = {}

        for parameter, score in normalized_scores.items():
            weighted_contributions[parameter] = round(
                score * self.weights[parameter],
                2
            )

        final_score = round(
            sum(weighted_contributions.values()),
            2
        )

        return {
            "parameter_scores": normalized_scores,
            "weights": self.weights,
            "weighted_contributions": weighted_contributions,
            "logical_reasoning_score": final_score
        }

    def score_response(
        self,
        candidate_id,
        question_id,
        question,
        difficulty,
        response,
        parameter_scores
    ):
        """
        Create a complete explainable scoring result.
        """

        score_result = self.calculate_score(parameter_scores)

        return {
            "candidate_id": candidate_id,
            "question_id": question_id,
            "question": question,
            "difficulty": difficulty,
            "response": response,
            "parameter_scores": score_result["parameter_scores"],
            "weights": score_result["weights"],
            "weighted_contributions": score_result["weighted_contributions"],
            "logical_reasoning_score": score_result["logical_reasoning_score"]
        }

    def save_result(self, result, output_file=None):

        if output_file is None:
            output_directory = os.path.join(
                os.path.dirname(__file__),
                "results"
            )

            os.makedirs(output_directory, exist_ok=True)

            output_file = os.path.join(
                output_directory,
                "logical_reasoning_results.json"
            )

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4)

        return output_file


if __name__ == "__main__":

    scorer = LogicalReasoningScorer()

    candidate_id = "candidate_006"
    question_id = "APT_LOGIC_003"

    question = (
        "A project has five tasks. Task A must be completed before "
        "Task B, and Task C must be completed before Task D. "
        "Which tasks can be started independently?"
    )

    difficulty = "medium"

    response = (
        "Task A and Task C can be started independently because "
        "neither of them depends on another task. After Task A, "
        "Task B can be started, and after Task C, Task D can be started."
    )

    parameter_scores = {
        "problem_understanding": 90,
        "reasoning": 85,
        "decision_quality": 85,
        "explanation_clarity": 90,
        "conclusion": 85
    }

    result = scorer.score_response(
        candidate_id=candidate_id,
        question_id=question_id,
        question=question,
        difficulty=difficulty,
        response=response,
        parameter_scores=parameter_scores
    )

    print("DAY 38 — LOGICAL REASONING SCORING")
    print("-----------------------------------")
    print(f"Candidate: {candidate_id}")
    print(f"Question ID: {question_id}")
    print(f"Difficulty: {difficulty}")

    print("\nParameter Scores:")

    for parameter, score in result["parameter_scores"].items():
        print(
            f"{parameter.replace('_', ' ').title()}: {score}"
        )

    print("\nWeighted Contributions:")

    for parameter, contribution in result["weighted_contributions"].items():
        print(
            f"{parameter.replace('_', ' ').title()}: {contribution}"
        )

    print(
        f"\nLogical Reasoning Score: "
        f"{result['logical_reasoning_score']}/100"
    )

    output_file = scorer.save_result(result)

    print(f"\nSaved Result: {output_file}")