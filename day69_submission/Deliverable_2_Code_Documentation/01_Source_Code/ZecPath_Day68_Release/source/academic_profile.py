import json

# ==========================================================
# Read Parsed Education
# ==========================================================

with open("parsed_education.json", "r", encoding="utf-8") as file:

    parsed_data = json.load(file)

# ==========================================================
# Create Structured Academic Profile
# ==========================================================

structured_academic_profile = {

    "candidate_id": parsed_data["candidate_id"],

    "education": [],

    "certifications": []

}

# ==========================================================
# Add Education Details
# ==========================================================

for edu in parsed_data["education"]:

    structured_academic_profile["education"].append({

        "degree": edu["degree"],

        "field_of_study": edu["field_of_study"],

        "institution": edu["institution"],

        "university": edu["university"],

        "graduation_year": edu["graduation_year"],

        "cgpa": edu["cgpa"]

    })

# ==========================================================
# Add Certifications
# ==========================================================

for cert in parsed_data["certifications"]:

    structured_academic_profile["certifications"].append(cert)

# ==========================================================
# Display Structured Academic Profile
# ==========================================================

print("\n===================================")
print("STRUCTURED ACADEMIC PROFILE")
print("===================================\n")

print(

    json.dumps(

        structured_academic_profile,

        indent=4,

        ensure_ascii=False

    )

)

# ==========================================================
# Save Structured Academic Profile
# ==========================================================

with open(

    "structured_academic_profile.json",

    "w",

    encoding="utf-8"

) as file:

    json.dump(

        structured_academic_profile,

        file,

        indent=4,

        ensure_ascii=False

    )

print("\nStructured academic profile saved to structured_academic_profile.json")