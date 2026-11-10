import json

# ==========================================================
# Read Similarity Score
# ==========================================================

with open(
    "similarity_score.json",
    "r",
    encoding="utf-8"
) as file:

    similarity_data = json.load(file)

# ==========================================================
# Read Structured Experience
# ==========================================================

with open(
    "structured_experience.json",
    "r",
    encoding="utf-8"
) as file:

    experience_data = json.load(file)

# ==========================================================
# Read Structured Academic Profile
# ==========================================================

with open(
    "structured_academic_profile.json",
    "r",
    encoding="utf-8"
) as file:

    education_data = json.load(file)

# ==========================================================
# Get Similarity Score
# ==========================================================

similarity_score = similarity_data["similarity_score"]

# ==========================================================
# Decide Matching Status
# ==========================================================

if similarity_score >= 0.90:

    status = "Excellent Match"

elif similarity_score >= 0.80:

    status = "Strong Match"

elif similarity_score >= 0.70:

    status = "Good Match"

elif similarity_score >= 0.50:

    status = "Moderate Match"

else:

    status = "Poor Match"

# ==========================================================
# Recommendation
# ==========================================================

if similarity_score >= 0.80:

    recommendation = "Recommended for Interview"

elif similarity_score >= 0.60:

    recommendation = "Can be Considered"

else:

    recommendation = "Not Recommended"

# ==========================================================
# Create Matching Report
# ==========================================================

matching_report = {

    "candidate_id": similarity_data["candidate_id"],

    "overall_similarity_score":
        similarity_data["similarity_score"],

    "similarity_percentage":
        similarity_data["similarity_percentage"],

    "matching_status":
        status,

    "recommendation":
        recommendation,

    "total_experience":
        experience_data["total_experience"],

    "education":
        education_data["education"],

    "certifications":
        education_data["certifications"]

}

# ==========================================================
# Display Report
# ==========================================================

print("\n===================================")
print("MATCHING ACCURACY REPORT")
print("===================================\n")

print(json.dumps(

    matching_report,

    indent=4,

    ensure_ascii=False

))

# ==========================================================
# Save Report
# ==========================================================

with open(

    "matching_report.json",

    "w",

    encoding="utf-8"

) as file:

    json.dump(

        matching_report,

        file,

        indent=4,

        ensure_ascii=False

    )

print("\nMatching report saved to matching_report.json")