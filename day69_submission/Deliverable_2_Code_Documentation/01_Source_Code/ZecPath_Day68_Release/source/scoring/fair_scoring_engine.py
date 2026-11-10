import json


# ==========================================================
# Input File
# ==========================================================

INPUT_FILE = "ats_score.json"


# ==========================================================
# Output File
# ==========================================================

OUTPUT_FILE = "fair_ats_score.json"


# ==========================================================
# Normalize Score
# ==========================================================

def normalize_score(score):

    # Missing score
    if score is None:

        return None

    # Convert 0-1 score to 0-100
    if 0 <= score <= 1:

        return score * 100

    # Keep score within 0-100
    if score < 0:

        return 0

    if score > 100:

        return 100

    return score


# ==========================================================
# Get Safe Score
# ==========================================================

def get_safe_score(component_data):

    score = component_data.get(
        "score"
    )

    status = component_data.get(
        "status",
        "Available"
    )

    # Missing information
    if score is None or status == "Missing":

        return None

    return normalize_score(
        score
    )


# ==========================================================
# Calculate Fair Weighted Score
# ==========================================================

def calculate_fair_score(
    components
):

    # ------------------------------------------------------
    # Original weights
    # ------------------------------------------------------

    weights = {

        "skill_match": 0.35,

        "experience_relevance": 0.25,

        "education_alignment": 0.15,

        "semantic_similarity": 0.25

    }


    available_components = {}

    weighted_total = 0

    total_weight = 0


    # ------------------------------------------------------
    # Process each component
    # ------------------------------------------------------

    for component, weight in weights.items():

        if component not in components:

            continue

        score = get_safe_score(
            components[component]
        )


        # Skip missing information
        if score is None:

            continue


        available_components[
            component
        ] = {

            "score": round(
                score,
                2
            ),

            "weight": weight

        }


        weighted_total += (
            score * weight
        )

        total_weight += weight


    # ------------------------------------------------------
    # No valid scores
    # ------------------------------------------------------

    if total_weight == 0:

        return None, available_components


    # ------------------------------------------------------
    # Normalize available weights
    # ------------------------------------------------------

    fair_score = (
        weighted_total
        /
        total_weight
    )


    return round(
        fair_score,
        2
    ), available_components


# ==========================================================
# Generate Fairness Notes
# ==========================================================

def generate_fairness_notes(
    components
):

    notes = []


    # ------------------------------------------------------
    # Check personal information
    # ------------------------------------------------------

    notes.append(
        "Scoring is based on job-related "
        "qualifications rather than non-essential "
        "personal attributes."
    )


    # ------------------------------------------------------
    # Check semantic matching
    # ------------------------------------------------------

    if "semantic_similarity" in components:

        notes.append(
            "Semantic similarity is included to reduce "
            "over-dependence on exact keyword matching."
        )


    # ------------------------------------------------------
    # Check normalization
    # ------------------------------------------------------

    notes.append(
        "All available scoring components are "
        "normalized to a 0-100 scale."
    )


    # ------------------------------------------------------
    # Missing data
    # ------------------------------------------------------

    missing_components = []


    for component, data in components.items():

        if data.get("status") == "Missing":

            missing_components.append(
                component
            )


    if missing_components:

        notes.append(
            "Missing components were excluded from "
            "the weighted calculation and the remaining "
            "weights were normalized."
        )

    else:

        notes.append(
            "All scoring components were available."
        )


    return notes


# ==========================================================
# Generate Fair ATS Report
# ==========================================================

def generate_fair_report(
    ats_data
):

    components = ats_data.get(
        "components",
        {}
    )


    fair_score, available_components = (
        calculate_fair_score(
            components
        )
    )


    fairness_notes = (
        generate_fairness_notes(
            components
        )
    )


    if fair_score is None:

        status = "Insufficient Data"

        recommendation = "Manual Review Required"

    elif fair_score >= 80:

        status = "Strong Match"

        recommendation = (
            "Recommended for Interview"
        )

    elif fair_score >= 60:

        status = "Good Match"

        recommendation = (
            "Can be Considered"
        )

    elif fair_score >= 50:

        status = "Moderate Match"

        recommendation = (
            "Manual Review Required"
        )

    else:

        status = "Poor Match"

        recommendation = (
            "Not Recommended"
        )


    report = {

        "candidate_id":
            ats_data.get(
                "candidate_id"
            ),

        "target_role":
            ats_data.get(
                "target_role"
            ),

        "fair_ats_score":
            fair_score,

        "matching_status":
            status,

        "recommendation":
            recommendation,

        "components":
            available_components,

        "fairness_improvements":
            fairness_notes

    }


    return report


# ==========================================================
# Display Report
# ==========================================================

def display_report(
    report
):

    print("\n===================================")
    print("ZecPath FAIR SCORING ENGINE")
    print("===================================\n")


    print(
        "Candidate ID :",
        report["candidate_id"]
    )


    print(
        "Target Role  :",
        report["target_role"]
    )


    print(
        "Fair ATS Score:",
        report["fair_ats_score"]
    )


    print(
        "Matching Status:",
        report["matching_status"]
    )


    print(
        "Recommendation:",
        report["recommendation"]
    )


    print("\n-----------------------------------")
    print("FAIRNESS IMPROVEMENTS")
    print("-----------------------------------")


    for note in report[
        "fairness_improvements"
    ]:

        print(
            "•",
            note
        )


# ==========================================================
# Save Report
# ==========================================================

def save_report(
    report
):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )


    print(
        "\nFair ATS score saved to "
        "fair_ats_score.json"
    )


# ==========================================================
# Main Program
# ==========================================================

if __name__ == "__main__":

    print("\n===================================")
    print("ZecPath FAIR SCORING")
    print("===================================\n")


    # ------------------------------------------------------
    # Step 1: Read ATS score
    # ------------------------------------------------------

    try:

        with open(
            INPUT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            ats_data = json.load(
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
    # Step 2: Generate fair score
    # ------------------------------------------------------

    fair_report = generate_fair_report(
        ats_data
    )


    # ------------------------------------------------------
    # Step 3: Display result
    # ------------------------------------------------------

    display_report(
        fair_report
    )


    # ------------------------------------------------------
    # Step 4: Save result
    # ------------------------------------------------------

    save_report(
        fair_report
    )