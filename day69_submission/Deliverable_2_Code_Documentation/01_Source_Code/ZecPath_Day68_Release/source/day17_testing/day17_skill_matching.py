
import os
import sys
import json
import re

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


# ==========================================================
# ZecPath - Day 17 Role-Aware Skill Matching Engine
# Updated: Graphic Designer + Role Validation
# ==========================================================


# ==========================================================
# STEP 1: ROLE-SPECIFIC SKILL DICTIONARIES
# ==========================================================

ROLE_SKILLS = {

    "backend developer": [
        "python", "django", "fastapi", "rest api",
        "sql", "postgresql", "mongodb", "git",
        "docker", "linux", "aws", "redis", "ci/cd"
    ],

    "python developer": [
        "python", "django", "flask", "fastapi",
        "rest api", "sql", "postgresql", "mongodb",
        "git", "docker", "linux", "aws",
        "pytest", "pandas", "numpy"
    ],

    "hr executive": [
        "recruitment", "talent acquisition",
        "employee relations", "human resources",
        "hr management", "onboarding", "payroll",
        "performance management", "communication",
        "interviewing", "candidate screening", "hrms",
        "employee engagement", "training and development"
    ],

    "marketing executive": [
        "marketing", "digital marketing",
        "social media", "seo", "sem",
        "content marketing", "email marketing",
        "market research", "brand management",
        "content creation", "google analytics",
        "advertising", "communication"
    ],

    "fresher python developer": [
        "python", "django", "flask", "fastapi",
        "rest api", "sql", "mysql", "postgresql",
        "mongodb", "git", "html", "css",
        "javascript", "pandas", "numpy"
    ],

    "fresher data analyst": [
        "python", "pandas", "numpy", "sql",
        "excel", "power bi", "tableau",
        "data analysis", "data visualization",
        "statistics", "machine learning"
    ],

    "senior python developer": [
        "python", "django", "fastapi", "flask",
        "rest api", "microservices", "sql",
        "postgresql", "mongodb", "redis",
        "docker", "kubernetes", "aws", "git",
        "ci/cd", "unit testing", "pytest",
        "system design"
    ],

    "senior backend developer": [
        "python", "django", "fastapi", "rest api",
        "microservices", "sql", "postgresql",
        "mongodb", "redis", "docker", "kubernetes",
        "linux", "aws", "git", "ci/cd",
        "unit testing", "system design"
    ],

    # ------------------------------------------------------
    # NEW ROLE: MERN STACK DEVELOPER
    # Based on Day 63 JD001 mandatory and preferred skills
    # ------------------------------------------------------

    "mern stack developer": [
        "react.js",
        "node.js",
        "express.js",
        "mongodb",
        "javascript",
        "html5",
        "css3",
        "bootstrap",
        "rest api",
        "jwt authentication",
        "git",
        "github"
    ],

    # ------------------------------------------------------
    # NEW ROLE: JAVA DEVELOPER
    # Based on Day 63 JD003 mandatory and preferred skills
    # ------------------------------------------------------

    "java developer": [
        "java",
        "spring boot",
        "sql",
        "spring mvc",
        "hibernate",
        "microservices",
        "rest api",
        "mysql",
        "postgresql",
        "oracle",
        "maven",
        "git",
        "jenkins",
        "junit"
    ],

    # ------------------------------------------------------
    # EXISTING ROLE: GRAPHIC DESIGNER
    # ------------------------------------------------------

    "graphic designer": [
        "adobe photoshop",
        "adobe illustrator",
        "figma",
        "canva",
        "graphic design",
        "ui design",
        "branding",
        "video editing",
        "visual communication",
        "layout design",
        "typography"
    ]

}


# ==========================================================
# STEP 2: ROLE ALIASES
# ==========================================================

ROLE_ALIASES = {

    "backend": "backend developer",

    "python": "python developer",

    "hr": "hr executive",

    "marketing": "marketing executive",

    "data analyst": "fresher data analyst",

    "python fresher": "fresher python developer",

    "senior python": "senior python developer",

    "senior backend": "senior backend developer",

    "mern": "mern stack developer",

    "mern stack": "mern stack developer",

    "java": "java developer",

    "graphic": "graphic designer"

}


# ==========================================================
# STEP 3: SKILL ALIASES
# ==========================================================

SKILL_ALIASES = {

    "restful api": "rest api",
    "restful apis": "rest api",
    "rest apis": "rest api",

    "postgres": "postgresql",
    "postgre sql": "postgresql",

    "mongo": "mongodb",
    "mongo db": "mongodb",

    "amazon web services": "aws",

    "continuous integration": "ci/cd",
    "continuous deployment": "ci/cd",

    "photoshop": "adobe photoshop",
    "illustrator": "adobe illustrator",

    "ui/ux design": "ui design",

    "social media marketing": "social media"

}


# ==========================================================
# STEP 4: PROJECT PATHS
# ==========================================================

BASE_DIR = "day17_testing"


# ==========================================================
# STEP 5: TEXT NORMALIZATION
# ==========================================================

def normalize_text(text):

    text = str(text).lower()

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_role(role):

    role = str(role).lower().strip()

    role = role.replace("_", " ")
    role = role.replace("-", " ")

    role = re.sub(r"\s+", " ", role)

    role = ROLE_ALIASES.get(role, role)

    return role


# ==========================================================
# STEP 6: CHECK WHETHER A SKILL EXISTS IN TEXT
# ==========================================================

def contains_skill(text, skill):

    escaped_skill = re.escape(skill)

    pattern = (
        r"(?<!\w)"
        + escaped_skill
        + r"(?!\w)"
    )

    return bool(
        re.search(pattern, text)
    )


# ==========================================================
# STEP 7: EXTRACT SKILLS
# ==========================================================

def extract_skills(text, skill_list):

    found_skills = []

    sorted_skills = sorted(
        skill_list,
        key=len,
        reverse=True
    )

    for skill in sorted_skills:

        if contains_skill(text, skill):

            canonical_skill = SKILL_ALIASES.get(
                skill,
                skill
            )

            if canonical_skill not in found_skills:

                found_skills.append(
                    canonical_skill
                )

    return found_skills


# ==========================================================
# STEP 8: MAIN SKILL MATCHING FUNCTION
# ==========================================================

def main():

    if len(sys.argv) < 3:

        print("\nUsage:")

        print(
            'python -m day17_testing.day17_skill_matching '
            'candidate_006 "Backend Developer"'
        )

        return 1

    candidate_id = sys.argv[1]

    target_role = sys.argv[2]

    role_key = normalize_role(target_role)

    # ------------------------------------------------------
    # Validate role
    # ------------------------------------------------------

    if role_key not in ROLE_SKILLS:

        print("\nERROR: Unsupported target role.")
        print("Target Role:", target_role)

        print("\nAvailable roles:")

        for role in ROLE_SKILLS:

            print("-", role)

        return 1

    skills = ROLE_SKILLS[role_key]

    # ------------------------------------------------------
    # Candidate paths
    # ------------------------------------------------------

    candidate_folder = os.path.join(
        BASE_DIR,
        "results",
        candidate_id
    )

    resume_file = os.path.join(
        candidate_folder,
        "cleaned_resume.txt"
    )

    jd_file = os.path.join(
        candidate_folder,
        "job_description.txt"
    )

    output_file = os.path.join(
        candidate_folder,
        "day17_skill_match.json"
    )

    # ------------------------------------------------------
    # Validate input files
    # ------------------------------------------------------

    if not os.path.isfile(resume_file):

        print("\nError: Resume file not found:")
        print(resume_file)

        return 1

    if not os.path.isfile(jd_file):

        print("\nError: Job description file not found:")
        print(jd_file)

        return 1

    # ------------------------------------------------------
    # Read resume
    # ------------------------------------------------------

    with open(
        resume_file,
        "r",
        encoding="utf-8"
    ) as file:

        resume_text = normalize_text(
            file.read()
        )

    # ------------------------------------------------------
    # Read job description
    # ------------------------------------------------------

    with open(
        jd_file,
        "r",
        encoding="utf-8"
    ) as file:

        job_description = normalize_text(
            file.read()
        )

    # ------------------------------------------------------
    # Extract required skills from JD
    # ------------------------------------------------------

    required_skills = extract_skills(
        job_description,
        skills
    )

    # ------------------------------------------------------
    # Extract candidate skills from resume
    # ------------------------------------------------------

    resume_skills = extract_skills(
        resume_text,
        skills
    )

    # ------------------------------------------------------
    # Validate recognized JD skills
    # ------------------------------------------------------

    if not required_skills:

        print(
            "\nERROR: No recognized role-specific skills "
            "found in the job description."
        )

        print("Target Role:", target_role)
        print("Normalized Role:", role_key)

        return 1

    # ------------------------------------------------------
    # Find matched and missing skills
    # ------------------------------------------------------

    matched_skills = []

    missing_skills = []

    for skill in required_skills:

        if skill in resume_skills:

            matched_skills.append(skill)

        else:

            missing_skills.append(skill)

    # ------------------------------------------------------
    # Calculate score
    # ------------------------------------------------------

    total_required_skills = len(
        required_skills
    )

    total_matched_skills = len(
        matched_skills
    )

    skill_match_score = (

        total_matched_skills
        / total_required_skills

    ) * 100

    skill_match_score = round(
        skill_match_score,
        2
    )

    # ------------------------------------------------------
    # Determine matching status
    # ------------------------------------------------------

    if skill_match_score >= 80:

        matching_status = "Excellent Skill Match"

    elif skill_match_score >= 60:

        matching_status = "Good Skill Match"

    elif skill_match_score >= 40:

        matching_status = "Moderate Skill Match"

    else:

        matching_status = "Low Skill Match"

    # ------------------------------------------------------
    # Display results
    # ------------------------------------------------------

    print("\n" + "=" * 55)

    print("       ZecPath DAY 17 SKILL MATCHING")

    print("=" * 55)

    print("\nCandidate ID :", candidate_id)

    print("Target Role  :", target_role)

    print("Normalized Role:", role_key)

    print(
        "\nSkill Match Score:",
        f"{skill_match_score:.2f}%"
    )

    print("Status:", matching_status)

    # ------------------------------------------------------
    # Required skills
    # ------------------------------------------------------

    print("\n" + "-" * 50)
    print("REQUIRED SKILLS")
    print("-" * 50)

    for skill in required_skills:

        print("•", skill)

    # ------------------------------------------------------
    # Matched skills
    # ------------------------------------------------------

    print("\n" + "-" * 50)
    print("MATCHED SKILLS")
    print("-" * 50)

    if matched_skills:

        for skill in matched_skills:

            print("[MATCHED]", skill)

    else:

        print("No matching skills found.")

    # ------------------------------------------------------
    # Missing skills
    # ------------------------------------------------------

    print("\n" + "-" * 50)
    print("MISSING SKILLS")
    print("-" * 50)

    if missing_skills:

        for skill in missing_skills:

            print("[MISSING]", skill)

    else:

        print("No missing skills.")

    # ------------------------------------------------------
    # JSON output
    # ------------------------------------------------------

    output = {

        "candidate_id": candidate_id,

        "target_role": target_role,

        "normalized_role": role_key,

        "skill_match_score": skill_match_score,

        "matching_status": matching_status,

        "required_skills": required_skills,

        "resume_skills": resume_skills,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "total_required_skills": total_required_skills,

        "total_matched_skills": total_matched_skills,

        "role_dictionary_source": "Day 17 Role-Specific Skill Dictionary"

    }

    # ------------------------------------------------------
    # Save JSON
    # ------------------------------------------------------

    os.makedirs(
        candidate_folder,
        exist_ok=True
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nSkill matching report saved to:")
    print(output_file)

    return 0


# ==========================================================
# STEP 9: EXECUTION ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    sys.exit(main())
