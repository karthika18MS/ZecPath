import json
from datetime import datetime, timezone
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = CURRENT_DIR / "results"


class ImprovedScoringModel:
    """
    Improved screening scoring model for Day 30.

    The model keeps the original four scoring dimensions:
    - Clarity
    - Relevance
    - Completeness
    - Consistency

    It adds conservative handling for communication problems
    so that a candidate is not excessively penalized for a
    single weak response.
    """

    PARAMETERS = [
        "clarity",
        "relevance",
        "completeness",
        "consistency"
    ]

    WEIGHTS = {
        "clarity": 0.25,
        "relevance": 0.25,
        "completeness": 0.25,
        "consistency": 0.25
    }

    def normalize_score(self, score):
        score = max(
            0,
            min(10, score)
        )

        return round(
            (score / 10) * 100,
            2
        )

    def calculate_question_score(
        self,
        clarity,
        relevance,
        completeness,
        consistency
    ):
        scores = {
            "clarity": clarity,
            "relevance": relevance,
            "completeness": completeness,
            "consistency": consistency
        }

        weighted_score = sum(
            scores[parameter]
            * self.WEIGHTS[parameter]
            for parameter in self.PARAMETERS
        )

        return {
            "raw_score": round(
                weighted_score,
                2
            ),
            "normalized_score": self.normalize_score(
                weighted_score
            ),
            "parameter_scores": scores
        }

    def calculate_response_score(
        self,
        response_type,
        answer_status,
        clarity,
        relevance,
        completeness,
        consistency
    ):
        """
        Calculate a score while preventing an isolated
        communication problem from causing an extreme score.
        """

        if answer_status == "no_response":
            return {
                "score": 0,
                "reason": "No response was provided."
            }

        result = self.calculate_question_score(
            clarity,
            relevance,
            completeness,
            consistency
        )

        normalized_score = result["normalized_score"]

        if response_type == "off_topic":
            normalized_score = min(
                normalized_score,
                50
            )

        elif response_type == "vague":
            normalized_score = max(
                normalized_score,
                35
            )

        elif response_type == "confused":
            normalized_score = max(
                normalized_score,
                40
            )

        return {
            "score": normalized_score,
            "raw_score": result["raw_score"],
            "parameter_scores": result["parameter_scores"],
            "reason": (
                "Score calculated using the improved "
                "four-parameter screening model."
            )
        }

    def save_result(
        self,
        result,
        filename="scoring_optimization_results.json"
    ):
        RESULTS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path = RESULTS_DIR / filename

        result["created_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                result,
                file,
                indent=4
            )

        return output_path


if __name__ == "__main__":

    scorer = ImprovedScoringModel()

    test_cases = [
        {
            "test_id": "STRONG_RESPONSE",
            "response_type": "valid",
            "answer_status": "valid",
            "clarity": 9,
            "relevance": 10,
            "completeness": 10,
            "consistency": 9
        },
        {
            "test_id": "VAGUE_RESPONSE",
            "response_type": "vague",
            "answer_status": "valid",
            "clarity": 4,
            "relevance": 4,
            "completeness": 3,
            "consistency": 5
        },
        {
            "test_id": "CONFUSED_RESPONSE",
            "response_type": "confused",
            "answer_status": "valid",
            "clarity": 4,
            "relevance": 5,
            "completeness": 4,
            "consistency": 6
        },
        {
            "test_id": "OFF_TOPIC_RESPONSE",
            "response_type": "off_topic",
            "answer_status": "valid",
            "clarity": 8,
            "relevance": 1,
            "completeness": 2,
            "consistency": 7
        }
    ]

    results = []

    for case in test_cases:

        score = scorer.calculate_response_score(
            response_type=case["response_type"],
            answer_status=case["answer_status"],
            clarity=case["clarity"],
            relevance=case["relevance"],
            completeness=case["completeness"],
            consistency=case["consistency"]
        )

        results.append({
            "test_id": case["test_id"],
            "score_result": score
        })

    output = {
        "report_type": "Improved Screening Scoring Results",
        "model": "Improved Four-Parameter Scoring Model",
        "parameters": [
            "Clarity",
            "Relevance",
            "Completeness",
            "Consistency"
        ],
        "results": results
    }

    output_path = scorer.save_result(output)

    print("\nImproved Scoring Results:")
    print(json.dumps(output, indent=4))

    print(
        f"\nResult saved to: {output_path}"
    )