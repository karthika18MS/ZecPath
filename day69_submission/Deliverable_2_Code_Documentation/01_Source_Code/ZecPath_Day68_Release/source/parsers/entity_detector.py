
import re


# ==========================================================
# SKILL ALIASES
# ==========================================================

SKILL_ALIASES = {

    # Python
    "python": "python",
    "python programming": "python",

    # Python frameworks
    "django": "django",
    "flask": "flask",
    "fast api": "fastapi",
    "fastapi": "fastapi",

    # REST APIs
    "rest api": "rest api",
    "rest apis": "rest api",
    "restful api": "rest api",
    "restful apis": "rest api",
    "rest": "rest api",
    "rest api development": "rest api",

    # Databases
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "mongo db": "mongodb",
    "mongodb": "mongodb",
    "mysql": "mysql",
    "sql": "sql",
    "oracle": "oracle",
    "redis": "redis",

    # MERN stack
    "react.js": "react",
    "reactjs": "react",
    "react": "react",

    "node.js": "node.js",
    "node js": "node.js",
    "nodejs": "node.js",

    "express.js": "express.js",
    "express js": "express.js",
    "expressjs": "express.js",
    "express": "express.js",

    "javascript": "javascript",

    # Frontend
    "html5": "html5",
    "html": "html",
    "css3": "css3",
    "css": "css",
    "bootstrap": "bootstrap",

    # Authentication and development tools
    "jwt authentication": "jwt authentication",
    "jwt": "jwt authentication",
    "github": "github",
    "git": "git",
    "postman": "postman",
    "vs code": "visual studio code",
    "visual studio code": "visual studio code",

    # Java ecosystem
    "spring boot": "spring boot",
    "springboot": "spring boot",
    "spring mvc": "spring mvc",
    "hibernate": "hibernate",
    "microservices": "microservices",
    "maven": "maven",
    "jenkins": "jenkins",
    "junit": "junit",
    "java": "java",

    # Python data science ecosystem
    "scikit-learn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "pandas": "pandas",
    "numpy": "numpy",
    "data processing": "data processing",
    "machine learning fundamentals": "machine learning",
    "machine learning": "machine learning",
    "deep learning": "deep learning",
    "nlp": "nlp",

    # Programming languages
    "c++": "c++",
    "c#": "c#",

    # Other technologies
    "docker": "docker",
    "linux": "linux",
    "amazon web services": "aws",
    "aws": "aws",
    "power bi": "power bi",
    "tableau": "tableau",
    "excel": "excel",

    # Software engineering
    "ci/cd": "ci/cd",
    "ci / cd": "ci/cd",
    "cicd": "ci/cd",
    "unit testing": "unit testing",
    "unit tests": "unit testing",
    "testing": "testing",
    "mvc architecture": "mvc architecture",
    "object oriented programming": "object oriented programming",
    "oop": "object oriented programming",

    # HR and recruitment
    "human resources": "human resources",
    "human resource management": "human resource management",
    "hr management": "human resource management",
    "hr operations": "hr operations",
    "recruitment": "recruitment",
    "talent acquisition": "talent acquisition",
    "talent management": "talent management",
    "screening": "candidate screening",
    "candidate screening": "candidate screening",
    "interview coordination": "interview coordination",
    "employee relations": "employee relations",
    "employee engagement": "employee engagement",
    "payroll": "payroll",
    "performance management": "performance management",
    "onboarding": "onboarding",
    "training and development": "training and development",
    "labour law": "labour law",
    "labor law": "labour law",
    "hris": "hris",

    # Marketing
    "digital marketing": "digital marketing",
    "social media marketing": "social media marketing",
    "social media management": "social media management",
    "content marketing": "content marketing",
    "content creation": "content creation",
    "search engine optimization": "seo",
    "seo": "seo",
    "search engine marketing": "sem",
    "sem": "sem",
    "google analytics": "google analytics",
    "google ads": "google ads",
    "email marketing": "email marketing",
    "market research": "market research",
    "brand management": "brand management",
    "branding": "branding",
    "campaign management": "campaign management",
    "lead generation": "lead generation",
    "copywriting": "copywriting",

    # Graphic design and creative tools
    "adobe photoshop": "adobe photoshop",
    "photoshop": "adobe photoshop",
    "adobe illustrator": "adobe illustrator",
    "illustrator": "adobe illustrator",
    "adobe indesign": "adobe indesign",
    "indesign": "adobe indesign",
    "figma": "figma",
    "canva": "canva",
    "graphic design": "graphic design",
    "ui design": "ui design",
    "ux design": "ux design",
    "user interface design": "ui design",
    "user experience design": "ux design",
    "visual communication": "visual communication",
    "layout design": "layout design",
    "typography": "typography",
    "video editing": "video editing",
    "motion graphics": "motion graphics",
    "illustration": "illustration",
    "photo editing": "photo editing",

    # Data analytics
    "data analysis": "data analysis",
    "data analytics": "data analytics",
    "data visualization": "data visualization",
    "statistical analysis": "statistical analysis",
    "statistics": "statistics",
    "power bi": "power bi",
    "tableau": "tableau",
    "excel": "excel",
    "advanced excel": "advanced excel",
    "sql queries": "sql",
    "business intelligence": "business intelligence",
    "etl": "etl",

    # General professional skills commonly listed in JDs
    "communication skills": "communication",
    "communication": "communication",
    "teamwork": "teamwork",
    "problem solving": "problem solving",
    "problem-solving": "problem solving",
    "project management": "project management",
    "time management": "time management",
    "customer relationship management": "customer relationship management",
    "crm": "customer relationship management",
}


# ==========================================================
# DEGREE ALIASES
# ==========================================================

DEGREE_ALIASES = {

    "mca": "mca",
    "m.c.a": "mca",
    "master of computer applications": "mca",

    "mba": "mba",
    "m.b.a": "mba",
    "master of business administration": "mba",

    "bca": "bca",
    "b.c.a": "bca",
    "bachelor of computer applications": "bca",

    "btech": "btech",
    "b.tech": "btech",
    "bachelor of technology": "btech",

    "mtech": "mtech",
    "m.tech": "mtech",
    "master of technology": "mtech",

    "bsc": "bsc",
    "b.sc": "bsc",
    "bachelor of science": "bsc",

    "msc": "msc",
    "m.sc": "msc",
    "master of science": "msc",
}


# ==========================================================
# SECTION ALIASES
# ==========================================================

SECTION_ALIASES = {

    "summary": [
        "professional summary",
        "summary",
        "profile",
        "career objective",
        "objective",
    ],

    "skills": [
        "technical skills",
        "technical skill",
        "skills",
        "skills & technologies",
        "technical expertise",
        "core skills",
    ],

    "experience": [
        "professional experience",
        "work experience",
        "experience",
        "employment history",
        "professional employment",
    ],

    "education": [
        "education",
        "academic background",
        "academic qualification",
        "qualifications",
    ],

    "projects": [
        "projects",
        "academic projects",
        "personal projects",
    ],

    "soft_skills": [
        "soft skills",
        "personal skills",
        "interpersonal skills",
    ],

    "certifications": [
        "certifications",
        "certificates",
        "professional certifications",
    ],

    "achievements": [
        "achievements",
        "awards",
        "accomplishments",
    ],

    "languages": [
        "languages",
        "language proficiency",
    ],

    "declaration": [
        "declaration",
    ],
}


# ==========================================================
# KNOWN JOB TITLES
# ==========================================================

KNOWN_JOB_TITLES = [

    # MERN / Full Stack
    "senior mern stack developer",
    "mern stack developer",
    "mern developer",
    "full stack developer",

    # Backend
    "senior backend developer",
    "backend developer",

    # Python
    "senior python developer",
    "python developer",
    "fresher python developer",

    # Java
    "senior java developer",
    "java developer",

    # Frontend
    "frontend developer",
    "front end developer",

    # General software development
    "software engineer",
    "software developer",

    # Data roles
    "data analyst",
    "fresher data analyst",
    "data scientist",
    "machine learning engineer",

    # Other roles
    "hr executive",
    "human resources executive",
    "hr manager",
    "recruitment executive",
    "talent acquisition specialist",
    "marketing executive",
    "digital marketing executive",
    "marketing manager",
    "graphic designer",
    "ui designer",
    "ux designer",
    "visual designer",
    "project manager",
    "business analyst",
]


# ==========================================================
# TEXT NORMALIZATION
# ==========================================================

def normalize_text(text):
    """
    Basic normalization of extracted resume text.
    Preserves line breaks for section detection.
    """

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    return text.strip()


# ==========================================================
# NORMALIZE SECTION BOUNDARIES
# ==========================================================

def normalize_section_boundaries(text):
    """
    Repairs resumes where section headings are merged
    with the previous or next content.

    Matching is case-sensitive so ordinary lowercase
    phrases such as 'professional experience' are not
    incorrectly treated as section headings.
    """

    section_patterns = [

        "PROFESSIONAL SUMMARY",
        "TECHNICAL SKILLS",
        "PROFESSIONAL EXPERIENCE",
        "WORK EXPERIENCE",
        "EDUCATION",
        "PROJECTS",
        "ACADEMIC PROJECTS",
        "PERSONAL PROJECTS",
        "EMPLOYMENT HISTORY",
        "SOFT SKILLS",
        "PERSONAL SKILLS",
        "INTERPERSONAL SKILLS",
        "CERTIFICATIONS",
        "PROFESSIONAL CERTIFICATIONS",
        "ACHIEVEMENTS",
        "AWARDS",
        "ACCOMPLISHMENTS",
        "LANGUAGES",
        "LANGUAGE PROFICIENCY",
        "DECLARATION",
    ]

    for section in section_patterns:

        pattern = (
            r"\s+"
            + re.escape(section)
            + r"\s*:?\s*"
        )

        replacement = (
            "\n"
            + section
            + ":\n"
        )

        text = re.sub(
            pattern,
            replacement,
            text
        )

    return text


# ==========================================================
# DETECT SECTIONS
# ==========================================================

def detect_sections(text):
    """
    Detect resume sections after section boundaries
    have been normalized.
    """

    text = normalize_section_boundaries(text)

    lines = text.splitlines()

    sections = {}

    current_section = None

    for line in lines:

        line = line.strip()

        if not line:
            continue

        normalized_line = (
            line.lower()
            .rstrip(":")
            .strip()
        )

        detected_section = None

        for section_name, aliases in SECTION_ALIASES.items():

            if normalized_line in aliases:

                detected_section = section_name
                break

        if detected_section:

            current_section = detected_section

            sections.setdefault(
                current_section,
                []
            )

            continue

        if current_section:

            sections[current_section].append(line)

    return sections


# ==========================================================
# DETECT NAME
# ==========================================================

def detect_name(text):
    """
    Detect candidate name from an explicit NAME field.
    """

    section_names = (
        r"PROFESSIONAL SUMMARY|"
        r"TECHNICAL SKILLS|"
        r"PROFESSIONAL EXPERIENCE|"
        r"WORK EXPERIENCE|"
        r"EDUCATION|"
        r"PROJECTS|"
        r"SOFT SKILLS|"
        r"CERTIFICATIONS|"
        r"ACHIEVEMENTS|"
        r"LANGUAGES|"
        r"DECLARATION"
    )

    # Case 1: NAME appears before a known section.

    match = re.search(
        r"\bNAME\s*:\s*(.*?)(?=\s+(?:"
        + section_names
        + r")\s*:?)",
        text,
        flags=re.IGNORECASE
    )

    if match:

        name = match.group(1).strip()

        if name:
            return name

    # Case 2: NAME appears on its own line.

    match = re.search(
        r"(?im)^\s*NAME\s*:\s*(.+)$",
        text
    )

    if match:

        name = match.group(1).strip()

        name = re.split(
            r"\b(?:" + section_names + r")\b",
            name,
            maxsplit=1,
            flags=re.IGNORECASE
        )[0].strip()

        return name

    # Case 3: Find NAME anywhere in the text.

    match = re.search(
        r"\bNAME\s*:\s*([A-Za-z][A-Za-z .'-]{1,80})",
        text,
        flags=re.IGNORECASE
    )

    if match:

        name = match.group(1).strip()

        name = re.split(
            r"\b(?:" + section_names + r")\b",
            name,
            maxsplit=1,
            flags=re.IGNORECASE
        )[0].strip()

        return name

    # Case 4: First meaningful line fallback.

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if lines:

        first_line = lines[0]

        if (
            len(first_line.split()) <= 5
            and not first_line.upper().startswith(
                (
                    "PROFESSIONAL",
                    "TECHNICAL",
                    "EDUCATION",
                    "EXPERIENCE",
                    "PROJECTS",
                )
            )
        ):

            return first_line

    return None


# ==========================================================
# DETECT SKILLS
# ==========================================================

def detect_skills(text):
    """
    Detect normalized technical skills using aliases.
    """

    normalized_text = text.lower()

    detected_skills = set()

    aliases = sorted(
        SKILL_ALIASES.keys(),
        key=len,
        reverse=True
    )

    for alias in aliases:

        canonical_skill = SKILL_ALIASES[alias]

        pattern = (
            r"(?<![a-z0-9+#])"
            + re.escape(alias)
            + r"(?![a-z0-9+#])"
        )

        if re.search(
            pattern,
            normalized_text
        ):

            detected_skills.add(
                canonical_skill
            )

    return sorted(detected_skills)


# ==========================================================
# DETECT DEGREES
# ==========================================================

def detect_degrees(text):
    """
    Detect normalized academic degrees.
    """

    normalized_text = text.lower()

    detected_degrees = set()

    aliases = sorted(
        DEGREE_ALIASES.keys(),
        key=len,
        reverse=True
    )

    for alias in aliases:

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(alias)
            + r"(?![a-z0-9])"
        )

        if re.search(
            pattern,
            normalized_text
        ):

            detected_degrees.add(
                DEGREE_ALIASES[alias]
            )

    return sorted(detected_degrees)


# ==========================================================
# DETECT YEARS
# ==========================================================

def detect_years(text):
    """
    Detect four-digit years.
    """

    years = re.findall(
        r"\b(?:19|20)\d{2}\b",
        text
    )

    return sorted(
        set(
            int(year)
            for year in years
        )
    )


# ==========================================================
# DETECT EXPERIENCE
# ==========================================================

def detect_experience(text):
    """
    Detect experience formats such as:

    3 years of experience
    3+ years of experience
    3 years experience
    3 years of professional experience
    3 years professional experience
    Experience: 3 years
    """

    patterns = [

        # 3 years of professional experience
        (
            r"(\d+(?:\.\d+)?)\+?\s+years?\s+of\s+"
            r"(?:professional\s+)?experience"
        ),

        # 3 years professional experience
        (
            r"(\d+(?:\.\d+)?)\+?\s+years?\s+"
            r"(?:of\s+)?professional\s+experience"
        ),

        # 3 years experience
        (
            r"(\d+(?:\.\d+)?)\+?\s+years?\s+experience"
        ),

        # Experience: 3 years
        (
            r"experience\s*:\s*(\d+(?:\.\d+)?)\s*years?"
        ),
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            return float(
                match.group(1)
            )

    return None


# ==========================================================
# DETECT JOB TITLES
# ==========================================================

def detect_job_titles(text):
    """
    Detect known job titles.
    """

    normalized_text = text.lower()

    detected_titles = set()

    for title in sorted(
        KNOWN_JOB_TITLES,
        key=len,
        reverse=True
    ):
        pattern = r"(?<![a-z0-9])" + re.escape(title) + r"(?![a-z0-9])"
        if re.search(pattern, normalized_text):
            detected_titles.add(title)

    return sorted(
        detected_titles,
        key=len,
        reverse=True
    )


# ==========================================================
# DETECT PROJECTS
# ==========================================================

def detect_projects(sections):
    """
    Return project information detected under PROJECTS.
    """

    projects = sections.get(
        "projects",
        []
    )

    return [
        project.strip()
        for project in projects
        if project.strip()
    ]


# ==========================================================
# MAIN ENTITY EXTRACTION
# ==========================================================

def extract_entities(text):
    """
    Main entity extraction function.

    Returns:

        name
        job_titles
        skills
        degrees
        experience_years
        years
        projects
        sections
    """

    text = normalize_text(text)

    normalized_text = normalize_section_boundaries(
        text
    )

    sections = detect_sections(
        normalized_text
    )

    entities = {

        "name": detect_name(
            normalized_text
        ),

        "job_titles": detect_job_titles(
            normalized_text
        ),

        "skills": detect_skills(
            normalized_text
        ),

        "degrees": detect_degrees(
            normalized_text
        ),

        "experience_years": detect_experience(
            normalized_text
        ),

        "years": detect_years(
            normalized_text
        ),

        "projects": detect_projects(
            sections
        ),

        "sections": sections
    }

    return entities


# ==========================================================
# STANDALONE TEST
# ==========================================================

if __name__ == "__main__":

    sample_text = """
    NAME: ARUN KUMAR

    PROFESSIONAL SUMMARY
    MERN Stack Developer with 3 years of professional experience.

    TECHNICAL SKILLS
    React.js, Node.js, Express.js, MongoDB, JavaScript,
    HTML5, CSS3, Bootstrap, MySQL, Git, GitHub,
    JWT Authentication.

    PROFESSIONAL EXPERIENCE
    MERN Stack Developer.

    EDUCATION
    MCA
    BCA

    PROJECTS
    Online Shopping Management System.

    SOFT SKILLS
    Communication
    Teamwork

    DECLARATION
    Information is correct.
    """

    result = extract_entities(sample_text)

    print("\nZecPath Entity Detection Test")
    print("=" * 45)

    for key, value in result.items():

        print(f"\n{key.upper()}:")
        print(value)
