import re
import json

# ==========================================================
# Resume Section Heading Dictionary
# ==========================================================

section_headings = {

    "Profile": [
        "profile",
        "profile summary",
        "professional summary",
        "summary",
        "career objective",
        "objective"
    ],

    "Skills": [
        "skills",
        "technical skills",
        "technical expertise",
        "core skills",
        "core competencies"
    ],

    "Education": [
        "education",
        "academic qualification",
        "academic qualifications",
        "academic background",
        "educational details"
    ],

    "Experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "internship"
    ],

    "Projects": [
        "projects",
        "academic projects",
        "major projects",
        "personal projects"
    ],

    "Certifications": [
        "certifications",
        "certificates",
        "professional certifications"
    ],

    "Achievements": [
        "achievements",
        "awards",
        "honors"
    ],

    "Languages": [
        "languages",
        "language proficiency"
    ],

    "Hobbies": [
        "hobbies",
        "interests"
    ]
}


# ==========================================================
# Normalize Resume Text
# ==========================================================

def normalize_text(text):

    # Convert to lowercase
    text = text.lower()

    # Remove Windows line breaks
    text = text.replace("\r", "")

    # Replace Unicode dashes with normal hyphen
    text = text.replace("–", "-")   # En dash
    text = text.replace("—", "-")   # Em dash

    return text

# ==========================================================
# Check if line is a separator
# ==========================================================

def is_separator(line):

    line = line.strip()

    return re.fullmatch(r"[-=]{3,}", line) is not None


# ==========================================================
# Clean Resume Line
# ==========================================================

def clean_line(line):

    # Remove bullet symbols
    line = line.lstrip("•*- ")

    # Remove extra spaces
    line = line.strip()

    return line


# ==========================================================
# Resume Section Classifier
# ==========================================================

def classify_sections(text):

    lines = text.split("\n")

    sections = {
        "Profile": [],
        "Skills": [],
        "Education": [],
        "Experience": [],
        "Projects": [],
        "Certifications": [],
        "Achievements": [],
        "Languages": [],
        "Hobbies": []
    }

    current_section = None

    for line in lines:

        line = line.strip()

        # Ignore blank lines
        if not line:
            continue

        # Ignore separator lines
        if is_separator(line):
            continue

        lower_line = line.lower()

        heading_found = False

        # Detect section heading
        for section, headings in section_headings.items():

            if lower_line in headings:

                current_section = section
                heading_found = True
                break

        # Skip heading line
        if heading_found:
            continue

        # Clean the line
        line = clean_line(line)

        # Store content
        if current_section and line:

            sections[current_section].append(line)

    return sections


# ==========================================================
# Remove Empty Sections
# ==========================================================

def remove_empty_sections(sections):

    cleaned = {}

    for section, content in sections.items():

        if content:

            cleaned[section] = content

    return cleaned


# ==========================================================
# Read Resume
# ==========================================================

with open("sample_resume.txt", "r", encoding="utf-8") as file:

    resume = file.read()


# ==========================================================
# Normalize Resume
# ==========================================================

normalized_resume = normalize_text(resume)

print("\n==============================")
print("Normalized Resume")
print("==============================\n")

print(normalized_resume)


# ==========================================================
# Classify Resume
# ==========================================================

classified_resume = classify_sections(normalized_resume)


# ==========================================================
# Remove Empty Sections
# ==========================================================

classified_resume = remove_empty_sections(classified_resume)


# ==========================================================
# Display Output
# ==========================================================

print("\n==============================")
print("Resume Section Classification")
print("==============================\n")

print(json.dumps(classified_resume, indent=4, ensure_ascii=False))


# ==========================================================
# Save JSON Output
# ==========================================================

with open("output_sections.json", "w", encoding="utf-8") as file:

    json.dump(
        classified_resume,
        file,
        indent=4,
        ensure_ascii=False
    )

print("\nOutput successfully saved to output_sections.json")