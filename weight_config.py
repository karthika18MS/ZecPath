import json


# ==========================================================
# Weight Configuration File
# ==========================================================

WEIGHTS_FILE = "scoring_weights.json"


# ==========================================================
# Load Weight Configuration
# ==========================================================

def load_weights():

    try:

        with open(
            WEIGHTS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            weights = json.load(file)

        return weights

    except FileNotFoundError:

        print("Error: scoring_weights.json not found.")

        return {}

    except json.JSONDecodeError:

        print("Error: Invalid JSON format in scoring_weights.json.")

        return {}


# ==========================================================
# Validate Weights
# ==========================================================

def validate_weights(weights):

    required_parameters = [

        "skill_match",

        "experience_relevance",

        "education_alignment",

        "semantic_similarity"

    ]

    # Check required parameters
    for parameter in required_parameters:

        if parameter not in weights:

            print(
                f"Missing weight: {parameter}"
            )

            return False

    # Check weight values
    for parameter in required_parameters:

        value = weights[parameter]

        if not isinstance(value, (int, float)):

            print(
                f"Invalid value for {parameter}"
            )

            return False

        if value < 0 or value > 1:

            print(
                f"Weight for {parameter} "
                f"must be between 0 and 1."
            )

            return False

    # Check total
    total = sum(
        weights[parameter]
        for parameter in required_parameters
    )

    if abs(total - 1.0) > 0.0001:

        print(
            f"Invalid weight total: {total}"
        )

        print(
            "Weights must add up to 1.0."
        )

        return False

    return True


# ==========================================================
# Get Weights for a Specific Job Role
# ==========================================================

def get_weights_for_role(target_role):

    all_weights = load_weights()

    if not all_weights:

        return None

    if target_role not in all_weights:

        print(
            f"Error: No weights found for "
            f"'{target_role}'."
        )

        return None

    role_weights = all_weights[target_role]

    if validate_weights(role_weights):

        return role_weights

    return None


# ==========================================================
# Display Weights
# ==========================================================

def display_weights(target_role):

    weights = get_weights_for_role(target_role)

    if weights is None:

        return

    print("\n===================================")
    print("SCORING WEIGHTS")
    print("===================================\n")

    print("Target Role :", target_role)

    print(
        f"Skill Match          : "
        f"{weights['skill_match'] * 100:.0f}%"
    )

    print(
        f"Experience Relevance : "
        f"{weights['experience_relevance'] * 100:.0f}%"
    )

    print(
        f"Education Alignment  : "
        f"{weights['education_alignment'] * 100:.0f}%"
    )

    print(
        f"Semantic Similarity  : "
        f"{weights['semantic_similarity'] * 100:.0f}%"
    )

    print("-----------------------------------")

    total = sum(weights.values())

    print(
        f"Total Weight         : "
        f"{total * 100:.0f}%"
    )


# ==========================================================
# Main Program
# ==========================================================

if __name__ == "__main__":

    target_role = "Python Developer"

    display_weights(target_role)