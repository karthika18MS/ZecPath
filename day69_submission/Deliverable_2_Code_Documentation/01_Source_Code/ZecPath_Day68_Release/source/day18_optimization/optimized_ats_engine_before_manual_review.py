import os
import sys
import json
import time
import subprocess
import gc


# ==========================================================
# ZecPath DAY 18
# OPTIMIZED ATS ENGINE
# ==========================================================


# ==========================================================
# PROJECT ROOT
# ==========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ==========================================================
# DAY 18 MODULES
# ==========================================================

from parsers.noisy_text_cleaner import (
    clean_noisy_resume_text
)

from parsers.entity_detector import (
    extract_entities
)


# ==========================================================
# ATS WEIGHTS
# ==========================================================

SKILL_WEIGHT = 0.35
EXPERIENCE_WEIGHT = 0.25
EDUCATION_WEIGHT = 0.15
SEMANTIC_WEIGHT = 0.25


# ==========================================================
# PATH FUNCTIONS
# ==========================================================

def get_resume_path(candidate_id):

    return os.path.join(
        PROJECT_ROOT,
        "day17_testing",
        "resumes",
        f"{candidate_id}.docx"
    )


def get_job_description_path(job_description_file):

    return os.path.join(
        PROJECT_ROOT,
        "day17_testing",
        "job_descriptions",
        job_description_file
    )


def get_day17_result_directory(candidate_id):

    return os.path.join(
        PROJECT_ROOT,
        "day17_testing",
        "results",
        candidate_id
    )


def get_day18_result_directory(candidate_id):

    result_dir = os.path.join(
        PROJECT_ROOT,
        "day18_optimization",
        "results",
        candidate_id
    )

    os.makedirs(
        result_dir,
        exist_ok=True
    )

    return result_dir


# ==========================================================
# DOCX TEXT EXTRACTION
# ==========================================================

def extract_docx_text(file_path):

    from docx import Document

    document = Document(
        file_path
    )

    paragraphs = []

    # ------------------------------------------------------
    # Normal paragraphs
    # ------------------------------------------------------

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(
                text
            )

    # ------------------------------------------------------
    # Tables
    # ------------------------------------------------------

    for table in document.tables:

        for row in table.rows:

            for cell in row.cells:

                text = cell.text.strip()

                if text:
                    paragraphs.append(
                        text
                    )

    return "\n".join(
        paragraphs
    )


# ==========================================================
# TEXT FILE LOADER
# ==========================================================

def load_text(file_path):

    if not os.path.exists(
        file_path
    ):

        raise FileNotFoundError(
            f"File not found:\n{file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ==========================================================
# SKILL NORMALIZATION
# ==========================================================

def normalize_skill(skill):

    skill = (
        str(skill)
        .lower()
        .strip()
    )

    aliases = {

        "fast api":
            "fastapi",

        "restful api":
            "rest api",

        "restful apis":
            "rest api",

        "rest apis":
            "rest api",

        "mongo db":
            "mongodb",

        "postgres":
            "postgresql",

        "node js":
            "node.js",

        "nodejs":
            "node.js",

        "ci / cd":
            "ci/cd",

        "cicd":
            "ci/cd",

        "amazon web services":
            "aws"
    }

    return aliases.get(
        skill,
        skill
    )


# ==========================================================
# RECURSIVE JSON VALUE FINDER
# ==========================================================

def find_value_recursive(
    data,
    possible_keys
):

    if isinstance(
        data,
        dict
    ):

        for key, value in data.items():

            normalized_key = (
                str(key)
                .lower()
                .replace("-", "_")
                .replace(" ", "_")
            )

            if normalized_key in possible_keys:

                return value

        for value in data.values():

            result = find_value_recursive(
                value,
                possible_keys
            )

            if result is not None:

                return result

    elif isinstance(
        data,
        list
    ):

        for item in data:

            result = find_value_recursive(
                item,
                possible_keys
            )

            if result is not None:

                return result

    return None


# ==========================================================
# DAY 17 SKILL MATCHING
# ==========================================================
#
# We reuse the validated Day 17 skill matcher so that
# Day 18 does not unintentionally change the original
# skill-matching behavior.
# ==========================================================

def run_day17_skill_matching(
    candidate_id,
    target_role
):

    command = [

        sys.executable,

        "-m",

        "day17_testing.day17_skill_matching",

        candidate_id,

        target_role
    ]

    process = subprocess.run(

        command,

        cwd=PROJECT_ROOT,

        capture_output=True,

        text=True
    )

    if process.returncode != 0:

        raise RuntimeError(
            "Day 17 skill matching failed.\n\n"
            + process.stdout
            + "\n"
            + process.stderr
        )

    result_path = os.path.join(

        PROJECT_ROOT,

        "day17_testing",

        "results",

        candidate_id,

        "day17_skill_match.json"
    )

    if not os.path.exists(
        result_path
    ):

        raise FileNotFoundError(
            "Day 17 skill matching result "
            "was not created:\n"
            + result_path
        )

    with open(
        result_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file
        )


# ==========================================================
# CONVERT DAY 17 SKILL RESULT
# ==========================================================

def convert_day17_skill_result(
    raw_result
):

    score = find_value_recursive(

        raw_result,

        {
            "skill_match_score",
            "skill_score",
            "score"
        }
    )

    if score is None:

        raise ValueError(
            "Could not find skill score in "
            "Day 17 skill result."
        )

    required_skills = find_value_recursive(

        raw_result,

        {
            "required_skills",
            "required_skill"
        }
    )

    matched_skills = find_value_recursive(

        raw_result,

        {
            "matched_skills",
            "matched_skill"
        }
    )

    missing_skills = find_value_recursive(

        raw_result,

        {
            "missing_skills",
            "missing_skill"
        }
    )

    if not isinstance(
        required_skills,
        list
    ):

        required_skills = []

    if not isinstance(
        matched_skills,
        list
    ):

        matched_skills = []

    if not isinstance(
        missing_skills,
        list
    ):

        missing_skills = []

    required_skills = sorted(
        {
            normalize_skill(skill)
            for skill in required_skills
        }
    )

    matched_skills = sorted(
        {
            normalize_skill(skill)
            for skill in matched_skills
        }
    )

    missing_skills = sorted(
        {
            normalize_skill(skill)
            for skill in missing_skills
        }
    )

    return {

        "score":
            round(
                float(score),
                2
            ),

        "required_skills":
            required_skills,

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills,

        "total_required_skills":
            len(required_skills),

        "total_matched_skills":
            len(matched_skills),

        "source":
            "Day 17 validated skill matcher"
    }


# ==========================================================
# EXPERIENCE RANGE EXTRACTION
# ==========================================================

def extract_experience_range(
    job_description
):
    """
    Extract an experience requirement from a job description.

    Supported examples:
    - 1-3 years
    - 1 to 3 years
    - 5+ years of experience
    - 5+ years of professional backend development experience
    - Minimum 3 years of experience
    - At least 5 years of relevant work experience

    Returns (minimum_years, maximum_years). A None maximum means
    that the requirement has a minimum but no stated upper bound.
    Returns (None, None) when no explicit experience requirement is found.
    """

    import re

    text = str(job_description or "")

    # ------------------------------------------------------
    # 1. Explicit ranges: 1-3 years, 1 to 3 years, 3–5 years
    # ------------------------------------------------------

    range_patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:-|–|—|to)\s*"
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\b"
    ]

    for pattern in range_patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            minimum = float(match.group(1))
            maximum = float(match.group(2))

            if maximum < minimum:
                minimum, maximum = maximum, minimum

            return minimum, maximum

    # ------------------------------------------------------
    # 2. Explicit minimum phrases:
    #    Minimum 3 years of experience
    #    Minimum of 3 years' experience
    #    At least 5 years of relevant experience
    # ------------------------------------------------------

    explicit_minimum_patterns = [
        r"\bminimum(?:\s+of)?\s+"
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\b['’]?"
        r"(?:\s+(?:of\s+)?(?:(?!experience\b)[\w&/-]+\s+){0,8})?\s*experience\b",

        r"\bat\s+least\s+"
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\b['’]?"
        r"(?:\s+(?:of\s+)?(?:(?!experience\b)[\w&/-]+\s+){0,8})?\s*experience\b",

        r"\b(\d+(?:\.\d+)?)\s*\+\s*years?\b['’]?"
        r"(?:\s+(?:of\s+)?(?:(?!experience\b)[\w&/-]+\s+){0,8})?\s*experience\b"
    ]

    for pattern in explicit_minimum_patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            return float(match.group(1)), None

    return None, None


# ==========================================================
# EXPERIENCE MATCHING
# ==========================================================

def calculate_experience_match(resume_entities, job_description):
    """
    Compare candidate experience with the JD requirement.

    A missing JD requirement is not treated as a 100% match.
    Missing candidate evidence is not treated as zero experience.
    Both cases return score=None so the final scorer can exclude
    the component and normalize the remaining weights.
    """

    candidate_experience = resume_entities.get("experience_years")

    minimum_experience, maximum_experience = extract_experience_range(
        job_description
    )

    # No experience requirement in the job description.
    if minimum_experience is None and maximum_experience is None:
        return {
            "score": None,
            "candidate_experience_years": candidate_experience,
            "minimum_required_years": None,
            "maximum_required_years": None,
            "is_applicable": False,
            "status": "Not Applicable - Experience Requirement Not Specified"
        }

    # The JD has a requirement, but candidate experience is unavailable.
    if candidate_experience is None:
        return {
            "score": None,
            "candidate_experience_years": None,
            "minimum_required_years": minimum_experience,
            "maximum_required_years": maximum_experience,
            "is_applicable": True,
            "status": "Needs Review - Candidate Experience Not Detected"
        }

    # Minimum-only requirement.
    if maximum_experience is None:
        if candidate_experience >= minimum_experience:
            score = 100.0
            status = "Experience Meets Requirement"
        else:
            score = min(
                100.0,
                (candidate_experience / minimum_experience) * 100
            )
            status = "Experience Below Requirement"

        return {
            "score": round(score, 2),
            "candidate_experience_years": candidate_experience,
            "minimum_required_years": minimum_experience,
            "maximum_required_years": None,
            "is_applicable": True,
            "status": status
        }

    # Candidate is within the specified range.
    if minimum_experience <= candidate_experience <= maximum_experience:
        return {
            "score": 100.0,
            "candidate_experience_years": candidate_experience,
            "minimum_required_years": minimum_experience,
            "maximum_required_years": maximum_experience,
            "is_applicable": True,
            "status": "Experience Fully Meets Requirement"
        }

    # Candidate is below the minimum.
    if candidate_experience < minimum_experience:
        score = min(
            100.0,
            (candidate_experience / minimum_experience) * 100
        )

        return {
            "score": round(score, 2),
            "candidate_experience_years": candidate_experience,
            "minimum_required_years": minimum_experience,
            "maximum_required_years": maximum_experience,
            "is_applicable": True,
            "status": "Experience Below Requirement"
        }

    # Candidate exceeds the stated maximum.
    # Existing policy is preserved: exceeding the range receives 100%.
    return {
        "score": 100.0,
        "candidate_experience_years": candidate_experience,
        "minimum_required_years": minimum_experience,
        "maximum_required_years": maximum_experience,
        "is_applicable": True,
        "status": "Experience Exceeds Requirement"
    }


# ==========================================================
# EDUCATION FIELDS
# ==========================================================

EDUCATION_FIELDS = [

    "computer science",
    "computer applications",
    "information technology",
    "engineering",

    "business administration",
    "human resources",
    "marketing",
    "management",

    "finance",
    "accounting",

    "data science",
    "statistics",
    "mathematics"
]


# ==========================================================
# EDUCATION FIELD DETECTION
# ==========================================================

def detect_education_fields(
    text
):

    text_lower = (
        text.lower()
    )

    detected = set()

    for field in EDUCATION_FIELDS:

        if field in text_lower:

            detected.add(
                field
            )

    return sorted(
        detected
    )


# ==========================================================
# EDUCATION MATCHING
# ==========================================================

def calculate_education_match(
    resume_entities,
    resume_text,
    job_description
):
    """
    Day 17-compatible education scoring.

    Rules:
    - Degree match OR education-field match -> 100%
    - Candidate has education information but no match -> 50%
    - No candidate education information -> 0%

    This preserves the validated Day 17 behavior, including
    Candidate 013 where "marketing" is present in the resume
    but does not match the Python Developer JD fields.
    """

    candidate_degrees = resume_entities.get(
        "degrees",
        []
    )

    candidate_fields = resume_entities.get(
        "education_fields",
        []
    )

    # Some entity-detector versions may not expose education
    # fields directly. Fall back to the text detector.
    if not isinstance(candidate_fields, list):
        candidate_fields = []

    if not candidate_fields:
        candidate_fields = detect_education_fields(
            resume_text
        )

    # Detect JD education fields directly from the JD text.
    # This avoids depending on whether the entity detector
    # exposes a separate education_fields key for JDs.
    jd_fields = detect_education_fields(
        job_description
    )

    # Degrees are already supplied by the entity detector.
    # Normalize them safely for comparison.
    candidate_degrees = [
        str(degree).lower().strip()
        for degree in candidate_degrees
        if str(degree).strip()
    ]

    jd_degrees = []

    # If the JD entity detector exposes degrees, use them.
    # Otherwise the list remains empty, which is correct for
    # JDs such as Candidate 013's Python Developer JD.
    try:
        jd_entities = extract_entities(
            job_description
        )
        detected_jd_degrees = jd_entities.get(
            "degrees",
            []
        )

        if isinstance(
            detected_jd_degrees,
            list
        ):
            jd_degrees = [
                str(degree).lower().strip()
                for degree in detected_jd_degrees
                if str(degree).strip()
            ]
    except Exception:
        jd_degrees = []

    candidate_fields = [
        str(field).lower().strip()
        for field in candidate_fields
        if str(field).strip()
    ]

    jd_fields = [
        str(field).lower().strip()
        for field in jd_fields
        if str(field).strip()
    ]

    degree_match = any(
        degree in jd_degrees
        for degree in candidate_degrees
    )

    field_match = any(
        field in jd_fields
        for field in candidate_fields
    )

    # ------------------------------------------------------
    # EXACT DAY 17 SCORING BEHAVIOR
    # ------------------------------------------------------

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

    elif candidate_degrees or candidate_fields:

        # Important:
        # Candidate 013 reaches this branch.
        #
        # Candidate has:
        #   degree = none
        #   field  = marketing
        #
        # JD fields:
        #   computer science
        #   computer applications
        #   information technology
        #   engineering
        #
        # Therefore Day 17 gives 50%.
        education_score = 50.0

        education_status = (
            "Education Partially Aligned"
        )

    else:

        education_score = 0.0

        education_status = (
            "Education Information Not Found"
        )

    return {

        "score":
            round(
                education_score,
                2
            ),

        "candidate_degrees":
            candidate_degrees,

        "candidate_fields":
            candidate_fields,

        "required_degrees":
            jd_degrees,

        "required_fields":
            jd_fields,

        "degree_match":
            degree_match,

        "field_match":
            field_match,

        "status":
            education_status
    }


# ==========================================================
# VALIDATED DAY 17 SEMANTIC RESUME
# ==========================================================
#
# IMPORTANT DAY 18 COMPATIBILITY FIX
#
# Day 17 semantic matching uses:
#
# day17_testing/results/<candidate>/cleaned_resume.txt
#
# We verified that fresh Day 18 DOCX extraction followed by
# Day 18 cleaning can produce slightly different text.
#
# Example:
#
# Day 18 cleaned text : 1076 characters
# Day 17 semantic text: 1074 characters
#
# Therefore, Day 18 uses the validated Day 17 semantic
# representation specifically for semantic scoring.
#
# The Day 18 cleaned text is STILL used for:
#
# - Entity detection
# - Experience matching
# - Education matching
# - Day 18 noisy-resume handling
#
# This prevents a semantic-score regression while allowing
# Day 18 extraction/cleaning optimization to remain active.
# ==========================================================

def get_validated_semantic_resume_text(
    candidate_id
):

    day17_result_directory = (
        get_day17_result_directory(
            candidate_id
        )
    )

    semantic_resume_path = os.path.join(
        day17_result_directory,
        "cleaned_resume.txt"
    )

    if not os.path.exists(
        semantic_resume_path
    ):

        raise FileNotFoundError(

            "Validated Day 17 semantic "
            "resume was not found:\n"
            + semantic_resume_path
            + "\n\n"
            "Run the Day 17 testing pipeline "
            "for this candidate first."
        )

    with open(
        semantic_resume_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ==========================================================
# SEMANTIC MATCHING
# ==========================================================
#
# Uses models.semantic_model.
#
# That module:
#
# - Loads all-MiniLM-L6-v2
# - Reuses the model within the current Python process
# - Uses Day 17-compatible text normalization
# - Uses model.encode()
# - Uses sklearn cosine_similarity()
#
# No normalize_embeddings=True is used.
# ==========================================================

def calculate_semantic_similarity(
    resume_text,
    job_description
):
    """Calculate semantic similarity and measure cached-model access.

    The existing semantic calculation and Day 17-compatible inputs remain
    unchanged. This timing measures access to the model in this process;
    initial model loading is measured by the batch runner.
    """
    from models.semantic_model import (
        calculate_semantic_similarity as semantic_calculator,
        get_semantic_model,
    )

    model_access_start = time.perf_counter()
    get_semantic_model()
    model_access_time = time.perf_counter() - model_access_start

    semantic_result = semantic_calculator(
        resume_text,
        job_description,
    )

    # Keep the original score fields; add diagnostic timing only.
    semantic_result["model_access_time_seconds"] = round(
        model_access_time, 6
    )
    return semantic_result


# ==========================================================
# MATCHING STATUS
# ==========================================================

def get_matching_status(
    final_score
):

    if final_score >= 85:

        return (
            "Excellent Match"
        )

    if final_score >= 70:

        return (
            "Good Match"
        )

    if final_score >= 50:

        return (
            "Moderate Match"
        )

    return (
        "Low Match"
    )


# ==========================================================
# SHORTLISTING STATUS
# ==========================================================

def get_shortlisting_status(
    final_score
):

    if final_score >= 70:

        return (
            "Shortlisted"
        )

    return (
        "Not Shortlisted"
    )


# ==========================================================
# RECOMMENDATION
# ==========================================================

def get_recommendation(
    final_score
):

    if final_score >= 70:

        return (
            "Recommended for Interview"
        )

    return (
        "Not Recommended"
    )


# ==========================================================
# FINAL ATS SCORE
# ==========================================================

def calculate_final_score(
    skill_score,
    experience_score,
    education_score,
    semantic_score
):
    """
    Calculate ATS score using the configured base weights.

    Components with unavailable scores (None) are excluded.
    The remaining component weights are normalized to total 1.0.
    """

    base_weights = {
        "skill_matching": SKILL_WEIGHT,
        "experience_relevance": EXPERIENCE_WEIGHT,
        "education_alignment": EDUCATION_WEIGHT,
        "semantic_similarity": SEMANTIC_WEIGHT
    }

    component_scores = {
        "skill_matching": skill_score,
        "experience_relevance": experience_score,
        "education_alignment": education_score,
        "semantic_similarity": semantic_score
    }

    available_components = {
        name: score
        for name, score in component_scores.items()
        if score is not None
    }

    if not available_components:
        raise ValueError(
            "Cannot calculate ATS score: no component scores are available."
        )

    available_weight_total = sum(
        base_weights[name]
        for name in available_components
    )

    if available_weight_total <= 0:
        raise ValueError(
            "Invalid ATS weights: available weight total must be positive."
        )

    effective_weights = {
        name: (
            base_weights[name] / available_weight_total
            if name in available_components
            else 0.0
        )
        for name in base_weights
    }

    contributions = {
        name: (
            score * effective_weights[name]
            if score is not None
            else 0.0
        )
        for name, score in component_scores.items()
    }

    final_score = sum(contributions.values())

    return {
        "final_score": round(final_score, 2),
        "skill_contribution": round(contributions["skill_matching"], 2),
        "experience_contribution": round(contributions["experience_relevance"], 2),
        "education_contribution": round(contributions["education_alignment"], 2),
        "semantic_contribution": round(contributions["semantic_similarity"], 2),
        "effective_weights": {
            name: round(weight, 6)
            for name, weight in effective_weights.items()
        },
        "excluded_components": [
            name
            for name, score in component_scores.items()
            if score is None
        ]
    }


# ==========================================================
# SAVE JSON
# ==========================================================

def save_json(
    data,
    file_path
):

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ==========================================================
# MAIN OPTIMIZED ATS PIPELINE
# ==========================================================

def run_optimized_ats(
    candidate_id,
    target_role,
    job_description_file
):

    pipeline_start = (
        time.perf_counter()
    )

    print()

    print(
        "=" * 70
    )

    print(
        "       ZecPath DAY 18 OPTIMIZED ATS ENGINE"
    )

    print(
        "=" * 70
    )

    print()

    print(
        f"Candidate ID : {candidate_id}"
    )

    print(
        f"Target Role  : {target_role}"
    )

    # ======================================================
    # PATHS
    # ======================================================

    resume_path = get_resume_path(
        candidate_id
    )

    jd_path = get_job_description_path(
        job_description_file
    )

    result_dir = get_day18_result_directory(
        candidate_id
    )

    # ======================================================
    # VALIDATE INPUT FILES
    # ======================================================

    if not os.path.exists(
        resume_path
    ):

        raise FileNotFoundError(
            f"Resume not found:\n"
            f"{resume_path}"
        )

    if not os.path.exists(
        jd_path
    ):

        raise FileNotFoundError(
            f"Job description not found:\n"
            f"{jd_path}"
        )

    # ======================================================
    # STEP 1
    # OPTIMIZED TEXT EXTRACTION
    # ======================================================

    print()

    print(
        "--------------------------------------------------"
    )

    print(
        "STEP 1: OPTIMIZED TEXT EXTRACTION"
    )

    print(
        "--------------------------------------------------"
    )

    extraction_start = (
        time.perf_counter()
    )

    raw_resume_text = (
        extract_docx_text(
            resume_path
        )
    )

    extraction_time = (
        time.perf_counter()
        - extraction_start
    )

    print(
        f"Extraction Time: "
        f"{extraction_time:.6f} seconds"
    )

    print(
        f"Characters: "
        f"{len(raw_resume_text)}"
    )

    print(
        f"Words: "
        f"{len(raw_resume_text.split())}"
    )

    # ======================================================
    # STEP 2
    # NOISY TEXT CLEANING
    # ======================================================

    print()

    print(
        "--------------------------------------------------"
    )

    print(
        "STEP 2: NOISY TEXT CLEANING"
    )

    print(
        "--------------------------------------------------"
    )

    cleaning_start = (
        time.perf_counter()
    )

    cleaned_resume_text = (
        clean_noisy_resume_text(
            raw_resume_text
        )
    )

    cleaning_time = (
        time.perf_counter()
        - cleaning_start
    )

    print(
        f"Cleaning Time: "
        f"{cleaning_time:.6f} seconds"
    )

    # ------------------------------------------------------
    # Save Day 18 cleaned resume
    # ------------------------------------------------------

    cleaned_resume_output = os.path.join(
        result_dir,
        "cleaned_resume.txt"
    )

    with open(
        cleaned_resume_output,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            cleaned_resume_text
        )

    # ======================================================
    # LOAD JOB DESCRIPTION
    # ======================================================

    job_description = load_text(
        jd_path
    )

    # ======================================================
    # STEP 3
    # ENTITY DETECTION
    # ======================================================

    print()

    print(
        "--------------------------------------------------"
    )

    print(
        "STEP 3: ENTITY DETECTION"
    )

    print(
        "--------------------------------------------------"
    )

    entity_start = (
        time.perf_counter()
    )

    resume_entities = (
        extract_entities(
            cleaned_resume_text
        )
    )

    jd_entities = (
        extract_entities(
            job_description
        )
    )

    entity_detection_time = (
        time.perf_counter()
        - entity_start
    )

    print(
        f"Entity Detection Time: "
        f"{entity_detection_time:.6f} seconds"
    )

    print(
        f"Detected Resume Skills: "
        f"{len(resume_entities.get('skills', []))}"
    )

    print(
        f"Detected JD Skills: "
        f"{len(jd_entities.get('skills', []))}"
    )

    # ======================================================
    # STEP 4
    # SKILL MATCHING
    # ======================================================

    print()

    print(
        "--------------------------------------------------"
    )

    print(
        "STEP 4: SKILL MATCHING"
    )

    print(
        "--------------------------------------------------"
    )

    skill_start = (
        time.perf_counter()
    )

    raw_skill_result = (
        run_day17_skill_matching(
            candidate_id,
            target_role
        )
    )

    skill_result = (
        convert_day17_skill_result(
            raw_skill_result
        )
    )

    skill_matching_time = (
        time.perf_counter()
        - skill_start
    )

    skill_score = (
        skill_result[
            "score"
        ]
    )

    print()

    print(
        f"Skill Match Score: "
        f"{skill_score:.2f}%"
    )

    print()

    print(
        "Required Skills:"
    )

    for skill in skill_result[
        "required_skills"
    ]:

        print(
            f"• {skill}"
        )

    print()

    print(
        "Matched Skills:"
    )

    if skill_result[
        "matched_skills"
    ]:

        for skill in skill_result[
            "matched_skills"
        ]:

            print(
                f"[MATCHED] {skill}"
            )

    else:

        print(
            "No matching skills."
        )

    print()

    print(
        "Missing Skills:"
    )

    if skill_result[
        "missing_skills"
    ]:

        for skill in skill_result[
            "missing_skills"
        ]:

            print(
                f"[MISSING] {skill}"
            )

    else:

        print(
            "No missing skills."
        )

    # ======================================================
    # STEP 5
    # EXPERIENCE MATCHING
    # ======================================================

    print()

    print(
        "--------------------------------------------------"
    )

    print(
        "STEP 5: EXPERIENCE MATCHING"
    )

    print(
        "--------------------------------------------------"
    )

    experience_result = (
        calculate_experience_match(
            resume_entities,
            job_description
        )
    )

    experience_score = (
        experience_result[
            "score"
        ]
    )

    if experience_score is None:
        print("Experience Score: N/A")
    else:
        print(f"Experience Score: {experience_score:.2f}%")

    print(f"Status: {experience_result['status']}")

    # ======================================================
    # STEP 6
    # EDUCATION MATCHING
    # ======================================================

    print()

    print(
        "--------------------------------------------------"
    )

    print(
        "STEP 6: EDUCATION MATCHING"
    )

    print(
        "--------------------------------------------------"
    )

    education_result = (
        calculate_education_match(
            resume_entities,
            cleaned_resume_text,
            job_description
        )
    )

    education_score = (
        education_result[
            "score"
        ]
    )

    print(
        f"Education Score: "
        f"{education_score:.2f}%"
    )

    print(
        f"Status: "
        f"{education_result['status']}"
    )

    # ======================================================
    # STEP 7
    # SEMANTIC MATCHING
    # ======================================================
    #
    # IMPORTANT:
    #
    # Use the validated Day 17 cleaned resume.
    #
    # This is necessary because we experimentally confirmed:
    #
    # Fresh DOCX text       = 1076 characters
    # Day 18 cleaned text   = 1076 characters
    # Day 17 cleaned text   = 1074 characters
    #
    # and:
    #
    # CLEANED SAME = False
    #
    # Therefore using the Day 18 cleaned text directly
    # changes the Sentence Transformer result.
    # ======================================================

    print()

    print(
        "--------------------------------------------------"
    )

    print(
        "STEP 7: SEMANTIC MATCHING"
    )

    print(
        "--------------------------------------------------"
    )

    semantic_start = (
        time.perf_counter()
    )

    validated_semantic_resume = (
        get_validated_semantic_resume_text(
            candidate_id
        )
    )

    semantic_result = (
        calculate_semantic_similarity(
            validated_semantic_resume,
            job_description
        )
    )

    semantic_time = (
        time.perf_counter()
        - semantic_start
    )

    semantic_score = (
        semantic_result[
            "score"
        ]
    )

    print(
        f"Semantic Score: "
        f"{semantic_score:.2f}%"
    )

    print(
        f"Semantic Time: "
        f"{semantic_time:.6f} seconds"
    )

    # ======================================================
    # STEP 8
    # FINAL ATS SCORE
    # ======================================================

    print()

    print(
        "--------------------------------------------------"
    )

    print(
        "STEP 8: FINAL ATS SCORE"
    )

    print(
        "--------------------------------------------------"
    )

    final_result = (
        calculate_final_score(
            skill_score,
            experience_score,
            education_score,
            semantic_score
        )
    )

    final_score = (
        final_result[
            "final_score"
        ]
    )

    matching_status = (
        get_matching_status(
            final_score
        )
    )

    shortlisting_status = (
        get_shortlisting_status(
            final_score
        )
    )

    recommendation = (
        get_recommendation(
            final_score
        )
    )

    # ======================================================
    # DISPLAY COMPONENT SCORES
    # ======================================================

    print()

    print(
        "ATS COMPONENT SCORES"
    )

    print(f"Skill Matching         : {skill_score:.2f}%")

    if experience_score is None:
        print("Experience Relevance   : N/A")
    else:
        print(f"Experience Relevance   : {experience_score:.2f}%")

    print(f"Education Alignment    : {education_score:.2f}%")
    print(f"Semantic Similarity    : {semantic_score:.2f}%")

    # ======================================================
    # DISPLAY WEIGHTS
    # ======================================================

    print()

    print("EFFECTIVE WEIGHTS")

    effective_weights = final_result["effective_weights"]

    print(
        f"Skill Matching         : "
        f"{effective_weights['skill_matching'] * 100:.2f}%"
    )
    print(
        f"Experience Relevance   : "
        f"{effective_weights['experience_relevance'] * 100:.2f}%"
    )
    print(
        f"Education Alignment    : "
        f"{effective_weights['education_alignment'] * 100:.2f}%"
    )
    print(
        f"Semantic Similarity    : "
        f"{effective_weights['semantic_similarity'] * 100:.2f}%"
    )

    if final_result["excluded_components"]:
        print(
            "Excluded Components   : "
            + ", ".join(final_result["excluded_components"])
        )

    # ======================================================
    # DISPLAY CONTRIBUTIONS
    # ======================================================

    print()

    print(
        "WEIGHTED CONTRIBUTIONS"
    )

    print(
        f"Skill Contribution       : "
        f"{final_result['skill_contribution']:.2f}"
    )

    print(
        f"Experience Contribution  : "
        f"{final_result['experience_contribution']:.2f}"
    )

    print(
        f"Education Contribution   : "
        f"{final_result['education_contribution']:.2f}"
    )

    print(
        f"Semantic Contribution    : "
        f"{final_result['semantic_contribution']:.2f}"
    )

    # ======================================================
    # FINAL RESULT
    # ======================================================

    print()

    print(
        f"FINAL ATS SCORE: "
        f"{final_score:.2f}%"
    )

    print(
        f"Matching Status: "
        f"{matching_status}"
    )

    print(
        f"Shortlisting Status: "
        f"{shortlisting_status}"
    )

    print(
        f"Recommendation: "
        f"{recommendation}"
    )

    # ======================================================
    # PERFORMANCE
    # ======================================================

    total_pipeline_time = (
        time.perf_counter()
        - pipeline_start
    )

    print()

    print(
        "PERFORMANCE"
    )

    print(
        f"Extraction Time        : "
        f"{extraction_time:.6f} sec"
    )

    print(
        f"Cleaning Time          : "
        f"{cleaning_time:.6f} sec"
    )

    print(
        f"Entity Detection       : "
        f"{entity_detection_time:.6f} sec"
    )

    print(
        f"Skill Matching         : "
        f"{skill_matching_time:.6f} sec"
    )

    print(
        f"Semantic Processing    : "
        f"{semantic_time:.6f} sec"
    )

    print(
        f"Total Pipeline Time    : "
        f"{total_pipeline_time:.6f} sec"
    )

    # ======================================================
    # FINAL ATS JSON
    # ======================================================

    final_output = {

        "candidate_id":
            candidate_id,

        "target_role":
            target_role,

        "job_description":
            job_description_file,

        "engine":
            "ZecPath Day 18 Optimized ATS Engine",

        "pipeline_status":
            "SUCCESS",

        "scores": {

            "skill_matching":
                skill_score,

            "experience_relevance":
                experience_score,

            "education_alignment":
                education_score,

            "semantic_similarity":
                semantic_score,

            "final_ats_score":
                final_score
        },

        "weights":
            final_result["effective_weights"],

        "excluded_components":
            final_result["excluded_components"],

        "contributions": {

            "skill_matching":
                final_result[
                    "skill_contribution"
                ],

            "experience_relevance":
                final_result[
                    "experience_contribution"
                ],

            "education_alignment":
                final_result[
                    "education_contribution"
                ],

            "semantic_similarity":
                final_result[
                    "semantic_contribution"
                ]
        },

        "matching_status":
            matching_status,

        "shortlisting_status":
            shortlisting_status,

        "recommendation":
            recommendation,

        "skill_details":
            skill_result,

        "experience_details":
            experience_result,

        "education_details":
            education_result,

        "semantic_details":
            semantic_result,

        "entity_detection":
            resume_entities,

        "semantic_input":
            "Validated Day 17 cleaned resume",

        "performance": {

            "extraction_time_seconds":
                round(
                    extraction_time,
                    6
                ),

            "cleaning_time_seconds":
                round(
                    cleaning_time,
                    6
                ),

            "entity_detection_time_seconds":
                round(
                    entity_detection_time,
                    6
                ),

            "skill_matching_time_seconds":
                round(
                    skill_matching_time,
                    6
                ),

            "semantic_processing_time_seconds":
                round(
                    semantic_time,
                    6
                ),

            "semantic_model_access_time_seconds":
                semantic_result.get(
                    "model_access_time_seconds",
                    0.0
                ),

            "unaccounted_pipeline_time_seconds":
                round(
                    max(
                        0.0,
                        total_pipeline_time
                        - extraction_time
                        - cleaning_time
                        - entity_detection_time
                        - skill_matching_time
                        - semantic_time
                    ),
                    6
                ),

            "total_pipeline_time_seconds":
                round(
                    total_pipeline_time,
                    6
                ),

            "output_save_time_seconds": 0.0
        }
    }

    # ======================================================
    # SAVE FINAL ATS RESULT
    # ======================================================

    output_path = os.path.join(
        result_dir,
        "day18_optimized_ats_score.json"
    )

    # ======================================================
    # SAVE ENTITY RESULT
    # ======================================================

    entity_output_path = os.path.join(
        result_dir,
        "day18_entities.json"
    )

    # Measure the first write of both result files.
    output_save_start = time.perf_counter()

    save_json(
        final_output,
        output_path
    )

    save_json(
        resume_entities,
        entity_output_path
    )

    output_save_time = time.perf_counter() - output_save_start
    final_output["performance"]["output_save_time_seconds"] = round(
        output_save_time, 6
    )

    # Persist the measured timing in the ATS result. This final rewrite is
    # intentionally not included in output_save_time to avoid self-reference.
    save_json(
        final_output,
        output_path
    )

    print(
        f"Model Access Time       : "
        f"{semantic_result.get('model_access_time_seconds', 0.0):.6f} sec"
    )
    print(
        f"Output Save Time        : "
        f"{output_save_time:.6f} sec"
    )
    print(
        f"Unaccounted Pipeline    : "
        f"{final_output['performance']['unaccounted_pipeline_time_seconds']:.6f} sec"
    )

    # ======================================================
    # MEMORY CLEANUP
    # ======================================================

    del raw_resume_text
    del cleaned_resume_text
    del job_description
    del validated_semantic_resume

    gc.collect()

    # ======================================================
    # OUTPUT PATHS
    # ======================================================

    print()

    print(
        "Optimized ATS result saved to:"
    )

    print(
        output_path
    )

    print()

    print(
        "Entity result saved to:"
    )

    print(
        entity_output_path
    )

    return final_output


# ==========================================================
# COMMAND LINE INTERFACE
# ==========================================================

def main():

    if len(sys.argv) < 3:

        print()

        print(
            "Usage:"
        )

        print()

        print(
            "python -m "
            "day18_optimization.optimized_ats_engine "
            "candidate_011 "
            "\"Senior Python Developer\" "
            "senior_python_developer.txt"
        )

        print()

        return

    candidate_id = (
        sys.argv[1]
    )

    target_role = (
        sys.argv[2]
    )

    # ------------------------------------------------------
    # Job description file
    # ------------------------------------------------------

    if len(sys.argv) >= 4:

        job_description_file = (
            sys.argv[3]
        )

    else:

        default_mapping = {

            "candidate_006":
                "backend_developer.txt",

            "candidate_007":
                "hr_executive.txt",

            "candidate_008":
                "marketing_executive.txt",

            "candidate_009":
                "fresher_python_developer.txt",

            "candidate_010":
                "fresher_data_analyst.txt",

            "candidate_011":
                "senior_python_developer.txt",

            "candidate_012":
                "senior_backend_developer.txt",

            "candidate_013":
                "python_developer.txt"
        }

        job_description_file = (
            default_mapping.get(
                candidate_id
            )
        )

        if not job_description_file:

            print()

            print(
                "ERROR: Job description file "
                "was not provided."
            )

            print()

            return

    # ------------------------------------------------------
    # Run ATS pipeline
    # ------------------------------------------------------

    try:

        run_optimized_ats(

            candidate_id,

            target_role,

            job_description_file
        )

    except Exception as error:

        print()

        print(
            "=" * 70
        )

        print(
            "OPTIMIZED ATS PIPELINE FAILED"
        )

        print(
            "=" * 70
        )

        print()

        print(
            f"Error: {error}"
        )

        raise


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()