import json


# Confidence Score Rules


# These are rule-based confidence scores.
# You can modify them later or replace them with ML/NLP scores.

default_scores = {
    "Technical Skills": 0.95,
    "Business Skills": 0.90,
    "Creative Skills": 0.85
}



# Generate Confidence Scores


def generate_confidence_scores(skills):

    confidence_scores = {}

    # Technical Skills
    for skill in skills["Technical Skills"]:

        confidence_scores[skill] = default_scores["Technical Skills"]

    # Business Skills
    for skill in skills["Business Skills"]:

        confidence_scores[skill] = default_scores["Business Skills"]

    # Creative Skills
    for skill in skills["Creative Skills"]:

        confidence_scores[skill] = default_scores["Creative Skills"]

    return confidence_scores



# Read Extracted Skills


with open("extracted_skills.json", "r", encoding="utf-8") as file:

    extracted_skills = json.load(file)


# Generate Confidence Scores


confidence = generate_confidence_scores(extracted_skills)



# Display Output


print("\n==============================")
print("Skill Confidence Scores")
print("==============================\n")

print(json.dumps(confidence, indent=4, ensure_ascii=False))


# Save Output


with open("confidence_scores.json", "w", encoding="utf-8") as file:

    json.dump(
        confidence,
        file,
        indent=4,
        ensure_ascii=False
    )

print("\nConfidence scores saved to confidence_scores.json")