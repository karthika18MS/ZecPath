import json


# Read Extracted Skills


with open("extracted_skills.json", "r", encoding="utf-8") as file:

    extracted_skills = json.load(file)



# Read Confidence Scores


with open("confidence_scores.json", "r", encoding="utf-8") as file:

    confidence_scores = json.load(file)


# Create Structured Skill Output


structured_output = {

    "candidate_id": "CAND001",

    "technical_skills": extracted_skills["Technical Skills"],

    "business_skills": extracted_skills["Business Skills"],

    "creative_skills": extracted_skills["Creative Skills"],

    "confidence_scores": confidence_scores
}



# Display Structured Output


print("\n==============================")
print("Structured Skill Output")
print("==============================\n")

print(json.dumps(structured_output, indent=4, ensure_ascii=False))


# Save Structured Output


with open("structured_skills.json", "w", encoding="utf-8") as file:

    json.dump(
        structured_output,
        file,
        indent=4,
        ensure_ascii=False
    )

print("\nStructured skill output saved to structured_skills.json")