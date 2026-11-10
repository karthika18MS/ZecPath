import os
import sys
import json
import re


# ==========================================================
# ZecPath - Day 17 Education Matching Engine
# ==========================================================
#
# Purpose:
# Compare the candidate's education with the education
# requirement mentioned in the job description.
#
# Usage:
#
# python -m day17_testing.day17_education candidate_006 "Backend Developer"
#
# Example:
#
# python -m day17_testing.day17_education candidate_007 "HR Executive"
#
# ==========================================================


# ==========================================================
# STEP 1: Read Candidate Information
# ==========================================================

if len(sys.argv) < 3:

    print("\nUsage:")

    print(
        'python -m day17_testing.day17_education '
        'candidate_id "Target Role"'
    )

    print("\nExample:")

    print(
        'python -m day17_testing.day17_education '
        'candidate_006 "Backend Developer"'
    )

    sys.exit(1)


candidate_id = sys.argv[1]

target_role = sys.argv[2]


# ==========================================================
# STEP 2: Project Paths
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
    "day17_education_match.json"
)


# ==========================================================
# STEP 3: Check Resume
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
# STEP 4: Check Job Description
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

    text = text.lower()

    text = text.replace(
        "–",
        "-"
    )

    text = text.replace(
        "—",
        "-"
    )

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
# STEP 8: Education Degree Dictionary
# ==========================================================
#
# Different ways of writing the same degree are mapped
# to one standard name.
#
# ==========================================================

DEGREE_ALIASES = {

    # ------------------------------------------------------
    # MCA
    # ------------------------------------------------------

    "mca":
        "mca",

    "m.c.a":
        "mca",

    "master of computer applications":
        "mca",

    "master in computer applications":
        "mca",

    # ------------------------------------------------------
    # BCA
    # ------------------------------------------------------

    "bca":
        "bca",

    "b.c.a":
        "bca",

    "bachelor of computer applications":
        "bca",

    "bachelor in computer applications":
        "bca",

    # ------------------------------------------------------
    # B.Tech
    # ------------------------------------------------------

    "b.tech":
        "btech",

    "btech":
        "btech",

    "b. tech":
        "btech",

    "bachelor of technology":
        "btech",

    # ------------------------------------------------------
    # BE
    # ------------------------------------------------------

    "b.e":
        "be",

    "be":
        "be",

    "bachelor of engineering":
        "be",

    # ------------------------------------------------------
    # M.Tech
    # ------------------------------------------------------

    "m.tech":
        "mtech",

    "mtech":
        "mtech",

    "master of technology":
        "mtech",

    # ------------------------------------------------------
    # MSc
    # ------------------------------------------------------

    "msc":
        "msc",

    "m.sc":
        "msc",

    "master of science":
        "msc",

    # ------------------------------------------------------
    # BSc
    # ------------------------------------------------------

    "bsc":
        "bsc",

    "b.sc":
        "bsc",

    "bachelor of science":
        "bsc",

    # ------------------------------------------------------
    # MBA
    # ------------------------------------------------------

    "mba":
        "mba",

    "m.b.a":
        "mba",

    "master of business administration":
        "mba",

    # ------------------------------------------------------
    # MA
    # ------------------------------------------------------

    "ma":
        "ma",

    "m.a":
        "ma",

    "master of arts":
        "ma",

    # ------------------------------------------------------
    # BA
    # ------------------------------------------------------

    "ba":
        "ba",

    "b.a":
        "ba",

    "bachelor of arts":
        "ba"

}


# ==========================================================
# STEP 9: Education Field Keywords
# ==========================================================

EDUCATION_FIELDS = {

    "computer science": [

        "computer science",
        "computer sciences",
        "cs"

    ],

    "computer applications": [

        "computer applications",
        "computer application"

    ],

    "information technology": [

        "information technology",
        "information technologies",
        "it"

    ],

    "business administration": [

        "business administration",
        "business management"

    ],

    "human resources": [

        "human resources",
        "human resource",
        "hr"

    ],

    "marketing": [

        "marketing",
        "digital marketing"

    ],

    "data science": [

        "data science",
        "data analytics",
        "data analysis"

    ],

    "statistics": [

        "statistics",
        "statistical science"

    ],

    "engineering": [

        "engineering",
        "technology"

    ]

}


# ==========================================================
# STEP 10: Extract Candidate Degrees
# ==========================================================

def extract_candidate_degrees(text):

    found_degrees = []

    # Check longer phrases first
    aliases = sorted(
        DEGREE_ALIASES.keys(),
        key=len,
        reverse=True
    )

    for degree in aliases:

        pattern = (
            r"(?<!\w)"
            + re.escape(degree)
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            text
        ):

            standard_degree = (
                DEGREE_ALIASES[
                    degree
                ]
            )

            if standard_degree not in found_degrees:

                found_degrees.append(
                    standard_degree
                )

    return found_degrees


# ==========================================================
# STEP 11: Extract Candidate Education Fields
# ==========================================================

def extract_candidate_fields(text):

    found_fields = []

    for field, keywords in (
        EDUCATION_FIELDS.items()
    ):

        for keyword in keywords:

            pattern = (
                r"(?<!\w)"
                + re.escape(keyword)
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                text
            ):

                if field not in found_fields:

                    found_fields.append(
                        field
                    )

                break

    return found_fields


# ==========================================================
# STEP 12: Extract Candidate Education
# ==========================================================

candidate_degrees = (
    extract_candidate_degrees(
        resume_text
    )
)


candidate_fields = (
    extract_candidate_fields(
        resume_text
    )
)


# ==========================================================
# STEP 13: Extract Education Requirement from JD
# ==========================================================
#
# The function checks common degree names and education
# fields mentioned in the job description.
#
# ==========================================================

required_degrees = (
    extract_candidate_degrees(
        job_description
    )
)


required_fields = (
    extract_candidate_fields(
        job_description
    )
)


# ==========================================================
# STEP 14: Determine Education Match
# ==========================================================

degree_match = False

field_match = False


# ----------------------------------------------------------
# Degree matching
# ----------------------------------------------------------

for candidate_degree in candidate_degrees:

    if candidate_degree in required_degrees:

        degree_match = True

        break


# ----------------------------------------------------------
# Field matching
# ----------------------------------------------------------

for candidate_field in candidate_fields:

    if candidate_field in required_fields:

        field_match = True

        break


# ==========================================================
# STEP 15: Education Scoring Logic
# ==========================================================
#
# 100 = Strong education alignment
# 75  = Degree or field partially matches
# 50  = Related but not directly matching
# 0   = No education information
#
# ==========================================================

if degree_match and field_match:

    education_score = 100.0

    education_status = (
        "Education Fully Aligned"
    )


elif degree_match:

    education_score = 100.0

    education_status = (
        "Degree Requirement Met"
    )


elif field_match:

    education_score = 100.0

    education_status = (
        "Education Field Requirement Met"
    )


elif (
    candidate_degrees
    or
    candidate_fields
):

    education_score = 50.0

    education_status = (
        "Education Partially Aligned"
    )


else:

    education_score = 0.0

    education_status = (
        "Education Information Not Found"
    )


# ==========================================================
# STEP 16: Round Score
# ==========================================================

education_score = round(
    education_score,
    2
)


# ==========================================================
# STEP 17: Display Header
# ==========================================================

print(
    "\n=============================================="
)

print(
    "       ZecPath DAY 17 EDUCATION MATCHING"
)

print(
    "==============================================\n"
)


# ==========================================================
# STEP 18: Candidate Information
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
# STEP 19: Candidate Education
# ==========================================================

print(
    "\nCandidate Degrees:"
)


if candidate_degrees:

    for degree in candidate_degrees:

        print(
            "•",
            degree
        )

else:

    print(
        "No recognized degree found."
    )


print(
    "\nCandidate Education Fields:"
)


if candidate_fields:

    for field in candidate_fields:

        print(
            "•",
            field
        )

else:

    print(
        "No recognized education field found."
    )


# ==========================================================
# STEP 20: JD Education Requirement
# ==========================================================

print(
    "\nJob Description Education Requirements:"
)


print(
    "\nDegrees:"
)


if required_degrees:

    for degree in required_degrees:

        print(
            "•",
            degree
        )

else:

    print(
        "No specific degree detected."
    )


print(
    "\nEducation Fields:"
)


if required_fields:

    for field in required_fields:

        print(
            "•",
            field
        )

else:

    print(
        "No specific education field detected."
    )


# ==========================================================
# STEP 21: Display Match Result
# ==========================================================

print(
    "\nEducation Alignment Score:",
    f"{education_score:.2f}%"
)


print(
    "Education Status:",
    education_status
)


# ==========================================================
# STEP 22: Create JSON Output
# ==========================================================

output = {

    "candidate_id":
        candidate_id,

    "target_role":
        target_role,

    "candidate_education": {

        "degrees":
            candidate_degrees,

        "fields":
            candidate_fields

    },

    "job_description_education": {

        "required_degrees":
            required_degrees,

        "required_fields":
            required_fields

    },

    "degree_match":
        degree_match,

    "field_match":
        field_match,

    "education_score":
        education_score,

    "education_status":
        education_status

}


# ==========================================================
# STEP 23: Save JSON Output
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
# STEP 24: Display Output Location
# ==========================================================

print(
    "\nEducation matching result saved to:"
)

print(
    OUTPUT_FILE
)