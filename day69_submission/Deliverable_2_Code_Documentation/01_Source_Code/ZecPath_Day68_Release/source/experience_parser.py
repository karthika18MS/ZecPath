import pymupdf      # PyMuPDF
import re
import json
from datetime import datetime

# ==========================================================
# Experience Section Headings
# ==========================================================

experience_headings = [

    "experience",
    "work experience",
    "professional experience",
    "employment history",
    "career history",
    "internship",
    "internships"

]

# ==========================================================
# Next Section Headings
# Used to know where Experience section ends
# ==========================================================

next_sections = [

    "education",
    "skills",
    "technical skills",
    "projects",
    "certifications",
    "languages",
    "achievements",
    "hobbies",
    "interests",
    "references"

]

# ==========================================================
# Read PDF
# ==========================================================

def read_pdf(pdf_path):

    document = pymupdf.open(pdf_path)

    text = ""

    for page in document:

        text += page.get_text()

        text += "\n"

    document.close()

    return text


# ==========================================================
# Normalize Text
# ==========================================================

def normalize_text(text):

    text = text.lower()

    text = text.replace("\r", "")

    text = text.replace("–", "-")

    text = text.replace("—", "-")

    return text



# ==========================================================
# Extract Experience Section
# ==========================================================

def extract_experience_section(text):

    lines = text.split("\n")

    experience_lines = []

    inside_experience = False

    for line in lines:

        line = line.strip()

        # Skip blank lines
        if line == "":
            continue

        # Skip separator lines
        if re.fullmatch(r"-{3,}", line):
            continue

        # Detect beginning of Experience section
        if line in experience_headings:

            inside_experience = True
            continue

        # Detect end of Experience section
        if inside_experience:

            if line in next_sections:
                break

            experience_lines.append(line)

    return experience_lines


# ==========================================================
# Display Experience Section
# ==========================================================

def display_experience(experience):

    print("\n===================================")
    print("EXPERIENCE SECTION")
    print("===================================\n")

    if not experience:

        print("No experience section found.")

    else:

        for line in experience:

            print(line)


# ==========================================================
# Job Titles
# ==========================================================


job_titles = [

    "software engineer",
    "software developer",

    "python developer",
    "python developer intern",
    "intern python developer",
    "intern - python developer",

    "backend developer",
    "frontend developer",
    "full stack developer",
    "web developer",

    "data analyst",
    "data scientist",

    "machine learning engineer",
    "ai engineer",

    "intern",
    "graduate trainee",
    "devops engineer"

]


# ==========================================================
# Date Pattern
# ==========================================================


date_pattern = re.compile(

    r"(january|february|march|april|may|june|july|august|"
    r"september|october|november|december)\s+\d{4}\s*-\s*"
    r"(present|(january|february|march|april|may|june|july|"
    r"august|september|october|november|december)\s+\d{4})"

)


# ==========================================================
# Parse Experience Details
# ==========================================================


def parse_experience(experience_lines):

    parsed_experience = []

    i = 0

    while i < len(experience_lines):

        line = experience_lines[i]

        matched = False

        for title in job_titles:

            if title in line:

                matched = True
                break

        if matched:

            experience = {}

            experience["job_title"] = line.title()

            # Company
            if i + 1 < len(experience_lines):
                experience["company"] = experience_lines[i + 1].title()
            else:
                experience["company"] = "Unknown"

            # Dates
            if i + 2 < len(experience_lines):

                date_line = experience_lines[i + 2]

                if date_pattern.fullmatch(date_line):

                    experience["duration"] = date_line

                    parts = date_line.split("-")

                    experience["start_date"] = parts[0].strip().title()

                    experience["end_date"] = parts[1].strip().title()

                else:

                    experience["duration"] = "Unknown"

                    experience["start_date"] = ""

                    experience["end_date"] = ""

            parsed_experience.append(experience)

        i += 1

    return parsed_experience


# ==========================================================
# Display Parsed Experience
# ==========================================================


def display_parsed_experience(parsed):

    print("\n===================================")
    print("PARSED EXPERIENCE")
    print("===================================\n")

    for exp in parsed:

        print("Job Title :", exp["job_title"])

        print("Company   :", exp["company"])

        print("Start     :", exp["start_date"])

        print("End       :", exp["end_date"])

        print("Duration  :", exp["duration"])

        print("----------------------------------")


# ==========================================================
# Month Mapping
# ==========================================================


month_map = {

    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12

}


# ==========================================================
# Calculate Total Experience
# ==========================================================



def calculate_total_experience(parsed_experience):

    total_months = 0

    current_date = datetime.now()

    for exp in parsed_experience:

        start = exp["start_date"].lower()

        end = exp["end_date"].lower()

        try:

            # -------------------------
            # Start Date
            # -------------------------

            start_month = month_map[start.split()[0]]

            start_year = int(start.split()[1])

            # -------------------------
            # End Date
            # -------------------------

            if end == "present":

                end_month = current_date.month

                end_year = current_date.year

            else:

                end_month = month_map[end.split()[0]]

                end_year = int(end.split()[1])

            months = (end_year - start_year) * 12

            months += (end_month - start_month)

            total_months += months

        except:

            continue

    years = total_months // 12

    months = total_months % 12

    return f"{years} years {months} months"


# ==========================================================
# Save JSON Output
# ==========================================================


def save_json(parsed_experience, total_experience):

    output = {

        "candidate_id": "CAND001",

        "experience": parsed_experience,

        "total_experience": total_experience

    }

    with open(

        "parsed_experience.json",

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            output,

            file,

            indent=4,

            ensure_ascii=False

        )

    print("\n===================================")

    print("JSON SAVED SUCCESSFULLY")

    print("===================================\n")

    print(json.dumps(

        output,

        indent=4,

        ensure_ascii=False

    ))



# ==========================================================
# Main Program
# ==========================================================



if __name__ == "__main__":

    pdf_path = "data/resumes/samplee_resume.pdf"

    print("\n===================================")
    print("READING RESUME PDF")
    print("===================================\n")

    # Read PDF
    resume = read_pdf(pdf_path)

    # Normalize Resume Text
    normalized_resume = normalize_text(resume)

    # Extract Experience Section
    experience = extract_experience_section(normalized_resume)

    # Display Experience Section
    display_experience(experience)

    # Parse Experience Details
    parsed = parse_experience(experience)

    # Display Parsed Experience
    display_parsed_experience(parsed)

    # Calculate Total Experience
    total = calculate_total_experience(parsed)

    # Display Total Experience
    print("\n===================================")
    print("TOTAL EXPERIENCE")
    print("===================================\n")

    print(total)

    # Save Parsed Experience to JSON
    save_json(parsed, total)
