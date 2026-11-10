#This uses your actual Candidate 006 cleaned resume.
import os
import sys
import json


# ==========================================================
# PROJECT ROOT
# ==========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:

    sys.path.insert(
        0,
        PROJECT_ROOT
    )


from parsers.entity_detector import (
    extract_entities
)


# ==========================================================
# CANDIDATE
# ==========================================================

CANDIDATE_ID = "candidate_006"


RESUME_PATH = os.path.join(
    PROJECT_ROOT,
    "day17_testing",
    "results",
    CANDIDATE_ID,
    "cleaned_resume.txt"
)


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("\n")
    print("=" * 70)
    print(
        "       ZecPath DAY 18 ENTITY DETECTION"
    )
    print("=" * 70)

    if not os.path.exists(
        RESUME_PATH
    ):

        print(
            f"\nERROR: Resume not found:"
        )

        print(
            RESUME_PATH
        )

        return

    # ------------------------------------------------------
    # Load resume
    # ------------------------------------------------------

    with open(
        RESUME_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        resume_text = file.read()

    # ------------------------------------------------------
    # Extract entities
    # ------------------------------------------------------

    entities = extract_entities(
        resume_text
    )

    # ------------------------------------------------------
    # Display
    # ------------------------------------------------------

    print(
        "\nCandidate Name:"
    )

    print(
        entities["name"]
    )

    print(
        "\nJob Titles:"
    )

    if entities["job_titles"]:

        for title in entities["job_titles"]:

            print(
                f"[DETECTED] {title}"
            )

    else:

        print(
            "No job titles detected."
        )

    print(
        "\nSkills:"
    )

    for skill in entities["skills"]:

        print(
            f"[DETECTED] {skill}"
        )

    print(
        "\nDegrees:"
    )

    for degree in entities["degrees"]:

        print(
            f"[DETECTED] {degree}"
        )

    print(
        "\nExperience:"
    )

    if entities["experience_years"] is not None:

        print(
            f"{entities['experience_years']:.2f} years"
        )

    else:

        print(
            "Experience not detected."
        )

    print(
        "\nYears:"
    )

    for year in entities["years"]:

        print(
            f"[DETECTED] {year}"
        )

    print(
        "\nProjects:"
    )

    if entities["projects"]:

        for project in entities["projects"]:

            print(
                f"[DETECTED] {project}"
            )

    else:

        print(
            "No projects detected."
        )

    # ------------------------------------------------------
    # Save
    # ------------------------------------------------------

    results_dir = os.path.join(
        PROJECT_ROOT,
        "day18_optimization",
        "results"
    )

    os.makedirs(
        results_dir,
        exist_ok=True
    )

    output_path = os.path.join(
        results_dir,
        f"{CANDIDATE_ID}_entities.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            entities,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        "\nEntity detection result saved to:"
    )

    print(
        output_path
    )


if __name__ == "__main__":

    main()