class ScoreValidator:

    REQUIRED_PARAMETERS = [
        "answer_relevance",
        "communication",
        "confidence",
        "consistency"
    ]

    def __init__(
        self,
        weights,
        score_min=0,
        score_max=100
    ):

        self.weights = weights

        self.score_min = (
            score_min
        )

        self.score_max = (
            score_max
        )

    # =========================================================
    # VALIDATE WEIGHTS
    # =========================================================

    def validate_weights(self):

        errors = []

        if not isinstance(
            self.weights,
            dict
        ):

            return {
                "valid": False,
                "errors": [
                    "Weights must be a dictionary."
                ]
            }

        # -----------------------------------------------------
        # Required parameters
        # -----------------------------------------------------

        for parameter in (
            self.REQUIRED_PARAMETERS
        ):

            if parameter not in self.weights:

                errors.append(
                    f"Missing weight: {parameter}"
                )

        # -----------------------------------------------------
        # Numeric values
        # -----------------------------------------------------

        for parameter, weight in (
            self.weights.items()
        ):

            if not isinstance(
                weight,
                (int, float)
            ):

                errors.append(
                    f"Invalid weight for "
                    f"{parameter}."
                )

            elif weight < 0:

                errors.append(
                    f"Negative weight for "
                    f"{parameter}."
                )

        # -----------------------------------------------------
        # Weight total
        # -----------------------------------------------------

        if not errors:

            total = sum(
                self.weights.values()
            )

            if abs(
                total - 1.0
            ) > 0.000001:

                errors.append(
                    f"Weight total must equal 1.0. "
                    f"Current total: {total}"
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    # =========================================================
    # VALIDATE SCORE
    # =========================================================

    def validate_score(
        self,
        score
    ):

        errors = []

        if not isinstance(
            score,
            (int, float)
        ):

            errors.append(
                "Score must be numeric."
            )

        else:

            if score < self.score_min:

                errors.append(
                    f"Score cannot be below "
                    f"{self.score_min}."
                )

            if score > self.score_max:

                errors.append(
                    f"Score cannot exceed "
                    f"{self.score_max}."
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    # =========================================================
    # VALIDATE PARAMETER SCORES
    # =========================================================

    def validate_parameter_scores(
        self,
        parameter_scores
    ):

        errors = []

        if not isinstance(
            parameter_scores,
            dict
        ):

            return {
                "valid": False,
                "errors": [
                    "Parameter scores must be a dictionary."
                ]
            }

        for parameter in (
            self.REQUIRED_PARAMETERS
        ):

            if parameter not in parameter_scores:

                errors.append(
                    f"Missing parameter score: "
                    f"{parameter}"
                )

                continue

            score_validation = (
                self.validate_score(
                    parameter_scores[
                        parameter
                    ]
                )
            )

            errors.extend(
                score_validation["errors"]
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }