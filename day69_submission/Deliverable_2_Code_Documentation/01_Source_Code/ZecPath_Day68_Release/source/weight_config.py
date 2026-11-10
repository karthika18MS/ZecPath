import json


# ==========================================================
# Weight Configuration File
# ==========================================================

WEIGHTS_FILE = "scoring_weights.json" #This creates a variable containing the filename.


# ==========================================================
# Load Weight Configuration
# ==========================================================

def load_weights(): #Open scoring_weights.json, read the JSON data, and return it to the program.

    try:

        with open(
            WEIGHTS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            weights = json.load(file) #json.load() reads the JSON file and converts it into a Python object.

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

def validate_weights(weights): #This function checks whether the weights are valid.

    #This creates a list containing the four components required by your ATS framework.

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
    for parameter in required_parameters: #Again, the program checks each of the four parameters.

        value = weights[parameter] #Gets the actual weight.

        if not isinstance(value, (int, float)): #This checks whether the weight is a number.

            print(
                f"Invalid value for {parameter}"
            )

            return False

        if value < 0 or value > 1: #This ensures every weight is between: 0 and 1

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

    if abs(total - 1.0) > 0.0001: #This checks whether the total is approximately 1.0

        print(
            f"Invalid weight total: {total}"
        )

        print(
            "Weights must add up to 1.0."
        )

        return False

    return True #If the program reaches this line, all checks passed.


# ==========================================================
# Get Weights for a Specific Job Role
# ==========================================================

def get_weights_for_role(target_role): #This function gets the correct weight configuration for a particular role.

    all_weights = load_weights()

    if not all_weights:

        return None

    if target_role not in all_weights:

        print(
            f"Error: No weights found for "
            f"'{target_role}'."
        )

        return None

    role_weights = all_weights[target_role] #This extracts the configuration for the requested role.

    if validate_weights(role_weights):

        return role_weights

    return None


# ==========================================================
# Display Weights
# ==========================================================

def display_weights(target_role): #This function is only responsible for displaying the selected role's weights in a readable format.

    weights = get_weights_for_role(target_role) #Gets the validated weights for the role.

    if weights is None:

        return #Stop the function.

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

    total = sum(weights.values()) #weights.values() gets all the weight values:

    print(
        f"Total Weight         : "
        f"{total * 100:.0f}%"
    )


# ==========================================================
# Main Program
# ==========================================================

if __name__ == "__main__": #weights.values() gets all the weight values:

    target_role = "Python Developer"

    display_weights(target_role)
