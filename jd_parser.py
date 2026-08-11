import re
import json

# -------------------------------
# Skill Synonym Dictionary
# -------------------------------
skill_synonyms = {
    "python": "Python",
    "sql": "SQL",
    "django": "Django",
    "docker": "Docker",
    "git": "Git",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "mongo database": "MongoDB",
    "tensorflow": "TensorFlow",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "machine learning": "Machine Learning"
}

# -------------------------------
# Role Variation Dictionary
# -------------------------------
role_variations = {
    "python engineer": "Python Developer",
    "backend python developer": "Python Developer",
    "software developer": "Software Engineer",
    "application developer": "Software Engineer",
    "ml engineer": "Machine Learning Engineer"
}

# -------------------------------
# Normalize Text
# -------------------------------
def normalize_text(text):
    text = text.lower()

    # Remove special characters
    text = re.sub(r'[^\w\s]', ' ', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# -------------------------------
# Extract Role
# -------------------------------
def extract_role(text):

    roles = [
        "python developer",
        "python engineer",
        "software developer",
        "software engineer",
        "data scientist",
        "machine learning engineer",
        "ml engineer",
        "frontend developer",
        "backend developer",
        "full stack developer",
        "java developer"
    ]

    for role in roles:
        if role in text:
            return role_variations.get(role, role.title())

    return "Not Found"


# -------------------------------
# Extract Skills
# -------------------------------
def extract_skills(text):

    skills = [
        "python",
        "sql",
        "django",
        "docker",
        "git",
        "react",
        "reactjs",
        "node",
        "nodejs",
        "javascript",
        "js",
        "mongodb",
        "mongo",
        "tensorflow",
        "pandas",
        "numpy",
        "machine learning"
    ]

    found = []

    for skill in skills:

        if skill in text:

            standard = skill_synonyms.get(skill, skill)

            if standard not in found:
                found.append(standard)

    return found

# -------------------------------
# Extract Education
# -------------------------------
def extract_education(text):

    education = []

    degrees = {
        "b tech": "B.Tech",
        "mca": "MCA",
        "bca": "BCA",
        "m tech": "M.Tech",
        "bachelor": "Bachelor's Degree",
        "master": "Master's Degree"
    }

    for key, value in degrees.items():

        if key in text:

            education.append(value)

    return education




# -------------------------------
# Extract Experience
# -------------------------------
def extract_experience(text):

    match = re.search(r'(\d+)\s*\+?\s*years?', text)

    if match:
        return match.group(1) + " years"

    elif "fresher" in text:
        return "0 years"

    return "Not Mentioned"



# -------------------------------
# Main Parser
# -------------------------------
def parse_job_description(jd_text):

    clean_text = normalize_text(jd_text)

    print("\nNormalized JD Text:")
    print(clean_text)

    job = {

        "job_id": "JD001",

        "role": extract_role(clean_text),

        "skills": extract_skills(clean_text),

        "experience": extract_experience(clean_text),

        "education": extract_education(clean_text)

    }

    return job


# -------------------------------
# Read Job Description
# -------------------------------
with open("sample_jd.txt", "r") as file:
    jd = file.read()

job = parse_job_description(jd)

print("\nStructured JD Output:\n")
print(json.dumps(job, indent=4))

# Save JSON
with open("output.json", "w") as file:
    json.dump(job, file, indent=4)

print("\nOutput successfully saved to output.json")