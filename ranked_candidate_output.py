import json


# ==========================================================
# Input Files
# ==========================================================

RANKING_FILE = "ranked_candidates.json"

SHORTLIST_FILE = "shortlisted_candidates.json"


# ==========================================================
# Output File
# ==========================================================

OUTPUT_FILE = "ranked_candidate_output.json"


# ==========================================================
# Load JSON File
# ==========================================================

def load_json_file(file_path):

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except FileNotFoundError:

        print(
            f"Error: {file_path} not found."
        )

        return None

    except json.JSONDecodeError:

        print(
            f"Error: Invalid JSON format "
            f"in {file_path}."
        )

        return None


# ==========================================================
# Create Final Ranked Output
# ==========================================================

def generate_ranked_output(
    ranking_data,
    shortlist_data
):

    ranked_candidates = ranking_data.get(
        "ranked_candidates",
        []
    )

    shortlisted = shortlist_data.get(
        "shortlisted_candidates",
        []
    )

    review = shortlist_data.get(
        "review_candidates",
        []
    )

    rejected = shortlist_data.get(
        "rejected_candidates",
        []
    )


    # ------------------------------------------------------
    # Create status lookup
    # ------------------------------------------------------

    status_lookup = {}


    for candidate in shortlisted:

        status_lookup[
            candidate["candidate_id"]
        ] = "Shortlisted"


    for candidate in review:

        status_lookup[
            candidate["candidate_id"]
        ] = "Review"


    for candidate in rejected:

        status_lookup[
            candidate["candidate_id"]
        ] = "Rejected"


    # ------------------------------------------------------
    # Generate final candidate list
    # ------------------------------------------------------

    final_candidates = []


    for candidate in ranked_candidates:

        candidate_id = candidate.get(
            "candidate_id"
        )

        final_candidate = {

            "rank":
                candidate.get(
                    "rank"
                ),

            "candidate_id":
                candidate_id,

            "target_role":
                candidate.get(
                    "target_role",
                    "Unknown"
                ),

            "ats_score":
                candidate.get(
                    "ats_score",
                    0
                ),

            "matching_status":
                candidate.get(
                    "matching_status",
                    "Unknown"
                ),

            "shortlisting_status":
                status_lookup.get(
                    candidate_id,
                    "Not Processed"
                ),

            "recommendation":
                candidate.get(
                    "recommendation",
                    "Not Available"
                )

        }

        final_candidates.append(
            final_candidate
        )


    return final_candidates


# ==========================================================
# Generate Top Candidates
# ==========================================================

def generate_top_candidates(
    candidates,
    number_of_candidates=3
):

    top_candidates = candidates[
        :number_of_candidates
    ]

    return top_candidates


# ==========================================================
# Display Ranked Candidate Output
# ==========================================================

def display_output(
    candidates,
    top_candidates
):

    print("\n============================================================")
    print("          ZecPath RANKED CANDIDATE OUTPUT")
    print("============================================================\n")


    # ------------------------------------------------------
    # Complete Ranking
    # ------------------------------------------------------

    print("ALL RANKED CANDIDATES")

    print("------------------------------------------------------------")

    print(
        f"{'Rank':<8}"
        f"{'Candidate':<15}"
        f"{'ATS Score':<12}"
        f"{'Status':<15}"
        f"Decision"
    )

    print("------------------------------------------------------------")


    for candidate in candidates:

        print(
            f"{candidate['rank']:<8}"
            f"{candidate['candidate_id']:<15}"
            f"{candidate['ats_score']:<12.2f}"
            f"{candidate['shortlisting_status']:<15}"
            f"{candidate['recommendation']}"
        )


    # ------------------------------------------------------
    # Top Candidates
    # ------------------------------------------------------

    print("\n============================================================")

    print("TOP CANDIDATES")

    print("============================================================")


    for candidate in top_candidates:

        print(
            f"\nRank {candidate['rank']}"
        )

        print(
            f"Candidate ID : "
            f"{candidate['candidate_id']}"
        )

        print(
            f"ATS Score    : "
            f"{candidate['ats_score']:.2f}%"
        )

        print(
            f"Status       : "
            f"{candidate['shortlisting_status']}"
        )

        print(
            f"Recommendation: "
            f"{candidate['recommendation']}"
        )


# ==========================================================
# Save Final Output
# ==========================================================

def save_output(
    candidates,
    top_candidates
):

    output = {

        "total_candidates":
            len(candidates),

        "top_candidate_count":
            len(top_candidates),

        "ranked_candidates":
            candidates,

        "top_candidates":
            top_candidates

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
        "\nRanked candidate output saved to "
        "ranked_candidate_output.json"
    )


# ==========================================================
# Main Program
# ==========================================================

if __name__ == "__main__":

    print("\n============================================================")
    print("ZecPath CANDIDATE OUTPUT GENERATOR")
    print("============================================================\n")


    # ------------------------------------------------------
    # Step 1: Load ranking file
    # ------------------------------------------------------

    ranking_data = load_json_file(
        RANKING_FILE
    )


    if ranking_data is None:

        exit()


    # ------------------------------------------------------
    # Step 2: Load shortlisting file
    # ------------------------------------------------------

    shortlist_data = load_json_file(
        SHORTLIST_FILE
    )


    if shortlist_data is None:

        exit()


    # ------------------------------------------------------
    # Step 3: Generate final ranking
    # ------------------------------------------------------

    final_candidates = generate_ranked_output(
        ranking_data,
        shortlist_data
    )


    # ------------------------------------------------------
    # Step 4: Generate top candidates
    # ------------------------------------------------------

    top_candidates = generate_top_candidates(
        final_candidates,
        3
    )


    # ------------------------------------------------------
    # Step 5: Display output
    # ------------------------------------------------------

    display_output(
        final_candidates,
        top_candidates
    )


    # ------------------------------------------------------
    # Step 6: Save output
    # ------------------------------------------------------

    save_output(
        final_candidates,
        top_candidates
    )