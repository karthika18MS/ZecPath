import json

# ==========================================================
# Read Parsed Experience
# ==========================================================

with open("parsed_experience.json", "r", encoding="utf-8") as file:

    parsed_data = json.load(file)

# ==========================================================
# Read Relevance Scores
# ==========================================================

with open("relevance_scores.json", "r", encoding="utf-8") as file:

    relevance_scores = json.load(file) 

# ==========================================================
# Create Structured Experience Object
# ==========================================================

structured_experience = {

    "candidate_id": parsed_data["candidate_id"],

    "total_experience": parsed_data["total_experience"],

    "experience": []

}

# ==========================================================
# Merge Experience + Relevance Score
# ==========================================================

for exp, score in zip(parsed_data["experience"], relevance_scores):

    structured_experience["experience"].append({

        "job_title": exp["job_title"],

        "company": exp["company"],

        "start_date": exp["start_date"],

        "end_date": exp["end_date"],

        "duration": exp["duration"],

        "relevance_score": score["relevance_score"]

    })

# ==========================================================
# Display Structured Experience
# ==========================================================

print("\n===================================")
print("STRUCTURED EXPERIENCE OBJECT")
print("===================================\n")

print(json.dumps(structured_experience, indent=4, ensure_ascii=False))

# ==========================================================
# Save Structured Experience
# ==========================================================

with open("structured_experience.json", "w", encoding="utf-8") as file:

    json.dump(

        structured_experience,

        file,

        indent=4,

        ensure_ascii=False

    )

print("\nStructured experience saved to structured_experience.json")