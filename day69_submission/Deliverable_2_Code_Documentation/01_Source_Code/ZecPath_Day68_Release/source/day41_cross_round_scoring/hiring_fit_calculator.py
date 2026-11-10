class HiringFitCalculator:
    """
    Day 41 - Hiring Fit Calculator

    Calculates hiring fit using:
        ATS score
        Screening score
        HR interview score

    The weights are role-specific and are supplied
    through config.json.
    """

    def __init__(self, role_weights):
        self.role_weights = role_weights
        self.validate_weights()

    # --------------------------------------------------
    # Validate weights
    # --------------------------------------------------

    def validate_weights(self):

        required_weights = {
            "ats",
            "screening",
            "hr"
        }

        if set(self.role_weights.keys()) != required_weights:
            raise ValueError(
                "Weights must contain exactly: "
                "ats, screening, hr"
            )

        for name, weight in self.role_weights.items():

            if not isinstance(weight, (int, float)):
                raise ValueError(
                    f"{name} weight must be numeric."
                )

            if weight < 0 or weight > 1:
                raise ValueError(
                    f"{name} weight must be between 0 and 1."
                )

        total = sum(self.role_weights.values())

        if abs(total - 1.0) > 0.0001:
            raise ValueError(
                f"Weights must total 1.0. "
                f"Current total = {total}"
            )

    # --------------------------------------------------
    # Validate scores
    # --------------------------------------------------

    def validate_scores(
        self,
        ats_score,
        screening_score,
        hr_score
    ):

        scores = {
            "ats": ats_score,
            "screening": screening_score,
            "hr": hr_score
        }

        for name, score in scores.items():

            if not isinstance(score, (int, float)):
                raise ValueError(
                    f"{name} score must be numeric."
                )

            if score < 0 or score > 100:
                raise ValueError(
                    f"{name} score must be between 0 and 100."
                )

    # --------------------------------------------------
    # Calculate hiring fit
    # --------------------------------------------------

    def calculate(
        self,
        ats_score,
        screening_score,
        hr_score
    ):

        self.validate_scores(
            ats_score,
            screening_score,
            hr_score
        )

        ats_contribution = (
            ats_score * self.role_weights["ats"]
        )

        screening_contribution = (
            screening_score
            * self.role_weights["screening"]
        )

        hr_contribution = (
            hr_score
            * self.role_weights["hr"]
        )

        hiring_fit = (
            ats_contribution
            + screening_contribution
            + hr_contribution
        )

        return round(hiring_fit, 2)

    # --------------------------------------------------
    # Generate complete result
    # --------------------------------------------------

    def generate_result(
        self,
        candidate_id,
        job_id,
        target_role,
        ats_score,
        screening_score,
        hr_score
    ):

        hiring_fit = self.calculate(
            ats_score,
            screening_score,
            hr_score
        )

        return {
            "candidate_id": candidate_id,

            "job_id": job_id,

            "target_role": target_role,

            "round_scores": {
                "ats": round(ats_score, 2),
                "screening": round(screening_score, 2),
                "hr": round(hr_score, 2)
            },

            "weights": {
                "ats": self.role_weights["ats"],
                "screening": self.role_weights["screening"],
                "hr": self.role_weights["hr"]
            },

            "weighted_contributions": {
                "ats": round(
                    ats_score
                    * self.role_weights["ats"],
                    2
                ),

                "screening": round(
                    screening_score
                    * self.role_weights["screening"],
                    2
                ),

                "hr": round(
                    hr_score
                    * self.role_weights["hr"],
                    2
                )
            },

            "hiring_fit_percentage": hiring_fit,

            "status": "Calculated"
        }