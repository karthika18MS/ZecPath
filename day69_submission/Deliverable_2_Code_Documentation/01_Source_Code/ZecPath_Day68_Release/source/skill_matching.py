import re
import json
from pdf_reader import extract_text_from_pdf, normalize_text


# ==========================================================
# FILE PATHS
# ==========================================================

RESUME_PATH = "data/resumes/samplee_resume.pdf"

JD_PATH = "data/job_descriptions/python_developer.txt"

OUTPUT_FILE = "skill_match.json"


# ==========================================================
# REQUIRED SKILLS
# ==========================================================

REQUIRED_SKILLS = [

    "python",

    "object oriented programming",

    "data structures and algorithms",

    "django",

    "django rest framework",

    "fastapi",

    "rest api",

    "api development",

    "microservices",

    "backend development",

    "sql",

    "mysql",

    "postgresql",

    "mongodb",

    "database design",

    "query optimization",

    "orm",

    "unit testing",

    "integration testing",

    "pytest",

    "debugging",

    "error handling",

    "logging",

    "code optimization",

    "git",

    "github",

    "agile",

    "scrum",

    "code review",

    "clean code",

    "problem solving",

    "communication",

    "linux",

    "command line",

    "environment variables",

    "application deployment"

]


# ==========================================================
# PREFERRED SKILLS
# ==========================================================

PREFERRED_SKILLS = [

    "docker",

    "kubernetes",

    "aws",

    "ci/cd",

    "jenkins",

    "github actions",

    "redis",

    "celery",

    "rabbitmq",

    "nginx",

    "terraform",

    "jwt",

    "oauth 2.0",

    "swagger",

    "openapi",

    "system design",

    "cloud computing"

]


# ==========================================================
# SKILL ALIASES
# ==========================================================
#
# Different terms can represent the same skill.
# ==========================================================

SKILL_ALIASES = {

    # Python / OOP

    "oop":
        "object oriented programming",

    "object-oriented programming":
        "object oriented programming",

    "object oriented programming":
        "object oriented programming",


    # REST API

    "restful api":
        "rest api",

    "restful apis":
        "rest api",

    "rest apis":
        "rest api",

    "rest api":
        "rest api",


    # Django

    "django rest framework":
        "django rest framework",

    "drf":
        "django rest framework",


    # MongoDB

    "mongo":
        "mongodb",

    "mongo db":
        "mongodb",


    # MySQL

    "mysql database":
        "mysql",


    # PostgreSQL

    "postgres":
        "postgresql",

    "postgres database":
        "postgresql",


    # Git

    "git version control":
        "git",

    "github":
        "github",


    # CI/CD

    "continuous integration":
        "ci/cd",

    "continuous deployment":
        "ci/cd",

    "continuous integration and deployment":
        "ci/cd",


    # AWS

    "amazon web services":
        "aws",


    # API documentation

    "swagger ui":
        "swagger",

    "open api":
        "openapi"

}


# ==========================================================
# RELATED SKILLS
# ==========================================================
#
# If the resume contains one skill, it can provide partial
# evidence for a related skill.
# ==========================================================

RELATED_SKILLS = {

    "backend development": [

        "python",

        "django",

        "fastapi",

        "rest api",

        "django rest framework"

    ],

    "api development": [

        "rest api",

        "django rest framework",

        "fastapi",

        "django"

    ],

    "object oriented programming": [

        "python",

        "java",

        "c++",

        "oop"

    ],

    "database design": [

        "sql",

        "mysql",

        "postgresql",

        "mongodb",

        "database"

    ],

    "orm": [

        "django",

        "django orm",

        "sqlalchemy"

    ],

    "django orm": [

        "django",

        "orm"

    ],

    "debugging": [

        "debug",

        "bug",

        "troubleshooting",

        "error handling"

    ],

    "code optimization": [

        "optimization",

        "performance",

        "performance optimization",

        "query optimization"

    ],

    "command line": [

        "linux",

        "terminal",

        "shell"

    ],

    "application deployment": [

        "docker",

        "aws",

        "linux",

        "deployment",

        "ci/cd"

    ],

    "cloud computing": [

        "aws",

        "docker",

        "kubernetes"

    ],

    "system design": [

        "microservices",

        "backend",

        "api",

        "scalable"

    ]

}


# ==========================================================
# READ RESUME
# ==========================================================

def read_resume():

    try:

        resume = extract_text_from_pdf(
            RESUME_PATH
        )

        if not resume:

            print(
                "Error: Resume text could not be extracted."
            )

            return ""

        return normalize_text(resume)

    except Exception as e:

        print(
            "Error reading resume:"
        )

        print(e)

        return ""


# ==========================================================
# READ JOB DESCRIPTION
# ==========================================================

def read_job_description():

    try:

        with open(
            JD_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            job_description = file.read()

        return normalize_text(
            job_description
        )

    except FileNotFoundError:

        print(
            "Error: Job description not found."
        )

        return ""


# ==========================================================
# NORMALIZE SKILL
# ==========================================================

def normalize_skill(skill):

    skill = skill.lower().strip()

    skill = skill.replace(
        "-",
        " "
    )

    skill = re.sub(
        r"\s+",
        " ",
        skill
    )

    if skill in SKILL_ALIASES:

        return SKILL_ALIASES[skill]

    return skill


# ==========================================================
# CHECK DIRECT SKILL MATCH
# ==========================================================

def direct_skill_match(
    resume_text,
    skill
):

    skill = normalize_skill(
        skill
    )

    if " " in skill:

        return skill in resume_text

    pattern = (
        r"\b"
        + re.escape(skill)
        + r"\b"
    )

    return bool(
        re.search(
            pattern,
            resume_text
        )
    )


# ==========================================================
# CHECK RELATED SKILL MATCH
# ==========================================================

def related_skill_match(
    resume_text,
    skill
):

    skill = normalize_skill(
        skill
    )

    if skill not in RELATED_SKILLS:

        return False

    related_terms = (
        RELATED_SKILLS[skill]
    )

    matched_count = 0

    for related in related_terms:

        if direct_skill_match(
            resume_text,
            related
        ):

            matched_count += 1

    # At least one related skill
    # gives partial evidence.

    return matched_count > 0


# ==========================================================
# FIND SKILL MATCH
# ==========================================================

def check_skill(
    resume_text,
    skill
):

    # Direct match
    if direct_skill_match(
        resume_text,
        skill
    ):

        return "direct"

    # Related match
    if related_skill_match(
        resume_text,
        skill
    ):

        return "related"

    return "missing"


# ==========================================================
# MATCH SKILLS
# ==========================================================

def find_matching_skills(
    resume_text,
    skills
):

    direct_matches = []

    related_matches = []

    missing_skills = []

    for skill in skills:

        result = check_skill(
            resume_text,
            skill
        )

        normalized_skill = normalize_skill(
            skill
        )

        if result == "direct":

            direct_matches.append(
                normalized_skill
            )

        elif result == "related":

            related_matches.append(
                normalized_skill
            )

        else:

            missing_skills.append(
                normalized_skill
            )

    return (
        direct_matches,
        related_matches,
        missing_skills
    )


# ==========================================================
# CALCULATE REQUIRED SKILL SCORE
# ==========================================================

def calculate_required_score(
    direct_matches,
    related_matches,
    total_skills
):

    if total_skills == 0:

        return 0

    # Direct match = full credit
    direct_points = (
        len(direct_matches)
    )

    # Related match = 50% credit
    related_points = (
        len(related_matches)
        * 0.50
    )

    score = (

        (
            direct_points
            +
            related_points
        )
        /
        total_skills

    ) * 100

    return round(
        score,
        2
    )


# ==========================================================
# CALCULATE PREFERRED SCORE
# ==========================================================

def calculate_preferred_score(
    direct_matches,
    related_matches,
    total_skills
):

    if total_skills == 0:

        return 0

    direct_points = (
        len(direct_matches)
    )

    related_points = (
        len(related_matches)
        * 0.50
    )

    score = (

        (
            direct_points
            +
            related_points
        )
        /
        total_skills

    ) * 100

    return round(
        score,
        2
    )


# ==========================================================
# CALCULATE OVERALL SKILL SCORE
# ==========================================================

def calculate_overall_score(
    required_score,
    preferred_score
):

    # Required skills = 85%
    # Preferred skills = 15%

    overall_score = (

        required_score * 0.85

        +

        preferred_score * 0.15

    )

    return round(
        overall_score,
        2
    )


# ==========================================================
# MAIN PROGRAM
# ==========================================================

if __name__ == "__main__":

    print("\n===================================")
    print("ZecPath SKILL MATCHING ENGINE")
    print("===================================\n")


    # ------------------------------------------------------
    # Read Resume
    # ------------------------------------------------------

    resume_text = read_resume()

    if not resume_text:

        exit()


    # ------------------------------------------------------
    # Read JD
    # ------------------------------------------------------

    job_description = (
        read_job_description()
    )

    if not job_description:

        exit()


    # ------------------------------------------------------
    # Required Skills
    # ------------------------------------------------------

    (
        required_direct,
        required_related,
        required_missing

    ) = find_matching_skills(

        resume_text,

        REQUIRED_SKILLS

    )


    # ------------------------------------------------------
    # Preferred Skills
    # ------------------------------------------------------

    (
        preferred_direct,
        preferred_related,
        preferred_missing

    ) = find_matching_skills(

        resume_text,

        PREFERRED_SKILLS

    )


    # ------------------------------------------------------
    # Calculate Scores
    # ------------------------------------------------------

    required_score = (
        calculate_required_score(

            required_direct,

            required_related,

            len(REQUIRED_SKILLS)

        )
    )


    preferred_score = (
        calculate_preferred_score(

            preferred_direct,

            preferred_related,

            len(PREFERRED_SKILLS)

        )
    )


    overall_score = (
        calculate_overall_score(

            required_score,

            preferred_score

        )
    )


    # ------------------------------------------------------
    # Display Required Skills
    # ------------------------------------------------------

    print(
        "Required Skills - Direct Matches:"
    )

    for skill in required_direct:

        print(
            "✓",
            skill
        )


    print(
        "\nRequired Skills - Related Matches:"
    )

    for skill in required_related:

        print(
            "≈",
            skill
        )


    print(
        "\nRequired Skills Missing:"
    )

    for skill in required_missing:

        print(
            "✗",
            skill
        )


    # ------------------------------------------------------
    # Display Preferred Skills
    # ------------------------------------------------------

    print(
        "\nPreferred Skills - Direct Matches:"
    )

    for skill in preferred_direct:

        print(
            "✓",
            skill
        )


    print(
        "\nPreferred Skills - Related Matches:"
    )

    for skill in preferred_related:

        print(
            "≈",
            skill
        )


    print(
        "\nPreferred Skills Missing:"
    )

    for skill in preferred_missing:

        print(
            "✗",
            skill
        )


    # ------------------------------------------------------
    # Display Scores
    # ------------------------------------------------------

    print(
        "\nRequired Skill Score :",
        required_score,
        "%"
    )

    print(
        "Preferred Skill Score:",
        preferred_score,
        "%"
    )

    print(
        "Overall Skill Score  :",
        overall_score,
        "%"
    )


    # ------------------------------------------------------
    # Save Result
    # ------------------------------------------------------

    output = {

        "candidate_id":
            "CAND001",

        "target_role":
            "Python Developer",

        "required_skills": {

            "total":
                len(REQUIRED_SKILLS),

            "direct_matches":
                required_direct,

            "related_matches":
                required_related,

            "missing":
                required_missing,

            "match_percentage":
                required_score

        },

        "preferred_skills": {

            "total":
                len(PREFERRED_SKILLS),

            "direct_matches":
                preferred_direct,

            "related_matches":
                preferred_related,

            "missing":
                preferred_missing,

            "match_percentage":
                preferred_score

        },

        "overall_skill_score":
            overall_score

    }


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


    print(
        "\nSkill matching result saved to",
        OUTPUT_FILE
    )