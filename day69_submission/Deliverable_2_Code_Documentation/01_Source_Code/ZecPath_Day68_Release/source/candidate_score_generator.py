import json


# ==========================================================
# Input and Output Files
# ==========================================================

INPUT_FILE = "ats_score.json"

OUTPUT_FILE = "candidate_score.json"


# ==========================================================
# Read ATS Score
# ==========================================================

def load_ats_score(): #Read the ATS result from ats_score.json and return it as a Python dictionary.

    try:

        with open(
            INPUT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except FileNotFoundError:

        print(
            "Error: ats_score.json not found."
        )

        return None

    except json.JSONDecodeError:

        print(
            "Error: Invalid JSON format."
        )

        return None


# ==========================================================
# Generate Strengths
# ==========================================================

def generate_strengths(components): #This function generates positive observations about the candidate.

    strengths = []

    for component, data in components.items():

        score = data.get("score") #Gets the candidate's score for that component.

        if score is None: #If there is no score, the program skips that component.
            continue

        if score >= 80:

            if component == "skill_match":

                strengths.append(
                    "Strong match with required skills."
                )

            elif component == "experience_relevance":

                strengths.append(
                    "Highly relevant professional experience."
                )

            elif component == "education_alignment":

                strengths.append(
                    "Education aligns well with the job requirements."
                )

            elif component == "semantic_similarity":

                strengths.append(
                    "Resume has strong semantic similarity with the job description."
                )

    return strengths


# ==========================================================
# Generate Areas to Review
# ==========================================================

def generate_areas_to_review(components): #This function identifies areas where the candidate may need review.

    areas = []

    for component, data in components.items():

        score = data.get("score")

        status = data.get("status")

        # --------------------------------------------------
        # Missing information
        # --------------------------------------------------

        if status == "Missing":

            if component == "skill_match":

                areas.append(
                    "Skill information is missing."
                )

            elif component == "experience_relevance":

                areas.append(
                    "Relevant experience information is missing."
                )

            elif component == "education_alignment":

                areas.append(
                    "Education information is missing."
                )

            elif component == "semantic_similarity":

                areas.append(
                    "Semantic similarity could not be calculated."
                )

        # --------------------------------------------------
        # Low score
        # --------------------------------------------------

        elif score is not None and score < 60:

            if component == "skill_match":

                areas.append(
                    "Skill match is relatively low."
                )

            elif component == "experience_relevance":

                areas.append(
                    "Experience relevance is relatively low."
                )

            elif component == "education_alignment":

                areas.append(
                    "Education alignment is relatively low."
                )

            elif component == "semantic_similarity":

                areas.append(
                    "Semantic similarity is relatively low."
                )

    return areas


# ==========================================================
# Generate Candidate Score
# ==========================================================

def generate_candidate_score(ats_data):

    components = ats_data.get(
        "components",
        {}
    )

    # ------------------------------------------------------
    # Generate strengths
    # ------------------------------------------------------

    strengths = generate_strengths(
        components
    )

    # ------------------------------------------------------
    # Generate areas to review
    # ------------------------------------------------------

    areas_to_review = generate_areas_to_review(
        components
    )

    # ------------------------------------------------------
    # Create final candidate score
    # ------------------------------------------------------

    candidate_score = {

        "candidate_id":
            ats_data.get(
                "candidate_id"
            ),

        "target_role":
            ats_data.get(
                "target_role"
            ),

        "final_ats_score":
            ats_data.get(
                "final_ats_score"
            ),

        "matching_status":
            ats_data.get(
                "matching_status"
            ),

        "recommendation":
            ats_data.get(
                "recommendation"
            ),

        "score_breakdown":
            components,

        "strengths":
            strengths,

        "areas_to_review":
            areas_to_review

    }

    return candidate_score


# ==========================================================
# Display Candidate Score
# ==========================================================

def display_candidate_score(candidate_score):

    print("\n===================================")
    print("CANDIDATE SCORE")
    print("===================================\n")

    print(
        "Candidate ID :",
        candidate_score["candidate_id"]
    )

    print(
        "Target Role  :",
        candidate_score["target_role"]
    )

    print(
        "ATS Score    :",
        candidate_score["final_ats_score"]
    )

    print(
        "Status       :",
        candidate_score["matching_status"]
    )

    print(
        "Recommendation:",
        candidate_score["recommendation"]
    )

    print("\n-----------------------------------")
    print("STRENGTHS")
    print("-----------------------------------")

    if candidate_score["strengths"]:

        for strength in candidate_score["strengths"]:

            print(
                "•",
                strength
            )

    else:

        print(
            "No major strengths identified."
        )

    print("\n-----------------------------------")
    print("AREAS TO REVIEW")
    print("-----------------------------------")

    if candidate_score["areas_to_review"]:

        for area in candidate_score["areas_to_review"]:

            print(
                "•",
                area
            )

    else:

        print(
            "No major areas to review."
        )


# ==========================================================
# Save Candidate Score
# ==========================================================

def save_candidate_score(candidate_score):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            candidate_score,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        "\nCandidate score saved to "
        "candidate_score.json"
    )


# ==========================================================
# Main Program
# ==========================================================

if __name__ == "__main__":

    print("\n===================================")
    print("ZecPath CANDIDATE SCORE GENERATOR")
    print("===================================\n")

    # ------------------------------------------------------
    # Load ATS score
    # ------------------------------------------------------

    ats_data = load_ats_score()

    if ats_data is None:

        exit()

    # ------------------------------------------------------
    # Generate candidate score
    # ------------------------------------------------------

    candidate_score = generate_candidate_score(
        ats_data
    )

    # ------------------------------------------------------
    # Display result
    # ------------------------------------------------------

    display_candidate_score(
        candidate_score
    )

    # ------------------------------------------------------
    # Save result
    # ------------------------------------------------------

    save_candidate_score(
        candidate_score
    )