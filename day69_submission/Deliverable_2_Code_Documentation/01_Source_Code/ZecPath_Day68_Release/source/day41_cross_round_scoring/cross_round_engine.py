class CrossRoundScoringEngine:

    def __init__(self, weights):

        self.weights = weights

        self.validate_weights()

    def validate_weights(self):

        required_rounds = {
            "ats",
            "hr",
            "aptitude"
        }

        if set(self.weights.keys()) != required_rounds:

            raise ValueError(
                "Weights must contain exactly: "
                "ats, hr, aptitude"
            )

        total = sum(
            self.weights.values()
        )

        if abs(total - 1.0) > 0.0001:

            raise ValueError(
                f"Round weights must total 1.0. "
                f"Current total = {total}"
            )

    def calculate(
        self,
        ats_score,
        hr_score,
        aptitude_score
    ):

        final_score = (

            ats_score
            * self.weights["ats"]

            +

            hr_score
            * self.weights["hr"]

            +

            aptitude_score
            * self.weights["aptitude"]

        )

        return round(final_score, 2)