import json

# ==========================================================
# Target Job Role
# ==========================================================

target_role = "Python Developer"

# ==========================================================
# Degree Relevance Scores
# ==========================================================

degree_scores = {

    "MCA": 1.00,

    "BCA": 0.95,

    "M.Tech": 0.90,

    "B.Tech": 0.90,

    "ME": 0.85,

    "BE": 0.85

}

# ==========================================================
# Certification Relevance Rules
# ==========================================================

certification_keywords = {

    "python": {
        "category": "Programming",
        "score": 1.00
    },

    "data science": {
        "category": "Data Science",
        "score": 0.95
    },

    "machine learning": {
        "category": "Artificial Intelligence",
        "score": 0.95
    },

    "aws": {
        "category": "Cloud Computing",
        "score": 0.90
    },

    "azure": {
        "category": "Cloud Computing",
        "score": 0.90
    },

    "mongodb": {
        "category": "Database",
        "score": 0.85
    },

    "sql": {
        "category": "Database",
        "score": 0.85
    }

}

# ==========================================================
# Degree Relevance Function
# ==========================================================

def calculate_degree_score(degree):

    return degree_scores.get(degree, 0.60)


# ==========================================================
# Certification Relevance Function
# ==========================================================

def calculate_certification(certification):

    certification_lower = certification.lower()

    for keyword, value in certification_keywords.items():

        if keyword in certification_lower:

            return {

                "certification": certification,

                "category": value["category"],

                "relevance_score": value["score"]

            }

    return {

        "certification": certification,

        "category": "General",

        "relevance_score": 0.70

    }


# ==========================================================
# Read Structured Academic Profile
# ==========================================================

with open(

    "structured_academic_profile.json",

    "r",

    encoding="utf-8"

) as file:

    academic_profile = json.load(file)


# ==========================================================
# Degree Scores
# ==========================================================

education_output = []

for edu in academic_profile["education"]:

    education_output.append({

        "degree": edu["degree"],

        "field_of_study": edu["field_of_study"],

        "relevance_score": calculate_degree_score(

            edu["degree"]

        )

    })


# ==========================================================
# Certification Scores
# ==========================================================

certification_output = []

for cert in academic_profile["certifications"]:

    certification_output.append(

        calculate_certification(cert)

    )


# ==========================================================
# Final Structured Output
# ==========================================================

education_relevance = {

    "candidate_id":

        academic_profile["candidate_id"],

    "target_role":

        target_role,

    "education_relevance":

        education_output,

    "certification_relevance":

        certification_output

}


# ==========================================================
# Display Output
# ==========================================================

print("\n===================================")
print("EDUCATION RELEVANCE")
print("===================================\n")

print(

    json.dumps(

        education_relevance,

        indent=4,

        ensure_ascii=False

    )

)


# ==========================================================
# Save JSON
# ==========================================================

with open(

    "education_relevance.json",

    "w",

    encoding="utf-8"

) as file:

    json.dump(

        education_relevance,

        file,

        indent=4,

        ensure_ascii=False

    )

print("\nEducation relevance saved to education_relevance.json")