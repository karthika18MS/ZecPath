import json
import os

from .hiring_fit_calculator import HiringFitCalculator


# --------------------------------------------------
# Paths
# --------------------------------------------------

DAY41_DIRECTORY = os.path.dirname(
    os.path.abspath(__file__)
)

BASE_DIRECTORY = os.path.dirname(
    DAY41_DIRECTORY
)

CONFIG_FILE = os.path.join(
    DAY41_DIRECTORY,
    "config.json"
)

CROSS_ROUND_FILE = os.path.join(
    DAY41_DIRECTORY,
    "results",
    "cross_round_summary.json"
)


# --------------------------------------------------
# JSON helpers
# --------------------------------------------------

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
            indent=4,
            ensure_ascii=False
        )


# --------------------------------------------------
# Load Day 32 screening score
# --------------------------------------------------

def load_screening_result(file_path):

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            "Day 32 screening result not found:\n"
            + file_path
        )

    data = load_json(file_path)

    candidate_id = data.get(
        "candidate_id"
    )

    job_id = data.get(
        "job_id"
    )

    screening_summary = data.get(
        "screening_summary",
        {}
    )

    final_screening_score = (
        screening_summary.get(
            "final_screening_score"
        )
    )

    if candidate_id is None:
        raise ValueError(
            "candidate_id not found in "
            "Day 32 screening result."
        )

    if final_screening_score is None:
        raise ValueError(
            "final_screening_score not found "
            "in Day 32 screening result."
        )

    return {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "final_screening_score": float(
            final_screening_score
        )
    }


# --------------------------------------------------
# Load ATS result
# --------------------------------------------------

def load_ats_result(candidate_id):

    file_path = os.path.join(
        BASE_DIRECTORY,
        "day18_optimization",
        "results",
        candidate_id,
        "day18_optimized_ats_score.json"
    )

    if not os.path.exists(file_path):
        return None

    data = load_json(file_path)

    scores = data.get(
        "scores",
        {}
    )

    return {
        "ats_score": scores.get(
            "final_ats_score"
        ),

        "target_role": data.get(
            "target_role"
        ),

        "job_description": data.get(
            "job_description"
        )
    }


# --------------------------------------------------
# Load HR result
# --------------------------------------------------

def load_hr_result(candidate_id):

    file_path = os.path.join(
        BASE_DIRECTORY,
        "day37_hr_interview_scoring",
        "results",
        "candidate_hr_score_report.json"
    )

    if not os.path.exists(file_path):
        return None

    data = load_json(file_path)

    candidate_information = data.get(
        "candidate_information",
        {}
    )

    stored_candidate_id = (
        candidate_information.get(
            "candidate_id"
        )
    )

    if stored_candidate_id != candidate_id:
        return None

    final_evaluation = data.get(
        "final_evaluation",
        {}
    )

    hr_score = final_evaluation.get(
        "final_hr_interview_score"
    )

    if hr_score is None:
        return None

    return float(hr_score)


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("=" * 75)
    print(
        "       ZecPath DAY 41 - HIRING FIT CALCULATOR"
    )
    print("=" * 75)

    # --------------------------------------------------
    # Load configuration
    # --------------------------------------------------

    config = load_json(
        CONFIG_FILE
    )

    hiring_fit_config = config.get(
        "hiring_fit",
        {}
    )

    roles = hiring_fit_config.get(
        "roles",
        {}
    )

    default_role = hiring_fit_config.get(
        "default_role"
    )

    if default_role not in roles:

        raise ValueError(
            f"Role configuration not found: "
            f"{default_role}"
        )

    role_weights = roles[
        default_role
    ]

    print()
    print(
        f"Default role: {default_role}"
    )

    print()
    print("Hiring-fit weights:")
    print(
        f"ATS        : "
        f"{role_weights['ats'] * 100:.0f}%"
    )
    print(
        f"Screening  : "
        f"{role_weights['screening'] * 100:.0f}%"
    )
    print(
        f"HR         : "
        f"{role_weights['hr'] * 100:.0f}%"
    )

    # --------------------------------------------------
    # Load cross-round candidates
    # --------------------------------------------------

    if not os.path.exists(
        CROSS_ROUND_FILE
    ):

        print()
        print(
            "ERROR: Cross-round summary not found."
        )

        print()
        print(
            "Run Deliverable 1 first:"
        )

        print(
            "python -m "
            "day41_cross_round_scoring.run_cross_round"
        )

        return

    cross_round_data = load_json(
        CROSS_ROUND_FILE
    )

    # --------------------------------------------------
    # Load actual Day 32 Screening
    # --------------------------------------------------

    screening_relative_path = (
        hiring_fit_config
        .get("screening", {})
        .get("file")
    )

    if screening_relative_path is None:

        raise ValueError(
            "Screening file path not configured."
        )

    screening_file = os.path.join(
        BASE_DIRECTORY,
        screening_relative_path
    )

    screening_result = load_screening_result(
        screening_file
    )

    screening_candidate_id = (
        screening_result["candidate_id"]
    )

    screening_score = (
        screening_result["final_screening_score"]
    )

    screening_job_id = (
        screening_result["job_id"]
    )

    print()
    print("Real Day 32 screening result loaded:")
    print(
        f"Candidate   : {screening_candidate_id}"
    )
    print(
        f"Screening   : {screening_score:.2f}"
    )
    print(
        f"Job         : {screening_job_id}"
    )

    # --------------------------------------------------
    # Calculator
    # --------------------------------------------------

    calculator = HiringFitCalculator(
        role_weights
    )

    results = []

    print()
    print("-" * 75)

    # --------------------------------------------------
    # Process candidates
    # --------------------------------------------------

    for candidate_data in cross_round_data:

        candidate_id = candidate_data.get(
            "candidate_id"
        )

        print()
        print(
            f"Processing: {candidate_id}"
        )

        # ----------------------------------------------
        # ATS
        # ----------------------------------------------

        ats_result = load_ats_result(
            candidate_id
        )

        ats_score = None
        target_role = None
        job_id = None

        if ats_result:

            ats_score = ats_result.get(
                "ats_score"
            )

            target_role = ats_result.get(
                "target_role"
            )

        # ----------------------------------------------
        # Screening
        # ----------------------------------------------

        if candidate_id == screening_candidate_id:

            candidate_screening_score = (
                screening_score
            )

            if job_id is None:
                job_id = screening_job_id

        else:

            candidate_screening_score = None

        # ----------------------------------------------
        # HR
        # ----------------------------------------------

        hr_score = load_hr_result(
            candidate_id
        )

        # ----------------------------------------------
        # Missing data
        # ----------------------------------------------

        missing = []

        if ats_score is None:
            missing.append("ATS")

        if candidate_screening_score is None:
            missing.append("Screening")

        if hr_score is None:
            missing.append("HR")

        if missing:

            print(
                "Status : Incomplete"
            )

            print(
                "Missing:",
                ", ".join(missing)
            )

            result = {
                "candidate_id": candidate_id,
                "target_role": target_role,
                "status": "Incomplete",
                "missing_rounds": missing,

                "round_scores": {
                    "ats": (
                        float(ats_score)
                        if ats_score is not None
                        else None
                    ),

                    "screening": (
                        float(candidate_screening_score)
                        if candidate_screening_score
                        is not None
                        else None
                    ),

                    "hr": (
                        float(hr_score)
                        if hr_score is not None
                        else None
                    )
                }
            }

            results.append(result)

            continue

        # ----------------------------------------------
        # Calculate
        # ----------------------------------------------

        result = calculator.generate_result(

            candidate_id=candidate_id,

            job_id=job_id,

            target_role=target_role
            or default_role,

            ats_score=float(ats_score),

            screening_score=float(
                candidate_screening_score
            ),

            hr_score=float(hr_score)
        )

        results.append(result)

        # ----------------------------------------------
        # Display
        # ----------------------------------------------

        print(
            f"ATS        : {ats_score:.2f}"
        )

        print(
            f"Screening  : "
            f"{candidate_screening_score:.2f}"
        )

        print(
            f"HR         : {hr_score:.2f}"
        )

        print(
            f"Hiring Fit : "
            f"{result['hiring_fit_percentage']:.2f}%"
        )

        print(
            "Status     : Calculated"
        )

        # ----------------------------------------------
        # Save individual result
        # ----------------------------------------------

        candidate_directory = os.path.join(
            DAY41_DIRECTORY,
            "results",
            candidate_id
        )

        candidate_file = os.path.join(
            candidate_directory,
            "hiring_fit_score.json"
        )

        save_json(
            candidate_file,
            result
        )

    # --------------------------------------------------
    # Save summary
    # --------------------------------------------------

    summary_file = os.path.join(
        DAY41_DIRECTORY,
        "results",
        "hiring_fit_summary.json"
    )

    save_json(
        summary_file,
        results
    )

    calculated_count = sum(
        1
        for result in results
        if result.get("status")
        == "Calculated"
    )

    incomplete_count = (
        len(results)
        - calculated_count
    )

    print()
    print("=" * 75)
    print(
        "Hiring Fit calculation completed."
    )

    print()
    print(
        f"Calculated candidates : "
        f"{calculated_count}"
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