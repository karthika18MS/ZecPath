def extract_ats_score(data):
    """
    Extract final ATS score from Day 18 result.
    """

    try:
        return float(data["scores"]["final_ats_score"])
    except (KeyError, TypeError, ValueError):
        raise ValueError(
            "Unable to extract ATS score from Day 18 result."
        )


def extract_hr_score(data):
    """
    Extract final HR interview score from Day 37 result.
    """

    try:
        return float(data["final_evaluation"]["final_hr_interview_score"])
    except (KeyError, TypeError, ValueError):
        raise ValueError(
            "Unable to extract HR interview score from Day 37 result."
        )


def extract_aptitude_score(logical_data, scenario_data):
    """
    Calculate the combined aptitude score using:

    Logical Reasoning Score
    +
    Scenario Evaluation Score

    divided by 2.
    """

    try:
        logical_score = float(
            logical_data["logical_reasoning_score"]
        )

        scenario_score = float(
            scenario_data["scenario_evaluation_score"]
        )

    except (KeyError, TypeError, ValueError):
        raise ValueError(
            "Unable to extract aptitude scores from Day 38 results."
        )

    aptitude_score = (
        logical_score + scenario_score
    ) / 2

    return round(aptitude_score, 2)
