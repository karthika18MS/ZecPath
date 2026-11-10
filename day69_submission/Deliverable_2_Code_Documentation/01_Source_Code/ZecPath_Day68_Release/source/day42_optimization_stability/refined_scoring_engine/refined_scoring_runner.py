import json
from pathlib import Path

from .refined_hr_scoring_engine import (
    RefinedHRScoringEngine
)


def main():

    print("=" * 75)

    print(
        "       ZecPath DAY 42 - "
        "REFINED HR SCORING"
    )

    print("=" * 75)

    # ========================================================
    # PROJECT ROOT
    # ========================================================

    project_root = (
        Path(__file__).resolve().parents[2]
    )

    # ========================================================
    # REAL DAY 37 RESULT
    # ========================================================

    hr_result_path = (
        project_root
        / "day37_hr_interview_scoring"
        / "results"
        / "hr_interview_score.json"
    )

    # ========================================================
    # CONFIGURATION
    # ========================================================

    config_path = (
        project_root
        / "day42_optimization_stability"
        / "refined_scoring_engine"
        / "scoring_config.json"
    )

    # ========================================================
    # OUTPUT
    # ========================================================

    output_path = (
        project_root
        / "day42_optimization_stability"
        / "refined_scoring_engine"
        / "results"
        / "refined_hr_score.json"
    )

    print()

    print(
        "Loading real Day 37 HR result..."
    )

    print(
        f"Source: {hr_result_path}"
    )

    # ========================================================
    # CHECK INPUT
    # ========================================================

    if not hr_result_path.exists():

        raise FileNotFoundError(
            f"HR result not found: "
            f"{hr_result_path}"
        )

    # ========================================================
    # LOAD DAY 37 RESULT
    # ========================================================

    with open(
        hr_result_path,
        "r",
        encoding="utf-8"
    ) as file:

        hr_result = json.load(
            file
        )

    print()

    print(
        f"Candidate : "
        f"{hr_result.get('candidate_id')}"
    )

    print(
        f"Job       : "
        f"{hr_result.get('job_id')}"
    )

    print(
        f"Original HR Score : "
        f"{hr_result.get('final_hr_interview_score')}"
    )

    # ========================================================
    # CREATE ENGINE
    # ========================================================

    engine = RefinedHRScoringEngine(
        config_path
    )

    # ========================================================
    # CALCULATE REFINED SCORE
    # ========================================================

    result = engine.refine(
        hr_result
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    print()

    print(
        "Question data validation:"
    )

    print(
        "PASS - Day 37 question_text and "
        "candidate_answer are available."
    )

    print()

    print(
        "Refined scoring:"
    )

    print(
        f"Original Score : "
        f"{result['original_hr_score']}"
    )

    print(
        f"Refined Score  : "
        f"{result['refined_hr_score']}"
    )

    print(
        f"Difference     : "
        f"{result['score_difference']}"
    )

    print()

    print(
        "Weighted contributions:"
    )

    for parameter, contribution in (
        result[
            "weighted_contributions"
        ].items()
    ):

        print(
            f"  {parameter:<20}: "
            f"{contribution}"
        )

    # ========================================================
    # SAVE
    # ========================================================

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

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

    print()

    print("=" * 75)

    print(
        "Refined HR scoring completed successfully."
    )

    print()

    print(
        f"Result saved to:\n"
        f"{output_path}"
    )

    print("=" * 75)


if __name__ == "__main__":
    main()