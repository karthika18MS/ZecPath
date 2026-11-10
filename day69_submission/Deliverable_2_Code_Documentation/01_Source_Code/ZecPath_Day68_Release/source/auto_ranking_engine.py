import json
import os


# ==========================================================
# Candidate Folder
# ==========================================================

CANDIDATE_FOLDER = "candidates"


# ==========================================================
# Output File
# ==========================================================

OUTPUT_FILE = "ranked_candidates.json"


# ==========================================================
# Load Candidate Scores
# ==========================================================

def load_candidate_scores():

    candidates = []

    # Check whether candidate folder exists

    if not os.path.exists(CANDIDATE_FOLDER):

        print(
            "Error: candidates folder not found."
        )

        return candidates

    # Read all files in candidates folder

    for filename in os.listdir(
        CANDIDATE_FOLDER
    ):

        # Only process JSON files

        if not filename.endswith(".json"):

            continue

        file_path = os.path.join(
            CANDIDATE_FOLDER,
            filename
        )

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                candidate = json.load(file)

            # Check candidate ID

            if "candidate_id" not in candidate:

                print(
                    f"Warning: candidate_id missing "
                    f"in {filename}"
                )

                continue

            # Check ATS score

            if "final_ats_score" not in candidate:

                print(
                    f"Warning: final_ats_score missing "
                    f"in {filename}"
                )

                continue

            candidates.append(candidate)

        except json.JSONDecodeError:

            print(
                f"Warning: Invalid JSON in "
                f"{filename}"
            )

    return candidates


# ==========================================================
# Sort Candidates by ATS Score
# ==========================================================

def sort_candidates(candidates):

    sorted_candidates = sorted(

        candidates,

        key=lambda candidate:
            candidate.get(
                "final_ats_score",
                0
            ),

        reverse=True

    )

    return sorted_candidates


# ==========================================================
# Assign Ranks
# ==========================================================

def assign_ranks(candidates):

    ranked_candidates = []

    for index, candidate in enumerate(
        candidates,
        start=1
    ):

        ranked_candidate = {

            "rank":
                index,

            "candidate_id":
                candidate.get(
                    "candidate_id"
                ),

            "target_role":
                candidate.get(
                    "target_role",
                    "Unknown"
                ),

            "ats_score":
                candidate.get(
                    "final_ats_score",
                    0
                ),

            "matching_status":
                candidate.get(
                    "matching_status",
                    "Unknown"
                ),

            "recommendation":
                candidate.get(
                    "recommendation",
                    "Not Available"
                )

        }

        ranked_candidates.append(
            ranked_candidate
        )

    return ranked_candidates


# ==========================================================
# Display Ranked Candidates
# ==========================================================

def display_ranked_candidates(
    ranked_candidates
):

    print("\n===================================")
    print("ZecPath AUTO-RANKING ENGINE")
    print("===================================\n")

    if not ranked_candidates:

        print(
            "No valid candidates found."
        )

        return

    print(
        f"{'Rank':<8}"
        f"{'Candidate':<15}"
        f"{'ATS Score':<12}"
        f"Status"
    )

    print("-----------------------------------")

    for candidate in ranked_candidates:

        print(
            f"{candidate['rank']:<8}"
            f"{candidate['candidate_id']:<15}"
            f"{candidate['ats_score']:<12.2f}"
            f"{candidate['matching_status']}"
        )


# ==========================================================
# Save Ranked Candidates
# ==========================================================

def save_ranked_candidates(
    ranked_candidates
):

    output = {

        "total_candidates":
            len(ranked_candidates),

        "ranked_candidates":
            ranked_candidates

    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        "\nRanked candidates saved to "
        "ranked_candidates.json"
    )


# ==========================================================
# Main Program
# ==========================================================

if __name__ == "__main__":

    print("\n===================================")
    print("ZecPath CANDIDATE RANKING")
    print("===================================\n")

    # ------------------------------------------------------
    # Step 1: Load candidates
    # ------------------------------------------------------

    candidates = load_candidate_scores()

    if not candidates:

        print(
            "No candidate score files found."
        )

        exit()

    # ------------------------------------------------------
    # Step 2: Sort candidates
    # ------------------------------------------------------

    sorted_candidates = sort_candidates(
        candidates
    )

    # ------------------------------------------------------
    # Step 3: Assign ranks
    # ------------------------------------------------------

    ranked_candidates = assign_ranks(
        sorted_candidates
    )

    # ------------------------------------------------------
    # Step 4: Display ranking
    # ------------------------------------------------------

    display_ranked_candidates(
        ranked_candidates
    )

    # ------------------------------------------------------
    # Step 5: Save ranking
    # ------------------------------------------------------

    save_ranked_candidates(
        ranked_candidates
    )