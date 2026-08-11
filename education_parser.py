import fitz      # PyMuPDF
import re
import json

# ==========================================================
# Education Section Headings
# ==========================================================

education_headings = [

    "education",
    "academic qualification",
    "academic qualifications",
    "academic background",
    "educational details"

]

# ==========================================================
# Certification Section Headings
# ==========================================================

certification_headings = [

    "certifications",
    "certificates",
    "professional certifications"

]

# ==========================================================
# Next Section Headings
# ==========================================================

next_sections = [

    "experience",
    "work experience",
    "professional experience",
    "projects",
    "skills",
    "technical skills",
    "languages",
    "achievements",
    "hobbies",
    "interests",
    "references"

]

# ==========================================================
# Degree Mapping (Normalization)
# ==========================================================

degree_mapping = {

    "master of computer applications": "MCA",
    "mca": "MCA",
    "m.c.a": "MCA",

    "bachelor of computer applications": "BCA",
    "bca": "BCA",
    "b.c.a": "BCA",

    "bachelor of technology": "B.Tech",
    "b.tech": "B.Tech",
    "b tech": "B.Tech",

    "master of technology": "M.Tech",
    "m.tech": "M.Tech",

    "bachelor of engineering": "BE",
    "b.e": "BE",

    "master of engineering": "ME",
    "m.e": "ME"

}

# ==========================================================
# Read PDF
# ==========================================================

def read_pdf(pdf_path):

    document = fitz.open(pdf_path)

    text = ""

    for page in document:

        text += page.get_text() #extract text
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
# Extract Education Section
# ==========================================================

def extract_education_section(text):

    lines = text.split("\n") #whole resume is converted into individual lines

    education = []

    inside = False #intially parser  is outside the education

    for line in lines:

        line = line.strip()

        if line == "":
            continue

        if line in education_headings:

            inside = True #now everything is added to education[]
            continue

        if inside:

            if line in certification_headings:

                break

            if line in next_sections:

                break

            education.append(line)

    return education

# ==========================================================
# Extract Certification Section
# ==========================================================

def extract_certification_section(text):

    lines = text.split("\n")

    certifications = []

    inside = False

    for line in lines:

        line = line.strip()

        if line == "":
            continue

        if line in certification_headings:

            inside = True
            continue

        if inside:

            if line in next_sections:

                break

            certifications.append(line)

    return certifications

# ==========================================================
# Parse Education
# ==========================================================

def parse_education(lines):

    education = []

    i = 0

    while i < len(lines):

        line = lines[i]

        degree = None

        for key in degree_mapping:

            if key in line:

                degree = degree_mapping[key]

                break

        if degree:

            record = {}

            record["degree"] = degree

            # Field of Study

            if degree in ["MCA", "BCA"]:

                record["field_of_study"] = "Computer Applications"

            elif degree in ["B.Tech", "M.Tech", "BE", "ME"]:

                record["field_of_study"] = "Engineering"

            else:

                record["field_of_study"] = ""

            # Institution

            if i + 1 < len(lines):

                record["institution"] = lines[i + 1].title()

            else:

                record["institution"] = ""

            # University

            if i + 2 < len(lines):

                record["university"] = lines[i + 2].title()

            else:

                record["university"] = ""

            # Graduation Year

            if i + 3 < len(lines):

                years = re.findall(r"\d{4}", lines[i + 3])

                if len(years) > 0:

                    record["graduation_year"] = years[-1]

                else:

                    record["graduation_year"] = ""

            else:

                record["graduation_year"] = ""

            # CGPA

            record["cgpa"] = ""

            if i + 4 < len(lines):

                cgpa = re.search(r"cgpa[: ]*([0-9.]+)", lines[i + 4])

                if cgpa:

                    record["cgpa"] = cgpa.group(1)

            education.append(record)

        i += 1

    return education

# ==========================================================
# Parse Certifications
# ==========================================================

def parse_certifications(lines):

    certifications = []

    for line in lines:

        line = line.strip()

        # Skip empty lines
        if line == "":
            continue

        # Skip separator lines
        if re.fullmatch(r"-{3,}", line):
            continue

        # Remove bullets
        line = line.lstrip("•*- ")

        certifications.append(line.title())

    return certifications

# ==========================================================
# Display Education
# ==========================================================

def display_education(education):

    print("\n===================================")
    print("EDUCATION")
    print("===================================\n")

    for edu in education:

        print(json.dumps(edu, indent=4))

# ==========================================================
# Display Certifications
# ==========================================================

def display_certifications(certifications):

    print("\n===================================")
    print("CERTIFICATIONS")
    print("===================================\n")

    for cert in certifications:

        print(cert)

# ==========================================================
# Save JSON
# ==========================================================

def save_json(education, certifications):

    output = {

        "candidate_id": "CAND001",

        "education": education,

        "certifications": certifications

    }

    with open(

        "parsed_education.json",

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

    print(json.dumps(output, indent=4, ensure_ascii=False))

# ==========================================================
# Main Program
# ==========================================================

if __name__ == "__main__":

    pdf_path = "data/resumes/samplee_resume.pdf"

    print("\n===================================")
    print("READING RESUME PDF")
    print("===================================\n")

    resume = read_pdf(pdf_path)

    normalized = normalize_text(resume)

    education_section = extract_education_section(normalized)

    certification_section = extract_certification_section(normalized)

    education = parse_education(education_section)

    certifications = parse_certifications(certification_section)

    display_education(education)

    display_certifications(certifications)

    save_json(education, certifications)