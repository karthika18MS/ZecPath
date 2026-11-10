import json


# ==========================================================
# Input File
# ==========================================================

INPUT_FILE = "ranked_candidates.json"


# ==========================================================
# Output File
# ==========================================================

OUTPUT_FILE = "shortlisted_candidates.json"


# ==========================================================
# Shortlisting Thresholds
# ==========================================================

SHORTLIST_THRESHOLD = 80

REVIEW_THRESHOLD = 60


# ==========================================================
# Load Ranked Candidates
# ==========================================================

def load_ranked_candidates():

    try:

        with open(
            INPUT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return data.get(
            "ranked_candidates",
            []
        )

    except FileNotFoundError:

        print(
            "Error: ranked_candidates.json not found."
        )

        return []

    except json.JSONDecodeError:

        print(
            "Error: Invalid JSON format."
        )

        return []


# ==========================================================
# Decide Candidate Status
# ==========================================================

def decide_candidate_status(score):

    if score >= SHORTLIST_THRESHOLD:

        return "Shortlisted"

    elif score >= REVIEW_THRESHOLD:

        return "Review"

    else:

        return "Rejected"


# ==========================================================
# Generate Shortlisting Result
# ==========================================================

def generate_shortlisting(
    candidates
):

    shortlisted = []

    review = []

    rejected = []

    for candidate in candidates:

        score = candidate.get(
            "ats_score",
            0
        )

        status = decide_candidate_status(
            score
        )

        result = {

            "rank":
                candidate.get(
                    "rank"
                ),

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
                score,

            "matching_status":
                candidate.get(
                    "matching_status",
                    "Unknown"
                ),

            "shortlisting_status":
                status,

            "recommendation":
                candidate.get(
                    "recommendation",
                    "Not Available"
                )

        }

        if status == "Shortlisted":

            shortlisted.append(
                result
            )

        elif status == "Review":

            review.append(
                result
            )

        else:

            rejected.append(
                result
            )

    return (
        shortlisted,
        review,
        rejected
    )


# ==========================================================
# Display Shortlisting Results
# ==========================================================

def display_results(
    shortlisted,
    review,
    rejected
):

    print("\n===================================")
    print("ZecPath SHORTLISTING AUTOMATION")
    print("===================================\n")


    # ------------------------------------------------------
    # Shortlisted Candidates
    # ------------------------------------------------------

    print("SHORTLISTED CANDIDATES")
    print("-----------------------------------")

    if shortlisted:

        for candidate in shortlisted:

            print(
                f"{candidate['candidate_id']} "
                f"- {candidate['ats_score']:.2f}% "
                f"- {candidate['shortlisting_status']}"
            )

    else:

        print(
            "No candidates shortlisted."
        )


    # ------------------------------------------------------
    # Review Candidates
    # ------------------------------------------------------

    print("\nCANDIDATES FOR REVIEW")
    print("-----------------------------------")

    if review:

        for candidate in review:

            print(
                f"{candidate['candidate_id']} "
                f"- {candidate['ats_score']:.2f}% "
                f"- {candidate['shortlisting_status']}"
            )

    else:

        print(
            "No candidates require review."
        )


    # ------------------------------------------------------
    # Rejected Candidates
    # ------------------------------------------------------

    print("\nREJECTED CANDIDATES")
    print("-----------------------------------")

    if rejected:

        for candidate in rejected:

            print(
                f"{candidate['candidate_id']} "
                f"- {candidate['ats_score']:.2f}% "
                f"- {candidate['shortlisting_status']}"
            )

    else:

        print(
            "No candidates rejected."
        )


# ==========================================================
# Save Shortlisting Results
# ==========================================================

def save_results(
    shortlisted,
    review,
    rejected
):

    output = {

        "thresholds": {

            "shortlist_threshold":
                SHORTLIST_THRESHOLD,

            "review_threshold":
                REVIEW_THRESHOLD

        },

        "summary": {

            "total_candidates":
                len(shortlisted)
                + len(review)
                + len(rejected),

            "shortlisted":
                len(shortlisted),

            "review":
                len(review),

            "rejected":
                len(rejected)

        },

        "shortlisted_candidates":
            shortlisted,

        "review_candidates":
            review,

        "rejected_candidates":
            rejected

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
        "\nShortlisting results saved to "
        "shortlisted_candidates.json"
    )


# ==========================================================
# Main Program
# ==========================================================

if __name__ == "__main__":

    print("\n===================================")
    print("ZecPath CANDIDATE SHORTLISTING")
    print("===================================\n")


    # ------------------------------------------------------
    # Step 1: Load ranked candidates
    # ------------------------------------------------------

    candidates = load_ranked_candidates()


    # ------------------------------------------------------
    # Check candidates
    # ------------------------------------------------------

    if not candidates:

        print(
            "No ranked candidates found."
        )

        exit()


    # ------------------------------------------------------
    # Step 2: Generate shortlisting
    # ------------------------------------------------------

    (
        shortlisted,
        review,
        rejected
    ) = generate_shortlisting(
        candidates
    )


    # ------------------------------------------------------
    # Step 3: Display results
    # ------------------------------------------------------

    display_results(
        shortlisted,
        review,
        rejected
    )


    # ------------------------------------------------------
    # Step 4: Save results
    # ------------------------------------------------------

    save_results(
        shortlisted,
        review,
        rejected
    )