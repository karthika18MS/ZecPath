import json
import os

from .unified_candidate_score import UnifiedCandidateScore


BASE_DIR = os.getcwd()

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "day41_cross_round_scoring",
    "results"
)

HIRING_FIT_SUMMARY = os.path.join(
    RESULTS_DIR,
    "hiring_fit_summary.json"
)


def load_json(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_json(file_path, data):

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
    print("       ZecPath DAY 41 - UNIFIED CANDIDATE SCORE")
    print("=" * 75)

    if not os.path.exists(HIRING_FIT_SUMMARY):

        print()
        print("ERROR: Hiring Fit summary not found.")
        print()
        print(
            "Run Deliverable 2 first:"
        )
        print(
            "python -m day41_cross_round_scoring.run_hiring_fit"
        )

        return

    hiring_fit_data = load_json(
        HIRING_FIT_SUMMARY
    )

    calculator = UnifiedCandidateScore()

    unified_results = []

    complete_count = 0
    incomplete_count = 0

    print()
    print("Loading Hiring Fit results...")
    print()

    for candidate in hiring_fit_data:

        candidate_id = candidate.get(
            "candidate_id"
        )

        target_role = candidate.get(
            "target_role"
        )

        status = candidate.get(
            "status"
        )

        print("-" * 75)

        print(
            f"Processing: {candidate_id}"
        )

        if status != "Calculated":

            incomplete_count += 1

            incomplete_result = {

                "candidate_id": candidate_id,

                "target_role": target_role,

                "status": "Incomplete",

                "missing_rounds": candidate.get(
                    "missing_rounds",
                    []
                ),

                "round_scores": candidate.get(
                    "round_scores",
                    {}
                )
            }

            unified_results.append(
                incomplete_result
            )

            print(
                "Status : Incomplete"
            )

            print(
                "Missing:",
                ", ".join(
                    candidate.get(
                        "missing_rounds",
                        []
                    )
                )
            )

            continue

        round_scores = candidate.get(
            "round_scores",
            {}
        )

        weights = candidate.get(
            "weights",
            {}
        )

        weighted_contributions = candidate.get(
            "weighted_contributions",
            {}
        )

        hiring_fit = candidate.get(
            "hiring_fit_percentage"
        )

        job_id = candidate.get(
            "job_id",
            "JOB_BACKEND_001"
        )

        unified_object = (
            calculator.create_unified_object(

                candidate_id=candidate_id,

                job_id=job_id,

                target_role=target_role,

                ats_score=round_scores["ats"],

                screening_score=round_scores[
                    "screening"
                ],

                hr_score=round_scores["hr"],

                hiring_fit_percentage=hiring_fit,

                weights=weights,

                weighted_contributions=
                    weighted_contributions
            )
        )

        complete_count += 1

        unified_results.append(
            unified_object
        )

        candidate_directory = os.path.join(
            RESULTS_DIR,
            candidate_id
        )

        output_file = os.path.join(
            candidate_directory,
            "unified_candidate_score.json"
        )

        save_json(
            output_file,
            unified_object
        )

        print(
            f"ATS              : "
            f"{round_scores['ats']:.2f}"
        )

        print(
            f"Screening        : "
            f"{round_scores['screening']:.2f}"
        )

        print(
            f"HR               : "
            f"{round_scores['hr']:.2f}"
        )

        print(
            f"Hiring Fit       : "
            f"{hiring_fit:.2f}%"
        )

        print(
            "Status             : Complete"
        )

    summary_file = os.path.join(
        RESULTS_DIR,
        "unified_candidate_score_summary.json"
    )

    save_json(
        summary_file,
        unified_results
    )

    print()
    print("=" * 75)

    print(
        "Unified candidate score generation completed."
    )

    print()

    print(
        f"Complete candidates   : "
        f"{complete_count}"
    )

    print(
        f"Incomplete candidates : "
        f"{incomplete_count}"
    )

    print()

    print(
        "Summary saved to:"
    )

    print(
        summary_file
    )

    print("=" * 75)


if __name__ == "__main__":
    main()