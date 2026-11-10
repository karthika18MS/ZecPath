import json
import os


class ScenarioEvaluation:

    DEFAULT_WEIGHTS = {
        "situation_understanding": 0.15,
        "problem_identification": 0.15,
        "decision_making": 0.20,
        "problem_solving": 0.25,
        "communication_clarity": 0.15,
        "outcome_awareness": 0.10
    }

    def __init__(self, weights_file=None):

        self.weights = self.DEFAULT_WEIGHTS.copy()

        if weights_file and os.path.exists(weights_file):
            with open(weights_file, "r", encoding="utf-8") as file:
                loaded_weights = json.load(file)

            self._validate_weights(loaded_weights)
            self.weights = loaded_weights

    def _validate_weights(self, weights):

        expected_keys = set(self.DEFAULT_WEIGHTS.keys())

        if set(weights.keys()) != expected_keys:
            raise ValueError("Invalid scoring weight parameters.")

        total = 0

        for key, value in weights.items():

            if not isinstance(value, (int, float)):
                raise ValueError(
                    f"Weight for {key} must be numeric."
                )

            if value < 0:
                raise ValueError(
                    f"Weight for {key} cannot be negative."
                )

            total += value

        if abs(total - 1.0) > 0.0001:
            raise ValueError(
                f"Scoring weights must total 1.0. Current total: {total}"
            )

    def normalize_score(self, score):

        score = max(0, min(100, score))

        return round(score, 2)

    def calculate_score(self, parameter_scores):

        weighted_contributions = {}

        final_score = 0

        for parameter, weight in self.weights.items():

            score = self.normalize_score(
                parameter_scores.get(parameter, 0)
            )

            contribution = score * weight

            weighted_contributions[parameter] = round(
                contribution, 2
            )

            final_score += contribution

        return {
            "weighted_contributions": weighted_contributions,
            "scenario_evaluation_score": round(final_score, 2)
        }

    def get_evaluation_level(self, score):

        if score >= 80:
            return "strong"

        elif score >= 60:
            return "moderate"

        return "needs_improvement"

    def get_response_status(self, response):

        if not response or not response.strip():
            return "empty"

        words = response.strip().split()

        if len(words) < 5:
            return "insufficient"

        return "valid"

    def evaluate_scenario(
        self,
        candidate_id,
        scenario_id,
        scenario,
        response,
        parameter_scores
    ):

        response_status = self.get_response_status(response)

        scoring_result = self.calculate_score(
            parameter_scores
        )

        final_score = scoring_result[
            "scenario_evaluation_score"
        ]

        evaluation_level = self.get_evaluation_level(
            final_score
        )

        return {
            "candidate_id": candidate_id,
            "scenario_id": scenario_id,
            "scenario": scenario,
            "response": response,
            "response_status": response_status,
            "parameter_scores": parameter_scores,
            "weights": self.weights,
            "weighted_contributions": scoring_result[
                "weighted_contributions"
            ],
            "scenario_evaluation_score": final_score,
            "evaluation_level": evaluation_level
        }

    def save_result(self, result, output_file):

        os.makedirs(
            os.path.dirname(output_file),
            exist_ok=True
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4,
                ensure_ascii=False
            )


if __name__ == "__main__":

    print("DAY 38 — SCENARIO EVALUATION FRAMEWORK")
    print("---------------------------------------")

    scorer = ScenarioEvaluation()

    candidate_id = "candidate_006"

    scenario_id = "APT_SCENARIO_003"

    scenario = (
        "A team member is not completing an assigned "
        "task on time and the project deadline is approaching. "
        "What would you do?"
    )

    response = (
        "First, I would talk to the team member and understand "
        "the reason for the delay. If they are facing a technical "
        "or workload-related issue, I would help them or discuss "
        "how the task can be completed efficiently. If the delay "
        "can affect the project deadline, I would inform the team "
        "lead and work with the team to redistribute tasks if "
        "required. I would then monitor the progress to ensure "
        "that the deadline is achieved."
    )

    parameter_scores = {
        "situation_understanding": 90,
        "problem_identification": 90,
        "decision_making": 88,
        "problem_solving": 92,
        "communication_clarity": 90,
        "outcome_awareness": 88
    }

    result = scorer.evaluate_scenario(
        candidate_id,
        scenario_id,
        scenario,
        response,
        parameter_scores
    )

    output_file = os.path.join(
        os.path.dirname(__file__),
        "results",
        "scenario_evaluation_results.json"
    )

    scorer.save_result(
        result,
        output_file
    )

    print(f"Candidate: {candidate_id}")
    print(f"Scenario ID: {scenario_id}")
    print(f"Response Status: {result['response_status']}")
    print()
    print("Parameter Scores:")

    for parameter, score in parameter_scores.items():

        print(
            f"{parameter.replace('_', ' ').title()}: {score}"
        )

    print()
    print("Weighted Contributions:")

    for parameter, contribution in result[
        "weighted_contributions"
    ].items():

        print(
            f"{parameter.replace('_', ' ').title()}: "
            f"{contribution}"
        )

    print()
    print(
        f"Scenario Evaluation Score: "
        f"{result['scenario_evaluation_score']}/100"
    )

    print(
        f"Evaluation Level: "
        f"{result['evaluation_level']}"
    )

    print()
    print(f"Saved Result: {output_file}")