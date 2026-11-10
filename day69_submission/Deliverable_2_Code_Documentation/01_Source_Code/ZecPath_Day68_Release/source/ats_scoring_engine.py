import json


# ==========================================================
# TARGET JOB ROLE
# ==========================================================

target_role = "Python Developer"


# ==========================================================
# FILE PATHS
# ==========================================================

WEIGHTS_FILE = "scoring_weights.json"

SKILL_FILE = "skill_match.json"

SIMILARITY_FILE = "similarity_score.json"

EXPERIENCE_FILE = "structured_experience.json"

EDUCATION_FILE = "structured_academic_profile.json"

OUTPUT_FILE = "ats_score.json"


# ==========================================================
# LOAD JSON
# ==========================================================

def load_json(file_path):

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
            f"Error: Invalid JSON in {file_path}."
        )

        return None


# ==========================================================
# LOAD ROLE WEIGHTS
# ==========================================================

def load_role_weights(target_role):

    data = load_json(
        WEIGHTS_FILE
    )

    if data is None:

        return None

    if target_role not in data:

        print(
            f"No weights found for {target_role}."
        )

        return None

    return data[target_role]


# ==========================================================
# VALIDATE WEIGHTS
# ==========================================================

def validate_weights(weights):

    required_parameters = [

        "skill_match",

        "experience_relevance",

        "education_alignment",

        "semantic_similarity"

    ]


    # ------------------------------------------------------
    # Check parameters
    # ------------------------------------------------------

    for parameter in required_parameters:

        if parameter not in weights:

            print(
                f"Missing weight: {parameter}"
            )

            return False


    # ------------------------------------------------------
    # Check values
    # ------------------------------------------------------

    for parameter in required_parameters:

        value = weights[parameter]

        if not isinstance(
            value,
            (int, float)
        ):

            print(
                f"Invalid weight: {parameter}"
            )

            return False

        if value < 0 or value > 1:

            print(
                f"Weight must be between 0 and 1: "
                f"{parameter}"
            )

            return False


    # ------------------------------------------------------
    # Check total
    # ------------------------------------------------------

    total = sum(
        weights[parameter]
        for parameter in required_parameters
    )


    if abs(total - 1.0) > 0.0001:

        print(
            f"Invalid total weight: {total}"
        )

        print(
            "Weights must equal 1.0."
        )

        return False


    return True


# ==========================================================
# GET SKILL SCORE
# ==========================================================

def get_skill_score(skill_data):

    if skill_data is None:

        return None

    score = skill_data.get(
        "overall_skill_score"
    )

    if score is None:

        return None

    return float(score)


# ==========================================================
# GET EXPERIENCE SCORE
# ==========================================================

def get_experience_score(
    experience_data
):

    if experience_data is None:

        return None

    experiences = experience_data.get(
        "experience",
        []
    )


    if not experiences:

        return None


    relevance_scores = []


    for experience in experiences:

        score = experience.get(
            "relevance_score"
        )

        if score is not None:

            relevance_scores.append(
                float(score)
            )


    if not relevance_scores:

        return None


    # Highest relevant experience

    highest_score = max(
        relevance_scores
    )


    # Convert 0-1 to 0-100

    return highest_score * 100


# ==========================================================
# GET EDUCATION SCORE
# ==========================================================

def get_education_score(
    education_data
):

    if education_data is None:

        return None


    education = education_data.get(
        "education",
        []
    )


    if not education:

        return None


    # ------------------------------------------------------
    # Current rule
    # ------------------------------------------------------
    #
    # Education exists and is relevant
    # to Python Developer.
    #
    # This can later be replaced with
    # detailed education matching.
    #

    return 100.0


# ==========================================================
# GET SEMANTIC SCORE
# ==========================================================

def get_semantic_score(
    similarity_data
):

    if similarity_data is None:

        return None


    score = similarity_data.get(
        "similarity_score"
    )


    if score is None:

        return None


    # Convert 0-1 to 0-100

    return float(score) * 100


# ==========================================================
# CALCULATE ATS SCORE
# ==========================================================

def calculate_ats_score(
    scores,
    weights
):

    valid_scores = {}

    valid_weights = {}


    # ------------------------------------------------------
    # Keep available scores
    # ------------------------------------------------------

    for component in scores:

        if scores[component] is not None:

            valid_scores[component] = (
                scores[component]
            )

            valid_weights[component] = (
                weights[component]
            )


    # ------------------------------------------------------
    # No data
    # ------------------------------------------------------

    if not valid_scores:

        return None, {}, {}


    # ------------------------------------------------------
    # Available weight
    # ------------------------------------------------------

    total_available_weight = sum(
        valid_weights.values()
    )


    # ------------------------------------------------------
    # Calculate weighted score
    # ------------------------------------------------------

    final_score = 0

    normalized_weights = {}

    contributions = {}


    for component in valid_scores:

        normalized_weight = (

            valid_weights[component]
            /
            total_available_weight

        )


        contribution = (

            valid_scores[component]
            *
            normalized_weight

        )


        final_score += contribution


        normalized_weights[component] = (
            normalized_weight
        )


        contributions[component] = (
            contribution
        )


    return (

        round(
            final_score,
            2
        ),

        normalized_weights,

        contributions

    )


# ==========================================================
# MATCHING STATUS
# ==========================================================

def get_matching_status(
    score
):

    if score is None:

        return "Insufficient Data"

    if score >= 90:

        return "Excellent Match"

    elif score >= 80:

        return "Strong Match"

    elif score >= 70:

        return "Good Match"

    elif score >= 50:

        return "Moderate Match"

    else:

        return "Poor Match"


# ==========================================================
# RECOMMENDATION
# ==========================================================

def get_recommendation(
    score
):

    if score is None:

        return "Manual Review Required"

    if score >= 80:

        return "Recommended for Interview"

    elif score >= 60:

        return "Can be Considered"

    else:

        return "Not Recommended"


# ==========================================================
# CREATE COMPONENT REPORT
# ==========================================================

def create_component_report(
    scores,
    weights,
    normalized_weights,
    contributions
):

    report = {}


    for component in scores:

        # --------------------------------------------------
        # Missing
        # --------------------------------------------------

        if scores[component] is None:

            report[component] = {

                "score": None,

                "original_weight":
                    weights[component],

                "normalized_weight":
                    None,

                "contribution":
                    0,

                "status":
                    "Missing"

            }


        # --------------------------------------------------
        # Available
        # --------------------------------------------------

        else:

            report[component] = {

                "score":
                    round(
                        scores[component],
                        2
                    ),

                "original_weight":
                    weights[component],

                "normalized_weight":
                    round(
                        normalized_weights[component],
                        4
                    ),

                "contribution":
                    round(
                        contributions[component],
                        2
                    ),

                "status":
                    "Available"

            }


    return report


# ==========================================================
# MAIN PROGRAM
# ==========================================================

if __name__ == "__main__":

    print("\n===================================")
    print("ZecPath ATS SCORING ENGINE")
    print("===================================\n")


    # ------------------------------------------------------
    # Load weights
    # ------------------------------------------------------

    weights = load_role_weights(
        target_role
    )


    if weights is None:

        exit()


    # ------------------------------------------------------
    # Validate weights
    # ------------------------------------------------------

    if not validate_weights(
        weights
    ):

        exit()


    # ------------------------------------------------------
    # Load data
    # ------------------------------------------------------

    skill_data = load_json(
        SKILL_FILE
    )

    similarity_data = load_json(
        SIMILARITY_FILE
    )

    experience_data = load_json(
        EXPERIENCE_FILE
    )

    education_data = load_json(
        EDUCATION_FILE
    )


    # ------------------------------------------------------
    # Check required files
    # ------------------------------------------------------

    if (
        skill_data is None
        or similarity_data is None
        or experience_data is None
        or education_data is None
    ):

        print(
            "\nRequired data is missing."
        )

        exit()


    # ------------------------------------------------------
    # Calculate individual scores
    # ------------------------------------------------------

    skill_score = get_skill_score(
        skill_data
    )

    experience_score = get_experience_score(
        experience_data
    )

    education_score = get_education_score(
        education_data
    )

    semantic_score = get_semantic_score(
        similarity_data
    )


    # ------------------------------------------------------
    # Store scores
    # ------------------------------------------------------

    scores = {

        "skill_match":
            skill_score,

        "experience_relevance":
            experience_score,

        "education_alignment":
            education_score,

        "semantic_similarity":
            semantic_score

    }


    # ------------------------------------------------------
    # Display individual scores
    # ------------------------------------------------------

    print(
        "Individual Scores:\n"
    )


    for component in scores:

        if scores[component] is None:

            print(
                f"{component}: Missing"
            )

        else:

            print(
                f"{component}: "
                f"{scores[component]:.2f}"
            )


    # ------------------------------------------------------
    # Calculate final ATS score
    # ------------------------------------------------------

    (
        final_score,
        normalized_weights,
        contributions

    ) = calculate_ats_score(

        scores,

        weights

    )


    # ------------------------------------------------------
    # Matching status
    # ------------------------------------------------------

    matching_status = (
        get_matching_status(
            final_score
        )
    )


    # ------------------------------------------------------
    # Recommendation
    # ------------------------------------------------------

    recommendation = (
        get_recommendation(
            final_score
        )
    )


    # ------------------------------------------------------
    # Component report
    # ------------------------------------------------------

    component_report = (
        create_component_report(

            scores,

            weights,

            normalized_weights,

            contributions

        )
    )


    # ------------------------------------------------------
    # Final ATS Report
    # ------------------------------------------------------

    ats_report = {

        "candidate_id":
            skill_data.get(
                "candidate_id",
                "CAND001"
            ),

        "target_role":
            target_role,

        "final_ats_score":
            final_score,

        "similarity_percentage":
            similarity_data.get(
                "similarity_percentage"
            ),

        "matching_status":
            matching_status,

        "recommendation":
            recommendation,

        "components":
            component_report

    }


    # ------------------------------------------------------
    # Display Final Result
    # ------------------------------------------------------

    print("\n===================================")
    print("FINAL ATS SCORE")
    print("===================================\n")


    print(
        json.dumps(
            ats_report,
            indent=4,
            ensure_ascii=False
        )
    )


    # ------------------------------------------------------
    # Save Result
    # ------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(

            ats_report,

            file,

            indent=4,

            ensure_ascii=False

        )


    print(
        "\nATS score saved to ats_score.json"
    )