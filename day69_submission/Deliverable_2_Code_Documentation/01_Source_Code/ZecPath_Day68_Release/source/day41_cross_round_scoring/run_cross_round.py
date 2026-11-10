import os
import json

from .result_loader import ResultLoader
from .score_extractor import (
    extract_ats_score,
    extract_hr_score,
    extract_aptitude_score
)
from .cross_round_engine import (
    CrossRoundScoringEngine
)


CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

BASE_DIR = os.path.dirname(
    CURRENT_DIR
)


def load_config():

    config_path = os.path.join(
        CURRENT_DIR,
        "config.json"
    )

    with open(
        config_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_json(
    file_path,
    data
):

    os.makedirs(
        os.path.dirname(file_path),
        exist_ok=True
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


def main():

    print("=" * 75)
    print(
        "       ZecPath DAY 41 - CROSS-ROUND SCORING SYSTEM"
    )
    print("=" * 75)

    config = load_config()

    weights = config["weights"]

    print()
    print("Round weights:")

    print(
        f"ATS        : {weights['ats'] * 100:.0f}%"
    )

    print(
        f"HR         : {weights['hr'] * 100:.0f}%"
    )

    print(
        f"Aptitude   : {weights['aptitude'] * 100:.0f}%"
    )

    loader = ResultLoader(
        BASE_DIR
    )

    # ------------------------------------------------
    # LOAD ATS
    # ------------------------------------------------

    ats_config = config["rounds"]["ats"]

    ats_results = loader.load_ats_results(
        ats_config["directory"],
        ats_config["filename"]
    )

    # ------------------------------------------------
    # LOAD HR
    # ------------------------------------------------

    hr_config = config["rounds"]["hr"]

    hr_results = loader.load_hr_results(
        hr_config["directory"],
        hr_config["filename"]
    )

    # ------------------------------------------------
    # LOAD APTITUDE
    # ------------------------------------------------

    aptitude_config = config["rounds"]["aptitude"]

    aptitude_results = loader.load_aptitude_results(
        aptitude_config["logical_reasoning_file"],
        aptitude_config["scenario_file"]
    )

    print()
    print("Loading real round results...")
    print()

    print(
        f"ATS candidates found       : {len(ats_results)}"
    )

    print(
        f"HR candidates found        : {len(hr_results)}"
    )

    print(
        f"Aptitude candidates found : {len(aptitude_results)}"
    )

    # ------------------------------------------------
    # FIND ALL CANDIDATES
    # ------------------------------------------------

    all_candidates = sorted(
        set(ats_results.keys())
        |
        set(hr_results.keys())
        |
        set(aptitude_results.keys())
    )

    print()
    print(
        f"Total unique candidates   : {len(all_candidates)}"
    )

    print()

    engine = CrossRoundScoringEngine(
        weights
    )

    output_directory = os.path.join(
        CURRENT_DIR,
        "results"
    )

    summary = []

    # ------------------------------------------------
    # PROCESS EACH CANDIDATE
    # ------------------------------------------------

    for candidate_id in all_candidates:

        print("-" * 75)

        print(
            f"Processing: {candidate_id}"
        )

        missing_rounds = []

        # ATS

        if candidate_id in ats_results:

            ats_score = extract_ats_score(
                ats_results[candidate_id]
            )

        else:

            ats_score = None
            missing_rounds.append("ATS")

        # HR

        if candidate_id in hr_results:

            hr_score = extract_hr_score(
                hr_results[candidate_id]
            )

        else:

            hr_score = None
            missing_rounds.append("HR")

        # Aptitude

        if candidate_id in aptitude_results:

            aptitude_data = aptitude_results[
                candidate_id
            ]

            aptitude_score = extract_aptitude_score(
                aptitude_data["logical"],
                aptitude_data["scenario"]
            )

        else:

            aptitude_score = None
            missing_rounds.append("Aptitude")

        # ------------------------------------------------
        # INCOMPLETE CANDIDATE
        # ------------------------------------------------

        if missing_rounds:

            result = {

                "candidate_id": candidate_id,

                "status": "Incomplete",

                "missing_rounds": missing_rounds,

                "round_scores": {

                    "ats": ats_score,

                    "hr": hr_score,

                    "aptitude": aptitude_score
                }

            }

            print(
                "Status : Incomplete"
            )

            print(
                "Missing:",
                ", ".join(missing_rounds)
            )

        # ------------------------------------------------
        # COMPLETE CANDIDATE
        # ------------------------------------------------

        else:

            final_score = engine.calculate(

                ats_score,

                hr_score,

                aptitude_score
            )

            result = {

                "candidate_id": candidate_id,

                "status": "Complete",

                "round_scores": {

                    "ats": ats_score,

                    "hr": hr_score,

                    "aptitude": aptitude_score
                },

                "weights": weights,

                "cross_round_score": final_score

            }

            print(
                f"ATS       : {ats_score:.2f}"
            )

            print(
                f"HR        : {hr_score:.2f}"
            )

            print(
                f"Aptitude  : {aptitude_score:.2f}"
            )

            print(
                f"Final Score: {final_score:.2f}"
            )

        # ------------------------------------------------
        # SAVE INDIVIDUAL RESULT
        # ------------------------------------------------

        candidate_directory = os.path.join(
            output_directory,
            candidate_id
        )

        candidate_output = os.path.join(
            candidate_directory,
            "cross_round_score.json"
        )

        save_json(
            candidate_output,
            result
        )

        summary.append(result)

    # ------------------------------------------------
    # SAVE SUMMARY
    # ------------------------------------------------

    summary_path = os.path.join(
        output_directory,
        "cross_round_summary.json"
    )

    save_json(
        summary_path,
        summary
    )

    # ------------------------------------------------
    # FINAL MESSAGE
    # ------------------------------------------------

    complete_count = sum(
        1
        for item in summary
        if item["status"] == "Complete"
    )

    incomplete_count = sum(
        1
        for item in summary
        if item["status"] == "Incomplete"
    )

    print()
    print("=" * 75)

    print(
        "Cross-round scoring completed."
    )

    print()

    print(
        f"Complete candidates   : {complete_count}"
    )

    print(
        f"Incomplete candidates : {incomplete_count}"
    )

    print()

    print(
        "Summary saved to:"
    )

    print(
        summary_path
    )

    print("=" * 75)


if __name__ == "__main__":
    main()