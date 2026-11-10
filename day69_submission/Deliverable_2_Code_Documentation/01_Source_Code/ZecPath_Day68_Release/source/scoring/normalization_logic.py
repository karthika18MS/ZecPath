import re
import json


# ==========================================================
# Input File
# ==========================================================

INPUT_FILE = "ats_score.json"



# ==========================================================
# Output File
# ==========================================================

OUTPUT_FILE = "normalized_candidate.json"


# ==========================================================
# Normalize General Text
# ==========================================================

def normalize_text(text):

    if text is None:

        return ""

    # Convert to string
    text = str(text)

    # Convert text to lowercase
    text = text.lower()

    # Replace different dash characters
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Replace multiple spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    # Remove spaces from beginning and end
    text = text.strip()

    return text


# ==========================================================
# Normalize Skill Names
# ==========================================================

def normalize_skill(skill):

    skill = normalize_text(
        skill
    )

    skill_aliases = {

        "py": "python",

        "python programming":
            "python",

        "django rest":
            "django rest framework",

        "drf":
            "django rest framework",

        "restful api":
            "rest api",

        "restful apis":
            "rest api",

        "mongo":
            "mongodb",

        "mongo db":
            "mongodb",

        "postgres":
            "postgresql",

        "postgre sql":
            "postgresql",

        "js":
            "javascript",

        "k8s":
            "kubernetes",

        "amazon web services":
            "aws",

        "continuous integration":
            "ci/cd",

        "continuous deployment":
            "ci/cd"

    }

    return skill_aliases.get(
        skill,
        skill
    )


# ==========================================================
# Normalize Education
# ==========================================================

def normalize_degree(degree):

    degree = normalize_text(
        degree
    )

    degree_aliases = {

        "m.c.a":
            "mca",

        "master of computer applications":
            "mca",

        "mca degree":
            "mca",

        "b.c.a":
            "bca",

        "bachelor of computer applications":
            "bca",

        "bca degree":
            "bca",

        "b.tech":
            "btech",

        "b.e":
            "be",

        "m.tech":
            "mtech"

    }

    return degree_aliases.get(
        degree,
        degree
    )

    #.get(key,default) first degree indicates the key you are looking up.the second degree indicates the default value if the key isn't found.
# ==========================================================
# Normalize Experience
# ==========================================================

def normalize_experience(
    experience
):

    if experience is None:

        return None

    experience = normalize_text(
        experience
    )

    # Convert "4 years" into standard format
    match = re.search(
        r"(\d+)\s*years?",
        experience
    )

    years = 0

    if match:

        years = int(
            match.group(1)
        )

    # Extract months
    match_months = re.search(
        r"(\d+)\s*months?",
        experience
    )

    months = 0

    if match_months:

        months = int(
            match_months.group(1)
        )

    total_months = (
        years * 12
        + months
    )

    return {

        "years": years,

        "months": months,

        "total_months":
            total_months

    }


# ==========================================================
# Normalize Score
# ==========================================================

def normalize_score(score):

    if score is None:

        return None

    # Convert 0-1 scores to 0-100
    if 0 <= score <= 1:

        score = score * 100

    # Keep scores inside 0-100
    score = max(
        0,
        min(
            score,
            100
        )
    )

    return round(
        score,
        2
    )


# ==========================================================
# Normalize ATS Components
# ==========================================================

def normalize_components(
    components
):

    normalized = {}

    for component, data in components.items():

        normalized[
            component
        ] = {

            "score":
                normalize_score(
                    data.get(
                        "score"
                    )
                ),

            "status":
                data.get(
                    "status",
                    "Available"
                )

        }

    return normalized


# ==========================================================
# Normalize Candidate Data
# ==========================================================

def normalize_candidate(
    candidate
):

    normalized_candidate = {

        "candidate_id":
            normalize_text(
                candidate.get(
                    "candidate_id",
                    ""
                )
            ),

        "target_role":
            normalize_text(
                candidate.get(
                    "target_role",
                    ""
                )
            ),

        "final_ats_score":
            normalize_score(
                candidate.get(
                    "final_ats_score"
                )
            ),

        "components":
            normalize_components(
                candidate.get(
                    "components",
                    {}
                )
            )

    }

    # Normalize experience if available

    if "total_experience" in candidate:

        normalized_candidate[
            "total_experience"
        ] = normalize_experience(
            candidate[
                "total_experience"
            ]
        )

    return normalized_candidate


# ==========================================================
# Display Normalized Candidate
# ==========================================================

def display_candidate(
    candidate
):

    print("\n===================================")
    print("ZecPath NORMALIZATION LOGIC")
    print("===================================\n")

    print(
        "Candidate ID :",
        candidate[
            "candidate_id"
        ]
    )

    print(
        "Target Role  :",
        candidate[
            "target_role"
        ]
    )

    print(
        "ATS Score    :",
        candidate[
            "final_ats_score"
        ]
    )

    print(
        "\nNormalized Components:"
    )

    for component, data in candidate[
        "components"
    ].items():

        print(
            f"{component:<25}"
            f": {data['score']}"
        )


    if "total_experience" in candidate:

        print(
            "\nNormalized Experience:"
        )

        print(
            candidate[
                "total_experience"
            ])


# ==========================================================
# Save Normalized Candidate
# ==========================================================

def save_candidate(
    candidate
):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            candidate,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        "\nNormalized candidate saved to "
        "normalized_candidate.json"
    )


# ==========================================================
# Main Program
# ==========================================================

if __name__ == "__main__":

    print(
        "\n==================================="
    )

    print(
        "ZecPath CANDIDATE NORMALIZATION"
    )

    print(
        "===================================\n"
    )


    # ------------------------------------------------------
    # Step 1: Read ATS score
    # ------------------------------------------------------

    try:

        with open(
            INPUT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            candidate_data = json.load(
                file
            )

    except FileNotFoundError:

        print(
            "Error: ats_score.json not found."
        )

        exit()

    except json.JSONDecodeError:

        print(
            "Error: Invalid JSON format."
        )

        exit()


    # ------------------------------------------------------
    # Step 2: Normalize candidate
    # ------------------------------------------------------

    normalized_candidate = (
        normalize_candidate(
            candidate_data
        )
    )


    # ------------------------------------------------------
    # Step 3: Display result
    # ------------------------------------------------------

    display_candidate(
        normalized_candidate
    )


    # ------------------------------------------------------
    # Step 4: Save result
    # ------------------------------------------------------

    save_candidate(
        normalized_candidate
    )