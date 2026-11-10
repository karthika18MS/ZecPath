#This handles extraction noise while preserving technical punctuation.
import re
import unicodedata


# ==========================================================
# COMMON TERM CORRECTIONS
# ==========================================================

COMMON_CORRECTIONS = {
    "fast api": "FastAPI",
    "fast-api": "FastAPI",

    "restful api": "REST API",
    "restful apis": "REST APIs",

    "post gres": "PostgreSQL",
    "post gre sql": "PostgreSQL",

    "mongo db": "MongoDB",

    "node js": "Node.js",
    "node-js": "Node.js",

    "power bi": "Power BI",

    "machine-learning": "Machine Learning",

    "deep-learning": "Deep Learning",
}


# ==========================================================
# UNICODE NORMALIZATION
# ==========================================================

def normalize_unicode(text):

    return unicodedata.normalize(
        "NFKC",
        text
    )


# ==========================================================
# LINE ENDINGS
# ==========================================================

def normalize_line_endings(text):

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    return text


# ==========================================================
# REMOVE ZERO WIDTH CHARACTERS
# ==========================================================

def remove_zero_width_characters(text):

    return re.sub(
        r"[\u200B-\u200D\uFEFF]",
        "",
        text
    )


# ==========================================================
# NORMALIZE BULLETS
# ==========================================================

def normalize_bullets(text):

    bullets = [
        "•",
        "●",
        "▪",
        "◦",
        "‣",
        "⁃",
        "∙",
        "◆",
        "■",
    ]

    for bullet in bullets:

        text = text.replace(
            bullet,
            "-"
        )

    return text


# ==========================================================
# NORMALIZE DASHES
# ==========================================================

def normalize_dashes(text):

    for dash in [
        "–",
        "—",
        "−",
        "-",
    ]:

        text = text.replace(
            dash,
            "-"
        )

    return text


# ==========================================================
# NORMALIZE REPEATED PUNCTUATION
# ==========================================================

def normalize_repeated_punctuation(text):

    text = re.sub(
        r"!{2,}",
        "!",
        text
    )

    text = re.sub(
        r"\?{2,}",
        "?",
        text
    )

    text = re.sub(
        r"\.{3,}",
        ".",
        text
    )

    text = re.sub(
        r",{2,}",
        ",",
        text
    )

    return text


# ==========================================================
# NORMALIZE SECTION HEADINGS
# ==========================================================

def normalize_section_headings(text):

    patterns = {

        r"(?im)^\s*technical\s*\n\s*skills\s*:?\s*$":
            "TECHNICAL SKILLS",

        r"(?im)^\s*professional\s*\n\s*summary\s*:?\s*$":
            "PROFESSIONAL SUMMARY",

        r"(?im)^\s*professional\s*\n\s*experience\s*:?\s*$":
            "PROFESSIONAL EXPERIENCE",

        r"(?im)^\s*work\s*\n\s*experience\s*:?\s*$":
            "WORK EXPERIENCE",

        r"(?im)^\s*education\s*\n\s*:?\s*$":
            "EDUCATION",

        r"(?im)^\s*projects\s*\n\s*:?\s*$":
            "PROJECTS",
    }

    for pattern, replacement in patterns.items():

        text = re.sub(
            pattern,
            replacement,
            text
        )

    return text


# ==========================================================
# NORMALIZE COMMON TERMS
# ==========================================================

def normalize_common_terms(text):

    for incorrect, correct in COMMON_CORRECTIONS.items():

        text = re.sub(
            re.escape(incorrect),
            correct,
            text,
            flags=re.IGNORECASE
        )

    return text


# ==========================================================
# NORMALIZE SPACING
# ==========================================================

def normalize_spaces(text):

    text = text.replace(
        "\t",
        " "
    )

    text = re.sub(
        r"[ ]{2,}",
        " ",
        text
    )

    return text


# ==========================================================
# NORMALIZE SEPARATORS
# ==========================================================

def normalize_separators(text):

    # CI / CD → CI/CD
    text = re.sub(
        r"\bCI\s*/\s*CD\b",
        "CI/CD",
        text,
        flags=re.IGNORECASE
    )

    # Spaces around slash for normal words
    text = re.sub(
        r"\s*/\s*",
        "/",
        text
    )

    # Normalize vertical separators
    text = re.sub(
        r"\s*\|\s*",
        " | ",
        text
    )

    return text


# ==========================================================
# REMOVE CONTROL CHARACTERS
# ==========================================================

def remove_control_characters(text):

    result = []

    for character in text:

        if character in "\n\t":

            result.append(
                character
            )

        elif unicodedata.category(
            character
        ).startswith("C"):

            continue

        else:

            result.append(
                character
            )

    return "".join(
        result
    )


# ==========================================================
# REMOVE EXCESSIVE BLANK LINES
# ==========================================================

def normalize_blank_lines(text):

    return re.sub(
        r"\n[ \t]*\n+",
        "\n",
        text
    )


# ==========================================================
# FINAL CLEANUP
# ==========================================================

def final_cleanup(text):

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:

            lines.append(
                line
            )

    return "\n".join(
        lines
    ).strip()


# ==========================================================
# MAIN CLEANER
# ==========================================================

def clean_noisy_resume_text(text):

    if not text:

        return ""

    text = normalize_unicode(
        text
    )

    text = normalize_line_endings(
        text
    )

    text = remove_zero_width_characters(
        text
    )

    text = remove_control_characters(
        text
    )

    text = normalize_bullets(
        text
    )

    text = normalize_dashes(
        text
    )

    text = normalize_section_headings(
        text
    )

    text = normalize_common_terms(
        text
    )

    text = normalize_repeated_punctuation(
        text
    )

    text = normalize_separators(
        text
    )

    text = normalize_spaces(
        text
    )

    text = normalize_blank_lines(
        text
    )

    text = final_cleanup(
        text
    )

    return text