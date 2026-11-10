import os
import sys
import json
import re


# ==========================================================
# ZecPath - Day 17 Experience Matching Engine
# ==========================================================
#
# Purpose:
# Compare candidate experience from the resume with the
# experience requirement mentioned in the job description.
#
# Usage:
#
# python -m day17_testing.day17_experience_matching candidate_006 "Backend Developer"
#
# Example:
#
# python -m day17_testing.day17_experience_matching candidate_007 "HR Executive"
#
# ==========================================================


# ==========================================================
# STEP 1: Read Candidate Information
# ==========================================================

if len(sys.argv) < 3:

    print("\nUsage:")

    print(
        'python -m day17_testing.day17_experience_matching '
        'candidate_id "Target Role"'
    )

    print("\nExample:")

    print(
        'python -m day17_testing.day17_experience_matching '
        'candidate_006 "Backend Developer"'
    )

    sys.exit(1)


candidate_id = sys.argv[1]

target_role = sys.argv[2]


# ==========================================================
# STEP 2: Define Project Paths
# ==========================================================

BASE_DIR = "day17_testing"


candidate_folder = os.path.join(
    BASE_DIR,
    "results",
    candidate_id
)


# ==========================================================
# Input Files
# ==========================================================

RESUME_FILE = os.path.join(
    candidate_folder,
    "cleaned_resume.txt"
)


JD_FILE = os.path.join(
    candidate_folder,
    "job_description.txt"
)


# ==========================================================
# Output File
# ==========================================================

OUTPUT_FILE = os.path.join(
    candidate_folder,
    "day17_experience_match.json"
)


# ==========================================================
# STEP 3: Check Resume File
# ==========================================================

if not os.path.exists(RESUME_FILE):

    print(
        "\nError: Resume file not found:"
    )

    print(
        RESUME_FILE
    )

    print(
        "\nRun run_day17_test.py first."
    )

    sys.exit(1)


# ==========================================================
# STEP 4: Check Job Description File
# ==========================================================

if not os.path.exists(JD_FILE):

    print(
        "\nError: Job description file not found:"
    )

    print(
        JD_FILE
    )

    print(
        "\nRun run_day17_test.py first."
    )

    sys.exit(1)


# ==========================================================
# STEP 5: Read Resume
# ==========================================================

with open(
    RESUME_FILE,
    "r",
    encoding="utf-8"
) as file:

    resume_text = file.read()


# ==========================================================
# STEP 6: Read Job Description
# ==========================================================

with open(
    JD_FILE,
    "r",
    encoding="utf-8"
) as file:

    job_description = file.read()


# ==========================================================
# STEP 7: Normalize Text
# ==========================================================

def normalize_text(text):

    text = str(text)

    # Convert to lowercase
    text = text.lower()

    # Normalize dash characters
    text = text.replace(
        "–",
        "-"
    )

    text = text.replace(
        "—",
        "-"
    )

    # Normalize multiple spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


resume_text = normalize_text(
    resume_text
)

job_description = normalize_text(
    job_description
)


# ==========================================================
# STEP 8: Extract Candidate Experience
# ==========================================================
#
# The function looks for common formats such as:
#
# 3 years
# 3 years of experience
# 3+ years
# 2.5 years
# 6 months
#
# ==========================================================

def extract_candidate_experience(text):

    # ------------------------------------------------------
    # Search for years
    # ------------------------------------------------------

    year_matches = re.findall(
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
        text
    )

    years = []

    for value in year_matches:

        try:

            years.append(
                float(value)
            )

        except ValueError:

            pass


    # ------------------------------------------------------
    # Search for months
    # ------------------------------------------------------

    month_matches = re.findall(
        r"(\d+)\s*\+?\s*months?",
        text
    )

    months = []

    for value in month_matches:

        try:

            months.append(
                int(value)
            )

        except ValueError:

            pass


    # ------------------------------------------------------
    # Convert experience to months
    # ------------------------------------------------------

    total_months = 0


    if years:

        # Use the largest detected year value.
        #
        # This avoids adding the same experience multiple
        # times when a resume mentions "3 years" in both
        # summary and experience sections.

        maximum_years = max(
            years
        )

        total_months = int(
            maximum_years * 12
        )


    # Add months only if years were not detected.

    elif months:

        total_months = max(
            months
        )


    # ------------------------------------------------------
    # Convert months to years
    # ------------------------------------------------------

    experience_years = (
        total_months / 12
    )


    return {

        "years":
            round(
                experience_years,
                2
            ),

        "months":
            total_months

    }


# ==========================================================
# STEP 9: Extract Required Experience from JD
# ==========================================================
#
# Examples supported:
#
# 1-4 years
# 2-5 years
# 3+ years
# minimum 2 years
# 2 years of experience
#
# ==========================================================

def extract_required_experience(text):

    # ------------------------------------------------------
    # Pattern 1:
    #
    # 1-4 years
    # 2–5 years
    #
    # ------------------------------------------------------

    range_match = re.search(
        r"(\d+(?:\.\d+)?)\s*[-to]+\s*(\d+(?:\.\d+)?)\s*years?",
        text
    )


    if range_match:

        minimum_years = float(
            range_match.group(1)
        )

        maximum_years = float(
            range_match.group(2)
        )

        return {

            "minimum_years":
                minimum_years,

            "maximum_years":
                maximum_years,

            "requirement_type":
                "range"

        }


    # ------------------------------------------------------
    # Pattern 2:
    #
    # 3+ years
    #
    # ------------------------------------------------------

    plus_match = re.search(
        r"(\d+(?:\.\d+)?)\s*\+\s*years?",
        text
    )


    if plus_match:

        minimum_years = float(
            plus_match.group(1)
        )

        return {

            "minimum_years":
                minimum_years,

            "maximum_years":
                None,

            "requirement_type":
                "minimum"

        }


    # ------------------------------------------------------
    # Pattern 3:
    #
    # minimum 2 years
    #
    # ------------------------------------------------------

    minimum_match = re.search(
        r"minimum\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*years?",
        text
    )


    if minimum_match:

        minimum_years = float(
            minimum_match.group(1)
        )

        return {

            "minimum_years":
                minimum_years,

            "maximum_years":
                None,

            "requirement_type":
                "minimum"

        }


    # ------------------------------------------------------
    # Pattern 4:
    #
    # 2 years of experience
    #
    # ------------------------------------------------------

    single_match = re.search(
        r"(\d+(?:\.\d+)?)\s*years?\s*(?:of\s+)?experience",
        text
    )


    if single_match:

        required_years = float(
            single_match.group(1)
        )

        return {

            "minimum_years":
                required_years,

            "maximum_years":
                required_years,

            "requirement_type":
                "exact"

        }


    # ------------------------------------------------------
    # No requirement found
    # ------------------------------------------------------

    return {

        "minimum_years":
            None,

        "maximum_years":
            None,

        "requirement_type":
            "not_specified"

    }


# ==========================================================
# STEP 10: Extract Experience
# ==========================================================

candidate_experience = (
    extract_candidate_experience(
        resume_text
    )
)


required_experience = (
    extract_required_experience(
        job_description
    )
)


# ==========================================================
# STEP 11: Get Candidate Experience in Years
# ==========================================================

candidate_years = (
    candidate_experience[
        "years"
    ]
)


# ==========================================================
# STEP 12: Get JD Experience Requirement
# ==========================================================

minimum_years = (
    required_experience[
        "minimum_years"
    ]
)


maximum_years = (
    required_experience[
        "maximum_years"
    ]
)


requirement_type = (
    required_experience[
        "requirement_type"
    ]
)


# ==========================================================
# STEP 13: Calculate Experience Score
# ==========================================================

if requirement_type == "not_specified":

    # If the JD doesn't mention experience,
    # experience cannot be used to penalize the candidate.

    experience_score = 100.0

    experience_status = (
        "Experience Requirement Not Specified"
    )


elif requirement_type == "range":

    if (
        candidate_years >= minimum_years
        and
        candidate_years <= maximum_years
    ):

        experience_score = 100.0

        experience_status = (
            "Experience Fully Meets Requirement"
        )


    elif candidate_years < minimum_years:

        # Candidate has less experience than required.

        ratio = (
            candidate_years
            /
            minimum_years
        )

        experience_score = (
            ratio * 100
        )

        # Prevent score from exceeding 100.

        experience_score = min(
            experience_score,
            100.0
        )

        experience_status = (
            "Experience Below Requirement"
        )


    else:

        # Candidate exceeds the maximum.
        #
        # Extra experience is not treated as a failure.
        # The candidate still satisfies the requirement.

        experience_score = 100.0

        experience_status = (
            "Experience Meets Requirement"
        )


elif requirement_type == "minimum":

    if candidate_years >= minimum_years:

        experience_score = 100.0

        experience_status = (
            "Experience Meets Minimum Requirement"
        )

    else:

        ratio = (
            candidate_years
            /
            minimum_years
        )

        experience_score = (
            ratio * 100
        )

        experience_score = min(
            experience_score,
            100.0
        )

        experience_status = (
            "Experience Below Minimum Requirement"
        )


elif requirement_type == "exact":

    if candidate_years >= minimum_years:

        experience_score = 100.0

        experience_status = (
            "Experience Meets Requirement"
        )

    else:

        ratio = (
            candidate_years
            /
            minimum_years
        )

        experience_score = (
            ratio * 100
        )

        experience_score = min(
            experience_score,
            100.0
        )

        experience_status = (
            "Experience Below Requirement"
        )


else:

    experience_score = 100.0

    experience_status = (
        "Experience Requirement Not Specified"
    )


# ==========================================================
# STEP 14: Round Score
# ==========================================================

experience_score = round(
    experience_score,
    2
)


# ==========================================================
# STEP 15: Display Header
# ==========================================================

print(
    "\n=============================================="
)

print(
    "       ZecPath DAY 17 EXPERIENCE MATCHING"
)

print(
    "==============================================\n"
)


# ==========================================================
# STEP 16: Candidate Information
# ==========================================================

print(
    "Candidate ID:",
    candidate_id
)

print(
    "Target Role :",
    target_role
)


# ==========================================================
# STEP 17: Candidate Experience
# ==========================================================

print(
    "\nCandidate Experience:"
)

print(
    f"{candidate_years:.2f} years"
)


# ==========================================================
# STEP 18: JD Requirement
# ==========================================================

print(
    "\nJob Description Requirement:"
)


if requirement_type == "range":

    print(
        f"{minimum_years:g}-{maximum_years:g} years"
    )


elif requirement_type == "minimum":

    print(
        f"{minimum_years:g}+ years"
    )


elif requirement_type == "exact":

    print(
        f"{minimum_years:g} years"
    )


else:

    print(
        "Not specified"
    )


# ==========================================================
# STEP 19: Display Score
# ==========================================================

print(
    "\nExperience Relevance Score:",
    f"{experience_score:.2f}%"
)


print(
    "Experience Status:",
    experience_status
)


# ==========================================================
# STEP 20: Create JSON Output
# ==========================================================

output = {

    "candidate_id":
        candidate_id,

    "target_role":
        target_role,

    "candidate_experience": {

        "years":
            candidate_experience[
                "years"
            ],

        "months":
            candidate_experience[
                "months"
            ]

    },

    "required_experience": {

        "minimum_years":
            minimum_years,

        "maximum_years":
            maximum_years,

        "requirement_type":
            requirement_type

    },

    "experience_score":
        experience_score,

    "experience_status":
        experience_status

}


# ==========================================================
# STEP 21: Save JSON
# ==========================================================

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


# ==========================================================
# STEP 22: Display Output Location
# ==========================================================

print(
    "\nExperience matching result saved to:"
)

print(
    OUTPUT_FILE
)