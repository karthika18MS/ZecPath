class ScoringParameters:
    """
    Defines the scoring parameters used for candidate screening.

    Each parameter is scored from 0 to 10.
    The final score is normalized to 0 to 100.
    """

    MIN_SCORE = 0
    MAX_SCORE = 10

    # Scoring parameters
    CLARITY = "clarity"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"

    PARAMETERS = [
        CLARITY,
        RELEVANCE,
        COMPLETENESS,
        CONSISTENCY
    ]

    # Equal weights
    WEIGHTS = {
        CLARITY: 0.25,
        RELEVANCE: 0.25,
        COMPLETENESS: 0.25,
        CONSISTENCY: 0.25
    }

    @classmethod
    def validate_score(cls, score):
        """
        Validate that a score is between 0 and 10.
        """

        return (
            isinstance(score, (int, float))
            and cls.MIN_SCORE <= score <= cls.MAX_SCORE
        )

    @classmethod
    def normalize_score(cls, score):
        """
        Convert a score from 0-10 to 0-100.
        """

        if not cls.validate_score(score):
            raise ValueError("Score must be between 0 and 10.")

        return round(
            (score / cls.MAX_SCORE) * 100,
            2
        )

    @classmethod
    def calculate_weighted_score(
        cls,
        clarity,
        relevance,
        completeness,
        consistency
    ):
        """
        Calculate the weighted score out of 10.
        """

        scores = {
            cls.CLARITY: clarity,
            cls.RELEVANCE: relevance,
            cls.COMPLETENESS: completeness,
            cls.CONSISTENCY: consistency
        }

        # Validate every score
        for parameter, score in scores.items():

            if not cls.validate_score(score):
                raise ValueError(
                    f"{parameter} score must be between 0 and 10."
                )

        weighted_score = sum(
            scores[parameter] * cls.WEIGHTS[parameter]
            for parameter in cls.PARAMETERS
        )

        return round(weighted_score, 2)


if __name__ == "__main__":

    print("=" * 70)
    print("ZecPath - Day 26")
    print("SCORING PARAMETERS")
    print("=" * 70)

    print("\nParameters:")

    for parameter in ScoringParameters.PARAMETERS:
        print(f"- {parameter.capitalize()}")

    print("\nWeights:")

    for parameter, weight in ScoringParameters.WEIGHTS.items():
        print(
            f"- {parameter.capitalize()}: "
            f"{weight * 100:.0f}%"
        )

    # Example calculation
    score = ScoringParameters.calculate_weighted_score(
        clarity=9,
        relevance=10,
        completeness=9,
        consistency=10
    )

    normalized = ScoringParameters.normalize_score(score)

    print("\nExample:")
    print(f"Weighted Score: {score}/10")
    print(f"Normalized Score: {normalized}/100")

    print("=" * 70)