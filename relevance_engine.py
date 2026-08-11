import json

# ==========================================================
# Target Job Role
# ==========================================================

target_role = "Python Developer"

# ==========================================================
# Relevance Score Rules
# ==========================================================

def calculate_relevance(job_title, target_role):

    job_title = job_title.lower()
    target_role = target_role.lower()

    # Exact Match
    if job_title == target_role:
        return 1.00

    # High Relevance
    elif "python developer" in job_title:
        return 0.95

    elif "software developer" in job_title:
        return 0.90

    elif "backend developer" in job_title:
        return 0.85

    elif "full stack developer" in job_title:
        return 0.80

    elif "software engineer" in job_title:
        return 0.80

    elif "intern" in job_title:
        return 0.70

    else:
        return 0.50


# ==========================================================
# Read Parsed Experience
# ==========================================================

with open("parsed_experience.json", "r", encoding="utf-8") as file:

    parsed_data = json.load(file)

experience_list = parsed_data["experience"]

# ==========================================================
# Calculate Relevance Scores
# ==========================================================

relevance_output = []

for experience in experience_list:

    score = calculate_relevance(

        experience["job_title"],
        target_role

    )

    relevance_output.append({

        "job_title": experience["job_title"],

        "company": experience["company"],

        "relevance_score": score

    })

# ==========================================================
# Display Output
# ==========================================================

print("\n===================================")
print("EXPERIENCE RELEVANCE SCORES")
print("===================================\n")

print(json.dumps(relevance_output, indent=4, ensure_ascii=False))

# ==========================================================
# Save JSON
# ==========================================================

with open("relevance_scores.json", "w", encoding="utf-8") as file:

    json.dump(

        relevance_output,

        file,

        indent=4,

        ensure_ascii=False

    )

print("\nRelevance scores saved to relevance_scores.json")