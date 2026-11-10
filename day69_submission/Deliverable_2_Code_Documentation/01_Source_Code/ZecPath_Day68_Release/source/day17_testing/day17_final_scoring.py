import os
import sys
import json


# ==========================================================
# ZecPath - Day 17 Final ATS Scoring Engine
# ==========================================================
#
# Purpose:
# Combine the four ATS components:
#
# 1. Skill Matching          -> 35%
# 2. Experience Relevance    -> 25%
# 3. Education Alignment     -> 15%
# 4. Semantic Similarity     -> 25%
#
# Formula:
#
# Final ATS Score =
#
# (Skill Score × 0.35)
# +
# (Experience Score × 0.25)
# +
# (Education Score × 0.15)
# +
# (Semantic Score × 0.25)
#
#
# Usage:
#
# python -m day17_testing.day17_final_scoring candidate_006 "Backend Developer"
#
# Example:
#
# python -m day17_testing.day17_final_scoring candidate_007 "HR Executive"
#
# ==========================================================


# ==========================================================
# STEP 1: Read Candidate Information
# ==========================================================

if len(sys.argv) < 3:

    print("\nUsage:")

    print(
        'python -m day17_testing.day17_final_scoring '
        'candidate_id "Target Role"'
    )

    print("\nExample:")

    print(
        'python -m day17_testing.day17_final_scoring '
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
# Component JSON Files
# ==========================================================

SKILL_FILE = os.path.join(
    candidate_folder,
    "day17_skill_match.json"
)


SEMANTIC_FILE = os.path.join(
    candidate_folder,
    "day17_semantic_similarity.json"
)


EXPERIENCE_FILE = os.path.join(
    candidate_folder,
    "day17_experience_match.json"
)


EDUCATION_FILE = os.path.join(
    candidate_folder,
    "day17_education_match.json"
)


# ==========================================================
# Final Output File
# ==========================================================

OUTPUT_FILE = os.path.join(
    candidate_folder,
    "day17_final_ats_score.json"
)


# ==========================================================
# STEP 3: Check Component Files
# ==========================================================

required_files = {

    "Skill Matching":
        SKILL_FILE,

    "Semantic Matching":
        SEMANTIC_FILE,

    "Experience Matching":
        EXPERIENCE_FILE,

    "Education Matching":
        EDUCATION_FILE

}


missing_files = []


for component, file_path in required_files.items():

    if not os.path.exists(file_path):

        missing_files.append(
            f"{component}: {file_path}"
        )


if missing_files:

    print(
        "\nError: Required component result files "
        "are missing."
    )

    print(
        "\nMissing files:"
    )

    for file_path in missing_files:

        print(
            "•",
            file_path
        )

    print(
        "\nRun the missing ATS components first."
    )

    sys.exit(1)


# ==========================================================
# STEP 4: Function to Read JSON
# ==========================================================

def read_json(file_path):

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(
                file
            )

    except json.JSONDecodeError:

        print(
            "\nError: Invalid JSON file:"
        )

        print(
            file_path
        )

        sys.exit(1)


# ==========================================================
# STEP 5: Read All Component Results
# ==========================================================

skill_data = read_json(
    SKILL_FILE
)


semantic_data = read_json(
    SEMANTIC_FILE
)


experience_data = read_json(
    EXPERIENCE_FILE
)


education_data = read_json(
    EDUCATION_FILE
)


# ==========================================================
# STEP 6: Extract Component Scores
# ==========================================================

skill_score = float(
    skill_data.get(
        "skill_match_score",
        0
    )
)


semantic_score = float(
    semantic_data.get(
        "semantic_similarity_percentage",
        0
    )
)


experience_score = float(
    experience_data.get(
        "experience_score",
        0
    )
)


education_score = float(
    education_data.get(
        "education_score",
        0
    )
)


# ==========================================================
# STEP 7: Define Weights
# ==========================================================
#
# Total weight = 100%
#
# Skill          = 35%
# Experience     = 25%
# Education      = 15%
# Semantic       = 25%
#
# ==========================================================

SKILL_WEIGHT = 0.35

EXPERIENCE_WEIGHT = 0.25

EDUCATION_WEIGHT = 0.15

SEMANTIC_WEIGHT = 0.25


# ==========================================================
# STEP 8: Calculate Contributions
# ==========================================================

skill_contribution = (
    skill_score
    *
    SKILL_WEIGHT
)


experience_contribution = (
    experience_score
    *
    EXPERIENCE_WEIGHT
)


education_contribution = (
    education_score
    *
    EDUCATION_WEIGHT
)


semantic_contribution = (
    semantic_score
    *
    SEMANTIC_WEIGHT
)


# ==========================================================
# STEP 9: Calculate Final ATS Score
# ==========================================================

final_ats_score = (

    skill_contribution
    +
    experience_contribution
    +
    education_contribution
    +
    semantic_contribution

)


# ==========================================================
# STEP 10: Round Values
# ==========================================================

skill_contribution = round(
    skill_contribution,
    2
)


experience_contribution = round(
    experience_contribution,
    2
)


education_contribution = round(
    education_contribution,
    2
)


semantic_contribution = round(
    semantic_contribution,
    2
)


final_ats_score = round(
    final_ats_score,
    2
)


# ==========================================================
# STEP 11: Determine Matching Status
# ==========================================================

if final_ats_score >= 85:

    matching_status = (
        "Excellent Match"
    )

elif final_ats_score >= 75:

    matching_status = (
        "Strong Match"
    )

elif final_ats_score >= 60:

    matching_status = (
        "Good Match"
    )

elif final_ats_score >= 50:

    matching_status = (
        "Moderate Match"
    )

else:

    matching_status = (
        "Low Match"
    )


# ==========================================================
# STEP 12: Determine Recommendation
# ==========================================================

if final_ats_score >= 80:

    recommendation = (
        "Recommended for Interview"
    )

elif final_ats_score >= 65:

    recommendation = (
        "Can be Considered"
    )

else:

    recommendation = (
        "Not Recommended"
    )


# ==========================================================
# STEP 13: Determine Shortlisting Status
# ==========================================================

if final_ats_score >= 80:

    shortlisting_status = (
        "Shortlisted"
    )

elif final_ats_score >= 60:

    shortlisting_status = (
        "Review"
    )

else:

    shortlisting_status = (
        "Not Shortlisted"
    )


# ==========================================================
# STEP 14: Display Header
# ==========================================================

print(
    "\n=============================================="
)

print(
    "       ZecPath DAY 17 FINAL ATS SCORING"
)

print(
    "==============================================\n"
)


# ==========================================================
# STEP 15: Candidate Information
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
# STEP 16: Display Component Scores
# ==========================================================

print(
    "\n----------------------------------------------"
)

print(
    "ATS COMPONENT SCORES"
)

print(
    "----------------------------------------------"
)


print(
    f"Skill Matching         : "
    f"{skill_score:.2f}%"
)


print(
    f"Experience Relevance   : "
    f"{experience_score:.2f}%"
)


print(
    f"Education Alignment    : "
    f"{education_score:.2f}%"
)


print(
    f"Semantic Similarity    : "
    f"{semantic_score:.2f}%"
)


# ==========================================================
# STEP 17: Display Weights
# ==========================================================

print(
    "\n----------------------------------------------"
)

print(
    "WEIGHTS"
)

print(
    "----------------------------------------------"
)


print(
    "Skill Matching         : 35%"
)


print(
    "Experience Relevance   : 25%"
)


print(
    "Education Alignment    : 15%"
)


print(
    "Semantic Similarity    : 25%"
)


# ==========================================================
# STEP 18: Display Contributions
# ==========================================================

print(
    "\n----------------------------------------------"
)

print(
    "WEIGHTED CONTRIBUTIONS"
)

print(
    "----------------------------------------------"
)


print(
    f"Skill Contribution       : "
    f"{skill_contribution:.2f}"
)


print(
    f"Experience Contribution  : "
    f"{experience_contribution:.2f}"
)


print(
    f"Education Contribution   : "
    f"{education_contribution:.2f}"
)


print(
    f"Semantic Contribution    : "
    f"{semantic_contribution:.2f}"
)


# ==========================================================
# STEP 19: Display Final Score
# ==========================================================

print(
    "\n=============================================="
)

print(
    f"FINAL ATS SCORE: "
    f"{final_ats_score:.2f}%"
)

print(
    "=============================================="
)


# ==========================================================
# STEP 20: Display Matching Status
# ==========================================================

print(
    "\nMatching Status:",
    matching_status
)


print(
    "Shortlisting Status:",
    shortlisting_status
)


print(
    "Recommendation:",
    recommendation
)


# ==========================================================
# STEP 21: Create JSON Output
# ==========================================================

output = {

    "candidate_id":
        candidate_id,

    "target_role":
        target_role,

    "final_ats_score":
        final_ats_score,

    "matching_status":
        matching_status,

    "shortlisting_status":
        shortlisting_status,

    "recommendation":
        recommendation,

    "components": {

        "skill_match": {

            "score":
                skill_score,

            "weight":
                SKILL_WEIGHT,

            "contribution":
                skill_contribution

        },

        "experience_relevance": {

            "score":
                experience_score,

            "weight":
                EXPERIENCE_WEIGHT,

            "contribution":
                experience_contribution

        },

        "education_alignment": {

            "score":
                education_score,

            "weight":
                EDUCATION_WEIGHT,

            "contribution":
                education_contribution

        },

        "semantic_similarity": {

            "score":
                semantic_score,

            "weight":
                SEMANTIC_WEIGHT,

            "contribution":
                semantic_contribution

        }

    }

}


# ==========================================================
# STEP 22: Save Final JSON
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
# STEP 23: Display Output Location
# ==========================================================

print(
    "\nFinal ATS result saved to:"
)

print(
    OUTPUT_FILE
)