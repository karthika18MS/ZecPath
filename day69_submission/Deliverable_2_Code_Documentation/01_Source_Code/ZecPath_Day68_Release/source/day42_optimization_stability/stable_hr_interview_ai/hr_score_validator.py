class HRScoreValidator:
    """
    Day 42 - HR Score Stability Validator

    Validates the real HR interview score generated
    by the Day 37 HR scoring engine.
    """

    def __init__(self, config):

        self.config = config

        self.score_min = config[
            "hr_scoring"
        ]["score_min"]

        self.score_max = config[
            "hr_scoring"
        ]["score_max"]

        self.required_weight_total = config[
            "hr_scoring"
        ]["require_weight_total"]

    # =========================================================
    # VALIDATE FINAL SCORE
    # =========================================================

    def validate_score(self, score):
        """
        Validate a score between 0 and 100.
        """

        errors = []

        if not isinstance(
            score,
            (int, float)
        ):

            errors.append(
                "HR score is not numeric."
            )

            return errors

        if not (
            self.score_min
            <= score
            <= self.score_max
        ):

            errors.append(
                f"HR score {score} is outside "
                f"the valid range "
                f"{self.score_min}-{self.score_max}."
            )

        return errors

    # =========================================================
    # VALIDATE WEIGHTS
    # =========================================================

    def validate_weights(self, weights):
        """
        Validate scoring weights.
        """

        errors = []

        if not isinstance(
            weights,
            dict
        ):

            return [
                "Scoring weights are missing."
            ]

        # -----------------------------------------------------
        # Validate numeric values
        # -----------------------------------------------------

        for name, weight in weights.items():

            if not isinstance(
                weight,
                (int, float)
            ):

                errors.append(
                    f"Weight '{name}' is not numeric."
                )

            elif weight < 0:

                errors.append(
                    f"Weight '{name}' is negative."
                )

        # -----------------------------------------------------
        # Validate total
        # -----------------------------------------------------

        if not errors:

            total = sum(
                weights.values()
            )

            if round(total, 6) != round(
                self.required_weight_total,
                6
            ):

                errors.append(
                    f"Weight total is {total}, "
                    f"expected "
                    f"{self.required_weight_total}."
                )

        return errors

    # =========================================================
    # VALIDATE QUESTION
    # =========================================================

    def validate_question(
        self,
        question,
        index
    ):
        """
        Validate one Day 37 question record.

        Day 37 now provides:
            question_id
            question_text
            candidate_answer
            question_score
        """

        errors = []

        question_id = question.get(
            "question_id"
        )

        # -----------------------------------------------------
        # Question ID
        # -----------------------------------------------------

        if not question_id:

            errors.append(
                f"Question {index}: "
                f"Missing question_id."
            )

        # -----------------------------------------------------
        # Question text
        # -----------------------------------------------------

        question_text = question.get(
            "question_text"
        )

        if not question_text:

            errors.append(
                f"{question_id or index}: "
                f"Missing question_text."
            )

        # -----------------------------------------------------
        # Candidate answer
        # -----------------------------------------------------

        candidate_answer = question.get(
            "candidate_answer"
        )

        if not candidate_answer:

            errors.append(
                f"{question_id or index}: "
                f"Missing candidate_answer."
            )

        # -----------------------------------------------------
        # Question score
        # -----------------------------------------------------

        question_score = question.get(
            "question_score"
        )

        errors.extend(
            self.validate_score(
                question_score
            )
        )

        return errors

    # =========================================================
    # VALIDATE COMPLETE RESULT
    # =========================================================

    def validate_result(self, result):
        """
        Validate the complete Day 37 HR scoring result.
        """

        errors = []

        # -----------------------------------------------------
        # Final HR score
        # -----------------------------------------------------

        final_score = result.get(
            "final_hr_interview_score"
        )

        errors.extend(
            self.validate_score(
                final_score
            )
        )

        # -----------------------------------------------------
        # Scoring weights
        # -----------------------------------------------------

        weights = result.get(
            "scoring_weights"
        )

        errors.extend(
            self.validate_weights(
                weights
            )
        )

        # -----------------------------------------------------
        # Question scores
        # -----------------------------------------------------

        question_scores = result.get(
            "question_scores",
            []
        )

        if not question_scores:

            errors.append(
                "No question scores found."
            )

        # -----------------------------------------------------
        # Validate every question
        # -----------------------------------------------------

        for index, question in enumerate(
            question_scores,
            start=1
        ):

            if not isinstance(
                question,
                dict
            ):

                errors.append(
                    f"Question {index} is not a valid object."
                )

                continue

            errors.extend(
                self.validate_question(
                    question,
                    index
                )
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "final_hr_interview_score":
                final_score,
            "question_count":
                len(question_scores)
        }