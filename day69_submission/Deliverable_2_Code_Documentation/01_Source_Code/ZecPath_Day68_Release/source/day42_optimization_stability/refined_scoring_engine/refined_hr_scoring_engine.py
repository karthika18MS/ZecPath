import json
from pathlib import Path

from .score_validator import (
    ScoreValidator
)


class RefinedHRScoringEngine:

    def __init__(
        self,
        config_path
    ):

        self.config_path = Path(
            config_path
        )

        self.config = (
            self.load_config()
        )

        self.weights = (
            self.config["weights"]
        )

        score_range = (
            self.config.get(
                "score_range",
                {}
            )
        )

        self.score_min = (
            score_range.get(
                "minimum",
                0
            )
        )

        self.score_max = (
            score_range.get(
                "maximum",
                100
            )
        )

        self.validator = (
            ScoreValidator(
                self.weights,
                self.score_min,
                self.score_max
            )
        )

    # =========================================================
    # LOAD CONFIGURATION
    # =========================================================

    def load_config(self):

        if not self.config_path.exists():

            raise FileNotFoundError(
                f"Scoring configuration not found: "
                f"{self.config_path}"
            )

        with open(
            self.config_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    # =========================================================
    # EXTRACT PARAMETER SCORES
    # =========================================================

    def get_parameter_scores(
        self,
        hr_result
    ):

        parameter_scores = (
            hr_result.get(
                "parameter_averages",
                {}
            )
        )

        return parameter_scores

    # =========================================================
    # VALIDATE QUESTION DATA
    # =========================================================

    def validate_question_data(
        self,
        hr_result
    ):

        errors = []

        questions = (
            hr_result.get(
                "question_scores",
                []
            )
        )

        if not isinstance(
            questions,
            list
        ):

            return [
                "question_scores must be a list."
            ]

        if not questions:

            errors.append(
                "No question scores found."
            )

            return errors

        for index, question in enumerate(
            questions,
            start=1
        ):

            question_id = (
                question.get(
                    "question_id"
                )
            )

            question_text = (
                question.get(
                    "question_text"
                )
                or question.get(
                    "question"
                )
            )

            candidate_answer = (
                question.get(
                    "candidate_answer"
                )
            )

            if not question_id:

                errors.append(
                    f"Question {index}: "
                    f"Missing question_id."
                )

            if not question_text:

                errors.append(
                    f"{question_id or index}: "
                    f"Missing question_text."
                )

            if not candidate_answer:

                errors.append(
                    f"{question_id or index}: "
                    f"Missing candidate_answer."
                )

        return errors

    # =========================================================
    # CALCULATE REFINED SCORE
    # =========================================================

    def calculate_refined_score(
        self,
        parameter_scores
    ):

        weight_validation = (
            self.validator.validate_weights()
        )

        if not weight_validation["valid"]:

            raise ValueError(
                "Invalid scoring weights: "
                + str(
                    weight_validation["errors"]
                )
            )

        score_validation = (
            self.validator.validate_parameter_scores(
                parameter_scores
            )
        )

        if not score_validation["valid"]:

            raise ValueError(
                "Invalid parameter scores: "
                + str(
                    score_validation["errors"]
                )
            )

        weighted_contributions = {}

        total_score = 0.0

        for parameter, weight in (
            self.weights.items()
        ):

            raw_score = (
                parameter_scores.get(
                    parameter
                )
            )

            contribution = (
                raw_score * weight
            )

            weighted_contributions[
                parameter
            ] = round(
                contribution,
                2
            )

            total_score += contribution

        rounding = (
            self.config.get(
                "rounding",
                2
            )
        )

        refined_score = round(
            total_score,
            rounding
        )

        return {

            "parameter_scores":
                parameter_scores,

            "weights":
                self.weights,

            "weighted_contributions":
                weighted_contributions,

            "refined_hr_score":
                refined_score
        }

    # =========================================================
    # REFINE REAL DAY 37 RESULT
    # =========================================================

    def refine(
        self,
        hr_result
    ):

        # -----------------------------------------------------
        # Validate Day 37 question data
        # -----------------------------------------------------

        question_errors = (
            self.validate_question_data(
                hr_result
            )
        )

        if question_errors:

            raise ValueError(
                "Invalid Day 37 question data: "
                + str(question_errors)
            )

        # -----------------------------------------------------
        # Parameter scores
        # -----------------------------------------------------

        parameter_scores = (
            self.get_parameter_scores(
                hr_result
            )
        )

        # -----------------------------------------------------
        # Calculate
        # -----------------------------------------------------

        result = (
            self.calculate_refined_score(
                parameter_scores
            )
        )

        # -----------------------------------------------------
        # Original score
        # -----------------------------------------------------

        original_score = (
            hr_result.get(
                "final_hr_interview_score"
            )
        )

        result[
            "original_hr_score"
        ] = original_score

        # -----------------------------------------------------
        # Difference
        # -----------------------------------------------------

        if isinstance(
            original_score,
            (int, float)
        ):

            result[
                "score_difference"
            ] = round(
                result[
                    "refined_hr_score"
                ]
                - original_score,
                2
            )

        else:

            result[
                "score_difference"
            ] = None

        # -----------------------------------------------------
        # Candidate
        # -----------------------------------------------------

        result[
            "candidate_id"
        ] = hr_result.get(
            "candidate_id"
        )

        # -----------------------------------------------------
        # Job
        # -----------------------------------------------------

        result[
            "job_id"
        ] = hr_result.get(
            "job_id"
        )

        # -----------------------------------------------------
        # Questions
        # -----------------------------------------------------

        result[
            "question_count"
        ] = hr_result.get(
            "total_questions"
        )

        # -----------------------------------------------------
        # Validation
        # -----------------------------------------------------

        result[
            "question_data_validation"
        ] = {
            "valid": True,
            "message":
                "Day 37 question_text and "
                "candidate_answer are available."
        }

        return result